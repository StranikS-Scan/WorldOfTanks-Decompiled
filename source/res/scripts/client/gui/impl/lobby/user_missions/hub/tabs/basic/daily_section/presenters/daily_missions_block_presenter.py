# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/user_missions/hub/tabs/basic/daily_section/presenters/daily_missions_block_presenter.py
import typing
import BigWorld
from constants import DAILY_QUESTS_CONFIG, PremiumConfigs
from gui import SystemMessages
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.user_missions.hub.tabs.basic_missions.daily.daily_mission_model import DailyMissionModel
from gui.impl.gen.view_models.views.lobby.user_missions.hub.tabs.basic_missions.daily.daily_missions_block_model import DailyMissionsBlockModel
from gui.impl.gui_decorators import args2params
from gui.impl.lobby.missions.missions_helpers import needToUpdateQuestsInModelByIds, markQuestProgressAsViewed, isPremiumPlusAccount
from gui.impl.lobby.user_missions.hub.tabs.basic.daily_section.presenters.base_missions_block_presenter import BaseMissionsBlockPresenter
from gui.impl.lobby.user_missions.tooltips.daily_reroll_tooltip import DailyRerollTooltip
from gui.server_events import daily_quests
from gui.server_events.events_helpers import dailyQuestsSortFunc, isDailyQuestsEnable, isRerollEnabled, EventInfoModel, getRerollTimeout, isPremiumQuestsEnable
from gui.server_events.settings import getNewCommonEvents, visitEventsGUI
from gui.shared.utils import decorators
from helpers import dependency, time_utils
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
if typing.TYPE_CHECKING:
    from typing import List, Optional
    from gui.server_events.event_items import DailyQuest

