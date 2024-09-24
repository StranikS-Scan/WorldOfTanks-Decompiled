# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/Tankman.py
import time
from collections import OrderedDict, namedtuple
from copy import copy
from itertools import chain
import typing
from constants import NEW_PERK_SYSTEM as NPS, SkinInvData
from debug_utils import LOG_WARNING
from gui import GUI_NATIONS_ORDER_INDEX, TANKMEN_ROLES_ORDER_DICT, nationCompareByIndex
from gui.Scaleform.genConsts.SKILLS_CONSTANTS import SKILLS_CONSTANTS
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.gui_items import GUI_ITEM_TYPE, ItemsCollection, collectKpi
from gui.shared.gui_items.gui_item import GUIItem, HasStrCD
from gui.shared.skill_parameters import SKILLS
from gui.shared.utils.functions import replaceHyphenToUnderscore
from helpers import dependency, i18n
from items import ITEM_TYPE_NAMES, special_crew, tankmen, tankmen_cfg, vehicles
from items.artefacts import SkillEquipment
from items.components import skills_constants
from items.components.component_constants import EMPTY_STRING
from items.components.crew_skins_constants import NO_CREW_SKIN_ID
from items.components.skills_constants import SKILLS_BY_ROLES, SkillTypeName, UNLEARNABLE_SKILLS
from items.tankmen import MAX_SKILL_LEVEL, sortTankmanRoles
from nations import MAP
from shared_utils import findFirst
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from typing import Sequence, List, Tuple, Optional
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
COMMANDER_BONUS = 'commander_bonus'
NO_TANKMAN = -1
NO_SLOT = -1
MAX_ROLE_LEVEL = 100
SKILL_EFFICIENCY_UNTRAINED = -1
RRLBonuses = namedtuple('RRLBonuses', 'commBonus, brothersBonus, eqsBonus, optDevsBonus, penalty')

