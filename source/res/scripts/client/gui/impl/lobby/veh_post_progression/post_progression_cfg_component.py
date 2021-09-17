# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/veh_post_progression/post_progression_cfg_component.py
import typing
import BigWorld
from adisp import process
from Event import Event
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.impl.gen import R
from gui.impl.gen.view_models.common.price_item_model import PriceItemModel
from gui.impl.gen.view_models.views.lobby.post_progression.step_model import StepState
from gui.impl.gen.view_models.views.lobby.post_progression.modification_model import ModificationModel
from gui.impl.gen.view_models.views.lobby.post_progression.post_progression_base_view_model import ProgressionAvailability, ProgressionState
from gui.impl.gen.view_models.views.lobby.post_progression.post_progression_cfg_view_model import PostProgressionCfgViewModel
from gui.impl.lobby.veh_post_progression.post_progression_base_component import PostProgressionBaseComponentView
from gui.impl.lobby.veh_post_progression.tooltips.pair_modification_tooltip_view import CfgPairModificationTooltipView
from gui.impl.lobby.veh_post_progression.tooltips.level_tooltip_view import CfgProgressionLevelTooltipView
from gui.impl.lobby.veh_post_progression.tooltips.role_slot_tooltip_view import RoleSlotTooltipView
from gui.impl.lobby.veh_post_progression.tooltips.setup_tooltip_view import SetupTooltipView
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.items_actions import factory
from gui.shared.items_cache import CACHE_SYNC_REASON
from gui.veh_post_progression.helpers import storeLastSeenStep
from gui.veh_post_progression.models.ext_money import ExtendedMoney, ExtendedCurrency, EXT_MONEY_UNDEFINED
from gui.veh_post_progression.models.progression import PostProgressionAvailability, PostProgressionCompletion
from gui.veh_post_progression.models.progression_step import PostProgressionStepState
from gui.veh_post_progression.models.purchase import PurchaseCheckResult, PurchaseProvider
from helpers import dependency
from post_progression_common import GROUP_ID_BY_FEATURE
from skeletons.gui.shared import IItemsCache
from skeletons.gui.game_control import IWalletController
if typing.TYPE_CHECKING:
    from gui.impl.gen.view_models.common.price_model import PriceModel
    from gui.impl.gen.view_models.common.bonuses_model import BonusesModel
    from gui.impl.gen.view_models.views.lobby.post_progression.multi_step_model import MultiStepModel
    from gui.impl.gen.view_models.views.lobby.post_progression.single_step_model import SingleStepModel
    from gui.veh_post_progression.models.progression import PostProgressionItem
    from gui.veh_post_progression.models.progression_step import PostProgressionStepItem
_AVAILABILITY_MAP = {PostProgressionAvailability.AVAILABLE: ProgressionAvailability.AVAILABLE,
 PostProgressionAvailability.VEH_NOT_ELITE: ProgressionAvailability.UNAVAILABLEELITE,
 PostProgressionAvailability.VEH_NOT_IN_INVENTORY: ProgressionAvailability.UNAVAILABLEPURCHASE,
 PostProgressionAvailability.VEH_IS_RENTED: ProgressionAvailability.UNAVAILABLERENT,
 PostProgressionAvailability.VEH_IS_RENT_OVER: ProgressionAvailability.UNAVAILABLERENTOVER,
 PostProgressionAvailability.VEH_IN_BATTLE: ProgressionAvailability.UNAVAILABLEBATTLE,
 PostProgressionAvailability.VEH_IN_QUEUE: ProgressionAvailability.UNAVAILABLEBATTLE,
 PostProgressionAvailability.VEH_IN_FORMATION: ProgressionAvailability.UNAVAILABLEFORMATION,
 PostProgressionAvailability.VEH_IN_BREAKER: ProgressionAvailability.UNAVAILABLEBREAKER,
 PostProgressionAvailability.VEH_IS_BROKEN: ProgressionAvailability.UNAVAILABLEBROKEN}
_COMPLETION_MAP = {PostProgressionCompletion.EMPTY: ProgressionState.INITIAL,
 PostProgressionCompletion.PARTIAL: ProgressionState.TRANSITIONAL,
 PostProgressionCompletion.FULL: ProgressionState.FINAL}
