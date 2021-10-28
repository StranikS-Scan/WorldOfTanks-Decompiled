# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/halloween/tooltips/shop_vehicle_tooltip_model.py
from frameworks.wulf import ViewModel

class ShopVehicleTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(ShopVehicleTooltipModel, self).__init__(properties=properties, commands=commands)

    def getId(self):
        return self._getNumber(0)

    def setId(self, value):
        self._setNumber(0, value)

    def getFooter(self):
        return self._getString(1)

    def setFooter(self, value):
        self._setString(1, value)

    def getVehicleName(self):
        return self._getString(2)

    def setVehicleName(self, value):
        self._setString(2, value)

    def getVehicleIcon(self):
        return self._getString(3)

    def setVehicleIcon(self, value):
        self._setString(3, value)

    def _initialize(self):
        super(ShopVehicleTooltipModel, self)._initialize()
        self._addNumberProperty('id', 0)
        self._addStringProperty('footer', '')
        self._addStringProperty('vehicleName', '')
        self._addStringProperty('vehicleIcon', '')