class RealRoleLevel(namedtuple('RealRoleLevel', 'lvl_, bonuses_')):
    __slots__ = ()

    @property
    def lvl(self):
        return self.lvl_

    @property
    def bonuses(self):
        return self.bonuses_


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
    NO_VEHICLE_INV_ID = -1
    _itemsCache = dependency.descriptor(IItemsCache)
    __slots__ = ('__descriptor', '_invID', '_nationID', '_itemTypeID', '_itemTypeName', '_combinedRoles', '_dismissedAt', '_isDismissed', '_vehicleNativeDescr', '_vehicleInvID', '_vehicleDescr', '_vehicleBonuses', '_vehicleSlotIdx', '_skills', '_skillsMap', '_bonusSkills', '_skinID', '_comparator', '__brotherhoodMarkedAsActive')

    class ROLES(object):
        COMMANDER = 'commander'
        RADIOMAN = 'radioman'
        DRIVER = 'driver'
        GUNNER = 'gunner'
        LOADER = 'loader'

    TANKMEN_ROLES_ORDER = OrderedDict(((ROLES.COMMANDER, 0),
     (ROLES.GUNNER, 1),
     (ROLES.DRIVER, 2),
     (ROLES.RADIOMAN, 3),
     (ROLES.LOADER, 4)))
    _NON_COMMANDER_SKILLS = skills_constants.ACTIVE_SKILLS.difference(skills_constants.COMMANDER_SKILLS)

    def __init__(self, strCompactDescr, inventoryID=-1, vehicle=None, dismissedAt=None, proxy=None, vehicleSlotIdx=-1, bonusSkillsLevels=None):
        super(Tankman, self).__init__(strCD=HasStrCD(strCompactDescr))
        bonusSkillsLevels = bonusSkillsLevels or []
        self.__descriptor = None
        _descr = self.descriptor
        self._invID = inventoryID
        self._nationID = _descr.nationID
        self._itemTypeID = GUI_ITEM_TYPE.TANKMAN
        self._itemTypeName = ITEM_TYPE_NAMES[self.itemTypeID]
        self._combinedRoles = (_descr.role,)
        self._dismissedAt = dismissedAt
        self._isDismissed = self.dismissedAt is not None
        self.__brotherhoodMarkedAsActive = False
        self._vehicleNativeDescr = vehicles.VehicleDescr(typeID=(self.nationID, _descr.vehicleTypeID))
        self._vehicleInvID = self.NO_VEHICLE_INV_ID
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
        self._skills = self._buildSkills(proxy)
        self._skillsMap = self._buildSkillsMap()
        self._bonusSkills = self.buildBonusSkills(proxy, bonusSkillsLevels, bonusRoles=self.bonusRoles())
        self._skinID = self._equippedSkinID(proxy)
        self._comparator = TankmenComparator()
        return

    def __cmp__(self, other):
        return self._comparator(self, other)

    def _buildSkills(self, proxy):
        return [ getTankmanSkill(skill, self, proxy) for skill in self.descriptor.skills if skill != 'any' ]

    def buildBonusSkills(self, proxy, bonusSkillsLevels=None, bonusRoles=None):
        bonusSkills = OrderedDict()
        if bonusRoles is None:
            return bonusSkills
        else:
            bonusSkillsLevels = bonusSkillsLevels or []
            skillNamesMaxLvl = []
            if bonusSkillsLevels and bonusSkillsLevels[0]:
                self.descriptor.bonusSkillsLevels = bonusSkillsLevels[0]
            if len(bonusSkillsLevels) > 1:
                skillNamesMaxLvl = bonusSkillsLevels[1]
            for role, skillName in self.descriptor.getRoleBonusSkills(bonusRoles):
                bonusSkills.setdefault(role, [])
                idx = len(bonusSkills[role])
                if len(self.bonusSkillsLevels) <= idx or skillName in skillNamesMaxLvl:
                    level = tankmen.MAX_SKILL_LEVEL
                else:
                    level = self.bonusSkillsLevels[idx]
                skill = getTankmanSkill(skillName, self, proxy, level=level) if skillName != 'any' else None
                bonusSkills[role].append(skill)
                if skill:
                    self._skillsMap[skill.name] = skill

            return bonusSkills

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
    def skillsCount(self):
        return len(self._skills)

    @property
    def skillsLevels(self):
        newSkills, lastNewSkillLevel = self.newSkillsCount
        newSkills += self.newFreeSkillsCount
        if newSkills or lastNewSkillLevel:
            levels = [MAX_SKILL_LEVEL] * self.descriptor.getFullSkillsCount(withFree=True)
            if lastNewSkillLevel != MAX_SKILL_LEVEL:
                levels.append(lastNewSkillLevel)
            return levels
        levels = [MAX_SKILL_LEVEL] * (self.skillsCount - 1)
        levels.append(self.descriptor.lastSkillLevel)
        return levels

    @property
    def selectedFreeSkillsCount(self):
        return self.descriptor.selectedFreeSkillsCount

    @property
    def bonusSkills(self):
        return self._bonusSkills

    @property
    def bonusSkillsCount(self):
        return len(filter(None, chain(*self._bonusSkills.values())))

    @property
    def bonusSkillsCountByRole(self):
        return {role:len(filter(None, skills)) for role, skills in self._bonusSkills.iteritems()}

    @property
    def bonusSkillsLevels(self):
        return self.descriptor.bonusSkillsLevels

    @property
    def bonusSlotsLevels(self):
        milestones = [ idx * NPS.BONUS_SKILL_ENABLING_FREQUENCY * MAX_SKILL_LEVEL for idx in range(NPS.MAX_BONUS_SKILLS_PER_ROLE) ]
        majorSkillsProgress = sum(self.skillsLevels)
        levels = []
        for slotIDX, lvl in enumerate(self.descriptor.bonusSkillsLevels):
            levels.append(lvl if majorSkillsProgress >= milestones[slotIDX] else None)

        return levels

    @property
    def freeSkills(self):
        return self._skills[:self.selectedFreeSkillsCount]

    @property
    def freeSkillsNames(self):
        return self.descriptor.selectedFreeSkills

    @property
    def earnedSkills(self):
        return self._skills[self.selectedFreeSkillsCount:]

    @property
    def earnedSkillsCount(self):
        return self.descriptor.earnedSkillsCount

    @property
    def skillsInProgress(self):
        skillsInProgress = []
        for skill in self.skills:
            if skill.level < tankmen.MAX_SKILL_LEVEL:
                skillsInProgress.append(skill.name)

        return skillsInProgress

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
        return RealRoleLevel(realRoleLevel, RRLBonuses(commBonus, brothersBonus, eqsBonus, optDevsBonus, penalty))

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
    def nativeTankRealRoleLevel(self):
        effRoleLevel = self.roleLevel
        commBonus = self.vehicleBonuses.get('commander', 0)
        if self.descriptor.role == self.ROLES.COMMANDER:
            commBonus = 0
        brothersBonus = self.vehicleBonuses.get('brotherhood', 0)
        eqsBonus = self.vehicleBonuses.get('equipment', 0)
        optDevsBonus = self.vehicleBonuses.get('optDevices', 0)
        nativeTankRealRoleLevel = effRoleLevel + commBonus + brothersBonus + eqsBonus + optDevsBonus
        return nativeTankRealRoleLevel

    @property
    def descriptor(self):
        if self.__descriptor is None or not self.strCD.endswith(self.__descriptor.dossierCompactDescr):
            self.__descriptor = tankmen.TankmanDescr(compactDescr=self.strCD)
        return self.__descriptor

    @property
    def isInTank(self):
        return self.vehicleDescr is not None

    @property
    def isInNativeTank(self):
        return self.isInTank and self.vehicleDescr.type.compactDescr == self.vehicleNativeDescr.type.compactDescr

    @property
    def isInSkin(self):
        return self.skinID != NO_CREW_SKIN_ID

    @property
    def skin(self):
        return self._itemsCache.items.getCrewSkin(self.skinID) if self.isInSkin else None

    @property
    def role(self):
        return self.descriptor.role

    @property
    def roleLevel(self):
        return self.descriptor.roleLevel

    @property
    def skillsEfficiencyXP(self):
        return self.descriptor.skillsEfficiencyXP

    @property
    def skillsEfficiency(self):
        return self.descriptor.skillsEfficiency

    @property
    def canUseSkillsInCurrentVehicle(self):
        return False if not self.isInTank else self.descriptor.isOwnVehicleOrPremium(self.vehicleDescr.type)

    @property
    def currentVehicleSkillsEfficiency(self):
        descr = self.descriptor
        if not self.isInTank:
            return descr.skillsEfficiency
        return descr.skillsEfficiency if self.canUseSkillsInCurrentVehicle else SKILL_EFFICIENCY_UNTRAINED

    @property
    def isMaxCurrentVehicleSkillsEfficiency(self):
        return self.currentVehicleSkillsEfficiency >= tankmen.MAX_SKILLS_EFFICIENCY

    @property
    def isMaxSkillEfficiency(self):
        return self.descriptor.hasMaxEfficiency

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
    def iconRank(self):
        return getRankIconName(self.nationID, self.descriptor.rankID)

    @property
    def extensionLessIconRank(self):
        return self.iconRank.split('.png')[0]

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
        tdescr = self.descriptor
        return getFullUserName(self.nationID, tdescr.firstNameID, tdescr.lastNameID)

    @property
    def rankUserName(self):
        return getRankUserName(self.nationID, self.descriptor.rankID)

    @property
    def roleUserName(self):
        return getRoleUserName(self.descriptor.role)

    @property
    def loreDescription(self):
        tdescr = self.descriptor
        groups = tankmen.getNationGroups(tdescr.nationID, tdescr.isPremium)
        return getLoreDescr(groups[tdescr.gid].name, tdescr.nationID)

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

    @property
    def maxSkillsCount(self):
        return self.descriptor.maxSkillsCount

    def hasNewSkill(self, useCombinedRoles=False):
        availSkills = self.availableSkills(useCombinedRoles)
        return self.roleLevel == tankmen.MAX_SKILL_LEVEL and bool(availSkills) and (self.descriptor.lastSkillLevel == tankmen.MAX_SKILL_LEVEL or not self.skills)

    @property
    def newSkillsCount(self):
        return self.descriptor.getNewSkillsCount(withFree=False)

    @property
    def freeSkillsCount(self):
        return self.descriptor.freeSkillsNumber

    @property
    def newFreeSkillsCount(self):
        return self.descriptor.newFreeSkillsCount

    @property
    def newBonusSkillsCountByRole(self):
        enabledSlotsCount = len([ lvl for lvl in self.bonusSlotsLevels if lvl is not None ])
        bSkillsCount = self.bonusSkillsCountByRole
        return {role:enabledSlotsCount - bSkillsCount[role] for role in bSkillsCount}

    @property
    def efficiencyRoleLevel(self):
        return float(self.roleLevel)

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

    @property
    def skillRoles(self):
        return (s.roleType for s in self.skills)

    @property
    def bigIconDynAccessorWithSkin(self):
        return R.images.gui.maps.icons.tankmen.icons.big.crewSkins if self.isInSkin else R.images.gui.maps.icons.tankmen.icons.big

    def getExtensionLessIconWithSkin(self):
        return getDynIconName(self.skin.getIconID()) if self.isInSkin else getExtensionLessIconName(self.nationID, self.descriptor.iconID)

    def getDescription(self):
        return i18n.makeString(self.skin.getDescription()) if self.isInSkin else self.loreDescription

    def getFullUserNameWithSkin(self):
        return self.skin.getLocalizedFullName() if self.isInSkin else self.fullUserName

    def isSearchableByName(self, name):
        return name.lower() in self.fullUserName.lower()

    def isSearchableBySkinName(self, name):
        if self.isInSkin:
            skinName = self.skin.getLocalizedFullName()
            return name.lower() in skinName.lower()
        return False

    def isLockedByVehicle(self):
        if not self.isInTank:
            return False
        vehicle = self._itemsCache.items.getVehicle(self.vehicleInvID)
        return vehicle.isCrewLocked

    def canLearnSkills(self):
        if self.isInTank:
            vehicle = self._itemsCache.items.getVehicle(self.vehicleInvID)
            if vehicle.isLocked:
                return False
        return False if self.isDismissed else True

    def skillAlreadyLearned(self, skillName):
        return skillName in self.skillsMap and self.skillsMap[skillName].level == tankmen.MAX_SKILL_LEVEL

    def skillIsInProgress(self, skillName):
        return skillName in self.skillsMap and self.skillsMap[skillName].level < tankmen.MAX_SKILL_LEVEL

    def canHaveBoosterBonus(self, skillName):
        return self.skillAlreadyLearned(skillName) and self.canUseSkillsInCurrentVehicle and self.isMaxSkillEfficiency

    def allSkillsLearned(self):
        allowedGroups = ['common'] + list(self.combinedRoles)
        for group, skills in self.getPossibleSkillsByRole().iteritems():
            if group not in allowedGroups:
                continue
            for skill in skills:
                if not skill.isLearnedAsMajor:
                    return False

        return True

    def getPossibleSkills(self):
        skillnames = frozenset()
        for role in self.combinedRoles:
            skillnames |= tankmen.SKILLS_BY_ROLES.get(role, frozenset())

        skillnames -= set(UNLEARNABLE_SKILLS)
        return skillnames

    def getPossibleSkillsByRole(self):
        result = OrderedDict()
        for skill in tankmen.COMMON_SKILLS_ORDERED:
            result.setdefault('common', []).append(getTankmanSkill(skill, tankman=self))

        roles = set(self.skillRoles) | set(self.roles())

        def fillSkills(currentRole):
            if currentRole in roles:
                roleSkills = tankmen.SKILLS_BY_ROLES_ORDERED.get(currentRole, [])
                for currentSkill in roleSkills:
                    if currentSkill in tankmen.COMMON_SKILLS:
                        continue
                    if currentSkill in UNLEARNABLE_SKILLS:
                        continue
                    if currentSkill in self._skillsMap:
                        result.setdefault(role, []).append(self._skillsMap[currentSkill])
                    result.setdefault(role, []).append(getTankmanSkill(currentSkill, tankman=self))

        for role in self.roles():
            fillSkills(role)

        for role in TANKMEN_ROLES_ORDER_DICT['plain']:
            if not result.get(role):
                fillSkills(role)

        return result

    def getFreeSkillsToLearn(self):
        result = []
        commonSkills = []
        tdescr = self.descriptor
        for skill in tankmen.COMMON_SKILLS:
            if skill not in tdescr.freeSkills:
                commonSkills.append(self.__packSkill(getTankmanSkill(skill, tankman=self)))

        result.append({'id': 'common',
         'skills': commonSkills})
        roleSkills = tankmen.SKILLS_BY_ROLES.get(tdescr.role, tuple())
        skills = []
        for skill in roleSkills:
            if skill not in tankmen.COMMON_SKILLS and skill not in tdescr.freeSkills and skill not in skills_constants.UNLEARNABLE_SKILLS:
                skills.append(self.__packSkill(getTankmanSkill(skill)))

        result.append({'id': self.role,
         'skills': skills})
        return result

    def hasSkillToLearn(self):
        bonusRolesCount = len(self.bonusRoles())
        return self.skillsCount < NPS.MAX_MAJOR_PERKS or self.bonusSkillsCount < bonusRolesCount * NPS.MAX_BONUS_SKILLS_PER_ROLE

    def roles(self):
        if self.isInTank:
            roles = self.vehicleDescr.type.crewRoles[self.vehicleSlotIdx]
        else:
            roles = self.rolesInNativeVehicle()
        return sortTankmanRoles(roles, self.TANKMEN_ROLES_ORDER)

    def bonusRoles(self):
        return self.roles()[1:]

    def rolesInNativeVehicle(self):
        for roles in self.vehicleNativeDescr.type.crewRoles:
            if roles and self.role == roles[0]:
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

    def setCombinedRoles(self, combinedRoles):
        self._combinedRoles = combinedRoles

    def rebuildSkills(self, proxy=None):
        self._skills = self._buildSkills(proxy)
        self._skillsMap = self._buildSkillsMap()
        self._bonusSkills = self.buildBonusSkills(proxy, bonusRoles=self.bonusRoles())

    def updateBonusesFromVehicle(self, vehicle):
        if vehicle:
            self._vehicleBonuses = dict(vehicle.bonuses)

    def getVehicle(self):
        return None if not self.isInTank else self._itemsCache.items.getVehicle(self.vehicleInvID)

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
    __slots__ = ('_name', '_level', '_roleType', '_isEnable', '_isFemale', '_isZero', '_customName', '_tankmanRole', '_isLearnedAsMajor', '_isLearnedAsBonus', '_packer', '_typeName', '_isSkillActive')
    CUSTOM_NAME_EXT = ''

    def __init__(self, skillName, tankman=None, proxy=None, skillLevel=None):
        super(TankmanSkill, self).__init__(proxy)
        self._name = skillName
        self._level = skillLevel or 0
        self._typeName = getSkillTypeName(skillName)
        if tankman is not None:
            tdescr = tankman.descriptor
            skills = tdescr.skills
            self._tankmanRole = tankman.role
            self._isFemale = tankman.isFemale
            self._isZero = False
            skillRole = tankman.role
            if skillName in skills and skillLevel is None:
                if skills.index(skillName) == len(skills) - 1:
                    self._level = tdescr.lastSkillLevel
                else:
                    self._level = tankmen.MAX_SKILL_LEVEL
                self._isZero = skills.index(skillName) < tdescr.freeSkillsNumber
            else:
                roles = list(tankmen.ROLES_BY_SKILLS[skillName])
                bonusSkillsRole = roles[0]
                bonusSkills = tankman.descriptor.getBonusSkillsForRole(bonusSkillsRole)
                if skillName in bonusSkills:
                    skillRole = bonusSkillsRole
                    idx = bonusSkills.index(skillName)
                    self._isLearnedAsBonus = True
                    bonusSkillsLevels = tankman.descriptor.bonusSkillsLevels
                    if len(bonusSkillsLevels) > idx and self._level != MAX_SKILL_LEVEL:
                        self._level = bonusSkillsLevels[idx]
            self._roleType = tankmen.getSkillRoleType(skillName)
            self._isEnable = self.__getEnabledSkill(tankman)
            self._isLearnedAsMajor = self.name in tankman.descriptor.earnedSkills or self._isZero
            self._isLearnedAsBonus = self.name in tankman.descriptor.getPossibleBonusSkills(tankman.bonusRoles())
            self._isSkillActive = self.isEnable and self.isRelevantForRole(skillRole) and tankman.canUseSkillsInCurrentVehicle
        else:
            self._isFemale = False
            self._isZero = False
            self._roleType = None
            self._isEnable = False
            self._tankmanRole = None
            self._isLearnedAsMajor = False
            self._isLearnedAsBonus = False
            self._isSkillActive = False
        self._customName = ''
        if self.CUSTOM_NAME_EXT:
            customName = '_'.join((self.CUSTOM_NAME_EXT, BROTHERHOOD_SKILL_NAME))
            if skillName in (BROTHERHOOD_SKILL_NAME, customName):
                self._customName = customName
                self._name = BROTHERHOOD_SKILL_NAME
        return

    def __repr__(self):
        return 'TankmanSkill<name:%s, level:%d, isEnable:%s>' % (self.name, self.level, self.isEnable)

    def __eq__(self, other):
        return False if not isinstance(other, TankmanSkill) else self.name == other.name

    def __ne__(self, other):
        return not self.__eq__(other)

    def __getEnabledSkill(self, tankman):
        for role in tankman.roles():
            roleSkills = tankmen.SKILLS_BY_ROLES.get(role, tuple())
            if self.name in roleSkills:
                return True

        return False

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
    def isZero(self):
        return self._isZero

    @property
    def isSituational(self):
        return self._typeName is SkillTypeName.SITUATIONAL

    @property
    def userName(self):
        if self._customName:
            resStr = '_'.join((self._name, self.CUSTOM_NAME_EXT))
            return backport.text(R.strings.crew_perks.dyn(resStr).name())
        return getSkillUserName(self.name)

    @property
    def isLearned(self):
        return self.isLearnedAsMajor or self.isLearnedAsBonus

    @property
    def isLearnedAsMajor(self):
        return self._isLearnedAsMajor

    @property
    def isLearnedAsBonus(self):
        return self._isLearnedAsBonus

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
        return getSkillCurrentLvlDescription(self.name)

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
            iconName = '{}_{}'.format(self.CUSTOM_NAME_EXT, iconName)
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
    def isMaxLevel(self):
        return self._level >= tankmen.MAX_SKILL_LEVEL

    @property
    def customName(self):
        return self.CUSTOM_NAME_EXT

    @property
    def isSkillActive(self):
        return self._isSkillActive

    def isRelevantForRole(self, role):
        isBonusRole = self._tankmanRole and self._tankmanRole != role
        return self.name in SKILLS_BY_ROLES[role] or isBonusRole and self.isLearnedAsBonus

    def updateLevel(self, level):
        self._level = level

    def setIsSkillActive(self, isSkillActive):
        self._isSkillActive = isSkillActive


