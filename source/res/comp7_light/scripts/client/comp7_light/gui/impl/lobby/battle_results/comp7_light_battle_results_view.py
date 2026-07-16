# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_light/scripts/client/comp7_light/gui/impl/lobby/battle_results/comp7_light_battle_results_view.py
from __future__ import absolute_import
import typing
from functools import partial
from comp7_light.gui.impl.gen.view_models.views.lobby.comp7_light_battle_results_view_model import Comp7LightBattleResultsViewModel
from comp7_light.gui.impl.lobby.battle_results.comp7_light_flag_view import Comp7LightFlagWindow
from comp7_light.gui.impl.lobby.battle_results.submodel_presenters.comp7_light_sub_presenter import Comp7LightBattleResultsSubPresenter
from comp7_light.gui.impl.lobby.battle_results.missions_progress.progress_presenter_helpers import getComp7LightProgressionCategoriesPresenters
from comp7_core.gui.battle_results.components.comp7_core_components import checkIfDeserter
from fairplay_violation_types import FairplayViolations
from frameworks.wulf import WindowFlags
from gui.Scaleform.lobby_entry import getLobbyStateMachine
from gui.impl.gen import R
from gui.impl.lobby.battle_results.sounds import RANDOM_BATTLE_RESULTS_SOUND_SPACE
from gui.impl.lobby.battle_results.submodel_presenters.battle_achievements import BattleAchievementsSubPresenter
from gui.impl.lobby.user_missions.hub.hub_view import DailyTabs
from gui.impl.pub import WindowImpl
from gui.impl.pub.view_component import ViewComponent
from gui.lobby_state_machine.routable_view import IRoutableView
from gui.lobby_state_machine.router import SubstateRouter
from gui.server_events.events_dispatcher import showDailyQuests
from gui.shared.view_helpers.blur_manager import ImmediateSceneBlurConfig
from gui.sounds.ambients import BattleResultsEnv
from helpers import dependency
from skeletons.connection_mgr import IConnectionManager
from skeletons.gui.battle_results import IBattleResultsService
from skeletons.gui.game_control import IBlurController
from skeletons.gui.shared.utils import IHangarSpace
if typing.TYPE_CHECKING:
    from skeletons.gui.game_control import IBlurEffect

class Comp7LightBattleResultsWindow(WindowImpl):

    def __init__(self, layer, **kwargs):
        super(Comp7LightBattleResultsWindow, self).__init__(content=Comp7LightBattleResultsView(**kwargs), wndFlags=WindowFlags.WINDOW, layer=layer)


class Comp7LightBattleResultsView(ViewComponent[Comp7LightBattleResultsViewModel], IRoutableView):
    __battleResults = dependency.descriptor(IBattleResultsService)
    __blurCtrl = dependency.descriptor(IBlurController)
    __connectionMgr = dependency.descriptor(IConnectionManager)
    __hangarSpace = dependency.descriptor(IHangarSpace)
    __localStorage = ''
    _COMMON_SOUND_SPACE = RANDOM_BATTLE_RESULTS_SOUND_SPACE
    __sound_env__ = BattleResultsEnv
    _POST_BATTLE_BLUR_SETTINGS_KEY = 'maximum'

    def __init__(self, ctx, *args, **kwargs):
        super(Comp7LightBattleResultsView, self).__init__(layoutID=R.views.comp7_light.mono.lobby.post_battle_results_view(), model=Comp7LightBattleResultsViewModel)
        self.__arenaUniqueID = ctx.get('arenaUniqueID', None)
        self.__subPresenter = Comp7LightBattleResultsSubPresenter(self.viewModel, self)
        self.__flagWindow = None
        self.__router = None
        self.__blur = self.__blurCtrl.createBlur((ImmediateSceneBlurConfig(spaceID=self.__hangarSpace.spaceID, settings=self.__blurCtrl.getSettingsByAlias(self._POST_BATTLE_BLUR_SETTINGS_KEY), persistent=True),))
        return

    @property
    def arenaUniqueID(self):
        return self.__arenaUniqueID

    @property
    def blur(self):
        return self.__blur

    @property
    def viewModel(self):
        return super(Comp7LightBattleResultsView, self).getViewModel()

    def getRouterModel(self):
        return self.viewModel.router

    def createContextMenu(self, event):
        window = self.__subPresenter.createContextMenu(event)
        return window if window is not None else super(Comp7LightBattleResultsView, self).createContextMenu(event)

    def createToolTipContent(self, event, contentID):
        content = self.__subPresenter.createToolTipContent(event, contentID)
        return content if content is not None else super(Comp7LightBattleResultsView, self).createToolTipContent(event, contentID)

    @classmethod
    def getLocalStorage(cls):
        return cls.__localStorage

    @classmethod
    def saveLocalStorage(cls, ctx):
        cls.__localStorage = ctx

    def _getChildComponents(self):
        progressPresenters = getComp7LightProgressionCategoriesPresenters()
        childComponents = {}
        for item in progressPresenters:
            categoryProgressFilter, presenter, allCommonQuests = item
            childComponents[presenter.getViewAlias()] = partial(presenter, categoryProgressFilter=categoryProgressFilter, arenaUniqueID=self.__arenaUniqueID, allCommonQuests=allCommonQuests)

        return childComponents

    def _finalize(self):
        self.__arenaUniqueID = None
        self.__subPresenter.finalize()
        self.__subPresenter = None
        if self.__flagWindow:
            self.__flagWindow.destroy()
            self.__flagWindow = None
        self.__router.fini()
        self.__router = None
        self.__blur.disable()
        self.__blur.fini()
        self.__blur = None
        super(Comp7LightBattleResultsView, self)._finalize()
        return

    def _getEvents(self):
        return ((self.viewModel.onClose, self._onClose), (self.viewModel.onOpenMissions, self._onOpenMissions))

    def _onLoading(self, *args, **kwargs):
        lsm = getLobbyStateMachine()
        self.__router = SubstateRouter(lsm, self, lsm.getStateFromView(self))
        self.__router.init()
        super(Comp7LightBattleResultsView, self)._onLoading(*args, **kwargs)
        statsController = self.__battleResults.getStatsCtrl(self.__arenaUniqueID)
        battleResults = statsController.getResults()
        self.__createFlagWindow()
        self.__subPresenter.initialize()
        with self.viewModel.transaction():
            self.__subPresenter.packBattleResults(battleResults)

    def _onClose(self):
        state = getLobbyStateMachine().getStateFromView(self)
        if state is not None:
            state.goBack()
        return

    def _onOpenMissions(self):
        showDailyQuests(subTab=DailyTabs.QUESTS)

    def __createFlagWindow(self):
        self.__flagWindow = Comp7LightFlagWindow()
        self.__flagWindow.load()
        statsController = self.__battleResults.getStatsCtrl(self.__arenaUniqueID)
        battleResults = statsController.getResults()
        reusable = battleResults.reusable
        isDeserter = checkIfDeserter(reusable, FairplayViolations.COMP7_LIGHT_DESERTER)
        self.__flagWindow.content.viewModel.setWinStatus(reusable.getPersonalTeamResult())
        self.__flagWindow.content.viewModel.setIsLeave(isDeserter)
        achievementPresenter = BattleAchievementsSubPresenter(self.__flagWindow.content.viewModel.getAchievements(), self.__flagWindow.content)
        achievementPresenter.packBattleResults(battleResults)
