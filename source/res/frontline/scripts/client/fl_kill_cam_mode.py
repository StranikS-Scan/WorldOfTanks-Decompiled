# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/fl_kill_cam_mode.py
from AvatarInputHandler.kill_cam_modes import LookAtKillerMode

class FLLookAtKillerMode(LookAtKillerMode):

    def _canSwitchToAllyVehicle(self):
        return False
