# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: armory_yard/scripts/client/armory_yard/gui/impl/lobby/feature/armory_yard_progress_presenter.py
from adisp import adisp_process
from armory_yard_constants import State
from armory_yard.gui.shared.gui_items.items_actions import COLLECT_REWARDS
from armory_yard.gui.window_events import showArmoryYardRewardWindow
from debug_utils import LOG_ERROR
from gui.shared.gui_items.items_actions import factory
from gui.shared.utils import decorators
from armory_yard.gui.shared.gui_items.processors.armory_yard_processors import ClaimRareRewardProcessor
from shared_utils import first
from armory_yard.gui.impl.gen.view_models.views.lobby.feature.armory_yard_main_view_model import ArmoryYardMainViewModel, AnimationStatus, ArmoryYardLevelModel, RewardStatus, BuyButtonState, EscSource
from armory_yard.gui.impl.gen.view_models.views.lobby.feature.armory_yard_rewards_view_model import State as SateView
from armory_yard.gui.impl.gen.view_models.views.lobby.feature.armory_yard_level_model import RewardType
from armory_yard.gui.shared.bonus_packers import getArmoryYardBonusPacker
from armory_yard.gui.shared.bonuses_sorter import bonusesSortKeyFunc
from Event import SuspendableEventSubscriber
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import LobbySimpleEvent, ArmoryYardEvent
from gui.hangar_cameras.hangar_camera_common import CameraRelatedEvents
from gui.impl.lobby.common.view_helpers import packBonusModelAndTooltipData
from gui.server_events.bonuses import getNonQuestBonuses, mergeBonuses, splitBonuses
from helpers import dependency
from skeletons.gui.game_control import IArmoryYardController
from skeletons.account_helpers.settings_core import ISettingsCore
from armory_yard.gui.window_events import showArmoryYardVideoRewardWindow, showArmoryYardInfoPage, showArmoryYardBuyWindow, showArmoryYardBundlesWindow, showArmoryYardShopWindow
from skeletons.gui.shared import IItemsCache
from skeletons.gui.shared.utils import IHangarSpace

class _InternalState(object):
    __NONE = -1
    __REPLAY_ANIMATION = 1
    __BUILDING = 2

    def __init__(self):
        self.__status = self.__NONE

    def reset(self):
        self.__status = self.__NONE

    def setReplayAnimation(self):
        self.__status = self.__REPLAY_ANIMATION

    def setBuilding(self):
        self.__status = self.__BUILDING

    @property
    def isReplayAnimation(self):
        return self.__status == self.__REPLAY_ANIMATION

    @property
    def isBuilding(self):
        return self.__status == self.__BUILDING

    @property
    def isAnimation(self):
        return self.isBuilding or self.isReplayAnimation


