# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/wt_event/wt_event_constants.py
from enum import Enum

class VehicleCharacteristics(Enum):
    PROS = 'pros'
    CONS = 'cons'


class BonusGroup(object):
    STYLE_3D = 'style3d'
    VEHICLES = 2
    LOOTBOX = 'lootbox'
    OTHER = 'other'
    HIGH = 0
    AVERAGE = 1
    LOW = 2
    RENT = 3


def getBonusGroup(num):
    if num == 0:
        return BonusGroup.HIGH
    if num == 1:
        return BonusGroup.AVERAGE
    if num == 2:
        return BonusGroup.LOW
    return BonusGroup.RENT if num == 3 else None
