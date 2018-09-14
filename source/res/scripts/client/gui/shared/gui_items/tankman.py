# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/Tankman.py
from gui.Scaleform.locale.ITEM_TYPES import ITEM_TYPES
from helpers import i18n
from items import tankmen, vehicles, ITEM_TYPE_NAMES, sabaton_crew
from gui import nationCompareByIndex, TANKMEN_ROLES_ORDER_DICT
from gui.shared.utils.functions import getShortDescr
from gui.shared.gui_items import ItemsCollection, GUI_ITEM_TYPE
from gui.shared.gui_items.gui_item import HasStrCD, GUIItem
from items.vehicles import VEHICLE_CLASS_TAGS

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
    ROLES = tankmen.TANKMEN_ROLES
    TANKMEN_ROLES_ORDER = tankmen.TANKMEN_ROLES_ORDER

    def __init__(self, strCompactDescr, inventoryID=-1, vehicle=None, dismissedAt=None, proxy=None):
        GUIItem.__init__(self, proxy)
        HasStrCD.__init__(self, strCompactDescr)
        self.__descriptor = None
        self.invID = inventoryID
        self.nationID = self.descriptor.nationID
        self.itemTypeID = GUI_ITEM_TYPE.TANKMAN
        self.itemTypeName = ITEM_TYPE_NAMES[self.itemTypeID]
        self.combinedRoles = (self.descriptor.role,)
        self.dismissedAt = dismissedAt
        self.isDismissed = self.dismissedAt is not None
        self.areClassesCompatible = False
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
            self.areClassesCompatible = len(VEHICLE_CLASS_TAGS & self.vehicleDescr.type.tags & self.vehicleNativeDescr.type.tags) > 0
        self.skills = self._buildSkills(proxy)
        self.skillsMap = self._buildSkillsMap()
        if proxy is not None:
            pass
        self.__cmp__ = TankmenComparator()
        return

    def _buildSkills(self, proxy):
        return [ getTankmanSkill(skill, self, proxy) for skill in self.descriptor.skills ]

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
        """ Get list of skills which tankman can learn
        :param useCombinedRoles: get skills for combined roles (True/False)
        :return: List with text name of skills, e.g. ['brotherhood', 'gunner_gunsmith', 'gunner_smoothTurret']
        """
        if useCombinedRoles:
            availSkills = set()
            for role in self.combinedRoles:
                availSkills |= tankmen.SKILLS_BY_ROLES.get(role, set())

        else:
            availSkills = tankmen.SKILLS_BY_ROLES.get(self.descriptor.role, set())
        availSkills -= set(self.descriptor.skills)
        return availSkills

    def hasNewSkill(self, useCombinedRoles=False):
        """ Has tankman new skills for learn
        :param useCombinedRoles: take in account combined roles skills, (e.g. commander and radioman skills)
        :return: True/False
        """
        availSkills = self.availableSkills(useCombinedRoles)
        return self.roleLevel == tankmen.MAX_SKILL_LEVEL and len(availSkills) > 0 and (self.descriptor.lastSkillLevel == tankmen.MAX_SKILL_LEVEL or not len(self.skills))

    @property
    def newSkillCount(self):
        if self.hasNewSkill(useCombinedRoles=True):
            tmanDescr = tankmen.TankmanDescr(self.strCD)
            i = 0
            skills_list = list(tankmen.ACTIVE_SKILLS)
            while 1:
                if tmanDescr.roleLevel == 100 and (tmanDescr.lastSkillLevel == 100 or len(tmanDescr.skills) == 0) and len(skills_list) > 0:
                    skillname = skills_list.pop()
                    skillname not in tmanDescr.skills and tmanDescr.addSkill(skillname)
                    i += 1

            return (i, tmanDescr.lastSkillLevel)

    @property
    def efficiencyRoleLevel(self):
        factor, addition = (1, 0)
        if self.isInTank:
            factor, addition = self.descriptor.efficiencyOnVehicle(self.vehicleDescr)
        return round(self.roleLevel * factor)

    def getNextLevelXpCost(self):
        """ Calculate the XP cost to raise a skill by one point
        :return: integer -> value of xp cost
        """
        descr = self.descriptor
        if self.roleLevel != tankmen.MAX_SKILL_LEVEL or len(self.skills) and descr.lastSkillLevel != tankmen.MAX_SKILL_LEVEL:
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
        """ Calculate the XP cost to raise a skill to MAX_SKILL_LEVEL
        :return: integer -> value of xp cost
        """
        descr = self.descriptor
        if self.roleLevel != tankmen.MAX_SKILL_LEVEL or len(self.skills) and descr.lastSkillLevel != tankmen.MAX_SKILL_LEVEL:
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

    def __init__(self, skillName, tankman=None, proxy=None):
        super(TankmanSkill, self).__init__(proxy)
        self.name = skillName
        self.isPerk = self.name in tankmen.PERKS
        self.level = 0
        self.type = self.__getSkillType()
        self.roleType = None
        self.isActive = False
        self.isEnable = False
        self.isFemale = False
        self.isPermanent = False
        if tankman is not None:
            tdescr = tankman.descriptor
            skills = tdescr.skills
            self.isFemale = tankman.isFemale
            if self.name in skills:
                if skills.index(self.name) == len(skills) - 1:
                    self.level = tdescr.lastSkillLevel
                else:
                    self.level = tankmen.MAX_SKILL_LEVEL
                self.isPermanent = skills.index(self.name) < tdescr.freeSkillsNumber
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

    def getSkillIconName(self, skillName):
        """Change icon for brotherhood skill
        :return:
        """
        return 'sabaton_brotherhood.png' if skillName == 'brotherhood' else i18n.convert(tankmen.getSkillsConfig()[skillName]['icon'])

    def getSkillUserName(self, skillName):
        """Change description for brotherhood skill
        :param skillName:
        :return:
        """
        return i18n.makeString(ITEM_TYPES.TANKMAN_SKILLS_BROTHERHOOD_SABATON) if skillName == 'brotherhood' else tankmen.getSkillsConfig()[skillName]['userString']

    @property
    def userName(self):
        return self.getSkillUserName(self.name)

    @property
    def icon(self):
        return self.getSkillIconName(self.name)


