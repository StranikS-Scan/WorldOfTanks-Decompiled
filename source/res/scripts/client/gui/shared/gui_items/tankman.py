# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/Tankman.py
from gui.Scaleform.locale.ITEM_TYPES import ITEM_TYPES
from helpers import i18n
from items import tankmen, vehicles, ITEM_TYPE_NAMES, sabaton_crew
from gui import nationCompareByIndex, TANKMEN_ROLES_ORDER_DICT
from gui.shared.utils.functions import getShortDescr
from gui.shared.gui_items import ItemsCollection, GUI_ITEM_TYPE
from gui.shared.gui_items.gui_item import HasStrCD, GUIItem
from items.components import skills_constants
from constants import SkinInvData
from items.vehicles import VEHICLE_CLASS_TAGS
from items.components.crewSkins_constants import NO_CREW_SKIN_ID

class CrewTypes(object):
    SKILL_100 = 100
    SKILL_75 = 75
    SKILL_50 = 50
    CURRENT = -1
    ALL = (SKILL_100,
     SKILL_75,
     SKILL_50,
     CURRENT)
    CREW_AVAILABLE_SKILLS = (SKILL_50, SKILL_75, SKILL_100)


class TankmenCollection(ItemsCollection):

    def _filterItem(self, item, nation=None, role=None, isInTank=None):
        if role is not None and item.descriptor.role != role:
            return False
        else:
            return False if isInTank is not None and item.isInTank != isInTank else ItemsCollection._filterItem(self, item, nation)


