# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/lootbox_system/base/sound.py
import logging
from enum import Enum
import typing
from typing import TYPE_CHECKING
import SoundGroups
import WWISE
from gui.impl import backport
from gui.impl.gen import R
if TYPE_CHECKING:
    from typing import Tuple
_logger = logging.getLogger(__name__)

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


def enterLootBoxesSoundState(eventName):
    WWISE.WW_setState(_LootBoxesSounds.STATE_GROUP, _LootBoxesSounds.STATE_LOOTBOXES)
    _playAmbientOn(eventName)


def exitLootBoxesSoundState(eventName):
    _playAmbientOff(eventName)
    WWISE.WW_setState(_LootBoxesSounds.STATE_GROUP, _LootBoxesSounds.STATE_GARAGE)


def enterLootBoxesMultipleRewardState():
    WWISE.WW_setState(_LootBoxesSounds.STATE_OVERLAY_GROUP, _LootBoxesSounds.STATE_REWARDS_ENTER)


def exitLootBoxesMultipleRewardState():
    WWISE.WW_setState(_LootBoxesSounds.STATE_OVERLAY_GROUP, _LootBoxesSounds.STATE_REWARDS_EXIT)


def playInfopageEnterSound(eventName):
    _playSounds((_LootBoxesSounds.INFOPAGE_ENTER,), eventName)


def playInfopageExitSound(eventName):
    _playSounds((_LootBoxesSounds.INFOPAGE_EXIT,), eventName)


def playVideoPauseSound(eventName):
    _playSounds((_LootBoxesSounds.VIDEO_PAUSE,), eventName)


def playVideoResumeSound(eventName):
    _playSounds((_LootBoxesSounds.VIDEO_RESUME,), eventName)


def _playAmbientOn(eventName):
    _playSounds((_LootBoxesSounds.AMBIENT_ON,), eventName)


def _playAmbientOff(eventName):
    _playSounds((_LootBoxesSounds.AMBIENT_OFF,), eventName)


def _playSounds(soundNames, eventName):
    for soundName in soundNames:
        SoundGroups.g_instance.playSafeSound2D(_getSound(soundName, eventName))


def _getSound(soundName, eventName):
    eventSoundName = '_'.join((soundName, eventName))
    soundRes = R.sounds.dyn(eventSoundName)
    if not soundRes.exists():
        _logger.debug('Event sound: "%s" not found, try to use default: "%s"', eventSoundName, soundName.value)
        soundRes = R.sounds.dyn(soundName)
        if not soundRes.exists():
            _logger.error('Event sound: "%s" not found', soundName.value)
            return None
    return backport.sound(soundRes())
