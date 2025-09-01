# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/control_modes.py
import CommandMapping
from AvatarInputHandler import control_modes

class LSArcadeControlMode(control_modes.ArcadeControlMode):

    def handleKeyEvent(self, isDown, key, mods, event=None):
        cmdMap = CommandMapping.g_instance
        return False if cmdMap.isFired(CommandMapping.CMD_CM_VEHICLE_SWITCH_AUTOROTATION, key) and isDown else super(LSArcadeControlMode, self).handleKeyEvent(isDown, key, mods, event)


class LSSniperControlMode(control_modes.SniperControlMode):

    def handleKeyEvent(self, isDown, key, mods, event=None):
        cmdMap = CommandMapping.g_instance
        return False if cmdMap.isFired(CommandMapping.CMD_CM_VEHICLE_SWITCH_AUTOROTATION, key) and isDown else super(LSSniperControlMode, self).handleKeyEvent(isDown, key, mods, event)
