# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: armory_yard/scripts/client/armory_yard/gui/impl/lobby/feature/armory_yard_buy_view.py
from adisp import adisp_process
from armory_yard.gui.impl.gen.view_models.views.lobby.feature.armory_yard_buy_step_config import ArmoryYardBuyStepConfig
from armory_yard.gui.impl.gen.view_models.views.lobby.feature.armory_yard_buy_view_model import ArmoryYardBuyViewModel, ParentAlias
from armory_yard.gui.impl.gen.view_models.views.lobby.feature.armory_yard_main_view_model import TabId
from armory_yard.gui.impl.lobby.feature.tooltips.armory_yard_currency_tooltip_view import ArmoryYardCurrencyTooltipView
from armory_yard.gui.impl.lobby.feature.tooltips.rest_reward_tooltip_view import RestRewardTooltipView
from armory_yard.gui.shared.bonus_packers import packVehicleModel, packRestModel, getArmoryYardBonusPacker
from armory_yard.gui.shared.bonuses_sorter import bonusesSortKeyFunc
from armory_yard.gui.shared.gui_items.items_actions import BUY_STEP_TOKENS
from armory_yard.gui.window_events import showBuyGoldForArmoryYard
from constants import Configs
from frameworks.wulf import WindowFlags, WindowLayer, ViewSettings, ViewFlags
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework.entities.View import ViewKeyDynamic, ViewKey
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.lobby.common.view_helpers import packBonusModelAndTooltipData
from gui.impl.lobby.common.view_wrappers import createBackportTooltipDecorator
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyWindow
from gui.impl.wrappers.user_compound_price_model import BuyPriceModelBuilder
from gui.server_events.bonuses import getNonQuestBonuses, VehiclesBonus, mergeBonuses, splitBonuses
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import LobbySimpleEvent
from gui.shared.gui_items.items_actions import factory
from gui.shared.missions.packers.bonus import BACKPORT_TOOLTIP_CONTENT_ID
from gui.shared.money import Currency
from gui.shared.view_helpers.blur_manager import CachedBlur
from helpers import dependency
from shared_utils import first
from skeletons.gui.game_control import IArmoryYardController, IWalletController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
_PARENT_ALIASES_TO_VIEW_KEY = {ParentAlias.MAINVIEW: ViewKeyDynamic(R.views.armory_yard.lobby.feature.ArmoryYardMainView()),
 ParentAlias.VEHICLEPREVIEW: ViewKey(VIEW_ALIAS.VEHICLE_PREVIEW)}
_VIEW_KEY_TO_PARENT_ALIASES = {value:key for key, value in _PARENT_ALIASES_TO_VIEW_KEY.iteritems()}
_LOOTBOX_RES = R.views.dyn('gui_lootboxes').dyn('lobby').dyn('gui_lootboxes').dyn('tooltips').dyn('LootboxTooltip')