class SabatonTankmanSkill(TankmanSkill):
    __slots__ = ()
    CUSTOM_NAME_EXT = 'sabaton'


class OffspringTankmanSkill(TankmanSkill):
    __slots__ = ()
    CUSTOM_NAME_EXT = 'offspring'


class YhaTankmanSkill(TankmanSkill):
    __slots__ = ()
    CUSTOM_NAME_EXT = 'yha'


class WitchesTankmanSkill(TankmanSkill):
    __slots__ = ()
    CUSTOM_NAME_EXT = 'witches'


class BaseBookConvertingFormatter(object):
    __crewBooks = list()

    def getTextMessage(self, header, qtyPrefix=''):
        formatedDate = str(time.strftime('%d.%m.%Y %H:%M:%S', time.localtime(time.time())))
        message = backport.text(header, at=formatedDate)
        message += ',\n'.join(('{} ({}{})'.format(crewBook['name'], qtyPrefix, crewBook['count']) for crewBook in self.__crewBooks)) + '.'
        return message

    def setCrewBooks(self, crewBooks, itemsCache):
        self.__crewBooks = []
        for intCD, count in crewBooks.iteritems():
            crewBook = itemsCache.items.getItemByCD(intCD)
            if crewBook is None:
                continue
            self.__crewBooks.append(dict(name=crewBook.getName().strip(), count=count, nation=GUI_NATIONS_ORDER_INDEX[crewBook.getNation()], xp=crewBook.getXP(), type=crewBook.getBookTypeOrder()))

        return

    def sortCrewBooks(self, key):
        self.__crewBooks.sort(key=key)


