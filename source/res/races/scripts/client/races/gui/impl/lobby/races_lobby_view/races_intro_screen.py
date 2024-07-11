# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: races/scripts/client/races/gui/impl/lobby/races_lobby_view/races_intro_screen.py
from account_helpers.AccountSettings import RACES_INTRO_SCREEN_SHOWN
from frameworks.wulf import ViewSettings, WindowFlags, WindowLayer
from gui.impl.pub.lobby_window import LobbyNotificationWindow
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from helpers import dependency
from skeletons.gui.game_control import IRacesBattleController
from races.gui.impl.gen.view_models.views.lobby.races_lobby_view.races_intro_view_model import RacesIntroViewModel

class RacesIntroScreen(ViewImpl):
    __racesCtrl = dependency.descriptor(IRacesBattleController)

    def __init__(self):
        settings = ViewSettings(R.views.races.lobby.races_lobby_view.RacesIntroScreen())
        settings.model = RacesIntroViewModel()
        super(RacesIntroScreen, self).__init__(settings)

    @property
    def viewModel(self):
        return super(RacesIntroScreen, self).getViewModel()

    def _getEvents(self):
        return ((self.viewModel.onClose, self.__onClose),)

    def __onClose(self):
        self.__racesCtrl.setRacesAccountSettings(RACES_INTRO_SCREEN_SHOWN, True)
        self.destroyWindow()


class RacesIntroWindow(LobbyNotificationWindow):
    __slots__ = ()

    def __init__(self, parent=None):
        super(RacesIntroWindow, self).__init__(WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=RacesIntroScreen(), layer=WindowLayer.OVERLAY, parent=parent)
