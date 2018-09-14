# Embedded file name: scripts/client/gui/shared/gui_items/Tankman.py
from helpers import i18n
from items import tankmen, vehicles, ITEM_TYPE_NAMES
from gui import nationCompareByIndex
from gui.shared.utils.functions import getShortDescr
from gui.shared.gui_items import HasStrCD, GUIItem, ItemsCollection

class TankmenCollection(ItemsCollection):

    def _filterItem(self, item, nation = None, role = None, isInTank = None):
        if role is not None and item.descriptor.role != role:
            return False
        elif isInTank is not None and item.isInTank != isInTank:
            return False
        else:
            return ItemsCollection._filterItem(self, item, nation)


class TankmenComparator(object):

    def __init__(self, vehicleGetter = None):
        self._vehicleGetter = vehicleGetter

    def __call__(self, first, second):
        if first is None or second is None:
            return 1
        else:
            res = nationCompareByIndex(first.nationID, second.nationID)
            if res:
                return res
            if first.isInTank and not second.isInTank:
                return -1
            if not first.isInTank and second.isInTank:
                return 1
            if first.isInTank and second.isInTank:
                if self._vehicleGetter is not None:
                    tman1vehicle = self._vehicleGetter(first.vehicleInvID)
                    tman2vehicle = self._vehicleGetter(second.vehicleInvID)
                    if tman1vehicle is not None and tman2vehicle is not None:
                        res = tman1vehicle.__cmp__(tman2vehicle)
                        if res:
                            return res
                TANKMEN_ROLES_ORDER = Tankman.TANKMEN_ROLES_ORDER
                if TANKMEN_ROLES_ORDER[first.descriptor.role] < TANKMEN_ROLES_ORDER[second.descriptor.role]:
                    return -1
                if TANKMEN_ROLES_ORDER[first.descriptor.role] > TANKMEN_ROLES_ORDER[second.descriptor.role]:
                    return 1
            return cmp(first.lastUserName, second.lastUserName) or 1