def getTankmanSkill(skillName, tankman=None, proxy=None, skillCustomisation=None, level=None):
    if tankman is not None:
        descriptor = tankman.descriptor
        if special_crew.isSabatonCrew(descriptor):
            return SabatonTankmanSkill(skillName, tankman, proxy, skillLevel=level)
        if special_crew.isOffspringCrew(descriptor):
            return OffspringTankmanSkill(skillName, tankman, proxy, skillLevel=level)
        if special_crew.isYhaCrew(descriptor):
            return YhaTankmanSkill(skillName, tankman, proxy, skillLevel=level)
        if special_crew.isWitchesCrew(descriptor):
            return WitchesTankmanSkill(skillName, tankman, proxy, skillLevel=level)
    if skillCustomisation is not None:
        if skillCustomisation == SabatonTankmanSkill.CUSTOM_NAME_EXT:
            return SabatonTankmanSkill(skillName, tankman, proxy, skillLevel=level)
        if skillCustomisation == OffspringTankmanSkill.CUSTOM_NAME_EXT:
            return OffspringTankmanSkill(skillName, tankman, proxy, skillLevel=level)
        if skillCustomisation == YhaTankmanSkill.CUSTOM_NAME_EXT:
            return YhaTankmanSkill(skillName, tankman, proxy, skillLevel=level)
        if skillCustomisation == WitchesTankmanSkill.CUSTOM_NAME_EXT:
            return WitchesTankmanSkill(skillName, tankman, proxy, skillLevel=level)
    return TankmanSkill(skillName, tankman, proxy, skillLevel=level)


