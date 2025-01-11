# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/paragons/tooltips/vehicle_select_tooltip_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.missions.bonuses.icon_bonus_model import IconBonusModel
from gui.impl.gen.view_models.views.lobby.paragons.common.paragons_vehicle_model import ParagonsVehicleModel

class VehicleSelectTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(VehicleSelectTooltipModel, self).__init__(properties=properties, commands=commands)

    @property
    def reward(self):
        return self._getViewModel(0)

    @staticmethod
    def getRewardType():
        return IconBonusModel

    def getIsReceived(self):
        return self._getBool(1)

    def setIsReceived(self, value):
        self._setBool(1, value)

    def getVehicles(self):
        return self._getArray(2)

    def setVehicles(self, value):
        self._setArray(2, value)

    @staticmethod
    def getVehiclesType():
        return ParagonsVehicleModel

    def _initialize(self):
        super(VehicleSelectTooltipModel, self)._initialize()
        self._addViewModelProperty('reward', IconBonusModel())
        self._addBoolProperty('isReceived', False)
        self._addArrayProperty('vehicles', Array())
