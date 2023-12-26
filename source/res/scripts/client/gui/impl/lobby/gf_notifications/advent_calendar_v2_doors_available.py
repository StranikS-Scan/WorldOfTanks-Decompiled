# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/gf_notifications/advent_calendar_v2_doors_available.py
from account_helpers import AccountSettings
from account_helpers.AccountSettings import ADVENT_CALENDAR_NOTIFICATION_SHOWED, ADVENT_CALENDAR_LAST_DAY_POPUP_SEEN, ADVENT_CALENDAR_POST_EVENT_NOTIFICATION_SHOWED
from gui.impl.gen.view_models.views.lobby.advent_calendar.notifications.doors_available_view_model import DoorsAvailableViewModel, DoorsAvailableNotificationState
from gui.impl.lobby.gf_notifications.base.notification_base import NotificationBase
from gui.shared.event_dispatcher import showAdventCalendarMainWindow
from helpers import dependency
from skeletons.gui.game_control import IAdventCalendarV2Controller, IGFNotificationsController

class AdventCalendarV2DoorsAvailable(NotificationBase):
    __adventCalendarV2Ctrl = dependency.descriptor(IAdventCalendarV2Controller)
    __gfNotificationController = dependency.descriptor(IGFNotificationsController)

    def __init__(self, resId, *args, **kwargs):
        model = DoorsAvailableViewModel()
        super(AdventCalendarV2DoorsAvailable, self).__init__(resId, model, *args, **kwargs)

    @property
    def viewModel(self):
        return self.getViewModel()

    def _getEvents(self):
        events = super(AdventCalendarV2DoorsAvailable, self)._getEvents()
        return events + ((self.viewModel.onClick, self.__onClick), (self.__gfNotificationController.onBattleQueueStateUpdated, self.__onBattleQueueStateUpdated))

    def _onLoading(self, *args, **kwargs):
        super(AdventCalendarV2DoorsAvailable, self)._onLoading(*args, **kwargs)
        with self.viewModel.transaction() as tx:
            state = DoorsAvailableNotificationState(self.linkageData.state)
            tx.setState(state)
            tx.setEventEndDate(self.linkageData.eventEndDate)
            if state == DoorsAvailableNotificationState.FIRST_ENTRY:
                AccountSettings.setUIFlag(ADVENT_CALENDAR_NOTIFICATION_SHOWED, True)
            elif state == DoorsAvailableNotificationState.POST_EVENT:
                AccountSettings.setUIFlag(ADVENT_CALENDAR_POST_EVENT_NOTIFICATION_SHOWED, True)
            if self._isPopUp:
                AccountSettings.setUIFlag(ADVENT_CALENDAR_LAST_DAY_POPUP_SEEN, self.linkageData.currentDay)
            tx.setIsPopUp(self._isPopUp)
            tx.setIsButtonDisabled(not self._canNavigate())

    def __onClick(self):
        if self._canNavigate() and self.__adventCalendarV2Ctrl.isAvailable():
            showAdventCalendarMainWindow()

    def __onBattleQueueStateUpdated(self):
        self.viewModel.setIsButtonDisabled(not self._canNavigate())
