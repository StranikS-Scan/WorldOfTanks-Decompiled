# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/dragon_boat/dragon_boat_entry_point.py
from functools import partial
from account_helpers import AccountSettings
from account_helpers.AccountSettings import DBOAT_INTRO_SCREEN_SHOWN
from account_helpers.settings_core.settings_constants import DragonBoatStorageKeys
from frameworks.wulf import ViewSettings
from frameworks.wulf.gui_constants import ViewFlags
from gui.Scaleform import MENU
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor
from gui.Scaleform.genConsts.MISSIONS_STATES import MISSIONS_STATES
from gui.game_control.dragon_boat_controller import DBOAT_WEEKLY_QUEST, DragonBoatState
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.dragon_boat.dragon_boat_entry_point_model import DragonBoatEntryPointModel
from gui.impl.pub import ViewImpl
from gui.server_events.events_dispatcher import showDragonBoatTab
from gui.server_events.events_helpers import EventInfoModel
from gui.shared.event_dispatcher import showDragonBoatIntroWindow
from gui.shared.missions.packers.events import findFirstConditionModel, DailyQuestUIDataPacker
from gui.shared.utils.scheduled_notifications import Notifiable, PeriodicNotifier
from helpers import dependency, time_utils
from skeletons.account_helpers.settings_core import ISettingsCore, ISettingsCache
from skeletons.gui.game_control import IDragonBoatController
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from skeletons.gui.lobby_context import ILobbyContext

@dependency.replace_none_kwargs(dragonBoatCtrl=IDragonBoatController)
def isDragonBoatEntryPointAvailable(dragonBoatCtrl=None):
    return dragonBoatCtrl.isAvailable()


class DragonBoatEntrancePointInjectWidget(InjectComponentAdaptor):

    def _makeInjectView(self):
        return DragonBoatEntrancePointWidget()


