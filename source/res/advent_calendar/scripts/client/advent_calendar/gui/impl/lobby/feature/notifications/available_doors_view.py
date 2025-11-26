# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: advent_calendar/scripts/client/advent_calendar/gui/impl/lobby/feature/notifications/available_doors_view.py
from __future__ import absolute_import
from account_helpers.AccountSettings import AdventCalendar
from advent_calendar.gui.impl.gen.view_models.views.lobby.notifications.available_doors_view_model import AvailableDoorsViewModel, State, Theme
from advent_calendar.gui.impl.lobby.feature.advent_helper import setAdventCalendarSetting
from advent_calendar.gui.shared.event_dispatcher import showAdventCalendarMainWindow
from advent_calendar.skeletons import IAdventCalendarController
from gui.impl.lobby.gf_notifications.notification_base import NotificationBase
from helpers import dependency

class AvailableDoorsView(NotificationBase):
    __adventController = dependency.descriptor(IAdventCalendarController)

    def __init__(self, resId, *args, **kwargs):
        super(AvailableDoorsView, self).__init__(resId, AvailableDoorsViewModel(), *args, **kwargs)

    @property
    def viewModel(self):
        return self.getViewModel()

    def _getEvents(self):
        events = super(AvailableDoorsView, self)._getEvents()
        return events + ((self.viewModel.onClick, self.__onClick),)

    def _update(self):
        state = State(self.linkageData.state)
        if self.__adventController.isNYEntryPointStarted:
            theme = Theme.WINTER
        else:
            theme = Theme.AUTUMN
        if self._isPopUp:
            currentDay = self.__adventController.getCurrentDayNumber()
            setAdventCalendarSetting(AdventCalendar.LAST_DAY_POPUP_SEEN, currentDay)
        with self.viewModel.transaction() as tx:
            tx.setState(state)
            tx.setTheme(theme)
            tx.setEventEndDate(self.__adventController.postEventEndDate)
            tx.setIsPopUp(self._isPopUp)
            tx.setIsButtonDisabled(not self._canNavigate())

    def __onClick(self):
        if self._canNavigate() and self.__adventController.isAvailable():
            showAdventCalendarMainWindow()
