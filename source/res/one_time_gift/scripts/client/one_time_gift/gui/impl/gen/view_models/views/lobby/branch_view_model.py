# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: one_time_gift/scripts/client/one_time_gift/gui/impl/gen/view_models/views/lobby/branch_view_model.py
from frameworks.wulf import Array, ViewModel
from one_time_gift.gui.impl.gen.view_models.views.lobby.branch_vehicle_info_model import BranchVehicleInfoModel

class BranchViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(BranchViewModel, self).__init__(properties=properties, commands=commands)

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

    def getNumVehiclesToCredit(self):
        return self._getNumber(2)

    def setNumVehiclesToCredit(self, value):
        self._setNumber(2, value)

    def _initialize(self):
        super(BranchViewModel, self)._initialize()
        self._addNumberProperty('id', 0)
        self._addArrayProperty('vehiclesList', Array())
        self._addNumberProperty('numVehiclesToCredit', 0)
