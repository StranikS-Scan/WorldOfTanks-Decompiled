# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/crew_welcome_screen.py
from frameworks.wulf import ViewSettings, WindowFlags
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.crew.crew_welcome_screen_model import CrewWelcomeScreenModel
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyWindow
from gui.shared.account_settings_helper import AccountSettingsHelper

class CrewWelcomeScreen(ViewImpl):
    __slots__ = ()

    def __init__(self):
        settings = ViewSettings(R.views.lobby.crew.CrewWelcomeScreen())
        settings.model = CrewWelcomeScreenModel()
        super(CrewWelcomeScreen, self).__init__(settings)

    @property
    def viewModel(self):
        return super(CrewWelcomeScreen, self).getViewModel()

    def _initialize(self, *args, **kwargs):
        super(CrewWelcomeScreen, self)._initialize()
        self.viewModel.onCloseClick += self.__onClose

    def _finalize(self):
        super(CrewWelcomeScreen, self)._finalize()
        self.viewModel.onCloseClick -= self.__onClose

    def __onClose(self):
        AccountSettingsHelper.welcomeScreenShown()
        self.destroyWindow()


class CrewWelcomeScreenWindow(LobbyWindow):
    __slots__ = ()
    UI_SPAM_WINDOW_NAME = 'CrewWelcomeScreenWindow'

    def __init__(self):
        super(CrewWelcomeScreenWindow, self).__init__(wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=CrewWelcomeScreen())
