# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/common/vehicle_mechanic_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class MechanicsEnum(Enum):
    MAGAZINE_GUN = 'magazineGun'
    AUTO_LOADER_GUN = 'autoLoaderGun'
    AUTO_LOADER_GUN_BOOST = 'autoLoaderGunBoost'
    DAMAGE_MUTABLE = 'damageMutable'
    DUAL_GUN = 'dualGun'
    HYDRAULIC_CHASSIS = 'hydraulicChassis'
    TRACK_WITHIN_TRACK = 'trackWithinTrack'
    SIEGE_MODE = 'siegeMode'
    STUN = 'stun'
    HYDRAULIC_WHEELED_CHASSIS = 'hydraulicWheeledChassis'
    TURBOSHAFT_ENGINE = 'turboshaftEngine'
    ROCKET_ACCELERATION = 'rocketAcceleration'
    TARGET_DESIGNATOR = 'targetDesignator'
    DUAL_ACCURACY = 'dualAccuracy'
    AUTO_SHOOT_GUN = 'autoShootGun'
    TWIN_GUN = 'twinGun'
    IMPROVED_RAMMING = 'improvedRamming'
    CONCENTRATION_MODE = 'concentrationMode'
    BATTLE_FURY = 'battleFury'
    EXTRA_SHOT_CLIP = 'extraShotClip'
    POWER_MODE = 'powerMode'
    ACCURACY_STACKS = 'accuracyStacks'
    SUPPORT_WEAPON = 'supportWeapon'
    PILLBOX_SIEGE_MODE = 'pillboxSiegeMode'
    CHARGEABLE_BURST = 'chargeableBurst'
    RECHARGEABLE_NITRO = 'rechargeableNitro'
    CHARGE_SHOT = 'chargeShot'
    OVERHEAT_STACKS = 'overheatStacks'
    STANCE_DANCE = 'stanceDance'
    STATIONARY_RELOAD = 'stationaryReload'


class VehicleMechanicModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(VehicleMechanicModel, self).__init__(properties=properties, commands=commands)

    def getName(self):
        return MechanicsEnum(self._getString(0))

    def setName(self, value):
        self._setString(0, value.value)

    def getIsSpecial(self):
        return self._getBool(1)

    def setIsSpecial(self, value):
        self._setBool(1, value)

    def getHasVideo(self):
        return self._getBool(2)

    def setHasVideo(self, value):
        self._setBool(2, value)

    def _initialize(self):
        super(VehicleMechanicModel, self)._initialize()
        self._addStringProperty('name')
        self._addBoolProperty('isSpecial', False)
        self._addBoolProperty('hasVideo', False)
