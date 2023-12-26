# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/gift_machine/ny_gift_machine_view.py
import logging
import typing
import BigWorld
from contextlib import contextmanager
from BWUtil import AsyncReturn
import CGF
from CurrentVehicle import g_currentPreviewVehicle
from account_helpers import AccountSettings
from account_helpers.AccountSettings import NY_GIFT_MACHINE_BUY_TOKEN_VISITED
from cgf_components.hangar_camera_manager import HangarCameraManager, CameraMode
from constants import PREBATTLE_TYPE
from gui.SystemMessages import SM_TYPE
from gui.impl import backport
from gui.impl.lobby.new_year.gift_machine import getRentDaysLeftByExpiryTime, getVehicleRewardSpecialArg
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import LobbySimpleEvent
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.game_control import IWalletController
from wg_async import AsyncScope, AsyncEvent, wg_async, BrokenPromiseError, wg_await
from gui import SystemMessages
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.components.ny_resource_model import NyResourceModel
from gui.impl.gen.view_models.views.lobby.new_year.views.gift_machine.ny_gift_machine_view_model import MachineState
from gui.impl.lobby.new_year.gift_machine.ny_gift_machine_bonuses_helper import getFormattedGiftBonuses
from gui.impl.lobby.new_year.gift_machine.ny_gift_machine_display_view import NyGiftMachineDisplayView
from gui.impl.lobby.new_year.ny_selectable_logic_presenter import SelectableLogicPresenter
from gui.impl.lobby.new_year.scene_rotatable_view import SceneRotatableView
from gui.impl.lobby.new_year.tooltips.ny_gift_machine_token_tooltip import NyGiftMachineTokenTooltip
from gui.impl.lobby.new_year.tooltips.ny_market_lack_the_res_tooltip import NyMarketLackTheResTooltip
from gui.impl.new_year.navigation import NewYearNavigation, ViewAliases
from gui.impl.new_year.sounds import NewYearSoundsManager, NewYearSoundEvents
from gui.impl.pub import WindowImpl
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.prb_control import prbDispatcherProperty, prb_getters
from gui.shared.event_dispatcher import showGiftMachineTokenPurchaseDialog, selectVehicleInHangar, hideSquadWindow
from helpers import dependency
from adisp import adisp_process
from frameworks.wulf import WindowFlags, WindowLayer
from items.components.ny_constants import NyCurrency
from new_year.gift_machine_helper import getCoinPrice
from new_year.ny_processor import ApplyNyCoinProcessor
from new_year.ny_constants import NYObjects, SyncDataKeys, NyTabBarChallengeView, GuestsQuestsTokens, RESOURCES_ORDER
from shared_utils import first
from skeletons.gui.shared.utils import IHangarSpace
from skeletons.new_year import IGiftMachineController, ICelebrityController, ICelebritySceneController
if typing.TYPE_CHECKING:
    from gui.impl.gen.view_models.views.lobby.new_year.views.gift_machine.ny_gift_machine_view_model import NyGiftMachineViewModel
    from typing import Dict
_logger = logging.getLogger(__name__)

class GiftMachineCamera(object):
    GIFT_MACHINE_CLOSE = 'GiftMachineClose'
    GIFT_MACHINE_VEH_PREVIEW = 'GiftMachineVehiclePreview'


_ACTIVATE_SELECTABLE_LOGIC_STATES = (MachineState.IDLE,
 MachineState.BUYTOKENS,
 MachineState.REWARDPREQUEL,
 MachineState.SPECIALREWARDPREQUEL,
 MachineState.REWARD,
 MachineState.SPECIALREWARD,
 MachineState.RAREREWARDPREQUEL,
 MachineState.RAREREWARD,
 MachineState.ERROR)
_ANIMATION_END_STATE_TRANSITION = {MachineState.SPECIALREWARDPREQUEL: MachineState.SPECIALREWARDPREVIEW,
 MachineState.REWARDPREQUEL: MachineState.REWARD,
 MachineState.SKIPSPECIALREWARDPREQUEL: MachineState.SPECIALREWARDPREVIEW,
 MachineState.SKIPREWARDPREQUEL: MachineState.REWARD,
 MachineState.RAREREWARDPREQUEL: MachineState.RAREREWARD,
 MachineState.SKIPRAREREWARDPREQUEL: MachineState.RAREREWARD}
