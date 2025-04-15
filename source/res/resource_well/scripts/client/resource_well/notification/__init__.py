# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: resource_well/scripts/client/resource_well/notification/__init__.py
from gui.shared.system_factory import registerNotificationsActionsHandlers, registerNotificationsListeners
from resource_well.notification.actions_handlers import OpenResourceWellProgressionStartWindow, OpenResourceWellProgressionWindow
from resource_well.notification.listeners import ResourceWellListener

def registerResourceWellNotifications():
    registerNotificationsListeners((ResourceWellListener,))
    registerNotificationsActionsHandlers((OpenResourceWellProgressionStartWindow, OpenResourceWellProgressionWindow))
