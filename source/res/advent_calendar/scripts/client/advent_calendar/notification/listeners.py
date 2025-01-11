# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: advent_calendar/scripts/client/advent_calendar/notification/listeners.py
import BigWorld
from account_helpers.AccountSettings import AdventCalendar
from advent_calendar.gui.feature.constants import MIN_AVAILABLE_DOORS_REQUIRED_FOR_NOTIFICATION
from advent_calendar.gui.impl.gen.view_models.views.lobby.door_view_model import DoorState
from advent_calendar.gui.impl.gen.view_models.views.lobby.notifications.doors_available_view_model import DoorsAvailableNotificationState
from advent_calendar.gui.impl.lobby.feature.advent_helper import getDoorState, getAdventCalendarSetting
from advent_calendar.notification.decorators import AdventCalendarDoorsAvailableDecorator
from advent_calendar.skeletons import IAdventCalendarController
from gui.shared import g_eventBus, EVENT_BUS_SCOPE, events
from gui.shared.notifications import NotificationPriorityLevel
from helpers import dependency, time_utils
from notification.listeners import BaseReminderListener
from notification.settings import NOTIFICATION_TYPE
from shared_utils import CONST_CONTAINER
from skeletons.gui.shared import IItemsCache
from skeletons.new_year import INewYearController

class GFNotificationTemplates(CONST_CONTAINER):
    ADVENT_CALENDAR_DOORS_AVAILABLE_FIRST_ENTRY = 'AdventCalendarDoorsAvailableFirstEntry'
    ADVENT_CALENDAR_DOORS_AVAILABLE = 'AdventCalendarDoorsAvailable'
    ADVENT_CALENDAR_DOORS_AVAILABLE_POST_EVENT = 'AdventCalendarDoorsAvailablePostEvent'


class AdventCalendarDoorsAvailableListener(BaseReminderListener):
    __adventController = dependency.descriptor(IAdventCalendarController)
    __itemsCache = dependency.descriptor(IItemsCache)
    __nyController = dependency.descriptor(INewYearController)
    MSG_ID = 0
    POPUP_NOTIFICATION_DELAY = 90

    def __init__(self):
        super(AdventCalendarDoorsAvailableListener, self).__init__(NOTIFICATION_TYPE.ADVENT_CALENDAR_DOORS_AVAILABLE, self.MSG_ID)
        self.__popUpNotificationCallbackID = None
        return

    def start(self, model):
        result = super(AdventCalendarDoorsAvailableListener, self).start(model)
        self.__tryNotify()
        self.__adventController.onDoorOpened += self.__tryNotify
        self.__adventController.onConfigChanged += self.__tryNotify
        g_eventBus.addListener(events.NyInitialNotificationEvent.INITIAL_NOTIFICATION_SHOWN, self.__onNyInitialNotificationShown, EVENT_BUS_SCOPE.LOBBY)
        return result

    def stop(self):
        super(AdventCalendarDoorsAvailableListener, self).stop()
        g_eventBus.removeListener(events.NyInitialNotificationEvent.INITIAL_NOTIFICATION_SHOWN, self.__onNyInitialNotificationShown, EVENT_BUS_SCOPE.LOBBY)
        self.__adventController.onConfigChanged -= self.__tryNotify
        self.__adventController.onDoorOpened -= self.__tryNotify

    def _createNotificationData(self, **kwargs):
        return kwargs.get('ctx', {})

    def _createDecorator(self, notificationData):
        return AdventCalendarDoorsAvailableDecorator(self._getNotificationId(), self._model(), **notificationData)

    def __tryNotify(self):
        if not self.__adventController.isAvailable():
            return self.__notifyOrRemoveOrDelay(False)
        availableDoorsAmount = len([ dayID for dayID in range(1, self.__adventController.config.doorsCount + 1) if getDoorState(dayID) == DoorState.READY_TO_OPEN ])
        if not availableDoorsAmount:
            self.__notifyOrRemoveOrDelay(False)
            return
        template, state, canShowPopUp = self.__getNotificationInfo(availableDoorsAmount)
        data = {'state': state.value,
         'template': template}
        priority = NotificationPriorityLevel.LOW
        if canShowPopUp:
            priority = NotificationPriorityLevel.HIGH
        self.__notifyOrRemoveOrDelay(True, canShowPopUp=canShowPopUp, isDelayed=self.__nyController.isEnabled(), ctx={'priority': priority,
         'template': template,
         'linkageData': data})

    def __notifyOrRemoveOrDelay(self, isAdding, canShowPopUp=False, isDelayed=False, ctx=None):
        if not isAdding:
            self.__cancelPopUpNotificationCallback()
            self._notifyOrRemove(False)
            return
        if not isDelayed:
            self._notifyOrRemove(isAdding, isStateChanged=canShowPopUp, ctx=ctx)
            return

        def callback():
            self.__popUpNotificationCallbackID = None
            self._notifyOrRemove(isAdding, isStateChanged=canShowPopUp, ctx=ctx)
            return

        self.__cancelPopUpNotificationCallback()
        self.__popUpNotificationCallbackID = BigWorld.callback(self.POPUP_NOTIFICATION_DELAY, callback)

    def __getNotificationInfo(self, availableDoorsAmount):
        canShowPopUp = False
        template = GFNotificationTemplates.ADVENT_CALENDAR_DOORS_AVAILABLE
        state = DoorsAvailableNotificationState.DOORS_AVAILABLE
        isFirstEntry = not getAdventCalendarSetting(AdventCalendar.FIRST_ENTRY_NOTIFICATION_SHOWN) and not self.__nyController.isEnabled()
        if self.__adventController.isInPostActivePhase():
            template = GFNotificationTemplates.ADVENT_CALENDAR_DOORS_AVAILABLE_POST_EVENT
            state = DoorsAvailableNotificationState.POST_EVENT
        elif isFirstEntry:
            template = GFNotificationTemplates.ADVENT_CALENDAR_DOORS_AVAILABLE_FIRST_ENTRY
            state = DoorsAvailableNotificationState.FIRST_ENTRY
        isEnoughAvailableDoors = availableDoorsAmount >= MIN_AVAILABLE_DOORS_REQUIRED_FOR_NOTIFICATION
        if self.__isFirstDayPostEvent() or self.__isLastDayPostEvent() or isEnoughAvailableDoors or isFirstEntry:
            canShowPopUp = self.__canShowPopUp()
        return (template, state, canShowPopUp)

    def __canShowPopUp(self):
        currentDay = self.__adventController.getCurrentDayNumber()
        return getAdventCalendarSetting(AdventCalendar.LAST_DAY_POPUP_SEEN) < currentDay

    def __isFirstDayPostEvent(self):
        startDate = self.__adventController.postEventStartDate
        return startDate + time_utils.ONE_DAY > self.__adventController.getCurrentTime > startDate

    def __isLastDayPostEvent(self):
        endDate = self.__adventController.postEventEndDate
        return endDate > self.__adventController.getCurrentTime > endDate - time_utils.ONE_DAY

    def __onNyInitialNotificationShown(self, _):
        self.__tryNotify()

    def __cancelPopUpNotificationCallback(self):
        if self.__popUpNotificationCallbackID is not None:
            BigWorld.cancelCallback(self.__popUpNotificationCallbackID)
            self.__popUpNotificationCallbackID = None
        return
