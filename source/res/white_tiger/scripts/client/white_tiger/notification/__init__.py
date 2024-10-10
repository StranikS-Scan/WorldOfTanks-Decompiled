# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/notification/__init__.py
from white_tiger.notification.actions_handlers import ShowWTBattleResultsHandler, OpenWTEventPortalsHandler, OpenWTEventCollectionHandler, OpenWTEventHandler, OpenWTEventQuestsHandler, OpenWTEventTicketPurchasingHandler
from gui.shared.system_factory import registerNotificationsActionsHandlers

def registerClientNotificationHandlers():
    registerNotificationsActionsHandlers((ShowWTBattleResultsHandler,
     OpenWTEventPortalsHandler,
     OpenWTEventCollectionHandler,
     OpenWTEventHandler,
     OpenWTEventQuestsHandler,
     OpenWTEventTicketPurchasingHandler))