def getFirstUserName(nationID, firstNameID):
    return i18n.convert(tankmen.getNationConfig(nationID).getFirstName(firstNameID))


def getLastUserName(nationID, lastNameID):
    return i18n.convert(tankmen.getNationConfig(nationID).getLastName(lastNameID))


def getFullUserName(nationID, firstNameID, lastNameID):
    firstUserName = getFirstUserName(nationID, firstNameID)
    lastUserName = getLastUserName(nationID, lastNameID)
    return (firstUserName + ' ' + lastUserName).strip()


def getRoleUserName(role):
    skillConf = tankmen.getSkillsConfig()
    skill = skillConf.getSkill(role)
    userString = skill.userString
    return i18n.convert(userString)


def getLoreDescr(group, nationID):
    loreConf = tankmen_cfg.getLoreConfig()
    key = loreConf.getLoreDescrForGroup(group, MAP[nationID])
    if key:
        loc = R.strings.lore.tankman.lore
        return str(backport.text(loc.dyn(replaceHyphenToUnderscore(key))()))


def getRoleWithFeminineUserName(role, isFemale):
    loc = R.strings.item_types.tankman.roles.female if isFemale else R.strings.item_types.tankman.roles
    return str(backport.text(loc.dyn(role)()))


def getRolePossessiveCaseUserName(role, isFemale):
    loc = R.strings.item_types.tankman.roles.female.possessiveCase if isFemale else R.strings.item_types.tankman.roles.possessiveCase
    return str(backport.text(loc.dyn(role)()))


