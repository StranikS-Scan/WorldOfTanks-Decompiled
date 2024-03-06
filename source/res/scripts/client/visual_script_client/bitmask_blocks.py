# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/visual_script_client/bitmask_blocks.py
from visual_script.bitmask_blocks_common import BitMaskBase
from visual_script.misc import ASPECT
from constants import EQUIPMENT_ERROR_STATES, CollisionFlags, VEHICLE_HIT_FLAGS

class BitMask(BitMaskBase):
    _MASK_TYPES = {'Equipment ErrorStates': EQUIPMENT_ERROR_STATES,
     'Collision Flags': CollisionFlags,
     'Vehicle Hit Flags': VEHICLE_HIT_FLAGS}

    @classmethod
    def blockAspects(cls):
        return [ASPECT.CLIENT]
