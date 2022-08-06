# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/veh_post_progression/tooltips/level_tooltip_view.py
import typing
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.common.bonus_model import BonusModel
from gui.impl.gen.view_models.common.bonus_value_model import BonusValueModel
from gui.impl.gen.view_models.views.lobby.post_progression.tooltip.post_progression_level_tooltip_view_model import PostProgressionLevelTooltipViewModel, ModificationType
from gui.impl.pub import ViewImpl
if typing.TYPE_CHECKING:
    from frameworks.wulf import Array
    from gui.shared.gui_items.Vehicle import Vehicle
    from gui.veh_post_progression.models.modifications import SimpleModItem
    from gui.veh_post_progression.models.progression import PostProgressionItem
    from gui.veh_post_progression.models.progression_step import PostProgressionStepItem

class BaseProgressionLevelTooltipView(ViewImpl):
    __slots__ = ()

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.veh_post_progression.tooltip.PostProgressionLevelTooltipView())
        settings.model = PostProgressionLevelTooltipViewModel()
        settings.args = args
        settings.kwargs = kwargs
        super(BaseProgressionLevelTooltipView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(BaseProgressionLevelTooltipView, self).getViewModel()

    def _onLoading(self, vehicle, stepID, *args, **kwargs):
        super(BaseProgressionLevelTooltipView, self)._onLoading(*args, **kwargs)
        step = vehicle.postProgression.getStep(stepID)
        modification = step.action
        with self.viewModel.transaction() as model:
            model.setLevel(step.getLevel())
            model.setIsUnlocked(self._getIsUnlocked(step))
            model.setNameRes(modification.getLocNameRes()())
            model.setType(self._getModificationType(vehicle.postProgression, step))
            self.__fillModifiers(vehicle, model.modifier.getItems(), modification)

    def _getIsUnlocked(self, step):
        return True

    def _getModificationType(self, postProgression, step):
        return ModificationType.NONE

    def __fillModifiers(self, vehicle, modifiers, modification):
        modifiers.clear()
        for kpi in modification.getKpi(vehicle):
            value = BonusValueModel()
            value.setValue(kpi.value)
            value.setValueKey(kpi.name)
            value.setValueType(kpi.type)
            bonusModel = BonusModel()
            bonusModel.setLocaleName(kpi.name)
            bonusModel.getValues().addViewModel(value)
            modifiers.addViewModel(bonusModel)

        modifiers.invalidate()


class CmpProgressionLevelTooltipView(BaseProgressionLevelTooltipView):
    __slots__ = ()

    def _getModificationType(self, postProgression, step):
        return ModificationType.PAIRMODIFICATION if any((postProgression.getStep(stepId).action.isMultiAction() for stepId in step.getNextStepIDs())) else ModificationType.FEATURE


class CfgProgressionLevelTooltipView(CmpProgressionLevelTooltipView):
    __slots__ = ()

    @property
    def viewModel(self):
        return super(CfgProgressionLevelTooltipView, self).getViewModel()

    def _getIsUnlocked(self, step):
        return step.isReceived()
