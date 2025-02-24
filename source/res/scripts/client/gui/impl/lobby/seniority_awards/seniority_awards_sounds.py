# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/seniority_awards/seniority_awards_sounds.py
import WWISE
from sound_gui_manager import CommonSoundSpaceSettings
from gui.sounds.filters import StatesGroup, States
SENIORITY_REWARD_SOUND_SPACE = CommonSoundSpaceSettings(name='seniority_award', entranceStates={StatesGroup.OVERLAY_HANGAR_GENERAL: States.OVERLAY_HANGAR_GENERAL_ON}, exitStates={StatesGroup.OVERLAY_HANGAR_GENERAL: States.OVERLAY_HANGAR_GENERAL_OFF}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True, enterEvent='', exitEvent='')

def playSound(eventName):
    if eventName:
        WWISE.WW_eventGlobal(eventName)
