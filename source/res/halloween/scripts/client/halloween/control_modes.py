# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/control_modes.py
from __future__ import absolute_import
import CommandMapping
from AvatarInputHandler import control_modes

class HWArcadeControlMode(control_modes.ArcadeControlMode):

    def handleKeyEvent(self, isDown, key, mods, event=None):
        cmdMap = CommandMapping.g_instance
        return False if cmdMap.isFired(CommandMapping.CMD_CM_VEHICLE_SWITCH_AUTOROTATION, key) and isDown else super(HWArcadeControlMode, self).handleKeyEvent(isDown, key, mods, event)


class HWSniperControlMode(control_modes.SniperControlMode):

    def handleKeyEvent(self, isDown, key, mods, event=None):
        cmdMap = CommandMapping.g_instance
        return False if cmdMap.isFired(CommandMapping.CMD_CM_VEHICLE_SWITCH_AUTOROTATION, key) and isDown else super(HWSniperControlMode, self).handleKeyEvent(isDown, key, mods, event)


class HWPostMortemControlMode(control_modes.PostMortemControlMode):

    def _isPostmortemDelayEnabled(self):
        return False
