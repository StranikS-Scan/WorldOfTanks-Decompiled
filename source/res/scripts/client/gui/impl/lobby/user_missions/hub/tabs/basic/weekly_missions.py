# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/user_missions/hub/tabs/basic/weekly_missions.py
import sys
import typing
from constants import Configs
from gui.impl.gen.view_models.views.lobby.tooltips.additional_rewards_tooltip_model import AdditionalRewardsTooltipModel
from helpers import dependency, time_utils
from gui import SystemMessages
from gui.impl.gen import R
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
from gui.impl.gui_decorators import args2params
from gui.impl.lobby.common.tooltips.extended_text_tooltip import ExtendedTextTooltip
from gui.impl.lobby.tooltips.additional_rewards_tooltip import AdditionalRewardsTooltip
from gui.impl.pub.view_component import ViewComponent
from gui.impl.lobby.user_missions.hangar_widget.utils import addSpecialConditions
from gui.server_events import weekly_quests
from gui.server_events.events_helpers import getWeeklyRerollTimeout
from gui.shared.missions.packers.bonus import getWeeklyMissionsBonusPacker, weeklyBonusSort
from gui.shared.missions.packers.events import WeeklyQuestUIDataPacker, findFirstConditionModel, packQuestBonusModelAndTooltipData, packQuestBonusModel
from gui.shared.utils import decorators
from gui.shared.utils.scheduled_notifications import AcyclicNotifier
from gui.impl.backport import BackportTooltipWindow, TooltipData
from gui.impl.gen.view_models.views.lobby.user_missions.hub.tabs.basic_missions.weekly_missions_model import WeeklyMissionsModel
if typing.TYPE_CHECKING:
    from typing import Union
    from frameworks.wulf.view.view_event import ViewEvent

