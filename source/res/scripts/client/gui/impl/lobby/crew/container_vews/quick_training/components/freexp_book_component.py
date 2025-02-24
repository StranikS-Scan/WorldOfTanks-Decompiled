# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/container_vews/quick_training/components/freexp_book_component.py
import typing
from gui.impl.gen import R
from gui.impl.lobby.container_views.base.components import ComponentBase
from gui.impl.lobby.crew.tooltips.experience_stepper_tooltip import ExperienceStepperTooltip
from gui.impl.lobby.crew.tooltips.quick_training_discount_tooltip import QuickTrainingDiscountTooltip
from gui.impl.lobby.crew.utils import jsonArgsConverter
if typing.TYPE_CHECKING:
    from gui.impl.gen.view_models.views.lobby.crew.quick_training.quick_training_view_model import QuickTrainingViewModel
    from gui.impl.gen.view_models.views.lobby.crew.quick_training.freeXp_book_component_model import FreeXpBookComponentModel

class FreeXpBookComponent(ComponentBase):

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.crew.tooltips.QuickTrainingDiscountTooltip():
            return QuickTrainingDiscountTooltip(oldXpExchange=self.context.xpDefaultConversionRate, newXpExchange=self.context.xpDiscountConversionRate)
        return ExperienceStepperTooltip() if contentID == R.views.lobby.crew.tooltips.ExperienceStepperTooltip() else None

    def _getViewModel(self, vm):
        return vm.freeXp

    def _getEvents(self):
        return super(FreeXpBookComponent, self)._getEvents() + ((self.viewModel.mouseEnter, self.events.onFreeXpMouseEnter),
         (self.viewModel.select, self._onSelected),
         (self.viewModel.update, self.events.onFreeXpUpdated),
         (self.viewModel.manualInput, self._onManualInput))

    @jsonArgsConverter(('isSelected',))
    def _onSelected(self, isSelected):
        self.events.onFreeXpSelected(isSelected)

    @jsonArgsConverter(('value',))
    def _onManualInput(self, value):
        self.events.onFreeXpManualInput(value)

    def _fillViewModel(self, vm):
        vm.setCurrentXpValue(self.context.selection.freeXp)
        vm.setMaxXpValue(self.context.maxPossibleXpCount)
        vm.setDiscountSize(self.context.xpConversionDiscount)
        vm.setExchangeRate(self.context.xpDiscountConversionRate)
        isDisabled = not (self.context.canCrewSelectFreeXp and self.context.canCurrentTankmanUseFreeXp)
        vm.setIsDisabled(isDisabled)
        vm.setHasError(isDisabled and self.context.itemsCache.items.stats.freeXP > 0)
