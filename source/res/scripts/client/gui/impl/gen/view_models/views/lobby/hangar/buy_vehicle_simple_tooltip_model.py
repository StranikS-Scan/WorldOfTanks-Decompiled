# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/hangar/buy_vehicle_simple_tooltip_model.py
from frameworks.wulf import ViewModel

class BuyVehicleSimpleTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(BuyVehicleSimpleTooltipModel, self).__init__(properties=properties, commands=commands)

    def getTooltipId(self):
        return self._getString(0)

    def setTooltipId(self, value):
        self._setString(0, value)

    def getHeader(self):
        return self._getString(1)

    def setHeader(self, value):
        self._setString(1, value)

    def getBody(self):
        return self._getString(2)

    def setBody(self, value):
        self._setString(2, value)

    def _initialize(self):
        super(BuyVehicleSimpleTooltipModel, self)._initialize()
        self._addStringProperty('tooltipId', '')
        self._addStringProperty('header', '')
        self._addStringProperty('body', '')
