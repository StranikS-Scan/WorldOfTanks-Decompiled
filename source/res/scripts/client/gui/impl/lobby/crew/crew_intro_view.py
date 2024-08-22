# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/crew_intro_view.py
from account_helpers.settings_core.settings_constants import GuiSettingsBehavior
from base_crew_view import BaseCrewSubView
from frameworks.wulf import ViewSettings, WindowFlags, WindowLayer
from gui import GUI_SETTINGS
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.crew.crew_intro_view_model import CrewIntroViewModel
from gui.impl.gui_decorators import args2params
from gui.impl.pub.lobby_window import LobbyWindow
from gui.shared.account_settings_helper import AccountSettingsHelper, WelcomeScreen
from uilogging.crew_nps.logging_constants import CrewNpsViewKeys
from uilogging.crew_nps.loggers import CrewNpsWelcomeViewLogger

class CrewIntroView(BaseCrewSubView):
    __slots__ = ('__screenName', '__uiLogger')

    def __init__(self, screenName):
        settings = ViewSettings(R.views.lobby.crew.CrewIntroView())
        settings.model = CrewIntroViewModel()
        self.__screenName = screenName
        self.__uiLogger = CrewNpsWelcomeViewLogger(self, CrewNpsViewKeys.WELCOME)
        super(CrewIntroView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(CrewIntroView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(CrewIntroView, self)._onLoading(*args, **kwargs)
        self.__uiLogger.initialize()
        self.__updateViewModel()

    def _finalize(self):
        super(CrewIntroView, self)._finalize()
        self.__uiLogger.finalize()

    def _getEvents(self):
        return ((self.viewModel.onClose, self.__close),)

    def __updateViewModel(self):
        slideData = GUI_SETTINGS.crew.get('welcomeScreens', {}).get(self.__screenName, [])
        with self.viewModel.transaction() as tx:
            tx.setScreenName(self.__screenName)
            slides = tx.getSlides()
            slides.clear()
            for value in slideData:
                slides.addNumber(value)

            slides.invalidate()

    @args2params(str)
    def __close(self, reason):
        self.__uiLogger.logButtonClick(reason)
        self.destroyWindow()
        AccountSettingsHelper.welcomeScreenShown(GuiSettingsBehavior.CREW_NPS_WELCOME_SHOWN)


class CrewIntroWindow(LobbyWindow):
    __slots__ = ()

    def __init__(self, screenName=WelcomeScreen.CREW_NPS_WELCOME):
        super(CrewIntroWindow, self).__init__(wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=CrewIntroView(screenName), layer=WindowLayer.TOP_WINDOW)
