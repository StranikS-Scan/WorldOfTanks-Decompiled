# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/impl/lobby/views/frontline_battle_results_view.py
from frontline.constants.aliases import FrontlineHangarAliases
from frameworks.wulf import ViewSettings, WindowFlags, ViewFlags
from gui.Scaleform.framework.entities.View import ViewKey
from gui.Scaleform.lobby_entry import getLobbyStateMachine
from gui.impl.gen import R
from gui.impl.pub import ViewImpl, WindowImpl
from gui.lobby_state_machine.routable_view import IRoutableView
from gui.lobby_state_machine.router import SubstateRouter
from helpers import dependency
from frontline.gui.impl.gen.view_models.views.lobby.views.post_battle_results_view.post_battle_results_view_model import PostBattleResultsViewModel
from frontline.gui.impl.lobby.presenters.frontline_battle_result_sub_presenter import FrontlineBattleResultsSubPresenter
from skeletons.connection_mgr import IConnectionManager
from skeletons.gui.battle_results import IBattleResultsService

class FrontlineBattleResultsView(ViewImpl, IRoutableView):
    __battleResults = dependency.descriptor(IBattleResultsService)
    __connectionMgr = dependency.descriptor(IConnectionManager)
    __localStorage = ''

    def __init__(self, ctx, *args, **kwargs):
        viewModel = PostBattleResultsViewModel()
        settings = ViewSettings(R.views.frontline.mono.lobby.post_battle_results_view(), flags=ViewFlags.VIEW, model=viewModel)
        super(FrontlineBattleResultsView, self).__init__(settings)
        self.__arenaUniqueID = ctx.get('arenaUniqueID', None)
        self.__subPresenter = FrontlineBattleResultsSubPresenter(viewModel, self)
        self.__router = None
        return

    @property
    def arenaUniqueID(self):
        return self.__arenaUniqueID

    @property
    def viewModel(self):
        return super(FrontlineBattleResultsView, self).getViewModel()

    def getRouterModel(self):
        return self.viewModel.router

    def createContextMenu(self, event):
        window = self.__subPresenter.createContextMenu(event)
        return window if window is not None else super(FrontlineBattleResultsView, self).createContextMenu(event)

    def createToolTipContent(self, event, contentID):
        content = self.__subPresenter.createToolTipContent(event, contentID)
        return content if content is not None else super(FrontlineBattleResultsView, self).createToolTipContent(event, contentID)

    @classmethod
    def getLocalStorage(cls):
        return cls.__localStorage

    @classmethod
    def saveLocalStorage(cls, ctx):
        cls.__localStorage = ctx

    def _initialize(self, *args, **kwargs):
        super(FrontlineBattleResultsView, self)._initialize(*args, **kwargs)
        self.__subPresenter.initialize()

    def _finalize(self):
        self.__subPresenter.finalize()
        self.__subPresenter = None
        self.__arenaUniqueID = None
        self.__router.fini()
        self.__router = None
        super(FrontlineBattleResultsView, self)._finalize()
        return

    def _getEvents(self):
        return ((self.viewModel.onClose, self.__onClose),)

    def _onLoading(self, *args, **kwargs):
        lsm = getLobbyStateMachine()
        state = lsm.getStateByViewKey(ViewKey(alias=FrontlineHangarAliases.FRONTLINE_BATTLE_RESULTS))
        self.__router = SubstateRouter(lsm, self, state)
        self.__router.init()
        super(FrontlineBattleResultsView, self)._onLoading(*args, **kwargs)
        statsController = self.__battleResults.getStatsCtrl(self.__arenaUniqueID)
        battleResults = statsController.getResults()
        with self.viewModel.transaction():
            self.__subPresenter.packBattleResults(battleResults)

    def __onClose(self):
        self.destroyWindow()


class FrontlinePostBattleResultsWindow(WindowImpl):

    def __init__(self, layer, **kwargs):
        super(FrontlinePostBattleResultsWindow, self).__init__(content=FrontlineBattleResultsView(**kwargs), wndFlags=WindowFlags.WINDOW, layer=layer)
