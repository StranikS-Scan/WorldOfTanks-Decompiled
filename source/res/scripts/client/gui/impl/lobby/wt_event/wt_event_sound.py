# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/wt_event/wt_event_sound.py
import SoundGroups
import WWISE
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.gui_items.loot_box import EventLootBoxes

class WTEventSounds(object):

    class LootBoxSwitch(object):
        NAME = 'SWITCH_ext_WT_lootbox'
        HUNTER = 'SWITCH_ext_WT_lootbox_hunter'
        BOSS = 'SWITCH_ext_WT_lootbox_wt'
        SPECIAL = 'SWITCH_ext_WT_lootbox_special'


def playLootBoxEnter():
    SoundGroups.g_instance.playSound2D(backport.sound(R.sounds.ev_white_tiger_hangar_lootbox_enter()))


def playLootBoxExit():
    SoundGroups.g_instance.playSound2D(backport.sound(R.sounds.ev_white_tiger_hangar_lootbox_exit()))


def playLootBoxStorageEnter():
    SoundGroups.g_instance.playSound2D(backport.sound(R.sounds.ev_white_tiger_hangar_lootbox_storage()))


def playLootBoxSelect():
    SoundGroups.g_instance.playSound2D(backport.sound(R.sounds.ev_white_tiger_hangar_lootbox_select()))


def playOpenLootBox(rewardsCount):
    if rewardsCount > 1:
        soundEventR = R.sounds.ev_white_tiger_hangar_lootbox_open_double()
    else:
        soundEventR = R.sounds.ev_white_tiger_hangar_lootbox_open_solo()
    SoundGroups.g_instance.playSound2D(backport.sound(soundEventR))


def playReRollLootBox(rewardsCount):
    if rewardsCount > 1:
        soundEventR = R.sounds.ev_white_tiger_hangar_lootbox_reroll_double()
    else:
        soundEventR = R.sounds.ev_white_tiger_hangar_lootbox_reroll_solo()
    SoundGroups.g_instance.playSound2D(backport.sound(soundEventR))


def playCollectionAward(isFinalReward):
    if isFinalReward:
        SoundGroups.g_instance.playSound2D(backport.sound(R.sounds.ev_white_tiger_hangar_lootbox_collection_all()))
    else:
        SoundGroups.g_instance.playSound2D(backport.sound(R.sounds.ev_white_tiger_hangar_lootbox_collections()))


def playLootBoxCrashEnter():
    SoundGroups.g_instance.playSound2D(backport.sound(R.sounds.ev_white_tiger_hangar_lootbox_crash_enter()))


def playLootBoxCrashExit():
    SoundGroups.g_instance.playSound2D(backport.sound(R.sounds.ev_white_tiger_hangar_lootbox_crash_exit()))


def playCollectionViewEnter():
    SoundGroups.g_instance.playSound2D(backport.sound(R.sounds.ev_white_tiger_hangar_collections_enter()))


def playCollectionViewExit():
    SoundGroups.g_instance.playSound2D(backport.sound(R.sounds.ev_white_tiger_hangar_collections_exit()))


def playLootBoxRewardTape():
    SoundGroups.g_instance.playSound2D(backport.sound(R.sounds.ev_white_tiger_hangar_lootbox_reward_tape_appears()))


def playLootBoxRewardExit():
    SoundGroups.g_instance.playSound2D('ev_white_tiger_hangar_lootbox_reward_exit')


def setLootBoxState(boxType):
    if boxType == EventLootBoxes.WT_SPECIAL:
        WWISE.WW_setSwitch(WTEventSounds.LootBoxSwitch.NAME, WTEventSounds.LootBoxSwitch.SPECIAL)
    elif boxType == EventLootBoxes.WT_HUNTER:
        WWISE.WW_setSwitch(WTEventSounds.LootBoxSwitch.NAME, WTEventSounds.LootBoxSwitch.HUNTER)
    elif boxType == EventLootBoxes.WT_BOSS:
        WWISE.WW_setSwitch(WTEventSounds.LootBoxSwitch.NAME, WTEventSounds.LootBoxSwitch.BOSS)


def playHangarCameraFly(forward=True):
    if forward:
        SoundGroups.g_instance.playSound2D(backport.sound(R.sounds.ev_white_tiger_hangar_camera_fly_forward()))
    else:
        SoundGroups.g_instance.playSound2D(backport.sound(R.sounds.ev_white_tiger_hangar_camera_fly_backward()))


def playProgressBarGrowing(isGrowing):
    if isGrowing:
        SoundGroups.g_instance.playSound2D(backport.sound(R.sounds.ev_white_tiger_hangar_ui_progress_bar_start()))
    else:
        SoundGroups.g_instance.playSound2D(backport.sound(R.sounds.ev_white_tiger_hangar_ui_progress_bar_stop()))


class WTEventHangarEnterSound(object):

    def __init__(self):
        self.__isSelected = False

    def clear(self):
        self.__isSelected = False

    def update(self, isSelected):
        if isSelected != self.__isSelected:
            self.__isSelected = isSelected
            self.__playSound()

    def __playSound(self):
        if self.__isSelected:
            SoundGroups.g_instance.playSound2D(backport.sound(R.sounds.ev_white_tiger_hangar_enter()))
        else:
            SoundGroups.g_instance.playSound2D(backport.sound(R.sounds.ev_white_tiger_hangar_exit()))
