# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/advent_calendar_v2/advent_calendar_v2_main_view.py
import logging
import time
import typing
import json
from account_helpers import AccountSettings
from account_helpers.AccountSettings import ADVENT_CALENDAR_V2_ANIMATION_LAST_SHOWN_DOOR
from frameworks.wulf import ViewFlags, ViewSettings, WindowFlags, WindowLayer
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl.backport import TooltipData, BackportTooltipWindow
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.advent_calendar.advent_calendar_door_view_model import AdventCalendarDoorViewModel, DoorState
from gui.impl.gen.view_models.views.lobby.advent_calendar.advent_calendar_progression_reward_item_view_model import AdventCalendarProgressionRewardItemViewModel, ProgressionState, RewardType
from gui.impl.gen.view_models.views.lobby.advent_calendar.components.advent_calendar_events import EventType
from gui.impl.lobby.advent_calendar_v2.advent_calendar_optimization import AdventWindowOptimizationManager, AdventWindowOptimizationSettings, AdventWindowOptimizationProcessorSettings
from gui.impl.lobby.advent_calendar_v2.advent_calendar_v2_helper import getQuestNeededTokensCount, getAccountTokensAmount, showAdventCalendarRewardWindow, getProgressionRewardType, showAdventCalendarPurchaseDialogWindow, getMaxResourceCount, isAdventAnimationEnabled, getProgressionRewardQuestBonus
from gui.shared.advent_calendar_v2_consts import ADVENT_CALENDAR_TOKEN
from gui.impl.gen.view_models.views.lobby.advent_calendar.advent_calendar_main_view_model import AdventCalendarMainViewModel, StatePhase
from gui.impl.lobby.advent_calendar_v2.advent_calendar_v2_parent_view import AdventCalendarParentView
from gui.impl.lobby.advent_calendar_v2.advent_calendar_v2_sound import ADVENT_CALENDAR_V2_MAIN_WINDOW_SOUND
from gui.impl.lobby.advent_calendar_v2.ny_components.advent_calendar_v2_ny_resources_balance_view import AdventCalendarNYResourceBalance
from gui.impl.lobby.advent_calendar_v2.tooltips.advent_calendar_big_lootbox_tooltip import AdventCalendarBigLootBoxTooltip
from gui.impl.lobby.advent_calendar_v2.tooltips.advent_calendar_all_rewards_tooltip import AdventCalendarAllRewardsTooltip
from gui.impl.lobby.new_year.tooltips.ny_gift_machine_token_tooltip import NyGiftMachineTokenTooltip
from gui.impl.pub.lobby_window import LobbyWindow
from gui.shared import events, EVENT_BUS_SCOPE
from gui.shared.events import LobbySimpleEvent
from helpers import dependency
from shared_utils import nextTick
from skeletons.gui.game_control import IAdventCalendarV2Controller
from wg_async import wg_async, wg_await
if typing.TYPE_CHECKING:
    from typing import Tuple
_logger = logging.getLogger(__name__)
REWARD_TYPE_TO_TOOLTIP_ID = {RewardType.GIFT_MACHINE_TOKEN: R.views.lobby.new_year.tooltips.NyGiftMachineTokenTooltip(),
 RewardType.CREW_MEMBER: R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent(),
 RewardType.BIG_LOOTBOX: R.views.lobby.advent_calendar.tooltips.AdventCalendarBigLootBoxTooltip()}

def predictionFunction(window):
    return not isinstance(window.content, AdventCalendarMainView)


ADVENT_CALENDAR_OPTIMIZATION_SETTINGS = AdventWindowOptimizationSettings(disableWindowsVisibility=True, windowOptimizationProcessorSettings=AdventWindowOptimizationProcessorSettings(windowsVisibilityPredicateFunction=predictionFunction))
_INVALID_IDX = -1

