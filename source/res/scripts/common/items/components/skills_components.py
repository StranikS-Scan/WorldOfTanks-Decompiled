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

    def recreate(self, *args):
        raise NotImplementedError


class SingleNumberSkill(BasicSkill):
    __slots__ = ('_value',)

    def __init__(self, basicSkill, value):
        super(SingleNumberSkill, self).__init__(basicSkill.name, i18n=basicSkill.i18n, icon=basicSkill.icon)
        self._value = value

    def recreate(self, value):
        return self.__class__(BasicSkill(self.name, self.i18n, self.icon), value)


class DualNumberSkill(BasicSkill):
    __slots__ = ('_first', '_second')

    def __init__(self, basicSkill, left, right):
        super(DualNumberSkill, self).__init__(basicSkill.name, i18n=basicSkill.i18n, icon=basicSkill.icon)
        self._first = left
        self._second = right

    def recreate(self, left, right):
        return self.__class__(BasicSkill(self.name, self.i18n, self.icon), left, right)


class BrotherhoodSkill(SingleNumberSkill):
    __slots__ = ()

    @property
    def crewLevelIncrease(self):
        return self._value


class CommanderTutorSkill(SingleNumberSkill):
    __slots__ = ()

    @property
    def xpBonusFactorPerLevel(self):
        return self._value


class CommanderUniversalistSkill(SingleNumberSkill):
    __slots__ = ()

    @property
    def efficiency(self):
        return self._value


class CommanderSkillWithDelay(SingleNumberSkill):
    __slots__ = ()

    @property
    def delay(self):
        return self._value


class CommanderEagleEyeSkill(DualNumberSkill):
    __slots__ = ()

    @property
    def distanceFactorPerLevelWhenDeviceWorking(self):
        return self._first

    @property
    def distanceFactorPerLevelWhenDeviceDestroyed(self):
        return self._second


class DriverTidyPersonSkill(SingleNumberSkill):
    __slots__ = ()

    @property
    def fireStartingChanceFactor(self):
        return self._value


class DriverSmoothDrivingSkill(SingleNumberSkill):
    __slots__ = ()

    @property
    def shotDispersionFactorPerLevel(self):
        return self._value


class DriverVirtuosoSkill(SingleNumberSkill):
    __slots__ = ()

    @property
    def rotationSpeedFactorPerLevel(self):
        return self._value


class DriverRammingMasterSkill(SingleNumberSkill):
    __slots__ = ()

    @property
    def rammingBonusFactorPerLevel(self):
        return self._value


class DriverBadRoadsKingSkill(DualNumberSkill):
    __slots__ = ()

    @property
    def softGroundResistanceFactorPerLevel(self):
        return self._first

    @property
    def mediumGroundResistanceFactorPerLevel(self):
        return self._second


class GunnerSmoothTurretSkill(SingleNumberSkill):
    __slots__ = ()

    @property
    def shotDispersionFactorPerLevel(self):
        return self._value


class GunnerGunsmithSkill(SingleNumberSkill):
    __slots__ = ()

    @property
    def shotDispersionFactorPerLevel(self):
        return self._value


class GunnerSniperSkill(SingleNumberSkill):
    __slots__ = ()

    @property
    def deviceChanceToHitBoost(self):
        return self._value


class GunnerRancorousSkill(DualNumberSkill):
    __slots__ = ()

    @property
    def duration(self):
        return self._first

    @property
    def sectorHalfAngle(self):
        return self._second


class LoaderPedantSkill(SingleNumberSkill):
    __slots__ = ()

    @property
    def ammoBayHealthFactor(self):
        return self._value


class LoaderIntuitionSkill(SingleNumberSkill):
    __slots__ = ()

    @property
    def chance(self):
        return self._value


class LoaderDesperadoSkill(DualNumberSkill):
    __slots__ = ()

    @property
    def vehicleHealthFraction(self):
        return self._first

    @property
    def gunReloadTimeFactor(self):
        return self._second


class RadiomanFinderSkill(SingleNumberSkill):
    __slots__ = ()

    @property
    def visionRadiusFactorPerLevel(self):
        return self._value


class RadiomanInventorSkill(SingleNumberSkill):
    __slots__ = ()

    @property
    def radioDistanceFactorPerLevel(self):
        return self._value


class RadiomanLastEffortSkill(SingleNumberSkill):
    __slots__ = ()

    @property
    def duration(self):
        return self._value


class RadiomanRetransmitterSkill(SingleNumberSkill):
    __slots__ = ()

    @property
    def distanceFactorPerLevel(self):
        return self._value


class SkillsConfig(legacy_stuff.LegacyStuff):
    __slots__ = skills_constants.ROLES | skills_constants.ACTIVE_SKILLS

    @staticmethod
    def getNumberOfActiveSkills():
        return len(skills_constants.ACTIVE_SKILLS)

    def addSkill(self, name, skill):
        setattr(self, name, skill)

    def getSkill(self, name):
        return getattr(self, name, BasicSkill('unknown'))