class _ProgressionTabPresenter(object):
    __armoryYardCtrl = dependency.descriptor(IArmoryYardController)
    __settingsCore = dependency.descriptor(ISettingsCore)
    __itemsCache = dependency.descriptor(IItemsCache)
    __hangarSpace = dependency.descriptor(IHangarSpace)

    def __init__(self, viewModel, stageManager, closeCB):
        self.__viewModel = viewModel
        self.__tooltipData = {}
        self.__stageManager = stageManager
        self._isActiveCollectRewardsBtn = False
        self._isBuyWindowLoad = False
        self.__playAnimationLastID = None
        self.__closeCB = closeCB
        self.__eventsSubscriber = SuspendableEventSubscriber()
        self.__parent = None
        self.__state = _InternalState()
        self.__unload = False
        return

    def init(self, parent):
        self.__parent = parent
        self.__eventsSubscriber.subscribeToEvents((self.__armoryYardCtrl.serverSettings.onUpdated, self.__onServerSettingsUpdated), (self.__armoryYardCtrl.onAYCoinsUpdate, self.__onAYCoinsUpdate), (self.__stageManager.onStartStage, self.__onStartStage), (self.__stageManager.onFinishStage, self.__onFinishStage), (self.__viewModel.onCollectReward, self.__onCollectReward), (self.__viewModel.onPlayAnimation, self.__onPlayAnimation), (self.__armoryYardCtrl.onProgressUpdated, self.__onProgressUpdate), (self.__armoryYardCtrl.onCollectFinalReward, self._checkAndShowRareRewardWindow), (self.__viewModel.onAboutEvent, self.__onAboutEvent), (self.__viewModel.onClose, self.__closeView), (self.__viewModel.onSkipAnimation, self.__onSkipAnimation), (self.__viewModel.onMoveSpace, self.__onMoveSpace), (self.__viewModel.onBuyTokens, self.__onBuyTokens), (self.__viewModel.onStartMoving, self.__onStartMoving), (self.__viewModel.onShowVehiclePreview, self.__onShowVehiclePreview), (self.__viewModel.onShowStylePreview, self.__onShowStylePreview), (self.__armoryYardCtrl.onStatusChange, self.__updateState), (self.__viewModel.onShopOpen, self.__onShopOpen), (self.__viewModel.onPlayStageSound, self.__onPlayStageContent))
        self.__eventsSubscriber.pause()
        self.__armoryYardCtrl.cameraManager.init()

    def fini(self):
        self.__eventsSubscriber.unsubscribeFromAllEvents()
        self.__viewModel = None
        self.__stageManager = None
        self.__playAnimationLastID = None
        self.__parent = None
        self.__state = None
        return

    def onLoad(self):
        self.__unload = False
        self.__eventsSubscriber.resume()
        with self.__viewModel.transaction() as model:
            self.__updateSteps(model)
            self.__updateProgressionTimes(model)
            model.setViewedLevel(self.__armoryYardCtrl.getProgressionLevel())
            model.setCurrentLevel(self.__armoryYardCtrl.getCurrentProgress())
            model.setStartStepOfPostProgression(self.__armoryYardCtrl.startStepOfPostProgression)
            model.setAnimationLevel(-1)
            model.setLevelDuration(-1)
            model.setAnimationStatus(AnimationStatus.DISABLED)
            model.setReplay(True)
            model.setState(self.__armoryYardCtrl.getState())
            self.__checkBuyButton(model)
        if self.__state.isAnimation:
            self.__stageManager.resume()
        else:
            self.__firstEnterActions()
        g_eventBus.handleEvent(LobbySimpleEvent(LobbySimpleEvent.NOTIFY_CURSOR_OVER_3DSCENE, ctx={'isOver3dScene': True}), EVENT_BUS_SCOPE.GLOBAL)

    def getTooltipData(self, key, type):
        return self.__tooltipData.get(key, {}) if key is not None and type is not None else None

    def onUnload(self):
        self.__eventsSubscriber.pause()
        self.__unload = True
        if self.__state.isAnimation:
            self.__onSkipAnimation()
        g_eventBus.handleEvent(LobbySimpleEvent(LobbySimpleEvent.NOTIFY_CURSOR_OVER_3DSCENE, ctx={'isOver3dScene': False}), EVENT_BUS_SCOPE.GLOBAL)

    def __checkBuyButton(self, model):
        if self.__armoryYardCtrl.isCompleted():
            model.setBuyButtonState(BuyButtonState.HIDDEN)
            return
        model.setBuyButtonState(BuyButtonState.TOKENS)

    def __onMoveSpace(self, args=None):
        if args is None:
            return
        else:
            g_eventBus.handleEvent(CameraRelatedEvents(CameraRelatedEvents.LOBBY_VIEW_MOUSE_MOVE, ctx={'dx': args.get('dx'),
             'dy': args.get('dy'),
             'dz': args.get('dz')}), EVENT_BUS_SCOPE.GLOBAL)
            return

    def __onBuyTokens(self):
        if self.__armoryYardCtrl.isCompleted():
            return
        else:
            if self.__state.isAnimation:
                self.__onSkipAnimation()
            if self.__armoryYardCtrl.isStarterPackAvailable() and not self.__armoryYardCtrl.isPostProgressionState:
                showArmoryYardBundlesWindow(parent=self.__parent)
            else:
                showArmoryYardBuyWindow(parent=self.__parent, onLoadedCallback=lambda _=None: self.__onBuyWindowLoadStateChange(True), onClosedCallback=lambda _=None: self.__onCloseBuyWindow())
            return

    def __onBuyWindowLoadStateChange(self, isLoad):
        self._isBuyWindowLoad = isLoad

    def __onCloseBuyWindow(self):
        self.__onBuyWindowLoadStateChange(False)
        self._checkAndShowRareRewardWindow()

    def __onShopOpen(self):
        if not self.__armoryYardCtrl.isCompleted():
            return
        showArmoryYardShopWindow()

    def __setEmptyRewardsButton(self):
        with self.__viewModel.transaction() as model:
            model.setRewardStatus(RewardStatus.EMPTYREWARDS)

    def __setSkipButton(self):
        with self.__viewModel.transaction() as model:
            model.setRewardStatus(RewardStatus.ANIMATEDREWARDS)

    def __setGrabRewardsButton(self):
        with self.__viewModel.transaction() as model:
            model.setRewardStatus(RewardStatus.READYREWARDS)

    def __onSkipAnimation(self, isClosing=False):
        if self.__state.isAnimation:
            stage = self.__armoryYardCtrl.getProgressionTokenCount()
            if self.__state.isBuilding:
                self.__setLastPlayedStageID(stage)
                if not isClosing:
                    self._checkAndShowRareRewardWindow()
                ctx = {'index': stage}
                g_eventBus.handleEvent(ArmoryYardEvent(ArmoryYardEvent.STAGE_FINISHED, ctx=ctx))
            self.__stageManager.gotToPositionByStage(stage)
            self.__stageManager.skip(stage)
            self.__updateCollectRewardsButton()
        self.__state.reset()
        with self.__viewModel.transaction() as model:
            model.setAnimationStatus(AnimationStatus.DISABLED)
            model.setReplay(True)

    def __onBrowserViewClosed(self, **_):
        self._checkAndShowRareRewardWindow()

    def __onAboutEvent(self):
        self.__onSkipAnimation()
        showArmoryYardInfoPage(parent=self.__parent, closeCallback=self.__onBrowserViewClosed)

    def __closeView(self, *args):
        if self.__state and self.__state.isAnimation:
            isEscape = False
            firstArg = first(args)
            if firstArg is not None:
                isEscape = firstArg.get('escSource', EscSource.KEYBOARD) == EscSource.KEYBOARD
            self.__onSkipAnimation(isClosing=not isEscape)
            if isEscape:
                return
        self.__closeCB(args)
        return

    def __onServerSettingsUpdated(self):
        if not self.__armoryYardCtrl.isActive():
            self.__closeView()
            return
        self.__updateState()
        with self.__viewModel.transaction() as model:
            self.__updateSteps(model)
            self.__updateProgressionTimes(model)
            self.__checkBuyButton(model)

    def __onAYCoinsUpdate(self):
        with self.__viewModel.transaction() as model:
            self.__checkBuyButton(model)

    def __onProgressUpdate(self):
        with self.__viewModel.transaction() as model:
            model.setCurrentLevel(self.__armoryYardCtrl.getCurrentProgress())
            self.__checkBuyButton(model)
        if not self.__state.isAnimation:
            self.__updateView(progressUpdated=True)

    def __updateView(self, progressUpdated=False):
        self.__updateStage(progressUpdated=progressUpdated)
        self.__updateProgress()
        self.__updateState()

    def __updateProgressionTimes(self, model):
        state = self.__armoryYardCtrl.getState()
        startTime, endTime = self.__armoryYardCtrl.getPurchaseStageTimes() if state == State.PURCHASESTAGE else self.__armoryYardCtrl.getProgressionTimes()
        model.setToTimestamp(endTime)
        model.setFromTimestamp(startTime)

    def __updateState(self):
        if not self.__armoryYardCtrl.isActive():
            self.__closeView()
            return
        with self.__viewModel.transaction() as model:
            model.setState(self.__armoryYardCtrl.getState())

    def __updateSteps(self, model):
        steps = model.getLevels()
        steps.clear()
        stepsRewards = self.__armoryYardCtrl.getStepsRewards()
        for stepNum in range(1, self.__armoryYardCtrl.maxNumberOfSteps + 1):
            stepModel = ArmoryYardLevelModel()
            stepModel.setLevel(stepNum)
            stepRewardsModel = stepModel.getRewards()
            stepRewardsModel.clear()
            if stepNum == self.__armoryYardCtrl.startStepOfPostProgression:
                stepModel.setRewardType(RewardType.PROGRESSION)
            elif stepNum == self.__armoryYardCtrl.maxNumberOfSteps:
                stepModel.setRewardType(RewardType.POSTPROGRESSION)
            stepRewards = []
            for itemType, itemID in stepsRewards[stepNum].iteritems():
                stepRewards.extend(getNonQuestBonuses(itemType, itemID))

            stepRewards = splitBonuses(mergeBonuses(stepRewards))
            stepRewards.sort(key=bonusesSortKeyFunc)
            packBonusModelAndTooltipData(stepRewards, stepRewardsModel, self.__tooltipData, getArmoryYardBonusPacker())
            stepRewardsModel.invalidate()
            steps.addViewModel(stepModel)

        steps.invalidate()

    def _showVideoRewardWindow(self, result):
        if result.success:
            showArmoryYardVideoRewardWindow(self.__armoryYardCtrl.getFinalRewardVehicle())

    def _showRewardWindow(self, result):
        if result.success:
            finalPostProgressionRewardStep = self.__armoryYardCtrl.getFinalPostProgressionRewardStep()
            bonuses = self.__armoryYardCtrl.getStepsRewards().get(finalPostProgressionRewardStep, {})
            showArmoryYardRewardWindow(bonuses=bonuses, state=SateView.STYLE, isFinalReward=True)

    def __onStartStage(self, stage, duration, skipCameraTransition=False):
        with self.__viewModel.transaction() as model:
            model.setAnimationLevel(stage)
            model.setLevelDuration(duration)
        self.__setSkipButton()
        self.__stageManager.pause()
        if not skipCameraTransition:
            self.__stageManager.gotToPositionByStage(stage, instantly=False)
        self.__stageManager.resume()

    def __playProgress(self, progress, stageCount=1, isReplay=False):
        if isReplay:
            self.__state.setReplayAnimation()
            self.__stageManager.startStages(progress, self.__lastPlayedStageID + 1, reset=True)
        else:
            self.__state.setBuilding()
            self.__stageManager.playProgress(progress, stageCount)
        with self.__viewModel.transaction() as model:
            model.setAnimationStatus(AnimationStatus.ACTIVE)
            model.setReplay(isReplay)

    def __onPlayAnimation(self):
        if self.__state.isAnimation:
            self.__onSkipAnimation()
        with self.__viewModel.transaction() as model:
            model.setRewardStatus(RewardStatus.ANIMATEDREWARDS)
        self.__playProgress(1, isReplay=True)

    def __updateProgress(self):
        progress = max(self.__lastPlayedStageID, self.__stageManager.getLastStageIndexToPlay())
        currentTokenCount = self.__armoryYardCtrl.getProgressionTokenCount()
        if currentTokenCount > progress:
            self.__playProgress(progress + 1, stageCount=currentTokenCount - progress)

    @decorators.adisp_process('loadPage')
    def __onCollectReward(self):
        stage = min(self.__armoryYardCtrl.getProgressionTokenCount(), self.__armoryYardCtrl.maxNumberOfSteps - 1) - self.__armoryYardCtrl.getProgressionLevel()
        action = factory.getAction(COLLECT_REWARDS, stage)
        result = yield factory.asyncDoAction(action)
        if result and self.__viewModel is not None:
            self.__updateCollectRewardsButton()
            currentLvl = self.__armoryYardCtrl.getCurrentProgress()
            with self.__viewModel.transaction() as model:
                model.setViewedLevel(currentLvl)
                model.setCurrentLevel(currentLvl)
        return

    def __onFinishStage(self, stage):
        self.__stageManager.gotToPositionByStage(stage)
        if self.__state.isBuilding:
            self.__setLastPlayedStageID(stage)
            self.__updateProgress()
            if stage >= self.__armoryYardCtrl.startStepOfPostProgression:
                self._checkAndShowRareRewardWindow()
            ctx = {'index': stage}
            g_eventBus.handleEvent(ArmoryYardEvent(ArmoryYardEvent.STAGE_FINISHED, ctx=ctx))
        if self.__state.isReplayAnimation and stage == self.__lastPlayedStageID:
            self.__state.reset()
            self.__updateProgress()
        if stage == self.__armoryYardCtrl.getProgressionTokenCount():
            self.__updateCollectRewardsButton()
            self.__state.reset()
        if not self.__state.isAnimation:
            with self.__viewModel.transaction() as model:
                model.setAnimationStatus(AnimationStatus.DISABLED)
                model.setReplay(True)

    def __firstEnterActions(self):
        self.__updateView()
        self.__updateCollectRewardsButton()
        self._checkAndShowRareRewardWindow()

    def _checkAndShowRareRewardWindow(self):
        if not self.__viewModel:
            return
        armoryCtrl = self.__armoryYardCtrl
        hasPostProgression = armoryCtrl.getFinalRewardStep() != armoryCtrl.getFinalPostProgressionRewardStep()
        if not self.__armoryYardCtrl.isClaimedProgressionReward() and self.__lastPlayedStageID >= self.__armoryYardCtrl.startStepOfPostProgression:
            if self.__unload or self._isBuyWindowLoad:
                return
            self.__claimRareReward(callback=self._showVideoRewardWindow)
        elif not self.__armoryYardCtrl.isClaimedPostProgressionReward() and self.__lastPlayedStageID == self.__armoryYardCtrl.maxNumberOfSteps and hasPostProgression:
            if self._isBuyWindowLoad:
                return
            self.__claimRareReward(callback=self._showRewardWindow)
        if self.__viewModel.getViewedLevel() == self.__armoryYardCtrl.maxNumberOfSteps:
            with self.__viewModel.transaction() as model:
                model.setViewedLevel(self.__armoryYardCtrl.maxNumberOfSteps)

    @adisp_process
    def __claimRareReward(self, callback):
        result = yield ClaimRareRewardProcessor().request()
        callback(result)

    def __updateCollectRewardsButton(self):
        if self.__armoryYardCtrl.hasCurrentRewards():
            self.__setGrabRewardsButton()
        else:
            self.__setEmptyRewardsButton()

    def __updateStage(self, progressUpdated=False):
        if not progressUpdated:
            self.__stageManager.setStage(max(0, self.__lastPlayedStageID))
        self.__stageManager.gotToPositionByStage(max(0, self.__lastPlayedStageID), instantly=not progressUpdated)

    @property
    def __lastPlayedStageID(self):
        progress = self.__settingsCore.serverSettings.getArmoryYardProgress()
        return min(progress, self.__armoryYardCtrl.maxNumberOfSteps)

    def __setLastPlayedStageID(self, stage):
        self.__settingsCore.serverSettings.setArmoryYardProgress(stage)

    def __onStartMoving(self):
        g_eventBus.handleEvent(LobbySimpleEvent(LobbySimpleEvent.NOTIFY_CURSOR_OVER_3DSCENE, ctx={'isOver3dScene': True}), EVENT_BUS_SCOPE.GLOBAL)

    def __onShowVehiclePreview(self):
        self.__armoryYardCtrl.showVehiclePreview(self.__state.isAnimation, self.__onSkipAnimation)

    def __onShowStylePreview(self):
        self.__armoryYardCtrl.showStylePreview(self.__state.isAnimation, self.__onSkipAnimation)

    def __onPlayStageContent(self, stage):
        stageId = stage.get('stageId', None) if stage else None
        if stageId is None:
            LOG_ERROR('stageId is not defined')
            return
        elif stageId > self.__armoryYardCtrl.getProgressionTokenCount():
            return
        else:
            stageVideoName = self.__stageManager.getStageVideoName(stageId)
            if stageVideoName:
                if self.__state.isAnimation:
                    self.__onSkipAnimation()
                self.__stageManager.playStageVideo(stageVideoName)
                return
            g_eventBus.handleEvent(ArmoryYardEvent(ArmoryYardEvent.STAGE_CLICKED, ctx={'stageId': int(stageId)}))
            return
