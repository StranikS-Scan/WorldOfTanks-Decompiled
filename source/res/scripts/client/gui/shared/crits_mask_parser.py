# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/crits_mask_parser.py
from shared_utils import BitmaskHelper
from shared_utils import CONST_CONTAINER
from items.vehicles import VEHICLE_DEVICE_TYPE_NAMES, VEHICLE_TANKMAN_TYPE_NAMES

class CRIT_MASK_SUB_TYPES(CONST_CONTAINER):
    DESTROYED_DEVICES = 'destroyedDevices'
    CRITICAL_DEVICES = 'criticalDevices'
    DESTROYED_TANKMENS = 'destroyedTankmen'


def critsParserGenerator(mask):
    maskMap = {CRIT_MASK_SUB_TYPES.DESTROYED_DEVICES: (mask >> 12 & 4095, VEHICLE_DEVICE_TYPE_NAMES),
     CRIT_MASK_SUB_TYPES.CRITICAL_DEVICES: (mask & 255, VEHICLE_DEVICE_TYPE_NAMES),
     CRIT_MASK_SUB_TYPES.DESTROYED_TANKMENS: (mask >> 24 & 255, VEHICLE_TANKMAN_TYPE_NAMES)}
    for subType, (subMask, types) in maskMap.iteritems():
        if subMask > 0:
            for index in BitmaskHelper.iterateInt64SetBitsIndexes(subMask):
                yield (subType, types[index])
