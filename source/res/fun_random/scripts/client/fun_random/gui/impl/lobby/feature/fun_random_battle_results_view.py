# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/impl/lobby/feature/fun_random_battle_results_view.py
from __future__ import absolute_import
import typing
from frameworks.wulf import ViewSettings, WindowFlags
from fun_random.gui.feature.fun_sounds import FUN_BATTLE_RESULTS_SOUND_SPACE
from fun_random.gui.sounds.ambients import FunRandomBattleResultsEnv
from gui.impl.pub import ViewImpl, WindowImpl
from helpers import dependency
from skeletons.connection_mgr import IConnectionManager
from skeletons.gui.battle_results import IBattleResultsService
if typing.TYPE_CHECKING:
    from fun_random.gui.impl.gen.view_models.views.lobby.feature.battle_results.fun_battle_results_view_model import FunBattleResultsViewModel

class FunRandomBattleResultsView(ViewImpl):
    _COMMON_SOUND_SPACE = FUN_BATTLE_RESULTS_SOUND_SPACE
    __sound_env__ = FunRandomBattleResultsEnv
    __battleResults = dependency.descriptor(IBattleResultsService)
    __connectionMgr = dependency.descriptor(IConnectionManager)

    def __init__(self, layoutID, *args, **kwargs):
        self.__arenaUniqueID = kwargs.get('arenaUniqueID', None)
        subPresenterCls = kwargs['subPresenterCls']
        modelClass = subPresenterCls.getViewModelType()
        viewModel = modelClass()
        self.__subPresenter = subPresenterCls(viewModel, self)
        super(FunRandomBattleResultsView, self).__init__(ViewSettings(layoutID, model=viewModel))
        return

    @property
    def arenaUniqueID(self):
        return self.__arenaUniqueID

    @property
    def viewModel(self):
        return super(FunRandomBattleResultsView, self).getViewModel()

    def createContextMenu(self, event):
        window = self.__subPresenter.createContextMenu(event)
        return window if window is not None else super(FunRandomBattleResultsView, self).createContextMenu(event)

    def createToolTipContent(self, event, contentID):
        content = self.__subPresenter.createToolTipContent(event, contentID)
        return content if content is not None else super(FunRandomBattleResultsView, self).createToolTipContent(event, contentID)

    def _initialize(self, *args, **kwargs):
        super(FunRandomBattleResultsView, self)._initialize(*args, **kwargs)
        self.__subPresenter.initialize()

    def _finalize(self):
        self.__subPresenter.finalize()
        self.__subPresenter = None
        self.__arenaUniqueID = None
        super(FunRandomBattleResultsView, self)._finalize()
        return

    def _getEvents(self):
        return ((self.viewModel.onClose, self.__onClose),)

    def _onLoading(self, *args, **kwargs):
        super(FunRandomBattleResultsView, self)._onLoading(*args, **kwargs)
        statsController = self.__battleResults.getStatsCtrl(self.__arenaUniqueID)
        with self.viewModel.transaction():
            battleResults = statsController.getResults()
            self.__subPresenter.packBattleResults(battleResults)

    def __onClose(self):
        self.destroyWindow()


class FunPostBattleResultsWindow(WindowImpl):

    def __init__(self, layer, **kwargs):
        super(FunPostBattleResultsWindow, self).__init__(content=FunRandomBattleResultsView(**kwargs), wndFlags=WindowFlags.WINDOW, layer=layer)
