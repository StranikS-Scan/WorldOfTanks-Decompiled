# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/lobby/new_year/ny_leaderboard_info_view.py
from frameworks.wulf import ViewFlags, ViewSettings, WindowFlags
from gui.impl.gen import R
from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.ny_leaderboard_info_view_model import NyLeaderboardInfoViewModel
from gui.impl.pub import ViewImpl, WindowImpl

class NyLeaderboardInfoView(ViewImpl):
    __slots__ = ()

    def __init__(self):
        settings = ViewSettings(R.views.new_year.lobby.new_year.NyLeaderboardInfoView())
        settings.flags = ViewFlags.VIEW
        settings.model = NyLeaderboardInfoViewModel()
        super(NyLeaderboardInfoView, self).__init__(settings)

    def _getEvents(self):
        return ((self.getViewModel().onClose, self.__onClose),)

    def __onClose(self):
        self.destroy()


class NyLeaderboardInfoViewWindow(WindowImpl):
    __slots__ = ()

    def __init__(self, parent=None):
        super(NyLeaderboardInfoViewWindow, self).__init__(wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=NyLeaderboardInfoView(), parent=parent)
