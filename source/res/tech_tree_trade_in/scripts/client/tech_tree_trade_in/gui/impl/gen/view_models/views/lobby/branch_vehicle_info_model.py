# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: tech_tree_trade_in/scripts/client/tech_tree_trade_in/gui/impl/gen/view_models/views/lobby/branch_vehicle_info_model.py
from gui.impl.gen.view_models.common.vehicle_info_model import VehicleInfoModel

class BranchVehicleInfoModel(VehicleInfoModel):
    __slots__ = ()

    def __init__(self, properties=12, commands=0):
        super(BranchVehicleInfoModel, self).__init__(properties=properties, commands=commands)

    def getIcon(self):
        return self._getString(7)

    def setIcon(self, value):
        self._setString(7, value)

    def getIconSmall(self):
        return self._getString(8)

    def setIconSmall(self, value):
        self._setString(8, value)

    def getUnlocked(self):
        return self._getBool(9)

    def setUnlocked(self, value):
        self._setBool(9, value)

    def getObtained(self):
        return self._getBool(10)

    def setObtained(self, value):
        self._setBool(10, value)

    def getId(self):
        return self._getNumber(11)

    def setId(self, value):
        self._setNumber(11, value)

    def _initialize(self):
        super(BranchVehicleInfoModel, self)._initialize()
        self._addStringProperty('icon', '')
        self._addStringProperty('iconSmall', '')
        self._addBoolProperty('unlocked', False)
        self._addBoolProperty('obtained', False)
        self._addNumberProperty('id', 0)
