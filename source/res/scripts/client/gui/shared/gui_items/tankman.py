# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/Tankman.py
import typing
from constants import SkinInvData
from debug_utils import LOG_WARNING
from shared_utils import findFirst
from gui import nationCompareByIndex, TANKMEN_ROLES_ORDER_DICT
from gui.Scaleform.genConsts.SKILLS_CONSTANTS import SKILLS_CONSTANTS
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.gui_items import ItemsCollection, GUI_ITEM_TYPE, collectKpi
from gui.shared.gui_items.gui_item import HasStrCD, GUIItem
from gui.shared.skill_parameters import SKILLS
from gui.shared.skill_parameters.skills_packers import g_skillPackers, packBase
from helpers import dependency
from helpers import i18n
from items import tankmen, vehicles, ITEM_TYPE_NAMES, special_crew
from items.artefacts import SkillEquipment
from items.components import skills_constants
from items.components.component_constants import EMPTY_STRING
from items.components.crew_skins_constants import NO_CREW_SKIN_ID
from items.components.skills_constants import SkillTypeName
from items.vehicles import VEHICLE_CLASS_TAGS
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from typing import Sequence, List, Tuple
    from items.readers.skills_readers import SkillDescrsArg
    from gui.shared.gui_items.Vehicle import Vehicle

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


BROTHERHOOD_SKILL_NAME = 'brotherhood'

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


