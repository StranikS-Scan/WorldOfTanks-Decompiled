# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_light_progression/scripts/client/comp7_light_progression/notification/__init__.py
from comp7_light_progression.notification.actions_handlers import ShowComp7LightProgressionActionHandler
from gui.shared.system_factory import registerNotificationsActionsHandlers

def registerClientNotificationHandlers():
    registerNotificationsActionsHandlers((ShowComp7LightProgressionActionHandler,))
