# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_modifiers/modifier_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class ModType(Enum):
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
    RADIANS = 'radians'
    HIT_POINTS = 'hitPoints'
    MILLIMETERS = 'millimeters'
    SECONDS = 'seconds'
    METERS = 'meters'
    RADIANS_PER_SECOND = 'radians_per_second'
    METER_PER_SECOND_SQUARED = 'meter_per_second_squared'
    PROBABILITY = 'probability'
    DEVIATION = 'deviation'


class ModUseType(Enum):
    VAL = 'val'
    MUL = 'mul'
    ADD = 'add'


class ModGameplayImpact(Enum):
    UNDEFINED = 'undefined'
    POSITIVE = 'positive'
    NEGATIVE = 'negative'


class ModifierModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=5, commands=0):
        super(ModifierModel, self).__init__(properties=properties, commands=commands)

    def getModificationType(self):
        return ModType(self._getString(0))

    def setModificationType(self, value):
        self._setString(0, value.value)

    def getValue(self):
        return self._getReal(1)

    def setValue(self, value):
        self._setReal(1, value)

    def getPhysicalType(self):
        return ModPhysType(self._getString(2))

    def setPhysicalType(self, value):
        self._setString(2, value.value)

    def getUseType(self):
        return ModUseType(self._getString(3))

    def setUseType(self, value):
        self._setString(3, value.value)

    def getGameplayImpact(self):
        return ModGameplayImpact(self._getString(4))

    def setGameplayImpact(self, value):
        self._setString(4, value.value)

    def _initialize(self):
        super(ModifierModel, self)._initialize()
        self._addStringProperty('modificationType')
        self._addRealProperty('value', 0.0)
        self._addStringProperty('physicalType')
        self._addStringProperty('useType')
        self._addStringProperty('gameplayImpact')
