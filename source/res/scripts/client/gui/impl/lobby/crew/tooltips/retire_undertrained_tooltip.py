# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/tooltips/retire_undertrained_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.pub import ViewImpl
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.crew.tooltips.retire_undertrained_tooltip_view_model import RetireUndertrainedTooltipViewModel

class RetireUndertrainedTooltip(ViewImpl):

    def __init__(self, hasJunkTankmen=False):
        settings = ViewSettings(R.views.lobby.crew.tooltips.RetireUndertrainedTooltip())
        settings.model = RetireUndertrainedTooltipViewModel()
        self._hasJunkTankmen = hasJunkTankmen
        super(RetireUndertrainedTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(RetireUndertrainedTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(RetireUndertrainedTooltip, self)._onLoading()
        with self.viewModel.transaction() as vm:
            vm.setHasUndertrainedCrewMembers(self._hasJunkTankmen)
