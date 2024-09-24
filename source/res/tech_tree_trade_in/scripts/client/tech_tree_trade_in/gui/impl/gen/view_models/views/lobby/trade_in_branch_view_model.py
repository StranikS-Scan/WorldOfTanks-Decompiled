# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: tech_tree_trade_in/scripts/client/tech_tree_trade_in/gui/impl/gen/view_models/views/lobby/trade_in_branch_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from tech_tree_trade_in.gui.impl.gen.view_models.views.lobby.branch_vehicle_info_model import BranchVehicleInfoModel

class TradeInBranchViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(TradeInBranchViewModel, self).__init__(properties=properties, commands=commands)

    def getId(self):
        return self._getNumber(0)

    def setId(self, value):
        self._setNumber(0, value)

    def getVehiclesList(self):
        return self._getArray(1)

    def setVehiclesList(self, value):
        self._setArray(1, value)

    @staticmethod
    def getVehiclesListType():
        return BranchVehicleInfoModel

    def _initialize(self):
        super(TradeInBranchViewModel, self)._initialize()
        self._addNumberProperty('id', 0)
        self._addArrayProperty('vehiclesList', Array())
