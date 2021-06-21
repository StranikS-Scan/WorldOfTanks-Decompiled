# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/veh_post_progression/vehicle_post_progression_component.py
import logging
import typing
from adisp import process
from Event import Event, EventManager
from frameworks.wulf import ViewFlags, ViewSettings
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.impl.gen import R
from gui.impl.gen.view_models.common.bonus_model import BonusModel
from gui.impl.gen.view_models.common.bonus_value_model import BonusValueModel
from gui.impl.gen.view_models.common.price_item_model import PriceItemModel
from gui.impl.gen.view_models.views.lobby.post_progression.modification_model import RoleCategory, ModificationModel
from gui.impl.gen.view_models.views.lobby.post_progression.base_step_model import ActionState, ActionType, StepState
from gui.impl.gen.view_models.views.lobby.post_progression.multi_step_model import MultiStepModel
from gui.impl.gen.view_models.views.lobby.post_progression.post_progression_view_model import PostProgressionViewModel, ProgressionAvailability, ProgressionState
from gui.impl.gen.view_models.views.lobby.post_progression.post_progression_grid_model import PostProgressionGridModel
from gui.impl.gen.view_models.views.lobby.post_progression.single_step_model import SingleStepModel
from gui.impl.lobby.veh_post_progression.tooltip.pair_modification_tooltip_view import PairModificationTooltipView
from gui.impl.lobby.veh_post_progression.tooltip.post_progression_level_tooltip_view import PostProgressionLevelTooltipView
from gui.impl.lobby.veh_post_progression.tooltip.role_slot_tooltip_view import RoleSlotTooltipView
from gui.impl.lobby.veh_post_progression.tooltip.setup_tooltip_view import SetupTooltipView
from gui.impl.pub import ViewImpl
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.items_actions import factory
from gui.shared.items_cache import CACHE_SYNC_REASON
from gui.shared.items_parameters.functions import aggregateKpi
from gui.veh_post_porgression.models.ext_money import ExtendedMoney, ExtendedCurrency, EXT_MONEY_UNDEFINED
from gui.veh_post_porgression.models.modifications import PostProgressionActionState, PostProgressionActionTooltip
from gui.veh_post_porgression.models.progression import PostProgressionAvailability, PostProgressionCompletion
from gui.veh_post_porgression.models.progression_step import PostProgressionStepState
from gui.veh_post_porgression.models.purchase import PurchaseCheckResult, PurchaseProvider
from helpers import dependency
from items.components.supply_slot_categories import SlotCategories
from post_progression_common import ACTION_TYPES
from skeletons.gui.shared import IItemsCache
from skeletons.gui.game_control import IWalletController
if typing.TYPE_CHECKING:
    from frameworks.wulf import Array, ViewEvent
    from gui.impl.gen.view_models.common.price_model import PriceModel
    from gui.veh_post_porgression.models.modifications import SimpleModItem
    from gui.veh_post_porgression.models.progression import PostProgressionItem
    from gui.veh_post_porgression.models.progression_step import PostProgressionStepItem
    from gui.impl.gen.view_models.common.bonuses_model import BonusesModel
    from gui.impl.gen.view_models.views.lobby.post_progression.restrictions_model import RestrictionsModel
    from gui.impl.gen.view_models.views.lobby.post_progression.post_progression_purchase_model import PostProgressionPurchaseModel
    from gui.shared.gui_items import KPI
    from items.artefacts_helpers import VehicleFilter
    from post_progression_common import VehicleState
_logger = logging.getLogger(__name__)
_NOT_SELECTED_IDX = -1
_ACTION_TYPE_MAP = {ACTION_TYPES.MODIFICATION: ActionType.MODIFICATION,
 ACTION_TYPES.PAIR_MODIFICATION: ActionType.PAIRMODIFICATION,
 ACTION_TYPES.FEATURE: ActionType.MODIFICATIONWITHFEATURE}
_ACTION_STATE_MAP = {PostProgressionActionState.PERSISTENT: ActionState.PERSISTENT,
 PostProgressionActionState.SELECTABLE: ActionState.SELECTABLE,
 PostProgressionActionState.CHANGEABLE: ActionState.CHANGEABLE}
