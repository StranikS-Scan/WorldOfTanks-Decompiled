# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/components/skills_components.py
from typing import Optional
from items.components import legacy_stuff
from items.components import skills_constants
from items.components.skills_constants import SkillTypeName
from perks_constants import StubPerkIDs

class BasicSkill(legacy_stuff.LegacyStuff):
    __slots__ = ('__name', '__vsePerk', '__uiSettings')

    def __init__(self, name, vsePerk=None, uiSettings=None):
        super(BasicSkill, self).__init__()
        self.__name = name
        self.__vsePerk = vsePerk
        self.__uiSettings = uiSettings

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, self.__name)

    @property
    def name(self):
        return self.__name

    @property
    def vsePerk(self):
        return self.__vsePerk

    @property
    def kpi(self):
        return self.uiSettings.kpi if self.uiSettings else []

    @property
    def tooltipSection(self):
        return self.uiSettings.tooltipSection if self.uiSettings else 'skill'

    def recreate(self, *args):
        raise NotImplementedError

    @property
    def uiSettings(self):
        return self.__uiSettings

    @property
    def situational(self):
        return self.uiSettings.typeName == SkillTypeName.SITUATIONAL if self.uiSettings else False

    @property
    def typeName(self):
        return self.uiSettings.typeName if self.uiSettings else SkillTypeName.MAIN

    @property
    def params(self):
        return self.uiSettings.params if self.uiSettings else {}


class ExtendedSkill(BasicSkill):
    __slots__ = ('_setOfParameters',)

    def __init__(self, basicSkill, *args):
        super(ExtendedSkill, self).__init__(basicSkill.name, vsePerk=basicSkill.vsePerk, uiSettings=basicSkill.uiSettings)
        self._setOfParameters = args

    def recreate(self, *args):
        return self.__class__(BasicSkill(self.name, self.vsePerk, self.uiSettings), *args)


class BrotherhoodSkill(ExtendedSkill):
    __slots__ = ()

    @property
    def crewLevelIncrease(self):
        return self._setOfParameters[0]


class CommanderTutorSkill(ExtendedSkill):
    __slots__ = ()

    @property
    def xpBonusFactorPerLevel(self):
        return self._setOfParameters[0]

    @property
    def efficiency(self):
        return self._setOfParameters[1]


class CommanderSkillWithDelay(ExtendedSkill):
    __slots__ = ()

    @property
    def delay(self):
        return self._setOfParameters[0]


class CommanderEnemyShotPredictor(ExtendedSkill):
    __slots__ = ()

    @property
    def minExplosionRadius(self):
        return self._setOfParameters[0]

    @property
    def explosionMultiplier(self):
        return self._setOfParameters[1]

    @property
    def recalculatingHeight(self):
        return self._setOfParameters[2]

    @property
    def targetRadius(self):
        return self._setOfParameters[3]


class CommonSkill(ExtendedSkill):
    __slots__ = ()


class DriverSmoothDrivingSkill(ExtendedSkill):
    __slots__ = ()

    @property
    def shotDispersionFactorPerLevel(self):
        return self._setOfParameters[0]


class GunnerArmorerSkill(ExtendedSkill):
    __slots__ = ()

    @property
    def shotDispersionFactorPerLevel(self):
        return self._setOfParameters[0]


class GunnerSniperSkill(ExtendedSkill):
    __slots__ = ()

    @property
    def deviceChanceToHitBoost(self):
        return self._setOfParameters[0]


class RadiomanLastEffortSkill(ExtendedSkill):
    __slots__ = ()

    @property
    def durationPerLevel(self):
        return self._setOfParameters[0]

    @property
    def chanceToHitPerLevel(self):
        return self._setOfParameters[1]


class CrewMasterySkill(ExtendedSkill):
    __slots__ = ()

    @property
    def crewLevelIncrease(self):
        return self._setOfParameters[0]


class SkillsConfig(legacy_stuff.LegacyStuff):
    __slots__ = skills_constants.ROLES | skills_constants.ACTIVE_SKILLS | {'vsePerkToSkill'}

    def __init__(self):
        self.vsePerkToSkill = {StubPerkIDs.COMMANDER_TUTOR: 'commander_tutor'}

    @staticmethod
    def getNumberOfActiveSkills():
        return len(skills_constants.ACTIVE_SKILLS)

    def addSkill(self, name, skill):
        setattr(self, name, skill)
        vsePerk = skill.vsePerk
        if vsePerk is not None:
            self.vsePerkToSkill[vsePerk] = name
        return

    def getSkill(self, name):
        return getattr(self, name, BasicSkill('unknown'))