class AdventCalendarMainView(AdventCalendarParentView):
    __adventCalendarV2Ctrl = dependency.descriptor(IAdventCalendarV2Controller)
    _COMMON_SOUND_SPACE = ADVENT_CALENDAR_V2_MAIN_WINDOW_SOUND
    __UPDATE_DOOR_ANIMATION_DELTA_TIME = 2

    def __init__(self):
        settings = ViewSettings(R.views.lobby.advent_calendar.MainView())
        settings.flags = ViewFlags.VIEW
        settings.model = AdventCalendarMainViewModel()
        self.__doorsModels = []
        self.__progressionRewardInProgressIdx = _INVALID_IDX
        self.__selectedDayId = 0
        self.__lastUpdatedTime = 0
        self.__currencyName = ''
        self._optimizationManager = AdventWindowOptimizationManager(settings=ADVENT_CALENDAR_OPTIMIZATION_SETTINGS)
        super(AdventCalendarMainView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(AdventCalendarMainView, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.advent_calendar.tooltips.AdventCalendarAllRewardsTooltip():
            if self.__adventCalendarV2Ctrl.isAvailableAndActivePhase():
                return AdventCalendarAllRewardsTooltip()
        elif contentID in (R.views.lobby.new_year.tooltips.NyGiftMachineTokenTooltip(), R.views.lobby.advent_calendar.tooltips.AdventCalendarBigLootBoxTooltip()):
            return self.__createProgressionRewardTooltip(contentID)
        return super(AdventCalendarMainView, self).createToolTipContent(event, contentID)

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            toolTipData = None
            idx, progressionReward = self.__getProgressionRewardModelByTooltipId(event.contentID)
            if progressionReward and progressionReward.getRewardType() == RewardType.CREW_MEMBER:
                actualDoorsAmount = progressionReward.getActualOpenedDoorsAmount()
                requerdDoorsAmount = progressionReward.getRequiredOpenedDoorsAmount()
                doorsToOpenAmount = requerdDoorsAmount - actualDoorsAmount
                state = progressionReward.getState()
                crewMemberToken = getProgressionRewardQuestBonus(self.__adventCalendarV2Ctrl.progressionRewardQuestsOrdered[idx])
                toolTipData = TooltipData(tooltip=None, isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.ADVENT_CALENDAR_TANKMAN_NOT_RECRUITED, specialArgs=[crewMemberToken,
                 state,
                 doorsToOpenAmount,
                 True])
            if not toolTipData:
                _logger.warning('TooltipData not found for %s', TOOLTIPS_CONSTANTS.ADVENT_CALENDAR_TANKMAN_NOT_RECRUITED)
                return
            window = BackportTooltipWindow(toolTipData, self.getParentWindow())
            window.load()
            return window
        else:
            return super(AdventCalendarMainView, self).createToolTip(event)

    def _getEvents(self):
        return ((self.viewModel.onClose, self.__onClose),
         (self.viewModel.onOpenDoor, self.__onOpenDoor),
         (self.__adventCalendarV2Ctrl.onNewDayStarted, self.__onNewDayStarted),
         (self.__adventCalendarV2Ctrl.onConfigChanged, self.__onSettingsChange),
         (self.viewModel.onShowReward, self.__openRewardScreen),
         (self.viewModel.progressionRewards.onProgressionRewardCompleted, self.__showProgressionRewardWindow),
         (self.viewModel.onShowPurchaseDialog, self.__onShowPurchaseDialogWindow),
         (self.viewModel.onAnimationCompleted, self.__releaseAdventWindowUpdates),
         (self.__adventCalendarV2Ctrl.onDoorOpened, self.__updateModel))

    def _getListeners(self):
        return ((events.AdventCalendarV2Event.PROGRESSION_REWARD_VIEWED, self.__updateProgressionRewards, EVENT_BUS_SCOPE.LOBBY), (events.AdventCalendarV2Event.CHANGE_BLUR_STATUS, self.__changeBlurState, EVENT_BUS_SCOPE.LOBBY), (LobbySimpleEvent.SHOW_LOOT_BOX_VIEW, self.__onClose, EVENT_BUS_SCOPE.LOBBY))

    def _onLoading(self, *args, **kwargs):
        super(AdventCalendarMainView, self)._onLoading(*args, **kwargs)
        if not self.__adventCalendarV2Ctrl.isAvailable():
            _logger.error('Advent calendar is disabled')
            return self.destroyWindow()
        self.__createDoorsModels()
        self.__updateModel()
        self._optimizationManager.start()

    def _finalize(self):
        self._optimizationManager.fini()
        self.__doorsModels = []
        self.__completedProgressionRewardsIdx = _INVALID_IDX
        self.__selectedDayId = 0
        self.__lastUpdatedTime = 0
        self.__currencyName = ''
        super(AdventCalendarMainView, self)._finalize()

    def _registerSubModels(self):
        return [AdventCalendarNYResourceBalance(self.viewModel.balance, self, self.__onClose, self.__updateModel, self._isConvertPopoverAvailable)]

    def _isConvertPopoverAvailable(self):
        return not self.viewModel.getDoorOpenBlocked()

    def __onClose(self, *args, **kwargs):
        self.destroyWindow()

    def __createDoorsModels(self):
        self.__doorsModels = [ AdventCalendarDoorViewModel() for _ in range(self.__adventCalendarV2Ctrl.getMaxDayNumbers) ]

    def __fillModel(self, tx):
        if self.viewModel.getDoorOpenBlocked():
            _logger.debug('Advent calendar window is locked for updates')
            return
        phase = self.__getPhaseState()
        if not self.__adventCalendarV2Ctrl.isAvailable() or not phase:
            return self.destroyWindow()
        tx.setStatePhase(phase)
        tx.setStartTime(self.__adventCalendarV2Ctrl.startDate)
        tx.setActivePhaseEndTime(self.__adventCalendarV2Ctrl.postEventStartDate)
        tx.setPostActivePhaseEndTime(self.__adventCalendarV2Ctrl.postEventEndDate)
        tx.setDoorOpenBlocked(False)
        tx.setIsAnimationEnabled(isAdventAnimationEnabled())
        tx.setIsCalendarComplited(self.__adventCalendarV2Ctrl.getOpenedDoorsAmount == self.__adventCalendarV2Ctrl.getMaxDayNumbers)
        self.__createDoorsInfo(tx)
        self.__createProgressionInfo(tx.progressionRewards)

    def __onSettingsChange(self):
        if not self.__adventCalendarV2Ctrl.isAvailable():
            return self.destroyWindow()
        self.__updateModel()

    def __createDoorsInfo(self, viewModel):
        doorsList = viewModel.getDoors()
        doorsList.clear()
        maxResCount = getMaxResourceCount()
        updateDoorAnimation = True if not self.__lastUpdatedTime or time.time() - self.__lastUpdatedTime > self.__UPDATE_DOOR_ANIMATION_DELTA_TIME else False
        for dayId, doorModel in enumerate(self.__doorsModels):
            self.__fillDoorInfo(doorModel, maxResCount, self.__getOneDoorInfo(dayId + 1), updateDoorAnimation)
            doorsList.addViewModel(doorModel)

        doorsList.invalidate()

    def __getOneDoorInfo(self, doorId):
        default = (0,
         DoorState.CLOSED,
         0,
         0)
        if self.__adventCalendarV2Ctrl.getMaxDayNumbers >= doorId > 0:
            return (doorId,
             self.__adventCalendarV2Ctrl.getDoorState(doorId),
             self.__adventCalendarV2Ctrl.doorsCost[doorId - 1],
             self.__adventCalendarV2Ctrl.getDoorOpenTimeUI(doorId))
        _logger.error('Wrong door id = %s', doorId)
        return default

    def __fillDoorInfo(self, doorModel, maxResourceCount, doorItem, updateDoorAnimation):
        doorId, status, price, availableTimestamp = doorItem
        doorModel.setDayId(doorId)
        doorModel.setDoorState(status)
        doorModel.setPrice(price)
        doorModel.setIsEnoughResources(maxResourceCount >= price)
        doorModel.setOpenTimeStamp(availableTimestamp)
        lastShownAnimationDoorId = AccountSettings.getUIFlag(ADVENT_CALENDAR_V2_ANIMATION_LAST_SHOWN_DOOR)
        if updateDoorAnimation:
            if status == DoorState.READY_TO_OPEN and (doorId > lastShownAnimationDoorId or self.__adventCalendarV2Ctrl.isInPostActivePhase() and lastShownAnimationDoorId != doorId):
                doorModel.setOpenAnimationRequired(True)
                AccountSettings.setUIFlag(ADVENT_CALENDAR_V2_ANIMATION_LAST_SHOWN_DOOR, doorId)
            else:
                doorModel.setOpenAnimationRequired(False)
            self.__lastUpdatedTime = time.time()

    def __getPhaseState(self):
        if self.__adventCalendarV2Ctrl.isAvailableAndActivePhase():
            return StatePhase.ACTIVE_PHASE
        if self.__adventCalendarV2Ctrl.isAvailableAndPostActivePhase():
            return StatePhase.POST_ACTIVE_PHASE
        _logger.error('The advent calendar state is undefined, closing the window')

    def __createProgressionInfo(self, viewModel):
        isCompleted = True
        progressionRewards = viewModel.getRewards()
        progressionRewards.clear()
        accountTokensAmount = getAccountTokensAmount(ADVENT_CALENDAR_TOKEN)
        prevRequiredTokensAmount = 0
        prevState = None
        for quest in self.__adventCalendarV2Ctrl.progressionRewardQuestsOrdered:
            requiredTokensAmount = getQuestNeededTokensCount(quest)
            if accountTokensAmount >= requiredTokensAmount:
                state = ProgressionState.REWARD_RECEIVED
            elif prevState and not prevState == ProgressionState.REWARD_RECEIVED:
                state = ProgressionState.REWARD_LOCKED
            else:
                state = ProgressionState.REWARD_IN_PROGRESS
            isCompleted &= state == ProgressionState.REWARD_RECEIVED
            rewardType = getProgressionRewardType(quest)
            progressionRewardModel = AdventCalendarProgressionRewardItemViewModel()
            progressionRewardModel.setRewardType(rewardType)
            progressionRewardModel.setTooltipContentId(REWARD_TYPE_TO_TOOLTIP_ID.get(rewardType))
            progressionRewardModel.setState(state)
            progressionRewardModel.setActualOpenedDoorsAmount(accountTokensAmount - prevRequiredTokensAmount if state == ProgressionState.REWARD_IN_PROGRESS else 0)
            progressionRewardModel.setRequiredOpenedDoorsAmount(requiredTokensAmount - prevRequiredTokensAmount)
            progressionRewards.addViewModel(progressionRewardModel)
            prevRequiredTokensAmount = requiredTokensAmount
            prevState = state

        progressionRewards.invalidate()
        viewModel.setIsCompleted(isCompleted)
        return

    def __getProgressionRewardModelByTooltipId(self, tooltipId):
        progressionRewards = self.viewModel.progressionRewards.getRewards()
        for idx, model in enumerate(progressionRewards):
            if model.getTooltipContentId() == tooltipId:
                return (idx, model)

    def __createProgressionRewardTooltip(self, tooltipId):
        _, progressionReward = self.__getProgressionRewardModelByTooltipId(tooltipId)
        if progressionReward:
            doorsToOpenAmount = progressionReward.getRequiredOpenedDoorsAmount() - progressionReward.getActualOpenedDoorsAmount()
            state = progressionReward.getState()
            rewardType = progressionReward.getRewardType()
            isPostEvent = self.__adventCalendarV2Ctrl.isInPostActivePhase()
            if rewardType == RewardType.GIFT_MACHINE_TOKEN:
                return NyGiftMachineTokenTooltip(adventCalendarState=state, adventCalendarDoorsToOpenAmount=doorsToOpenAmount, isAdventCalendarPostEvent=isPostEvent)
            if rewardType == RewardType.BIG_LOOTBOX:
                if self.__adventCalendarV2Ctrl.getLootBoxInfo():
                    return AdventCalendarBigLootBoxTooltip(state, doorsToOpenAmount, isPostEvent, True)
            else:
                _logger.error('No reward with type %s found', rewardType.value)
        else:
            _logger.debug('No advent calendar progression rewards found')

    def __onOpenDoor(self, event):
        doorId = self.__getParametrFromEvent(event, 'dayId')
        if doorId is None:
            return
        elif self.__adventCalendarV2Ctrl.isAvailableAndActivePhase():
            self.__blockAdventWindowUpdates()
            return self.__openAdventDoor(dayId=doorId)
        else:
            _logger.error('Wrong advent calendar phase to open door for free')
            return

    def __openRewardScreen(self, event):
        doorId = self.__getParametrFromEvent(event, 'dayId')
        if doorId is None:
            return self.__releaseAdventWindowUpdates()
        else:
            self.__selectedDayId = doorId
            self.__showRewardScreen(doorId, self.getParentWindow())
            return

    def __onShowPurchaseDialogWindow(self, event):
        doorId = self.__getParametrFromEvent(event, 'dayId')
        if doorId is None:
            return
        elif self.__adventCalendarV2Ctrl.isAvailableAndPostActivePhase():
            doorIndex = doorId - 1
            if doorIndex < 0 or doorIndex >= len(self.__doorsModels):
                _logger.error('Could not find an element with id=%s', doorIndex)
                return
            self.__blockAdventWindowUpdates()
            if self.__adventCalendarV2Ctrl.doorsCost[doorIndex] < 1:
                return self.__openAdventDoor(doorId)
            return self.__showPurchaseDialogWindow(doorId, self.__adventCalendarV2Ctrl.doorsCost[doorIndex])
        else:
            _logger.error('Wrong advent calendar phase to open purchase dialog window')
            return

    @wg_async
    def __showPurchaseDialogWindow(self, doorId, price):
        _logger.debug('Opening the purchase dialog door window, doorId=%d, with price=%d', doorId, price)
        self.viewModel.setShowBlur(True)
        result = yield wg_await(showAdventCalendarPurchaseDialogWindow(doorId, price, parent=self.getParentWindow()))
        self.viewModel.setShowBlur(False)
        _logger.debug('Purchase dialog door window is closed with result=%s', result)
        if result:
            self.__currencyName = result.resourceStr
            self.__openAdventDoor(dayId=result.dayId)
        else:
            self.__releaseAdventWindowUpdates()

    @wg_async
    def __showRewardScreen(self, doorId, parent):
        _logger.debug('Show reward screen for doorId=%d', doorId)
        data = self.__adventCalendarV2Ctrl.getRewardsForQuest(doorId)
        self.viewModel.getDoors()[doorId - 1].setDoorState(DoorState.OPENED)
        self.viewModel.getDoors().invalidate()
        yield wg_await(showAdventCalendarRewardWindow(dayId=doorId, parent=parent, isProgressionReward=False, data=data, currencyName=self.__currencyName))
        self.__currencyName = ''

    @wg_async
    def __showProgressionRewardWindow(self):
        quest = self.__adventCalendarV2Ctrl.progressionQuestMayBeCompleted(openedDoorsAmount=getAccountTokensAmount(ADVENT_CALENDAR_TOKEN))
        if quest:
            _logger.debug('Show Progression reward screen for doorId=%d', self.__selectedDayId)
            self.viewModel.setShowBlur(True)
            yield wg_await(showAdventCalendarRewardWindow(dayId=self.__selectedDayId, parent=self.getParentWindow(), isProgressionReward=True, data=quest.getBonuses()))
            self.viewModel.setShowBlur(False)
            return
        self.__releaseAdventWindowUpdates()

    @staticmethod
    def __getParametrFromEvent(event, argument):
        parametr = int(event.get(argument, ''))
        if not parametr:
            _logger.error("Parametr '%s' is ommited", argument)
            return None
        else:
            return parametr

    def __openAdventDoor(self, dayId):
        with self.viewModel.event.transaction() as tx:
            tx.setEventType(EventType.OPEN_DOOR)
            tx.setPayload(json.dumps({'doorId': dayId,
             'timeStamp': time.time()}))

    def __onNewDayStarted(self):
        self.__updateModel()

    def __changeBlurState(self, event):
        state = event.ctx.get('setBlur', False)
        self.viewModel.setShowBlur(bool(state))

    def __updateModel(self):
        with self.viewModel.transaction() as tx:
            self.__fillModel(tx)

    def __getProgresssionRewardInPrgoressIdx(self, progressionRewards):
        if self.__progressionRewardInProgressIdx == _INVALID_IDX or self.__progressionRewardInProgressIdx >= len(progressionRewards):
            for idx, reward in enumerate(progressionRewards):
                if reward.getState() == ProgressionState.REWARD_IN_PROGRESS:
                    self.__progressionRewardInProgressIdx = idx
                    break
            else:
                self.__progressionRewardInProgressIdx = _INVALID_IDX

        return self.__progressionRewardInProgressIdx

    def __updateProgressionRewards(self, event):
        rewardCompleted = event.ctx.get('isProgressionRewardCompleted', False)
        doorIsOpened = event.ctx.get('doorIsOpened', False)
        if self.__adventCalendarV2Ctrl.isInPostActivePhase() or not doorIsOpened:
            return self.__releaseAdventWindowUpdates()
        with self.viewModel.transaction() as tx:
            progressionRewards = tx.progressionRewards.getRewards()
            rewardIdx = self.__getProgresssionRewardInPrgoressIdx(progressionRewards)
            if rewardIdx != _INVALID_IDX:
                reward = progressionRewards[rewardIdx]
                if rewardCompleted:
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
                _logger.warning("Can't find progression reward with state %s", ProgressionState.REWARD_IN_PROGRESS.value)

    @nextTick
    def __releaseAdventWindowUpdates(self):
        with self.viewModel.transaction() as tx:
            tx.setDoorOpenBlocked(False)
        self.__updateModel()

    def __blockAdventWindowUpdates(self):
        self.viewModel.setDoorOpenBlocked(True)


class AdventCalendarMainWindow(LobbyWindow):

    def __init__(self, parent=None):
        super(AdventCalendarMainWindow, self).__init__(WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, layer=WindowLayer.FULLSCREEN_WINDOW, content=AdventCalendarMainView(), parent=parent)