_ANIMATION_SKIP_STATE_TRANSITION = {MachineState.SPECIALREWARDPREQUEL: MachineState.SKIPSPECIALREWARDPREQUEL,
 MachineState.REWARDPREQUEL: MachineState.SKIPREWARDPREQUEL,
 MachineState.RAREREWARDPREQUEL: MachineState.SKIPRAREREWARDPREQUEL}
_CAM_OBJECT_BY_VIEW_STATE = {MachineState.IDLE: NYObjects.GIFT_MACHINE,
 MachineState.REWARD: GiftMachineCamera.GIFT_MACHINE_CLOSE,
 MachineState.REWARDPREQUEL: GiftMachineCamera.GIFT_MACHINE_CLOSE,
 MachineState.SPECIALREWARD: GiftMachineCamera.GIFT_MACHINE_CLOSE,
 MachineState.SPECIALREWARDPREQUEL: GiftMachineCamera.GIFT_MACHINE_CLOSE,
 MachineState.RAREREWARDPREQUEL: GiftMachineCamera.GIFT_MACHINE_CLOSE,
 MachineState.RAREREWARD: GiftMachineCamera.GIFT_MACHINE_CLOSE,
 MachineState.ERROR: GiftMachineCamera.GIFT_MACHINE_CLOSE,
 MachineState.BUYTOKENS: NYObjects.GIFT_MACHINE_SIDE}
_STATES_WITHOUT_MESSAGE_BAR = (MachineState.REWARD,
 MachineState.REWARDPREQUEL,
 MachineState.SKIPREWARDPREQUEL,
 MachineState.SPECIALREWARD,
 MachineState.SPECIALREWARDPREQUEL,
 MachineState.SPECIALREWARDPREVIEW,
 MachineState.SKIPSPECIALREWARDPREQUEL,
 MachineState.RAREREWARD,
 MachineState.RAREREWARDPREQUEL,
 MachineState.SKIPRAREREWARDPREQUEL,
 MachineState.ERROR)
_ALLOW_CAM_OBJECTS = _CAM_OBJECT_BY_VIEW_STATE.values() + list(CameraMode.ALL)
_CHANGE_LAYERS_VISIBILITY = (WindowLayer.WINDOW,)
_VIEW_STATE_BY_CAM_OBJECT = {v:k for k, v in _CAM_OBJECT_BY_VIEW_STATE.iteritems()}
_TRANSITION_HOLD_TIME = 15
_RARE_ITEMS_REWARDS = [[38649], [39417], [40185]]
_TEXTURE_PATH = 'content/Hangars/h30_newyear_2021/environment/h30_NY23_006_Machine_Screen_AM.dds'

def isRareReward(reward):
    if reward:
        bonusName = reward.get('bonusName', '')
        if bonusName == 'equipCoin':
            return True
        if bonusName == 'items' and reward.get('specialArgs') in _RARE_ITEMS_REWARDS:
            return True
    return False


def isRewardVehicle(reward):
    return reward and reward.get('bonusName', '') == 'vehicles'


