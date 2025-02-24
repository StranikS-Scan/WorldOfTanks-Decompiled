# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale_progression/scripts/client/battle_royale_progression/gui/impl/lobby/views/progression_view.py
from gui.impl.gen.resources import R
from battle_royale.gui.impl.lobby.tooltips.proxy_currency_tooltip_view import ProxyCurrencyTooltipView
from battle_royale_progression.gui.impl.gen.view_models.views.lobby.views.progression.progress_level_model import ProgressLevelModel
from battle_royale_progression.gui.impl.gen.view_models.views.lobby.views.progression.progression_view_model import ProgressionViewModel
from battle_royale_progression.gui.impl.lobby.views.bonus_packer import getBonusPacker
from battle_royale_progression.gui.impl.lobby.views.quests_packer import getEventUIDataPacker
from battle_royale_progression.skeletons.game_controller import IBRProgressionOnTokensController
from frameworks.wulf.view.submodel_presenter import SubModelPresenter
from gui.battle_pass.battle_pass_bonuses_packers import packBonusModelAndTooltipData
from gui.impl.lobby.common.view_wrappers import createBackportTooltipDecorator
from gui.impl.lobby.missions.missions_helpers import needToUpdateQuestsInModel
from gui.periodic_battles.models import PrimeTimeStatus
from gui.server_events.events_helpers import EventInfoModel
from gui.shared import event_dispatcher
from gui.shared.utils.scheduled_notifications import SimpleNotifier
from helpers import dependency, time_utils
from helpers.time_utils import ONE_DAY, getTimeDeltaFromNow, ONE_MINUTE
from skeletons.connection_mgr import IConnectionManager
from skeletons.gui.game_control import IBattleRoyaleController
from skeletons.gui.server_events import IEventsCache

