# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/common/vehicle_mechanic_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class MechanicsEnum(Enum):
    UNKNOWN = 'unknown'
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
    OVERHEAT_GUN = 'overheatGun'
    HEATING_ZONES_GUN = 'heatingZonesGun'
    STAGED_JET_BOOSTERS = 'stagedJetBoosters'


class MechanicsRank(Enum):
    UNDEFINED = 'undefined'
    SILVER = 'silver'
    GOLD = 'gold'


class VehicleMechanicModel(ViewModel):
    __slots__ = ()
    MIN_SPECIAL_PRIORITY = 1

    def __init__(self, properties=4, commands=0):
        super(VehicleMechanicModel, self).__init__(properties=properties, commands=commands)

    def getName(self):
        return MechanicsEnum(self._getString(0))

    def setName(self, value):
        self._setString(0, value.value)

    def getPriority(self):
        return self._getNumber(1)

    def setPriority(self, value):
        self._setNumber(1, value)

    def getRank(self):
        return MechanicsRank(self._getString(2))

    def setRank(self, value):
        self._setString(2, value.value)

    def getHasVideo(self):
        return self._getBool(3)

    def setHasVideo(self, value):
        self._setBool(3, value)

    def _initialize(self):
        super(VehicleMechanicModel, self)._initialize()
        self._addStringProperty('name')
        self._addNumberProperty('priority', 0)
        self._addStringProperty('rank', MechanicsRank.UNDEFINED.value)
        self._addBoolProperty('hasVideo', False)
