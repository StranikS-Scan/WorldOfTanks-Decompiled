# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/container_vews/quick_training/components/mentoring_license_component.py
import typing
from gui.impl.gen import R
from gui.impl.lobby.container_views.base.components import ComponentBase
from gui.impl.lobby.crew.utils import getMetoringLicensesAmount
from gui.impl.lobby.crew.tooltips.mentoring_license_tooltip import MentoringLicenseTooltip
if typing.TYPE_CHECKING:
    from gui.impl.gen.view_models.views.lobby.crew.quick_training.quick_training_view_model import QuickTrainingViewModel
    from gui.impl.gen.view_models.views.lobby.crew.quick_training.mentoring_license_component_model import MentoringLicenseComponentModel

class MentoringLicenseComponent(ComponentBase):

    def _getViewModel(self, vm):
        return vm.mentoringLicense

    def _getEvents(self):
        return super(MentoringLicenseComponent, self)._getEvents() + ((self.viewModel.openMentoring, self.events.onMentoringClick),)

    def createToolTipContent(self, event, contentID):
        return MentoringLicenseTooltip(getMetoringLicensesAmount()) if contentID == R.views.lobby.crew.tooltips.MentoringLicenseTooltip() else None

    def _fillViewModel(self, vm):
        amount = getMetoringLicensesAmount()
        vm.setAmount(amount)
        vm.setIsEnabled(amount > 0 and not self.context.isAllCrewMaxTrained)
        vm.setIsVisible(self.context.isMentoringLicenseEnabled)
