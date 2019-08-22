# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/battle_royale/tech_parameters_cmp_view_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.ui_kit.list_model import ListModel

class TechParametersCmpViewModel(ViewModel):
    __slots__ = ()

    @property
    def vehicleGoodSpec(self):
        return self._getViewModel(0)

    @property
    def vehicleBadSpec(self):
        return self._getViewModel(1)

    def _initialize(self):
        super(TechParametersCmpViewModel, self)._initialize()
        self._addViewModelProperty('vehicleGoodSpec', ListModel())
        self._addViewModelProperty('vehicleBadSpec', ListModel())
