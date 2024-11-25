# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: advent_calendar/scripts/client/advent_calendar/notification/listeners.py
from account_helpers.AccountSettings import AdventCalendar
from advent_calendar.gui.feature.constants import MIN_AVAILABLE_DOORS_REQUIRED_FOR_NOTIFICATION
from advent_calendar.gui.impl.gen.view_models.views.lobby.door_view_model import DoorState
from advent_calendar.gui.impl.lobby.feature.advent_helper import getDoorState, getAdventCalendarSetting, setAdventCalendarSetting
from advent_calendar.notification.decorators import AdventCalendarDoorsAvailableDecorator
from advent_calendar.skeletons import IAdventCalendarController
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.notifications import NotificationPriorityLevel
from helpers import dependency
from notification.listeners import BaseReminderListener
from notification.settings import NOTIFICATION_TYPE

class AdventCalendarDoorsAvailableListener(BaseReminderListener):
    __adventController = dependency.descriptor(IAdventCalendarController)
    MSG_ID = 0

    def __init__(self):
        super(AdventCalendarDoorsAvailableListener, self).__init__(NOTIFICATION_TYPE.ADVENT_CALENDAR_DOORS_AVAILABLE, self.MSG_ID)
        self.__popUpNotificationCallbackID = None
        return

    def start(self, model):
        result = super(AdventCalendarDoorsAvailableListener, self).start(model)
        self.__tryNotify()
        self.__adventController.onDoorOpened += self.__tryNotify
        self.__adventController.onConfigChanged += self.__tryNotify
        return result

    def stop(self):
        super(AdventCalendarDoorsAvailableListener, self).stop()
        self.__adventController.onConfigChanged -= self.__tryNotify
        self.__adventController.onDoorOpened -= self.__tryNotify

    def _createNotificationData(self, **kwargs):
        return kwargs.get('ctx', {})

    def _createDecorator(self, notificationData):
        return AdventCalendarDoorsAvailableDecorator(self._getNotificationId(), self._model(), **notificationData)

    def __tryNotify(self):
        if not self.__adventController.isAvailableAndActivePhase():
            return self._notifyOrRemove(False)
        currentDay = self.__adventController.getCurrentDayNumber()
        availableDoorsAmount = len([ dayID for dayID in range(max(currentDay - 1, 1), currentDay + 1) if getDoorState(dayID) == DoorState.READY_TO_OPEN ])
        if not availableDoorsAmount:
            self._notifyOrRemove(False)
            return
        canShowPopUp = self.__canShowPopUp(currentDay)
        linkageData = {}
        if not getAdventCalendarSetting(AdventCalendar.FIRST_ENTRY_NOTIFICATION_SHOWN):
            linkageData['description'] = backport.text(R.strings.messenger.serviceChannelMessages.adventCalendar.reward.description())
            canShowPopUp = True
            setAdventCalendarSetting(AdventCalendar.FIRST_ENTRY_NOTIFICATION_SHOWN, True)
        elif availableDoorsAmount < MIN_AVAILABLE_DOORS_REQUIRED_FOR_NOTIFICATION:
            canShowPopUp = False
        priority = NotificationPriorityLevel.LOW
        if canShowPopUp:
            priority = NotificationPriorityLevel.HIGH
            setAdventCalendarSetting(AdventCalendar.LAST_DAY_POPUP_SEEN, currentDay)
        self._notifyOrRemove(True, isStateChanged=canShowPopUp, ctx={'priority': priority,
         'linkageData': linkageData})

    @staticmethod
    def __canShowPopUp(currentDay):
        return getAdventCalendarSetting(AdventCalendar.LAST_DAY_POPUP_SEEN) < currentDay
