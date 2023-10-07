# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/veh_post_progression/post_progression_base_component.py
import typing
from Event import Event, EventManager
from frameworks.wulf import ViewFlags, ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.common.bonus_model import BonusModel
from gui.impl.gen.view_models.common.bonus_value_model import BonusValueModel
from gui.impl.gen.view_models.views.lobby.post_progression.modification_model import RoleCategory, ModificationModel
from gui.impl.gen.view_models.views.lobby.post_progression.base_step_model import ActionType
from gui.impl.gen.view_models.views.lobby.post_progression.step_model import ActionState
from gui.impl.gen.view_models.views.lobby.post_progression.multi_step_model import MultiStepModel
from gui.impl.gen.view_models.views.lobby.post_progression.single_step_model import SingleStepModel
from gui.impl.gen.view_models.views.lobby.post_progression.post_progression_grid_model import PostProgressionGridModel
from gui.impl.pub import ViewImpl
from gui.shared.items_parameters.functions import aggregateKpi
from gui.veh_post_progression.models.modifications import PostProgressionActionState, PostProgressionActionTooltip
from gui.veh_post_progression.models.progression import PostProgressionAvailability, PostProgressionCompletion
from items.components.supply_slot_categories import SlotCategories
from post_progression_common import ACTION_TYPES, VehicleState
if typing.TYPE_CHECKING:
    from frameworks.wulf import Array, ViewEvent
    from gui.veh_post_progression.models.modifications import SimpleModItem
    from gui.veh_post_progression.models.progression import PostProgressionItem
    from gui.veh_post_progression.models.progression_step import PostProgressionStepItem
    from gui.impl.gen.view_models.common.bonuses_model import BonusesModel
    from gui.impl.gen.view_models.views.lobby.post_progression.restrictions_model import RestrictionsModel
    from gui.impl.gen.view_models.views.lobby.post_progression.post_progression_base_view_model import PostProgressionBaseViewModel
    from gui.shared.gui_items import KPI
    from items.artefacts_helpers import VehicleFilter
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
_CATEGORY_MAP = {SlotCategories.STEALTH: RoleCategory.STEALTH,
 SlotCategories.MOBILITY: RoleCategory.MOBILITY,
 SlotCategories.UNIVERSAL: RoleCategory.NONE,
 SlotCategories.FIREPOWER: RoleCategory.FIREPOWER,
 SlotCategories.SURVIVABILITY: RoleCategory.SURVIVABILITY}

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
            step = progression.getStep(stepID)
            if step.action.isFeatureAction():
                stateCopy.addFeature(step.action.actionID)
            for childStepID in step.getNextStepIDs():
                if progression.getStep(childStepID).action.isMultiAction():
                    stateCopy.addUnlock(childStepID)

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
        self.__mainStepsBorder = 0
        self.__mainStepsSelection.clear()
        self.__multiStepsSelection.clear()
        for step in progression.iterOrderedSteps():
            if not step.isReceived():
                continue
            if not step.action.isMultiAction():
                self.__mainStepsSelection.add(step.stepID)
                self.__mainStepsBorder = step.stepID
            if step.action.isPurchased():
                self.__multiStepsSelection[step.stepID] = step.action.getPurchasedID()

        progression.setState(VehicleState())
        self.__postProgression = progression

    def mergePostProgression(self, progression):
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


