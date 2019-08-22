# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/battle_royale/battle_royale_results.py
import logging
from helpers import dependency
from skeletons.gui.app_loader import IAppLoader
from gui.impl.gen.resources import R
from gui.impl.pub import ViewImpl
from frameworks.wulf import ViewFlags, WindowFlags, Window, WindowSettings
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework.managers.loaders import ViewKey
from gui.impl.gen.view_models.views.battle_royale.battle_royale_results_view_model import BattleRoyaleResultsViewModel
from gui.Scaleform.daapi.view.lobby.battle_royale.battle_royale_score_view import BattleRoyaleScoreView
from gui.Scaleform.daapi.view.lobby.battle_royale.battle_royale_summary_results import BattleRoyaleSummaryResults
from gui.Scaleform.managers.battle_input import BattleGUIKeyHandler
_logger = logging.getLogger(__name__)

class BattleRoyaleResultsView(ViewImpl, BattleGUIKeyHandler):
    appLoader = dependency.descriptor(IAppLoader)

    def __init__(self, *args, **kwargs):
        super(BattleRoyaleResultsView, self).__init__(R.views.common.battle_royale.battle_royale_results.BattleRoyaleResults(), ViewFlags.VIEW, BattleRoyaleResultsViewModel, *args, **kwargs)
        self.__data = kwargs.get('ctx', None)
        self.__scoreResults = None
        self.__summaryResults = None
        self.__hasEscHandler = False
        return

    @property
    def viewModel(self):
        return super(BattleRoyaleResultsView, self).getViewModel()

    def handleEscKey(self, isDown):
        self.__unregisterEsc()
        self.__onCancelAnim()
        return True

    def _initialize(self, *args, **kwargs):
        super(BattleRoyaleResultsView, self)._initialize()
        with self.viewModel.transaction() as model:
            self.__scoreResults = BattleRoyaleScoreView(ctx=self.__data.get('scoreResults', None))
            model.setScoreResults(self.__scoreResults)
            self.__scoreResults.viewModel.onTableFadeOutComplete += self.__onTableFadeOutComplete
        app = self.appLoader.getApp()
        app.registerGuiKeyHandler(self)
        self.__hasEscHandler = True
        return

    def _finalize(self):
        super(BattleRoyaleResultsView, self)._finalize()
        if self.__scoreResults is not None:
            self.__scoreResults.viewModel.onTableFadeOutComplete -= self.__onTableFadeOutComplete
        if self.__summaryResults is not None:
            self.__summaryResults.viewModel.onTabBarAnimComplete -= self.__onTabBarAnimComplete
        self.__unregisterEsc()
        return

    def __onTableFadeOutComplete(self):
        self.__createSummaryResults()

    def __onTabBarAnimComplete(self):
        self.viewModel.setIsAnimInProgress(False)
        self.__unregisterEsc()

    def __unregisterEsc(self):
        if self.__hasEscHandler:
            app = self.appLoader.getApp()
            app.unregisterGuiKeyHandler(self)
            self.__hasEscHandler = False

    def __onCancelAnim(self):
        self.viewModel.setIsAnimInProgress(False)
        if self.__scoreResults is not None:
            self.__scoreResults.viewModel.onTableFadeOutComplete -= self.__onTableFadeOutComplete
            self.__scoreResults.viewModel.setIsAnimCanceled(True)
        if self.__summaryResults is None:
            self.__createSummaryResults()
        self.__summaryResults.viewModel.setIsAnimCanceled(True)
        self.__summaryResults.viewModel.setIsAnimInProgress(False)
        return

    def __createSummaryResults(self):
        with self.viewModel.transaction() as model:
            self.__summaryResults = BattleRoyaleSummaryResults(ctx=self.__data.get('summaryResults', None))
            model.setSummaryResults(self.__summaryResults)
            summaryResultsModel = self.__summaryResults.viewModel
            summaryResultsModel.onTabBarAnimComplete += self.__onTabBarAnimComplete
            summaryResultsModel.setIsAnimCanceled(not self.__hasEscHandler)
        return


class BattleRoyaleResultsWindow(Window):
    appLoader = dependency.descriptor(IAppLoader)
    __slots__ = ()

    def __init__(self, *args, **kwargs):
        view = self.appLoader.getApp().containerManager.getViewByKey(ViewKey(VIEW_ALIAS.BATTLE))
        if view is not None:
            parent = view.getParentWindow()
        else:
            parent = None
        settings = WindowSettings()
        settings.flags = WindowFlags.WINDOW
        settings.content = BattleRoyaleResultsView(*args, **kwargs)
        settings.parent = parent
        super(BattleRoyaleResultsWindow, self).__init__(settings)
        return
