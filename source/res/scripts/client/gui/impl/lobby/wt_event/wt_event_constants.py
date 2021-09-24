# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/wt_event/wt_event_constants.py
from enum import Enum

class VehicleCharacteristics(Enum):
    PROS = 'pros'
    CONS = 'cons'


class EventCollections(Enum):
    HUNTER = 'wt_hunter'
    BOSS = 'wt_boss'


class BonusGroup(object):
    COLLECTION = 'collection'
    STYLE_3D = 'style3d'
    VEHICLES = 'vehicles'
    LOOTBOX = 'lootbox'
    OTHER = 'other'


class SpecialVehicleSource(object):
    EXCHANGE = 'exchange'
    MULTIPLE_OPENING = 'multipleOpening'
