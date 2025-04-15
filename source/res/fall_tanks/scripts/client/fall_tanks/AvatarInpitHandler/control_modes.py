# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fall_tanks/scripts/client/fall_tanks/AvatarInpitHandler/control_modes.py
from AvatarInputHandler.control_modes import PostMortemControlMode

class FallTanksPostMortemCtrlMode(PostMortemControlMode):

    def _isPostmortemDelayEnabled(self):
        return False
