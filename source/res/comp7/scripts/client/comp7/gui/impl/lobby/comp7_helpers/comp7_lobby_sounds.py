# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/lobby/comp7_helpers/comp7_lobby_sounds.py
from enum import Enum
import SoundGroups
from shared_utils import CONST_CONTAINER
from comp7.gui.impl.gen.view_models.views.lobby.enums import MetaRootViews
from sound_gui_manager import CommonSoundSpaceSettings

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


class VehicleVideoSounds(CONST_CONTAINER):
    START = 'comp_7_video_reward_style_start'
    PAUSE = 'comp_7_video_reward_style_pause'
    RESUME = 'comp_7_video_reward_style_resume'
    END = 'comp_7_video_reward_style_stop'


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
