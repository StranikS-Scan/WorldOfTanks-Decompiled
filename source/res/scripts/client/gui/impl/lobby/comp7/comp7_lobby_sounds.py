# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/comp7/comp7_lobby_sounds.py
from enum import Enum
import SoundGroups
from gui.impl.gen.view_models.views.lobby.comp7.meta_view.root_view_model import MetaRootViews
from sound_gui_manager import CommonSoundSpaceSettings

class MetaViewSounds(Enum):
    ENTER_EVENT = 'comp_7_progression_enter'
    EXIT_EVENT = 'comp_7_progression_exit'
    ENTER_TAB_EVENTS = {MetaRootViews.RANKREWARDS: 'comp_7_rank_rewards_enter'}


def getComp7MetaSoundSpace():
    return CommonSoundSpaceSettings(name='comp7_meta_view', entranceStates={}, exitStates={}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True, enterEvent=MetaViewSounds.ENTER_EVENT.value, exitEvent=MetaViewSounds.EXIT_EVENT.value)


def playComp7MetaViewTabSound(tabId):
    soundName = MetaViewSounds.ENTER_TAB_EVENTS.value.get(tabId)
    if soundName is not None:
        SoundGroups.g_instance.playSound2D(soundName)
    return