class GiftMachineCameraHelper(object):
    __hangarSpace = dependency.descriptor(IHangarSpace)

    def __init__(self):
        super(GiftMachineCameraHelper, self).__init__()
        self.__scope = AsyncScope()
        self.__event = AsyncEvent(scope=self.__scope)
        self.__cameraManager = None
        self.__inited = False
        return

    @contextmanager
    def start(self):
        self.__initialize()
        yield self
        self.__finalize()

    def destroy(self):
        if self.__cameraManager and NewYearNavigation.getCurrentObject() == NYObjects.GIFT_MACHINE:
            self.__cameraManager.switchByCameraName(NYObjects.GIFT_MACHINE)
        self.__finalize()
        if self.__isVehicleSwitched():
            self.__selectPreviewVehicle()

    def forceRelease(self):
        self._releaseAsync(False)

    def getCurrentCamObjectName(self):
        if self.__cameraManager is None:
            self.__cameraManager = CGF.getManager(self.__hangarSpace.spaceID, HangarCameraManager)
        return self.__cameraManager.getCurrentCameraName() if self.__cameraManager is not None else None

    @wg_async
    def wait(self, state, reward):
        self.__applyState(state, reward)
        try:
            yield wg_await(self.__event.wait())
        except BrokenPromiseError:
            _logger.debug('%s has been destroyed without user decision', self)

        raise AsyncReturn(self.__result)

    def _releaseAsync(self, result):
        self.__result = result
        self.__event.set()

    def __initialize(self):
        self.__cameraManager = CGF.getManager(self.__hangarSpace.spaceID, HangarCameraManager)
        self.__cameraManager.onCameraSwitched += self.__onCameraSwitched
        self.__hangarSpace.onVehicleChanged += self.__onVehicleChanged
        self.__hangarSpace.onSpaceDestroy += self.__onSpaceDestroy
        self.__event.clear()
        self.__inited = True

    def __finalize(self):
        if not self.__inited:
            return
        else:
            if self.__cameraManager:
                self.__cameraManager.onCameraSwitched -= self.__onCameraSwitched
                self.__cameraManager = None
            self.__hangarSpace.onVehicleChanged -= self.__onVehicleChanged
            self.__hangarSpace.onSpaceDestroy -= self.__onSpaceDestroy
            self.__inited = False
            return

    def __onSpaceDestroy(self, inited):
        if inited:
            self.__finalize()

    def __applyState(self, state, reward):
        if state == MachineState.SPECIALREWARDPREVIEW:
            vehIntCD = getVehicleRewardSpecialArg(reward, 0)
            if vehIntCD:
                self.__selectPreviewVehicle(vehIntCD)
            else:
                self._releaseAsync(False)
        else:
            self.__switchCamByState(state)

    def __switchCamByState(self, state):
        if NewYearNavigation.getNavigationState().isCloseMainViewInProcess:
            return
        if state == MachineState.SPECIALREWARDPREVIEW:
            self.__cameraManager.switchToTank(False)
            return
        camObj = _CAM_OBJECT_BY_VIEW_STATE.get(state)
        if camObj:
            self.__cameraManager.switchByCameraName(camObj, False)
        else:
            self._releaseAsync(True)

    def __onCameraSwitched(self, camName):
        if camName not in _ALLOW_CAM_OBJECTS:
            return
        self.__processAfterCamSwitched(camName)

    def __processAfterCamSwitched(self, camName):
        if self.__isVehicleSwitched() and camName not in CameraMode.ALL:
            self.__selectPreviewVehicle()
        self._releaseAsync(True)

    def __selectPreviewVehicle(self, vehIntCD=None):
        g_currentPreviewVehicle.selectVehicle(vehIntCD, None, None, waitingSoftStart=True, showWaitingBg=False)
        return

    def __isVehicleSwitched(self):
        return bool(g_currentPreviewVehicle.item)

    def __onVehicleChanged(self):
        if self.__isVehicleSwitched():
            self.__switchCamByState(MachineState.SPECIALREWARDPREVIEW)
        else:
            self._releaseAsync(True)


