# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: tank_academy/scripts/client/tank_academy/gui/impl/lobby/tank_academy/tank_academy_welcome_view.py
import logging
from frameworks.wulf import ViewSettings, WindowFlags
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyNotificationWindow
from gui.server_events.events_dispatcher import showBattleMattersMainView
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.game_control import ITankAcademyController
from tank_academy.gui.impl.gen.view_models.views.lobby.tank_academy.tank_academy_welcome_view_model import TankAcademyWelcomeViewModel
_logger = logging.getLogger(__name__)

class TankAcademyWelcomeView(ViewImpl):
    __slots__ = ()
    __tankAcademyController = dependency.descriptor(ITankAcademyController)
    __settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self, ctx):
        settings = ViewSettings(layoutID=R.views.tank_academy.lobby.tank_academy.TankAcademyWelcomeView(), model=TankAcademyWelcomeViewModel())
        super(TankAcademyWelcomeView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(TankAcademyWelcomeView, self).getViewModel()

    def onClose(self):
        self.destroyWindow()
        showBattleMattersMainView()

    def _onLoading(self, *args, **kwargs):
        super(TankAcademyWelcomeView, self)._onLoading(*args, **kwargs)
        self.__settingsCore.serverSettings.setTankAcademyWelcomeScreenShown()
        with self.viewModel.transaction() as model:
            quests = self.__tankAcademyController.getTankAcademyQuests()
            delayedRewardsCount = sum((len(tokens) for quest in quests for tokens in [quest.getVehicleOfferTokens()] if tokens))
            model.setVehiclesCount(delayedRewardsCount)

    def _getEvents(self):
        return ((self.viewModel.onClose, self.onClose),)


class TankAcademyWelcomeViewWindow(LobbyNotificationWindow):
    __slots__ = ()

    def __init__(self, parent=None, ctx=None):
        super(TankAcademyWelcomeViewWindow, self).__init__(wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=TankAcademyWelcomeView(ctx=ctx), parent=parent)
