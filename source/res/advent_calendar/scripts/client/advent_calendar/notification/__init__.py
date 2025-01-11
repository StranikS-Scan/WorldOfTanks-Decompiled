# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: advent_calendar/scripts/client/advent_calendar/notification/__init__.py
from advent_calendar.gui.impl.lobby.feature.notifications.doors_available_view import DoorsAvailableView
from advent_calendar.notification.actions_handlers import AdventCalendarActionHandler
from advent_calendar.notification.listeners import AdventCalendarDoorsAvailableListener
from gui.shared.system_factory import registerNotificationsListeners, registerGamefaceNotifications
from gui.impl.gen import R

def registerAdventNotifications():
    notificationModelWithView = (R.views.advent_calendar.lobby.feature.DoorsAvailableView(), DoorsAvailableView)
    registerNotificationsListeners((AdventCalendarDoorsAvailableListener,))
    registerGamefaceNotifications({'AdventCalendarDoorsAvailableFirstEntry': notificationModelWithView,
     'AdventCalendarDoorsAvailable': notificationModelWithView,
     'AdventCalendarDoorsAvailablePostEvent': notificationModelWithView})
