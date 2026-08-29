# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/wt_kill_cam_mode.py
from __future__ import absolute_import
from AvatarInputHandler.kill_cam_modes import LookAtKillerMode

class WTLookAtKillerMode(LookAtKillerMode):

    def _canSwitchToAllyVehicle(self):
        return False
