# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/sounds/sound_helpers.py
import SoundGroups
import WWISE
from debug_utils import LOG_ERROR
from gui.battle_control import avatar_getter

def playVoiceover(eventName):
    soundNotifications = avatar_getter.getSoundNotifications()
    if soundNotifications:
        soundNotifications.play(eventName)
    else:
        LOG_ERROR('[PortalBattle]: could not play voiceover event {}'.format(eventName))


def play2DSound(name):
    SoundGroups.g_instance.playSound2D(name)


def play3DSound(name, point):
    SoundGroups.g_instance.playSoundPos(name, point)


def setCutSceneSoundGlobalEvent(state):
    WWISE.WW_eventGlobal(state)