class TankmenComparator(object):

    def __init__(self, vehicleGetter=None):
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
    __slots__ = ('__descriptor', '_invID', '_nationID', '_itemTypeID', '_itemTypeName', '_combinedRoles', '_dismissedAt', '_isDismissed', '_areClassesCompatible', '_vehicleNativeDescr', '_vehicleInvID', '_vehicleDescr', '_vehicleBonuses', '_vehicleSlotIdx', '_skills', '_skillsMap', '_skinID')

    class ROLES(object):
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
    _NON_COMMANDER_SKILLS = skills_constants.ACTIVE_SKILLS.difference(skills_constants.COMMANDER_SKILLS)

    def __init__(self, strCompactDescr, inventoryID=-1, vehicle=None, dismissedAt=None, proxy=None):
        GUIItem.__init__(self, proxy)
        HasStrCD.__init__(self, strCompactDescr)
        self.__descriptor = None
        self._invID = inventoryID
        self._nationID = self.descriptor.nationID
        self._itemTypeID = GUI_ITEM_TYPE.TANKMAN
        self._itemTypeName = ITEM_TYPE_NAMES[self.itemTypeID]
        self._combinedRoles = (self.descriptor.role,)
        self._dismissedAt = dismissedAt
        self._isDismissed = self.dismissedAt is not None
        self._areClassesCompatible = False
        self._vehicleNativeDescr = vehicles.VehicleDescr(typeID=(self.nationID, self.descriptor.vehicleTypeID))
        self._vehicleInvID = -1
        self._vehicleDescr = None
        self._vehicleBonuses = dict()
        self._vehicleSlotIdx = -1
        if vehicle is not None:
            self._vehicleInvID = vehicle.invID
            self._vehicleDescr = vehicle.descriptor
            self._vehicleBonuses = dict(vehicle.bonuses)
            self._vehicleSlotIdx = vehicle.crewIndices.get(inventoryID, -1)
            crewRoles = self.vehicleDescr.type.crewRoles
            if -1 < self.vehicleSlotIdx < len(crewRoles):
                self._combinedRoles = crewRoles[self.vehicleSlotIdx]
            self._areClassesCompatible = bool(VEHICLE_CLASS_TAGS & self.vehicleDescr.type.tags & self.vehicleNativeDescr.type.tags)
        self._skills = self._buildSkills(proxy)
        self._skillsMap = self._buildSkillsMap()
        self._skinID = self._equippedSkinID(proxy)
        self.__cmp__ = TankmenComparator()
        return

    def _buildSkills(self, proxy):
        return [ getTankmanSkill(skill, self, proxy) for skill in self.descriptor.skills ]

    def _buildSkillsMap(self):
        return dict([ (skill.name, skill) for skill in self.skills ])

    def _equippedSkinID(self, proxy):
        if proxy is not None and proxy.inventory.isSynced():
            skinsPdata = proxy.inventory.getCacheValue(GUI_ITEM_TYPE.CREW_SKINS, {})
            tankmanSkins = skinsPdata[SkinInvData.OUTFITS]
            return tankmanSkins.get(self._invID, NO_CREW_SKIN_ID)
        else:
            return NO_CREW_SKIN_ID

    @property
    def invID(self):
        return self._invID

    @property
    def nationID(self):
        return self._nationID

    @property
    def itemTypeID(self):
        return self._itemTypeID

    @property
    def itemTypeName(self):
        return self._itemTypeName

    @property
    def combinedRoles(self):
        return self._combinedRoles

    @property
    def dismissedAt(self):
        return self._dismissedAt

    @property
    def isDismissed(self):
        return self._isDismissed

    @property
    def areClassesCompatible(self):
        return self._areClassesCompatible

    @property
    def vehicleNativeDescr(self):
        return self._vehicleNativeDescr

    @property
    def vehicleInvID(self):
        return self._vehicleInvID

    @property
    def vehicleDescr(self):
        return self._vehicleDescr

    @property
    def vehicleBonuses(self):
        return self._vehicleBonuses

    @property
    def vehicleSlotIdx(self):
        return self._vehicleSlotIdx

    @property
    def skills(self):
        return self._skills

    @property
    def skillsMap(self):
        return self._skillsMap

    @property
    def skinID(self):
        return self._skinID

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
        if self.__descriptor is None or self.__descriptor.dossierCompactDescr != self.strCD:
            self.__descriptor = tankmen.TankmanDescr(compactDescr=self.strCD)
        return self.__descriptor

    @property
    def isInTank(self):
        return self.vehicleDescr is not None

    @property
    def role(self):
        return self.descriptor.role

    @property
    def roleLevel(self):
        return self.descriptor.roleLevel

    @property
    def isFemale(self):
        return self.descriptor.isFemale

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

    def availableSkills(self, useCombinedRoles=False):
        if useCombinedRoles:
            availSkills = set()
            for role in self.combinedRoles:
                availSkills |= tankmen.SKILLS_BY_ROLES.get(role, set())

        else:
            availSkills = tankmen.SKILLS_BY_ROLES.get(self.descriptor.role, set())
        availSkills -= set(self.descriptor.skills)
        return availSkills

    def hasNewSkill(self, useCombinedRoles=False):
        availSkills = self.availableSkills(useCombinedRoles)
        return self.roleLevel == tankmen.MAX_SKILL_LEVEL and bool(availSkills) and (self.descriptor.lastSkillLevel == tankmen.MAX_SKILL_LEVEL or not self.skills)

    @property
    def newSkillCount(self):
        if self.hasNewSkill(useCombinedRoles=True):
            tmanDescr = tankmen.TankmanDescr(self.strCD)
            i = 0
            if self.role == self.ROLES.COMMANDER:
                skills_list = list(skills_constants.ACTIVE_SKILLS)
            else:
                skills_list = list(self._NON_COMMANDER_SKILLS)
            while 1:
                if tmanDescr.roleLevel == 100 and (tmanDescr.lastSkillLevel == 100 or not tmanDescr.skills) and skills_list:
                    skillname = skills_list.pop()
                    skillname not in tmanDescr.skills and tmanDescr.addSkill(skillname)
                    i += 1

            return (i, tmanDescr.lastSkillLevel)

    @property
    def efficiencyRoleLevel(self):
        factor, _ = (1, 0)
        if self.isInTank:
            factor, _ = self.descriptor.efficiencyOnVehicle(self.vehicleDescr)
        return round(self.roleLevel * factor)

    def getNextLevelXpCost(self):
        descr = self.descriptor
        if self.roleLevel != tankmen.MAX_SKILL_LEVEL or self.skills and descr.lastSkillLevel != tankmen.MAX_SKILL_LEVEL:
            lastSkillNumValue = descr.lastSkillNumber - descr.freeSkillsNumber
            if lastSkillNumValue == 0 or self.roleLevel != tankmen.MAX_SKILL_LEVEL:
                nextSkillLevel = self.roleLevel
            else:
                nextSkillLevel = descr.lastSkillLevel
            skillSeqNum = 0
            if self.roleLevel == tankmen.MAX_SKILL_LEVEL:
                skillSeqNum = lastSkillNumValue
            return descr.levelUpXpCost(nextSkillLevel, skillSeqNum) - descr.freeXP

    def getNextSkillXpCost(self):
        descr = self.descriptor
        if self.roleLevel != tankmen.MAX_SKILL_LEVEL or self.skills and descr.lastSkillLevel != tankmen.MAX_SKILL_LEVEL:
            lastSkillNumValue = descr.lastSkillNumber - descr.freeSkillsNumber
            if lastSkillNumValue == 0 or self.roleLevel != tankmen.MAX_SKILL_LEVEL:
                nextSkillLevel = self.roleLevel
            else:
                nextSkillLevel = descr.lastSkillLevel
            skillSeqNum = 0
            if self.roleLevel == tankmen.MAX_SKILL_LEVEL:
                skillSeqNum = lastSkillNumValue
            needXp = 0
            for level in xrange(nextSkillLevel, tankmen.MAX_SKILL_LEVEL):
                needXp += descr.levelUpXpCost(level, skillSeqNum)

            return needXp - descr.freeXP

    @property
    def isMaxRoleLevel(self):
        return self.roleLevel == tankmen.MAX_SKILL_LEVEL

    @property
    def vehicleNativeType(self):
        for tag in vehicles.VEHICLE_CLASS_TAGS.intersection(self.vehicleNativeDescr.type.tags):
            return tag

    def getSkillsToLearn(self):
        result = []
        commonSkills = []
        for skill in tankmen.COMMON_SKILLS:
            if skill not in self.descriptor.skills:
                commonSkills.append(self.__packSkill(getTankmanSkill(skill, tankman=self)))

        result.append({'id': 'common',
         'skills': commonSkills})
        for role in TANKMEN_ROLES_ORDER_DICT['plain']:
            roleSkills = tankmen.SKILLS_BY_ROLES.get(role, tuple())
            if role not in self.combinedRoles:
                continue
            skills = []
            for skill in roleSkills:
                if skill not in tankmen.COMMON_SKILLS and skill not in self.descriptor.skills:
                    skills.append(self.__packSkill(getTankmanSkill(skill)))

            result.append({'id': role,
             'skills': skills})

        return result

    def hasSkillToLearn(self):
        for skillsData in self.getSkillsToLearn():
            if skillsData['skills']:
                return True

        return False

    def isRestorable(self):
        return self.descriptor.isRestorable()

    def __packSkill(self, skillItem):
        return {'id': skillItem.name,
         'name': skillItem.userName,
         'desc': skillItem.shortDescription,
         'enabled': True,
         'tankmanID': self.invID}

    def __eq__(self, other):
        return False if other is None or not isinstance(other, Tankman) else self.invID == other.invID

    def __repr__(self):
        return 'Tankman<id:%d, nation:%d, vehicleID:%d>' % (self.invID, self.nationID, self.vehicleInvID)


