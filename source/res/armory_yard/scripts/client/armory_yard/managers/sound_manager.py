# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: armory_yard/scripts/client/armory_yard/managers/sound_manager.py
import SoundGroups
from armory_yard.gui.Scaleform.daapi.view.lobby.hangar.sound_constants import SOUNDS

def setSoundDroneMode(isPostProgression):
    if isPostProgression:
        SoundGroups.g_instance.setSwitch(SOUNDS.SOUND_DRONE_SWITCH_GROUP, SOUNDS.SOUND_DRONE_02)
    else:
        SoundGroups.g_instance.setSwitch(SOUNDS.SOUND_DRONE_SWITCH_GROUP, SOUNDS.SOUND_DRONE_01)


class ArmorySoundManager(object):
    __slots__ = ('__isFirstEntrance', '__isEnabled')

    def __init__(self):
        self.__isFirstEntrance = True
        self.__isEnabled = False

    def clear(self):
        self.__isFirstEntrance = True
        self.__isEnabled = False

    def onSoundModeChanged(self, isArmorySoundMode):
        if isArmorySoundMode == self.__isEnabled:
            return
        if isArmorySoundMode:
            if self.__isFirstEntrance:
                self.__isFirstEntrance = False
                SoundGroups.g_instance.playSound2D(SOUNDS.FIRST_ENTER)
            else:
                SoundGroups.g_instance.playSound2D(SOUNDS.ENTER)
        else:
            SoundGroups.g_instance.playSound2D(SOUNDS.EXIT)
        self.__isEnabled = isArmorySoundMode
