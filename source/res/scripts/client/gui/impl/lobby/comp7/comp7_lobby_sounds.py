# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/comp7/comp7_lobby_sounds.py
from enum import Enum
from sound_gui_manager import CommonSoundSpaceSettings

class MetaViewSounds(Enum):
    ENTER_EVENT = 'comp_7_progression_enter'
    EXIT_EVENT = 'comp_7_progression_exit'
    REWARD_PROGRESSBAR_START = 'comp_7_progressbar_start'
    REWARD_PROGRESSBAR_STOP = 'comp_7_progressbar_stop'


def getComp7MetaSoundSpace():
    return CommonSoundSpaceSettings(name='comp7_meta_view', entranceStates={}, exitStates={}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True, enterEvent=MetaViewSounds.ENTER_EVENT.value, exitEvent=MetaViewSounds.EXIT_EVENT.value)
