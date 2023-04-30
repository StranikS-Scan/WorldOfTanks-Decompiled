# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale_progression/scripts/client/battle_royale_progression/notification/__init__.py
from battle_royale_progression.notification.actions_handlers import ShowBRProgressionActionHandler
from gui.shared.system_factory import registerNotificationsActionsHandlers

def registerClientNotificationHandlers():
    registerNotificationsActionsHandlers((ShowBRProgressionActionHandler,))
