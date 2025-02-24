# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/tankman_skill.py
import typing
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.gui_items.gui_item import GUIItem
from gui.shared.utils import skill_presenter_helper
from items.components.component_constants import EMPTY_STRING
from items.components.skills_constants import SKILLS_BY_ROLES, SkillTypeName
from items.special_crew import CustomSkills
from items.tankmen import MAX_SKILL_LEVEL, ROLES_BY_SKILLS, getSkillRoleType
from shared_utils import CONST_CONTAINER
from skeletons.gui.skill import ISkill, ISkillData, ISkillPresenter
if typing.TYPE_CHECKING:
    from typing import Optional, Sequence
    from items.tankmen import TankmanDescr
    from gui.shared.gui_items.Tankman import Tankman
BROTHERHOOD_SKILL_NAME = 'brotherhood'
COMMANDER_BONUS = 'commander_bonus'

class SkillLearnState(CONST_CONTAINER):
    UNLEARNED = 0
    MAJOR = 1
    BONUS = 2


class _Skill(GUIItem, ISkill):
    __slots__ = ('_name', '_customName', '_crewCustomName')

    def __init__(self, skillName, customName=EMPTY_STRING, crewCustomName=EMPTY_STRING, proxy=None, **_):
        super(_Skill, self).__init__(proxy)
        self._name = skillName
        self._customName = customName
        self._crewCustomName = crewCustomName

    @property
    def name(self):
        return self._name

    @property
    def customName(self):
        return self._customName

    @property
    def crewCustomName(self):
        return self._crewCustomName


class _SkillPresenter(_Skill, ISkillPresenter):
    __slots__ = ()

    def __init__(self, skillName, customName=EMPTY_STRING, crewCustomName=EMPTY_STRING, proxy=None, **kwargs):
        super(_SkillPresenter, self).__init__(skillName=skillName, customName=customName, crewCustomName=crewCustomName, proxy=proxy, **kwargs)

    @property
    def userName(self):
        return backport.text(R.strings.crew_perks.dyn(self._customName).name()) if self._customName else skill_presenter_helper.getSkillUserName(self.name)

    @property
    def description(self):
        return skill_presenter_helper.getSkillUserDescription(self.name)

    @property
    def shortDescription(self):
        return skill_presenter_helper.getSkillUserDescription(self.name)

    @property
    def maxLvlDescription(self):
        return skill_presenter_helper.getSkillMaxLvlDescription(self.name)

    @property
    def currentLvlDescription(self):
        return skill_presenter_helper.getSkillCurrentLvlDescription(self.name)

    @property
    def altDescription(self):
        return skill_presenter_helper.getSkillAltDescription(self.name)

    @property
    def altInfo(self):
        return skill_presenter_helper.getSkillAltInfo(self.name)

    @property
    def icon(self):
        return '{}.png'.format(self.customName) if self._customName else '{}.png'.format(self.name)

    @property
    def extensionLessIconName(self):
        return skill_presenter_helper.getSkillIconName(self._name, self._customName)

    @property
    def bigIconPath(self):
        return skill_presenter_helper.getSkillBigIconPath(self._name, self._customName)


class _SkillData(_Skill, ISkillData):
    __slots__ = ('_skillRole', '_tankmanRole', '_level', '_isSkillActive', '_isZero', '_roleType', '_isRelevant', '_typeName', '_isEnable', '_learnState')

    def __init__(self, skillName, skillRole, tankmanRole=None, level=0, isSkillActive=False, isZero=False, isEnable=False, learnState=SkillLearnState.UNLEARNED, customName=EMPTY_STRING, crewCustomName=EMPTY_STRING, proxy=None, **kwargs):
        super(_SkillData, self).__init__(skillName=skillName, customName=customName, crewCustomName=crewCustomName, proxy=proxy, **kwargs)
        self._skillRole = skillRole
        self._tankmanRole = tankmanRole if tankmanRole is not None else skillRole
        self._level = level
        self._isSkillActive = isSkillActive
        self._isZero = isZero
        self._isEnable = isEnable
        self._learnState = learnState
        self._roleType = getSkillRoleType(self._name)
        self._isRelevant = getIsRelevantForRole(self._name, self._skillRole)
        self._typeName = skill_presenter_helper.getSkillTypeName(self._name)
        return

    @property
    def level(self):
        return self._level

    @property
    def roleType(self):
        return self._roleType

    @property
    def typeName(self):
        return self._typeName

    @property
    def isSituational(self):
        return self._typeName == SkillTypeName.SITUATIONAL

    @property
    def isMaxLevel(self):
        return self._level >= MAX_SKILL_LEVEL

    @property
    def isSkillActive(self):
        return self._isSkillActive

    @property
    def isRelevant(self):
        return self._isRelevant

    @property
    def skillRole(self):
        return self._skillRole

    @property
    def tankmanRole(self):
        return self._tankmanRole

    @property
    def isEnable(self):
        return self._isEnable

    @property
    def isZero(self):
        return self._isZero

    @property
    def learnState(self):
        return self._learnState

    @property
    def isLearned(self):
        return self._learnState != SkillLearnState.UNLEARNED

    @property
    def isLearnedAsMajor(self):
        return self._learnState & SkillLearnState.MAJOR

    @property
    def isLearnedAsBonus(self):
        return self._learnState & SkillLearnState.BONUS

    def setIsSkillActive(self, isSkillActive):
        self._isSkillActive = isSkillActive


