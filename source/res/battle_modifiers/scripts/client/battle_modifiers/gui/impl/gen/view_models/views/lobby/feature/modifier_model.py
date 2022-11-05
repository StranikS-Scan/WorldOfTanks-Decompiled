# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_modifiers/scripts/client/battle_modifiers/gui/impl/gen/view_models/views/lobby/feature/modifier_model.py
from enum import Enum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from battle_modifiers.gui.impl.gen.view_models.views.lobby.feature.limit_model import LimitModel

class ModType(Enum):
    FAKE_MODIFIER = 'fakeModifier'
    VEHICLE_HEALTH = 'vehicleHealth'
    GRAVITY_FACTOR = 'gravityFactor'
    DISP_FACTOR_CHASSIS_MOVEMENT = 'dispFactorChassisMovement'
    DISP_FACTOR_CHASSIS_ROTATION = 'dispFactorChassisRotation'
    TURRET_ROTATION_SPEED = 'turretRotationSpeed'
    GUN_ROTATION_SPEED = 'gunRotationSpeed'
    RELOAD_TIME = 'reloadTime'
    CLIP_INTERVAL = 'clipInterval'
    BURST_INTERVAL = 'burstInterval'
    AUTORELOAD_TIME = 'autoreloadTime'
    AIMING_TIME = 'aimingTime'
    SHOT_DISPERSION_RADIUS = 'shotDispersionRadius'
    DISP_FACTOR_TURRET_ROTATION = 'dispFactorTurretRotation'
    DISP_FACTOR_AFTER_SHOT = 'dispFactorAfterShot'
    DISP_FACTOR_WHILE_GUN_DAMAGED = 'dispFactorWhileGunDamaged'
    SHELL_GRAVITY = 'shellGravity'
    SHELL_SPEED = 'shellSpeed'
    PIERCING_POWER_FIRST = 'piercingPowerFirst'
    PIERCING_POWER_LAST = 'piercingPowerLast'
    DAMAGE_RANDOMIZATION = 'damageRandomization'
    PIERCING_POWER_RANDOMIZATION = 'piercingPowerRandomization'
    NORMALIZATION_ANGLE = 'normalizationAngle'
    RICOCHET_ANGLE = 'ricochetAngle'
    ENGINE_POWER = 'enginePower'
    FW_MAX_SPEED = 'fwMaxSpeed'
    BK_MAX_SPEED = 'bkMaxSpeed'
    ROTATION_SPEED_ON_STILL = 'rotationSpeedOnStill'
    ROTATION_SPEED_ON_MOVE = 'rotationSpeedOnMove'
    ARMOR_DAMAGE = 'armorDamage'
    DEVICE_DAMAGE = 'deviceDamage'
    INVISIBILITY_ON_STILL = 'invisibilityOnStill'
    INVISIBILITY_ON_MOVE = 'invisibilityOnMove'
    VISION_RADIUS = 'visionRadius'
    RADIO_DISTANCE = 'radioDistance'
    BATTLE_LENGTH = 'battleLength'
    VEHICLE_RAMMING_DAMAGE = 'vehicleRammingDamage'
    VEHICLE_PRESSURE_DAMAGE = 'vehiclePressureDamage'
    TURRET_RAMMING_DAMAGE = 'turretRammingDamage'
    TURRET_PRESSURE_DAMAGE = 'turretPressureDamage'
    ENV_HULL_DAMAGE = 'envHullDamage'
    ENV_CHASSIS_DAMAGE = 'envChassisDamage'
    ENV_TANKMAN_DAMAGE_CHANCE = 'envTankmanDamageChance'
    ENV_MODULE_DAMAGE_CHANCE = 'envModuleDamageChance'
    REPAIR_SPEED = 'repairSpeed'
    VISION_MIN_RADIUS = 'visionMinRadius'
    VISION_TIME = 'visionTime'
    EQUIPMENT_COOLDOWN = 'equipmentCooldown'


class ModPhysType(Enum):
    UNDEFINED = 'undefined'
    METERS_PER_SECOND = 'metersPerSecond'
    KILOMETERS_PER_HOUR = 'km_per_hour'
    RADIANS = 'radians'
    DEGREES = 'degrees'
    DEGREES_PER_SECOND = 'degrees_per_second'
    HIT_POINTS = 'hitPoints'
    MILLIMETERS = 'millimeters'
    METERS = 'meters'
    SECONDS = 'seconds'
    MINUTES = 'minutes'
    RADIANS_PER_SECOND = 'radians_per_second'
    METER_PER_SECOND_SQUARED = 'meter_per_second_squared'
    PROBABILITY = 'probability'
    DEVIATION = 'deviation'
    LOGIC = 'logic'
    HORSEPOWER = 'horsepower'


class ModUseType(Enum):
    UNDEFINED = 'undefined'
    VAL = 'val'
    MUL = 'mul'
    ADD = 'add'


class ModGameplayImpact(Enum):
    UNDEFINED = 'undefined'
    POSITIVE = 'positive'
    NEGATIVE = 'negative'


class ModifierModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=7, commands=0):
        super(ModifierModel, self).__init__(properties=properties, commands=commands)

    def getModificationType(self):
        return ModType(self._getString(0))

    def setModificationType(self, value):
        self._setString(0, value.value)

    def getResName(self):
        return self._getString(1)

    def setResName(self, value):
        self._setString(1, value)

    def getValue(self):
        return self._getReal(2)

    def setValue(self, value):
        self._setReal(2, value)

    def getPhysicalType(self):
        return ModPhysType(self._getString(3))

    def setPhysicalType(self, value):
        self._setString(3, value.value)

    def getUseType(self):
        return ModUseType(self._getString(4))

    def setUseType(self, value):
        self._setString(4, value.value)

    def getGameplayImpact(self):
        return ModGameplayImpact(self._getString(5))

    def setGameplayImpact(self, value):
        self._setString(5, value.value)

    def getLimits(self):
        return self._getArray(6)

    def setLimits(self, value):
        self._setArray(6, value)

    @staticmethod
    def getLimitsType():
        return LimitModel

    def _initialize(self):
        super(ModifierModel, self)._initialize()
        self._addStringProperty('modificationType')
        self._addStringProperty('resName', '')
        self._addRealProperty('value', 0.0)
        self._addStringProperty('physicalType')
        self._addStringProperty('useType')
        self._addStringProperty('gameplayImpact')
        self._addArrayProperty('limits', Array())
