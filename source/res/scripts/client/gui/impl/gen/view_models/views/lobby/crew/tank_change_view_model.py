# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crew/tank_change_view_model.py
from frameworks.wulf import Array
from gui.impl.gen.view_models.views.lobby.crew.common.base_crew_view_model import BaseCrewViewModel
from gui.impl.gen.view_models.views.lobby.crew.tank_change_vehicle_model import TankChangeVehicleModel

class TankChangeViewModel(BaseCrewViewModel):
    __slots__ = ('onVehicleSelected', 'onResetFilters')

    def __init__(self, properties=4, commands=6):
        super(TankChangeViewModel, self).__init__(properties=properties, commands=commands)

    def getNation(self):
        return self._getString(2)

    def setNation(self, value):
        self._setString(2, value)

    def getVehicleList(self):
        return self._getArray(3)

    def setVehicleList(self, value):
        self._setArray(3, value)

    @staticmethod
    def getVehicleListType():
        return TankChangeVehicleModel

    def _initialize(self):
        super(TankChangeViewModel, self)._initialize()
        self._addStringProperty('nation', '')
        self._addArrayProperty('vehicleList', Array())
        self.onVehicleSelected = self._addCommand('onVehicleSelected')
        self.onResetFilters = self._addCommand('onResetFilters')
