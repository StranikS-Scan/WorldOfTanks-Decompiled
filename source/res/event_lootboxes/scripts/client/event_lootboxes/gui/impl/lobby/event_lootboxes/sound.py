# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: event_lootboxes/scripts/client/event_lootboxes/gui/impl/lobby/event_lootboxes/sound.py
from enum import Enum
from helpers import dependency
from skeletons.gui.app_loader import IAppLoader
import WWISE

class _EventLootBoxesSounds(Enum):
    LOOT_BOX_ENTER = 'ev_hangar_lootbox_enter'
    LOOT_BOX_EXIT = 'ev_hangar_lootbox_exit'
    LOOT_BOX_HIGHLIGHT = 'ev_hangar_lootbox_highlight'
    STATE_GROUP = 'STATE_hangar_place'
    STATE_LOOTBOXES = 'STATE_hangar_place_lootboxes'
    STATE_GARAGE = 'STATE_hangar_place_garage'


def enterLootBoxSoundState():
    WWISE.WW_setState(_EventLootBoxesSounds.STATE_GROUP.value, _EventLootBoxesSounds.STATE_LOOTBOXES.value)


def exitLootBoxSoundState():
    WWISE.WW_setState(_EventLootBoxesSounds.STATE_GROUP.value, _EventLootBoxesSounds.STATE_GARAGE.value)


def playStorageOpened(hasBoxes=False):
    names = [_EventLootBoxesSounds.LOOT_BOX_ENTER.value]
    if hasBoxes:
        names.append(_EventLootBoxesSounds.LOOT_BOX_HIGHLIGHT.value)
    _playSound(names)


def playStorageClosed():
    _playSound((_EventLootBoxesSounds.LOOT_BOX_EXIT.value,))


@dependency.replace_none_kwargs(appLoader=IAppLoader)
def _playSound(names, appLoader=None):
    app = appLoader.getApp()
    if app and app.soundManager:
        for name in names:
            app.soundManager.playEffectSound(name)
