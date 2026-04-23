# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/lobby/battle_results/comp7_battle_results_view.py
from __future__ import absolute_import
import logging
from functools import partial
import typing
from comp7.gui.impl.gen.view_models.views.lobby.comp7_battle_results_view_model import Comp7BattleResultsViewModel
from comp7.gui.impl.lobby.battle_results.comp7_flag_view import Comp7FlagWindow
from comp7.gui.impl.lobby.battle_results.missions_progress.progress_presenter_helpers import getComp7ProgressionCategoriesPresenters
from comp7.gui.impl.lobby.battle_results.submodel_presenters.comp7_sub_presenter import Comp7BattleResultsSubPresenter
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
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.game_control import IBlurController
from skeletons.gui.shared.utils import IHangarSpace
if typing.TYPE_CHECKING:
    from skeletons.gui.game_control import IBlurEffect
_logger = logging.getLogger(__name__)

class Comp7BattleResultsWindow(WindowImpl):

    def __init__(self, layer, **kwargs):
        super(Comp7BattleResultsWindow, self).__init__(content=Comp7BattleResultsView(**kwargs), wndFlags=WindowFlags.WINDOW, layer=layer)


class Comp7BattleResultsView(ViewComponent[Comp7BattleResultsViewModel], IRoutableView):
    __battleResults = dependency.descriptor(IBattleResultsService)
    __blurCtrl = dependency.descriptor(IBlurController)
    __c11nService = dependency.instance(ICustomizationService)
    __connectionMgr = dependency.descriptor(IConnectionManager)
    __hangarSpace = dependency.descriptor(IHangarSpace)
    __localStorage = ''
    _COMMON_SOUND_SPACE = RANDOM_BATTLE_RESULTS_SOUND_SPACE
    __sound_env__ = BattleResultsEnv
    _POST_BATTLE_BLUR_SETTINGS_KEY = 'maximum'

    def __init__(self, ctx, *args, **kwargs):
        super(Comp7BattleResultsView, self).__init__(layoutID=R.views.comp7.mono.lobby.post_battle_results_view(), model=Comp7BattleResultsViewModel)
        self.__arenaUniqueID = ctx.get('arenaUniqueID', None)
        self.__subPresenter = Comp7BattleResultsSubPresenter(self.viewModel, self)
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
        return super(Comp7BattleResultsView, self).getViewModel()

    def getRouterModel(self):
        return self.viewModel.router

    def createContextMenu(self, event):
        window = self.__subPresenter.createContextMenu(event)
        return window if window is not None else super(Comp7BattleResultsView, self).createContextMenu(event)

    def createToolTip(self, event):
        questsPresenter = self.getChildView(R.aliases.comp7.shared.BattleResultsCustomizationQuests())
        if questsPresenter is not None:
            tooltip = questsPresenter.createToolTip(event)
            if tooltip is not None:
                return tooltip
        return super(Comp7BattleResultsView, self).createToolTip(event)

    def createToolTipContent(self, event, contentID):
        content = self.__subPresenter.createToolTipContent(event, contentID)
        return content if content is not None else super(Comp7BattleResultsView, self).createToolTipContent(event, contentID)

    @classmethod
    def getLocalStorage(cls):
        return cls.__localStorage

    @classmethod
    def saveLocalStorage(cls, ctx):
        cls.__localStorage = ctx

    def _getChildComponents(self):
        progressPresenters = getComp7ProgressionCategoriesPresenters()
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
        super(Comp7BattleResultsView, self)._finalize()
        return

    def _getEvents(self):
        return ((self.viewModel.onClose, self._onClose), (self.viewModel.onOpenMissions, self._onOpenMissions))

    def _onLoading(self, *args, **kwargs):
        lsm = getLobbyStateMachine()
        self.__router = SubstateRouter(lsm, self, lsm.getStateFromView(self))
        self.__router.init()
        super(Comp7BattleResultsView, self)._onLoading(*args, **kwargs)
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
        self.__flagWindow = Comp7FlagWindow()
        self.__flagWindow.load()
        statsController = self.__battleResults.getStatsCtrl(self.__arenaUniqueID)
        battleResults = statsController.getResults()
        reusable = battleResults.reusable
        isDeserter = checkIfDeserter(reusable, FairplayViolations.COMP7_DESERTER)
        self.__flagWindow.content.viewModel.setWinStatus(reusable.getPersonalTeamResult())
        self.__flagWindow.content.viewModel.setIsLeave(isDeserter)
        achievementPresenter = BattleAchievementsSubPresenter(self.__flagWindow.content.viewModel.getAchievements(), self.__flagWindow.content)
        achievementPresenter.packBattleResults(battleResults)
