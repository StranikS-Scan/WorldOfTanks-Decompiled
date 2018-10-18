# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/EventPointsPickupSettings.py
from collections import namedtuple

class EventPointsPickupEvents(object):
    SPAWN_EP_PICKIUP = 'SpawnEPPickup'
    REMOVE_EP_PICKUP = 'RemoveEPPickup'


EventPointsPickupSettings = namedtuple('EventPointsPickupSettings', ('epPickupRadius', 'epPickupDuration', 'epEffects'))