class PostProgressionBaseComponentView(ViewImpl):
    __slots__ = ('onCustomProgressionState', 'onViewRendered', '_selectionProvider', '_vehicle', '_eventManager')

    def __init__(self, layoutID, model, **kwargs):
        settings = ViewSettings(layoutID=layoutID, flags=ViewFlags.VIEW, model=model)
        settings.kwargs = kwargs
        super(PostProgressionBaseComponentView, self).__init__(settings)
        self._vehicle = None
        self._selectionProvider = _SelectionProvider()
        self._eventManager = EventManager()
        self.onCustomProgressionState = Event(self._eventManager)
        self.onViewRendered = Event(self._eventManager)
        return

    @property
    def viewModel(self):
        return super(PostProgressionBaseComponentView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(PostProgressionBaseComponentView, self)._onLoading(*args, **kwargs)
        self._updateAll()

    def _initialize(self, *args, **kwargs):
        super(PostProgressionBaseComponentView, self)._initialize(*args, **kwargs)
        self._addListeners()

    def _finalize(self):
        self._removeListeners()
        super(PostProgressionBaseComponentView, self)._finalize()

    def _addListeners(self):
        grid = self.viewModel.grid
        grid.onMainStepActionClick += self._onMainStepActionClick
        grid.onMultiStepActionClick += self._onMultiStepActionClick
        grid.onMainStepSelectClick += self.__onMainStepSelectClick
        grid.onMultiStepSelectClick += self.__onMultiStepSelectClick
        self.viewModel.onViewRendered += self.__onViewRendered

    def _removeListeners(self):
        grid = self.viewModel.grid
        grid.onMainStepActionClick -= self._onMainStepActionClick
        grid.onMultiStepActionClick -= self._onMultiStepActionClick
        grid.onMainStepSelectClick -= self.__onMainStepSelectClick
        grid.onMultiStepSelectClick -= self.__onMultiStepSelectClick
        self.viewModel.onViewRendered -= self.__onViewRendered
        self._eventManager.clear()

    def _onMainStepActionClick(self, args):
        pass

    def _onMultiStepActionClick(self, args):
        pass

    def _updateAll(self, *args, **kwargs):
        self._updateVehicle(*args, **kwargs)
        _, availabilityReason = self._vehicle.postProgressionAvailability()
        if availabilityReason is PostProgressionAvailability.NOT_EXISTS:
            return
        postProgression = self._vehicle.postProgression
        completion = postProgression.getCompletion()
        with self.viewModel.transaction() as model:
            self._updateViewModel(model, availabilityReason, completion)
            self.__fillGridModel(model.grid, postProgression)
            self._fillPersistentBonuses(model.persistentBonuses, postProgression, completion)
            self._fillControlsModel(model, postProgression)

    def _updateVehicle(self, *args, **kwargs):
        raise NotImplementedError

    def _updateViewModel(self, viewModel, availabilityReason, completion):
        viewModel.setVehicleRole(self._vehicle.roleLabel if self._vehicle.role else '')

    def _fillBonusesArray(self, bonusesArray, kpiList):
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

    def _fillControlsModel(self, model, postProgression):
        pass

    def _fillModification(self, modModel, modification):
        modModel.setId(modification.actionID)
        modModel.setImageResName(modification.getImageName())
        modModel.setTitleRes(modification.getLocSplitNameRes()())
        modModel.setTooltipContentId(_ACTION_TOOLTIP_MAP[modification.getTooltip()])
        modModel.setRoleCategory(_CATEGORY_MAP[modification.getSlotCategory()])

    def _fillMultiStepModel(self, stepModel, step, selectedModID):
        action = step.action
        stepModel.setId(step.stepID)
        stepModel.setActionType(_ACTION_TYPE_MAP[action.actionType])
        stepModel.setActionState(_ACTION_STATE_MAP[action.getState()])
        stepModel.setIsDisabled(action.isDisabled())
        stepModel.setParentId(step.getParentStepID())
        stepModel.setSelectedIdx(action.getInnerIdx(selectedModID) if selectedModID is not None else _NOT_SELECTED_IDX)
        self.__fillModificationsArray(stepModel.getModifications(), action.modifications)
        self.__fillRestrictionsModel(stepModel.restrictions, step.getRestrictions())
        return

    def _fillPersistentBonuses(self, bonuses, postProgression, completion):
        pass

    def _fillSingleStepModel(self, stepModel, step):
        action = step.action
        stepModel.setId(step.stepID)
        stepModel.setActionType(_ACTION_TYPE_MAP[action.actionType])
        stepModel.setActionState(_ACTION_STATE_MAP[action.getState()])
        stepModel.setIsDisabled(action.isDisabled())
        self._fillModification(stepModel.modification, action)
        self.__fillChildrenArray(stepModel.getChildrenIds(), step.getNextStepIDs())
        self.__fillRestrictionsModel(stepModel.restrictions, step.getRestrictions())

    def _notifyCustomState(self, needDiff=True):
        self.onCustomProgressionState(self._selectionProvider.getCustomProgressionState(), needDiff)

    def _parseTooltipEvent(self, event):
        stepId = event.getArgument('stepId')
        modId = event.getArgument('modificationId')
        if stepId is not None:
            stepId = int(stepId)
        if modId is not None:
            modId = int(modId)
        return (stepId, modId)

    def __onViewRendered(self):
        self.onViewRendered()

    def __onMainStepSelectClick(self, args):
        self._selectionProvider.selectMainStep(int(args['stepID']))
        self.__updateSelection()

    def __onMultiStepSelectClick(self, args):
        stepID, modificationID = int(args['stepID']), int(args['modificationID'])
        self._selectionProvider.selectMultiStep(stepID, modificationID)
        self.__updateSelection(needDiff=stepID in self._selectionProvider.getSelectedMultiSteps())

    def __fillChildrenArray(self, childrenArray, childrenIds):
        childrenArray.clear()
        for childID in childrenIds:
            childrenArray.addNumber(childID)

        childrenArray.invalidate()

    def __fillGridModel(self, grid, postProgression):
        mainSteps, multiSteps = grid.getMainSteps(), grid.getMultiSteps()
        mainSelection = self._selectionProvider.getSelectedMainSteps()
        multiSelection = self._selectionProvider.getSelectedMultiSteps()
        mainStepsIdx = multiStepsIdx = 0
        mainSelectedIdx = -1
        for step in postProgression.iterOrderedSteps():
            if step.action.isMultiAction():
                multiStep = MultiStepModel() if multiStepsIdx >= len(multiSteps) else multiSteps[multiStepsIdx]
                with multiStep.transaction() as model:
                    self._fillMultiStepModel(model, step, multiSelection.get(step.stepID))
                if multiStepsIdx >= len(multiSteps):
                    multiSteps.addViewModel(multiStep)
                multiStepsIdx += 1
            singleStep = SingleStepModel() if mainStepsIdx >= len(mainSteps) else mainSteps[mainStepsIdx]
            with singleStep.transaction() as model:
                self._fillSingleStepModel(model, step)
            if mainStepsIdx >= len(mainSteps):
                mainSteps.addViewModel(singleStep)
            mainSelectedIdx = mainStepsIdx if step.stepID in mainSelection else mainSelectedIdx
            mainStepsIdx += 1

        mainSteps.invalidate()
        multiSteps.invalidate()
        grid.setMainSelectedIdx(mainSelectedIdx)

    def __fillModificationsArray(self, modsArray, modifications):
        for idx, modification in enumerate(modifications):
            modificationModel = ModificationModel() if idx >= len(modsArray) else modsArray[idx]
            with modificationModel.transaction() as model:
                self._fillModification(model, modification)
            if idx >= len(modsArray):
                modsArray.addViewModel(model)

        modsArray.invalidate()

    def __fillRestrictionsModel(self, restrictionsModel, restrictions):
        if restrictions is None:
            return
        else:
            allowedLevels = restrictionsModel.getAllowedLevels()
            allowedLevels.clear()
            minLvl, maxLvl = restrictions.getLevelRange()
            for level in xrange(minLvl, maxLvl + 1):
                allowedLevels.addNumber(level)

            allowedLevels.invalidate()
            return

    def __updateSelection(self, needDiff=False):
        postProgression = self._vehicle.postProgression
        with self.viewModel.transaction() as model:
            self.__fillGridModel(model.grid, postProgression)
            self._fillPersistentBonuses(model.persistentBonuses, postProgression, postProgression.getCompletion())
            self._fillControlsModel(model, postProgression)
        self._notifyCustomState(needDiff=needDiff)
