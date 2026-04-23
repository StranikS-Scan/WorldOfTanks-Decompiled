# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/gen/view_models/views/battle/comp7_vehicle_model.py
from gui.impl.gen.view_models.views.lobby.common.vehicle_model import VehicleModel

class Comp7VehicleModel(VehicleModel):
    __slots__ = ()

    def __init__(self, properties=12, commands=0):
        super(Comp7VehicleModel, self).__init__(properties=properties, commands=commands)

    def getRoleSkill(self):
        return self._getString(10)

    def setRoleSkill(self, value):
        self._setString(10, value)

    def getOriginalVehicleCD(self):
        return self._getNumber(11)

    def setOriginalVehicleCD(self, value):
        self._setNumber(11, value)

    def _initialize(self):
        super(Comp7VehicleModel, self)._initialize()
        self._addStringProperty('roleSkill', '')
        self._addNumberProperty('originalVehicleCD', 0)
