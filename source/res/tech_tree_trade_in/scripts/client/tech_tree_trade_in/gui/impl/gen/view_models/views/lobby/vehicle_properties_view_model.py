# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: tech_tree_trade_in/scripts/client/tech_tree_trade_in/gui/impl/gen/view_models/views/lobby/vehicle_properties_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from tech_tree_trade_in.gui.impl.gen.view_models.views.lobby.property_info_view_model import PropertyInfoViewModel

class VehiclePropertiesViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(VehiclePropertiesViewModel, self).__init__(properties=properties, commands=commands)

    def getVehicleState(self):
        return self._getString(0)

    def setVehicleState(self, value):
        self._setString(0, value)

    def getProperties(self):
        return self._getArray(1)

    def setProperties(self, value):
        self._setArray(1, value)

    @staticmethod
    def getPropertiesType():
        return PropertyInfoViewModel

    def _initialize(self):
        super(VehiclePropertiesViewModel, self)._initialize()
        self._addStringProperty('vehicleState', '')
        self._addArrayProperty('properties', Array())
