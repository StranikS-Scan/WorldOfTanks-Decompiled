# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/daily/daily_intro_screen_view.py
from frameworks.wulf import ViewFlags, ViewSettings, WindowFlags
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.daily.daily_intro_screen_view_model import DailyIntroScreenViewModel
from gui.impl.pub import ViewImpl, WindowImpl
from gui.server_events import settings
from gui.server_events.events_helpers import isDailyQuestsEnable, isPlayStreakEnable
from gui.shared.event_dispatcher import showDailyQuestsView

class DailyIntroScreenView(ViewImpl):

    def __init__(self, layoutID=R.views.lobby.daily.DailyIntroScreenView()):
        viewSettings = ViewSettings(layoutID)
        viewSettings.flags = ViewFlags.VIEW
        viewSettings.model = DailyIntroScreenViewModel()
        super(DailyIntroScreenView, self).__init__(viewSettings)

    @property
    def viewModel(self):
        return super(DailyIntroScreenView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(DailyIntroScreenView, self)._onLoading()
        with self.viewModel.transaction() as model:
            model.setIsPlayStreakEnabled(isPlayStreakEnable())
            model.setIsDailyQuestsEnabled(isDailyQuestsEnable())

    def _onLoaded(self, *args, **kwargs):
        super(DailyIntroScreenView, self)._onLoaded()
        with settings.dailyQuestSettings() as dq:
            dq.setDailyQuestsIntroSeen(True)

    def _getEvents(self):
        return ((self.viewModel.onClose, self.__onClose),)

    def __onClose(self):
        self.destroyWindow()
        showDailyQuestsView()


class DailyIntroScreenViewWindow(WindowImpl):
    __slots__ = ()

    def __init__(self, parent=None):
        super(DailyIntroScreenViewWindow, self).__init__(wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=DailyIntroScreenView(), parent=parent)
