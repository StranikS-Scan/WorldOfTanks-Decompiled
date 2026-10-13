# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: tank_academy/scripts/client/tank_academy/gui/impl/lobby/tank_academy/tank_academy_migration_updates_view.py
from frameworks.wulf import ViewSettings, WindowFlags
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyNotificationWindow
from gui.server_events.events_dispatcher import showBattleMattersMainView
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
from tank_academy.gui.impl.gen.view_models.views.lobby.tank_academy.tank_academy_migration_updates_view_model import TankAcademyMigrationUpdatesViewModel

class TankAcademyMigrationUpdatesView(ViewImpl):
    __slots__ = ()
    __settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self, ctx=None):
        settings = ViewSettings(layoutID=R.views.tank_academy.lobby.tank_academy.TankAcademyMigrationUpdatesView(), model=TankAcademyMigrationUpdatesViewModel())
        super(TankAcademyMigrationUpdatesView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(TankAcademyMigrationUpdatesView, self).getViewModel()

    def onClose(self):
        self.destroyWindow()
        showBattleMattersMainView()

    def _getEvents(self):
        return ((self.viewModel.onClose, self.onClose),)

    def _onLoading(self, *args, **kwargs):
        super(TankAcademyMigrationUpdatesView, self)._onLoading(*args, **kwargs)
        self.__settingsCore.serverSettings.setTankAcademyWelcomeScreenShown()


class TankAcademyMigrationUpdatesViewWindow(LobbyNotificationWindow):
    __slots__ = ()

    def __init__(self, parent=None, ctx=None):
        super(TankAcademyMigrationUpdatesViewWindow, self).__init__(wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=TankAcademyMigrationUpdatesView(ctx=ctx), parent=parent)
