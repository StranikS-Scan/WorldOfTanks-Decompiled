# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: tech_tree_trade_in/scripts/client/tech_tree_trade_in/gui/impl/gen/view_models/views/lobby/branch_info_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from tech_tree_trade_in.gui.impl.gen.view_models.views.lobby.vehicle_detail_model import VehicleDetailModel

class BranchInfoViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(BranchInfoViewModel, self).__init__(properties=properties, commands=commands)

    def getNation(self):
        return self._getString(0)

    def setNation(self, value):
        self._setString(0, value)

    def getVehiclesList(self):
        return self._getArray(1)

    def setVehiclesList(self, value):
        self._setArray(1, value)

    @staticmethod
    def getVehiclesListType():
        return VehicleDetailModel

    def _initialize(self):
        super(BranchInfoViewModel, self)._initialize()
        self._addStringProperty('nation', '')
        self._addArrayProperty('vehiclesList', Array())