def getRoleIconName(role):
    return tankmen.getSkillsConfig().getSkill(role).icon


def getExtensionLessRoleIconName(role):
    return tankmen.getSkillsConfig().getSkill(role).extensionLessIcon


def getRoleMediumIconPath(role):
    return '../maps/icons/tankmen/roles/medium/%s' % getRoleIconName(role)


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


def getBigIconPath(nationID, iconID):
    return __getIconPath(nationID, iconID, 'big')


def getSpecialIconPath(nationID, iconID):
    return __getIconPath(nationID, iconID, 'special')


def getBarracksIconPath(nationID, iconID):
    return __getIconPath(nationID, iconID, 'barracks')


def getRankIconName(nationID, rankID):
    return tankmen.getNationConfig(nationID).getRank(rankID).icon


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


def __getIconPath(nationID, iconID, iconType):
    iconName = getDynIconName(getExtensionLessIconName(nationID, iconID))
    iconPath = R.images.gui.maps.icons.tankmen.icons.dyn(iconType)
    dynAccessor = iconPath.dyn(iconName)
    return backport.image(dynAccessor()) if dynAccessor.isValid() else backport.image(iconPath.tankman())


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
        if tankman is None or not tankman.canHaveBoosterBonus(skillName):
            return False

    return True


def __isPersonalSkillLearnt(skillName, vehicle):
    skillRole = tankmen.getSkillRoleType(skillName)
    crewRoles = vehicle.descriptor.type.crewRoles
    for slotIdx, tankman in vehicle.crew or []:
        roles = crewRoles[slotIdx]
        if skillRole in roles:
            if tankman is None:
                return False
            if skillRole == roles[0]:
                if not tankman.canHaveBoosterBonus(skillName):
                    return False
            elif skillName not in tankman.descriptor.getPossibleBonusSkills(tankman.bonusRoles()) or not tankman.canHaveBoosterBonus(skillName):
                return False

    return True