class NyGiftMachineView(SceneRotatableView, SelectableLogicPresenter):
    __slots__ = ('__cameraHelper', '__displayView', '__storedReward', '__isCameraHelperActive', '__isMessageBarVisible', '__redButtonPressCallbackID', '__returnToIdleCallbackID', '__onCoinsUpdateCallbackID')
    __nyGiftMachineCtrl = dependency.descriptor(IGiftMachineController)
    __celebrityController = dependency.descriptor(ICelebrityController)
    __celebritySceneController = dependency.descriptor(ICelebritySceneController)
    __appLoader = dependency.instance(IAppLoader)
    __wallet = dependency.descriptor(IWalletController)

    def __init__(self, viewModel, parentView, soundConfig=None):
        super(NyGiftMachineView, self).__init__(viewModel, parentView, soundConfig)
        self.__cameraHelper = None
        self.__displayView = None
        self.__storedReward = None
        self.__isCameraHelperActive = False
        self.__isMessageBarVisible = True
        self.__redButtonPressCallbackID = None
        self.__returnToIdleCallbackID = None
        self.__onCoinsUpdateCallbackID = None
        return

    @property
    def viewModel(self):
        return self.getViewModel()

    @prbDispatcherProperty
    def prbDispatcher(self):
        pass

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.new_year.tooltips.NyGiftMachineTokenTooltip():
            return NyGiftMachineTokenTooltip()
        return NyMarketLackTheResTooltip(str(event.getArgument('resourceType')), int(event.getArgument('price'))) if contentID == R.views.lobby.new_year.tooltips.NyMarketLackTheResTooltip() else super(NyGiftMachineView, self).createToolTipContent(event, contentID)

    def preLoad(self, *args, **kwargs):
        self.__createDisplayView()

    def initialize(self, *args, **kwargs):
        super(NyGiftMachineView, self).initialize(*args, **kwargs)
        self.isMoveSpaceEnable(False)
        self.__onSwitchActive(False)
        self.__cameraHelper = GiftMachineCameraHelper()
        coinPrice = getCoinPrice()
        with self.viewModel.transaction() as model:
            tokenPrice = model.getTokenPrice()
            tokenPrice.clear()
            for currency in NyCurrency.ALL:
                resourceModel = NyResourceModel()
                resourceModel.setType(currency)
                resourceModel.setValue(coinPrice)
                tokenPrice.addViewModel(resourceModel)

            tokenPrice.invalidate()
            self.__onNyCoinsUpdate(model=model)
            self.__updateResources(model=model)
            self.__updateWalletStatus(model=model)
            self.__updateConditions(model=model)
            self.__setStartState(model=model)
            model.setIsInSquad(self.__isInSquad())

    def finalize(self):
        super(NyGiftMachineView, self).finalize()
        self.__clearRedButtonCallback()
        self.__clearReturnToIdleCallback()
        self.__clearOnCoinsUpdateCallback()
        self.__displayView.viewModel.onRewardAnimationEnd -= self.__onRewardAnimationEnd
        self.__displayView.destroyWindow()
        self.__displayView = None
        self.__cameraHelper.destroy()
        self.__cameraHelper = None
        self.__storedReward = None
        self.__changeLayersVisibility(False, _CHANGE_LAYERS_VISIBILITY)
        self.__changeMessageBarVisibility(True)
        self.__nyGiftMachineCtrl.updateGiftMachineBusyStatus(False)
        return

    def _getEvents(self):
        events = super(NyGiftMachineView, self)._getEvents()
        unitMgr = prb_getters.getClientUnitMgr()
        if unitMgr:
            events += ((unitMgr.onUnitJoined, self.__onUnitStatusUpdated), (unitMgr.onUnitLeft, self.__onUnitStatusUpdated))
        return events + ((self.viewModel.onGoToBuyTokens, self.__onGoToBuyTokens),
         (self.viewModel.onGoToIdle, self.__onGoToIdle),
         (self.viewModel.onBuyTokens, self.__onBuyTokens),
         (self.viewModel.onSkipAnimation, self.__onSkipAnimation),
         (self.viewModel.onBackFromVehiclePreview, self.__onBackFromVehiclePreview),
         (self.viewModel.onGoToHangar, self.__onGoToHangar),
         (self.viewModel.onGoToChallengeGuest, self.__onGoToChallengeGuest),
         (self.viewModel.onGoToVillage, self.__onGoToVillage),
         (self._nyController.onDataUpdated, self.__onNyDataUpdate),
         (self._nyController.currencies.onBalanceUpdated, self.__onBalanceUpdated),
         (self._nyController.currencies.onNyCoinsUpdate, self.__onNyCoinsUpdate),
         (self.__nyGiftMachineCtrl.onRedButtonPress, self.__onRedButtonPress),
         (self.__celebrityController.onCelebCompletedTokensUpdated, self.__onCompletedTokensChanged),
         (self.__celebritySceneController.onQuestsUpdated, self.__onCallengeQuestsUpdated),
         (self.__wallet.onWalletStatusChanged, self.__onWalletStatusChanged),
         (NewYearNavigation.onUpdateCurrentView, self.__onUpdateView))

    def __onUnitStatusUpdated(self, *_):
        self.viewModel.setIsInSquad(self.__isInSquad())

    def __onUpdateView(self, *_, **kwargs):
        if kwargs.get('viewAlias', NewYearNavigation.getCurrentViewName()) != ViewAliases.GIFT_MACHINE:
            return
        currentObject = kwargs.get('currentObject', NewYearNavigation.getCurrentObject())
        if currentObject == NYObjects.GIFT_MACHINE:
            newState = _VIEW_STATE_BY_CAM_OBJECT.get(currentObject, NYObjects.GIFT_MACHINE)
            self.__changeState(newState)

    def __onNyDataUpdate(self, diff, _):
        if SyncDataKeys.LEVEL in diff:
            self.__onCompletedTokensChanged()

    def __onCompletedTokensChanged(self):
        self.__updateConditions()

    def __onCallengeQuestsUpdated(self):
        self.__updateConditions()

    @replaceNoneKwargsModel
    def __updateConditions(self, model=None):
        model.setIsMaxAtmosphereLevel(self._nyController.isMaxAtmosphereLevel())
        model.setIsGuestQuestsCompleted(self.__celebrityController.isGuestQuestsCompletedFully((GuestsQuestsTokens.GUEST_A,)))

    @replaceNoneKwargsModel
    def __updateResources(self, model=None):
        resources = model.getResources()
        resources.clear()
        for resource in RESOURCES_ORDER:
            amount = self._nyController.currencies.getResouceBalance(resource.value)
            resourceModel = NyResourceModel()
            resourceModel.setType(resource.value)
            resourceModel.setValue(amount)
            resources.addViewModel(resourceModel)

        resources.invalidate()

    def __onBalanceUpdated(self):
        self.__updateResources()

    @replaceNoneKwargsModel
    def __onNyCoinsUpdate(self, model=None):
        self.__onCoinsUpdateCallbackID = None
        if self.__isCameraHelperActive:
            return
        else:
            count = self._nyController.currencies.getCoinsCount()
            if self.__displayView is None:
                return
            self.__displayView.updateTokens(count)
            model.setTokenCount(count)
            return

    @replaceNoneKwargsModel
    def __preUpdateState(self, state, model=None):
        model.setMachineState(state)
        self.__changeLayersVisibility(state not in (MachineState.IDLE, MachineState.BUYTOKENS), _CHANGE_LAYERS_VISIBILITY)
        self.__changeMessageBarVisibility(state not in _STATES_WITHOUT_MESSAGE_BAR)

    @replaceNoneKwargsModel
    def __updateState(self, state, model=None):
        if self.__displayView is None:
            return
        else:
            self.__displayView.updateState(state)
            model.setMachineState(state)
            isInVehiclePreview = state == MachineState.SPECIALREWARDPREVIEW
            self.isMoveSpaceEnable(isInVehiclePreview)
            self._updateSelectVehicleEntity(isInVehiclePreview)
            self.__nyGiftMachineCtrl.setMachineState(state)
            if state == MachineState.BUYTOKENS and self.__nyGiftMachineCtrl.isBuyingCoinsAvailable:
                AccountSettings.setUIFlag(NY_GIFT_MACHINE_BUY_TOKEN_VISITED, True)
            if state in _ACTIVATE_SELECTABLE_LOGIC_STATES:
                self._activateSelectableLogic()
            NewYearSoundsManager.setGiftMachineState(state is MachineState.BUYTOKENS)
            return

    def __onRedButtonPress(self):
        if self.__redButtonPressCallbackID is not None:
            return
        else:
            self.viewModel.setIsWaitRequest(True)
            self.__redButtonPressCallbackID = BigWorld.callback(0.2, self.__redButtonPress)
            return

    def __clearRedButtonCallback(self):
        if self.__redButtonPressCallbackID is not None:
            BigWorld.cancelCallback(self.__redButtonPressCallbackID)
            self.__redButtonPressCallbackID = None
        return

    def __clearReturnToIdleCallback(self):
        if self.__returnToIdleCallbackID is not None:
            BigWorld.cancelCallback(self.__returnToIdleCallbackID)
            self.__returnToIdleCallbackID = None
        return

    def __clearOnCoinsUpdateCallback(self):
        if self.__onCoinsUpdateCallbackID is not None:
            BigWorld.cancelCallback(self.__onCoinsUpdateCallbackID)
            self.__onCoinsUpdateCallbackID = None
        return

    def __redButtonPress(self):
        self.__clearRedButtonCallback()
        self.__clearReturnToIdleCallback()
        if NewYearNavigation.getNavigationState().isCloseMainViewInProcess or NewYearNavigation.getCurrentObject() != NYObjects.GIFT_MACHINE or NewYearNavigation.getCurrentViewName() != ViewAliases.GIFT_MACHINE:
            return
        if self.__nyGiftMachineCtrl.canApplyCoin:
            self.__tryApplyCoin()
        elif self.__nyGiftMachineCtrl.canRedButtonPress:
            self.__skipAnim()
        self.viewModel.setIsWaitRequest(False)

    def __returnToIdle(self):
        self.__clearReturnToIdleCallback()
        if NewYearNavigation.getNavigationState().isCloseMainViewInProcess:
            return
        self.__onGoToIdle()

    def __skipAnim(self):
        toState = _ANIMATION_SKIP_STATE_TRANSITION.get(self.__nyGiftMachineCtrl.machineState)
        if toState:
            self.__changeState(toState)

    def __updateRequestState(self, isInRequest):
        self.viewModel.setIsInRequest(isInRequest)
        self.__nyGiftMachineCtrl.setInRequestState(isInRequest)

    @adisp_process
    def __tryApplyCoin(self):
        coins = self._nyController.currencies.getCoins()
        self.__updateRequestState(True)
        result = yield ApplyNyCoinProcessor(coins).request()
        self.__updateRequestState(False)
        if result:
            if result.userMsg:
                SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)
            rewards = None
            if result.success:
                rewardsList = result.auxData.get('bonus')
                if rewardsList:
                    rewards = rewardsList[0]
                else:
                    SystemMessages.pushMessage(backport.text(R.strings.system_messages.newYear.coin23.apply.server_error()), type=SM_TYPE.Error)
                    return
            self.__onCoinApplied(result.success, rewards)
            NewYearSoundsManager.setGiftMachineAnimState(True)
        return

    def __onCoinApplied(self, success, rewards):
        hideSquadWindow()
        reward = None
        state = MachineState.ERROR
        if success and rewards:
            bonuses = getFormattedGiftBonuses(rewards)
            if bonuses:
                reward = first(bonuses)
                if isRewardVehicle(reward):
                    state = MachineState.SPECIALREWARDPREQUEL
                elif isRareReward(reward):
                    state = MachineState.RAREREWARDPREQUEL
                else:
                    state = MachineState.REWARDPREQUEL
        self.__changeState(state, reward)
        return

    @wg_async
    def __changeState(self, state, reward=None):
        if self.__nyGiftMachineCtrl.isGiftMachineBusy:
            return
        self.__clearReturnToIdleCallback()
        self.__onSwitchActive(True)
        self.__preUpdateState(state)
        with self.__cameraHelper.start() as cameraHelper:
            self.__isCameraHelperActive = True
            result = yield wg_await(cameraHelper.wait(state, reward))
        self.__isCameraHelperActive = False
        if result is False:
            state = MachineState.ERROR
        self.__fillRewardModel(state, reward)
        self.__updateState(state)
        self.__onCoinsUpdateCallbackID = BigWorld.callback(0.1, self.__onNyCoinsUpdate)
        self.__onSwitchActive(False)

    def __onSwitchActive(self, isInSwitching):
        self.__nyGiftMachineCtrl.updateGiftMachineBusyStatus(isInSwitching)
        self.viewModel.setIsCameraSwitching(isInSwitching)
        if isInSwitching:
            self._deactivateSelectableLogic()
            self.isMoveSpaceEnable(False)

    def __onGoToBuyTokens(self):
        NewYearSoundsManager.playEvent(NewYearSoundEvents.GIFT_MACHINE_SWITCH)
        self.__changeState(MachineState.BUYTOKENS)

    def __onGoToIdle(self):
        NewYearSoundsManager.playEvent(NewYearSoundEvents.GIFT_MACHINE_SWITCH)
        self.__changeState(MachineState.IDLE)

    def __onBackFromVehiclePreview(self):
        NewYearSoundsManager.playEvent(NewYearSoundEvents.GIFT_MACHINE_DEFAULT_TRANSITION)
        self.__changeState(MachineState.SPECIALREWARD)

    def __isInSquad(self):
        return self.prbDispatcher.getFunctionalState().isInUnit(PREBATTLE_TYPE.SQUAD) if self.prbDispatcher is not None else False

    def __onGoToHangar(self, args):
        if not self.__isInSquad():
            vehIntCD = int(args.get('vehIntCD', 0))
            veh = self._itemsCache.items.getItemByCD(vehIntCD)
            if not veh.isInInventory:
                return
            selectVehicleInHangar(vehIntCD, loadHangar=False)
        NewYearNavigation.closeMainView()

    def __onRewardAnimationEnd(self):
        toState = _ANIMATION_END_STATE_TRANSITION.get(self.__nyGiftMachineCtrl.machineState)
        if toState and self.__storedReward:
            self.__changeState(toState, self.__storedReward)
            self.__storedReward = None
            self.__returnToIdleCallbackID = BigWorld.callback(_TRANSITION_HOLD_TIME, self.__returnToIdle)
        NewYearSoundsManager.setGiftMachineAnimState(False)
        return

    def __fillRewardModel(self, state, reward):
        if reward is None:
            return
        else:
            if state in (MachineState.REWARDPREQUEL, MachineState.SPECIALREWARDPREQUEL, MachineState.RAREREWARDPREQUEL):
                isVehicleReward = isRewardVehicle(reward)
                if self.__displayView:
                    self.__displayView.fillReward(isVehicleReward, reward)
                if isVehicleReward:
                    self.__fillVehiclePreview(reward)
                self.__storedReward = reward
            return

    def __fillVehiclePreview(self, reward):
        vehIntCD = getVehicleRewardSpecialArg(reward, 0)
        vehicle = self._itemsCache.items.getItemByCD(vehIntCD)
        with self.viewModel.transaction() as model:
            rewardModel = model.vehiclePreview
            rewardModel.setRentDays(getRentDaysLeftByExpiryTime(getVehicleRewardSpecialArg(reward, 2, 0)))
            rewardModel.setRentBattles(getVehicleRewardSpecialArg(reward, 3, 0))
            rewardModel.setVehIntCD(vehIntCD)
            vehicleInfo = rewardModel.vehicleInfo
            vehicleInfo.setVehicleName(vehicle.userName)
            vehicleInfo.setVehicleType(vehicle.type)
            vehicleInfo.setVehicleLvl(vehicle.level)
            vehicleInfo.setIsElite(vehicle.isElite)

    def __onBuyTokens(self, args):
        resource = str(args.get('resource', NyCurrency.CRYSTAL))
        amount = int(args.get('amount', 0))
        if amount > 0 and resource in NyCurrency.ALL:
            showGiftMachineTokenPurchaseDialog(resource, amount)

    def __onSkipAnimation(self):
        NewYearSoundsManager.playEvent(NewYearSoundEvents.GIFT_MACHINE_DEFAULT_TRANSITION)
        self.__onRedButtonPress()

    def __onGoToChallengeGuest(self):
        self._goToCelebrityView(tabName=NyTabBarChallengeView.GUEST_A)

    def __onGoToVillage(self):
        self._goToMainView(tabName=NYObjects.TOWN)

    def __createDisplayView(self):
        if self.__displayView is None:
            self.__displayView = NyGiftMachineDisplayView()
            window = WindowImpl(WindowFlags.SURFACE, content=self.__displayView, layer=WindowLayer.VIEW, name=_TEXTURE_PATH)
            window.load()
            self.__onNyCoinsUpdate()
            self.__displayView.viewModel.onRewardAnimationEnd += self.__onRewardAnimationEnd
        return

    def __setStartState(self, model=None):
        curObj = NewYearNavigation.getCurrentObject()
        if curObj == NYObjects.GIFT_MACHINE_SIDE:
            self.__updateState(MachineState.BUYTOKENS, model=model)
        else:
            self.__changeState(MachineState.IDLE)

    def __changeMessageBarVisibility(self, visible):
        if self.__isMessageBarVisible == visible:
            return
        self.__isMessageBarVisible = visible
        g_eventBus.handleEvent(LobbySimpleEvent(LobbySimpleEvent.MESSENGER_BAR_VISIBLE, ctx={'visible': visible}), scope=EVENT_BUS_SCOPE.LOBBY)

    def __changeLayersVisibility(self, isHide, layers):
        lobby = self.__appLoader.getDefLobbyApp()
        if lobby:
            if isHide:
                lobby.containerManager.hideContainers(layers, time=0.3)
            else:
                lobby.containerManager.showContainers(layers, time=0.3)
            self.__appLoader.getApp().graphicsOptimizationManager.switchOptimizationEnabled(not isHide)

    def __onWalletStatusChanged(self, *_):
        self.__updateWalletStatus()

    @replaceNoneKwargsModel
    def __updateWalletStatus(self, model=None):
        model.setIsWalletAvailable(self.__wallet.isAvailable)
