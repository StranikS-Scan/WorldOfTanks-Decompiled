# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: gui_lootboxes/scripts/client/gui_lootboxes/notification/__init__.py
from gui.shared.system_factory import registerNotificationsListeners, registerNotificationsActionsHandlers
from gui_lootboxes.notification.lootbox_action_handler import _OpenEventLootBoxesShopHandler
from gui_lootboxes.notification.lootbox_listener import EventLootBoxesListener, LootBoxesBuyAvailableListener, LootBoxesStatisticSwitcher

def registerClientNotificationListener():
    registerNotificationsListeners((EventLootBoxesListener, LootBoxesBuyAvailableListener, LootBoxesStatisticSwitcher))


def registerClientNotificationHandler():
    registerNotificationsActionsHandlers((_OpenEventLootBoxesShopHandler,))
