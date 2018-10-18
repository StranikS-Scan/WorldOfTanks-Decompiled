# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/event_points_event_type.py
from collections import namedtuple
POINTS_LOST = 1
POINTS_SAVED = 2
PLAYER_DIED = 3
PLAYER_KILLED_CREEP = 4
POINTS_PICKED = 5
EventPointsEvent = namedtuple('EventPointsEvent', ('vehicleID', 'type', 'points', 'enemyID'))
EventPointsEvent.__new__.__defaults__ = (None, None, None, None)
VehicleKilledParams = namedtuple('VehicleKilledParams', ('position', 'rewardAmount'))
VehicleKilledParams.__new__.__defaults__ = (None, None)