_STEP_STATE_MAP = {PostProgressionStepState.RESTRICTED: StepState.RESTRICTED,
 PostProgressionStepState.LOCKED: StepState.UNAVAILABLELOCKED,
 PostProgressionStepState.RECEIVED: StepState.RECEIVED,
 PostProgressionStepState.UNLOCKED: StepState.AVAILABLEPURCHASE}
_TOGGLING_COOLDOWN = 1.0

class PostProgressionCfgComponentView(PostProgressionBaseComponentView):
    __itemsCache = dependency.descriptor(IItemsCache)
    __walletController = dependency.descriptor(IWalletController)
    __slots__ = ('onGoBackAction', 'onResearchAction', '__intCD', '__balance', '__creditsRate', '__togglingSteps', '__lockTogglingCallbackID')

    def __init__(self, layoutID=R.views.lobby.veh_post_progression.VehiclePostProgressionView(), **kwargs):
        super(PostProgressionCfgComponentView, self).__init__(layoutID, PostProgressionCfgViewModel(), **kwargs)
        self.__balance, self.__intCD = (None, None)
        self.onGoBackAction = Event(self._eventManager)
        self.onResearchAction = Event(self._eventManager)
        self.__togglingSteps = set()
        self.__lockTogglingCallbackID = None
        return

    @property
    def viewModel(self):
        return super(PostProgressionCfgComponentView, self).getViewModel()

    def invalidateVehicle(self, intCD):
        self.__intCD = intCD
        self._updateVehicle()

    def createToolTipContent(self, event, contentID):
        stepId, modId = self._parseTooltipEvent(event)
        if contentID == R.views.lobby.veh_post_progression.tooltip.PairModificationTooltipView() and stepId is not None and modId is not None:
            return CfgPairModificationTooltipView(self._vehicle, stepId, modId)
        elif contentID == R.views.lobby.veh_post_progression.tooltip.RoleSlotTooltipView() and stepId is not None:
            return RoleSlotTooltipView(step=self._vehicle.postProgression.getStep(stepId))
        elif contentID == R.views.lobby.veh_post_progression.tooltip.SetupTooltipView() and stepId is not None:
            return SetupTooltipView(step=self._vehicle.postProgression.getStep(stepId))
        else:
            return CfgProgressionLevelTooltipView(self._vehicle, stepId) if contentID == R.views.lobby.veh_post_progression.tooltip.PostProgressionLevelTooltipView() and stepId is not None else super(PostProgressionCfgComponentView, self).createToolTipContent(event, contentID)

    def _finalize(self):
        self.__cancelLockToggling()
        self.__togglingSteps.clear()
        super(PostProgressionCfgComponentView, self)._finalize()

    def _onLoading(self, intCD=None, *args, **kwargs):
        self.__intCD = intCD
        self.__balance = self.__itemsCache.items.stats.getMoneyExt(self.__intCD)
        self.__creditsRate = self.__itemsCache.items.shop.exchangeRate
        super(PostProgressionCfgComponentView, self)._onLoading(intCD, *args, **kwargs)

    def _updateAll(self):
        super(PostProgressionCfgComponentView, self)._updateAll()
        self.__updateLastSeenModification()

    def __updateLastSeenModification(self):
        purchasableStep = self._vehicle.postProgression.getFirstPurchasableStep(ExtendedMoney(xp=self._vehicle.xp))
        if purchasableStep is not None:
            storeLastSeenStep(self._vehicle.intCD, purchasableStep.stepID)
        return

    def _addListeners(self):
        super(PostProgressionCfgComponentView, self)._addListeners()
        self.viewModel.purchasePreview.onPurchaseClick += self.__onPurchaseClick
        self.viewModel.onGoBackAction += self.__onGoBackAction
        self.viewModel.onResearchAction += self.__onResearchAction
        self.viewModel.grid.onPrebattleSwitchToggleClick += self._onPrebattleSwitchToggleClick
        self.__itemsCache.onSyncCompleted += self.__onSyncCompleted
        self.__walletController.onWalletStatusChanged += self._updateAll
        g_clientUpdateManager.addCallbacks({'stats.{}'.format(c):self.__updateMoney for c in ExtendedCurrency.ALL})

    def _removeListeners(self):
        self.viewModel.purchasePreview.onPurchaseClick -= self.__onPurchaseClick
        self.viewModel.onGoBackAction -= self.__onGoBackAction
        self.viewModel.onResearchAction -= self.__onResearchAction
        self.viewModel.grid.onPrebattleSwitchToggleClick -= self._onPrebattleSwitchToggleClick
        self.__itemsCache.onSyncCompleted -= self.__onSyncCompleted
        self.__walletController.onWalletStatusChanged -= self._updateAll
        g_clientUpdateManager.removeObjectCallbacks(self)
        super(PostProgressionCfgComponentView, self)._removeListeners()

    @process
    def _onMainStepActionClick(self, args):
        vehicle = self._vehicle
        action = vehicle.postProgression.getStep(int(args['stepID'])).action.getServerAction(factory, vehicle)
        yield factory.asyncDoAction(action)

    @process
    def _onPrebattleSwitchToggleClick(self, args):
        stepID = int(args['stepID'])
        if stepID in self.__togglingSteps:
            return
        elif self.__lockTogglingCallbackID is not None:
            return
        else:
            self.__lockToggling()
            self.__togglingSteps.add(stepID)
            featureName = self._vehicle.postProgression.getStep(stepID).action.getTechName()
            groupID = GROUP_ID_BY_FEATURE[featureName]
            action = factory.getAction(factory.SWITCH_PREBATTLE_AMMO_PANEL_AVAILABILITY, self._vehicle, groupID, args['active'])
            yield factory.asyncDoAction(action)
            self.__togglingSteps.discard(stepID)
            return

    @process
    def _onMultiStepActionClick(self, args):
        vehicle = self._vehicle
        stepID, modificationID = int(args['stepID']), int(args['modificationID'])
        action = vehicle.postProgression.getStep(stepID).action.getServerAction(factory, vehicle, modificationID)
        yield factory.asyncDoAction(action)

    def _updateVehicle(self, *args, **kwargs):
        self._vehicle = self.__itemsCache.items.getItemByCD(self.__intCD)
        self._selectionProvider.mergePostProgression(self._vehicle.postProgression)
        self._notifyCustomState(needDiff=False)

    def _updateViewModel(self, viewModel, availabilityReason, completion):
        super(PostProgressionCfgComponentView, self)._updateViewModel(viewModel, availabilityReason, completion)
        viewModel.setProgressionState(_COMPLETION_MAP[completion])
        viewModel.setProgressionAvailability(_AVAILABILITY_MAP[availabilityReason])

    def _fillControlsModel(self, model, postProgression):
        toPurchaseKPIs = []
        toPurchasePrice = EXT_MONEY_UNDEFINED
        toPurchaseIDs = self.__getStepsToPurchase(postProgression)
        purchasePreviw = model.purchasePreview
        featureStepIds = purchasePreviw.getPurchasedFeatureStepIds()
        multiStepIds = purchasePreviw.getUnlockedMultiStepIds()
        singleStepIds = purchasePreviw.getPurchasedSingleStepIds()
        featureStepIds.clear()
        multiStepIds.clear()
        singleStepIds.clear()
        for stepID in toPurchaseIDs:
            step = postProgression.getStep(stepID)
            toPurchaseKPIs.extend(step.action.getKpi())
            toPurchasePrice += step.getPrice()
            singleStepIds.addNumber(stepID)
            if step.action.isFeatureAction():
                featureStepIds.addNumber(stepID)
            for childStepID in step.getNextStepIDs():
                childStep = postProgression.getStep(childStepID)
                if childStep.action.isMultiAction():
                    multiStepIds.addNumber(childStepID)

        featureStepIds.invalidate()
        multiStepIds.invalidate()
        singleStepIds.invalidate()
        purchaseCheck = PurchaseProvider.mayConsumeWithExhange(self.__balance, toPurchasePrice, self.__creditsRate)
        self.__fillPriceModel(purchasePreviw.price, toPurchasePrice, purchaseCheck)
        self._fillBonusesArray(purchasePreviw.modificationBonuses.getItems(), toPurchaseKPIs)

    def _fillModification(self, modModel, modification):
        super(PostProgressionCfgComponentView, self)._fillModification(modModel, modification)
        self.__fillPriceModel(modModel.price, modification.getPrice(), modification.mayPurchaseWithExchange(balance=self.__balance, creditsRate=self.__creditsRate, ignoreState=True))

    def _fillMultiStepModel(self, stepModel, step, selectedModID):
        super(PostProgressionCfgComponentView, self)._fillMultiStepModel(stepModel, step, selectedModID)
        stepModel.setStepState(_STEP_STATE_MAP[step.getState()])
        stepModel.setReceivedIdx(step.action.getPurchasedIdx())

    def _fillPersistentBonuses(self, bonuses, postProgression, completion):
        mainSelection = self._selectionProvider.getSelectedMainSteps()
        isCollectAll = completion == PostProgressionCompletion.EMPTY and not mainSelection
        pesistentKPIs = []
        for step in postProgression.iterUnorderedSteps():
            isValidStep = not step.isRestricted() and not step.action.isMultiAction()
            if isValidStep and (isCollectAll or step.isReceived() or step.stepID in mainSelection):
                pesistentKPIs.extend(step.action.getKpi(self._vehicle))

        self._fillBonusesArray(bonuses.getItems(), pesistentKPIs)

    def _fillSingleStepModel(self, stepModel, step):
        super(PostProgressionCfgComponentView, self)._fillSingleStepModel(stepModel, step)
        stepModel.setStepState(_STEP_STATE_MAP[step.getState()])
        featureName = self._vehicle.postProgression.getStep(step.stepID).action.getTechName()
        groupID = GROUP_ID_BY_FEATURE.get(featureName)
        if groupID is not None:
            stepModel.setIsPrebattleSwitchEnabled(not self._vehicle.postProgression.isPrebattleSwitchDisabled(groupID))
        else:
            stepModel.setIsPrebattleSwitchEnabled(True)
        return

    @process
    def __onPurchaseClick(self):
        vehicle = self._vehicle
        toPurchaseIDs = self.__getStepsToPurchase(vehicle.postProgression)
        action = factory.getAction(factory.PURCHASE_POST_PROGRESSION_STEPS, vehicle, toPurchaseIDs)
        yield factory.asyncDoAction(action)

    def __onGoBackAction(self):
        self.onGoBackAction()

    def __onResearchAction(self):
        self.onResearchAction()

    def __onSyncCompleted(self, reason, diff):
        changedVehicles = diff.get(GUI_ITEM_TYPE.VEHICLE, {})
        if self.__intCD in changedVehicles or reason in (CACHE_SYNC_REASON.SHOW_GUI, CACHE_SYNC_REASON.SHOP_RESYNC):
            self.__balance = self.__itemsCache.items.stats.getMoneyExt(self.__intCD)
            self.__creditsRate = self.__itemsCache.items.shop.exchangeRate
            self._updateAll()

    def __lockToggling(self):
        self.__updateTogglingLock(True)
        self.__lockTogglingCallbackID = BigWorld.callback(_TOGGLING_COOLDOWN, self.__unlockToggling)

    def __unlockToggling(self):
        self.__updateTogglingLock(False)
        self.__cancelLockToggling()

    def __cancelLockToggling(self):
        if self.__lockTogglingCallbackID is not None:
            BigWorld.cancelCallback(self.__lockTogglingCallbackID)
            self.__lockTogglingCallbackID = None
        return

    def __updateTogglingLock(self, isLocked):
        with self.viewModel.grid.transaction() as gridModel:
            for singleStep in gridModel.getMainSteps():
                singleStep.setIsPrebattleSwitchLocked(isLocked)

    def __fillPriceModel(self, priceModel, price, checkResult):
        prices = priceModel.getPrice()
        prices.clear()
        for currency, amount in price.iteritems():
            itemPriceModel = PriceItemModel()
            itemPriceModel.setName(currency)
            itemPriceModel.setValue(amount)
            itemPriceModel.setIsEnough(checkResult.result)
            prices.addViewModel(itemPriceModel)

        prices.invalidate()

    def __getStepsToPurchase(self, postProgression):
        return list(self._selectionProvider.getSelectedMainSteps()) or self.__getUnlockedMainSteps(postProgression)

    def __getUnlockedMainSteps(self, postProgression):
        result = []
        for stepItem in postProgression.iterUnorderedSteps():
            if stepItem.isUnlocked() and not stepItem.action.isMultiAction():
                result.append(stepItem.stepID)

        return result

    def __updateMoney(self, *_):
        self.__balance = self.__itemsCache.items.stats.getMoneyExt(self.__intCD)
        self._updateAll()
