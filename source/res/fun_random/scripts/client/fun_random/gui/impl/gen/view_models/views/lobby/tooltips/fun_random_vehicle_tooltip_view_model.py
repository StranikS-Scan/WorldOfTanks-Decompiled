# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/impl/gen/view_models/views/lobby/tooltips/fun_random_vehicle_tooltip_view_model.py
from enum import Enum
from frameworks.wulf import ViewModel
from fun_random.gui.impl.gen.view_models.views.lobby.common.fun_random_strengths_weaknesses import FunRandomStrengthsWeaknesses

class FunRandomVehicleStatus(Enum):
    READY = 'ready'
    NOT_READY = 'not_ready'
    IN_BATTLE = 'in_battle'


class FunRandomVehicleTooltipViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=5, commands=0):
        super(FunRandomVehicleTooltipViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def parameters(self):
        return self._getViewModel(0)

    @staticmethod
    def getParametersType():
        return FunRandomStrengthsWeaknesses

    def getVehicleName(self):
        return self._getString(1)

    def setVehicleName(self, value):
        self._setString(1, value)

    def getNationName(self):
        return self._getString(2)

    def setNationName(self, value):
        self._setString(2, value)

    def getDescription(self):
        return self._getString(3)

    def setDescription(self, value):
        self._setString(3, value)

    def getStatus(self):
        return FunRandomVehicleStatus(self._getString(4))

    def setStatus(self, value):
        self._setString(4, value.value)

    def _initialize(self):
        super(FunRandomVehicleTooltipViewModel, self)._initialize()
        self._addViewModelProperty('parameters', FunRandomStrengthsWeaknesses())
        self._addStringProperty('vehicleName', '')
        self._addStringProperty('nationName', '')
        self._addStringProperty('description', '')
        self._addStringProperty('status')
