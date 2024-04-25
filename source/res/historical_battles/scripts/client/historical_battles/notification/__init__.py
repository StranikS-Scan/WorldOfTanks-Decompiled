# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/notification/__init__.py
from historical_battles.notification.actions_handlers import ShowHBFairPlayActionHandler, ShowHBWarningFairPlayActionHandler, ShowHBProgressionActionHandler, ShowHBEventStartHandler, ShowHBBattleResultsHandler
from gui.shared.system_factory import registerNotificationsActionsHandlers

def registerClientNotificationHandlers():
    registerNotificationsActionsHandlers((ShowHBFairPlayActionHandler,
     ShowHBWarningFairPlayActionHandler,
     ShowHBProgressionActionHandler,
     ShowHBEventStartHandler,
     ShowHBBattleResultsHandler))
