# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/tooltips/tankman_change_preview_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.crew.tooltips.tankman_change_preview_tooltip_model import TankmanChangePreviewTooltipModel
from gui.impl.pub import ViewImpl

class TankmanChangePreviewTooltip(ViewImpl):
    __slots__ = ('__credits', '__retrainingGold', '__specialityGold')

    def __init__(self, credits, retrainingGold, specialityGold):
        settings = ViewSettings(R.views.lobby.crew.tooltips.TankmanChangePreviewTooltip())
        settings.model = TankmanChangePreviewTooltipModel()
        self.__credits = credits
        self.__retrainingGold = retrainingGold
        self.__specialityGold = specialityGold
        super(TankmanChangePreviewTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(TankmanChangePreviewTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        with self.viewModel.transaction() as vm:
            vm.setCredits(self.__credits)
            vm.setRetrainingGold(self.__retrainingGold)
            vm.setSpecialityGold(self.__specialityGold)
