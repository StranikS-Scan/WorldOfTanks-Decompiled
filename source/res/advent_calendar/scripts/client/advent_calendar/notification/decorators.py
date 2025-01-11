# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: advent_calendar/scripts/client/advent_calendar/notification/decorators.py
from gui.shared.notifications import NotificationGroup, NotificationGuiSettings, NotificationPriorityLevel
from messenger import g_settings
from notification.decorators import MessageDecorator
from notification.settings import NOTIFICATION_TYPE

class AdventCalendarDoorsAvailableDecorator(MessageDecorator):

    def __init__(self, entityID, model=None, linkageData=None, template=None, priority=NotificationPriorityLevel.LOW):
        super(AdventCalendarDoorsAvailableDecorator, self).__init__(entityID, self.__makeEntity(linkageData, template), self.__makeSettings(priority), model)

    def getGroup(self):
        return NotificationGroup.OFFER

    def getType(self):
        return NOTIFICATION_TYPE.ADVENT_CALENDAR_DOORS_AVAILABLE

    @staticmethod
    def __makeEntity(linkageData, template):
        return g_settings.msgTemplates.format(template, data={'linkageData': linkageData})

    @staticmethod
    def __makeSettings(priority):
        return NotificationGuiSettings(isNotify=True, priorityLevel=priority)
