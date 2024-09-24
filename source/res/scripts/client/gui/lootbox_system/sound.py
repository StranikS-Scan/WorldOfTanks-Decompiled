# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/lootbox_system/sound.py
from enum import Enum
import WWISE
from helpers import dependency
from skeletons.gui.app_loader import IAppLoader

class _LootBoxesSounds(str, Enum):
    STATE_GROUP = 'STATE_hangar_place'
    STATE_LOOTBOXES = 'STATE_hangar_place_lootboxes'
    STATE_GARAGE = 'STATE_hangar_place_garage'
    STATE_OVERLAY_GROUP = 'STATE_overlay_hangar_general'
    STATE_REWARDS_ENTER = 'STATE_overlay_hangar_general_on'
    STATE_REWARDS_EXIT = 'STATE_overlay_hangar_general_off'
    AMBIENT_ON = 'gui_lb_amb_on'
    AMBIENT_OFF = 'gui_lb_amb_off'
    VIDEO_PAUSE = 'gui_lb_video_pause'
    VIDEO_RESUME = 'gui_lb_video_resume'
    INFOPAGE_ENTER = 'gui_lb_infopage_enter'
    INFOPAGE_EXIT = 'gui_lb_infopage_exit'


def enterLootBoxesSoundState():
    WWISE.WW_setState(_LootBoxesSounds.STATE_GROUP, _LootBoxesSounds.STATE_LOOTBOXES)
    _playAmbientOn()


def exitLootBoxesSoundState():
    _playAmbientOff()
    WWISE.WW_setState(_LootBoxesSounds.STATE_GROUP, _LootBoxesSounds.STATE_GARAGE)


def enterLootBoxesMultipleRewardState():
    WWISE.WW_setState(_LootBoxesSounds.STATE_OVERLAY_GROUP, _LootBoxesSounds.STATE_REWARDS_ENTER)


def exitLootBoxesMultipleRewardState():
    WWISE.WW_setState(_LootBoxesSounds.STATE_OVERLAY_GROUP, _LootBoxesSounds.STATE_REWARDS_EXIT)


def playInfopageEnterSound():
    _playSound((_LootBoxesSounds.INFOPAGE_ENTER,))


def playInfopageExitSound():
    _playSound((_LootBoxesSounds.INFOPAGE_EXIT,))


def playVideoPauseSound():
    _playSound((_LootBoxesSounds.VIDEO_PAUSE,))


def playVideoResumeSound():
    _playSound((_LootBoxesSounds.VIDEO_RESUME,))


def _playAmbientOn():
    _playSound((_LootBoxesSounds.AMBIENT_ON,))


def _playAmbientOff():
    _playSound((_LootBoxesSounds.AMBIENT_OFF,))


@dependency.replace_none_kwargs(appLoader=IAppLoader)
def _playSound(names, appLoader=None):
    app = appLoader.getApp()
    if app and app.soundManager:
        for name in names:
            app.soundManager.playEffectSound(name)
