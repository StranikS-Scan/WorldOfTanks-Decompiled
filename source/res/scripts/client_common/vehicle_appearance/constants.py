# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client_common/vehicle_appearance/constants.py
from __future__ import absolute_import
import enum
DEFAULT_STICKERS_ALPHA = 1.0
PERIODIC_UPDATE_TIME = 0.25
DIRT_UPDATE_MIN_TIME = 0.05

class AppearanceState(enum.IntEnum):
    CREATED = 0
    CONSTRUCTED = 1
    COMPONENTS_CREATED = 2
    ACTIVATED = 3
    DEACTIVATED = 4
    DESTROYED = 5