def crewMemberRealSkillLevel(vehicle, skillName, commonWithIncrease=True, skipIrrelevantState=False, shouldIncrease=True):
    shouldIncrease = (skillName not in tankmen.COMMON_SKILLS or commonWithIncrease and skillName != SKILLS.BROTHERHOOD) and shouldIncrease
    booster = getBattleBooster(vehicle, skillName) if shouldIncrease else None
    hasBoosterForSkill = booster and skillName == booster.skillName
    tankmansCantUseBoosterCnt = 0
    tankmenSkillLevels = []
    skillRoleType = tankmen.getSkillRoleType(skillName)
    if skillRoleType is None:
        return tankmen.NO_SKILL
    else:
        isCommonSkill = skillRoleType == tankmen.COMMON_SKILL_ROLE_TYPE
        for slot, tankman in vehicle.crew:
            if tankman is None:
                if isCommonSkill or skillRoleType in vehicle.descriptor.type.crewRoles[slot]:
                    tankmenSkillLevels.append((slot, tankmen.NO_SKILL, True))
                continue
            if not tankman.descriptor.isOwnVehicleOrPremium(vehicle.descriptor.type) and not hasBoosterForSkill:
                if isCommonSkill or skillRoleType in vehicle.descriptor.type.crewRoles[slot]:
                    tankmenSkillLevels.append((slot, tankmen.NO_SKILL, True))
            if skillRoleType in tankman.combinedRoles or isCommonSkill:
                withoutPerkLvlMul = None
                if booster:
                    withoutPerkLvlMul = copy(booster)
                    withoutPerkLvlMul.perkLevelMultiplier = 1.0
                skill = getTankmanSkill(skillName, tankman=tankman)
                bonusSkills = [ s.name for s in sum(tankman.bonusSkills.values(), []) if s and s.isEnable ]
                isMajorRoleSkill = isCommonSkill or skillRoleType == tankman.role
                if isMajorRoleSkill:
                    hasMaxSkillsInRole = len(tankman.skills) == NPS.MAX_MAJOR_PERKS
                else:
                    selectedBonusSkillsCount = tankman.descriptor.selectedBonusSkillsCount(skillRoleType)
                    hasMaxSkillsInRole = selectedBonusSkillsCount == NPS.MAX_BONUS_SKILLS_PER_ROLE
                personalSkillLevel = tankmanPersonalSkillLevel(tankman, skillName, withoutPerkLvlMul, shouldIncrease, hasMaxSkillsInRole) if skill.isSkillActive or skillName in bonusSkills or skipIrrelevantState else tankmen.NO_SKILL
                if booster and personalSkillLevel == tankmen.NO_SKILL and hasMaxSkillsInRole:
                    tankmansCantUseBoosterCnt += 1
                tankmenSkillLevels.append((slot, personalSkillLevel, skill.isSkillActive or skillName in bonusSkills))

        if booster is not None and tankmansCantUseBoosterCnt != len(tankmenSkillLevels):
            tankmenSkillLevels = _boostSkill(vehicle.crew, skillName, tankmenSkillLevels, booster)
        if not vehicle.crew:
            return tankmen.NO_SKILL
        if all((hasSkill == tankmen.NO_SKILL for _, hasSkill, _ in tankmenSkillLevels)):
            return tankmen.NO_SKILL
        validSkillLevels = [ level for _, level, _ in tankmenSkillLevels if level != tankmen.NO_SKILL ]
        return sum(validSkillLevels) / float(len(tankmenSkillLevels))


