# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/halloween/shop_vehicle_bonus_model.py
from frameworks.wulf import ViewModel

class ShopVehicleBonusModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(ShopVehicleBonusModel, self).__init__(properties=properties, commands=commands)

    def getIcon(self):
        return self._getString(0)

    def setIcon(self, value):
        self._setString(0, value)

    def getName(self):
        return self._getString(1)

    def setName(self, value):
        self._setString(1, value)

    def getType(self):
        return self._getString(2)

    def setType(self, value):
        self._setString(2, value)

    def getTooltipId(self):
        return self._getString(3)

    def setTooltipId(self, value):
        self._setString(3, value)

    def _initialize(self):
        super(ShopVehicleBonusModel, self)._initialize()
        self._addStringProperty('icon', '')
        self._addStringProperty('name', '')
        self._addStringProperty('type', '')
        self._addStringProperty('tooltipId', '')