class TankmanSkill(_SkillData, _SkillPresenter):
    __slots__ = ()

    def __init__(self, skillName, skillRole, tankmanRole=None, level=0, isSkillActive=False, isZero=False, isEnable=False, learnState=SkillLearnState.UNLEARNED, customName=EMPTY_STRING, crewCustomName=EMPTY_STRING, proxy=None):
        super(TankmanSkill, self).__init__(skillName=skillName, skillRole=skillRole, tankmanRole=tankmanRole, level=level, isSkillActive=isSkillActive, isZero=isZero, isEnable=isEnable, learnState=learnState, customName=customName, crewCustomName=crewCustomName, proxy=proxy)

    def __repr__(self):
        return 'TankmanSkill<name:{}, level:{}, skillRole:{}, tankmanRole:{}, isRelevant:{}>'.format(self.name, self.level, self.skillRole, self.tankmanRole, self.isRelevant)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __eq__(self, other):
        return False if not isinstance(other, TankmanSkill) else self.name == other.name


def getIsSkillEnable(skillName, roles):
    for role in roles:
        roleSkills = SKILLS_BY_ROLES.get(role, tuple())
        if skillName in roleSkills:
            return True

    return False


def getSkilLevel(skillName, tdescr, skillLevel=None):
    if skillLevel is not None:
        return skillLevel
    else:
        skills = tdescr.skills
        if skillName in skills:
            if skills.index(skillName) == len(skills) - 1:
                return tdescr.lastSkillLevel
            return MAX_SKILL_LEVEL
        roles = list(ROLES_BY_SKILLS[skillName])
        bonusSkillsRole = roles[0]
        bonusSkills = tdescr.getBonusSkillsForRole(bonusSkillsRole)
        if skillName in bonusSkills:
            idx = bonusSkills.index(skillName)
            bonusSkillsLevels = tdescr.bonusSkillsLevels
            if len(bonusSkillsLevels) > idx:
                return bonusSkillsLevels[idx]
        return 0


def getSkillLearnedState(skillName, skillRole, tankmanRole, skills, bonusSkills):
    learnedState = SkillLearnState.UNLEARNED
    if skillRole == tankmanRole and skillName in skills:
        learnedState |= SkillLearnState.MAJOR
    if skillName in bonusSkills.get(skillRole, []):
        learnedState |= SkillLearnState.BONUS
    return learnedState


def getIsRelevantForRole(skillName, role):
    return True if not role else skillName in SKILLS_BY_ROLES[role]


def getSkillStates(skillName, skillRole, tankman, tdescr):
    skills = tdescr.skills
    bonusSkills = tdescr.bonusSkills
    isEnabled = getIsSkillEnable(skillName, tankman.roles())
    learnState = getSkillLearnedState(skillName, skillRole, tdescr.role, skills, bonusSkills)
    isRelevant = getIsRelevantForRole(skillName, tdescr.role)
    if isEnabled and tankman.canUseSkillsInCurrentVehicle:
        isSkillActive = isRelevant and learnState & SkillLearnState.MAJOR or learnState & SkillLearnState.BONUS
    else:
        isSkillActive = False
    isZero = learnState & SkillLearnState.MAJOR and skills.index(skillName) < tdescr.freeSkillsNumber
    return (isEnabled,
     learnState,
     isRelevant,
     isSkillActive,
     isZero)


def getTankmanSkill(skillName, skillRole, tankman=None, proxy=None, customCrewName=EMPTY_STRING, level=None, tankmanRole=None, **kwargs):
    customCrewName, skillCustomName = CustomSkills.getCustomSkill(skillName, tankman, customCrewName)
    if tankman is not None:
        tdescr = tankman.descriptor
        level = getSkilLevel(skillName, tdescr, level)
        isEnable, learnState, _, isSkillActive, isZero = getSkillStates(skillName, skillRole, tankman, tdescr)
        return TankmanSkill(skillName, skillRole, tdescr.role, level, isSkillActive, isZero, isEnable, learnState, skillCustomName, customCrewName, proxy)
    else:
        _tankmanRole = tankmanRole or skillRole
        return TankmanSkill(skillName, skillRole, _tankmanRole, level, customName=skillCustomName, crewCustomName=customCrewName, proxy=proxy, **kwargs)
