# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/battle/prebattle/prebattle_hints_view.py
import typing
import BigWorld
from account_helpers.settings_core.settings_constants import GRAPHICS
from constants import ARENA_PERIOD
from frameworks.wulf import ViewSettings, WindowFlags, WindowLayer, ViewStatus
from gui import InputHandler
from gui.Scaleform.managers.battle_input import BattleGUIKeyHandler
from gui.app_loader.settings import APP_NAME_SPACE
from gui.battle_control.arena_info.interfaces import IArenaLoadController
from gui.impl.gen import R
from gui.impl.gen.view_models.views.battle.prebattle.prebattle_hints_view_model import PrebattleHintsViewModel
from gui.impl.pub import ViewImpl, WindowImpl
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.connection_mgr import IConnectionManager
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.battle_session import IBattleSessionProvider
from skeletons.gui.prebattle_hints.controller import IPrebattleHintsController
from hints_common.prebattle.schemas import configSchema
if typing.TYPE_CHECKING:
    from hints_common.prebattle.schemas import HintModel

class PrebattleHintsView(ViewImpl, BattleGUIKeyHandler, IArenaLoadController):
    __slots__ = ('_hintModel',)
    _LAYOUT_ID = R.views.battle.prebattle.PrebattleHintsView()
    _VIEW_MODEL_CLASS = PrebattleHintsViewModel
    _TRY_CLOSE_WINDOW_PERIOD = 0.1
    _sessionProvider = dependency.descriptor(IBattleSessionProvider)
    _connectionMgr = dependency.descriptor(IConnectionManager)
    _hintsController = dependency.descriptor(IPrebattleHintsController)
    _appLoader = dependency.descriptor(IAppLoader)
    _settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self, hintModel):
        settings = ViewSettings(self._LAYOUT_ID)
        settings.model = self._VIEW_MODEL_CLASS()
        super(PrebattleHintsView, self).__init__(settings)
        self._hintModel = hintModel

    @classmethod
    def needToShow(cls):
        sessionProvider = dependency.instance(IBattleSessionProvider)
        period = sessionProvider.arenaVisitor.getArenaPeriod()
        return period == ARENA_PERIOD.WAITING or period == ARENA_PERIOD.PREBATTLE and configSchema.getModel() is not None and not cls._isTimeToCloseWindow(sessionProvider)

    @staticmethod
    def _isTimeToCloseWindow(sessionProvider):
        leftTime = max(int(sessionProvider.arenaVisitor.getArenaPeriodEndTime() - BigWorld.serverTime()), 0)
        return leftTime <= configSchema.getModel().battleTimerThreshold

    def handleEscKey(self, isDown):
        return isDown

    @property
    def viewModel(self):
        return super(PrebattleHintsView, self).getViewModel()

    def arenaLoadCompleted(self):
        self.viewModel.setCanSkip(True)

    def _onLoading(self, *args, **kwargs):
        super(PrebattleHintsView, self)._onLoading(*args, **kwargs)
        self._sessionProvider.addArenaCtrl(self)
        self._connectionMgr.onDisconnected += self._onDisconnected
        self.viewModel.setIsColorBlind(self._settingsCore.getSetting(GRAPHICS.COLOR_BLIND))

    def _initialize(self):
        InputHandler.g_instance.onKeyUp += self._onHandleKeyDown
        battleApp = self._battleApp
        if battleApp:
            battleApp.registerGuiKeyHandler(self)
            battleApp.enterGuiControlMode(self.uniqueID)
        self.viewModel.setHintType(self._hintModel.hintType)
        self._tryToCloseNextTime()

    def _finalize(self):
        super(PrebattleHintsView, self)._finalize()
        self._sessionProvider.removeArenaCtrl(self)
        self._connectionMgr.onDisconnected -= self._onDisconnected
        InputHandler.g_instance.onKeyUp -= self._onHandleKeyDown
        battleApp = self._battleApp
        if battleApp:
            battleApp.unregisterGuiKeyHandler(self)
            battleApp.leaveGuiControlMode(self.uniqueID)

    def _onHandleKeyDown(self, event):
        if self.viewModel.getCanSkip():
            self._successClose()
            return True
        return False

    def _tryToCloseWindow(self):
        if self.viewStatus == ViewStatus.DESTROYING or self.viewStatus == ViewStatus.DESTROYED:
            return
        period = self._sessionProvider.arenaVisitor.getArenaPeriod()
        if period == ARENA_PERIOD.WAITING:
            self._tryToCloseNextTime()
        elif period == ARENA_PERIOD.PREBATTLE:
            if self._isTimeToCloseWindow(self._sessionProvider):
                self._successClose()
            else:
                self._tryToCloseNextTime()
        else:
            self._successClose()

    def _tryToCloseNextTime(self):
        BigWorld.callback(self._TRY_CLOSE_WINDOW_PERIOD, self._tryToCloseWindow)

    def _onDisconnected(self):
        self.destroyWindow()

    def _successClose(self):
        self._hintsController.onShowHintsWindowSuccess(self._hintModel)
        self.destroyWindow()

    @property
    def _battleApp(self):
        return self._appLoader.getApp(APP_NAME_SPACE.SF_BATTLE)


class PrebattleHintsWindow(WindowImpl):
    __slots__ = ()

    def __init__(self, hintModel, hintsViewClass=None, parent=None):
        super(PrebattleHintsWindow, self).__init__(WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=hintsViewClass(hintModel), parent=parent, layer=WindowLayer.OVERLAY)