class TankmanSkill(GUIItem):
    __slots__ = ('_name', '_isPerk', '_level', '_type', '_roleType', '_isActive', '_isEnable', '_isFemale', '_isPermanent')

    def __init__(self, skillName, tankman=None, proxy=None):
        super(TankmanSkill, self).__init__(proxy)
        self._name = skillName
        self._isPerk = self._name in tankmen.PERKS
        self._type = self.__getSkillType()
        self._level = 0
        if tankman is not None:
            tdescr = tankman.descriptor
            skills = tdescr.skills
            self._isFemale = tankman.isFemale
            self._isPermanent = False
            if self._name in skills:
                if skills.index(self._name) == len(skills) - 1:
                    self._level = tdescr.lastSkillLevel
                else:
                    self._level = tankmen.MAX_SKILL_LEVEL
                self._isPermanent = skills.index(self._name) < tdescr.freeSkillsNumber
            self._roleType = self.__getSkillRoleType(skillName)
            self._isActive = self.__getSkillActivity(tankman)
            self._isEnable = self.__getEnabledSkill(tankman)
        else:
            self._isFemale = False
            self._isPermanent = False
            self._roleType = None
            self._isActive = False
            self._isEnable = False
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
            return 'perk'

    @property
    def name(self):
        return self._name

    @property
    def isPerk(self):
        return self._isPerk

    @property
    def level(self):
        return self._level

    @property
    def type(self):
        return self._type

    @property
    def roleType(self):
        return self._roleType

    @property
    def isActive(self):
        return self._isActive

    @property
    def isEnable(self):
        return self._isEnable

    @property
    def isFemale(self):
        return self._isFemale

    @property
    def isPermanent(self):
        return self._isPermanent

    @property
    def userName(self):
        if self.name == 'brotherhood':
            if self.isPermanent:
                return i18n.makeString('#item_types:tankman/skills/brotherhood_permanent')
        return getSkillUserName(self.name)

    @property
    def description(self):
        if self.name == 'brotherhood':
            if self.isFemale:
                return i18n.makeString('#item_types:tankman/skills/brotherhood_female_descr')
            if self.isPermanent:
                return i18n.makeString('#item_types:tankman/skills/brotherhood_permanent_descr')
        return getSkillUserDescription(self.name)

    @property
    def shortDescription(self):
        return getShortDescr(self.description)

    @property
    def icon(self):
        return getSkillIconName(self.name)

    @property
    def bigIconPath(self):
        return '../maps/icons/tankmen/skills/big/%s' % self.icon

    @property
    def smallIconPath(self):
        return '../maps/icons/tankmen/skills/small/%s' % self.icon

    def __repr__(self):
        return 'TankmanSkill<name:%s, level:%d, isActive:%s>' % (self.name, self.level, str(self.isActive))


