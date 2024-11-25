# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: advent_calendar/scripts/client/advent_calendar/notification/__init__.py
from advent_calendar.notification.actions_handlers import AdventCalendarActionHandler
from advent_calendar.notification.listeners import AdventCalendarDoorsAvailableListener
from gui.shared.system_factory import registerNotificationsListeners, registerNotificationsActionsHandlers

def registerAdventNotifications():
    registerNotificationsListeners((AdventCalendarDoorsAvailableListener,))
    registerNotificationsActionsHandlers((AdventCalendarActionHandler,))
