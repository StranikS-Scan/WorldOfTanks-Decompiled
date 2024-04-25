# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/gen/view_models/views/common/vehicle_model.py
from historical_battles.gui.impl.gen.view_models.views.common.base_vehicle_model import BaseVehicleModel

class VehicleModel(BaseVehicleModel):
    __slots__ = ()

    def __init__(self, properties=7, commands=0):
        super(VehicleModel, self).__init__(properties=properties, commands=commands)

    def getLevel(self):
        return self._getNumber(3)

    def setLevel(self, value):
        self._setNumber(3, value)

    def getIsPremium(self):
        return self._getBool(4)

    def setIsPremium(self, value):
        self._setBool(4, value)

    def getNation(self):
        return self._getString(5)

    def setNation(self, value):
        self._setString(5, value)

    def getIcon(self):
        return self._getString(6)

    def setIcon(self, value):
        self._setString(6, value)

    def _initialize(self):
        super(VehicleModel, self)._initialize()
        self._addNumberProperty('level', 0)
        self._addBoolProperty('isPremium', False)
        self._addStringProperty('nation', '')
        self._addStringProperty('icon', '')
