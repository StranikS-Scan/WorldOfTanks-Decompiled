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
    """
    Returns types of critical hits of the given crit mask. Types are represented by strings
    (see VEHICLE_DEVICE_TYPE_NAMES and VEHICLE_TANKMAN_TYPE_NAMES).
    Note that generator returns types according to priority rules (
    destroyed devices/devices with critical damage/destroyed tank mans).
    
    The mask has the following format: |destroyed tankmans|destroyed devices|critical devices|. For
    details see ..\\scripts\\item_defs\x0behicles\\common\x0behicle.xml and buildCritsFromAttackResults
    method of ..\\scripts\\cell\\helpers module.
    
    :param mask: Crits bit mask
    :return: string of crit type (from VEHICLE_DEVICE_TYPE_NAMES or VEHICLE_TANKMAN_TYPE_NAMES)
    """
    maskMap = {CRIT_MASK_SUB_TYPES.DESTROYED_DEVICES: (mask >> 12 & 4095, VEHICLE_DEVICE_TYPE_NAMES),
     CRIT_MASK_SUB_TYPES.CRITICAL_DEVICES: (mask & 255, VEHICLE_DEVICE_TYPE_NAMES),
     CRIT_MASK_SUB_TYPES.DESTROYED_TANKMENS: (mask >> 24 & 255, VEHICLE_TANKMAN_TYPE_NAMES)}
    for subType, (subMask, types) in maskMap.iteritems():
        if subMask > 0:
            for index in BitmaskHelper.iterateInt64SetBitsIndexes(subMask):
                yield (subType, types[index])
