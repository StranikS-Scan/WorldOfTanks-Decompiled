# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/prebattle_highlights/pbh_constants.py
from __future__ import absolute_import
from shared_utils import CONST_CONTAINER
TANK_SIZE_LOWER_BOUNDS = (float('-inf'), 5.0, 8.0)
TANK_POS_TEMPLATE = 'pbh_top{}_{}'
TANK_CAMERA_TEMPLATE = 'pbh_camera_{}_{}'
MARKER_X_FACTOR = 0
MARKER_Y_FACTOR = 1.1

class TankSizes(CONST_CONTAINER):
    SMALL = 'small'
    MEDIUM = 'medium'
    BIG = 'big'
    ORDERED_SIZES = (SMALL, MEDIUM, BIG)
