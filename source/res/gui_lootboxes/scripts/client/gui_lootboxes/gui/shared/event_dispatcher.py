# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: gui_lootboxes/scripts/client/gui_lootboxes/gui/shared/event_dispatcher.py
import logging
from gui import SystemMessages
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.notifications import NotificationPriorityLevel
from helpers import dependency
from shared_utils import findFirst
from skeletons.gui.shared import IItemsCache
_logger = logging.getLogger(__name__)

def showLootBoxesWelcomeScreen(parent=None):
    from gui_lootboxes.gui.impl.lobby.gui_lootboxes.welcome_screen import LootBoxesWelcomeScreenWindow
    window = LootBoxesWelcomeScreenWindow(parent=parent)
    window.load()


def showLootBoxOpenErrorWindow(parent=None):
    from gui_lootboxes.gui.impl.lobby.gui_lootboxes.open_box_error import LootBoxesOpenBoxErrorWindow
    window = LootBoxesOpenBoxErrorWindow(parent)
    window.load()
    SystemMessages.pushMessage(text=backport.text(R.strings.system_messages.lootboxes.open.server_error.DISABLED()), priority=NotificationPriorityLevel.MEDIUM, type=SystemMessages.SM_TYPE.Error)


def showStorageView(returnPlace=None, initialLootBoxId=0):
    from gui_lootboxes.gui.impl.lobby.gui_lootboxes.lootboxes_storage import LootBoxesStorageWindow
    from gui_lootboxes.gui.storage_context.context import ReturnPlaces
    if returnPlace is None:
        returnPlace = ReturnPlaces.TO_HANGAR
    window = LootBoxesStorageWindow(returnPlace, initialLootBoxId)
    window.load()
    return


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def showSpecificBoxInStorageView(category=None, lootBoxType=None, returnPlace=None, itemsCache=None):
    from gui_lootboxes.gui.impl.lobby.gui_lootboxes.lootboxes_storage import LootBoxesStorageWindow
    from gui_lootboxes.gui.storage_context.context import ReturnPlaces

    def boxPredicate(lootBox):
        if lootBox.getInventoryCount() == 0:
            return False
        isEqualCategory = lootBox.getCategory() == category if category else True
        isEqualType = lootBox.getType() == lootBoxType if lootBoxType else True
        return isEqualCategory and isEqualType

    boxId = 0
    box = findFirst(boxPredicate, itemsCache.items.tokens.getLootBoxes().itervalues())
    if box:
        boxId = box.getID()
    if returnPlace is None:
        returnPlace = ReturnPlaces.TO_HANGAR
    window = LootBoxesStorageWindow(returnPlace, boxId)
    window.load()
    return


def showBonusProbabilitiesWindow(lootBox, parent=None):
    from gui_lootboxes.gui.impl.lobby.gui_lootboxes.bonus_probabilities_view import BonusProbabilitiesWindow
    window = BonusProbabilitiesWindow(lootBox, parent=parent)
    window.load()


def showRewardScreenWindow(rewards, lootBox=None, parent=None):
    from gui_lootboxes.gui.impl.lobby.gui_lootboxes.reward_screen import LootBoxesRewardScreenWindow
    window = LootBoxesRewardScreenWindow(rewards=rewards, lootBox=lootBox, parent=parent)
    window.load()