class Tankman(GUIItem):
    _itemsCache = dependency.descriptor(IItemsCache)
    __slots__ = ('__descriptor', '_invID', '_nationID', '_itemTypeID', '_itemTypeName', '_combinedRoles', '_dismissedAt', '_isDismissed', '_areClassesCompatible', '_vehicleNativeDescr', '_vehicleInvID', '_vehicleDescr', '_vehicleBonuses', '_vehicleSlotIdx', '_skills', '_skillsMap', '_skinID', '_comparator', '__brotherhoodMarkedAsActive')

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

    def __init__(self, strCompactDescr, inventoryID=-1, vehicle=None, dismissedAt=None, proxy=None, vehicleSlotIdx=-1):
        super(Tankman, self).__init__(strCD=HasStrCD(strCompactDescr))
        self.__descriptor = None
        self._invID = inventoryID
        self._nationID = self.descriptor.nationID
        self._itemTypeID = GUI_ITEM_TYPE.TANKMAN
        self._itemTypeName = ITEM_TYPE_NAMES[self.itemTypeID]
        self._combinedRoles = (self.descriptor.role,)
        self._dismissedAt = dismissedAt
        self._isDismissed = self.dismissedAt is not None
        self._areClassesCompatible = False
        self.__brotherhoodMarkedAsActive = False
        self._vehicleNativeDescr = vehicles.VehicleDescr(typeID=(self.nationID, self.descriptor.vehicleTypeID))
        self._vehicleInvID = -1
        self._vehicleDescr = None
        self._vehicleBonuses = dict()
        self._vehicleSlotIdx = vehicleSlotIdx
        if vehicle is not None:
            self._vehicleInvID = vehicle.invID
            self._vehicleDescr = vehicle.descriptor
            self._vehicleBonuses = dict(vehicle.bonuses)
            self._vehicleSlotIdx = vehicle.crewIndices.get(inventoryID, self._vehicleSlotIdx)
            crewRoles = self.vehicleDescr.type.crewRoles
            if -1 < self.vehicleSlotIdx < len(crewRoles):
                self._combinedRoles = crewRoles[self.vehicleSlotIdx]
            self._areClassesCompatible = bool(VEHICLE_CLASS_TAGS & self.vehicleDescr.type.tags & self.vehicleNativeDescr.type.tags)
        self._skills = self._buildSkills(proxy)
        self._skillsMap = self._buildSkillsMap()
        self._skinID = self._equippedSkinID(proxy)
        self._comparator = TankmenComparator()
        return

    def __cmp__(self, other):
        return self._comparator(self, other)

    def _buildSkills(self, proxy):
        return [ getTankmanSkill(skill, self, proxy) for skill in self.descriptor.skills if skill != 'any' ]

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
    def chosenFreeSkillsCount(self):
        return self.descriptor.freeSkillsNumber - self.newFreeSkillsCount

    @property
    def freeSkills(self):
        return self._skills[:self.chosenFreeSkillsCount]

    @property
    def earnedSkills(self):
        return self._skills[self.chosenFreeSkillsCount:]

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
        levelIncrease, (commBonus, brothersBonus, eqsBonus, optDevsBonus) = self.crewLevelIncrease
        realRoleLevel = effRoleLevel + levelIncrease
        return (realRoleLevel, (commBonus,
          brothersBonus,
          eqsBonus,
          optDevsBonus,
          penalty))

    @property
    def specialityFactor(self):
        factor = 1
        if self.isInTank:
            factor = self.descriptor.efficiencyOnVehicle(self.vehicleDescr)
        return factor

    @property
    def crewLevelIncrease(self):
        commBonus = self.vehicleBonuses.get('commander', 0)
        if self.descriptor.role == self.ROLES.COMMANDER:
            commBonus = 0
        brothersBonus = self.vehicleBonuses.get('brotherhood', 0)
        eqsBonus = self.vehicleBonuses.get('equipment', 0)
        optDevsBonus = self.vehicleBonuses.get('optDevices', 0)
        levelIncrease = commBonus + brothersBonus + eqsBonus + optDevsBonus
        return (levelIncrease, (commBonus,
          brothersBonus,
          eqsBonus,
          optDevsBonus))

    @property
    def descriptor(self):
        if self.__descriptor is None or self.__descriptor.dossierCompactDescr != self.strCD:
            self.__descriptor = tankmen.TankmanDescr(compactDescr=self.strCD)
        return self.__descriptor

    @property
    def isInTank(self):
        return self.vehicleDescr is not None

    @property
    def isInSkin(self):
        return self.skinID != NO_CREW_SKIN_ID

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
    def extensionLessIcon(self):
        return getExtensionLessIconName(self.nationID, self.descriptor.iconID)

    @property
    def barracksIconPath(self):
        return getBarracksIconPath(self.nationID, self.descriptor.iconID)

    @property
    def smallIconPath(self):
        return getSmallIconPath(self.nationID, self.descriptor.iconID)

    @property
    def iconRank(self):
        return getRankIconName(self.nationID, self.descriptor.rankID)

    @property
    def iconRole(self):
        return getRoleIconName(self.descriptor.role)

    @property
    def extensionLessIconRole(self):
        return getExtensionLessRoleIconName(self.descriptor.role)

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
        availSkills -= set(skills_constants.UNLEARNABLE_SKILLS)
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
                skills_list = list(skills_constants.LEARNABLE_ACTIVE_SKILLS)
            else:
                skills_list = list(self._NON_COMMANDER_SKILLS)
            while 1:
                if tmanDescr.roleLevel == 100 and (tmanDescr.lastSkillLevel == 100 or not tmanDescr.skills) and skills_list:
                    skillname = skills_list.pop()
                    skillname not in tmanDescr.skills and tmanDescr.addSkill(skillname)
                    i += 1

            return (i, tmanDescr.lastSkillLevel)

    @property
    def newFreeSkillsCount(self):
        return self.descriptor.freeSkills.count('any')

    @property
    def efficiencyRoleLevel(self):
        return round(self.roleLevel * self.specialityFactor)

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
    def isMaxRoleEfficiency(self):
        return self.efficiencyRoleLevel == tankmen.MAX_SKILL_LEVEL

    @property
    def vehicleNativeType(self):
        for tag in vehicles.VEHICLE_CLASS_TAGS.intersection(self.vehicleNativeDescr.type.tags):
            return tag

    def canLearnSkills(self):
        if self.isInTank:
            vehicle = self._itemsCache.items.getVehicle(self.vehicleInvID)
            if vehicle.isLocked:
                return False
        return False if self.isDismissed else True

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
                if skill not in tankmen.COMMON_SKILLS and skill not in self.descriptor.skills and skill not in skills_constants.UNLEARNABLE_SKILLS:
                    skills.append(self.__packSkill(getTankmanSkill(skill)))

            result.append({'id': role,
             'skills': skills})

        return result

    def getFreeSkillsToLearn(self):
        result = []
        commonSkills = []
        for skill in tankmen.COMMON_SKILLS:
            if skill not in self.descriptor.freeSkills:
                commonSkills.append(self.__packSkill(getTankmanSkill(skill, tankman=self)))

        result.append({'id': 'common',
         'skills': commonSkills})
        roleSkills = tankmen.SKILLS_BY_ROLES.get(self.role, tuple())
        skills = []
        for skill in roleSkills:
            if skill not in tankmen.COMMON_SKILLS and skill not in self.descriptor.freeSkills and skill not in skills_constants.UNLEARNABLE_SKILLS:
                skills.append(self.__packSkill(getTankmanSkill(skill)))

        result.append({'id': self.role,
         'skills': skills})
        return result

    def hasSkillToLearn(self):
        for skillsData in self.getSkillsToLearn():
            if skillsData['skills']:
                return True

        return False

    def roles(self):
        return self.vehicleDescr.type.crewRoles[self.vehicleSlotIdx] if self.isInTank else self.rolesInNativeVehicle()

    def rolesInNativeVehicle(self):
        for roles in self.vehicleNativeDescr.type.crewRoles:
            if self.role in roles:
                return roles

        return (self.role,)

    def getKpi(self, vehicle):
        return collectKpi(self.descriptor, vehicle)

    def isRestorable(self):
        return self.descriptor.isRestorable()

    def brotherhoodIsActive(self):
        return self.vehicleBonuses.get(BROTHERHOOD_SKILL_NAME, 0) > 0 or self.__brotherhoodMarkedAsActive

    def setBrotherhoodActivity(self, active):
        self.__brotherhoodMarkedAsActive = active

    def rebuildSkills(self, proxy=None):
        self._skills = self._buildSkills(proxy)
        self._skillsMap = self._buildSkillsMap()

    def updateBonusesFromVehicle(self, vehicle):
        if vehicle:
            self._vehicleBonuses = dict(vehicle.bonuses)

    def __packSkill(self, skillItem):
        return {'id': skillItem.name,
         'iconName': skillItem.extensionLessIconName,
         'name': skillItem.userName,
         'desc': skillItem.shortDescription,
         'enabled': True,
         'tankmanID': self.invID,
         'isSituational': skillItem.isSituational}

    def __eq__(self, other):
        return False if other is None or not isinstance(other, Tankman) else self.invID == other.invID

    def __repr__(self):
        return 'Tankman<id:%d, nation:%d, vehicleID:%d>' % (self.invID, self.nationID, self.vehicleInvID)


