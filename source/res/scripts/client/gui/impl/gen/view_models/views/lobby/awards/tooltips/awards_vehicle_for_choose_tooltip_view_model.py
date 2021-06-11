# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/awards/tooltips/awards_vehicle_for_choose_tooltip_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.vehicle_info_model import VehicleInfoModel

class AwardsVehicleForChooseTooltipViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(AwardsVehicleForChooseTooltipViewModel, self).__init__(properties=properties, commands=commands)

    def getVehiclesList(self):
        return self._getArray(0)

    def setVehiclesList(self, value):
        self._setArray(0, value)

    def _initialize(self):
        super(AwardsVehicleForChooseTooltipViewModel, self)._initialize()
        self._addArrayProperty('vehiclesList', Array())
