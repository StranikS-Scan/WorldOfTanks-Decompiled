# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/veh_post_progression/tooltip/post_progression_level_tooltip_view.py
import typing
from frameworks.wulf import ViewSettings
from gui.Scaleform.daapi.view.lobby.veh_post_progression.veh_post_progression_vehicle import g_postProgressionVehicle
from gui.impl.gen import R
from gui.impl.gen.view_models.common.bonus_model import BonusModel
from gui.impl.gen.view_models.common.bonus_value_model import BonusValueModel
from gui.impl.gen.view_models.views.lobby.post_progression.tooltip.post_progression_level_tooltip_view_model import PostProgressionLevelTooltipViewModel, ModificationType
from gui.impl.pub import ViewImpl
from uilogging.veh_post_progression.constants import LogGroups
from uilogging.veh_post_progression.loggers import VehPostProgressionModificationTooltipLogger
if typing.TYPE_CHECKING:
    from frameworks.wulf import Array
    from gui.veh_post_porgression.models.modifications import SimpleModItem
    from gui.veh_post_porgression.models.progression_step import PostProgressionStepItem

class PostProgressionLevelTooltipView(ViewImpl):
    __uiLogger = VehPostProgressionModificationTooltipLogger(LogGroups.MODIFICATION_LEVEL)
    __slots__ = ()

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.veh_post_progression.tooltip.PostProgressionLevelTooltipView())
        settings.model = PostProgressionLevelTooltipViewModel()
        settings.args = args
        settings.kwargs = kwargs
        super(PostProgressionLevelTooltipView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(PostProgressionLevelTooltipView, self).getViewModel()

    def _onLoading(self, step, *args, **kwargs):
        super(PostProgressionLevelTooltipView, self)._onLoading(*args, **kwargs)
        if not g_postProgressionVehicle.isPresent():
            return
        modification = step.action
        with self.viewModel.transaction() as model:
            model.setLevel(step.getLevel())
            model.setIsUnlocked(step.isReceived())
            model.setNameRes(modification.getLocNameRes()())
            model.setType(self.__getModificationType(step))
            self.__fillModifiers(model.modifier.getItems(), modification)

    def _onLoaded(self, *args, **kwargs):
        super(PostProgressionLevelTooltipView, self)._onLoaded(*args, **kwargs)
        self.__uiLogger.onTooltipOpened()

    def _finalize(self):
        super(PostProgressionLevelTooltipView, self)._finalize()
        self.__uiLogger.onTooltipClosed()

    def __fillModifiers(self, modifiers, modification):
        modifiers.clear()
        for kpi in modification.getKpi(g_postProgressionVehicle.defaultItem):
            value = BonusValueModel()
            value.setValue(kpi.value)
            value.setValueKey(kpi.name)
            value.setValueType(kpi.type)
            bonusModel = BonusModel()
            bonusModel.setLocaleName(kpi.name)
            bonusModel.getValues().addViewModel(value)
            modifiers.addViewModel(bonusModel)

        modifiers.invalidate()

    def __getModificationType(self, step):
        postProgression = g_postProgressionVehicle.defaultItem.postProgression
        return ModificationType.PAIRMODIFICATION if any((postProgression.getStep(stepId).action.isMultiAction() for stepId in step.getNextStepIDs())) else ModificationType.FEATURE