_ACTION_TOOLTIP_MAP = {PostProgressionActionTooltip.SIMPLEMOD: R.invalid(),
 PostProgressionActionTooltip.MULTIMOD: R.views.lobby.veh_post_progression.tooltip.PairModificationTooltipView(),
 PostProgressionActionTooltip.FEATURE: R.views.lobby.veh_post_progression.tooltip.SetupTooltipView(),
 PostProgressionActionTooltip.ROLESLOT: R.views.lobby.veh_post_progression.tooltip.RoleSlotTooltipView()}
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
_CATEGORY_MAP = {SlotCategories.STEALTH: RoleCategory.STEALTH,
 SlotCategories.MOBILITY: RoleCategory.MOBILITY,
 SlotCategories.UNIVERSAL: RoleCategory.NONE,
 SlotCategories.FIREPOWER: RoleCategory.FIREPOWER,
 SlotCategories.SURVIVABILITY: RoleCategory.SURVIVABILITY}
_COMPLETION_MAP = {PostProgressionCompletion.EMPTY: ProgressionState.INITIAL,
 PostProgressionCompletion.PARTIAL: ProgressionState.TRANSITIONAL,
 PostProgressionCompletion.FULL: ProgressionState.FINAL}
_STEP_STATE_MAP = {PostProgressionStepState.RESTRICTED: StepState.RESTRICTED,
 PostProgressionStepState.LOCKED: StepState.UNAVAILABLELOCKED,
 PostProgressionStepState.RECEIVED: StepState.RECEIVED,
 PostProgressionStepState.UNLOCKED: StepState.AVAILABLEPURCHASE}

class _SelectionProvider(object):
    __slots__ = ('__mainStepsBorder', '__mainStepsSelection', '__multiStepsSelection', '__postProgression')

    def __init__(self):
        self.__mainStepsBorder = 0
        self.__mainStepsSelection = set()
        self.__multiStepsSelection = {}
        self.__postProgression = None
        return

    def getCustomProgressionState(self):
        progression = self.__postProgression
        stateCopy = progression.getState()
        for stepID in self.__mainStepsSelection:
            stateCopy.addUnlock(stepID)
            stepAction = progression.getStep(stepID).action
            if stepAction.isFeatureAction():
                stateCopy.addFeature(stepAction.actionID)

        for stepID, modID in self.__multiStepsSelection.iteritems():
            stateCopy.addUnlock(stepID)
            stepAction = progression.getStep(stepID).action
            stateCopy.setPair(stepID, stepAction.getInnerPairType(modID))

        return stateCopy

    def getSelectedMainSteps(self):
        return self.__mainStepsSelection

    def getSelectedMultiSteps(self):
        return self.__multiStepsSelection

    def setPostProgression(self, progression):
        self.__postProgression = progression
        mainSteps = self.__mainStepsSelection
        invalidMainIds = set()
        for stepID in mainSteps:
            if progression.getStep(stepID).isReceived():
                invalidMainIds.add(stepID)

        mainSteps -= invalidMainIds
        multiSteps = self.__multiStepsSelection
        invalidMultiIDs = []
        for stepID, modID in multiSteps.iteritems():
            if progression.getStep(stepID).action.getPurchasedID() == modID:
                invalidMultiIDs.append(stepID)

        for invalidStepID in invalidMultiIDs:
            multiSteps.pop(invalidStepID)

    def selectMainStep(self, stepID, isInternal=False):
        mainSteps = self.__mainStepsSelection
        if stepID == self.__mainStepsBorder:
            mainSteps.clear()
            self.__mainStepsBorder = 0
            self.__invalidateRelations()
            return
        progression = self.__postProgression
        if progression.getStep(stepID).isReceived() or stepID in mainSteps:
            mainSteps.clear()
        for orderedStep in progression.iterOrderedSteps():
            if not orderedStep.action.isMultiAction() and not orderedStep.isReceived():
                mainSteps.add(orderedStep.stepID)
            if orderedStep.stepID == stepID:
                self.__mainStepsBorder = stepID
                break

        if not isInternal:
            self.__invalidateRelations()

    def selectMultiStep(self, stepID, modID):
        progression = self.__postProgression
        if modID == progression.getStep(stepID).action.getPurchasedID():
            return
        multiSteps = self.__multiStepsSelection
        if stepID in multiSteps and modID == multiSteps[stepID]:
            multiSteps.pop(stepID)
            return
        multiSteps[stepID] = modID
        parentStep = progression.getStep(progression.getStep(stepID).getParentStepID())
        if not parentStep.isReceived() and parentStep.stepID not in self.__mainStepsSelection:
            self.selectMainStep(parentStep.stepID, isInternal=True)

    def __invalidateRelations(self):
        invalidMultiIDs = []
        postProgression = self.__postProgression
        for stepID in self.__multiStepsSelection:
            parentStep = postProgression.getStep(postProgression.getStep(stepID).getParentStepID())
            if not parentStep.isReceived() and parentStep.stepID not in self.__mainStepsSelection:
                invalidMultiIDs.append(stepID)

        for invalidStepID in invalidMultiIDs:
            self.__multiStepsSelection.pop(invalidStepID)


