# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/battle/prebattle_highlights/prebattle_highlights_view.py
from __future__ import absolute_import
from frameworks.wulf import ViewSettings, WindowFlags, WindowLayer
from gui.Scaleform.managers.battle_input import BattleGUIKeyHandler
from gui.app_loader.settings import APP_NAME_SPACE
from gui.impl.battle.prebattle_highlights.presenters.prebattle_highlights_presenter import PrebattleHighlightsPresenter
from gui.impl.gen import R
from gui.impl.gen.view_models.views.battle.prebattle.prebattle_hints_view_model import PrebattleHintsViewModel
from gui.impl.gen.view_models.views.battle.prebattle_highlights.prebattle_highlights_view_model import PrebattleHighlightsViewModel
from gui.impl.pub import ViewImpl, WindowImpl
from helpers import dependency
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.battle_session import IBattleSessionProvider

class PrebattleHighlightsView(ViewImpl, BattleGUIKeyHandler):
    _LAYOUT_ID = R.views.mono.prebattle_highlights.main()
    _VIEW_MODEL_CLASS = PrebattleHighlightsViewModel
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)
    __appLoader = dependency.descriptor(IAppLoader)

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(self._LAYOUT_ID)
        settings.model = self._VIEW_MODEL_CLASS()
        super(PrebattleHighlightsView, self).__init__(settings)
        self.__presenter = None
        self.__pbhCtrl = None
        self.__inStageState = False
        return

    @property
    def viewModel(self):
        return super(PrebattleHighlightsView, self).getViewModel()

    def handleEscKey(self, isDown):
        if self.__inStageState and isDown:
            self.__pbhCtrl.handleEscClose()
            return True
        return False

    @property
    def _battleApp(self):
        return self.__appLoader.getApp(APP_NAME_SPACE.SF_BATTLE)

    def _initialize(self, *args, **kwargs):
        super(PrebattleHighlightsView, self)._initialize()
        if self.__pbhCtrl is None:
            self.__pbhCtrl = self.__sessionProvider.dynamic.prebattleHighlightsController
            if self.__pbhCtrl is not None:
                self.__pbhCtrl.onVehiclesDataReady += self.__onVehiclesDataReady
                self.__pbhCtrl.onStartPbhStage += self.__onStartPbhStage
        return

    def _finalize(self):
        if self.__presenter:
            self.__presenter.finalize()
            self.__presenter = None
        if self.__pbhCtrl is not None:
            self.__pbhCtrl.onVehiclesDataReady -= self.__onVehiclesDataReady
            self.__pbhCtrl.onStartPbhStage -= self.__onStartPbhStage
            self.__pbhCtrl = None
        battleApp = self._battleApp
        if battleApp:
            battleApp.unregisterGuiKeyHandler(self)
            battleApp.leaveGuiControlMode(self.uniqueID)
        self.__inStageState = False
        super(PrebattleHighlightsView, self)._finalize()
        return

    def _onDisconnected(self):
        self.destroyWindow()

    def __onVehiclesDataReady(self):
        self.__presenter = PrebattleHighlightsPresenter(self.viewModel, self, self.__pbhCtrl)
        self.__presenter.initialize()
        self.__presenter.packModel()

    def __onStartPbhStage(self):
        self.__inStageState = True
        battleApp = self._battleApp
        if battleApp:
            battleApp.registerGuiKeyHandler(self)
            battleApp.enterGuiControlMode(self.uniqueID)


class PrebattleHighlightsWindow(WindowImpl):
    __slots__ = ()

    def __init__(self, parent=None):
        super(PrebattleHighlightsWindow, self).__init__(WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=PrebattleHighlightsView(), parent=parent, layer=WindowLayer.WINDOW)

    def _onReady(self):
        pass
