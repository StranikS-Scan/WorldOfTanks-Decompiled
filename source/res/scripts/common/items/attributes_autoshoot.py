# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/attributes_autoshoot.py
from items.attributes_helpers import CommonFactorsHelper
AUTOSHOOT_DYNAMIC_ATTRS = ['rate/multiplier', 'shotDispersionPerSecFactor', 'maxShotDispersionFactor']

class AutoshootFactorsHelper(CommonFactorsHelper):
    ALLOWED_ATTRS = AUTOSHOOT_DYNAMIC_ATTRS
    PREFIX = 'autoShootAttrs/'


attributes_autoshoot_factory = AutoshootFactorsHelper()
