# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/lobby/new_year/ny_leaderboard_recount_view.py
from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.ny_leaderboard_recount_view_model import NyLeaderboardRecountViewModel
from frameworks.wulf import ViewFlags, ViewSettings, WindowFlags, WindowLayer
from gui.shared.view_helpers.blur_manager import CachedBlur
from gui.impl.pub import ViewImpl, WindowImpl
from gui.impl.gen import R
from gui.shared.utils.graphics import isRendererPipelineDeferred

class NyLeaderboardRecountView(ViewImpl):
    __slots__ = ('__blur',)

    def __init__(self):
        settings = ViewSettings(R.views.new_year.lobby.new_year.NyLeaderboardRecountView())
        settings.flags = ViewFlags.VIEW
        settings.model = NyLeaderboardRecountViewModel()
        self.__blur = None
        super(NyLeaderboardRecountView, self).__init__(settings)
        return

    @property
    def viewModel(self):
        return super(NyLeaderboardRecountView, self).getViewModel()

    def _getEvents(self):
        return ((self.getViewModel().onClose, self.__onClose),)

    def _onLoading(self, *args, **kwargs):
        super(NyLeaderboardRecountView, self)._onLoading(*args, **kwargs)
        self.viewModel.setHasBackground(not isRendererPipelineDeferred())
        if isRendererPipelineDeferred():
            self.__blur = CachedBlur(enabled=True, ownLayer=WindowLayer.WINDOW)

    def _finalize(self):
        if self.__blur:
            self.__blur.fini()
            self.__blur = None
        return

    def __onClose(self):
        self.destroyWindow()


class NyLeaderboardRecountViewWindow(WindowImpl):
    __slots__ = ()

    def __init__(self, parent=None):
        super(NyLeaderboardRecountViewWindow, self).__init__(wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=NyLeaderboardRecountView(), parent=parent)
