# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/welcome_screen_view.py
from PlayerEvents import g_playerEvents
from base_crew_view import BaseCrewSubView
from frameworks.wulf import ViewFlags, ViewSettings, WindowFlags, WindowLayer
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.crew.welcome_screen_view_model import WelcomeScreenViewModel
from gui.impl.pub import WindowImpl

class WelcomeScreenView(BaseCrewSubView):
    __slots__ = ('__navigateFrom', '__onCloseCallback')

    def __init__(self, layoutID=R.views.mono.crew.welcome_screen(), navigateFrom=None, onCloseCallback=None):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.VIEW
        settings.model = WelcomeScreenViewModel()
        self.__navigateFrom = navigateFrom
        self.__onCloseCallback = onCloseCallback
        super(WelcomeScreenView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(WelcomeScreenView, self).getViewModel()

    def _getEvents(self):
        return ((self.viewModel.onClose, self._onViewClose), (g_playerEvents.onDisconnected, self._onDisconnected))

    def _onViewClose(self):
        if callable(self.__onCloseCallback):
            self.__onCloseCallback()
        self.destroyWindow()

    def _onDisconnected(self):
        self.destroyWindow()


class WelcomeScreenViewWindow(WindowImpl):

    def __init__(self, navigateFrom=None, parent=None, onCloseCallback=None):
        super(WelcomeScreenViewWindow, self).__init__(WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, layer=WindowLayer.TOP_WINDOW, content=WelcomeScreenView(navigateFrom=navigateFrom, onCloseCallback=onCloseCallback), parent=parent)
