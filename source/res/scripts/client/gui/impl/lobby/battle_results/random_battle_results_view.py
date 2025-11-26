# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/battle_results/random_battle_results_view.py
import logging
from gui.impl.lobby.battle_results.flag_view import FlagWindow
from gui.impl.lobby.battle_results.sounds import RANDOM_BATTLE_RESULTS_SOUND_SPACE
from gui.lobby_state_machine.routable_view import IRoutableView
from frameworks.wulf import ViewFlags, ViewSettings, WindowFlags
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.battle_results.random.random_battle_results_view_model import RandomBattleResultsViewModel
from gui.impl.lobby.battle_results.submodel_presenters.random_sub_presenter import RandomBattleResultsSubPresenter
from gui.impl.lobby.battle_results.submodel_presenters.battle_achievements import BattleAchievementsSubPresenter
from gui.impl.pub import ViewImpl, WindowImpl
from gui.sounds.ambients import BattleResultsEnv
from helpers import dependency
from skeletons.gui.battle_results import IBattleResultsService
from skeletons.gui.customization import ICustomizationService
from skeletons.connection_mgr import IConnectionManager
from gui.Scaleform.lobby_entry import getLobbyStateMachine
from gui.lobby_state_machine.router import SubstateRouter
_logger = logging.getLogger(__name__)

class PostBattleResultsWindow(WindowImpl):

    def __init__(self, layer, **kwargs):
        super(PostBattleResultsWindow, self).__init__(content=RandomBattleResultsView(**kwargs), wndFlags=WindowFlags.WINDOW, layer=layer)


class RandomBattleResultsView(ViewImpl, IRoutableView):
    __battleResults = dependency.descriptor(IBattleResultsService)
    __c11nService = dependency.instance(ICustomizationService)
    __connectionMgr = dependency.descriptor(IConnectionManager)
    __localStorage = ''
    _COMMON_SOUND_SPACE = RANDOM_BATTLE_RESULTS_SOUND_SPACE
    __sound_env__ = BattleResultsEnv

    def __init__(self, ctx, *args, **kwargs):
        viewModel = RandomBattleResultsViewModel()
        settings = ViewSettings(R.views.mono.post_battle.random(), flags=ViewFlags.VIEW, model=viewModel)
        super(RandomBattleResultsView, self).__init__(settings)
        self.__arenaUniqueID = ctx.get('arenaUniqueID', None)
        self.__subPresenter = RandomBattleResultsSubPresenter(viewModel, self)
        self.__flagWindow = None
        self.__router = None
        return

    @property
    def arenaUniqueID(self):
        return self.__arenaUniqueID

    @property
    def viewModel(self):
        return super(RandomBattleResultsView, self).getViewModel()

    def getRouterModel(self):
        return self.viewModel.router

    def createContextMenu(self, event):
        window = self.__subPresenter.createContextMenu(event)
        return window if window is not None else super(RandomBattleResultsView, self).createContextMenu(event)

    def createToolTipContent(self, event, contentID):
        content = self.__subPresenter.createToolTipContent(event, contentID)
        return content if content is not None else super(RandomBattleResultsView, self).createToolTipContent(event, contentID)

    @classmethod
    def getLocalStorage(cls):
        return cls.__localStorage

    @classmethod
    def saveLocalStorage(cls, ctx):
        cls.__localStorage = ctx

    def _initialize(self, *args, **kwargs):
        super(RandomBattleResultsView, self)._initialize(*args, **kwargs)
        self.__subPresenter.initialize()

    def _finalize(self):
        self.__arenaUniqueID = None
        self.__subPresenter.finalize()
        self.__subPresenter = None
        if self.__flagWindow:
            self.__flagWindow.destroy()
            self.__flagWindow = None
        self.__router.fini()
        self.__router = None
        super(RandomBattleResultsView, self)._finalize()
        return

    def _getEvents(self):
        return ((self.viewModel.onClose, self._onClose),)

    def _onLoading(self, *args, **kwargs):
        lsm = getLobbyStateMachine()
        self.__router = SubstateRouter(lsm, self, lsm.getStateFromView(self))
        self.__router.init()
        super(RandomBattleResultsView, self)._onLoading(*args, **kwargs)
        statsController = self.__battleResults.getStatsCtrl(self.__arenaUniqueID)
        battleResults = statsController.getResults()
        self.__createFlagWindow()
        with self.viewModel.transaction():
            self.__subPresenter.packBattleResults(battleResults)

    def _onClose(self):
        self.destroyWindow()

    def __createFlagWindow(self):
        self.__flagWindow = FlagWindow()
        self.__flagWindow.load()
        statsController = self.__battleResults.getStatsCtrl(self.__arenaUniqueID)
        battleResults = statsController.getResults()
        reusable = battleResults.reusable
        self.__flagWindow.content.viewModel.setWinStatus(reusable.getPersonalTeamResult())
        achievementPresenter = BattleAchievementsSubPresenter(self.__flagWindow.content.viewModel.getAchievements(), self.__flagWindow.content)
        achievementPresenter.packBattleResults(battleResults)
