# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/comp7/comp7_lobby_sounds.py
from enum import Enum
import SoundGroups
from gui.impl.gen.view_models.views.lobby.comp7.meta_view.root_view_model import MetaRootViews
from sound_gui_manager import CommonSoundSpaceSettings

class LobbySounds(Enum):
    LEAVE_MODE = 'comp_7_hangar_drone_stop'


class MetaViewSounds(Enum):
    ENTER_EVENT = 'comp_7_progression_enter'
    EXIT_EVENT = 'comp_7_progression_exit'
    ENTER_TAB_EVENTS = {MetaRootViews.RANKREWARDS: 'comp_7_rank_rewards_enter',
     MetaRootViews.YEARLYSTATISTICS: 'comp_7_season_statistics_screen_appear',
     MetaRootViews.SHOP: 'comp_7_shop_enter'}
    EXIT_TAB_EVENTS = {MetaRootViews.SHOP: 'comp_7_progression_enter'}


class FlybySounds(Enum):
    START = 'comp_7_shop_purchase_anim_start'
    STOP = 'comp_7_shop_purchase_anim_stop'


def getComp7MetaSoundSpace():
    return CommonSoundSpaceSettings(name='comp7_meta_view', entranceStates={}, exitStates={}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True, enterEvent=MetaViewSounds.ENTER_EVENT.value, exitEvent=MetaViewSounds.EXIT_EVENT.value)


def playComp7MetaViewTabSound(tabId, prevTabId=None):
    sounds = (MetaViewSounds.EXIT_TAB_EVENTS.value.get(prevTabId), MetaViewSounds.ENTER_TAB_EVENTS.value.get(tabId))
    for soundName in sounds:
        if soundName is not None:
            SoundGroups.g_instance.playSound2D(soundName)

    return


def playSound(eventName):
    SoundGroups.g_instance.playSound2D(eventName)
