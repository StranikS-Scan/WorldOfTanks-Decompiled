# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fort_rush/scripts/client/fort_rush/gui/impl/lobby/battle_results_view.py
from __future__ import absolute_import
from fort_rush.gui.impl.gen.view_models.views.lobby.post_battle_results_view.post_battle_results_view_model import PostBattleResultsViewModel
from fort_rush.gui.impl.lobby.presenters.fort_rush_battle_result_sub_presenter import FortRushBattleResultsSubPresenter
from fort_rush.gui.scaleform.genConsts.FORT_RUSH_HANGAR_ALIASES import FORT_RUSH_HANGAR_ALIASES
from frameworks.wulf import ViewSettings, WindowFlags, ViewFlags
from gui.Scaleform.framework.entities.View import ViewKey
from gui.Scaleform.lobby_entry import getLobbyStateMachine
from gui.impl.gen import R
from gui.impl.pub import ViewImpl, WindowImpl
from gui.sounds.ambients import BattleResultsEnv
from gui.lobby_state_machine.routable_view import IRoutableView
from gui.lobby_state_machine.router import SubstateRouter
from helpers import dependency
from skeletons.gui.battle_results import IBattleResultsService

class FortRushBattleResultsView(ViewImpl, IRoutableView):
    __battleResults = dependency.descriptor(IBattleResultsService)
    __sound_env__ = BattleResultsEnv

    def __init__(self, *args, **kwargs):
        viewModel = PostBattleResultsViewModel()
        settings = ViewSettings(R.views.fort_rush.mono.lobby.battle_results(), flags=ViewFlags.VIEW, model=viewModel)
        super(FortRushBattleResultsView, self).__init__(settings)
        self.__arenaUniqueID = kwargs.get('arenaUniqueID')
        self.__subPresenter = FortRushBattleResultsSubPresenter(viewModel, self)
        self.__router = None
        return

    @property
    def arenaUniqueID(self):
        return self.__arenaUniqueID

    @property
    def viewModel(self):
        return super(FortRushBattleResultsView, self).getViewModel()

    def getRouterModel(self):
        return self.viewModel.router

    def createContextMenu(self, event):
        window = self.__subPresenter.createContextMenu(event)
        return window if window is not None else super(FortRushBattleResultsView, self).createContextMenu(event)

    def createToolTipContent(self, event, contentID):
        content = self.__subPresenter.createToolTipContent(event, contentID)
        return content if content is not None else super(FortRushBattleResultsView, self).createToolTipContent(event, contentID)

    def _finalize(self):
        self.__subPresenter.finalize()
        self.__subPresenter = None
        self.__arenaUniqueID = None
        self.__router.fini()
        self.__router = None
        super(FortRushBattleResultsView, self)._finalize()
        return

    def _getEvents(self):
        return ((self.viewModel.onClose, self.__onClose),)

    def _onLoading(self, *args, **kwargs):
        lsm = getLobbyStateMachine()
        state = lsm.getStateByViewKey(ViewKey(alias=FORT_RUSH_HANGAR_ALIASES.FORT_RUSH_BATTLE_RESULTS))
        self.__router = SubstateRouter(lsm, self, state)
        self.__router.init()
        super(FortRushBattleResultsView, self)._onLoading(*args, **kwargs)
        statsController = self.__battleResults.getStatsCtrl(self.__arenaUniqueID)
        battleResults = statsController.getResults()
        self.__subPresenter.initialize()
        with self.viewModel.transaction() as viewModel:
            self.__subPresenter.packBattleResults(battleResults)
            viewModel.setIsLeaver(battleResults.reusable.personal.avatar.hasPenalties())

    def __onClose(self):
        self.destroyWindow()


class FortRushPostBattleResultsWindow(WindowImpl):

    def __init__(self, layer, **kwargs):
        super(FortRushPostBattleResultsWindow, self).__init__(content=FortRushBattleResultsView(**kwargs), wndFlags=WindowFlags.WINDOW, layer=layer)