class TankmanSkill(GUIItem):
    __slots__ = ('_name', '_level', '_roleType', '_isEnable', '_isFemale', '_isPermanent', '_customName', '_isAlreadyEarned', '_packer', '_typeName')
    _CUSTOM_NAME_EXT = ''

    def __init__(self, skillName, tankman=None, proxy=None):
        super(TankmanSkill, self).__init__(proxy)
        self._name = skillName
        self._level = 0
        self._typeName = getSkillTypeName(skillName)
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
            self._isEnable = self.__getEnabledSkill(tankman)
        else:
            self._isFemale = False
            self._isPermanent = False
            self._roleType = None
            self._isEnable = False
        self._packer = g_skillPackers.get(self._name, packBase)
        self._customName = ''
        if self._CUSTOM_NAME_EXT:
            customName = '_'.join((self._CUSTOM_NAME_EXT, BROTHERHOOD_SKILL_NAME))
            if skillName in (BROTHERHOOD_SKILL_NAME, customName):
                self._customName = customName
                self._name = BROTHERHOOD_SKILL_NAME
        self._isAlreadyEarned = self.name in tankman.descriptor.earnedSkills or self._isPermanent if tankman is not None else False
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

    @property
    def name(self):
        return self._name

    @property
    def level(self):
        return self._level

    @property
    def roleType(self):
        return self._roleType

    @property
    def isCommon(self):
        return self.name in tankmen.COMMON_SKILLS

    @property
    def typeName(self):
        return self._typeName

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
    def isSituational(self):
        return self._typeName is SkillTypeName.SITUATIONAL

    @property
    def userName(self):
        if self._customName:
            resStr = '_'.join((self._name, self._CUSTOM_NAME_EXT))
            return backport.text(R.strings.crew_perks.dyn(resStr).name())
        return getSkillUserName(self.name)

    @property
    def isAlreadyEarned(self):
        return self._isAlreadyEarned

    @property
    def description(self):
        return getSkillUserDescription(self.name)

    @property
    def shortDescription(self):
        return getSkillUserDescription(self.name)

    @property
    def maxLvlDescription(self):
        return getSkillMaxLvlDescription(self.name)

    @property
    def currentLvlDescription(self):
        return getSkillCurrentLvlDescription(self.name) + backport.text(R.strings.item_types.tankman.skills.permanent_descr()) if self.isPermanent else getSkillCurrentLvlDescription(self.name)

    @property
    def altDescription(self):
        return getSkillAltDescription(self.name)

    @property
    def altInfo(self):
        return getSkillAltInfo(self.name)

    @property
    def icon(self):
        if self._name == SKILLS_CONSTANTS.TYPE_NEW_SKILL:
            iconName = '{}.png'.format(self.name)
        else:
            iconName = getSkillIconName(self.name)
        if self._customName:
            iconName = '{}_{}'.format(self._CUSTOM_NAME_EXT, iconName)
        return iconName

    @property
    def extensionLessIconName(self):
        return self.icon[:-len('.png')]

    @property
    def bigIconPath(self):
        root = R.images.gui.maps.icons.tankmen.skills.big.dyn(self.extensionLessIconName)
        if root.isValid():
            return backport.image(root())
        LOG_WARNING('no {} image in gui.maps.icons.tankmen.skills.big'.format(self.icon))
        return EMPTY_STRING

    @property
    def smallIconPath(self):
        root = R.images.gui.maps.icons.tankmen.skills.small.dyn(self.extensionLessIconName)
        if root.isValid():
            return backport.image(root())
        LOG_WARNING('no {} image in gui.maps.icons.tankmen.skills.small'.format(self.extensionLessIconName))
        return EMPTY_STRING

    def getMaxLvlDescription(self):
        skillDescArgs = getSkillDescrArgs(self.name)
        skillParams = self._packer(skillDescArgs, tankmen.MAX_SKILL_LEVEL)
        keyArgs = skillParams.get('keyArgs', {})
        return self.maxLvlDescription % keyArgs

    def getCurrentLvlDescription(self, skillLvl=None):
        skillDescArgs = getSkillDescrArgs(self.name)
        skillParams = self._packer(skillDescArgs, skillLvl if skillLvl is not None else self.level)
        keyArgs = skillParams.get('keyArgs', {})
        return self.currentLvlDescription % keyArgs

    def __repr__(self):
        return '{cls}<name:{name}, level:{level}, isActive:{isActive}>'.format(cls=self.__class__.__name__, name=self.name, level=self.level, isActive=str(self.isActive))


