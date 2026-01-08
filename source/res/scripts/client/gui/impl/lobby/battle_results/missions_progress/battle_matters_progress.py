# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/battle_results/missions_progress/battle_matters_progress.py
import typing
from gui.battle_results.pbs_helpers.common import getBattleResults
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.battle_results.progression.battle_matters_progress_model import BattleMattersProgressModel
from gui.impl.lobby.battle_results.missions_progress.progression_presenter_interface import IProgressionCategoryPresenter
from gui.impl.pub.view_component import ViewComponent
from gui.shared.missions.packers.bonus import packMissionsBonusModelAndTooltipData
from gui.impl.lobby.battle_matters.battle_matters_bonus_packer import getBattleMattersBonusPacker, bonusesSort, battleMattersSort
from gui.impl.gen.view_models.views.lobby.battle_matters.quest_view_model import QuestViewModel, State
from gui.server_events.events_dispatcher import showBattleMatters
from gui.impl.backport import BackportTooltipWindow
from gui.impl.lobby.tooltips.additional_rewards_tooltip import AdditionalRewardsTooltip
from helpers import dependency
from skeletons.gui.battle_matters import IBattleMattersController
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.server_events import IEventsCache
if typing.TYPE_CHECKING:
    from typing import Union
    from gui.server_events.event_items import BattleMattersQuest, BattleMattersTokenQuest

class BattleMattersProgressPresenter(ViewComponent[BattleMattersProgressModel], IProgressionCategoryPresenter):
    __battleMattersController = dependency.descriptor(IBattleMattersController)
    __eventsCache = dependency.descriptor(IEventsCache)
    __settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self, categoryProgressFilter, arenaUniqueID, allCommonQuests):
        super(BattleMattersProgressPresenter, self).__init__(model=BattleMattersProgressModel)
        self.__categoryProgressFilter = categoryProgressFilter
        self.__arenaUniqueID = arenaUniqueID
        self.__allCommonQuests = allCommonQuests
        self.__progress = None
        self.__tooltipData = {}
        self.__bonusesModel = {}
        return

    @classmethod
    def getPathToResource(cls):
        return BattleMattersProgressModel.PATH

    @classmethod
    def getViewAlias(cls):
        return R.aliases.battle_results.progression.BattleMatters()

    @property
    def viewModel(self):
        return super(BattleMattersProgressPresenter, self).getViewModel()

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipData = self.getTooltipData(event)
            if tooltipData is not None:
                window = BackportTooltipWindow(tooltipData, self.getParentWindow(), event)
                window.load()
                return window
        return super(BattleMattersProgressPresenter, self).createToolTip(event)

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.tooltips.AdditionalRewardsTooltip():
            showFromIndex = event.getArgument('showFromIndex')
            quest = self.__progress[0][0]
            bonuses = self.__bonusesModel[quest.getID()]
            return AdditionalRewardsTooltip(bonuses[int(showFromIndex):])
        return super(BattleMattersProgressPresenter, self).createToolTipContent(event, contentID)

    def getTooltipData(self, event):
        tooltipId = event.getArgument('tooltipId')
        return None if tooltipId is None else self.__tooltipData.get(tooltipId)

    def _getEvents(self):
        return ((self.viewModel.onNavigate, self.__onNavigate),)

    def _onLoading(self, *args, **kwargs):
        super(BattleMattersProgressPresenter, self)._onLoading(*args, **kwargs)
        self._updateProgress()
        if not self.__progress:
            return
        self._updateModel()
        plugins = self.getParentView().viewModel.getPathToPlugins()
        plugins.set(self.getViewAlias(), self.getPathToResource())

    def _updateProgress(self):
        battleResults = getBattleResults(self.__arenaUniqueID)
        if battleResults:
            self.__progress = self.__categoryProgressFilter(battleResults.reusable, self.__allCommonQuests)

    def _updateModel(self):
        with self.viewModel.transaction() as model:
            questsModel = model.getBattleMatters()
            questsModel.clear()
            model.setNavigationEnabled(self.__battleMattersController.isEnabled())
            for event, pCur, pPrev, _, _ in self.__progress:
                questsModel.addViewModel(self.__createQuestModel(event, pCur, pPrev))

            questsModel.invalidate()

    def _finalize(self):
        self.__tooltipData.clear()
        self.__tooltipData = None
        self.__bonusesModel.clear()
        self.__bonusesModel = None
        self.__categoryProgressFilter = None
        self.__arenaUniqueID = None
        self.__progress = None
        self.__allCommonQuests = None
        super(BattleMattersProgressPresenter, self)._finalize()
        return

    def __createQuestModel(self, quest, pCur, pPrev):
        questModel = QuestViewModel()
        questModel.setNumber(quest.getOrder())
        questState = State.UNAVAILABLE
        if quest.isCompleted():
            questState = State.DONE
        elif quest.isAvailable().isValid:
            questState = State.INPROGRESS
        questModel.setState(questState)
        bonusConditions = quest.bonusCond.getConditions().items
        if bonusConditions:
            curProg, totalProg, diff, _ = bonusConditions[0].getProgressPerGroup(pCur, pPrev, True).values()[0]
            questModel.setLastSeenProgress(curProg - diff)
            questModel.setCurrentProgress(curProg)
            questModel.setMaxProgress(totalProg)
        bonuses = sorted(quest.getBonuses(), cmp=bonusesSort)
        packMissionsBonusModelAndTooltipData(bonuses, getBattleMattersBonusPacker(), questModel.getRewards(), self.__tooltipData, sort=battleMattersSort)
        self.__bonusesModel[quest.getID()] = questModel.getRewards()
        return questModel

    def __onNavigate(self):
        showBattleMatters()
