# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/lobby/new_year/surprise_machine/surprise_machine_view.py
import copy
import typing
import BigWorld
import SoundGroups
from gui.impl.gen import R
from functools import partial
from gui.impl import backport
from gui import SystemMessages
from adisp import adisp_process
from gui.impl.pub import WindowImpl
from gui.SystemMessages import SM_TYPE
from frameworks.wulf import WindowLayer, WindowFlags
from gui.shared.event_dispatcher import selectVehicleInHangar
from gui.shared.notifications import NotificationPriorityLevel
from gui.server_events.bonuses import getMergedBonusesFromDicts
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.impl.lobby.loot_box.loot_box_helper import getLootBoxIDFromToken
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.shared.gui_items.processors.loot_boxes import LootBoxOpenProcessor
from gui.battle_pass.battle_pass_decorators import createBackportTooltipDecorator
from new_year.gui.impl.gen.view_models.views.lobby.new_year.tooltips.ny_main_widget_tooltip_model import WidgetBlock
from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.surprise_machine.ny_surprise_machine_model import PurchaseFormState, MachineViews
from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.surprise_machine.robot_tv_screen_view_model import RobotTvScreenState
from new_year.gui.impl.lobby.new_year.surprise_machine.robot_tv_rewards_view import RobotTvRewardsViewWindow, RobotTvRewardsView
from new_year.gui.impl.new_year.sounds import NewYearSoundEvents, NewYearSoundsManager, NewYearSoundStates, NewYearSoundVars
from new_year.skeletons.new_year import INewYearSurpriseMachine, INewYearController, INewYearCurrencyController
from new_year.gui.impl.lobby.new_year.surprise_machine.robot_tv_screen_view import RobotTvScreenView
from new_year.gui.impl.lobby.new_year.tooltips.ny_main_widget_tooltip import NyMainWidgetTooltip
from new_year.gui.shared.gui_items.processors.ny_processor import BuyMachineCoinsProcessor
from new_year.gui.impl.lobby.new_year.sub_model_presenter import HistorySubModelPresenter
from new_year.ny_constants import InternalViewState, ViewAliases, NyBtnTypes
from new_year.gui.shared.ny_level_helper import NewYearAtmospherePresenter
from messenger.formatters.service_channel import LootBoxAchievesFormatter
from new_year.gui.shared.ny_machine_helper import getMachineLootboxToken
from new_year.helpers.server_settings import getNewYearMachineConfig
from new_year.gui.impl.new_year.navigation import NewYearNavigation
from tutorial.control.game_vars import getVehicleByIntCD
from skeletons.gui.impl import INewYearNavigation
from helpers.func_utils import waitEventAndCall
from skeletons.gui.shared import IItemsCache
from th_async import AsyncScope, AsyncEvent
from lootboxes_common import makeLootboxID
from PlayerEvents import g_playerEvents
from shared_utils import first
from helpers import dependency
from helpers import time_utils
if typing.TYPE_CHECKING:
    from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.surprise_machine.ny_surprise_machine_model import NySurpriseMachineModel
_TEXTURE_PATH = 'content/Hangars/h03_mt_ny_2026/environment/h03_NY26_Object_10_1_AM.dds'

def isRewardVehicle(reward):
    return reward and 'vehicles' in reward


_INTERNAL_STATE_TO_MACHINE_VIEW = {InternalViewState.MACHINE_MAIN: MachineViews.SPEND_TOKENS,
 InternalViewState.BUY_MACHINE_COIN: MachineViews.GET_TOKENS,
 InternalViewState.MACHINE_REWARDING: MachineViews.SPEND_TOKENS_ACTIVE,
 InternalViewState.VEHICLE_MACHINE_REWARDING: MachineViews.SPEND_TOKENS_ACTIVE}