class SabatonTankmanSkill(TankmanSkill):
    __slots__ = ()
    _CUSTOM_NAME_EXT = 'sabaton'


class OffspringTankmanSkill(TankmanSkill):
    __slots__ = ()
    _CUSTOM_NAME_EXT = 'offspring'


class YhaTankmanSkill(TankmanSkill):
    __slots__ = ()
    _CUSTOM_NAME_EXT = 'yha'


class WitchesTankmanSkill(TankmanSkill):
    __slots__ = ()
    _CUSTOM_NAME_EXT = 'witches'


def getTankmanSkill(skillName, tankman=None, proxy=None):
    if tankman is not None:
        if special_crew.isSabatonCrew(tankman.descriptor):
            return SabatonTankmanSkill(skillName, tankman, proxy)
        if special_crew.isOffspringCrew(tankman.descriptor):
            return OffspringTankmanSkill(skillName, tankman, proxy)
        if special_crew.isYhaCrew(tankman.descriptor):
            return YhaTankmanSkill(skillName, tankman, proxy)
        if special_crew.isWitchesCrew(tankman.descriptor):
            return WitchesTankmanSkill(skillName, tankman, proxy)
    return TankmanSkill(skillName, tankman, proxy)


def getFirstUserName(nationID, firstNameID):
    return i18n.convert(tankmen.getNationConfig(nationID).getFirstName(firstNameID))