class ProgressionView(SubModelPresenter):
    battleRoyale = dependency.descriptor(IBattleRoyaleController)
    brProgression = dependency.descriptor(IBRProgressionOnTokensController)
    eventsCache = dependency.descriptor(IEventsCache)
    connectionMgr = dependency.descriptor(IConnectionManager)
    _UPDATE_TIMER_DELAY = ONE_MINUTE
    __slots__ = ('__tooltipData', '__notifier')

    def __init__(self, viewModel, parentView):
        super(ProgressionView, self).__init__(viewModel, parentView)
        self.__tooltipData = {}
        self.__notifier = None
        return

    @property
    def viewModel(self):
        return super(ProgressionView, self).getViewModel()

    def getParentWindow(self):
        return self.parentView.getParentWindow()

    def createToolTipContent(self, event, contentID):
        return ProxyCurrencyTooltipView() if contentID == R.views.battle_royale.lobby.tooltips.ProxyCurrencyTooltipView() else super(ProgressionView, self).createToolTipContent(event, contentID)

    @createBackportTooltipDecorator()
    def createToolTip(self, event):
        return super(ProgressionView, self).createToolTip(event)

    def getTooltipData(self, event):
        tooltipId = event.getArgument('tooltipId')
        return None if tooltipId is None else self.__tooltipData.get(tooltipId)

    def initialize(self, *args, **kwargs):
        super(ProgressionView, self).initialize(args, kwargs)
        self.__updateModel()

    def finalize(self):
        self.brProgression.saveCurPoints()
        self.__stopNotification()
        super(ProgressionView, self).finalize()

    def _getEvents(self):
        return ((self.viewModel.onClose, self.__onClose),
         (self.viewModel.onAboutClicked, self.__onAboutClicked),
         (self.brProgression.onProgressPointsUpdated, self.__updateProgressionPoints),
         (self.brProgression.onSettingsChanged, self.__updateModel),
         (self.eventsCache.onSyncCompleted, self.__onSyncCompleted))

    def __restartNotifier(self, updateTime):
        self.__stopNotification()
        self.__notifier = SimpleNotifier(lambda : updateTime, self.__updateQuestTimer)
        self.__notifier.startNotification()

    def __stopNotification(self):
        if self.__notifier is not None:
            self.__notifier.stopNotification()
            self.__notifier.clear()
            self.__notifier = None
        return

    def __onClose(self):
        event_dispatcher.showHangar()

    def __onAboutClicked(self):
        self.battleRoyale.openInfoPageWindow()

    def __updateQuestTimer(self):
        with self.viewModel.transaction() as model:
            self.__setBattleQuestTimeLeft(model.battleQuests)

    def __updateMissionVisitedArray(self, missionVisitedArray, questsIDs):
        missionVisitedArray.clear()
        missionVisitedArray.reserve(len(questsIDs))
        for questID in questsIDs:
            missionCompletedVisited = not self.eventsCache.questsProgress.getQuestCompletionChanged(questID)
            missionVisitedArray.addBool(missionCompletedVisited)

        missionVisitedArray.invalidate()

    def __onSyncCompleted(self, *_):
        if not self.brProgression.isEnabled:
            return
        data = self.brProgression.getProgressionData()
        battleQuests = data['battleQuests']
        isNeedToUpdate = needToUpdateQuestsInModel(battleQuests.values(), self.viewModel.battleQuests.getTasksBattle())
        if not isNeedToUpdate:
            return
        with self.viewModel.transaction() as model:
            self.__updateBattleQuestsCards(model.battleQuests, data)
            self.__updateMissionVisitedArray(model.battleQuests.getMissionsCompletedVisited(), battleQuests.keys())
            self.__markAsVisited(data)

    def __updateProgressionPoints(self):
        if not self.brProgression.isEnabled:
            return
        data = self.brProgression.getProgessionPointsData()
        with self.viewModel.transaction() as model:
            model.setCurProgressPoints(data['curPoints'])

    def __updateModel(self):
        if not self.brProgression.isEnabled:
            return
        data = self.brProgression.getProgressionData()
        with self.viewModel.transaction() as model:
            self.__updateBattleQuestsCards(model.battleQuests, data)
            self.__updateProgression(data, model)
            self.__updateMissionVisitedArray(model.battleQuests.getMissionsCompletedVisited(), data['battleQuests'].keys())
            self.__markAsVisited(data)

    def __updateProgression(self, data, model):
        model.setCurProgressPoints(data['curPoints'])
        model.setPrevProgressPoints(data['prevPoints'])
        model.setPointsForLevel(data['pointsForLevel'])
        progressionLevels = model.getProgressLevels()
        progressionLevels.clear()
        packer = getBonusPacker()
        for levelData in data['progressionLevels']:
            level = ProgressLevelModel()
            rewards = level.getRewards()
            bonuses = levelData['rewards']
            packBonusModelAndTooltipData(bonuses, rewards, self.__tooltipData, packer)
            progressionLevels.addViewModel(level)

        progressionLevels.invalidate()

    def __updateBattleQuestsCards(self, battleQuestsModel, data):
        self.__setBattleQuestTimeLeft(battleQuestsModel)
        questsList = battleQuestsModel.getTasksBattle()
        questsList.clear()
        bonusIndexTotal = len(self.__tooltipData)
        for _, quest in data['battleQuests'].items():
            packer = getEventUIDataPacker(quest)
            questModels = packer.pack()
            bonusTooltipList = packer.getTooltipData()
            for bonusIndex, item in enumerate(questModels.getBonuses()):
                tooltipIdx = str(bonusIndexTotal)
                item.setTooltipId(tooltipIdx)
                if bonusTooltipList:
                    self.__tooltipData[tooltipIdx] = bonusTooltipList[str(bonusIndex)]
                bonusIndexTotal += 1

            questsList.addViewModel(questModels)

        questsList.invalidate()

    def __setBattleQuestTimeLeft(self, battleQuestsModel):
        status, primeTimeLeft, _ = self.battleRoyale.getPrimeTimeStatus()
        if primeTimeLeft == 0 and status in (PrimeTimeStatus.NOT_AVAILABLE, PrimeTimeStatus.NOT_SET, PrimeTimeStatus.FROZEN):
            battleQuestsModel.setShowEventEnded(True)
            self.__stopNotification()
            return
        timerDate, isShowPrimeTime = self.__getTimerData()
        battleQuestsModel.setCurrentTimerDate(timerDate)
        battleQuestsModel.setShowPrimeTime(isShowPrimeTime)
        self.__restartNotifier(timerDate + (self._UPDATE_TIMER_DELAY if timerDate > 0 else 0))

    def __getTimerData(self):
        dailyQuestProgressDelta = EventInfoModel.getDailyProgressResetTimeDelta()
        currentCycleEndTime = self.battleRoyale.getEndTime()
        currServerTime = time_utils.getCurrentLocalServerTimestamp()
        cycleTimeLeft = currentCycleEndTime - currServerTime
        isShowPrimeTime = False
        if cycleTimeLeft < ONE_DAY and cycleTimeLeft < dailyQuestProgressDelta:
            primeTime = self.battleRoyale.getPrimeTimes().get(self.connectionMgr.peripheryID)
            lastPrimeTimeEnd = max([ period[1] for period in primeTime.getPeriodsBetween(int(currServerTime), currentCycleEndTime) ])
            dailyQuestProgressDelta = getTimeDeltaFromNow(lastPrimeTimeEnd)
            isShowPrimeTime = True
        return (dailyQuestProgressDelta, isShowPrimeTime)

    def __markAsVisited(self, data):
        for seenQuestID in data['battleQuests'].keys():
            self.eventsCache.questsProgress.markQuestProgressAsViewed(seenQuestID)