def tankmanPersonalSkillLevel(tankman, skillName, booster=None, withIncrease=True, hasMaxSkillsInRole=False):
    progress = __getPersonalSkillLearningProgress(tankman, skillName)
    if not (progress == tankmen.NO_SKILL and (booster is None or hasMaxSkillsInRole)):
        if withIncrease:
            progress = _getSkillLevelWithIncrease(booster, progress, tankman)
            if booster is not None:
                return progress
        elif progress != tankmen.NO_SKILL:
            progress = tankman.skillsMap[skillName].level
        progress *= tankman.skillsEfficiency
    return progress


def _boostSkill(crew, skillName, tankmenSkillLevels, booster):
    if booster is None:
        return tankmenSkillLevels
    allTankmenHaveSkillAtMaxLevel = True
    allTankmenHaveMaxEfficiency = True
    allHasActiveSkill = True
    for slot, tankman, hasActiveSkill in tankmenSkillLevels:
        tankman = next((tankman for idxInCrew, tankman in crew if idxInCrew == slot), None)
        if tankman is None:
            allTankmenHaveSkillAtMaxLevel = False
            allTankmenHaveMaxEfficiency = False
            continue
        if not tankman.isMaxCurrentVehicleSkillsEfficiency:
            allTankmenHaveMaxEfficiency = False
            continue
        if skillName not in tankman.skillsMap:
            allTankmenHaveSkillAtMaxLevel = False
            continue
        if tankman.skillsMap[skillName].level < tankmen.MAX_SKILL_LEVEL:
            allTankmenHaveSkillAtMaxLevel = False
            continue
        if not hasActiveSkill:
            allHasActiveSkill = False

    if allTankmenHaveSkillAtMaxLevel and allTankmenHaveMaxEfficiency and allHasActiveSkill:
        multiplier = booster.perkLevelMultiplier if booster.perkLevelMultiplier is not None else 1.0
        return [ (slot, level * multiplier, isActive) for slot, level, isActive in tankmenSkillLevels ]
    elif sum((v for _, v, _ in tankmenSkillLevels)) > tankmen.MAX_SKILL_LEVEL * len(tankmenSkillLevels):
        return tankmenSkillLevels
    else:
        return [ (slot, tankmen.MAX_SKILL_LEVEL if skillLevel <= 0 else skillLevel, isActive) for slot, skillLevel, isActive in tankmenSkillLevels ]


def _getSkillLevelWithIncrease(booster, skillLevel, tankman):
    realSkillLevel = skillLevel + tankman.crewLevelIncrease[0]
    if booster is None:
        return realSkillLevel
    elif tankman.currentVehicleSkillsEfficiency == SKILL_EFFICIENCY_UNTRAINED or skillLevel == tankmen.NO_SKILL:
        return tankmen.MAX_SKILL_LEVEL
    elif not tankman.isMaxCurrentVehicleSkillsEfficiency or skillLevel < tankmen.MAX_SKILL_LEVEL:
        return tankmen.MAX_SKILL_LEVEL + tankman.crewLevelIncrease[0]
    else:
        boostFactor = booster.perkLevelMultiplier or 1
        return realSkillLevel * boostFactor


def getBattleBooster(vehicle, skillName):
    if vehicle:
        installedBoosters = vehicle.battleBoosters.installed.getItems()
        if installedBoosters:
            boosters = [ booster.descriptor for booster in installedBoosters ]
            return findFirst(lambda a, name=skillName: isinstance(a, SkillEquipment) and a.skillName == name, boosters, default=None)
    return None


def __makeFakeTankmanDescr(startRoleLevel, freeXpValue, typeID, skills=(), freeSkills=(), lastSkillLevel=tankmen.MAX_SKILL_LEVEL):
    vehType = vehicles.VehicleDescr(typeID=typeID).type
    tmanDescr = tankmen.TankmanDescr(tankmen.generateCompactDescr(tankmen.generatePassport(vehType.id[0]), vehType.id[1], vehType.crewRoles[0][0], startRoleLevel, skills=skills, freeSkills=freeSkills, lastSkillLevel=lastSkillLevel))
    tmanDescr.addXP(freeXpValue)
    return tmanDescr
