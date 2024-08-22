# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/battle/death_cam/death_cam_hud_view_model.py
from enum import Enum
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.battle.death_cam.hud_model import HudModel
from gui.impl.gen.view_models.views.battle.death_cam.marker_model import MarkerModel

class Phase(Enum):
    KILLER = 'killer'
    TRAJECTORY = 'trajectory'
    IMPACT = 'impact'


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


class ImpactMode(Enum):
    PENETRATION = 'penetration'
    NONPENETRATIONDAMAGE = 'nonPenetrationDamage'
    LEGACYHE = 'legacyHE'
    MODERNHE = 'modernHE'


class DeathCamHudViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=34, commands=0):
        super(DeathCamHudViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def marker(self):
        return self._getViewModel(0)

    @staticmethod
    def getMarkerType():
        return MarkerModel

    @property
    def hud(self):
        return self._getViewModel(1)

    @staticmethod
    def getHudType():
        return HudModel

    def getImpactMode(self):
        return ImpactMode(self._getString(2))

    def setImpactMode(self, value):
        self._setString(2, value.value)

    def getPhase(self):
        return Phase(self._getString(3))

    def setPhase(self, value):
        self._setString(3, value.value)

    def getIsAdvanced(self):
        return self._getBool(4)

    def setIsAdvanced(self, value):
        self._setBool(4, value)

    def getIsKillerUnspotted(self):
        return self._getBool(5)

    def setIsKillerUnspotted(self, value):
        self._setBool(5, value)

    def getIsMarkerVisible(self):
        return self._getBool(6)

    def setIsMarkerVisible(self, value):
        self._setBool(6, value)

    def getPhaseDuration(self):
        return self._getNumber(7)

    def setPhaseDuration(self, value):
        self._setNumber(7, value)

    def getPhaseTimePassed(self):
        return self._getNumber(8)

    def setPhaseTimePassed(self, value):
        self._setNumber(8, value)

    def getIsSimplified(self):
        return self._getBool(9)

    def setIsSimplified(self, value):
        self._setBool(9, value)

    def getShellType(self):
        return ShellType(self._getString(10))

    def setShellType(self, value):
        self._setString(10, value.value)

    def getShellIcon(self):
        return self._getString(11)

    def setShellIcon(self, value):
        self._setString(11, value)

    def getShellCaliber(self):
        return self._getNumber(12)

    def setShellCaliber(self, value):
        self._setNumber(12, value)

    def getCaliberRule(self):
        return CaliberRule(self._getString(13))

    def setCaliberRule(self, value):
        self._setString(13, value.value)

    def getShellDamageBasic(self):
        return self._getReal(14)

    def setShellDamageBasic(self, value):
        self._setReal(14, value)

    def getShellVelocityBasic(self):
        return self._getNumber(15)

    def setShellVelocityBasic(self, value):
        self._setNumber(15, value)

    def getShootDistance(self):
        return self._getNumber(16)

    def setShootDistance(self, value):
        self._setNumber(16, value)

    def getShellPenetrationEffective(self):
        return self._getNumber(17)

    def setShellPenetrationEffective(self, value):
        self._setNumber(17, value)

    def getShellPenetrationBasic(self):
        return self._getNumber(18)

    def setShellPenetrationBasic(self, value):
        self._setNumber(18, value)

    def getArmorRelative(self):
        return self._getNumber(19)

    def setArmorRelative(self, value):
        self._setNumber(19, value)

    def getArmorNominal(self):
        return self._getNumber(20)

    def setArmorNominal(self, value):
        self._setNumber(20, value)

    def getShellArmorAngleGain(self):
        return self._getNumber(21)

    def setShellArmorAngleGain(self, value):
        self._setNumber(21, value)

    def getAngleRicochet(self):
        return self._getNumber(22)

    def setAngleRicochet(self, value):
        self._setNumber(22, value)

    def getAngleFailure(self):
        return self._getNumber(23)

    def setAngleFailure(self, value):
        self._setNumber(23, value)

    def getAngleImpact(self):
        return self._getNumber(24)

    def setAngleImpact(self, value):
        self._setNumber(24, value)

    def getShellDamageEffective(self):
        return self._getReal(25)

    def setShellDamageEffective(self, value):
        self._setReal(25, value)

    def getShellDamageRandomizationFactor(self):
        return self._getReal(26)

    def setShellDamageRandomizationFactor(self, value):
        self._setReal(26, value)

    def getDamageDistanceModifier(self):
        return self._getReal(27)

    def setDamageDistanceModifier(self, value):
        self._setReal(27, value)

    def getHasDistanceFalloff(self):
        return self._getBool(28)

    def setHasDistanceFalloff(self, value):
        self._setBool(28, value)

    def getShellDamageBurst(self):
        return self._getNumber(29)

    def setShellDamageBurst(self, value):
        self._setNumber(29, value)

    def getShellDamageLossDistance(self):
        return self._getNumber(30)

    def setShellDamageLossDistance(self, value):
        self._setNumber(30, value)

    def getShellDamageLossProtectionHe(self):
        return self._getNumber(31)

    def setShellDamageLossProtectionHe(self, value):
        self._setNumber(31, value)

    def getShellDamageLossProtectionSpallLiner(self):
        return self._getNumber(32)

    def setShellDamageLossProtectionSpallLiner(self, value):
        self._setNumber(32, value)

    def getDeathReason(self):
        return DeathReason(self._getString(33))

    def setDeathReason(self, value):
        self._setString(33, value.value)

    def _initialize(self):
        super(DeathCamHudViewModel, self)._initialize()
        self._addViewModelProperty('marker', MarkerModel())
        self._addViewModelProperty('hud', HudModel())
        self._addStringProperty('impactMode')
        self._addStringProperty('phase')
        self._addBoolProperty('isAdvanced', False)
        self._addBoolProperty('isKillerUnspotted', False)
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
