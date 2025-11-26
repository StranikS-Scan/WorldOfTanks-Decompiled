# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: advent_calendar/scripts/client/advent_calendar/notification/__init__.py
from __future__ import absolute_import
from advent_calendar.gui.feature.constants import ADVENT_CALENDAR_DOORS_AVAILABLE_NOTIFICATION_NAME
from advent_calendar.gui.impl.lobby.feature.notifications.available_doors_view import AvailableDoorsView
from advent_calendar.notification.listeners import AdventCalendarDoorsAvailableListener
from gui.impl.gen import R
from gui.shared.system_factory import registerNotificationsListeners, registerGamefaceNotifications

def registerAdventNotifications():
    registerNotificationsListeners((AdventCalendarDoorsAvailableListener,))
    registerGamefaceNotifications({ADVENT_CALENDAR_DOORS_AVAILABLE_NOTIFICATION_NAME: (R.views.advent_calendar.mono.lobby.notification_view(), AvailableDoorsView)})
