# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: advent_calendar/scripts/client/advent_calendar/notification/decorators.py
from __future__ import absolute_import
from advent_calendar.gui.feature.constants import ADVENT_CALENDAR_DOORS_AVAILABLE_NOTIFICATION_NAME
from gui.shared.notifications import NotificationGroup, NotificationGuiSettings
from messenger import g_settings
from notification.decorators import MessageDecorator
from notification.settings import NOTIFICATION_TYPE

class AdventCalendarDoorsAvailableDecorator(MessageDecorator):

    def __init__(self, entityID, model, notificationData):
        super(AdventCalendarDoorsAvailableDecorator, self).__init__(entityID, self.__makeEntity(**notificationData.savedData), self.__makeSettings(notificationData.priorityLevel), model)

    def getGroup(self):
        return NotificationGroup.OFFER

    def getType(self):
        return NOTIFICATION_TYPE.ADVENT_CALENDAR_DOORS_AVAILABLE

    @staticmethod
    def __makeEntity(linkageData):
        return g_settings.msgTemplates.format(ADVENT_CALENDAR_DOORS_AVAILABLE_NOTIFICATION_NAME, data={'linkageData': linkageData})

    @staticmethod
    def __makeSettings(priority):
        return NotificationGuiSettings(isNotify=True, priorityLevel=priority)
