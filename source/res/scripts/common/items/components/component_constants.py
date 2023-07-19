# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/components/component_constants.py
import collections
from soft_exception import SoftException
from wrapped_reflection_framework import reflectedNamedTuple
from Math import Vector3
Autoreload = collections.namedtuple('Autoreload', ['reloadTime',
 'boostStartTime',
 'boostResidueTime',
 'boostFraction'])
AutoShoot = collections.namedtuple('AutoShoot', ['shotDispersionPerSec', 'maxShotDispersion'])
SpinGun = collections.namedtuple('SpinGun', ['spinUpTimeout',
 'spinDownTimeout',
 'isSpinUpShootingEnable',
 'startFactor'])
DualGun = reflectedNamedTuple('DualGun', ['chargeTime',
 'shootImpulse',
 'reloadLockTime',
 'reloadTimes',
 'rateTime',
 'chargeThreshold',
 'afterShotDelay',
 'preChargeIndication',
 'chargeCancelTime'])
UNDEFINED_ITEM_TYPE_ID = 0
ZERO_FLOAT = 0.0
ZERO_INT = 0
ZERO_VECTOR3 = Vector3(0.0, 0.0, 0.0)
EMPTY_STRING = ''
EMPTY_TUPLE = ()
INFLUENCE_ALL = 0
INFLUENCE_ALLY = 1
INFLUENCE_ENEMY = 2

class _ReadOnlyDict(dict):

    def __setitem__(self, key, value):
        raise SoftException('ReadOnlyDict set item attempt %s=>%s' % (key, value))

    def update(self, E=None, **F):
        raise SoftException('ReadOnlyDict update attempt %s, %s' % (E, F))


EMPTY_DICT = _ReadOnlyDict()
EMPTY_TAGS = frozenset()
LEVEL = 1
DEFAULT_ARMOR_HOMOGENIZATION = 1.0
DEFAULT_GUN_AUTORELOAD = Autoreload(reloadTime=(0.0,), boostStartTime=0.0, boostResidueTime=0.0, boostFraction=1.0)
DEFAULT_GUN_BURST = (1, 0.0)
DEFAULT_GUN_CLIP = (1, 0.0)
DEFAULT_GUN_DUALGUN = DualGun(chargeTime=4.0, shootImpulse=100.0, reloadLockTime=10.0, reloadTimes=(10, 8), rateTime=5, chargeThreshold=0.5, afterShotDelay=0.5, preChargeIndication=0.25, chargeCancelTime=0.18)
DEFAULT_GUN_AUTOSHOOT = AutoShoot(shotDispersionPerSec=0.0, maxShotDispersion=0.0)
DEFAULT_SPIN_GUN = SpinGun(startFactor=0.0, spinUpTimeout=0.0, spinDownTimeout=0.0, isSpinUpShootingEnable=True)
DEFAULT_FAKE_TURRETS = {'lobby': (),
 'battle': ()}
DEFAULT_HULL_VARIANT_MATCH = (None, None)
DEFAULT_PREMIUM_VEHICLE_XP_FACTOR = 0.0
DEFAULT_SPECIFIC_FRICTION = 0.6867000000000001
DEFAULT_INVISIBILITY_FACTOR = 1.0
DEFAULT_DAMAGE_RANDOMIZATION = 0.25
DEFAULT_PIERCING_POWER_RANDOMIZATION = 0.25
DEFAULT_MODERN_HE_OBSTACLE_PENETRATION = True
DEFAULT_MODERN_HE_SHIELD_PENETRATION = True
DEFAULT_PIERCING_SPALLS = True
MODERN_HE_PIERCING_POWER_REDUCTION_FACTOR_FOR_DESTRUCTIBLES = 1.0
MODERN_HE_PIERCING_POWER_REDUCTION_FACTOR_FOR_SHIELDS = 3.0
MODERN_HE_DAMAGE_ABSORPTION_FACTOR = 0.0
KMH_TO_MS = 0.27778
MS_TO_KMH = 3.5999712
KG_TO_NEWTON = 9.81
HP_TO_WATTS = 735.5
ALLOWED_EMBLEM_SLOTS = ('player', 'clan', 'inscription', 'insignia', 'insigniaOnGun', 'fixedEmblem', 'fixedInscription')
ALLOWED_PROJECTION_DECALS_ANCHORS = ('projectionDecal', 'fixedProjectionDecal')
ALLOWED_MISC_SLOTS = ('sequence', 'attachment')
ALLOWED_SLOTS_ANCHORS = ('paint', 'camouflage', 'effect', 'style')
TANKMEN_GROUPS = ('normalGroups', 'premiumGroups')
MAIN_TRACK_PAIR_IDX = 0
DynamicShotEffect = collections.namedtuple('DynamicShotEffect', ['effectsIndex', 'minShotsCount', 'maxShotsCount'])
DYNAMIC_SHOT_MAX_COUNT = 10000
ShootImpulse = collections.namedtuple('ShootImpulse', ['magnitude', 'applicationPoint', 'isStillSafe'])
