# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/container_vews/quick_training/components/learning_results_component.py
import typing
from gui.impl.lobby.container_views.base.components import ComponentBase
if typing.TYPE_CHECKING:
    from gui.impl.gen.view_models.views.lobby.crew.quick_training.quick_training_view_model import QuickTrainingViewModel
    from gui.impl.gen.view_models.views.lobby.crew.quick_training.learning_results_component_model import LearningResultsComponentModel

class LearningResultsComponent(ComponentBase):

    def _getViewModel(self, vm):
        return vm.learningResults

    def _getEvents(self):
        return super(LearningResultsComponent, self)._getEvents() + ((self.viewModel.learn, self.events.onLearn), (self.viewModel.cancel, self.events.onCancel))

    def _fillViewModel(self, vm):
        freeXP = self.context.getAcquiringFreeXpValue()
        personalXP, commonXP = self.context.selection.getAcquiringBooksXpValues()
        vm.setPersonalXpAmount(personalXP + freeXP)
        vm.setCrewXpAmount(commonXP)