class SabatonTankmanSkill(TankmanSkill):

    def __init__(self, skillName, tankman=None, proxy=None):
        super(SabatonTankmanSkill, self).__init__(skillName, tankman, proxy)
        if skillName == 'brotherhood':
            self._isPermanent = True

    def getSkillIconName(self, skillName):
        return 'sabaton_brotherhood.png' if skillName == 'brotherhood' else i18n.convert(tankmen.getSkillsConfig().getSkill(skillName).icon)

    def getSkillUserName(self, skillName):
        return i18n.makeString(ITEM_TYPES.TANKMAN_SKILLS_BROTHERHOOD_SABATON) if skillName == 'brotherhood' else tankmen.getSkillsConfig().getSkill(skillName).userString

    @property
    def userName(self):
        return self.getSkillUserName(self._name)

    @property
    def icon(self):
        return self.getSkillIconName(self._name)


def getTankmanSkill(skillName, tankman=None, proxy=None):
    return SabatonTankmanSkill(skillName, tankman, proxy) if tankman and sabaton_crew.isSabatonCrew(tankman.descriptor) else TankmanSkill(skillName, tankman, proxy)


def getFirstUserName(nationID, firstNameID):
    return i18n.convert(tankmen.getNationConfig(nationID).getFirstName(firstNameID))


def getLastUserName(nationID, lastNameID):
    return i18n.convert(tankmen.getNationConfig(nationID).getLastName(lastNameID))


def getFullUserName(nationID, firstNameID, lastNameID):
    return '%s %s' % (getFirstUserName(nationID, firstNameID), getLastUserName(nationID, lastNameID))


def getRoleUserName(role):
    skillConf = tankmen.getSkillsConfig()
    skill = skillConf.getSkill(role)
    userString = skill.userString
    return i18n.convert(userString)


def getRoleIconName(role):
    return tankmen.getSkillsConfig().getSkill(role).icon


def getRoleBigIconPath(role):
    return '../maps/icons/tankmen/roles/big/%s' % getRoleIconName(role)


def getRoleMediumIconPath(role):
    return '../maps/icons/tankmen/roles/medium/%s' % getRoleIconName(role)


def getRoleSmallIconPath(role):
    return '../maps/icons/tankmen/roles/small/%s' % getRoleIconName(role)


def getRoleWhiteIconPath(role):
    return '../maps/icons/tankmen/roles/white/{}'.format(getRoleIconName(role))


def getRankUserName(nationID, rankID):
    return i18n.convert(tankmen.getNationConfig(nationID).getRank(rankID).userString)