class NySurpriseMachineView(HistorySubModelPresenter):
    __slots__ = ('__displayView', '__asyncScope', '__finishRewardEvent', '__machineConfig', '__goToRewardVehicleEvent', '__onCoinAppliedEvent', '__rewardsWindow', '__cbOpenRewardsId', '__cbNotifyRewardsId')
    _INTERNAL_VIEW_STATE = InternalViewState.MACHINE_MAIN
    _MAX_TOKENS_NUM = 10
    _LOADING_TIME = 0.5
    _REWARDS_TIME = 1
    __itemsCache = dependency.descriptor(IItemsCache)
    __newYearNavigation = dependency.descriptor(INewYearNavigation)
    __nyMachineController = dependency.descriptor(INewYearSurpriseMachine)
    __nyController = dependency.descriptor(INewYearController)
    __nyCurrencyController = dependency.descriptor(INewYearCurrencyController)

    def __init__(self, model, parentView):
        super(NySurpriseMachineView, self).__init__(model, parentView)
        self.__displayView = None
        self.__machineConfig = getNewYearMachineConfig()
        self.__asyncScope = None
        self.__finishRewardEvent = None
        self.__onCoinAppliedEvent = None
        self.__goToRewardVehicleEvent = None
        self.__rewardsWindow = None
        self.__cbOpenRewardsId = None
        self.__cbNotifyRewardsId = None
        return

    @property
    def viewModel(self):
        return self.getViewModel()

    def initialize(self, *args, **kwargs):
        super(NySurpriseMachineView, self).initialize(*args, **kwargs)
        self.__asyncScope = AsyncScope()
        self.__finishRewardEvent = AsyncEvent(scope=self.__asyncScope)
        self.__onCoinAppliedEvent = AsyncEvent(scope=self.__asyncScope)
        self.__goToRewardVehicleEvent = AsyncEvent(scope=self.__asyncScope)
        self.__displayView.viewModel.rewardingFinished += self.__rewardingFinished
        self.__displayView.viewModel.goToRewardVehicle += self.__goToRewardVehicle
        self.__displayView.viewModel.onCoinApplied += self.__onCoinApplied
        self.setInternalViewState(self._INTERNAL_VIEW_STATE)
        self.__nyMachineController.deactivateMachine()
        self.__nyMachineController.updateSurpriseMachineBusyStatus(False)
        self.__nyMachineController.setState(RobotTvScreenState.IDLE)
        self.__nyMachineController.refreshApplyCoinState()
        with self.viewModel.transaction() as model:
            model.setExchangeRate(self.__machineConfig.getCoinPrice())
            model.setPurchaseFormState(PurchaseFormState.AVAILABLE if self.__nyMachineController.canBuyCoin else PurchaseFormState.NOT_AVAILABLE)
            model.setCurrentAtmosphereLevel(NewYearAtmospherePresenter.getLevel())

    def finalize(self):
        self.__nyController.unlockUIControls(id(self))
        self.__nyMachineController.deactivateMachine()
        self.__nyMachineController.updateSurpriseMachineBusyStatus(False)
        self.__nyMachineController.setState(RobotTvScreenState.IDLE)
        self.__nyMachineController.setViewState(None)
        self.__displayView.viewModel.rewardingFinished -= self.__rewardingFinished
        self.__displayView.viewModel.goToRewardVehicle -= self.__goToRewardVehicle
        self.__displayView.viewModel.onCoinApplied -= self.__onCoinApplied
        self.__displayView.destroyWindow()
        self.__displayView = None
        self.__asyncScope.destroy()
        super(NySurpriseMachineView, self).finalize()
        return

    def createToolTipContent(self, event, ctID):
        if ctID == R.views.new_year.lobby.new_year.tooltips.NyMainWidgetTooltip():
            return NyMainWidgetTooltip(block=WidgetBlock.SURPRISEMACHINE)
        else:
            from gui_lootboxes.gui.impl.lobby.gui_lootboxes.tooltips.lootbox_tooltip import LootboxTooltip
            if R.views.dyn('gui_lootboxes').isValid() and ctID == R.views.gui_lootboxes.lobby.gui_lootboxes.tooltips.LootboxTooltip():
                lootBoxType = event.getArgument('lootBoxType')
                if lootBoxType is not None:
                    return LootboxTooltip(self.__getLootBoxByType(lootBoxType))
            return super(NySurpriseMachineView, self).createToolTipContent(event, ctID)

    @createBackportTooltipDecorator()
    def createToolTip(self, event):
        return super(NySurpriseMachineView, self).createToolTip(event)

    def getTooltipData(self, event):
        vehicleName = event.getArgument('vehicleName')
        return backport.createTooltipData(isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.AWARD_VEHICLE, specialArgs=[self.__getVehicleCdByName(vehicleName)]) if vehicleName is not None else None

    def __getLootBoxByType(self, lootBoxType):
        boxes = self.__itemsCache.items.tokens.getLootBoxes()
        for tokenName, tokenData in boxes.iteritems():
            if tokenData.getType() == lootBoxType:
                return self.__itemsCache.items.tokens.getLootBoxByID(int(getLootBoxIDFromToken(tokenName)))

    def __getVehicleCdByName(self, vehicleName):
        for intCD in self.__itemsCache.items.getVehicles():
            if getVehicleByIntCD(intCD).name.split(':')[1] == vehicleName:
                return intCD

    def setInternalViewState(self, state, skipFlight=None):
        super(NySurpriseMachineView, self).setInternalViewState(state, skipFlight)
        viewState = _INTERNAL_STATE_TO_MACHINE_VIEW.get(state, MachineViews.SPEND_TOKENS)
        self.viewModel.setMachineViews(viewState)
        self.__nyMachineController.setViewState(viewState)

    def _getEvents(self):
        return ((self.__nyMachineController.onMachineButtonPress, self.__onMainButtonPress),
         (self.__nyMachineController.onActivationChanged, self.__onMachineActivated),
         (self.__nyMachineController.onMachineSelectButtonPress, self.__onSelectButtonPress),
         (self.__nyMachineController.onMachineButtonHovered, self.__onMachineButtonHovered),
         (self.viewModel.onBuyBtnClick, self.__onBuyBtnClick),
         (self.viewModel.goToMachineMain, self.__onGoToMachineMain),
         (self.viewModel.goToBuyTokens, self.__onGoToBuyTokens),
         (self.viewModel.goToQuest, self.__goToQuest),
         (self.viewModel.vehicleReward.showVehicle, self.__onShowVehicle),
         (self.viewModel.vehicleReward.closeRewardVehicle, self.__onCloseRewardVehicle),
         (self._nyController.onNySettingsChanged, self.__onNySettingsChanged),
         (g_playerEvents.onDisconnected, self.__onDisconnected))

    def preLoad(self, *args, **kwargs):
        super(NySurpriseMachineView, self).preLoad(*args, **kwargs)
        self.__createDisplayView()

    def __onDisconnected(self):
        self.__stopRewardsCallback()
        self.__closeRewardsWindow()

    def __closeRewardsWindow(self):
        if self.__rewardsWindow is not None:
            self.__rewardsWindow.content.viewModel.onClose -= self.__onRewardsClose
            self.__rewardsWindow.destroy()
            self.__rewardsWindow = None
        return

    def __stopRewardsCallback(self):
        if self.__cbOpenRewardsId is not None:
            BigWorld.cancelCallback(self.__cbOpenRewardsId)
            self.__cbOpenRewardsId = None
        if self.__cbNotifyRewardsId is not None:
            BigWorld.cancelCallback(self.__cbNotifyRewardsId)
            self.__cbNotifyRewardsId = None
        return

    def __onNySettingsChanged(self):
        if self.__machineConfig is not None and not self.__machineConfig.isEnabled():
            self.__newYearNavigation.closeMainView()
        return

    def __createDisplayView(self):
        if self.__displayView is None:
            self.__displayView = RobotTvScreenView()
            window = WindowImpl(WindowFlags.SURFACE, content=self.__displayView, layer=WindowLayer.VIEW, name=_TEXTURE_PATH, parent=self.getParentWindow())
            window.load()
        return

    def __onMachineActivated(self, isActive):
        if isActive:
            self.setInternalViewState(InternalViewState.MACHINE_REWARDING)
            tokensCount = self.__nyCurrencyController.getGiftMachineTokenCount
            if tokensCount == 1:
                self.__applyCoins()
                return
            self.__displayView.selectButton(self.__nyMachineController.selectedBtnType)
            self.__nyMachineController.setState(RobotTvScreenState.CHOOSEAMOUNT)

    def __onMainButtonPress(self):
        if not self.__nyMachineController.canApplyCoin:
            return
        self.__applyCoins(self.__calcApplyCount())

    def __calcApplyCount(self):
        tokens = self.__nyCurrencyController.getGiftMachineTokenCount
        multi = self.__nyMachineController.machineState == RobotTvScreenState.CHOOSEAMOUNT and self.__nyMachineController.selectedBtnType == NyBtnTypes.RIGHT
        return min(self._MAX_TOKENS_NUM, tokens) if multi else 1

    def __onSelectButtonPress(self, btnType):
        NewYearSoundsManager.playEvent(NewYearSoundEvents.MACHINE_CHOISE_BTN_PRESS)
        if self.__nyMachineController.machineState != RobotTvScreenState.CHOOSEAMOUNT and btnType == NyBtnTypes.LEFT:
            self.__nyMachineController.setState(RobotTvScreenState.CHOOSEAMOUNT)
            return
        if btnType == NyBtnTypes.LEFT:
            self.__nyMachineController.moveSelectionLeft()
        else:
            self.__nyMachineController.moveSelectionRight()
        self.__displayView.selectButton(self.__nyMachineController.selectedBtnType)

    def __applyCoins(self, count=1):
        if not self.__nyMachineController.canApplyCoin:
            return
        self.__nyMachineController.updateSurpriseMachineBusyStatus(True)
        NewYearSoundsManager.playEvent(NewYearSoundEvents.MACHINE_BTN_PRESS)
        self.__nyMachineController.setState(RobotTvScreenState.ACTIVE)
        self.__tryApplyCoins(count)

    @adisp_process
    def __tryApplyCoins(self, count=1):
        lootbox = self.__itemsCache.items.tokens.getLootBoxByID(makeLootboxID(getMachineLootboxToken()))
        if lootbox is None:
            return
        else:
            self.__nyController.lockUIControls(id(self))
            result = yield LootBoxOpenProcessor(lootbox, count).request()

            def _process():
                if not result or not result.success:
                    self.__nyMachineController.setState(RobotTvScreenState.ERROR)
                    SystemMessages.pushMessage(text=backport.text(R.strings.ny.notification.machine.server_error.text()), type=SM_TYPE.ErrorHeader, priority='high', messageData={'header': backport.text(R.strings.ny.notification.machine.server_error.header())})
                    self.__nyController.unlockUIControls(id(self))
                    if count > 1:
                        self.__changeState(InternalViewState.MACHINE_MAIN)
                    return
                rewardsList = result.auxData.get('bonus', [])
                if count == 1:
                    self.__handleSingleReward(result.success, rewardsList)
                else:
                    self.__handleMultipleRewards(rewardsList, count)

            BigWorld.callback(0.0, _process)
            return

    def __handleSingleReward(self, success, rewardsList):
        rewards = rewardsList[0] if rewardsList else None
        waitEventAndCall(self.__onCoinAppliedEvent, partial(self.__coinApplied, success, rewards))
        return

    def __handleMultipleRewards(self, rewardsList, usedCount):
        self.__nyMachineController.setState(RobotTvScreenState.ACTIVE)
        self.__nyMachineController.updateSurpriseMachineBusyStatus(True)
        self.__nyController.unlockUIControls(id(self))

        def _openRewards():
            self.__cbOpenRewardsId = None
            self.__rewardsWindow = RobotTvRewardsViewWindow(self.getParentWindow())
            content = self.__rewardsWindow.content
            content.setTokensUsed(usedCount)
            content.fillRewards(rewardsList)
            content.viewModel.onClose += self.__onRewardsClose
            self.__rewardsWindow.load()
            self.__nyMachineController.setState(self.__getBackgroundState())

            def _notify():
                self.__cbNotifyRewardsId = None
                self.__sendRewardsNotification(rewardsList)
                return

            self.__cbNotifyRewardsId = BigWorld.callback(self._REWARDS_TIME, _notify)
            return

        self.__cbOpenRewardsId = BigWorld.callback(self._LOADING_TIME, _openRewards)

    def __onRewardsClose(self):
        self.__nyMachineController.updateSurpriseMachineBusyStatus(False)
        tokensLeft = self.__nyCurrencyController.getGiftMachineTokenCount
        if tokensLeft > 1:
            self.setInternalViewState(InternalViewState.MACHINE_REWARDING)
            self.__displayView.selectButton(self.__nyMachineController.selectedBtnType)
        else:
            self.__nyMachineController.deactivateMachine()
            self.setInternalViewState(InternalViewState.MACHINE_MAIN)
        self.__closeRewardsWindow()

    def __getBackgroundState(self):
        tokensLeft = self.__nyCurrencyController.getGiftMachineTokenCount
        return RobotTvScreenState.CHOOSEAMOUNT if tokensLeft > 1 else RobotTvScreenState.IDLE

    def __sendRewardsNotification(self, rewardsList):
        mergedRewards = getMergedBonusesFromDicts(rewardsList)
        formattedRewards = LootBoxAchievesFormatter.formatQuestAchieves(mergedRewards, asBattleFormatter=False, processTokens=True)
        SystemMessages.pushMessage(text=backport.text(R.strings.ny.notification.machine.run.text(), time=time_utils.getDateTimeInLocal(time_utils.getCurrentTimestamp()).strftime('%d.%m.%y %H:%M:%S'), count=len(rewardsList)), type=SM_TYPE.NYSurpriseMachineReward, priority=NotificationPriorityLevel.MEDIUM, messageData={'rewards': formattedRewards})

    def __coinApplied(self, success, rewards):
        if success and rewards:
            if isRewardVehicle(rewards):
                self.__nyMachineController.setState(RobotTvScreenState.VEHICLEREWARDING)
                waitEventAndCall(self.__goToRewardVehicleEvent, partial(self.__showVehicle, rewards))
                waitEventAndCall(self.__finishRewardEvent, partial(self.__changeState, InternalViewState.MACHINE_MAIN))
            else:
                self.__nyMachineController.setState(RobotTvScreenState.REWARDING)
                self.__changeState()
            self.__displayView.fillReward(copy.deepcopy(rewards))
            self.__sendRewardsNotification([rewards])
        else:
            self.__nyMachineController.setState(RobotTvScreenState.ERROR)
            self.__changeState()
        self.__nyController.unlockUIControls(id(self))

    def __onBuyBtnClick(self, event):
        self.__buyMachineCoin(int(event.get('count')))

    @adisp_process
    @replaceNoneKwargsModel
    def __buyMachineCoin(self, count, model=None):
        self.viewModel.setIsBuyBtnLoading(True)
        try:
            result = yield BuyMachineCoinsProcessor(count).request()
            success = result and result.success
        finally:
            self.viewModel.setIsBuyBtnLoading(False)

        if success:
            model.setPurchaseFormState(PurchaseFormState.AVAILABLE)
            SystemMessages.pushMessage(priority=result.msgPriority, text=result.userMsg, type=result.sysMsgType, messageData=result.msgData)
        else:
            model.setPurchaseFormState(PurchaseFormState.ERROR)

    def __onGoToBuyTokens(self):
        if not self.__nyMachineController.isMachineBusy:
            self.__nyMachineController.setState(RobotTvScreenState.IDLE)
            self.setInternalViewState(InternalViewState.BUY_MACHINE_COIN)

    def __onGoToMachineMain(self):
        if not self.__nyMachineController.isMachineBusy:
            self.__nyMachineController.setState(RobotTvScreenState.IDLE)
            self.setInternalViewState(InternalViewState.MACHINE_MAIN)
            self.__nyMachineController.deactivateMachine()

    def __goToQuest(self):
        if not self.__nyMachineController.isMachineBusy:
            self.__newYearNavigation.showNavigationView(ViewAliases.QUESTS_VIEW)

    def __rewardingFinished(self):
        self.__finishRewardEvent.set()

    def __onCoinApplied(self):
        self.__onCoinAppliedEvent.set()

    def __goToRewardVehicle(self):
        self.__goToRewardVehicleEvent.set()

    def __showVehicle(self, rewards):
        vehList = rewards.get('vehicles', [])
        vehIntCD = first(vehList[0].keys()) if vehList else None
        if vehIntCD:
            self.setInternalViewState(InternalViewState.VEHICLE_MACHINE_REWARDING)
            selectVehicleInHangar(vehIntCD, loadHangar=False)
            veh = self.__itemsCache.items.getItemByCD(int(vehIntCD))
            NewYearSoundsManager.playEvent(NewYearSoundEvents.SURPRISE_MACHINE_EXIT)
            NewYearSoundsManager.playEvent(NewYearSoundEvents.HANGAR)
            SoundGroups.g_instance.setState(NewYearSoundVars.STATE_NEWYEAR_PLACE, NewYearSoundStates.HANGAR)
            with self.viewModel.vehicleReward.transaction() as model:
                model.setVehicleName(veh.userName)
                model.setVehicleLvl(veh.level)
                model.setVehicleType(veh.type)
                model.setIsElite(veh.isElite)
                model.setIsMainViewVisible(False)
        return

    def __changeState(self, state=None):
        self.__nyMachineController.updateSurpriseMachineBusyStatus(False)
        if state:
            self.setInternalViewState(state)
            self.__nyMachineController.setState(RobotTvScreenState.IDLE)
        self.__finishRewardEvent.clear()
        self.__goToRewardVehicleEvent.clear()
        self.__onCoinAppliedEvent.clear()

    def __onShowVehicle(self):
        self.__nyMachineController.updateSurpriseMachineBusyStatus(False)
        self.__nyMachineController.setState(RobotTvScreenState.IDLE)
        NewYearNavigation.closeMainView()

    def __onCloseRewardVehicle(self):
        self.viewModel.vehicleReward.setIsMainViewVisible(True)
        NewYearSoundsManager.playEvent(NewYearSoundEvents.HANGAR_EXIT)
        NewYearSoundsManager.playEvent(NewYearSoundEvents.SURPRISE_MACHINE)
        SoundGroups.g_instance.setState(NewYearSoundVars.STATE_NEWYEAR_PLACE, NewYearSoundStates.SURPRISE_MACHINE)
        self.__rewardingFinished()

    def __onMachineButtonHovered(self, isHovered):
        self.viewModel.setIsBtnHovered(isHovered)
