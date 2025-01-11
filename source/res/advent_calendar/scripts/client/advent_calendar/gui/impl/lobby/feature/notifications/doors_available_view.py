# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: advent_calendar/scripts/client/advent_calendar/gui/impl/lobby/feature/notifications/doors_available_view.py
from account_helpers.AccountSettings import AdventCalendar
from advent_calendar.gui.impl.gen.view_models.views.lobby.notifications.doors_available_view_model import DoorsAvailableViewModel, DoorsAvailableNotificationState
from advent_calendar.gui.impl.lobby.feature.advent_helper import setAdventCalendarSetting
from advent_calendar.gui.shared.event_dispatcher import showAdventCalendarMainWindow
from advent_calendar.skeletons import IAdventCalendarController
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.impl.lobby.gf_notifications.base.notification_base import NotificationBase
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import ViewEventType
from helpers import dependency

class DoorsAvailableView(NotificationBase):
    __adventController = dependency.descriptor(IAdventCalendarController)

    def __init__(self, resId, *args, **kwargs):
        super(DoorsAvailableView, self).__init__(resId, DoorsAvailableViewModel(), *args, **kwargs)

    @property
    def viewModel(self):
        return self.getViewModel()

    def _getEvents(self):
        events = super(DoorsAvailableView, self)._getEvents()
        return events + ((self.viewModel.onClick, self.__onClick),)

    def _initialize(self, *args, **kwargs):
        g_eventBus.addListener(ViewEventType.LOAD_VIEW, self.__loadViewHandler, EVENT_BUS_SCOPE.LOBBY)
        super(DoorsAvailableView, self)._initialize()

    def _finalize(self):
        g_eventBus.removeListener(ViewEventType.LOAD_VIEW, self.__loadViewHandler, EVENT_BUS_SCOPE.LOBBY)
        super(DoorsAvailableView, self)._finalize()

    def _onLoading(self, *args, **kwargs):
        super(DoorsAvailableView, self)._onLoading(*args, **kwargs)
        state = DoorsAvailableNotificationState(self.linkageData.state)
        if state == DoorsAvailableNotificationState.FIRST_ENTRY:
            setAdventCalendarSetting(AdventCalendar.FIRST_ENTRY_NOTIFICATION_SHOWN, True)
        if self._isPopUp:
            currentDay = self.__adventController.getCurrentDayNumber()
            setAdventCalendarSetting(AdventCalendar.LAST_DAY_POPUP_SEEN, currentDay)
        with self.viewModel.transaction() as tx:
            tx.setState(state)
            tx.setEventEndDate(self.__adventController.postEventEndDate)
            tx.setIsPopUp(self._isPopUp)
            tx.setIsButtonDisabled(not self._canNavigate())

    def __onClick(self):
        if self._canNavigate() and self.__adventController.isAvailable():
            showAdventCalendarMainWindow()

    def __loadViewHandler(self, event):
        if event.alias == VIEW_ALIAS.BATTLE_QUEUE:
            self.viewModel.setIsButtonDisabled(not self._canNavigate())
