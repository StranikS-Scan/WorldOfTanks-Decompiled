# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/battle_results/missions_progress/daily_missions_progress.py
from constants import EVENT_TYPE
from gui.battle_results.pbs_helpers.common import getBattleResults
from gui.battle_results.progress.progress_helpers import getReceivedTokensInfo
from gui.impl.backport import BackportTooltipWindow, TooltipData
from gui.impl.gen import R
from gui.impl.gen.view_models.common.missions.event_model import EventStatus
from gui.impl.gen.view_models.views.lobby.battle_results.progression.daily_quest_progress_model import DailyQuestProgressModel, DailyQuestTypes
from gui.impl.gen.view_models.views.lobby.battle_results.progression.daily_quests_progress_model import DailyQuestsProgressModel
from gui.impl.lobby.battle_results.missions_progress.rewards_helper import packBonusesWithActualTokensConvertion
from gui.impl.lobby.battle_results.missions_progress.progression_presenter_interface import IProgressionCategoryPresenter
from gui.impl.lobby.common.tooltips.extended_text_tooltip import ExtendedTextTooltip
from gui.impl.lobby.missions.daily_quests_view import DailyTabs
from gui.impl.lobby.tooltips.additional_rewards_tooltip import AdditionalRewardsTooltip
from gui.server_events import conditions
from gui.impl.pub.view_component import ViewComponent
from gui.server_events.events_dispatcher import showDailyQuests
from gui.server_events.events_helpers import isDailyQuest, isPremium
from gui.shared.missions.packers.bonus import getDailyMissionsBonusPacker
from gui.shared.missions.packers.events import getEventUIDataPacker
from helpers import dependency
from skeletons.gui.server_events import IEventsCache

class DailyMissionsProgressPresenter(ViewComponent[DailyQuestsProgressModel], IProgressionCategoryPresenter):
    __eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self, categoryProgressFilter, arenaUniqueID, allCommonQuests):
        super(DailyMissionsProgressPresenter, self).__init__(model=DailyQuestsProgressModel)
        self.__categoryProgressFilter = categoryProgressFilter
        self.__arenaUniqueID = arenaUniqueID
        self.__allCommonQuests = allCommonQuests
        self.__progress = None
        self.__tooltipData = {}
        self.__bonusesModel = {}
        return

    @classmethod
    def getPathToResource(cls):
        return DailyQuestsProgressModel.PATH

    @classmethod
    def getViewAlias(cls):
        return R.aliases.battle_results.progression.DailyMissions()

    @property
    def viewModel(self):
        return super(DailyMissionsProgressPresenter, self).getViewModel()

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipData = self.__getTooltipData(event)
            if tooltipData is not None:
                window = BackportTooltipWindow(tooltipData, self.getParentWindow(), event)
                window.load()
                return window
        return super(DailyMissionsProgressPresenter, self).createToolTip(event)

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

        return super(DailyMissionsProgressPresenter, self).createToolTipContent(event=event, contentID=contentID)

    def _finalize(self):
        self.__tooltipData.clear()
        self.__tooltipData = None
        self.__bonusesModel.clear()
        self.__bonusesModel = None
        self.__progress = None
        self.__categoryProgressFilter = None
        self.__arenaUniqueID = None
        self.__allCommonQuests = None
        super(DailyMissionsProgressPresenter, self)._finalize()
        return

    def _getEvents(self):
        return ((self.viewModel.onNavigate, self.__onNavigate),)

    def _onLoading(self, *args, **kwargs):
        super(DailyMissionsProgressPresenter, self)._onLoading(*args, **kwargs)
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
        with self.viewModel.transaction():
            quests = self.viewModel.getDailyQuests()
            quests.clear()
            for event, pCur, pPrev, reset, complete in self.__progress:
                if isPremium(event.getID()) or isDailyQuest(event.getID()):
                    questModel = self.__createModel(event, pCur, pPrev, reset, complete, questTokensConvertion, questTokensCount)
                    quests.addViewModel(questModel)

            quests.invalidate()

    def __createModel(self, event, pCur, pPrev, reset, complete, questTokensConvertion, questTokensCount):
        eventID = event.getID()
        self.__tooltipData[eventID] = {}
        self.__bonusesModel[eventID] = {}
        packer = getEventUIDataPacker(event)
        model = DailyQuestProgressModel()
        packer.pack(model)
        if complete:
            model.setStatus(EventStatus.DONE)
        elif event.isAvailable()[0]:
            model.setStatus(EventStatus.ACTIVE)
        else:
            model.setStatus(EventStatus.LOCKED)
        model.setNavigationEnabled(True)
        if event.getType() == EVENT_TYPE.TOKEN_QUEST:
            model.setLevel(DailyQuestTypes.EPIC)
        elif isPremium(eventID):
            model.setLevel(DailyQuestTypes.PREMIUM)
        else:
            model.setLevel(DailyQuestTypes(event.getLevel()))
        bonusPacker = getDailyMissionsBonusPacker()
        packBonusesWithActualTokensConvertion(pCur, model, event, questTokensConvertion, questTokensCount, self.__tooltipData[eventID], bonusPacker)
        self.__bonusesModel[eventID] = model.getBonuses()
        condsRoot = event.bonusCond.getConditions()
        if condsRoot.isEmpty():
            return model
        if not reset:
            index = 0
            items = model.bonusCondition.getItems()
            for cond in event.bonusCond.getConditions().items:
                if isinstance(cond, conditions._Cumulativable):
                    for curProg, totalProg, diff, _ in cond.getProgressPerGroup(pCur, pPrev).values():
                        if not diff:
                            continue
                        item = items[index]
                        item.setEarned(diff)
                        if complete:
                            item.setCurrent(totalProg)
                        else:
                            item.setCurrent(curProg)
                        item.setTotal(totalProg)
                        index += 1

        return model

    def __getTooltipData(self, event):
        missionParam = event.getArgument('tooltipId', '')
        missionParams = missionParam.rsplit(':', 1)
        if len(missionParams) != 2:
            return self.__tooltipData.get(missionParam)
        missionId, tooltipId = missionParams
        tooltipsData = self.__tooltipData.get(missionId, {})
        return tooltipsData.get(tooltipId, {})

    def __onNavigate(self):
        showDailyQuests(subTab=DailyTabs.QUESTS)