class DailyMissionsBlockPresenter(BaseMissionsBlockPresenter[DailyMissionsBlockModel]):
    eventsCache = dependency.descriptor(IEventsCache)
    lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self):
        self._isRerollEnabled = False
        self._rerollTimerID = None
        self._rerollTimeout = 0
        self._updateHasPremiumMissions()
        super(DailyMissionsBlockPresenter, self).__init__(model=DailyMissionsBlockModel)
        return

    def update(self):
        super(DailyMissionsBlockPresenter, self).update()
        with self.viewModel.transaction() as tx:
            self._updateCountDowns(tx)

    @property
    def viewModel(self):
        return super(DailyMissionsBlockPresenter, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        return DailyRerollTooltip(self.__getCountdown(), getRerollTimeout()) if contentID == R.views.mono.user_missions.tooltips.daily_reroll_tooltip() else super(DailyMissionsBlockPresenter, self).createToolTipContent(event, contentID)

    def _updateHasPremiumMissions(self):
        self._hasPremiumMissions = isPremiumPlusAccount() and isPremiumQuestsEnable()

    def _onLoading(self, *args, **kwargs):
        super(DailyMissionsBlockPresenter, self)._onLoading()
        with self.viewModel.transaction() as tx:
            self._updateModel(tx)
            self._updateCountDowns(tx)

    def _getEvents(self):
        vm = self.viewModel
        eventsTuple = super(DailyMissionsBlockPresenter, self)._getEvents()
        return eventsTuple + ((vm.onReroll, self.__onReRoll), (self.gameSession.onPremiumTypeChanged, self._onPremiumTypeChanged), (self.lobbyContext.getServerSettings().onServerSettingsChange, self._onServerSettingsChanged))

    def _finalize(self):
        self._cancelRerollTimer()
        super(DailyMissionsBlockPresenter, self)._finalize()

    def _updateModel(self, model, fullUpdate=False):
        self._isBlockEnabled = isDailyQuestsEnable()
        if not self._isBlockEnabled:
            return
        quests = sorted(self.eventsCache.getDailyQuests().values(), key=dailyQuestsSortFunc)
        with model.transaction() as tx:
            questIdsInModel = [ q.getId() for q in tx.getMissionsList() ]
            questIdsInModel.append(tx.bonusMission.getId())
            if not fullUpdate:
                newBonusQuests = getNewCommonEvents([ q for q in quests if q.isBonus() ])
                premiumQuests = self.eventsCache.getPremiumQuests().values()
                if not needToUpdateQuestsInModelByIds(quests + newBonusQuests + premiumQuests, questIdsInModel):
                    return
            self._isRerollEnabled = isRerollEnabled()
            self.__fillDailyMissions(tx, quests)

    def _markQuestsAsVisited(self):
        seenQuests = self.eventsCache.getDailyQuests().values()
        markQuestProgressAsViewed(seenQuests)
        visitEventsGUI(seenQuests)

    def _onSyncCompleted(self, *_):
        with self.viewModel.transaction() as tx:
            self._updateModel(tx)
        super(DailyMissionsBlockPresenter, self)._onSyncCompleted(*_)

    def _disableCompletedQuestAnimation(self, vm):
        super(DailyMissionsBlockPresenter, self)._disableCompletedQuestAnimation(vm)
        bmm = vm.bonusMission
        bmm.setAnimateCompletion(False)
        bmm.setEarned(0)

    def __fillDailyMissions(self, vm, quests):
        bonusQuest = None
        allMissionsCompleted = True
        missionsList = vm.getMissionsList()
        for m in missionsList:
            self._tooltipData.pop(m.getId(), None)

        missionsList.clear()
        for quest in quests:
            if quest.isBonus():
                bonusQuest = quest
                continue
            mm = DailyMissionModel()
            isCompleted = self._fillMissionModel(mm, quest)
            allMissionsCompleted &= isCompleted
            mm.setIsRerollEnabled(self._isRerollEnabled)
            missionsList.addViewModel(mm)

        missionsList.invalidate()
        bonusQuestAvailable = bonusQuest is not None
        bmm = vm.bonusMission
        self._tooltipData.pop(bmm.getId(), None)
        if bonusQuestAvailable:
            bmm.getBonuses().clear()
            isCompleted = self._fillMissionModel(bmm, bonusQuest)
            allMissionsCompleted &= isCompleted
        else:
            allMissionsCompleted = False
            bmm.setId(DailyMissionsBlockModel.BONUS_CARD_DEFAULT_ID)
            bmm.setIsCompleted(False)
            bmm.setAnimateCompletion(False)
            bmm.setTotalProgress(0)
            bmm.setEarned(0)
        bmm.setIsAvailable(bonusQuestAvailable)
        self._updateHasPremiumMissions()
        allMissionsCompleted &= self._arePremiumDailyMissionsCompleted()
        vm.setAreAllMissionsCompleted(allMissionsCompleted)
        return

    def _updateCountDowns(self, model):
        self._updateCountdownUntilNextDay(model)
        self._updateCountdownUntilNextReroll(model)

    def _updateCountdownUntilNextDay(self, model):
        dailyResetTimeDelta = EventInfoModel.getDailyProgressResetTimeDelta()
        model.setTimeToMissionsUpdate(int(dailyResetTimeDelta))

    def _updateCountdownUntilNextReroll(self, model):
        self._rerollTimeout = getRerollTimeout()
        cd = self.__getCountdownF()
        with model.transaction() as tx:
            tx.setTimeToNextRerol(int(cd))
        self._cancelRerollTimer()
        if cd > 0:
            self._rerollTimerID = BigWorld.callback(cd, self._onRerollTimerEnd)

    def _updateRerollEnabled(self, model):
        self._isRerollEnabled = isRerollEnabled()
        ml = model.getMissionsList()
        for m in ml:
            m.setIsRerollEnabled(self._isRerollEnabled)

    def _cancelRerollTimer(self):
        if self._rerollTimerID is not None:
            BigWorld.cancelCallback(self._rerollTimerID)
            self._rerollTimerID = None
        return

    def __getCountdown(self):
        return int(self.__getCountdownF())

    def __getCountdownF(self):
        nextRerollTime = self.eventsCache.dailyQuests.getNextAvailableRerollTimestamp()
        curTime = time_utils.getCurrentLocalServerTimestamp()
        return max(nextRerollTime - curTime, 0)

    def _onServerSettingsChanged(self, diff=None):
        diff = diff or {}
        if DAILY_QUESTS_CONFIG in diff:
            dqDiff = diff[DAILY_QUESTS_CONFIG]
            rerollStateChanged = 'rerollEnabled' in dqDiff and dqDiff['rerollEnabled'] is not self._isRerollEnabled
            stateChanged = 'enabled' in dqDiff and dqDiff['enabled'] is not self._isBlockEnabled
            rerollTimeoutChanged = 'rerollTimeout' in dqDiff and dqDiff['rerollTimeout'] != self._rerollTimeout
            with self.viewModel.transaction() as tx:
                if rerollStateChanged:
                    self._updateRerollEnabled(tx)
                if rerollTimeoutChanged:
                    self._updateCountdownUntilNextReroll(tx)
                if stateChanged:
                    self._updateModel(tx)
        if PremiumConfigs.PREM_QUESTS in diff:
            premDiff = diff[PremiumConfigs.PREM_QUESTS]
            stateChanged = 'enabled' in premDiff and premDiff['enabled'] is not self._hasPremiumMissions
            if stateChanged:
                with self.viewModel.transaction() as tx:
                    self._updateModel(tx, fullUpdate=True)

    def _onRerollTimerEnd(self):
        self._rerollTimerID = None
        with self.viewModel.transaction() as tx:
            tx.setTimeToNextRerol(0)
        return

    def _arePremiumDailyMissionsCompleted(self):
        if not self._hasPremiumMissions:
            return True
        for quest in self.eventsCache.getPremiumQuests().itervalues():
            if not quest.isCompleted():
                return False

        return True

    def _onPremiumTypeChanged(self, *_):
        with self.viewModel.transaction() as tx:
            self._updateModel(tx, fullUpdate=True)

    @decorators.adisp_process('dailyQuests/waitReroll')
    @args2params(str)
    def __onReRoll(self, questId):
        quests = self.eventsCache.getDailyQuests()
        if questId not in quests:
            return
        quest = quests[questId]
        result = yield daily_quests.DailyQuestReroll(quest).request()
        if result.success:
            with self.viewModel.transaction() as tx:
                self._updateCountdownUntilNextReroll(tx)
        if result.userMsg:
            SystemMessages.pushMessage(result.userMsg, type=result.sysMsgType)
