# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: advent_calendar/scripts/client/advent_calendar/gui/impl/lobby/feature/main_view.py
import json
import logging
import time
import BigWorld
from account_helpers.AccountSettings import AdventCalendar
from adisp import adisp_process
from advent_calendar.gui.feature.constants import ADVENT_CALENDAR_TOKEN
from advent_calendar.gui.impl.gen.view_models.views.lobby.components.advent_calendar_events import EventType
from advent_calendar.gui.impl.gen.view_models.views.lobby.door_view_model import DoorViewModel, DoorState, Mark
from advent_calendar.gui.impl.gen.view_models.views.lobby.main_view_model import StatePhase, MainViewModel
from advent_calendar.gui.impl.gen.view_models.views.lobby.progression_reward_item_view_model import ProgressionState
from advent_calendar.gui.impl.lobby.feature.advent_calendar_optimization import AdventWindowOptimizationManager, AdventWindowOptimizationSettings, AdventWindowOptimizationProcessorSettings
from advent_calendar.gui.impl.lobby.feature.advent_helper import getQuestNeededTokensCount, getAccountTokensAmount, isAdventAnimationEnabled, getAdventCalendarSetting, getDoorState, pushOpenDoorFailedError, getFirstClosedDayID, setAdventCalendarSetting, getHolidayOpsStartTime
from advent_calendar.gui.impl.lobby.feature.container_view import AdventCalendarContainerView
from advent_calendar.gui.impl.lobby.feature.progression_reward_packers import getProgressionBonusPacker
from advent_calendar.gui.impl.lobby.feature.sound_helper import ADVENT_CALENDAR_MAIN_WINDOW_SOUND
from advent_calendar.gui.impl.lobby.feature.tooltips.advent_calendar_all_rewards_tooltip import AdventCalendarAllRewardsTooltip
from advent_calendar.gui.impl.lobby.feature.tooltips.advent_calendar_big_lootbox_tooltip import AdventCalendarBigLootBoxTooltip
from advent_calendar.gui.shared.event_dispatcher import showAdventCalendarIntroWindow, showRewardWindow
from advent_calendar.gui.shared.events import AdventCalendarEvent
from advent_calendar.skeletons.game_controller import IAdventCalendarController
from advent_calendar_common.advent_calendar_constants import DoorMarkType
from frameworks.wulf import ViewFlags, ViewSettings, WindowFlags, WindowLayer
from gui.game_control.links import URLMacros
from gui.impl.backport import TooltipData
from gui.impl.gen import R
from gui.impl.gui_decorators import args2params
from gui.impl.lobby.common.view_wrappers import createBackportTooltipDecorator
from gui.impl.pub.lobby_window import LobbyWindow
from gui.shared import EVENT_BUS_SCOPE
from helpers import dependency
from shared_utils import nextTick, first
from wg_async import wg_await, wg_async, AsyncScope, AsyncEvent, BrokenPromiseError, TimeoutError, delay
_logger = logging.getLogger(__name__)
CONFIG_TO_MODEL_MARK_MAP = {DoorMarkType.NY_START: Mark.NY,
 DoorMarkType.NY_MODE: Mark.NY_EVENT,
 DoorMarkType.WDR: Mark.WDR,
 DoorMarkType.NONE: Mark.NONE}
QUEST_COMPLETED_TIMEOUT = 20

def predictionFunction(window):
    return not isinstance(window.content, AdventCalendarMainView)


ADVENT_CALENDAR_OPTIMIZATION_SETTINGS = AdventWindowOptimizationSettings(disableWindowsVisibility=True, windowOptimizationProcessorSettings=AdventWindowOptimizationProcessorSettings(windowsVisibilityPredicateFunction=predictionFunction))
_INVALID_IDX = -1

