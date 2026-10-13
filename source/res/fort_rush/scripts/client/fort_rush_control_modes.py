# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fort_rush/scripts/client/fort_rush_control_modes.py
from __future__ import absolute_import
import BigWorld
import CommandMapping
from AvatarInputHandler.control_modes import PostMortemControlMode
_VEHICLE_SWITCH_CMDS = (CommandMapping.CMD_CM_POSTMORTEM_SELF_VEHICLE,
 CommandMapping.CMD_CM_POSTMORTEM_TARGET_VEHICLE,
 CommandMapping.CMD_CM_POSTMORTEM_NEXT_VEHICLE,
 CommandMapping.CMD_CM_POSTMORTEM_PREV_VEHICLE)

class FortRushPostMortemControlMode(PostMortemControlMode):

    def enable(self, **args):
        args['immediateSwitchToAllyVehicle'] = False
        super(FortRushPostMortemControlMode, self).enable(**args)

    def selectPlayer(self, vehID):
        if vehID == BigWorld.player().playerVehicleID:
            super(FortRushPostMortemControlMode, self).selectPlayer(vehID)

    def onSwitchViewpoint(self, vehicleID, cameraPos):
        pass

    def handleKeyEvent(self, isDown, key, mods, event=None):
        if isDown:
            cmdMap = CommandMapping.g_instance
            if any((cmdMap.isFired(cmd, key) for cmd in _VEHICLE_SWITCH_CMDS)):
                return False
        return super(FortRushPostMortemControlMode, self).handleKeyEvent(isDown, key, mods, event)