def getIconName(nationID, iconID):
    return tankmen.getNationConfig(nationID).getIcon(iconID)


def getBarracksIconPath(nationID, iconID):
    return '../maps/icons/tankmen/icons/barracks/%s' % getIconName(nationID, iconID)


def getBigIconPath(nationID, iconID):
    return '../maps/icons/tankmen/icons/big/%s' % getIconName(nationID, iconID)


def getSmallIconPath(nationID, iconID):
    return '../maps/icons/tankmen/icons/small/%s' % getIconName(nationID, iconID)


def getRankIconName(nationID, rankID):
    return tankmen.getNationConfig(nationID).getRank(rankID).icon


def getRankBigIconPath(nationID, rankID):
    return '../maps/icons/tankmen/ranks/big/%s' % getRankIconName(nationID, rankID)


def getRankSmallIconPath(nationID, rankID):
    return '../maps/icons/tankmen/ranks/small/%s' % getRankIconName(nationID, rankID)


def getSkillIconName(skillName):
    return i18n.convert(tankmen.getSkillsConfig().getSkill(skillName).icon)


def getSkillBigIconPath(skillName):
    return '../maps/icons/tankmen/skills/big/%s' % getSkillIconName(skillName)


def getSkillSmallIconPath(skillName):
    return '../maps/icons/tankmen/skills/small/%s' % getSkillIconName(skillName)


def getSkillIconPath(skillName, size='big'):
    return '../maps/icons/tankmen/skills/{}/{}.png'.format(size, skillName)


def getCrewSkinIconBig(iconID):
    return '../maps/icons/tankmen/icons/big/crewSkins/%s' % iconID


def getCrewSkinNationPath(nationID):
    return '../maps/icons/tankmen/crewSkins/nations/{}.png'.format(nationID) if nationID is not None else ''


def getCrewSkinRolePath(roleID):
    return '../maps/icons/tankmen/roles/big/crewSkins/{}.png'.format(roleID) if roleID is not None else ''


def getCrewSkinIconSmall(iconID):
    return '../maps/icons/tankmen/icons/small/crewSkins/%s' % iconID


def getCrewSkinIconSmallWithoutPath(iconID):
    return 'crewSkins/%s' % iconID


def getSkillUserName(skillName):
    return tankmen.getSkillsConfig().getSkill(skillName).userString


def getSkillUserDescription(skillName):
    return tankmen.getSkillsConfig().getSkill(skillName).description


def calculateRoleLevel(startRoleLevel, freeXpValue=0, typeID=(0, 0)):
    return __makeFakeTankmanDescr(startRoleLevel, freeXpValue, typeID).roleLevel


def calculateRankID(startRoleLevel, freeXpValue=0, typeID=(0, 0)):
    return __makeFakeTankmanDescr(startRoleLevel, freeXpValue, typeID).rankID


def isSkillLearnt(skillName, vehicle):
    isCommonSkill = skillName in tankmen.COMMON_SKILLS
    return __isCommonSkillLearnt(skillName, vehicle) if isCommonSkill else __isPersonalSkillLearnt(skillName, vehicle)


def __isCommonSkillLearnt(skillName, vehicle):
    for _, tankman in vehicle.crew:
        if tankman is not None:
            if skillName in tankman.skillsMap:
                if tankman.skillsMap[skillName].level != tankmen.MAX_SKILL_LEVEL:
                    return False
            else:
                return False
        return False

    return True


def __isPersonalSkillLearnt(skillName, vehicle):
    for _, tankman in vehicle.crew:
        if tankman is not None:
            if skillName in tankman.skillsMap and tankman.skillsMap[skillName].level == tankmen.MAX_SKILL_LEVEL:
                return True

    return False


def __makeFakeTankmanDescr(startRoleLevel, freeXpValue, typeID):
    vehType = vehicles.VehicleDescr(typeID=typeID).type
    tmanDescr = tankmen.TankmanDescr(tankmen.generateCompactDescr(tankmen.generatePassport(vehType.id[0], False), vehType.id[1], vehType.crewRoles[0][0], startRoleLevel))
    tmanDescr.addXP(freeXpValue)
    return tmanDescr