class AdventCalendarMainView(AdventCalendarContainerView):
    __adventController = dependency.descriptor(IAdventCalendarController)
    _COMMON_SOUND_SPACE = ADVENT_CALENDAR_MAIN_WINDOW_SOUND
    __UPDATE_DOOR_ANIMATION_DELTA_TIME = 2
    __OPEN_DOOR_ANIM_TIME = 3

    def __init__(self):
        settings = ViewSettings(R.views.advent_calendar.lobby.feature.MainView(), flags=ViewFlags.VIEW, model=MainViewModel())
        self.__tooltips = {}
        self.__progressionRewardInProgressIdx = _INVALID_IDX
        self.__selectedDayId = 0
        self.__lastHighlightDoorAnimTime = 0
        self.__lasOpenDoorTime = 0
        self.__waitSuccessfulOpenDoor = False
        self._optimizationManager = AdventWindowOptimizationManager(settings=ADVENT_CALENDAR_OPTIMIZATION_SETTINGS)
        self.__scope = AsyncScope()
        self.__doorOpenedQuestCompletedEvent = AsyncEvent(scope=self.__scope)
        super(AdventCalendarMainView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(AdventCalendarMainView, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.advent_calendar.lobby.feature.tooltips.AdventCalendarAllRewardsTooltip():
            if self.__adventController.isAvailableAndActivePhase():
                return AdventCalendarAllRewardsTooltip()
        elif contentID == R.views.advent_calendar.lobby.feature.tooltips.AdventCalendarBigLootBoxTooltip():
            return AdventCalendarBigLootBoxTooltip()
        return super(AdventCalendarMainView, self).createToolTipContent(event, contentID)

    @createBackportTooltipDecorator()
    def createToolTip(self, event):
        return super(AdventCalendarMainView, self).createToolTip(event)

    def getTooltipData(self, event):
        tooltipId = event.getArgument('tooltipId')
        return None if tooltipId is None else self.__tooltips.get(tooltipId)

    def _getEvents(self):
        return ((self.viewModel.onClose, self.__onClose),
         (self.viewModel.onOpenDoorAnimStarted, self.__onOpenDoorAnimStarted),
         (self.viewModel.onOpenDoorAnimEnded, self.__onOpenDoorAnimEnded),
         (self.viewModel.progressionRewards.onProgressionRewardCompleted, self.__showProgressionRewardWindow),
         (self.viewModel.onShowPurchaseDialog, self.__onShowPurchaseDialogWindow),
         (self.viewModel.onAnimationCompleted, self.__onProgressionAnimationCompleted),
         (self.viewModel.onInfoClick, self.__onInfoClick),
         (self.viewModel.onOpenDownloadLink, self.__onOpenDownloadLink),
         (self.__adventController.onNewDayStarted, self.__onNewDayStarted),
         (self.__adventController.onConfigChanged, self.__onSettingsChange),
         (self.__adventController.onDoorOpened, self.__onDoorOpened))

    def _getListeners(self):
        return ((AdventCalendarEvent.PROGRESSION_REWARD_VIEWED, self.__updateProgressionRewards, EVENT_BUS_SCOPE.LOBBY), (AdventCalendarEvent.CHANGE_BLUR_STATUS, self.__changeBlurState, EVENT_BUS_SCOPE.LOBBY), (AdventCalendarEvent.INTRO_CLOSE_STARTED, self.__onIntroCloseStarted, EVENT_BUS_SCOPE.LOBBY))

    def _onLoading(self, *args, **kwargs):
        super(AdventCalendarMainView, self)._onLoading(*args, **kwargs)
        self.__updateModel()
        if not getAdventCalendarSetting(AdventCalendar.INTRO_SHOWN):
            self.__openIntro(isFirstTime=True)
        self._optimizationManager.start()

    def _finalize(self):
        self._optimizationManager.fini()
        self.__doorOpenedQuestCompletedEvent.clear()
        self.__scope.destroy()
        self.__completedProgressionRewardsIdx = _INVALID_IDX
        self.__selectedDayId = 0
        self.__waitSuccessfulOpenDoor = False
        super(AdventCalendarMainView, self)._finalize()

    def _registerSubModels(self):
        return []

    def __updateModel(self):
        with self.viewModel.transaction() as tx:
            if tx.getDoorOpenBlocked():
                _logger.debug('Advent calendar window is locked for updates')
                return
            phase = self.__getPhaseState()
            if not self.__adventController.isAvailable() or not phase:
                return self.destroyWindow()
            config = self.__adventController.config
            tx.setStatePhase(phase)
            tx.setStartTime(config.startDate)
            tx.setPostEventStartDate(config.postEventStartDate)
            tx.setPostEventEndDate(config.postEventEndDate)
            tx.setHolidayOpsStartTime(getHolidayOpsStartTime(adventController=self.__adventController))
            tx.setDoorOpenBlocked(False)
            tx.setIsAnimationEnabled(isAdventAnimationEnabled())
            tx.setIsCalendarCompleted(len(self.__adventController.completedAwardsQuests) == config.doorsCount)
            self.__fillDoors(tx)
            self.__createProgressionInfo(tx.progressionRewards)

    def __fillDoors(self, model):
        isHighlightDoorAnimationAvailable = not self.__lastHighlightDoorAnimTime or time.time() - self.__lastHighlightDoorAnimTime > self.__UPDATE_DOOR_ANIMATION_DELTA_TIME
        firstClosedDayID = getFirstClosedDayID()
        doors = model.getDoors()
        doors.clear()
        for dayId in range(1, self.__adventController.config.doorsCount + 1):
            doors.addViewModel(self.__createDoorModel(dayId, firstClosedDayID, isHighlightDoorAnimationAvailable))

        doors.invalidate()

    def __createDoorModel(self, dayID, firstClosedDayID, isHighlightDoorAnimationAvailable):
        doorsConfig = self.__adventController.config.doors
        state = getDoorState(dayID, firstClosedDayID=firstClosedDayID)
        doorModel = DoorViewModel()
        doorModel.setDayId(dayID)
        doorModel.setDoorState(state)
        doorModel.setOpenTimeStamp(self.__adventController.getDoorOpenTimeUI(dayID))
        doorModel.setMark(CONFIG_TO_MODEL_MARK_MAP.get(doorsConfig[dayID - 1].get('mark', DoorMarkType.NONE), Mark.NONE))
        doorModel.setIsEnoughResources(True)
        doorModel.setPrice(0)
        lastHighlightedDoorID = getAdventCalendarSetting(AdventCalendar.LAST_HIGHLIGHTED_DOOR)
        if isHighlightDoorAnimationAvailable and state == DoorState.READY_TO_OPEN:
            if dayID > lastHighlightedDoorID or self.__adventController.isInPostActivePhase() and lastHighlightedDoorID != dayID:
                doorModel.setOpenAnimationRequired(True)
                setAdventCalendarSetting(AdventCalendar.LAST_HIGHLIGHTED_DOOR, dayID)
            else:
                doorModel.setOpenAnimationRequired(False)
            self.__lastHighlightDoorAnimTime = time.time()
        return doorModel

    def __getPhaseState(self):
        if self.__adventController.isAvailableAndActivePhase():
            return StatePhase.ACTIVE_PHASE
        if self.__adventController.isAvailableAndPostActivePhase():
            return StatePhase.POST_ACTIVE_PHASE
        _logger.error('The advent calendar state is undefined, closing the window')

    def __createProgressionInfo(self, viewModel):
        isCompleted = True
        progressionRewards = viewModel.getRewards()
        progressionRewards.clear()
        self.__tooltips.clear()
        prevRequiredTokensAmount = 0
        prevState = None
        for quest in self.__adventController.progressionRewardQuestsOrdered:
            rewardModels, prevState, prevRequiredTokensAmount = self.__createProgressionRewardModels(quest, prevState, prevRequiredTokensAmount)
            isCompleted &= quest.isCompleted()
            for m in rewardModels:
                progressionRewards.addViewModel(m)

        progressionRewards.invalidate()
        viewModel.setIsCompleted(isCompleted)
        return

    def __createProgressionRewardModels(self, quest, prevState, prevRequiredTokensAmount):
        accountTokensAmount = getAccountTokensAmount(ADVENT_CALENDAR_TOKEN)
        requiredTokensAmount = getQuestNeededTokensCount(quest)
        packer = getProgressionBonusPacker()
        result = []
        if accountTokensAmount >= requiredTokensAmount:
            state = ProgressionState.REWARD_RECEIVED
        elif prevState and not prevState == ProgressionState.REWARD_RECEIVED:
            state = ProgressionState.REWARD_LOCKED
        else:
            state = ProgressionState.REWARD_IN_PROGRESS
        actualOpenedDoorsAmount = accountTokensAmount - prevRequiredTokensAmount if state == ProgressionState.REWARD_IN_PROGRESS else 0
        requiredOpenedDoorsAmount = requiredTokensAmount - prevRequiredTokensAmount
        bonus = first(quest.getBonuses())
        bonusList = packer.pack(bonus)
        bTooltipList = packer.getCustomToolTip(bonus, quest.getID())
        bContentIdList = packer.getContentId(bonus)
        tooltipIndex = len(self.__tooltips)
        for bIndex, progressionRewardModel in enumerate(bonusList):
            tooltipIdx = str(tooltipIndex)
            progressionRewardModel.setTooltipId(tooltipIdx)
            self.__tooltips[tooltipIdx] = bTooltipList[bIndex]
            progressionRewardModel.setTooltipContentId(bContentIdList[bIndex])
            progressionRewardModel.setState(state)
            progressionRewardModel.setActualOpenedDoorsAmount(actualOpenedDoorsAmount)
            progressionRewardModel.setRequiredOpenedDoorsAmount(requiredOpenedDoorsAmount)
            tooltipIndex += 1
            result.append(progressionRewardModel)

        return (result, state, requiredTokensAmount)

    @args2params(int)
    def __onOpenDoorAnimStarted(self, dayId):
        if not self.__adventController.isAvailableAndActivePhase():
            _logger.error('Wrong advent calendar phase to open door for free')
            return
        self.__blockAdventWindowUpdates()
        self.__lasOpenDoorTime = time.time()
        self.__openAdventDoor(dayId=dayId)

    @args2params(int)
    def __onOpenDoorAnimEnded(self, dayId):
        self.__selectedDayId = dayId
        self.__showRewardScreen(dayId)

    @staticmethod
    def __onShowPurchaseDialogWindow(*_):
        _logger.error('Not implemented')

    @wg_async
    def __showRewardScreen(self, dayId):
        _logger.debug('Show reward screen for dayId=%d', dayId)
        quest = self.__adventController.getQuestByDayId(dayId)
        self.__waitSuccessfulOpenDoor = True
        with self.viewModel.transaction() as tx:
            doors = tx.getDoors()
            doors[dayId - 1].setDoorState(DoorState.OPENED)
            doors.invalidate()
            tx.setIsCalendarCompleted(all([ d.getDoorState() == DoorState.OPENED for d in doors ]))
        if quest is None:
            yield wg_await(delay(self.__OPEN_DOOR_ANIM_TIME))
            pushOpenDoorFailedError()
            self.__releaseAdventWindowUpdates()
            self.__waitSuccessfulOpenDoor = False
            return
        else:
            showRewardWindow(dayId=dayId, isProgressionReward=False, data=quest.getBonuses(), parent=self.getParentWindow())
            return

    def __showProgressionRewardWindow(self):
        quest = self.__adventController.progressionQuestMayBeCompleted(openedDoorsAmount=getAccountTokensAmount(ADVENT_CALENDAR_TOKEN))
        if quest:
            _logger.debug('Show Progression reward screen for doorId=%d', self.__selectedDayId)
            showRewardWindow(dayId=self.__selectedDayId, isProgressionReward=True, data=quest.getBonuses(), parent=self.getParentWindow())
            return
        self.__releaseAdventWindowUpdates()

    def __openAdventDoor(self, dayId):
        with self.viewModel.event.transaction() as tx:
            tx.setEventType(EventType.OPEN_DOOR)
            tx.setPayload(json.dumps({'doorId': dayId,
             'timeStamp': time.time()}))

    def __changeBlurState(self, event):
        state = event.ctx.get('setBlur', False)
        self.viewModel.setShowBlur(bool(state))

    def __getProgressionRewardInProgressIdx(self, progressionRewards):
        if self.__progressionRewardInProgressIdx == _INVALID_IDX or self.__progressionRewardInProgressIdx >= len(progressionRewards):
            for idx, reward in enumerate(progressionRewards):
                if reward.getState() == ProgressionState.REWARD_IN_PROGRESS:
                    self.__progressionRewardInProgressIdx = idx
                    break
            else:
                self.__progressionRewardInProgressIdx = _INVALID_IDX

        return self.__progressionRewardInProgressIdx

    @wg_async
    def __updateProgressionRewards(self, event):
        isProgressionRewardCompleted = event.ctx.get('isProgressionRewardCompleted', False)
        doorIsOpened = event.ctx.get('doorIsOpened', False)
        try:
            try:
                if not isProgressionRewardCompleted and doorIsOpened:
                    yield wg_await(self.__doorOpenedQuestCompletedEvent.wait(), timeout=QUEST_COMPLETED_TIMEOUT)
            except TimeoutError:
                _logger.error('Received Timeout error waiting for quest completion')
            except BrokenPromiseError:
                _logger.info('%s has been destroyed before quest completed', self)

        finally:
            self.__doorOpenedQuestCompletedEvent.clear()
            self.__waitSuccessfulOpenDoor = False

        timeDelta = round(time.time() - self.__lasOpenDoorTime, 2)
        if 0 < timeDelta < self.__OPEN_DOOR_ANIM_TIME:
            yield wg_await(delay(self.__OPEN_DOOR_ANIM_TIME - timeDelta))
        if not self.viewModel or not self.viewModel.proxy:
            return
        if self.__adventController.isInPostActivePhase() or not doorIsOpened:
            self.__releaseAdventWindowUpdates()
            return
        with self.viewModel.transaction() as tx:
            progressionRewards = tx.progressionRewards.getRewards()
            rewardIdx = self.__getProgressionRewardInProgressIdx(progressionRewards)
            if rewardIdx != _INVALID_IDX:
                reward = progressionRewards[rewardIdx]
                if isProgressionRewardCompleted:
                    reward.setState(ProgressionState.REWARD_RECEIVED)
                    self.__progressionRewardInProgressIdx += 1
                    if self.__progressionRewardInProgressIdx == len(progressionRewards):
                        tx.progressionRewards.setIsCompleted(True)
                    else:
                        nextReward = progressionRewards[self.__progressionRewardInProgressIdx]
                        nextReward.setState(ProgressionState.REWARD_IN_PROGRESS)
                else:
                    openedDoorsAmount = reward.getActualOpenedDoorsAmount() + 1
                    reward.setActualOpenedDoorsAmount(openedDoorsAmount)
            else:
                self.__releaseAdventWindowUpdates()
                if not tx.progressionRewards.getIsCompleted():
                    _logger.warning("Can't find progression reward with state %s", ProgressionState.REWARD_IN_PROGRESS.value)

    def __onDoorOpened(self):
        if not self.__waitSuccessfulOpenDoor:
            self.__updateModel()
            return
        self.__doorOpenedQuestCompletedEvent.set()

    def __onProgressionAnimationCompleted(self):
        self.__releaseAdventWindowUpdates()

    @nextTick
    def __releaseAdventWindowUpdates(self):
        if not self.viewModel or not self.viewModel.proxy:
            return
        if not self.viewModel.getDoorOpenBlocked():
            return
        with self.viewModel.transaction() as tx:
            tx.setDoorOpenBlocked(False)
        self.__updateModel()

    def __blockAdventWindowUpdates(self):
        self.viewModel.setDoorOpenBlocked(True)

    def __onSettingsChange(self):
        if not self.__adventController.isAvailable():
            self.destroyWindow()
            return
        self.__updateModel()

    def __onNewDayStarted(self):
        self.__updateModel()

    def __onInfoClick(self):
        self.__openIntro()

    @adisp_process
    def __onOpenDownloadLink(self):
        processedUrl = yield URLMacros().parse(self.__adventController.config.downloadImgUrl)
        BigWorld.wg_openWebBrowser(processedUrl)

    def __openIntro(self, isFirstTime=False):
        with self.viewModel.transaction() as tx:
            tx.setIsIntroScreenVisible(True)
            tx.setShowBlur(True)
        showAdventCalendarIntroWindow(parent=self.getParentWindow(), isFirstTime=isFirstTime)

    def __onIntroCloseStarted(self, _):
        with self.viewModel.transaction() as tx:
            tx.setIsIntroScreenVisible(False)
            tx.setShowBlur(False)

    def __onClose(self, *_, **__):
        self.destroyWindow()


class AdventCalendarMainWindow(LobbyWindow):

    def __init__(self, parent=None):
        super(AdventCalendarMainWindow, self).__init__(WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, layer=WindowLayer.FULLSCREEN_WINDOW, content=AdventCalendarMainView(), parent=parent)