class WeeklyMissions(ViewComponent[WeeklyMissionsModel]):
    LAYOUT_ID = R.aliases.user_missions.hub.basicMissions.WeeklyMissions()
    eventsCache = dependency.descriptor(IEventsCache)
    lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self):
        super(WeeklyMissions, self).__init__(model=WeeklyMissionsModel)
        self._tooltipData = {}
        self._rerollTimeout = 0
        self.__weeklyQuests = {}
        self.__rerollCountdown = 0
        self.__acyclicNotifier = AcyclicNotifier(self.__getRerollCountdown, self._updateCountdownsUntilNextReroll)

    @property
    def viewModel(self):
        return super(WeeklyMissions, self).getViewModel()

    @property
    def _firstWeekDay(self):
        return time_utils.WEEK_START + self.lobbyContext.getServerSettings().regionals.getWeekStartingDay()

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipData = self._getTooltipData(event)
            if tooltipData is not None:
                window = BackportTooltipWindow(tooltipData, self.getParentWindow(), event)
                window.load()
                return window
        return super(WeeklyMissions, self).createToolTip(event)

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.common.tooltips.ExtendedTextTooltip():
            text = event.getArgument('text', '')
            stringifyKwargs = event.getArgument('stringifyKwargs', '')
            return ExtendedTextTooltip(text, stringifyKwargs)
        if contentID == R.views.lobby.tooltips.AdditionalRewardsTooltip():
            showFromIndex = event.getArgument('showFromIndex')
            questId = event.getArgument('questId')
            bonuses = AdditionalRewardsTooltipModel().getBonus()
            for _, weeklyQuest in self.__weeklyQuests.iteritems():
                if weeklyQuest.getID() == questId:
                    packQuestBonusModel(weeklyQuest, getWeeklyMissionsBonusPacker(), bonuses, sort=weeklyBonusSort)

            return AdditionalRewardsTooltip(bonuses[int(showFromIndex):])
        return super(WeeklyMissions, self).createToolTipContent(event=event, contentID=contentID)

    def _onLoading(self, *_, **__):
        super(WeeklyMissions, self)._onLoading()
        self._updateModel()

    def _finalize(self):
        self.__weeklyQuests.clear()
        self.__weeklyQuests = None
        self.__acyclicNotifier.stopNotification()
        self.__acyclicNotifier.clear()
        self.__acyclicNotifier = None
        super(WeeklyMissions, self)._finalize()
        return

    def _getEvents(self):
        return ((self.viewModel.onReroll, self.__onReRoll), (self.eventsCache.onSyncCompleted, self.__onSyncCompleted), (self.lobbyContext.getServerSettings().onServerSettingsChange, self._onServerSettingsChanged))

    def _updateModel(self):
        self._rerollTimeout = getWeeklyRerollTimeout()
        with self.viewModel.transaction() as tx:
            self.__weeklyQuests = self.eventsCache.getWeeklyQuests()
            tx.setUpdateWeekDay(self._firstWeekDay)
            self.__fillWeeklyMissions(tx, self.__getQuestData(self.__weeklyQuests))

    def _getTooltipData(self, event):
        missionParam = event.getArgument('tooltipId', '')
        missionParams = missionParam.rsplit(':', 1)
        if len(missionParams) != 2:
            return
        missionId, tooltipId = missionParams
        data = self._tooltipData.get(missionId, {})
        return data.get(tooltipId)

    def __fillWeeklyMissions(self, viewModel, questData):
        missionModelList = viewModel.getMissionsList()
        self._tooltipData.clear()
        missionModelList.clear()
        questIds = questData.keys()
        for qID in sorted(questIds):
            weeklyQuest, questInfo = questData[qID]
            questId = weeklyQuest.getID()
            wmm = self.__createWeeklyMissionModel(weeklyQuest, questInfo)
            missionModelList.addViewModel(wmm)
            bonuses = sorted(weeklyQuest.getBonuses(), cmp=weeklyBonusSort)
            self._tooltipData[questId] = {}
            packQuestBonusModelAndTooltipData(getWeeklyMissionsBonusPacker(), wmm.getBonuses(), weeklyQuest, questBonuses=bonuses, tooltipData=self._tooltipData[questId])
            self.eventsCache.questsProgress.markQuestProgressAsViewed(questId)

        missionModelList.invalidate()

    def __createWeeklyMissionModel(self, weeklyQuest, questInfo):
        wmm = self.viewModel.getMissionsListType()()
        wmm.setId(weeklyQuest.getID())
        addSpecialConditions(wmm, questInfo.getMainConditionId(), questInfo.getSpecialConditionIds())
        packer = WeeklyQuestUIDataPacker(weeklyQuest)
        weeklyQuestModel = packer.pack()
        cm = findFirstConditionModel(weeklyQuestModel.bonusCondition)
        currentValue = cm.getCurrent()
        previous = currentValue - cm.getEarned()
        wmm.setCurrentProgress(currentValue)
        wmm.setTotalProgress(cm.getTotal())
        wmm.setPreviousProgress(previous)
        wmm.setIsRerollInProgress(False)
        wmm.setRerollCooldown(self._rerollTimeout)
        wmm.setTimeToNextReroll(self.__getCountdown(weeklyQuest.getID()))
        weeklyQuestModel.unbind()
        return wmm

    def __getQuestData(self, weeklyQuests):
        questData = {}
        for _, weeklyQuest in weeklyQuests.iteritems():
            questInfo = weeklyQuest.getInfo()
            questData[questInfo.id] = (weeklyQuest, questInfo)

        return questData

    def _setRerollInProgress(self, model, questId):
        wMissionsList = model.getMissionsList()
        for wMission in wMissionsList:
            if wMission.getId() == questId:
                wMission.setIsRerollInProgress(True)
                break

    def _updateCountdownsUntilNextReroll(self, model):
        self._rerollTimeout = getWeeklyRerollTimeout()
        minCountdown = sys.maxsize
        wMissionsList = model.getMissionsList()
        for wMission in wMissionsList:
            wMission.setRerollCooldown(self._rerollTimeout)
            countdown = self.__getCountdownF(wMission.getId())
            wMission.setTimeToNextReroll(int(countdown))
            if 0 < countdown < minCountdown:
                minCountdown = countdown

        self.__acyclicNotifier.stopNotification()
        if minCountdown > 0:
            self.__rerollCountdown = minCountdown
            self.__acyclicNotifier.startNotification()

    def __getCountdown(self, id):
        return int(self.__getCountdownF(id))

    def __getCountdownF(self, id):
        nextRerollTime = 0
        quests = self.eventsCache.getWeeklyQuests()
        if id in quests:
            qId = quests[id].getInfo().id
            nextRerollTime = self.eventsCache.weeklyQuests.getNextAvailableRerollTimestamp(qId)
        curTime = time_utils.getCurrentLocalServerTimestamp()
        return max(nextRerollTime - curTime, 0)

    def _onRerollTimerEnd(self):
        with self.viewModel.transaction() as tx:
            self._updateCountdownsUntilNextReroll(tx)

    def _onServerSettingsChanged(self, diff=None):
        diff = diff or {}
        if Configs.WEEKLY_QUESTS_CONFIG.value in diff:
            dqDiff = diff[Configs.WEEKLY_QUESTS_CONFIG.value]
            rerollTimeoutChanged = 'rerollTimeout' in dqDiff and dqDiff['rerollTimeout'] != self._rerollTimeout
            if rerollTimeoutChanged:
                with self.viewModel.transaction() as tx:
                    self._updateCountdownsUntilNextReroll(tx)

    def __getRerollCountdown(self):
        return self.__rerollCountdown

    def __onSyncCompleted(self, *_):
        self._updateModel()

    @decorators.adisp_process('dailyQuests/waitReroll')
    @args2params(str)
    def __onReRoll(self, questId):
        quests = self.eventsCache.getWeeklyQuests()
        if questId not in quests:
            return
        quest = quests[questId]
        result = yield weekly_quests.WeeklyQuestReroll(quest).request()
        if result.success:
            with self.viewModel.transaction() as tx:
                self._setRerollInProgress(tx, questId)
        if result.userMsg:
            SystemMessages.pushMessage(result.userMsg, type=result.sysMsgType)
