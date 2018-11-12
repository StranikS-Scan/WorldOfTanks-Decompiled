# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/components/component_constants.py
import collections
from soft_exception import SoftException
Autoreload = collections.namedtuple('Autoreload', 'reloadTime revertFraction')
UNDEFINED_ITEM_TYPE_ID = 0
ZERO_FLOAT = 0.0
ZERO_INT = 0
EMPTY_STRING = ''
EMPTY_TUPLE = ()

class _ReadOnlyDict(dict):

    def __setitem__(self, key, value):
        raise SoftException('ReadOnlyDict set item attempt %s=>%s' % (key, value))

    def update(self, E=None, **F):
        raise SoftException('ReadOnlyDict update attempt %s, %s' % (E, F))


EMPTY_DICT = _ReadOnlyDict()
EMPTY_TAGS = frozenset()
LEVEL = 1
DEFAULT_ARMOR_HOMOGENIZATION = 1.0
DEFAULT_GUN_AUTORELOAD = Autoreload(reloadTime=(0.0,), revertFraction=0.0)
DEFAULT_GUN_BURST = (1, 0.0)
DEFAULT_GUN_CLIP = (1, 0.0)
DEFAULT_FAKE_TURRETS = {'lobby': (),
 'battle': ()}
DEFAULT_HULL_VARIANT_MATCH = (None, None)
DEFAULT_PREMIUM_VEHICLE_XP_FACTOR = 0.0
DEFAULT_SPECIFIC_FRICTION = 0.6867000000000001
DEFAULT_INVISIBILITY_FACTOR = 1.0
DEFAULT_DAMAGE_RANDOMIZATION = 0.25
DEFAULT_PIERCING_POWER_RANDOMIZATION = 0.25
KMH_TO_MS = 0.27778
KG_TO_NEWTON = 9.81
HP_TO_WATTS = 735.5
ALLOWED_EMBLEM_SLOTS = ('player', 'clan', 'inscription', 'insignia', 'insigniaOnGun', 'fixedEmblem', 'fixedInscription')
ALLOWED_SLOTS_ANCHORS = ('paint', 'camouflage', 'projectionDecal', 'effect', 'style')
TANKMEN_GROUPS = ('normalGroups', 'premiumGroups')