class DragonBoatEntrancePointWidget(ViewImpl, Notifiable):
    settingsCore = dependency.descriptor(ISettingsCore)
    itemsCache = dependency.descriptor(IItemsCache)
    lobbyContext = dependency.descriptor(ILobbyContext)
    eventsCache = dependency.descriptor(IEventsCache)
    dragonBoatCtrl = dependency.descriptor(IDragonBoatController)
    settingsCache = dependency.descriptor(ISettingsCache)
    __slots__ = ('__skipClicks',)

    def __init__(self):
        settings = ViewSettings(R.views.lobby.dragon_boats.EntryPoint())
        settings.flags = ViewFlags.COMPONENT
        settings.model = DragonBoatEntryPointModel()
        super(DragonBoatEntrancePointWidget, self).__init__(settings)
        self.__skipClicks = False

    @property
    def viewModel(self):
        return super(DragonBoatEntrancePointWidget, self).getViewModel()

    def _initialize(self):
        super(DragonBoatEntrancePointWidget, self)._initialize()
        self.__skipClicks = False
        self.viewModel.onWidgetClick += self._onWidgetClick
        self.itemsCache.onSyncCompleted += self.__onUpdate
        self.eventsCache.onProgressUpdated += self.__onUpdate
        self.lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingChanged
        self.addNotificators(PeriodicNotifier(self.__getUpdatePeriod, self.__onNotifierTriggered, periods=(time_utils.ONE_MINUTE,)))
        self.startNotification()

    def _finalize(self):
        self.clearNotification()
        self.viewModel.onWidgetClick -= self._onWidgetClick
        self.itemsCache.onSyncCompleted -= self.__onUpdate
        self.eventsCache.onProgressUpdated -= self.__onUpdate
        self.lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingChanged
        super(DragonBoatEntrancePointWidget, self)._finalize()

    def _onLoading(self, *args, **kwargs):
        super(DragonBoatEntrancePointWidget, self)._onLoading(*args, **kwargs)
        self.__onUpdate()

    def _onWidgetClick(self, _=None):
        if self.__skipClicks or self.dragonBoatCtrl.isFinalRewardInProcess():
            return
        state = self.dragonBoatCtrl.getState()
        dbStorage = dict()
        if self.settingsCore.isReady and self.settingsCache.isSynced():
            dbStorage = self.settingsCore.serverSettings.getDragonBoatStorage()
        if state == DragonBoatState.ENDED and not dbStorage.get(DragonBoatStorageKeys.DBOAT_FINAL_REWARD_OBTAINED, True):
            self.__skipClicks = True
            self.dragonBoatCtrl.processFinalReward()
            return
        finishTeam = self.dragonBoatCtrl.checkFinishScreenToShow()
        if finishTeam:
            self.dragonBoatCtrl.showFinishScreen(finishTeam)
            return
        if not AccountSettings.getSettings(DBOAT_INTRO_SCREEN_SHOWN):
            showDragonBoatIntroWindow(closeCallback=showDragonBoatTab)
            return
        showDragonBoatTab()

    def __onUpdate(self, *_):
        if self.dragonBoatCtrl.isAvailable():
            with self.viewModel.transaction() as tx:
                state = self.dragonBoatCtrl.getState()
                team = self.dragonBoatCtrl.getTeam()
                if state == DragonBoatState.FINISHED:
                    team = self.dragonBoatCtrl.checkFinishScreenToShow()
                newCountdownVal = EventInfoModel.getDailyProgressResetTimeDelta() + time_utils.ONE_MINUTE
                dailyQuestName = self.dragonBoatCtrl.getDailyQuestName()
                if dailyQuestName is not None:
                    dailyQuest = self.eventsCache.getHiddenQuests(partial(self.__filterFunc, postfix=dailyQuestName or '')).values()
                    quest = dailyQuest[0] if dailyQuest else None
                    if quest:
                        self._updateQuestModel(tx, quest, dayQuestModel=True)
                weeklyQuest = self.eventsCache.getHiddenQuests(partial(self.__filterFunc, postfix=DBOAT_WEEKLY_QUEST)).values()
                isWeekQuestDone = False
                for quest in weeklyQuest:
                    isWeekQuestDone = quest.isCompleted()
                    self._updateQuestModel(tx, quest, dayQuestModel=False)

                isDayQuestDone = self.dragonBoatCtrl.isDayQuestCompleted()
                isDayQuestObtained = dailyQuestName is not None or isDayQuestDone
                if time_utils.getCurrentLocalServerTimestamp() + time_utils.ONE_DAY >= self.dragonBoatCtrl.getLastDayOfEvent() and isDayQuestDone:
                    isDayQuestObtained = False
                tx.setState(state)
                tx.setTeam(team)
                tx.setIsDayQuestDone(isDayQuestDone)
                tx.setIsWeekQuestDone(isWeekQuestDone)
                tx.setIsDayQuestObtained(isDayQuestObtained)
                if isDayQuestDone:
                    tx.setTimeTillNextDayUpdate(newCountdownVal)
                    formattedTimeTillNextUpdate = time_utils.getTillTimeString(newCountdownVal, MENU.TIME_TIMEVALUESHORT)
                    tx.setFormattedTimeTillNextUpdate(formattedTimeTillNextUpdate)
        return

    def _updateQuestModel(self, baseModel, quest, dayQuestModel=False):
        tr = baseModel.progressDay if dayQuestModel else baseModel.progressWeek
        questUIPacker = DailyQuestUIDataPacker(quest)
        fullQuestModel = questUIPacker.pack()
        preFormattedConditionModel = self._getFirstConditionModelFromQuestModel(fullQuestModel)
        with tr.transaction() as tx:
            current = preFormattedConditionModel.getCurrent()
            total = preFormattedConditionModel.getTotal()
            if current == total == 0:
                total = 1
            tx.setCurrentProgress(current)
            tx.setTotalProgress(total)
            tx.setEarned(preFormattedConditionModel.getEarned())
            tx.setDescription(preFormattedConditionModel.getDescrData())
            tx.setId(fullQuestModel.getId())
            tx.setIcon(fullQuestModel.getIcon())
            tx.setCompleted(fullQuestModel.getStatus() == MISSIONS_STATES.COMPLETED)
        fullQuestModel.unbind()

    @classmethod
    def _getFirstConditionModelFromQuestModel(cls, dailyQuestModel):
        postBattleModel = findFirstConditionModel(dailyQuestModel.postBattleCondition)
        bonusConditionModel = findFirstConditionModel(dailyQuestModel.bonusCondition)
        return postBattleModel if postBattleModel else bonusConditionModel

    def __onServerSettingChanged(self, diff):
        if 'dragon_boat_config' in diff:
            self.__onUpdate()

    def __filterFunc(self, q, postfix=''):
        return q.getID().startswith(postfix)

    def __getUpdatePeriod(self):
        return time_utils.ONE_MINUTE if self.dragonBoatCtrl.isAvailable() else 0

    def __onNotifierTriggered(self):
        self.__onUpdate()