def getLastUserName(nationID, lastNameID):
    return i18n.convert(tankmen.getNationConfig(nationID).getLastName(lastNameID))


def getFullUserName(nationID, firstNameID, lastNameID):
    firstUserName = getFirstUserName(nationID, firstNameID)
    lastUserName = getLastUserName(nationID, lastNameID)
    return ('%s %s' % (firstUserName, lastUserName)).strip()


def getRoleUserName(role):
    skillConf = tankmen.getSkillsConfig()
    skill = skillConf.getSkill(role)
    userString = skill.userString
    return i18n.convert(userString)


def getRoleIconName(role):
    return tankmen.getSkillsConfig().getSkill(role).icon


def getExtensionLessRoleIconName(role):
    return tankmen.getSkillsConfig().getSkill(role).extensionLessIcon


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


def getExtensionLessIconName(nationID, iconID):
    return tankmen.getNationConfig(nationID).getExtensionLessIcon(iconID)


def getIconName(nationID, iconID):
    return tankmen.getNationConfig(nationID).getIcon(iconID)


def getDynIconName(iconName):
    return iconName.replace('-', '_').rsplit('.', 1)[0]


def getBarracksIconPath(nationID, iconID):
    iconName = getDynIconName(getExtensionLessIconName(nationID, iconID))
    dynAccessor = R.images.gui.maps.icons.tankmen.icons.barracks.dyn(iconName)
    return backport.image(dynAccessor()) if dynAccessor.isValid() else backport.image(R.images.gui.maps.icons.tankmen.icons.barracks.tankman())


def getBigIconPath(nationID, iconID):
    iconName = getDynIconName(getExtensionLessIconName(nationID, iconID))
    dynAccessor = R.images.gui.maps.icons.tankmen.icons.big.dyn(iconName)
    return backport.image(dynAccessor()) if dynAccessor.isValid() else backport.image(R.images.gui.maps.icons.tankmen.icons.big.tankman())


def getSmallIconPath(nationID, iconID):
    iconName = getDynIconName(getExtensionLessIconName(nationID, iconID))
    dynAccessor = R.images.gui.maps.icons.tankmen.icons.small.dyn(iconName)
    return backport.image(dynAccessor()) if dynAccessor.isValid() else backport.image(R.images.gui.maps.icons.tankmen.icons.small.tankman())


def getRankIconName(nationID, rankID):
    return tankmen.getNationConfig(nationID).getRank(rankID).icon


def getRankBigIconPath(nationID, rankID):
    return '../maps/icons/tankmen/ranks/big/%s' % getRankIconName(nationID, rankID)


def getRankSmallIconPath(nationID, rankID):
    return '../maps/icons/tankmen/ranks/small/%s' % getRankIconName(nationID, rankID)


def getSkillIconName(skillName):
    return i18n.convert(tankmen.getSkillsConfig().getSkill(skillName).icon)


def getExtensionLessSkillIconName(skillName):
    return tankmen.getSkillsConfig().getSkill(skillName).icon[:-len('.png')]


def getSkillBigIconPath(skillName):
    root = R.images.gui.maps.icons.tankmen.skills.big.dyn(getExtensionLessSkillIconName(skillName))
    if root.isValid():
        return backport.image(root())
    LOG_WARNING('no {} image in gui.maps.icons.tankmen.skills.big'.format(getExtensionLessSkillIconName(skillName)))
    return EMPTY_STRING


def getSkillSmallIconPath(skillName):
    root = R.images.gui.maps.icons.tankmen.skills.small.dyn(getExtensionLessSkillIconName(skillName))
    if root.isValid():
        return backport.image(root())
    LOG_WARNING('no {} image in gui.maps.icons.tankmen.skills.small'.format(getExtensionLessSkillIconName(skillName)))
    return EMPTY_STRING