class ArmoryYardBuyView(ViewImpl):
    __slots__ = ('__tooltipData', '__selectedStep', '__prevPassedStep', '_isBuyPostProgressionTokensState', '__blur', '__onLoadedCallback', '__onClosedCallback')
    __armoryYardCtrl = dependency.descriptor(IArmoryYardController)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __itemsCache = dependency.descriptor(IItemsCache)
    __wallet = dependency.descriptor(IWalletController)

    def __init__(self, layoutID, isBlurEnabled=False, onLoadedCallback=None, onClosedCallback=None):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.LOBBY_TOP_SUB_VIEW
        settings.model = ArmoryYardBuyViewModel()
        super(ArmoryYardBuyView, self).__init__(settings)
        self.__tooltipData = {ArmoryYardBuyViewModel.STEP_VEHICLE_TOOLTIP_TYPE: {},
         ArmoryYardBuyViewModel.FINAL_REWARD_TOOLTIP_TYPE: {},
         ArmoryYardBuyViewModel.MERGED_REWARD_TOOLTIP_TYPE: {}}
        self.__selectedStep = 0
        self.__prevPassedStep = 0
        self._isBuyPostProgressionTokensState = self.__armoryYardCtrl.isPostProgressionState
        self.__blur = CachedBlur(ownLayer=self.layer - 1) if isBlurEnabled else None
        self.__onLoadedCallback = onLoadedCallback
        self.__onClosedCallback = onClosedCallback
        return

    @property
    def viewModel(self):
        return super(ArmoryYardBuyView, self).getViewModel()

    @createBackportTooltipDecorator()
    def createToolTip(self, event):
        return super(ArmoryYardBuyView, self).createToolTip(event)

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.armory_yard.lobby.feature.tooltips.RestRewardTooltipView():
            tooltipData = self.getTooltipData(event)
            return RestRewardTooltipView([] if tooltipData is None else tooltipData.specialArgs[0])
        elif contentID == R.views.armory_yard.lobby.feature.tooltips.ArmoryYardCurrencyTooltipView():
            currency = event.getArgument('currency')
            if self.getTooltipData(event):
                currency = currency or self.getTooltipData(event).specialArgs[0]
            return ArmoryYardCurrencyTooltipView(currency)
        elif _LOOTBOX_RES.exists() and contentID == _LOOTBOX_RES():
            from gui_lootboxes.gui.impl.lobby.gui_lootboxes.tooltips.lootbox_tooltip import LootboxTooltip
            tooltipData = self.getTooltipData(event)
            lootBoxID = tooltipData.get('lootBoxID')
            lootBox = self.__itemsCache.items.tokens.getLootBoxByID(int(lootBoxID))
            return LootboxTooltip(lootBox)
        else:
            return super(ArmoryYardBuyView, self).createToolTipContent(event, contentID)

    def getTooltipData(self, event):
        tooltipId = event.getArgument('tooltipId')
        tooltipType = event.getArgument('tooltipType')
        return self.__tooltipData.get(tooltipType, {}).get(tooltipId, None) if tooltipId is not None and tooltipType is not None else None

    def onCancel(self, *args):
        self.destroyWindow(fromScene=True)

    def destroyWindow(self, fromScene=False):
        if self.__onClosedCallback is not None:
            self.__onClosedCallback(True)
        if fromScene:
            g_eventBus.handleEvent(LobbySimpleEvent(LobbySimpleEvent.NOTIFY_CURSOR_OVER_3DSCENE, ctx={'isOver3dScene': True}), EVENT_BUS_SCOPE.GLOBAL)
        super(ArmoryYardBuyView, self).destroyWindow()
        return

    @adisp_process
    def onBuySteps(self, args):
        currency = args.get('currency')
        if currency not in self.__armoryYardCtrl.getTokenCurrencies():
            return
        stepCount = int(args.get('steps'))
        price = self.__armoryYardCtrl.getCurrencyTokenCost(currency) * stepCount
        playerMoney = self.__itemsCache.items.stats.money
        shortage = playerMoney.getShortage(price)
        if shortage:
            setCurrencies = shortage.getSetCurrencies()
            if len(setCurrencies) == 1 and setCurrencies[0] == Currency.GOLD:
                showBuyGoldForArmoryYard(price)
            return
        isPostProgression = self.__armoryYardCtrl.isPostProgressionState
        action = factory.getAction(BUY_STEP_TOKENS, stepCount, currency)
        result = yield factory.asyncDoAction(action)
        if result:
            self.__armoryYardCtrl.onPayed(isPostProgression, stepCount, price, currency)
            self.destroyWindow(fromScene=True)
        else:
            self.__armoryYardCtrl.onPayedError()

    def onBack(self):
        self.destroyWindow()

    def onChangeSelectedStep(self, args):
        selectedStep = int(args.get('count')) + self.__getPassedSteps()
        if selectedStep <= self.__armoryYardCtrl.maxNumberOfSteps:
            with self.viewModel.transaction() as vm:
                self.__setSelectedStep(selectedStep, vm)

    def __openBuyViewHandler(self):
        buyViewContext = {'loadBuyView': True}
        self.__armoryYardCtrl.goToArmoryYard(tabId=TabId.PROGRESS, ctx=buyViewContext)

    def onShowVehiclePreview(self):
        self.__armoryYardCtrl.showVehiclePreview(backCallback=self.__openBuyViewHandler)

    def onShowStylePreview(self):
        self.__armoryYardCtrl.showStylePreview(backCallback=self.__openBuyViewHandler)

    def _onLoaded(self, *args, **kwargs):
        super(ArmoryYardBuyView, self)._onLoaded(*args, **kwargs)
        if self.__onLoadedCallback is not None:
            self.__onLoadedCallback()
        return

    def _onLoading(self, *args, **kwargs):
        super(ArmoryYardBuyView, self)._onLoading(*args, **kwargs)
        g_eventBus.handleEvent(LobbySimpleEvent(LobbySimpleEvent.NOTIFY_CURSOR_OVER_3DSCENE, ctx={'isOver3dScene': False}), EVENT_BUS_SCOPE.GLOBAL)
        if self.__blur is not None:
            self.__blur.enable()
        self.__selectedStep = self.__calcSelectedStep()
        self.__prevPassedStep = self.__getPassedSteps()
        self.__fullUpdate()
        self.viewModel.setIsBlurEnabled(self.__blur is not None)
        return

    def _finalize(self):
        if self.__blur is not None:
            self.__blur.disable()
        super(ArmoryYardBuyView, self)._finalize()
        return

    def _getEvents(self):
        return ((self.viewModel.onCancel, self.onCancel),
         (self.viewModel.onBack, self.onBack),
         (self.viewModel.onChangeSelectedStep, self.onChangeSelectedStep),
         (self.viewModel.onBuySteps, self.onBuySteps),
         (self.viewModel.onShowVehiclePreview, self.onShowVehiclePreview),
         (self.viewModel.onShowStylePreview, self.onShowStylePreview),
         (self.__lobbyContext.getServerSettings().onServerSettingsChange, self.__onServerSettingsChange),
         (self.__armoryYardCtrl.onUpdated, self.__onEventUpdated),
         (self.__armoryYardCtrl.onProgressUpdated, self.__onProgressUpdated),
         (self.__wallet.onWalletStatusChanged, self.__onWalletStatusChanged),
         (self.__armoryYardCtrl.onTabIdChanged, self.onCancel))

    def _getCallbacks(self):
        return (('stats', self.__onStatsUpdated),)

    def __fillPrices(self, model):
        pricesModel = model.getPrices()
        pricesModel.clear()
        for currency in self.__armoryYardCtrl.getTokenCurrencies():
            price = model.getPricesType()()
            BuyPriceModelBuilder.fillPriceModel(price, self.__armoryYardCtrl.getCurrencyTokenCost(currency) * (self.__selectedStep - self.__getPassedSteps()), checkBalanceAvailability=True)
            pricesModel.addViewModel(price)

        pricesModel.invalidate()

    def __getCurrentStepsRange(self):
        isPostProgression = self.__armoryYardCtrl.isPostProgressionState
        startPostProgressionStep = self.__armoryYardCtrl.startStepOfPostProgression
        stepsFrom = startPostProgressionStep if isPostProgression else 1
        stepsTo = self.__armoryYardCtrl.maxNumberOfSteps if isPostProgression else startPostProgressionStep
        return (stepsFrom, stepsTo)

    def __setMainData(self, model):
        model.setIsWalletAvailable(self.__wallet.isAvailable)
        stepsFrom, stepsTo = self.__getCurrentStepsRange()
        model.setStartStep(stepsFrom)
        model.setFinishStep(stepsTo)
        model.setStepSelected(self.__selectedStep)
        model.setStepsPassed(self.__getPassedSteps())
        model.setIsPostProgressionState(self.__armoryYardCtrl.isPostProgressionState)
        window = self.getParentWindow()
        parentWindow = window.parent if window is not None else None
        parentView = parentWindow.content if parentWindow is not None else None
        if parentView is not None:
            parentViewKey = parentView.key if hasattr(parentView, 'key') else ViewKeyDynamic(parentView.layoutID)
        else:
            parentViewKey = None
        model.setParentAlias(_VIEW_KEY_TO_PARENT_ALIASES.get(parentViewKey, ParentAlias.MAINVIEW))
        self.__fillPrices(model)
        return

    def __fillSteps(self, model):
        stepsModel = model.getSteps()
        stepsModel.clear()
        self.__tooltipData[ArmoryYardBuyViewModel.STEP_VEHICLE_TOOLTIP_TYPE].clear()
        stepsRewads = self.__armoryYardCtrl.getStepsRewards()
        stepsFrom, stepsTo = self.__getCurrentStepsRange()
        for stepId in range(stepsFrom, stepsTo + 1):
            stepModel = ArmoryYardBuyStepConfig()
            vehicleReward = stepsRewads[stepId].get(VehiclesBonus.VEHICLES_BONUS, None)
            if vehicleReward:
                vehicleBonus = getNonQuestBonuses(VehiclesBonus.VEHICLES_BONUS, vehicleReward)[0]
                vehicle = vehicleBonus.getVehicles()[0][0]
                stepModel.setHasVehicleInReward(True)
                tooltipID = str(len(self.__tooltipData[ArmoryYardBuyViewModel.STEP_VEHICLE_TOOLTIP_TYPE]))
                stepModel.setVehicleRewardTooltipId(tooltipID)
                stepModel.setVehicleRewardTooltipContentId(str(BACKPORT_TOOLTIP_CONTENT_ID))
                tooltipData = self.__tooltipData.get(ArmoryYardBuyViewModel.STEP_VEHICLE_TOOLTIP_TYPE, {})
                tooltipData[tooltipID] = backport.createTooltipData(isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.ARMORY_YARD_AWARD_VEHICLE, specialArgs=[vehicle.intCD])
            stepsModel.addViewModel(stepModel)

        stepsModel.invalidate()
        return

    def __onServerSettingsChange(self, diff):
        if Configs.ARMORY_YARD_CONFIG.value in diff:
            self.__selectedStep = self.__calcSelectedStep()
            self.__fullUpdate()

    def __fullUpdate(self):
        with self.viewModel.transaction() as vm:
            self.__setMainData(vm)
            self.__fillSteps(vm)
            self.__fillRewards(vm)
            self.__fillFinalReward(vm)

    def __onProgressUpdated(self):
        with self.viewModel.transaction() as vm:
            self.__updatePassedSteps(vm)

    def __onEventUpdated(self):
        if not self.__armoryYardCtrl.isActive() or self.__armoryYardCtrl.isCompleted():
            self.destroyWindow(fromScene=True)

    def __getPassedSteps(self):
        return self.__armoryYardCtrl.getProgressionTokenCount()

    def __calcSelectedStep(self):
        stepsDiff = max(self.__selectedStep - self.__prevPassedStep, 1)
        maxNumberOfSteps = self.__armoryYardCtrl.maxNumberOfSteps if self._isBuyPostProgressionTokensState else self.__armoryYardCtrl.startStepOfPostProgression
        return min(self.__getPassedSteps() + stepsDiff, maxNumberOfSteps)

    def __updatePassedSteps(self, model):
        model.setStepsPassed(self.__getPassedSteps())
        self.__setSelectedStep(self.__calcSelectedStep(), model)
        self.__prevPassedStep = self.__getPassedSteps()

    def __setSelectedStep(self, selectedStep, model):
        self.__selectedStep = selectedStep
        model.setStepSelected(self.__selectedStep)
        self.__fillPrices(model)
        self.__fillRewards(model)

    def __fillRewards(self, model):
        rewards = model.getRewards()
        rewards.clear()
        self.__tooltipData[ArmoryYardBuyViewModel.MERGED_REWARD_TOOLTIP_TYPE].clear()
        stepsRewads = self.__armoryYardCtrl.getStepsRewards()
        rewardsList = []
        for stepId in range(max(self.__getPassedSteps() + 1, 1), self.__selectedStep + 1):
            for rewardType, rewardValue in stepsRewads[stepId].items():
                rewardsList.extend(getNonQuestBonuses(rewardType, rewardValue))

        rewardsList = splitBonuses(mergeBonuses(rewardsList))
        rewardsList.sort(key=bonusesSortKeyFunc)
        for idx, value in enumerate(rewardsList):
            if value.getName() == 'battleToken' and value.getValue().get('ny24_yaga') is not None:
                rewardsList.pop(idx)

        if len(rewardsList) > ArmoryYardBuyViewModel.MAX_VISIBLE_REWARDS:
            packBonusModelAndTooltipData(rewardsList[:ArmoryYardBuyViewModel.MAX_VISIBLE_REWARDS - 1], rewards, self.__tooltipData[ArmoryYardBuyViewModel.MERGED_REWARD_TOOLTIP_TYPE], packer=getArmoryYardBonusPacker())
            packRestModel(rewardsList[ArmoryYardBuyViewModel.MAX_VISIBLE_REWARDS - 1:], rewards, self.__tooltipData[ArmoryYardBuyViewModel.MERGED_REWARD_TOOLTIP_TYPE], ArmoryYardBuyViewModel.MAX_VISIBLE_REWARDS - 1)
        else:
            packBonusModelAndTooltipData(rewardsList, rewards, self.__tooltipData[ArmoryYardBuyViewModel.MERGED_REWARD_TOOLTIP_TYPE], packer=getArmoryYardBonusPacker())
        rewards.invalidate()
        return

    def __fillFinalReward(self, model):
        if self.__armoryYardCtrl.isPostProgressionState:
            customization = self.__armoryYardCtrl.getStepsRewards()[self.__armoryYardCtrl.getFinalPostProgressionRewardStep()]
            itemType, itemID = first(customization.items())
            stepReward = first(getNonQuestBonuses(itemType, itemID))
            packer = getArmoryYardBonusPacker()
            bTooltip = first(packer.getToolTip(stepReward))
            bContentId = first(packer.getContentId(stepReward))
            tooltipIndex = str(len(self.__tooltipData))
            self.__tooltipData[ArmoryYardBuyViewModel.FINAL_REWARD_TOOLTIP_TYPE][tooltipIndex] = bTooltip
            model.finalReward.setTooltipId(tooltipIndex)
            model.finalReward.setTooltipContentId(str(bContentId))
        else:
            finalRewardVehicle = self.__armoryYardCtrl.getFinalRewardVehicle()
            if finalRewardVehicle:
                packVehicleModel(model.finalReward, finalRewardVehicle)
                self.__tooltipData[ArmoryYardBuyViewModel.FINAL_REWARD_TOOLTIP_TYPE] = {'0': backport.createTooltipData(isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.ARMORY_YARD_AWARD_VEHICLE, specialArgs=[finalRewardVehicle.intCD])}
                model.finalReward.setTooltipContentId(str(BACKPORT_TOOLTIP_CONTENT_ID))
                model.finalReward.setTooltipId('0')

    def __onStatsUpdated(self, _):
        with self.viewModel.transaction() as vm:
            self.__fillPrices(vm)

    def __onWalletStatusChanged(self, *_):
        with self.viewModel.transaction() as vm:
            vm.setIsWalletAvailable(self.__wallet.isAvailable)
            self.__fillPrices(vm)


class ArmoryYardBuyWindow(LobbyWindow):
    __slots__ = ()

    def __init__(self, parent=None, isBlurEnabled=False, onLoadedCallback=None, onClosedCallback=None):
        super(ArmoryYardBuyWindow, self).__init__(wndFlags=WindowFlags.WINDOW, layer=WindowLayer.TOP_SUB_VIEW, content=ArmoryYardBuyView(R.views.armory_yard.lobby.feature.ArmoryYardBuyView(), isBlurEnabled, onLoadedCallback, onClosedCallback), parent=parent)
