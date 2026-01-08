# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/battle_results/missions_progress/weekly_missions_progress.py
from gui.battle_results.pbs_helpers.common import getBattleResults
from gui.battle_results.progress.progress_helpers import getReceivedTokensInfo
from gui.impl.backport import BackportTooltipWindow, TooltipData
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.battle_results.progression.weekly_quest_progress_model import WeeklyQuestProgressModel
from gui.impl.gen.view_models.views.lobby.battle_results.progression.weekly_quests_progress_model import WeeklyQuestsProgressModel
from gui.impl.lobby.battle_results.missions_progress.rewards_helper import packBonusesWithActualTokensConvertion
from gui.impl.lobby.battle_results.missions_progress.progression_presenter_interface import IProgressionCategoryPresenter
from gui.impl.lobby.common.tooltips.extended_text_tooltip import ExtendedTextTooltip
from gui.impl.lobby.tooltips.additional_rewards_tooltip import AdditionalRewardsTooltip
from gui.impl.pub.view_component import ViewComponent
from gui.server_events import conditions
from gui.server_events.events_dispatcher import showMissions
from gui.server_events.events_helpers import isWeeklyQuest
from gui.shared.missions.packers.bonus import getWeeklyMissionsBonusPacker
from helpers import dependency
from skeletons.gui.server_events import IEventsCache

class WeeklyMissionsProgressPresenter(ViewComponent[WeeklyQuestsProgressModel], IProgressionCategoryPresenter):
    __eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self, categoryProgressFilter, arenaUniqueID, allCommonQuests):
        super(WeeklyMissionsProgressPresenter, self).__init__(model=WeeklyQuestsProgressModel)
        self.__categoryProgressFilter = categoryProgressFilter
        self.__arenaUniqueID = arenaUniqueID
        self.__allCommonQuests = allCommonQuests
        self.__progress = None
        self.__tooltipData = {}
        self.__bonusesModel = {}
        return

    @classmethod
    def getPathToResource(cls):
        return WeeklyQuestsProgressModel.PATH

    @classmethod
    def getViewAlias(cls):
        return R.aliases.battle_results.progression.WeeklyMissions()

    @property
    def viewModel(self):
        return super(WeeklyMissionsProgressPresenter, self).getViewModel()

    def createToolTip(self, event):
        if event.contentID != R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            return super(WeeklyMissionsProgressPresenter, self).createToolTip(event)
        else:
            tooltipData = self.__getTooltipData(event)
            if tooltipData and isinstance(tooltipData, TooltipData):
                window = BackportTooltipWindow(tooltipData, self.getParentWindow(), event)
                if window is not None:
                    window.load()
            else:
                window = super(WeeklyMissionsProgressPresenter, self).createToolTip(event)
            return window

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.common.tooltips.ExtendedTextTooltip():
            text = event.getArgument('text', '')
            stringifyKwargs = event.getArgument('stringifyKwargs', '')
            return ExtendedTextTooltip(text, stringifyKwargs)
        if contentID == R.views.lobby.tooltips.AdditionalRewardsTooltip():
            showFromIndex = event.getArgument('showFromIndex')
            questId = event.getArgument('questId')
            for data, _, _, _, _ in self.__progress:
                if questId == data.getID():
                    bonuses = self.__bonusesModel[questId]
                    return AdditionalRewardsTooltip(bonuses[int(showFromIndex):])

        return super(WeeklyMissionsProgressPresenter, self).createToolTipContent(event=event, contentID=contentID)

    def _finalize(self):
        self.__tooltipData.clear()
        self.__tooltipData = None
        self.__progress = None
        self.__categoryProgressFilter = None
        self.__arenaUniqueID = None
        self.__bonusesModel.clear()
        self.__bonusesModel = None
        self.__allCommonQuests = None
        super(WeeklyMissionsProgressPresenter, self)._finalize()
        return

    def _getEvents(self):
        return ((self.viewModel.onNavigate, self.__onNavigate),)

    def _onLoading(self, *args, **kwargs):
        super(WeeklyMissionsProgressPresenter, self)._onLoading(*args, **kwargs)
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
        questTokensConvertion, questTokensCount = getReceivedTokensInfo(self.__arenaUniqueID)
        with self.viewModel.transaction() as vm:
            quests = vm.getWeeklyQuests()
            quests.clear()
            for event, pCur, pPrev, reset, complete in self.__progress:
                if isWeeklyQuest(event.getID()):
                    quests.addViewModel(self._getModel(event, pCur, pPrev, reset, complete, questTokensConvertion, questTokensCount))

            quests.invalidate()

    def _getModel(self, data, pCur, pPrev, reset, complete, questTokensConvertion, questTokensCount):
        self.__tooltipData[data.getID()] = {}
        self.__bonusesModel[data.getID()] = {}
        model = WeeklyQuestProgressModel()
        model.setId(data.getID())
        model.setCommonConditionId(data.getInfo().getMainConditionId())
        model.setNavigationEnabled(True)
        if not reset:
            for cond in data.bonusCond.getConditions().items:
                if isinstance(cond, conditions._Cumulativable):
                    for curProg, totalProg, diff, _ in cond.getProgressPerGroup(pCur, pPrev, True).values():
                        model.setCurrentProgress(curProg)
                        model.setEarned(diff)
                        model.setIsCompleted(complete)
                        model.setTotalProgress(totalProg)

        self._packBonuses(pCur, model, data, questTokensConvertion, questTokensCount)
        return model

    def _packBonuses(self, pCur, model, data, questTokensConvertion, questTokensCount):
        bonusPacker = getWeeklyMissionsBonusPacker()
        packBonusesWithActualTokensConvertion(pCur, model, data, questTokensConvertion, questTokensCount, self.__tooltipData[data.getID()], bonusPacker)
        self.__bonusesModel[data.getID()] = model.getBonuses()

    def __getTooltipData(self, event):
        missionParam = event.getArgument('tooltipId', '')
        missionParams = missionParam.rsplit(':', 1)
        if len(missionParams) != 2:
            return self.__tooltipData.get(missionParam)
        missionId, tooltipId = missionParams
        tooltipsData = self.__tooltipData.get(missionId, {})
        return tooltipsData.get(tooltipId, {})

    def __onNavigate(self):
        showMissions()