def getSkillIconPath(skillName, size='big'):
    sizeRoot = R.images.gui.maps.icons.tankmen.skills.dyn(size)
    if not sizeRoot.isValid():
        LOG_WARNING('no {} size in gui.maps.icons.tankmen.skills'.format(size))
        return EMPTY_STRING
    icon = sizeRoot.dyn(getExtensionLessSkillIconName(skillName))
    if icon.isValid():
        return backport.image(icon())
    LOG_WARNING('no {} image in gui.maps.icons.tankmen.skills.{} '.format(getExtensionLessSkillIconName(skillName), size))
    return EMPTY_STRING


def getCrewSkinIconBig(iconID):
    return backport.image(R.images.gui.maps.icons.tankmen.icons.big.crewSkins.dyn(iconID)())


def getCrewSkinNationPath(nationID):
    return backport.image(R.images.gui.maps.icons.tankmen.crewSkins.nations.dyn(nationID)()) if nationID else ''


def getCrewSkinRolePath(roleID):
    return backport.image(R.images.gui.maps.icons.tankmen.roles.big.crewSkins.dyn(roleID)()) if roleID else ''


def getCrewSkinIconSmall(iconID):
    return backport.image(R.images.gui.maps.icons.tankmen.icons.small.crewSkins.dyn(iconID)())


def getCrewSkinIconSmallWithoutPath(iconID):
    fullPath = backport.image(R.images.gui.maps.icons.tankmen.icons.small.crewSkins.dyn(iconID)())
    return '/'.join(fullPath.rsplit('/')[-2:])


def getSkillUserName(skillName):
    return tankmen.getSkillsConfig().getSkill(skillName).userString


def getSkillUserDescription(skillName):
    return tankmen.getSkillsConfig().getSkill(skillName).description


def getSkillMaxLvlDescription(skillName):
    return tankmen.getSkillsConfig().getSkill(skillName).maxLvlDescription


def getSkillCurrentLvlDescription(skillName):
    return tankmen.getSkillsConfig().getSkill(skillName).currentLvlDescription


def getSkillAltDescription(skillName):
    return tankmen.getSkillsConfig().getSkill(skillName).altDescription


def getSkillAltInfo(skillName):
    return tankmen.getSkillsConfig().getSkill(skillName).altInfo


def getSkillDescrArgs(skillName):
    return tankmen.getSkillsConfig().getSkill(skillName).uiSettings.descrArgs


def getSkillSituational(skillName):
    return tankmen.getSkillsConfig().getSkill(skillName).situational


def getSkillTypeName(skillName):
    return tankmen.getSkillsConfig().getSkill(skillName).typeName


def calculateRoleLevel(startRoleLevel, freeXpValue=0, typeID=(0, 0)):
    return __makeFakeTankmanDescr(startRoleLevel, freeXpValue, typeID).roleLevel


def calculateRankID(startRoleLevel, freeXpValue=0, typeID=(0, 0), skills=(), freeSkills=(), lastSkillLevel=tankmen.MAX_SKILL_LEVEL):
    return __makeFakeTankmanDescr(startRoleLevel, freeXpValue, typeID, skills, freeSkills, lastSkillLevel).rankID


def __tankmanHasSkill(tankman, skillName):
    if tankman is None:
        return False
    else:
        return False if skillName not in tankman.skillsMap else True


def __getPersonalSkillLearningProgress(tankman, skillName):
    return tankman.skillsMap[skillName].level if __tankmanHasSkill(tankman, skillName) else tankmen.NO_SKILL


def isSkillLearnt(skillName, vehicle):
    isCommonSkill = skillName in tankmen.COMMON_SKILLS
    return __isCommonSkillLearnt(skillName, vehicle) if isCommonSkill else __isPersonalSkillLearnt(skillName, vehicle)


def __isCommonSkillLearnt(skillName, vehicle):
    for _, tankman in vehicle.crew:
        if not __tankmanHasSkill(tankman, skillName):
            return False
        if tankman.skillsMap[skillName].level != tankmen.MAX_SKILL_LEVEL:
            return False

    return True