class Tankman(GUIItem, HasStrCD):

    class ROLES:
        COMMANDER = 'commander'
        RADIOMAN = 'radioman'
        DRIVER = 'driver'
        GUNNER = 'gunner'
        LOADER = 'loader'

    TANKMEN_ROLES_ORDER = {ROLES.COMMANDER: 0,
     ROLES.GUNNER: 1,
     ROLES.DRIVER: 2,
     ROLES.RADIOMAN: 3,
     ROLES.LOADER: 4}

    def __init__(self, strCompactDescr, inventoryID = -1, vehicle = None, proxy = None):
        GUIItem.__init__(self, proxy)
        HasStrCD.__init__(self, strCompactDescr)
        self.__descriptor = None
        self.invID = inventoryID
        self.nationID = self.descriptor.nationID
        self.itemTypeID = vehicles._TANKMAN
        self.itemTypeName = ITEM_TYPE_NAMES[self.itemTypeID]
        self.combinedRoles = (self.descriptor.role,)
        self.vehicleNativeDescr = vehicles.VehicleDescr(typeID=(self.nationID, self.descriptor.vehicleTypeID))
        self.vehicleInvID = -1
        self.vehicleDescr = None
        self.vehicleBonuses = dict()
        self.vehicleSlotIdx = -1
        if vehicle is not None:
            self.vehicleInvID = vehicle.invID
            self.vehicleDescr = vehicle.descriptor
            self.vehicleBonuses = dict(vehicle.bonuses)
            self.vehicleSlotIdx = vehicle.crewIndices.get(inventoryID, -1)
            crewRoles = self.vehicleDescr.type.crewRoles
            if -1 < self.vehicleSlotIdx < len(crewRoles):
                self.combinedRoles = crewRoles[self.vehicleSlotIdx]
        self.skills = self._buildSkills(proxy)
        self.skillsMap = self._buildSkillsMap()
        if proxy is not None:
            pass
        self.__cmp__ = TankmenComparator()
        return

    def _buildSkills(self, proxy):
        return [ TankmanSkill(skill, self, proxy) for skill in self.descriptor.skills ]

    def _buildSkillsMap(self):
        return dict([ (skill.name, skill) for skill in self.skills ])

    @property
    def realRoleLevel(self):
        effRoleLevel = self.efficiencyRoleLevel
        penalty = effRoleLevel - self.roleLevel
        commBonus = self.vehicleBonuses.get('commander', 0)
        if self.descriptor.role == self.ROLES.COMMANDER:
            commBonus = 0
        brothersBonus = self.vehicleBonuses.get('brotherhood', 0)
        eqsBonus = self.vehicleBonuses.get('equipment', 0)
        optDevsBonus = self.vehicleBonuses.get('optDevices', 0)
        realRoleLevel = effRoleLevel + commBonus + brothersBonus + eqsBonus + optDevsBonus
        return (realRoleLevel, (commBonus,
          brothersBonus,
          eqsBonus,
          optDevsBonus,
          penalty))

    @property
    def descriptor(self):
        if self.__descriptor is None or self.__descriptor.dossierCompactDescr != self.strCompactDescr:
            self.__descriptor = tankmen.TankmanDescr(compactDescr=self.strCompactDescr)
        return self.__descriptor

    @property
    def isInTank(self):
        return self.vehicleDescr is not None

    @property
    def roleLevel(self):
        return self.descriptor.roleLevel

    @property
    def icon(self):
        return getIconName(self.nationID, self.descriptor.iconID)

    @property
    def iconRank(self):
        return getRankIconName(self.nationID, self.descriptor.rankID)

    @property
    def iconRole(self):
        return getRoleIconName(self.descriptor.role)

    @property
    def firstUserName(self):
        return getFirstUserName(self.nationID, self.descriptor.firstNameID)

    @property
    def lastUserName(self):
        return getLastUserName(self.nationID, self.descriptor.lastNameID)

    @property
    def fullUserName(self):
        return getFullUserName(self.nationID, self.descriptor.firstNameID, self.descriptor.lastNameID)

    @property
    def rankUserName(self):
        return getRankUserName(self.nationID, self.descriptor.rankID)

    @property
    def roleUserName(self):
        return getRoleUserName(self.descriptor.role)

    @property
    def hasNewSkill(self):
        return self.roleLevel == tankmen.MAX_SKILL_LEVEL and (self.descriptor.lastSkillLevel == tankmen.MAX_SKILL_LEVEL or not len(self.skills))

    @property
    def newSkillCount(self):
        if self.hasNewSkill:
            tmanDescr = tankmen.TankmanDescr(self.strCD)
            i = 0
            skills_list = list(tankmen.ACTIVE_SKILLS)
            while tmanDescr.roleLevel == 100 and (tmanDescr.lastSkillLevel == 100 or len(tmanDescr.skills) == 0) and len(skills_list) > 0:
                skillname = skills_list.pop()
                if skillname not in tmanDescr.skills:
                    tmanDescr.addSkill(skillname)
                    i += 1

            return (i, tmanDescr.lastSkillLevel)
        return (0, 0)

    @property
    def efficiencyRoleLevel(self):
        factor, addition = (1, 0)
        if self.isInTank:
            factor, addition = self.descriptor.efficiencyOnVehicle(self.vehicleDescr)
        return round(self.roleLevel * factor)

    def getNextLevelXpCost(self):
        if self.roleLevel != tankmen.MAX_SKILL_LEVEL or not self.hasNewSkill:
            descr = self.descriptor
            lastSkillNumValue = descr.lastSkillNumber - descr.freeSkillsNumber
            if lastSkillNumValue == 0 or self.roleLevel != tankmen.MAX_SKILL_LEVEL:
                nextSkillLevel = self.roleLevel
            else:
                nextSkillLevel = descr.lastSkillLevel
            skillSeqNum = 0
            if self.roleLevel == tankmen.MAX_SKILL_LEVEL:
                skillSeqNum = lastSkillNumValue
            return descr.levelUpXpCost(nextSkillLevel, skillSeqNum) - descr.freeXP
        return 0

    def getNextSkillXpCost(self):
        if self.roleLevel != tankmen.MAX_SKILL_LEVEL or not self.hasNewSkill:
            descr = self.descriptor
            lastSkillNumValue = descr.lastSkillNumber - descr.freeSkillsNumber
            if lastSkillNumValue == 0 or self.roleLevel != tankmen.MAX_SKILL_LEVEL:
                nextSkillLevel = self.roleLevel
            else:
                nextSkillLevel = descr.lastSkillLevel
            skillSeqNum = 0
            if self.roleLevel == tankmen.MAX_SKILL_LEVEL:
                skillSeqNum = lastSkillNumValue
            needXp = 0
            for level in range(nextSkillLevel, tankmen.MAX_SKILL_LEVEL):
                needXp += descr.levelUpXpCost(level, skillSeqNum)

            return needXp - descr.freeXP
        return 0

    @property
    def vehicleNativeType(self):
        for tag in vehicles.VEHICLE_CLASS_TAGS.intersection(self.vehicleNativeDescr.type.tags):
            return tag

    def __cmp__(self, other):
        if other is None:
            return -1
        res = nationCompareByIndex(self.nationID, other.nationID)
        if res:
            return res
        elif self.isInTank and not other.isInTank:
            return -1
        elif not self.isInTank and other.isInTank:
            return 1
        if self.isInTank and other.isInTank:
            if self.vehicleInvID != other.vehicleInvID:
                return -1
            res = self.TANKMEN_ROLES_ORDER[self.descriptor.role] - self.TANKMEN_ROLES_ORDER[other.descriptor.role]
            if res:
                return res
        if self.lastUserName < other.lastUserName:
            return -1
        elif self.lastUserName > other.lastUserName:
            return 1
        else:
            return 0

    def __eq__(self, other):
        if other is None or not isinstance(other, Tankman):
            return False
        else:
            return self.invID == other.invID

    def __repr__(self):
        return 'Tankman<id:%d, nation:%d, vehicleID:%d>' % (self.invID, self.nationID, self.vehicleInvID)


