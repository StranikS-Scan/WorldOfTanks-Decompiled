# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/battle/death_cam/marker_view_model.py
from enum import Enum
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.battle.death_cam.marker_model import MarkerModel

class Phase(Enum):
    KILLER = 'killer'
    TRAJECTORY = 'trajectory'
    IMPACT = 'impact'


class ImpactMode(Enum):
    PENETRATION = 'penetration'
    NONPENETRATIONDAMAGE = 'nonPenetrationDamage'
    LEGACYHE = 'legacyHE'
    MODERNHE = 'modernHE'


class CaliberRule(Enum):
    NONE = 'None'
    TWOCALIBER = 'TwoCaliber'
    THREECALIBER = 'ThreeCaliber'


class DeathReason(Enum):
    HP = ''
    IGNITION = 'ignition'
    DETONATION = 'detonation'
    CREW = 'crew'


class ShellType(Enum):
    ARMORPIERCING = 'ARMOR_PIERCING'
    ARMORPIERCINGCR = 'ARMOR_PIERCING_CR'
    ARMORPIERCINGCRPREMIUM = 'ARMOR_PIERCING_CR_PREMIUM'
    ARMORPIERCINGPREMIUM = 'ARMOR_PIERCING_PREMIUM'
    HIGHEXPLOSIVE = 'HIGH_EXPLOSIVE'
    HIGHEXPLOSIVEMODERN = 'HIGH_EXPLOSIVE_MODERN'
    HIGHEXPLOSIVEMODERNPREMIUM = 'HIGH_EXPLOSIVE_MODERN_PREMIUM'
    HIGHEXPLOSIVEPREMIUM = 'HIGH_EXPLOSIVE_PREMIUM'
    HIGHEXPLOSIVESPG = 'HIGH_EXPLOSIVE_SPG'
    HIGHEXPLOSIVESPGSTUN = 'HIGH_EXPLOSIVE_SPG_STUN'
    HOLLOWCHARGE = 'HOLLOW_CHARGE'
    HOLLOWCHARGEPREMIUM = 'HOLLOW_CHARGE_PREMIUM'


class MarkerViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=33, commands=0):
        super(MarkerViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def base(self):
        return self._getViewModel(0)

    @staticmethod
    def getBaseType():
        return MarkerModel

    def getPhase(self):
        return Phase(self._getString(1))

    def setPhase(self, value):
        self._setString(1, value.value)

    def getIsAdvanced(self):
        return self._getBool(2)

    def setIsAdvanced(self, value):
        self._setBool(2, value)

    def getIsKillerUnspotted(self):
        return self._getBool(3)

    def setIsKillerUnspotted(self, value):
        self._setBool(3, value)

    def getImpactMode(self):
        return ImpactMode(self._getString(4))

    def setImpactMode(self, value):
        self._setString(4, value.value)

    def getIsMarkerVisible(self):
        return self._getBool(5)

    def setIsMarkerVisible(self, value):
        self._setBool(5, value)

    def getPhaseDuration(self):
        return self._getNumber(6)

    def setPhaseDuration(self, value):
        self._setNumber(6, value)

    def getPhaseTimePassed(self):
        return self._getNumber(7)

    def setPhaseTimePassed(self, value):
        self._setNumber(7, value)

    def getIsSimplified(self):
        return self._getBool(8)

    def setIsSimplified(self, value):
        self._setBool(8, value)

    def getShellType(self):
        return ShellType(self._getString(9))

    def setShellType(self, value):
        self._setString(9, value.value)

    def getShellIcon(self):
        return self._getString(10)

    def setShellIcon(self, value):
        self._setString(10, value)

    def getShellCaliber(self):
        return self._getNumber(11)

    def setShellCaliber(self, value):
        self._setNumber(11, value)

    def getCaliberRule(self):
        return CaliberRule(self._getString(12))

    def setCaliberRule(self, value):
        self._setString(12, value.value)

    def getShellDamageBasic(self):
        return self._getReal(13)

    def setShellDamageBasic(self, value):
        self._setReal(13, value)

    def getShellVelocityBasic(self):
        return self._getNumber(14)

    def setShellVelocityBasic(self, value):
        self._setNumber(14, value)

    def getShootDistance(self):
        return self._getNumber(15)

    def setShootDistance(self, value):
        self._setNumber(15, value)

    def getShellPenetrationEffective(self):
        return self._getNumber(16)

    def setShellPenetrationEffective(self, value):
        self._setNumber(16, value)

    def getShellPenetrationBasic(self):
        return self._getNumber(17)

    def setShellPenetrationBasic(self, value):
        self._setNumber(17, value)

    def getArmorRelative(self):
        return self._getNumber(18)

    def setArmorRelative(self, value):
        self._setNumber(18, value)

    def getArmorNominal(self):
        return self._getNumber(19)

    def setArmorNominal(self, value):
        self._setNumber(19, value)

    def getShellArmorAngleGain(self):
        return self._getNumber(20)

    def setShellArmorAngleGain(self, value):
        self._setNumber(20, value)

    def getAngleRicochet(self):
        return self._getNumber(21)

    def setAngleRicochet(self, value):
        self._setNumber(21, value)

    def getAngleFailure(self):
        return self._getNumber(22)

    def setAngleFailure(self, value):
        self._setNumber(22, value)

    def getAngleImpact(self):
        return self._getNumber(23)

    def setAngleImpact(self, value):
        self._setNumber(23, value)

    def getShellDamageEffective(self):
        return self._getReal(24)

    def setShellDamageEffective(self, value):
        self._setReal(24, value)

    def getShellDamageRandomizationFactor(self):
        return self._getReal(25)

    def setShellDamageRandomizationFactor(self, value):
        self._setReal(25, value)

    def getDamageDistanceModifier(self):
        return self._getReal(26)

    def setDamageDistanceModifier(self, value):
        self._setReal(26, value)

    def getHasDistanceFalloff(self):
        return self._getBool(27)

    def setHasDistanceFalloff(self, value):
        self._setBool(27, value)

    def getShellDamageBurst(self):
        return self._getNumber(28)

    def setShellDamageBurst(self, value):
        self._setNumber(28, value)

    def getShellDamageLossDistance(self):
        return self._getNumber(29)

    def setShellDamageLossDistance(self, value):
        self._setNumber(29, value)

    def getShellDamageLossProtectionHe(self):
        return self._getNumber(30)

    def setShellDamageLossProtectionHe(self, value):
        self._setNumber(30, value)

    def getShellDamageLossProtectionSpallLiner(self):
        return self._getNumber(31)

    def setShellDamageLossProtectionSpallLiner(self, value):
        self._setNumber(31, value)

    def getDeathReason(self):
        return DeathReason(self._getString(32))

    def setDeathReason(self, value):
        self._setString(32, value.value)

    def _initialize(self):
        super(MarkerViewModel, self)._initialize()
        self._addViewModelProperty('base', MarkerModel())
        self._addStringProperty('phase')
        self._addBoolProperty('isAdvanced', False)
        self._addBoolProperty('isKillerUnspotted', False)
        self._addStringProperty('impactMode')
        self._addBoolProperty('isMarkerVisible', False)
        self._addNumberProperty('phaseDuration', 0)
        self._addNumberProperty('phaseTimePassed', 0)
        self._addBoolProperty('isSimplified', False)
        self._addStringProperty('shellType')
        self._addStringProperty('shellIcon', '')
        self._addNumberProperty('shellCaliber', 0)
        self._addStringProperty('caliberRule')
        self._addRealProperty('shellDamageBasic', 0.0)
        self._addNumberProperty('shellVelocityBasic', 0)
        self._addNumberProperty('shootDistance', 0)
        self._addNumberProperty('shellPenetrationEffective', 0)
        self._addNumberProperty('shellPenetrationBasic', 0)
        self._addNumberProperty('armorRelative', 0)
        self._addNumberProperty('armorNominal', 0)
        self._addNumberProperty('shellArmorAngleGain', 0)
        self._addNumberProperty('angleRicochet', 0)
        self._addNumberProperty('angleFailure', 0)
        self._addNumberProperty('angleImpact', 0)
        self._addRealProperty('shellDamageEffective', 0.0)
        self._addRealProperty('shellDamageRandomizationFactor', 0.0)
        self._addRealProperty('damageDistanceModifier', 0.0)
        self._addBoolProperty('hasDistanceFalloff', False)
        self._addNumberProperty('shellDamageBurst', 0)
        self._addNumberProperty('shellDamageLossDistance', 0)
        self._addNumberProperty('shellDamageLossProtectionHe', 0)
        self._addNumberProperty('shellDamageLossProtectionSpallLiner', 0)
        self._addStringProperty('deathReason')