def __isPersonalSkillLearnt(skillName, vehicle):
    if not vehicle.crew:
        return True
    for _, tankman in vehicle.crew:
        if not __tankmanHasSkill(tankman, skillName):
            continue
        if tankman.skillsMap[skillName].level == tankmen.MAX_SKILL_LEVEL:
            return True

    return False


def crewMemberRealSkillLevel(vehicle, skillName, role, commonWithIncrease=True):
    shouldIncrease = skillName not in tankmen.COMMON_SKILLS or commonWithIncrease and skillName != SKILLS.BROTHERHOOD
    booster = getBattleBooster(vehicle, skillName) if shouldIncrease else None
    tankmenSkillLevels = [ tankmanPersonalSkillLevel(tankman, skillName, booster, shouldIncrease) for _, tankman in vehicle.crew if tankman and (role in tankman.combinedRoles or skillName in tankmen.COMMON_SKILLS) ]
    return SKILL_LEVEL_PROCESSORS.get(skillName, DEFAULT_LEVEL_PROCESSOR)(vehicle.crew, tankmenSkillLevels)


def tankmanPersonalSkillLevel(tankman, skillName, booster=None, withIncrease=True):
    progress = __getPersonalSkillLearningProgress(tankman, skillName)
    if not (progress == tankmen.NO_SKILL and booster is None):
        if withIncrease:
            return _getSkillLevelWithIncrease(booster, progress, tankman)
        if progress != tankmen.NO_SKILL:
            return tankman.skillsMap[skillName].level
    return progress


def _getSkillLevelWithIncrease(booster, skillProgress, tankman):
    specialitySkillLevel = skillProgress * tankman.specialityFactor
    if booster is None:
        return specialitySkillLevel + tankman.crewLevelIncrease[0]
    elif skillProgress == tankmen.NO_SKILL:
        return tankmen.MAX_SKILL_LEVEL
    elif specialitySkillLevel < tankmen.MAX_SKILL_LEVEL:
        return tankmen.MAX_SKILL_LEVEL + tankman.crewLevelIncrease[0]
    else:
        return specialitySkillLevel + tankman.crewLevelIncrease[0] if booster.perkLevelMultiplier is None else (specialitySkillLevel + tankman.crewLevelIncrease[0]) * booster.perkLevelMultiplier


def getBattleBooster(vehicle, skillName):
    if vehicle:
        installedBoosters = vehicle.battleBoosters.installed.getItems()
        if installedBoosters:
            boosters = [ booster.descriptor for booster in installedBoosters ]
            return findFirst(lambda a, name=skillName: isinstance(a, SkillEquipment) and a.skillName == name, boosters, default=None)
    return None


def __makeFakeTankmanDescr(startRoleLevel, freeXpValue, typeID, skills=(), freeSkills=(), lastSkillLevel=tankmen.MAX_SKILL_LEVEL):
    vehType = vehicles.VehicleDescr(typeID=typeID).type
    tmanDescr = tankmen.TankmanDescr(tankmen.generateCompactDescr(tankmen.generatePassport(vehType.id[0], False), vehType.id[1], vehType.crewRoles[0][0], startRoleLevel, skills=skills, freeSkills=freeSkills, lastSkillLevel=lastSkillLevel))
    tmanDescr.addXP(freeXpValue)
    return tmanDescr


def __averageLevelProcessor(crew, levels):
    if levels:
        return sum([ lvl for lvl in levels if lvl != tankmen.NO_SKILL ]) / float(len(levels))


def __averageAllLevelProcessor(crew, levels):
    return sum([ lvl for lvl in levels if lvl != tankmen.NO_SKILL ]) / float(len(crew) or len(levels) or 1)


def __maxLevelProcessor(crew, levels):
    return max(levels or [0])


DEFAULT_LEVEL_PROCESSOR = __maxLevelProcessor
SKILL_LEVEL_PROCESSORS = {'repair': __averageAllLevelProcessor,
 'camouflage': __averageAllLevelProcessor,
 'brotherhood': __averageAllLevelProcessor,
 'fireFighting': __averageAllLevelProcessor,
 'loader_intuition': __averageLevelProcessor}
