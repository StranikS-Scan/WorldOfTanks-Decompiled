# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/components/skills_components.py
from typing import Optional
from items.components import component_constants
from items.components import legacy_stuff
from items.components import skills_constants
from items.components.shared_components import I18nComponent
from items.components.skills_constants import SkillTypeName
from perks_constants import StubPerkIDs

class BasicSkill(legacy_stuff.LegacyStuff):
    __slots__ = ('__name', '__i18n', '__icon', '__vsePerk', '__uiSettings')

    def __init__(self, name, i18n=None, icon=None, vsePerk=None, uiSettings=None):
        super(BasicSkill, self).__init__()
        self.__name = name
        self.__i18n = i18n
        self.__icon = icon
        self.__vsePerk = vsePerk
        self.__uiSettings = uiSettings

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, self.__name)

    @property
    def name(self):
        return self.__name

    @property
    def i18n(self):
        return self.__i18n

    @property
    def userString(self):
        if self.__i18n is not None:
            return self.__i18n.userString
        else:
            return component_constants.EMPTY_STRING
            return

    @property
    def description(self):
        if self.__i18n is not None:
            return self.__i18n.description
        else:
            return component_constants.EMPTY_STRING
            return

    @property
    def maxLvlDescription(self):
        if self.__i18n is not None:
            return self.__i18n.maxLvlDescription
        else:
            return component_constants.EMPTY_STRING
            return

    @property
    def currentLvlDescription(self):
        if self.__i18n is not None:
            return self.__i18n.currentLvlDescription
        else:
            return component_constants.EMPTY_STRING
            return

    @property
    def altDescription(self):
        if self.__i18n is not None:
            return self.__i18n.altDescription
        else:
            return component_constants.EMPTY_STRING
            return

    @property
    def altInfo(self):
        if self.__i18n is not None:
            return self.__i18n.altInfo
        else:
            return component_constants.EMPTY_STRING
            return

    @property
    def icon(self):
        return self.__icon

    @property
    def extensionLessIcon(self):
        return self.__icon.split('.png')[0]

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
        return self.uiSettings.typeName is SkillTypeName.SITUATIONAL if self.uiSettings else False

    @property
    def typeName(self):
        return self.uiSettings.typeName if self.uiSettings else SkillTypeName.MAIN

    @property
    def params(self):
        return self.uiSettings.params if self.uiSettings else {}


class ExtendedSkill(BasicSkill):
    __slots__ = ('_setOfParameters',)

    def __init__(self, basicSkill, *args):
        super(ExtendedSkill, self).__init__(basicSkill.name, i18n=basicSkill.i18n, icon=basicSkill.icon, vsePerk=basicSkill.vsePerk, uiSettings=basicSkill.uiSettings)
        self._setOfParameters = args

    def recreate(self, *args):
        return self.__class__(BasicSkill(self.name, self.i18n, self.icon, self.vsePerk, self.uiSettings), *args)


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


class SkillLocales(I18nComponent):
    __slots__ = ('__maxLvlDescription', '__currentLvlDescription', '__altDescription', '__altInfo')

    def __init__(self, userName='', description='', maxLvlDescription='', currentLvlDescription='', altDescription='', altInfo=''):
        super(SkillLocales, self).__init__(userName, description, description)
        self.__maxLvlDescription = maxLvlDescription
        self.__currentLvlDescription = currentLvlDescription
        self.__altDescription = altDescription
        self.__altInfo = altInfo

    @property
    def maxLvlDescription(self):
        return self.__maxLvlDescription

    @property
    def currentLvlDescription(self):
        return self.__currentLvlDescription

    @property
    def altDescription(self):
        return self.__altDescription

    @property
    def altInfo(self):
        return self.__altInfo