class VehiclePostProgressionComponentView(ViewImpl):
    __itemsCache = dependency.descriptor(IItemsCache)
    __walletController = dependency.descriptor(IWalletController)
    __slots__ = ('onGoBackAction', 'onResearchAction', 'onCustomProgressionState', 'onViewRendered', '__balance', '__eventManager', '__intCD', '__selectionProvider', '__vehicle')

    def __init__(self, layoutID=R.views.lobby.veh_post_progression.VehiclePostProgressionView(), **kwargs):
        settings = ViewSettings(layoutID, flags=ViewFlags.COMPONENT, model=PostProgressionViewModel())
        settings.kwargs = kwargs
        super(VehiclePostProgressionComponentView, self).__init__(settings)
        self.__balance, self.__intCD, self.__vehicle = (None, None, None)
        self.__selectionProvider = _SelectionProvider()
        self.__eventManager = EventManager()
        self.onGoBackAction = Event(self.__eventManager)
        self.onResearchAction = Event(self.__eventManager)
        self.onCustomProgressionState = Event(self.__eventManager)
        self.onViewRendered = Event(self.__eventManager)
        return None

    @property
    def viewModel(self):
        return super(VehiclePostProgressionComponentView, self).getViewModel()

    def invalidateVehicle(self, intCD):
        self.__intCD = intCD
        self.__updateVehicle()

    def createToolTipContent(self, event, contentID):
        stepId, modId = self.__parseTooltipEvent(event)
        if contentID == R.views.lobby.veh_post_progression.tooltip.PairModificationTooltipView() and stepId is not None and modId is not None:
            return PairModificationTooltipView(self.__vehicle.postProgression.getStep(stepId), modId)
        elif contentID == R.views.lobby.veh_post_progression.tooltip.RoleSlotTooltipView() and stepId is not None:
            return RoleSlotTooltipView(step=self.__vehicle.postProgression.getStep(stepId))
        elif contentID == R.views.lobby.veh_post_progression.tooltip.SetupTooltipView() and stepId is not None:
            return SetupTooltipView(step=self.__vehicle.postProgression.getStep(stepId))
        else:
            return PostProgressionLevelTooltipView(self.__vehicle.postProgression.getStep(stepId)) if contentID == R.views.lobby.veh_post_progression.tooltip.PostProgressionLevelTooltipView() and stepId is not None else super(VehiclePostProgressionComponentView, self).createToolTipContent(event, contentID)

    def _onLoading(self, intCD=None, *args, **kwargs):
        super(VehiclePostProgressionComponentView, self)._onLoading(intCD, *args, **kwargs)
        self.__intCD = intCD
        self.__updateAll()

    def _initialize(self, *args, **kwargs):
        super(VehiclePostProgressionComponentView, self)._initialize(*args, **kwargs)
        self.__addListeners()

    def _finalize(self):
        self.__removeListeners()
        super(VehiclePostProgressionComponentView, self)._finalize()

    def __addListeners(self):
        grid = self.viewModel.grid
        grid.onMainStepSelectClick += self.__onMainStepSelectClick
        grid.onMultiStepSelectClick += self.__onMultiStepSelectClick
        grid.onMainStepActionClick += self.__onMainStepActionClick
        grid.onMultiStepActionClick += self.__onMultiStepActionClick
        self.viewModel.purchasePreview.onPurchaseClick += self.__onPurchaseClick
        self.viewModel.onGoBackAction += self.__onGoBackAction
        self.viewModel.onResearchAction += self.__onResearchAction
        self.viewModel.onViewRendered += self.__onViewRendered
        self.__itemsCache.onSyncCompleted += self.__onSyncCompleted
        self.__walletController.onWalletStatusChanged += self.__updateAll
        g_clientUpdateManager.addCallbacks({'stats.{}'.format(c):self.__updateAll for c in ExtendedCurrency.ALL})

    def __removeListeners(self):
        grid = self.viewModel.grid
        grid.onMainStepSelectClick -= self.__onMainStepSelectClick
        grid.onMultiStepSelectClick -= self.__onMultiStepSelectClick
        grid.onMainStepActionClick -= self.__onMainStepActionClick
        grid.onMultiStepActionClick -= self.__onMultiStepActionClick
        self.viewModel.purchasePreview.onPurchaseClick -= self.__onPurchaseClick
        self.viewModel.onGoBackAction -= self.__onGoBackAction
        self.viewModel.onResearchAction -= self.__onResearchAction
        self.viewModel.onViewRendered -= self.__onViewRendered
        self.__itemsCache.onSyncCompleted -= self.__onSyncCompleted
        self.__walletController.onWalletStatusChanged -= self.__updateAll
        self.__eventManager.clear()
        g_clientUpdateManager.removeObjectCallbacks(self)

    def __onGoBackAction(self):
        self.onGoBackAction()

    def __onResearchAction(self):
        self.onResearchAction()

    def __onViewRendered(self):
        self.onViewRendered()

    def __onMainStepSelectClick(self, args):
        self.__selectionProvider.selectMainStep(int(args['stepID']))
        self.__updateSelection()

    def __onMultiStepSelectClick(self, args):
        stepID, modificationID = int(args['stepID']), int(args['modificationID'])
        self.__selectionProvider.selectMultiStep(stepID, modificationID)
        self.__updateSelection(needDiff=stepID in self.__selectionProvider.getSelectedMultiSteps())

    @process
    def __onMainStepActionClick(self, args):
        vehicle = self.__vehicle
        action = vehicle.postProgression.getStep(int(args['stepID'])).action.getServerAction(factory, vehicle)
        yield factory.asyncDoAction(action)

    @process
    def __onMultiStepActionClick(self, args):
        vehicle = self.__vehicle
        stepID, modificationID = int(args['stepID']), int(args['modificationID'])
        action = vehicle.postProgression.getStep(stepID).action.getServerAction(factory, vehicle, modificationID)
        yield factory.asyncDoAction(action)

    @process
    def __onPurchaseClick(self):
        vehicle = self.__vehicle
        toPurchaseIDs = self.__getStepsToPurchase(vehicle.postProgression)
        action = factory.getAction(factory.PURCHASE_POST_PROGRESSION_STEPS, vehicle, toPurchaseIDs)
        yield factory.asyncDoAction(action)

    def __onSyncCompleted(self, reason, diff):
        changedVehicles = diff.get(GUI_ITEM_TYPE.VEHICLE, {})
        if self.__intCD in changedVehicles or reason in (CACHE_SYNC_REASON.SHOW_GUI, CACHE_SYNC_REASON.SHOP_RESYNC):
            self.__updateAll()

    def __buildSingleStepModel(self, step, creditsRate):
        action = step.action
        stepModel = SingleStepModel()
        stepModel.setId(step.stepID)
        stepModel.setActionType(_ACTION_TYPE_MAP[action.actionType])
        stepModel.setActionState(_ACTION_STATE_MAP[action.getState()])
        stepModel.setIsDisabled(action.isDisabled())
        stepModel.setStepState(_STEP_STATE_MAP[step.getState()])
        self.__fillChildrenArray(stepModel.getChildrenIds(), step.getNextStepIDs())
        self.__fillModification(stepModel.modification, action, creditsRate)
        self.__fillRestrictionsModel(stepModel.restrictions, step.getRestrictions())
        return stepModel

    def __buildMultiStepModel(self, step, creditsRate, selectedModID):
        action = step.action
        stepModel = MultiStepModel()
        stepModel.setId(step.stepID)
        stepModel.setActionType(_ACTION_TYPE_MAP[action.actionType])
        stepModel.setActionState(_ACTION_STATE_MAP[action.getState()])
        stepModel.setIsDisabled(action.isDisabled())
        stepModel.setParentId(step.getParentStepID())
        stepModel.setStepState(_STEP_STATE_MAP[step.getHackedState()])
        stepModel.setReceivedIdx(action.getPurchasedIdx())
        stepModel.setSelectedIdx(action.getInnerIdx(selectedModID) if selectedModID is not None else _NOT_SELECTED_IDX)
        self.__fillModificationsArray(stepModel.getModifications(), action.modifications, creditsRate)
        self.__fillRestrictionsModel(stepModel.restrictions, step.getRestrictions())
        return stepModel

    def __fillBonusesArray(self, bonusesArray, kpiList):
        bonusesArray.clear()
        aggregatedBonuses = aggregateKpi(kpiList)
        uniqBonuses = set()
        for kpiName in (uniqBonuses.add(kpi.name) or kpi.name for kpi in kpiList if kpi.name not in uniqBonuses):
            kpi = aggregatedBonuses.getKpi(kpiName)
            value = BonusValueModel()
            value.setValue(kpi.value)
            value.setValueKey(kpiName)
            value.setValueType(kpi.type)
            bonusModel = BonusModel()
            bonusModel.setLocaleName(kpiName)
            bonusModel.getValues().addViewModel(value)
            bonusesArray.addViewModel(bonusModel)

        bonusesArray.invalidate()

    def __fillChildrenArray(self, childrenArray, childrenIds):
        for childID in childrenIds:
            childrenArray.addNumber(childID)

    def __fillGridModel(self, grid, postProgression, creditsRate):
        mainSteps, multiSteps = grid.getMainSteps(), grid.getMultiSteps()
        mainSelection = self.__selectionProvider.getSelectedMainSteps()
        multiSelection = self.__selectionProvider.getSelectedMultiSteps()
        mainSelectedIdx = mainCounter = -1
        multiSteps.clear()
        mainSteps.clear()
        for step in postProgression.iterOrderedSteps():
            if step.action.isMultiAction():
                multiStep = self.__buildMultiStepModel(step, creditsRate, multiSelection.get(step.stepID))
                multiSteps.addViewModel(multiStep)
            mainCounter += 1
            mainSteps.addViewModel(self.__buildSingleStepModel(step, creditsRate))
            mainSelectedIdx = mainCounter if step.stepID in mainSelection else mainSelectedIdx

        mainSteps.invalidate()
        multiSteps.invalidate()
        grid.setMainSelectedIdx(mainSelectedIdx)

    def __fillModification(self, modModel, modification, creditsRate):
        modModel.setId(modification.actionID)
        modModel.setImageResName(modification.getImageName())
        modModel.setTitleRes(modification.getLocSplitNameRes()())
        modModel.setTooltipContentId(_ACTION_TOOLTIP_MAP[modification.getTooltip()])
        modModel.setRoleCategory(_CATEGORY_MAP[modification.getSlotCategory()])
        self.__fillPriceModel(modModel.price, modification.getPrice(), modification.mayPurchaseWithExchange(balance=self.__balance, creditsRate=creditsRate, ignoreState=True))

    def __fillModificationsArray(self, modsArray, modifications, creditsRate):
        for modification in modifications:
            modificationModel = ModificationModel()
            self.__fillModification(modificationModel, modification, creditsRate)
            modsArray.addViewModel(modificationModel)

    def __fillPersistentBonuses(self, bonuses, postProgression, completion):
        mainSelection = self.__selectionProvider.getSelectedMainSteps()
        isCollectAll = completion == PostProgressionCompletion.EMPTY and not mainSelection
        pesistentKPIs = []
        for step in postProgression.iterUnorderedSteps():
            isValidStep = not step.isRestricted() and not step.action.isMultiAction()
            if isValidStep and (isCollectAll or step.isReceived() or step.stepID in mainSelection):
                pesistentKPIs.extend(step.action.getKpi(self.__vehicle))

        self.__fillBonusesArray(bonuses.getItems(), pesistentKPIs)

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

    def __fillPurchasePreview(self, purchasePreviw, postProgression, creditsRate):
        toPurchaseKPIs = []
        toPurchasePrice = EXT_MONEY_UNDEFINED
        toPurchaseIDs = self.__getStepsToPurchase(postProgression)
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
        purchaseCheck = PurchaseProvider.mayConsumeWithExhange(self.__balance, toPurchasePrice, creditsRate)
        self.__fillPriceModel(purchasePreviw.price, toPurchasePrice, purchaseCheck)
        self.__fillBonusesArray(purchasePreviw.modificationBonuses.getItems(), toPurchaseKPIs)

    def __fillRestrictionsModel(self, restrictionsModel, restrictions):
        if restrictions is None:
            return
        else:
            allowedLevels = restrictionsModel.getAllowedLevels()
            minLvl, maxLvl = restrictions.getLevelRange()
            for level in xrange(minLvl, maxLvl + 1):
                allowedLevels.addNumber(level)

            return

    def __getStepsToPurchase(self, postProgression):
        return list(self.__selectionProvider.getSelectedMainSteps()) or self.__getUnlockedMainSteps(postProgression)

    def __getUnlockedMainSteps(self, postProgression):
        result = []
        for stepItem in postProgression.iterUnorderedSteps():
            if stepItem.isUnlocked() and not stepItem.action.isMultiAction():
                result.append(stepItem.stepID)

        return result

    def __notifyCustomState(self, needDiff=True):
        self.onCustomProgressionState(self.__selectionProvider.getCustomProgressionState(), needDiff)

    def __parseTooltipEvent(self, event):
        stepId = event.getArgument('stepId')
        modId = event.getArgument('modificationId')
        if stepId is not None:
            stepId = int(stepId)
        if modId is not None:
            modId = int(modId)
        return (stepId, modId)

    def __updateAll(self, *_):
        self.__updateVehicle()
        _, availabilityReason = self.__vehicle.postProgressionAvailability
        if availabilityReason is PostProgressionAvailability.NOT_EXISTS:
            return
        self.__balance = self.__itemsCache.items.stats.getMoneyExt(self.__intCD)
        creditsRate = self.__itemsCache.items.shop.exchangeRate
        postProgression = self.__vehicle.postProgression
        completion = postProgression.getCompletion()
        with self.viewModel.transaction() as model:
            self.__updateViewModel(model, availabilityReason, completion)
            self.__fillGridModel(model.grid, postProgression, creditsRate)
            self.__fillPersistentBonuses(model.persistentBonuses, postProgression, completion)
            self.__fillPurchasePreview(model.purchasePreview, postProgression, creditsRate)

    def __updateSelection(self, needDiff=False):
        creditsRate = self.__itemsCache.items.shop.exchangeRate
        postProgression = self.__vehicle.postProgression
        with self.viewModel.transaction() as model:
            self.__fillGridModel(model.grid, postProgression, creditsRate)
            self.__fillPersistentBonuses(model.persistentBonuses, postProgression, postProgression.getCompletion())
            self.__fillPurchasePreview(model.purchasePreview, postProgression, creditsRate)
        self.__notifyCustomState(needDiff=needDiff)

    def __updateVehicle(self):
        self.__vehicle = self.__itemsCache.items.getItemByCD(self.__intCD)
        self.__selectionProvider.setPostProgression(self.__vehicle.postProgression)
        self.__notifyCustomState(needDiff=False)

    def __updateViewModel(self, viewModel, availabilityReason, completion):
        viewModel.setProgressionAvailability(_AVAILABILITY_MAP[availabilityReason])
        viewModel.setProgressionState(_COMPLETION_MAP[completion])
        viewModel.setVehicleRole(self.__vehicle.roleLabel if self.__vehicle.role else '')