def getTankmanSkill(skillName, tankman=None, proxy=None):
    return SabatonTankmanSkill(skillName, tankman, proxy) if tankman and sabaton_crew.isSabatonCrew(tankman.descriptor) else TankmanSkill(skillName, tankman, proxy)


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


def getRoleWhiteIconPath(role):
    return '../maps/icons/tankmen/roles/white/{}'.format(getRoleIconName(role))


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


def calculateRoleLevel(startRoleLevel, freeXpValue=0, typeID=(0, 0)):
    return __makeFakeTankmanDescr(startRoleLevel, freeXpValue, typeID).roleLevel


def calculateRankID(startRoleLevel, freeXpValue=0, typeID=(0, 0)):
    return __makeFakeTankmanDescr(startRoleLevel, freeXpValue, typeID).rankID


def isSkillLearnt(skillName, vehicle):
    """
    Check if the provided skill is learnt (100%) on the vehicle.
    For common skill - the whole crew will be checked
    :param skillName: string with skill
    :param vehicle: instance of gui_item.Vehicle
    :return: boolean result
    """
    isCommonSkill = skillName in tankmen.COMMON_SKILLS
    if isCommonSkill:
        return __isCommonSkillLearnt(skillName, vehicle)
    else:
        return __isPersonalSkillLearnt(skillName, vehicle)


def __isCommonSkillLearnt(skillName, vehicle):
    """
    Check if the provide COMMON skill is learnt. It means each member in crew
    should learn the skill
    :param skillName: string with skill
    :param vehicle: instance of gui_item.Vehicle
    :return: boolean result
    """
    for roleIndex, tankman in vehicle.crew:
        if tankman is not None:
            if skillName in tankman.skillsMap:
                if tankman.skillsMap[skillName].level != tankmen.MAX_SKILL_LEVEL:
                    return False
            else:
                return False
        return False

    return True


def __isPersonalSkillLearnt(skillName, vehicle):
    """
    Check if the personal skill is learnt for one member in crew.
    :param skillName: string with skill
    :param vehicle: vehicle: instance of gui_item.Vehicle
    :return: boolean result
    """
    for roleIndex, tankman in vehicle.crew:
        if tankman is not None:
            if skillName in tankman.skillsMap and tankman.skillsMap[skillName].level == tankmen.MAX_SKILL_LEVEL:
                return True

    return False


def __makeFakeTankmanDescr(startRoleLevel, freeXpValue, typeID):
    vehType = vehicles.VehicleDescr(typeID=typeID).type
    tmanDescr = tankmen.TankmanDescr(tankmen.generateCompactDescr(tankmen.generatePassport(vehType.id[0], False), vehType.id[1], vehType.crewRoles[0][0], startRoleLevel))
    tmanDescr.addXP(freeXpValue)
    return tmanDescr
