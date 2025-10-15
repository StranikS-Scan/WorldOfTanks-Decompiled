# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/gui/impl/lobby/tooltips/complexity_tooltip.py
from frameworks.wulf import ViewSettings
from portal.gui.impl.gen.view_models.views.lobby.tooltips.complexity_tooltip_model import ComplexityTooltipModel
from gui.impl.pub import ViewImpl
from gui.impl.gen import R

class ComplexityTooltip(ViewImpl):
    __slots__ = ('_level', '_vehicleLvl', '_isLocked')

    def __init__(self, level, isLocked, vehicleLvl):
        settings = ViewSettings(R.views.portal.lobby.tooltips.ComplexityTooltip())
        settings.model = ComplexityTooltipModel()
        self._level = level
        self._vehicleLvl = vehicleLvl
        self._isLocked = isLocked
        super(ComplexityTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(ComplexityTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(ComplexityTooltip, self)._onLoading(*args, **kwargs)
        self.__updateData()

    def __updateData(self):
        with self.viewModel.transaction() as vm:
            vm.setLevel(self._level)
            vm.setIsLock(self._isLocked)
            vm.setVehicleLevel(self._vehicleLvl)
