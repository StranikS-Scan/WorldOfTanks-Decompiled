# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/notification/__init__.py
from fun_random.notification.actions_handlers import SelectFunRandomMode
from fun_random.notification.listeners import FunRandomEventsListener
from gui.shared.system_factory import registerNotificationsListeners, registerNotificationsActionsHandlers

def registerFunRandomNotifications():
    registerNotificationsListeners((FunRandomEventsListener,))
    registerNotificationsActionsHandlers((SelectFunRandomMode,))
