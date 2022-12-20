# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/impl/lobby/views/welcome_view.py
from frameworks.wulf import ViewFlags, ViewSettings, WindowFlags, WindowLayer
from gui.impl.pub import ViewImpl, WindowImpl
from gui.impl.gen import R
from frontline.gui.impl.gen.view_models.views.lobby.views.welcome_view_model import WelcomeViewModel
from gui.shared.event_dispatcher import showFrontlineContainerWindow

class WelcomeView(ViewImpl):

    def __init__(self, layoutID=R.views.frontline.lobby.WelcomeView(), showFullScreen=False, showContainerOnClose=False):
        self._isFullScreen = showFullScreen
        self._showContainerOnClose = showContainerOnClose
        settings = ViewSettings(layoutID, ViewFlags.VIEW if showFullScreen else ViewFlags.LOBBY_TOP_SUB_VIEW, WelcomeViewModel())
        super(WelcomeView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(WelcomeView, self).getViewModel()

    def _getEvents(self):
        return ((self.viewModel.onClose, self.__onViewClose),)

    def __onViewClose(self):
        self.destroyWindow()
        if self._showContainerOnClose:
            showFrontlineContainerWindow()


class WelcomeViewWindow(WindowImpl):

    def __init__(self, parent=None, showFullScreen=False, showContainerOnClose=False):
        super(WelcomeViewWindow, self).__init__(WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, layer=WindowLayer.TOP_WINDOW, content=WelcomeView(showFullScreen=showFullScreen, showContainerOnClose=showContainerOnClose), parent=parent)