class TankmanSkill(GUIItem):

    def __init__(self, skillName, tankman = None, proxy = None):
        super(TankmanSkill, self).__init__(proxy)
        self.name = skillName
        self.isPerk = self.name in tankmen.PERKS
        self.level = 0
        self.type = self.__getSkillType()
        self.roleType = None
        self.isActive = False
        self.isEnable = False
        self.isFemale = False
        if tankman is not None:
            tdescr = tankman.descriptor
            self.isFemale = tdescr.isFemale
            self.level = tdescr.lastSkillLevel if tdescr.skills.index(self.name) == len(tdescr.skills) - 1 else tankmen.MAX_SKILL_LEVEL
            self.roleType = self.__getSkillRoleType(skillName)
            self.isActive = self.__getSkillActivity(tankman)
            self.isEnable = self.__getEnabledSkill(tankman)
        return

    def __getEnabledSkill(self, tankman):
        for role in tankman.combinedRoles:
            roleSkills = tankmen.SKILLS_BY_ROLES.get(role, tuple())
            if self.name in roleSkills:
                return True

        return False

    @classmethod
    def __getSkillRoleType(cls, skillName):
        if skillName in tankmen.COMMON_SKILLS:
            return 'common'
        else:
            for role, skills in tankmen.SKILLS_BY_ROLES.iteritems():
                if skillName in skills:
                    return role

            return None

    def __getSkillActivity(self, tankman):
        if tankman is None:
            return True
        else:
            isBrotherhood = tankman.vehicleBonuses.get('brotherhood', 0) > 0
            return not self.isPerk or self.name == 'brotherhood' and isBrotherhood or self.name != 'brotherhood' and self.level == tankmen.MAX_SKILL_LEVEL

    def __getSkillType(self):
        if self.isPerk:
            if self.name == 'brotherhood':
                return 'perk_common'
            else:
                return 'perk'
        return 'skill'

    @property
    def userName(self):
        if self.name == 'brotherhood' and self.isFemale:
            return i18n.makeString('#item_types:tankman/skills/brotherhood_female')
        return getSkillUserName(self.name)

    @property
    def description(self):
        if self.name == 'brotherhood' and self.isFemale:
            return i18n.makeString('#item_types:tankman/skills/brotherhood_female_descr')
        return getSkillUserDescription(self.name)

    @property
    def shortDescription(self):
        return getShortDescr(self.description)

    @property
    def icon(self):
        return getSkillIconName(self.name)

    def __repr__(self):
        return 'TankmanSkill<name:%s, level:%d, isActive:%s>' % (self.name, self.level, str(self.isActive))


