# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: one_time_gift/scripts/client/one_time_gift/gui/impl/gen/view_models/views/lobby/branch_vehicle_info_model.py
from gui.impl.gen.view_models.common.vehicle_info_model import VehicleInfoModel

class BranchVehicleInfoModel(VehicleInfoModel):
    __slots__ = ()

    def __init__(self, properties=22, commands=0):
        super(BranchVehicleInfoModel, self).__init__(properties=properties, commands=commands)

    def getIcon(self):
        return self._getString(17)

    def setIcon(self, value):
        self._setString(17, value)

    def getIconSmall(self):
        return self._getString(18)

    def setIconSmall(self, value):
        self._setString(18, value)

    def getUnlocked(self):
        return self._getBool(19)

    def setUnlocked(self, value):
        self._setBool(19, value)

    def getObtained(self):
        return self._getBool(20)

    def setObtained(self, value):
        self._setBool(20, value)

    def getId(self):
        return self._getNumber(21)

    def setId(self, value):
        self._setNumber(21, value)

    def _initialize(self):
        super(BranchVehicleInfoModel, self)._initialize()
        self._addStringProperty('icon', '')
        self._addStringProperty('iconSmall', '')
        self._addBoolProperty('unlocked', False)
        self._addBoolProperty('obtained', False)
        self._addNumberProperty('id', 0)
