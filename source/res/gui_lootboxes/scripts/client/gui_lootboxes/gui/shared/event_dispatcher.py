# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: gui_lootboxes/scripts/client/gui_lootboxes/gui/shared/event_dispatcher.py
import logging
from gui import SystemMessages
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.notifications import NotificationPriorityLevel
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


def showStorageView():
    from gui_lootboxes.gui.impl.lobby.gui_lootboxes.lootboxes_storage import LootBoxesStorageWindow
    window = LootBoxesStorageWindow()
    window.load()


def showBonusProbabilitiesWindow(lootBox, parent=None):
    from gui_lootboxes.gui.impl.lobby.gui_lootboxes.bonus_probabilities_view import BonusProbabilitiesWindow
    window = BonusProbabilitiesWindow(lootBox, parent=parent)
    window.load()


def showRewardScreenWindow(rewards, lootBox=None, parent=None):
    from gui_lootboxes.gui.impl.lobby.gui_lootboxes.reward_screen import LootBoxesRewardScreenWindow
    window = LootBoxesRewardScreenWindow(rewards=rewards, lootBox=lootBox, parent=parent)
    window.load()
