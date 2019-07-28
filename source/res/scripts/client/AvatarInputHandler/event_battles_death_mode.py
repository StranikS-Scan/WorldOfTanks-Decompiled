# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/AvatarInputHandler/event_battles_death_mode.py
import CommandMapping
from AvatarInputHandler.aih_constants import CTRL_MODE_NAME
from control_modes import PostMortemControlMode

class EventDeathTankFollowMode(PostMortemControlMode):

    def handleKeyEvent(self, isDown, key, mods, event=None):
        cmdMap = CommandMapping.g_instance
        if cmdMap.isFired(CommandMapping.CMD_CM_POSTMORTEM_SELF_VEHICLE, key) and isDown and self.curPostmortemDelay is None:
            self.selectPlayer(None)
            self._switchToCtrlMode(CTRL_MODE_NAME.DEATH_FREE_CAM)
            return True
        else:
            super(EventDeathTankFollowMode, self).handleKeyEvent(isDown, key, mods, event)
            return