def getFirstUserName(nationID, firstNameID):
    return i18n.convert(tankmen.getNationConfig(nationID)['firstNames'][firstNameID])


def getLastUserName(nationID, lastNameID):
    return i18n.convert(tankmen.getNationConfig(nationID)['lastNames'][lastNameID])


def getFullUserName(nationID, firstNameID, lastNameID):
    return '%s %s' % (getFirstUserName(nationID, firstNameID), getLastUserName(nationID, lastNameID))


def getRoleUserName(role):
    return i18n.convert(tankmen.getSkillsConfig()[role]['userString'])


def getRoleIconName(role):
    return tankmen.getSkillsConfig()[role]['icon']


def getRoleBigIconPath(role):
    return '../maps/icons/tankmen/roles/big/%s' % getRoleIconName(role)


def getRoleMediumIconPath(role):
    return '../maps/icons/tankmen/roles/medium/%s' % getRoleIconName(role)


def getRoleSmallIconPath(role):
    return '../maps/icons/tankmen/roles/small/%s' % getRoleIconName(role)


def getRankUserName(nationID, rankID):
    return i18n.convert(tankmen.getNationConfig(nationID)['ranks'][rankID]['userString'])


def getIconName(nationID, iconID):
    return tankmen.getNationConfig(nationID)['icons'][iconID]


def getBarracksIconPath(nationID, iconID):
    return '../maps/icons/tankmen/icons/barracks/%s' % getIconName(nationID, iconID)


def getBigIconPath(nationID, iconID):
    return '../maps/icons/tankmen/icons/big/%s' % getIconName(nationID, iconID)


def getSmallIconPath(nationID, iconID):
    return '../maps/icons/tankmen/icons/small/%s' % getIconName(nationID, iconID)


def getRankIconName(nationID, rankID):
    return tankmen.getNationConfig(nationID)['ranks'][rankID]['icon']


def getRankBigIconPath(nationID, rankID):
    return '../maps/icons/tankmen/ranks/big/%s' % getRankIconName(nationID, rankID)


def getRankSmallIconPath(nationID, rankID):
    return '../maps/icons/tankmen/ranks/small/%s' % getRankIconName(nationID, rankID)


def getSkillIconName(skillName):
    return i18n.convert(tankmen.getSkillsConfig()[skillName]['icon'])


def getSkillBigIconPath(skillName):
    return '../maps/icons/tankmen/skills/big/%s' % getSkillIconName(skillName)


def getSkillSmallIconPath(skillName):
    return '../maps/icons/tankmen/skills/small/%s' % getSkillIconName(skillName)


def getSkillUserName(skillName):
    return tankmen.getSkillsConfig()[skillName]['userString']


def getSkillUserDescription(skillName):
    return tankmen.getSkillsConfig()[skillName]['description']


def calculateRoleLevel(startRoleLevel, freeXpValue = 0, typeID = (0, 0)):
    return __makeFakeTankmanDescr(startRoleLevel, freeXpValue, typeID).roleLevel


def calculateRankID(startRoleLevel, freeXpValue = 0, typeID = (0, 0)):
    return __makeFakeTankmanDescr(startRoleLevel, freeXpValue, typeID).rankID


def __makeFakeTankmanDescr(startRoleLevel, freeXpValue, typeID):
    vehType = vehicles.VehicleDescr(typeID=typeID).type
    tmanDescr = tankmen.TankmanDescr(tankmen.generateCompactDescr(tankmen.generatePassport(vehType.id[0], False), vehType.id[1], vehType.crewRoles[0][0], startRoleLevel))
    tmanDescr.addXP(freeXpValue)
    return tmanDescr
