# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/daily/ny_daily_quests_info_view.py
from frameworks.wulf import ViewFlags, ViewSettings, WindowFlags
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.daily.ny_daily_quests_info_view_model import NyDailyQuestsInfoViewModel
from gui.impl.pub import ViewImpl, WindowImpl
from gui.shared.event_dispatcher import showDailyQuestsView

class NyDailyQuestsInfoView(ViewImpl):
    __slots__ = ()

    def __init__(self):
        settings = ViewSettings(R.views.lobby.daily.NyDailyQuestsInfoView())
        settings.flags = ViewFlags.VIEW
        settings.model = NyDailyQuestsInfoViewModel()
        super(NyDailyQuestsInfoView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(NyDailyQuestsInfoView, self).getViewModel()

    def _getEvents(self):
        return ((self.viewModel.onClose, self.__onClose),)

    def __onClose(self):
        self.destroyWindow()
        showDailyQuestsView()


class NyDailyQuestsInfoViewWindow(WindowImpl):
    __slots__ = ()

    def __init__(self, parent=None):
        super(NyDailyQuestsInfoViewWindow, self).__init__(wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=NyDailyQuestsInfoView(), parent=parent)
