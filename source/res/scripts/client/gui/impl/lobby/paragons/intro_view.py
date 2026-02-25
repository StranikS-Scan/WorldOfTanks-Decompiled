# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/paragons/intro_view.py
from account_helpers.AccountSettings import AccountSettings, Paragons
from frameworks.wulf import ViewFlags, ViewSettings, WindowFlags
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.paragons.intro_view_model import IntroViewModel
from gui.impl.gen.view_models.views.lobby.paragons.navigation_view_model import TabId
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyWindow
from gui.impl.lobby.paragons.paragons_window_events import showParagonsNavigationView
from helpers import dependency
from skeletons.gui.game_control import IParagonsController

class IntroView(ViewImpl):
    __slots__ = ('__onCloseCallback',)
    __paragonsController = dependency.descriptor(IParagonsController)

    def __init__(self, onCloseCallback=None):
        settings = ViewSettings(R.views.lobby.paragons.IntroView())
        settings.flags = ViewFlags.VIEW
        settings.model = IntroViewModel()
        self.__onCloseCallback = onCloseCallback
        super(IntroView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(IntroView, self).getViewModel()

    def _onLoaded(self, *args, **kwargs):
        super(IntroView, self)._onLoaded(*args, **kwargs)
        AccountSettings.setParagons(Paragons.INTRO_SEEN, True)

    def _getEvents(self):
        return ((self.viewModel.onClose, self.__onCloseView), (self.viewModel.onGoToFeature, self.__onGoToFeature), (self.__paragonsController.onFeatureStateChanged, self.__onFeatureStateChanged))

    def __onFeatureStateChanged(self, isPaused, isEnabled):
        if not isEnabled or isPaused:
            self.__onCloseView()

    def __onCloseView(self):
        self.destroyWindow()
        if self.__onCloseCallback is not None:
            self.__onCloseCallback()
        return

    def __onGoToFeature(self):
        self.destroyWindow()
        showParagonsNavigationView(tabId=TabId.CHAPTERS)


class IntroViewWindow(LobbyWindow):
    __slots__ = ()

    def __init__(self, parent=None, onCloseCallback=None):
        super(IntroViewWindow, self).__init__(WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=IntroView(onCloseCallback), parent=parent)
