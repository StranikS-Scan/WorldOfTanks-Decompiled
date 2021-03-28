# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/components/skills_components.py
from items.components import component_constants
from items.components import legacy_stuff
from items.components import shared_components
from items.components import skills_constants

class BasicSkill(legacy_stuff.LegacyStuff):
    __slots__ = ('__name', '__i18n', '__icon')

    def __init__(self, name, i18n=None, icon=None):
        super(BasicSkill, self).__init__()
        self.__name = name
        self.__i18n = i18n
        self.__icon = icon

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
    def icon(self):
        return self.__icon

    @property
    def extensionLessIcon(self):
        return self.__icon.split('.png')[0]

    def recreate(self, *args):
        raise NotImplementedError


class ExtendedSkill(BasicSkill):
    __slots__ = ('_setOfParameters',)

    def __init__(self, basicSkill, *args):
        super(ExtendedSkill, self).__init__(basicSkill.name, i18n=basicSkill.i18n, icon=basicSkill.icon)
        self._setOfParameters = args

    def recreate(self, *args):
        return self.__class__(BasicSkill(self.name, self.i18n, self.icon), *args)


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


class CommanderUniversalistSkill(ExtendedSkill):
    __slots__ = ()

    @property
    def efficiency(self):
        return self._setOfParameters[0]


class CommanderSkillWithDelay(ExtendedSkill):
    __slots__ = ()

    @property
    def delay(self):
        return self._setOfParameters[0]


class CommanderEagleEyeSkill(ExtendedSkill):
    __slots__ = ()

    @property
    def distanceFactorPerLevelWhenDeviceWorking(self):
        return self._setOfParameters[0]

    @property
    def distanceFactorPerLevelWhenDeviceDestroyed(self):
        return self._setOfParameters[1]


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


class DriverTidyPersonSkill(ExtendedSkill):
    __slots__ = ()

    @property
    def fireStartingChanceFactor(self):
        return self._setOfParameters[0]


class DriverSmoothDrivingSkill(ExtendedSkill):
    __slots__ = ()

    @property
    def shotDispersionFactorPerLevel(self):
        return self._setOfParameters[0]


class DriverVirtuosoSkill(ExtendedSkill):
    __slots__ = ()

    @property
    def rotationSpeedFactorPerLevel(self):
        return self._setOfParameters[0]


class DriverRammingMasterSkill(ExtendedSkill):
    __slots__ = ()

    @property
    def rammingBonusFactorPerLevel(self):
        return self._setOfParameters[0]


class DriverBadRoadsKingSkill(ExtendedSkill):
    __slots__ = ()

    @property
    def softGroundResistanceFactorPerLevel(self):
        return self._setOfParameters[0]

    @property
    def mediumGroundResistanceFactorPerLevel(self):
        return self._setOfParameters[1]


class GunnerSmoothTurretSkill(ExtendedSkill):
    __slots__ = ()

    @property
    def shotDispersionFactorPerLevel(self):
        return self._setOfParameters[0]


class GunnerGunsmithSkill(ExtendedSkill):
    __slots__ = ()

    @property
    def shotDispersionFactorPerLevel(self):
        return self._setOfParameters[0]


class GunnerSniperSkill(ExtendedSkill):
    __slots__ = ()

    @property
    def deviceChanceToHitBoost(self):
        return self._setOfParameters[0]


class GunnerRancorousSkill(ExtendedSkill):
    __slots__ = ()

    @property
    def duration(self):
        return self._setOfParameters[0]

    @property
    def sectorHalfAngle(self):
        return self._setOfParameters[1]


class LoaderPedantSkill(ExtendedSkill):
    __slots__ = ()

    @property
    def ammoBayHealthFactor(self):
        return self._setOfParameters[0]


class LoaderIntuitionSkill(ExtendedSkill):
    __slots__ = ()

    @property
    def quickShellChangerFactorPerPercent(self):
        return self._setOfParameters[0]


class LoaderDesperadoSkill(ExtendedSkill):
    __slots__ = ()

    @property
    def vehicleHealthFraction(self):
        return self._setOfParameters[0]

    @property
    def gunReloadTimeFactor(self):
        return self._setOfParameters[1]


class RadiomanFinderSkill(ExtendedSkill):
    __slots__ = ()

    @property
    def visionRadiusFactorPerLevel(self):
        return self._setOfParameters[0]


class RadiomanInventorSkill(ExtendedSkill):
    __slots__ = ()

    @property
    def radioDistanceFactorPerLevel(self):
        return self._setOfParameters[0]


class RadiomanLastEffortSkill(ExtendedSkill):
    __slots__ = ()

    @property
    def duration(self):
        return self._setOfParameters[0]


class RadiomanRetransmitterSkill(ExtendedSkill):
    __slots__ = ()

    @property
    def distanceFactorPerLevel(self):
        return self._setOfParameters[0]


class SkillsConfig(legacy_stuff.LegacyStuff):
    __slots__ = skills_constants.ROLES | skills_constants.ACTIVE_SKILLS

    @staticmethod
    def getNumberOfActiveSkills():
        return len(skills_constants.ACTIVE_SKILLS)

    def addSkill(self, name, skill):
        setattr(self, name, skill)

    def getSkill(self, name):
        return getattr(self, name, BasicSkill('unknown'))
