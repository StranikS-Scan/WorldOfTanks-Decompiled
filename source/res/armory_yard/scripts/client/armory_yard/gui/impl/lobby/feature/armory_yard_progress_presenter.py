# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: armory_yard/scripts/client/armory_yard/gui/impl/lobby/feature/armory_yard_progress_presenter.py
import BigWorld
from armory_yard.gui.shared.gui_items.items_actions import COLLECT_REWARDS
from armory_yard_constants import State
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.gui_items.items_actions import factory
from gui.shared.utils import decorators
from shared_utils import first
from armory_yard.gui.impl.gen.view_models.views.lobby.feature.armory_yard_main_view_model import ArmoryYardMainViewModel, AnimationStatus, ArmoryYardLevelModel, RewardStatus, BuyButtonState
from armory_yard.gui.impl.gen.view_models.views.lobby.feature.armory_yard_main_view_model import EscSource
from armory_yard.gui.shared.bonus_packers import getArmoryYardBuyViewPacker, packVehicleModel
from armory_yard.gui.shared.bonuses_sorter import bonusesSortKeyFunc
from Event import SuspendableEventSubscriber
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import LobbySimpleEvent, ArmoryYardEvent
from gui.shared.missions.packers.bonus import BACKPORT_TOOLTIP_CONTENT_ID
from gui.hangar_cameras.hangar_camera_common import CameraRelatedEvents
from gui.impl.backport import createTooltipData
from gui.impl.lobby.common.view_helpers import packBonusModelAndTooltipData
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.server_events.bonuses import getNonQuestBonuses, mergeBonuses, splitBonuses
from helpers import dependency
from skeletons.gui.game_control import IArmoryYardController
from skeletons.account_helpers.settings_core import ISettingsCore
from armory_yard.gui.window_events import showArmoryYardVideoRewardWindow, showArmoryYardInfoPage, showArmoryYardBuyWindow, showArmoryYardVehiclePreview, showArmoryYardBundlesWindow, showArmoryYardShopWindow, showArmoryYardPostProgressionBuyWindow
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
        self.__playAnimationLastID = None
        self.__closeCB = closeCB
        self.__eventsSubscriber = SuspendableEventSubscriber()
        self.__parent = None
        self.__state = _InternalState()
        self.__unload = False
        return

    def init(self, parent):
        self.__parent = parent
        self.__eventsSubscriber.subscribeToEvents((self.__armoryYardCtrl.serverSettings.onUpdated, self.__onServerSettingsUpdated), (self.__armoryYardCtrl.onAYCoinsUpdate, self.__onAYCoinsUpdate), (self.__stageManager.onStartStage, self.__onStartStage), (self.__stageManager.onFinishStage, self.__onFinishStage), (self.__viewModel.onCollectReward, self.__onCollectReward), (self.__viewModel.onPlayAnimation, self.__onPlayAnimation), (self.__armoryYardCtrl.onProgressUpdated, self.__onProgressUpdate), (self.__armoryYardCtrl.onCollectFinalReward, self._checkAndShowFinalRewardWindow), (self.__viewModel.onAboutEvent, self.__onAboutEvent), (self.__viewModel.onClose, self.__closeView), (self.__viewModel.onSkipAnimation, self.__onSkipAnimation), (self.__viewModel.onMoveSpace, self.__onMoveSpace), (self.__viewModel.onBuyTokens, self.__onBuyTokens), (self.__viewModel.onStartMoving, self.__onStartMoving), (self.__viewModel.onShowVehiclePreview, self.__onShowVehiclePreview), (self.__armoryYardCtrl.onStatusChange, self.__updateState), (self.__viewModel.onShopOpen, self.__onShopOpen))
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
            model.setViewedLevel(self.__armoryYardCtrl.getProgressionLevel() + int(self.__armoryYardCtrl.isClaimedFinalReward()))
            model.setCurrentLevel(self.__armoryYardCtrl.getCurrentProgress())
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
        if key is not None and type is not None:
            if type == ArmoryYardMainViewModel.FINAL_REWARD_TOOLTIP_TYPE:
                return self.__tooltipData.get(type, {}).get(key, None)
            return self.__tooltipData.get(key, {})
        else:
            return

    def onUnload(self):
        self.__eventsSubscriber.pause()
        self.__unload = True
        if self.__state.isAnimation:
            self.__onSkipAnimation()
        g_eventBus.handleEvent(LobbySimpleEvent(LobbySimpleEvent.NOTIFY_CURSOR_OVER_3DSCENE, ctx={'isOver3dScene': False}), EVENT_BUS_SCOPE.GLOBAL)

    def __checkBuyButton(self, model):
        if self.__armoryYardCtrl.payedTokensLeft() == 0:
            model.setBuyButtonState(BuyButtonState.HIDDEN)
            return
        if self.__armoryYardCtrl.isPostProgressionActive():
            model.setBuyButtonState(BuyButtonState.COINS)
        elif not self.__armoryYardCtrl.isClaimedFinalReward():
            model.setBuyButtonState(BuyButtonState.TOKENS)
        else:
            model.setBuyButtonState(BuyButtonState.HIDDEN)

    def __onMoveSpace(self, args=None):
        if args is None:
            return
        else:
            g_eventBus.handleEvent(CameraRelatedEvents(CameraRelatedEvents.LOBBY_VIEW_MOUSE_MOVE, ctx={'dx': args.get('dx'),
             'dy': args.get('dy'),
             'dz': args.get('dz')}), EVENT_BUS_SCOPE.GLOBAL)
            return

    def __onBuyTokens(self):
        if self.__armoryYardCtrl.payedTokensLeft() == 0:
            return
        if self.__armoryYardCtrl.isCompleted():
            if self.__armoryYardCtrl.isPostProgressionActive():
                showArmoryYardPostProgressionBuyWindow(parent=self.__parent)
            return
        if self.__armoryYardCtrl.isStarterPackAvailable():
            showArmoryYardBundlesWindow(parent=self.__parent)
        else:
            showArmoryYardBuyWindow(parent=self.__parent)

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
            stage = self.__armoryYardCtrl.getCurrencyTokenCount()
            if self.__state.isBuilding:
                self.__setLastPlayedStageID(stage)
                if not isClosing:
                    self._checkAndShowFinalRewardWindow()
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
        self._checkAndShowFinalRewardWindow()

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
        self.__fillFinalReward()

    def __fillFinalReward(self):
        finalRewardVehicle = self.__armoryYardCtrl.getFinalRewardVehicle()
        if not finalRewardVehicle:
            return
        with self.__viewModel.transaction() as model:
            packVehicleModel(model.finalReward, finalRewardVehicle)
            self.__tooltipData[ArmoryYardMainViewModel.FINAL_REWARD_TOOLTIP_TYPE] = {'0': createTooltipData(isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.ARMORY_YARD_AWARD_VEHICLE, specialArgs=[finalRewardVehicle.intCD])}
            model.finalReward.setTooltipContentId(str(BACKPORT_TOOLTIP_CONTENT_ID))
            model.finalReward.setTooltipId('0')

    def _closeIntroView(self):
        self.__updateView()

    def __updateProgressionTimes(self, model):
        state = self.__armoryYardCtrl.getState()
        startTime, endTime = self.__armoryYardCtrl.getPostProgressionTimes() if state == State.POSTPROGRESSION else self.__armoryYardCtrl.getProgressionTimes()
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
        for stepNum in range(1, self.__armoryYardCtrl.getTotalSteps() + 1):
            stepModel = ArmoryYardLevelModel()
            stepModel.setLevel(stepNum)
            stepRewardsModel = stepModel.getRewards()
            stepRewardsModel.clear()
            stepRewards = []
            for itemType, itemID in stepsRewards[stepNum].iteritems():
                stepRewards.extend(getNonQuestBonuses(itemType, itemID))

            stepRewards = splitBonuses(mergeBonuses(stepRewards))
            stepRewards.sort(key=bonusesSortKeyFunc)
            packBonusModelAndTooltipData(stepRewards, stepRewardsModel, self.__tooltipData, getArmoryYardBuyViewPacker())
            stepRewardsModel.invalidate()
            steps.addViewModel(stepModel)

        steps.invalidate()

    def _showVideoRewardWindow(self):
        showArmoryYardVideoRewardWindow(self.__armoryYardCtrl.getFinalRewardVehicle())

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
        currentTokenCount = self.__armoryYardCtrl.getCurrencyTokenCount()
        if currentTokenCount > progress:
            self.__playProgress(progress + 1, stageCount=currentTokenCount - progress)

    @decorators.adisp_process('loadPage')
    def __onCollectReward(self):
        stage = min(self.__armoryYardCtrl.getCurrencyTokenCount(), self.__armoryYardCtrl.getTotalSteps() - 1) - self.__armoryYardCtrl.getProgressionLevel()
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
            if stage == self.__armoryYardCtrl.getTotalSteps():
                self._checkAndShowFinalRewardWindow()
            ctx = {'index': stage}
            g_eventBus.handleEvent(ArmoryYardEvent(ArmoryYardEvent.STAGE_FINISHED, ctx=ctx))
        if self.__state.isReplayAnimation and stage == self.__lastPlayedStageID:
            self.__state.reset()
            self.__updateProgress()
        if stage == self.__armoryYardCtrl.getCurrencyTokenCount():
            self.__updateCollectRewardsButton()
            self.__state.reset()
        if not self.__state.isAnimation:
            with self.__viewModel.transaction() as model:
                model.setAnimationStatus(AnimationStatus.DISABLED)
                model.setReplay(True)

    def __firstEnterActions(self):
        self.__updateView()
        self.__updateCollectRewardsButton()
        self._checkAndShowFinalRewardWindow()

    def _checkAndShowFinalRewardWindow(self):
        if self.__lastPlayedStageID != self.__armoryYardCtrl.getTotalSteps() or self.__armoryYardCtrl.isClaimedFinalReward() or not self.__armoryYardCtrl.isFinalQuestCompleted:
            return
        if self.__unload:
            return
        self._showVideoRewardWindow()
        BigWorld.player().AccountArmoryYardComponent.claimFinalReward()
        if self.__viewModel.getViewedLevel() == self.__armoryYardCtrl.getTotalSteps() - 1:
            with self.__viewModel.transaction() as model:
                model.setViewedLevel(self.__armoryYardCtrl.getTotalSteps())

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
        return min(progress, self.__armoryYardCtrl.getTotalSteps())

    def __setLastPlayedStageID(self, stage):
        self.__settingsCore.serverSettings.setArmoryYardProgress(stage)

    def __onStartMoving(self):
        g_eventBus.handleEvent(LobbySimpleEvent(LobbySimpleEvent.NOTIFY_CURSOR_OVER_3DSCENE, ctx={'isOver3dScene': True}), EVENT_BUS_SCOPE.GLOBAL)

    def __onShowVehiclePreview(self):
        vehicle = self.__armoryYardCtrl.getFinalRewardVehicle()
        if vehicle is None:
            return
        elif self.__state.isAnimation:
            self.__onSkipAnimation()
            return
        else:
            self.__armoryYardCtrl.isVehiclePreview = True
            showArmoryYardVehiclePreview(vehicle.intCD, backToHangar=False, showHeroTankText=False, previewBackCb=self.__armoryYardCtrl.goToArmoryYard, backBtnLabel=backport.text(R.strings.armory_yard.buyView.backButton.mainView()))
            self.__armoryYardCtrl.cameraManager.goToHangar()
            return
