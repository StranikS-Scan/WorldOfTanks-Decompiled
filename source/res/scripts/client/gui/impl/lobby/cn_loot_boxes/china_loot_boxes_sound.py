# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/cn_loot_boxes/china_loot_boxes_sound.py
from enum import Enum
from helpers import dependency
from skeletons.gui.app_loader import IAppLoader
import WWISE

class _CNLootBoxesSounds(Enum):
    LOOT_BOX_ENTER = 'ev_cn_hangar_lootbox_enter'
    LOOT_BOX_EXIT = 'ev_cn_hangar_lootbox_exit'
    LOOT_BOX_HIGHLIGHT = 'ev_cn_hangar_lootbox_highlight'
    STATE_GROUP = 'STATE_hangar_place'
    STATE_LOOTBOXES = 'STATE_hangar_place_lootboxes'
    STATE_GARAGE = 'STATE_hangar_place_garage'


def enterLootBoxState():
    WWISE.WW_setState(_CNLootBoxesSounds.STATE_GROUP.value, _CNLootBoxesSounds.STATE_LOOTBOXES.value)


def exitLootBoxState():
    WWISE.WW_setState(_CNLootBoxesSounds.STATE_GROUP.value, _CNLootBoxesSounds.STATE_GARAGE.value)


def playStorageOpened(hasBoxes=False):
    names = [_CNLootBoxesSounds.LOOT_BOX_ENTER.value]
    if hasBoxes:
        names.append(_CNLootBoxesSounds.LOOT_BOX_HIGHLIGHT.value)
    _playSound(names)


def playStorageClosed():
    _playSound((_CNLootBoxesSounds.LOOT_BOX_EXIT.value,))


@dependency.replace_none_kwargs(appLoader=IAppLoader)
def _playSound(names, appLoader=None):
    app = appLoader.getApp()
    if app and app.soundManager:
        for name in names:
            app.soundManager.playEffectSound(name)
