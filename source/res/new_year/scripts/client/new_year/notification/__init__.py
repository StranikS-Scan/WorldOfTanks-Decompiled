# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/notification/__init__.py
from new_year.notification.actions_handlers import registerNewYearActionHandlers
from new_year.notification.listeners import registerNewYearNotificationListeners

def registerNewYearNotifications():
    registerNewYearNotificationListeners()
    registerNewYearActionHandlers()
