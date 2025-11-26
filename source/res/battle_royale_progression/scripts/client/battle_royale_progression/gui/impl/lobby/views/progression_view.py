# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale_progression/scripts/client/battle_royale_progression/gui/impl/lobby/views/progression_view.py
from battle_royale_progression.gui.impl.gen.view_models.views.lobby.views.progression.progress_level_model import ProgressLevelModel
from battle_royale_progression.gui.impl.gen.view_models.views.lobby.views.progression.progression_view_model import ProgressionViewModel, ProgressionState
from battle_royale_progression.gui.impl.lobby.views.bonus_packer import getBonusPacker
from battle_royale_progression.gui.impl.lobby.views.quests_packer import getEventUIDataPacker
from battle_royale_progression.skeletons.game_controller import IBRProgressionOnTokensController
from frameworks.wulf.view.submodel_presenter import SubModelPresenter
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.battle_pass.battle_pass_bonuses_packers import packBonusModelAndTooltipData
from gui.impl.backport import createTooltipData
from gui.impl.lobby.common.view_wrappers import createBackportTooltipDecorator
from gui.impl.lobby.missions.missions_helpers import needToUpdateQuestsInModel
from gui.server_events.events_helpers import EventInfoModel
from gui.shared import event_dispatcher
from gui.shared.utils.scheduled_notifications import SimpleNotifier
from helpers import dependency, time_utils
from helpers.time_utils import ONE_DAY, ONE_MINUTE
from skeletons.gui.game_control import IBattleRoyaleController
from skeletons.gui.server_events import IEventsCache

class ProgressionView(SubModelPresenter):
    battleRoyale = dependency.descriptor(IBattleRoyaleController)
    brProgression = dependency.descriptor(IBRProgressionOnTokensController)
    eventsCache = dependency.descriptor(IEventsCache)
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

    @createBackportTooltipDecorator()
    def createToolTip(self, event):
        return super(ProgressionView, self).createToolTip(event)

    def getTooltipData(self, event):
        tooltipId = event.getArgument('tooltipId')
        if tooltipId is None:
            return
        else:
            return createTooltipData(specialAlias=tooltipId, isSpecial=True, specialArgs=(None,)) if tooltipId == TOOLTIPS_CONSTANTS.BATTLE_ROYALE_SELECTOR_CALENDAR_INFO else self.__tooltipData.get(tooltipId)

    def initialize(self, *args, **kwargs):
        super(ProgressionView, self).initialize(args, kwargs)
        self.__updateModel()

    def finalize(self):
        self.__stopNotification()
        super(ProgressionView, self).finalize()

    def _getEvents(self):
        return ((self.viewModel.onClose, self.__onClose),
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
        self.__restartNotifier(self._UPDATE_TIMER_DELAY)
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
        curPoints = self.brProgression.getCurPoints()
        with self.viewModel.transaction() as model:
            state = ProgressionState.COMPLETED if self.brProgression.isFinished else ProgressionState.INPROGRESS
            model.setState(state)
            model.setCurProgressPoints(curPoints)

    def __updateModel(self):
        if not self.brProgression.isEnabled:
            return
        data = self.brProgression.getProgressionData()
        pointsData = self.brProgression.getProgessionPointsData()
        with self.viewModel.transaction() as model:
            state = ProgressionState.COMPLETED if self.brProgression.isFinished else ProgressionState.INPROGRESS
            model.setState(state)
            model.setStartTimestamp(self.battleRoyale.getStartTime())
            model.setEndTimestamp(self.battleRoyale.getEndTime())
            model.setCalendarTooltipId(TOOLTIPS_CONSTANTS.BATTLE_ROYALE_SELECTOR_CALENDAR_INFO)
            self.__updateBattleQuestsCards(model.battleQuests, data)
            self.__updateProgression(data, pointsData, model)
            self.__updateMissionVisitedArray(model.battleQuests.getMissionsCompletedVisited(), data['battleQuests'].keys())
            self.__markAsVisited(data)

    def __updateProgression(self, data, pointsData, model):
        progressionLevelsList = data['progressionLevels']
        totalLevels = len(progressionLevelsList)
        model.setCurProgressPoints(pointsData['curPoints'])
        model.setPrevProgressPoints(pointsData['prevPoints'])
        if totalLevels > 0:
            model.setPointsForLevel(int(pointsData['totalPoints'] / totalLevels))
        progressionLevels = model.getProgressLevels()
        progressionLevels.clear()
        for levelData in progressionLevelsList:
            level = ProgressLevelModel()
            rewards = level.getRewards()
            bonuses = levelData['rewards']
            packBonusModelAndTooltipData(bonuses, rewards, self.__tooltipData, getBonusPacker())
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
        questsTimer = self.battleRoyale.getQuestsTimerLeft()
        if questsTimer < 0:
            battleQuestsModel.setShowEventEnded(True)
            self.__stopNotification()
        dailyQuestProgressDelta = EventInfoModel.getDailyProgressResetTimeDelta()
        currentCycleEndTime = self.battleRoyale.getEndTime()
        currServerTime = time_utils.getCurrentLocalServerTimestamp()
        cycleTimeLeft = currentCycleEndTime - currServerTime
        isShowPrimeTime = cycleTimeLeft < ONE_DAY and cycleTimeLeft < dailyQuestProgressDelta
        battleQuestsModel.setCurrentTimerDate(questsTimer)
        battleQuestsModel.setShowPrimeTime(isShowPrimeTime)
        self.__restartNotifier(questsTimer + (self._UPDATE_TIMER_DELAY if questsTimer > 0 else 0))

    def __markAsVisited(self, data):
        for seenQuestID in data['battleQuests'].keys():
            self.eventsCache.questsProgress.markQuestProgressAsViewed(seenQuestID)
