# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/vehicle_compare/modifications_panel.py
import typing
from frameworks.wulf import ViewFlags, ViewSettings
from gui.Scaleform.daapi.view.lobby.vehicle_compare import cmp_helpers
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.post_progression.base_step_model import ActionType
from gui.impl.gen.view_models.views.lobby.vehicle_compare.compare_modifications_panel_view_model import CompareModificationsPanelViewModel
from gui.impl.gen.view_models.views.lobby.vehicle_compare.compare_modification_model import CompareModificationModel
from gui.impl.gen.view_models.views.lobby.vehicle_compare.compare_step_model import CompareStepModel
from gui.impl.lobby.veh_post_progression.tooltips.level_tooltip_view import BaseProgressionLevelTooltipView
from gui.impl.lobby.veh_post_progression.tooltips.pair_modification_tooltip_view import CmpPanelPairModificationTooltipView
from gui.impl.pub import ViewImpl
from gui.shared import event_dispatcher as shared_events
from gui.veh_post_progression.models.modifications import PostProgressionActionTooltip
from gui.veh_post_progression.models.progression import PostProgressionCompletion
if typing.TYPE_CHECKING:
    from frameworks.wulf import Array, ViewEvent
    from gui.veh_post_progression.models.progression import PostProgressionItem
    from gui.veh_post_progression.models.progression_step import PostProgressionStepItem
_ACTION_TOOLTIP_MAP = {PostProgressionActionTooltip.SIMPLEMOD: R.invalid(),
 PostProgressionActionTooltip.MULTIMOD: R.views.lobby.veh_post_progression.tooltip.PairModificationTooltipView(),
 PostProgressionActionTooltip.FEATURE: R.invalid(),
 PostProgressionActionTooltip.ROLESLOT: R.invalid()}

class CompareModificationsPanelView(ViewImpl):
    __slots__ = ('__vehItem',)

    def __init__(self, layoutID=R.views.lobby.vehicle_compare.CompareModificationsPanelView()):
        settings = ViewSettings(layoutID, flags=ViewFlags.VIEW, model=CompareModificationsPanelViewModel())
        super(CompareModificationsPanelView, self).__init__(settings)
        self.__vehItem = None
        return

    @property
    def viewModel(self):
        return super(CompareModificationsPanelView, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        stepId, modId = self.__parseTooltipEvent(event)
        if contentID == R.views.lobby.veh_post_progression.tooltip.PairModificationTooltipView() and stepId is not None and modId is not None:
            return CmpPanelPairModificationTooltipView(self.__vehItem.getItem(), stepId, modId)
        else:
            return BaseProgressionLevelTooltipView(self.__vehItem.getItem(), stepId) if contentID == R.views.lobby.veh_post_progression.tooltip.PostProgressionLevelTooltipView() and stepId is not None else super(CompareModificationsPanelView, self).createToolTipContent(event, contentID)

    def update(self):
        postProgression = self.__vehItem.getItem().postProgression
        suitableSteps = [ step for step in postProgression.iterOrderedSteps() if not step.isRestricted() and not step.action.isMultiAction() and not step.action.isFeatureAction() ]
        with self.viewModel.transaction() as model:
            model.setIsEmpty(postProgression.getCompletion() is PostProgressionCompletion.EMPTY)
            self.__updateSteps(model.getSteps(), suitableSteps, postProgression)

    def _onLoading(self, *args, **kwargs):
        super(CompareModificationsPanelView, self)._onLoading(*args, **kwargs)
        self.__vehItem = cmp_helpers.getCmpConfiguratorMainView().getCurrentVehicleItem()
        self.update()

    def _initialize(self, *args, **kwargs):
        super(CompareModificationsPanelView, self)._initialize(*args, **kwargs)
        self.__addListeners()

    def _finalize(self):
        self.__removeListeners()
        self.__vehItem = None
        super(CompareModificationsPanelView, self)._finalize()
        return

    def __addListeners(self):
        self.viewModel.onClearModifications += self.__onClearModifications
        self.viewModel.onConfigureModifications += self.__onConfigureModifications
        self.viewModel.onClose += self.__onClose

    def __removeListeners(self):
        self.viewModel.onClearModifications -= self.__onClearModifications
        self.viewModel.onConfigureModifications -= self.__onConfigureModifications
        self.viewModel.onClose -= self.__onClose

    def __onClose(self):
        cmp_helpers.getCmpConfiguratorMainView().closeView()

    def __onClearModifications(self):
        cmp_helpers.getCmpConfiguratorMainView().removePostProgression()

    def __onConfigureModifications(self):
        shared_events.showVehPostProgressionCmpView(self.__vehItem.getItem().intCD)

    def __parseTooltipEvent(self, event):
        stepId = event.getArgument('stepId')
        modId = event.getArgument('modificationId')
        if stepId is not None:
            stepId = int(stepId)
        if modId is not None:
            modId = int(modId)
        return (stepId, modId)

    def __updateSteps(self, stepsArray, suitableSteps, postProgression):
        stepsArray.clear()
        for step in suitableSteps:
            stepModel = CompareStepModel()
            stepModel.setId(step.stepID)
            stepModel.setActionType(ActionType.MODIFICATION)
            stepModel.setIsInstalled(step.isReceived())
            stepModel.setLevel(step.getLevel())
            self.__fillModificationModel(stepModel.modification, step, postProgression)
            stepsArray.addViewModel(stepModel)

        stepsArray.invalidate()

    def __fillModificationModel(self, modificationModel, step, postProgression):
        modificationModel.setId(CompareModificationModel.UNDEFINED)
        childMultiStep, relatedMultiModification = (None, None)
        for stepID in step.getNextStepIDs():
            childMultiStep = postProgression.getStep(stepID)
            if childMultiStep.action.isMultiAction():
                relatedMultiModification = childMultiStep.action.getPurchasedModification()
                break

        if childMultiStep is not None and relatedMultiModification is not None:
            modificationModel.setId(relatedMultiModification.actionID)
            modificationModel.setParentStepId(childMultiStep.stepID)
            modificationModel.setImageResName(relatedMultiModification.getImageName())
            modificationModel.setTitleRes(relatedMultiModification.getLocNameRes()())
            modificationModel.setTooltipContentId(_ACTION_TOOLTIP_MAP[relatedMultiModification.getTooltip()])
        return
