# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/gen/view_models/views/lobby/order_info_view_model.py
from frameworks.wulf import ViewModel

class OrderInfoViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(OrderInfoViewModel, self).__init__(properties=properties, commands=commands)

    def getFrontName(self):
        return self._getString(0)

    def setFrontName(self, value):
        self._setString(0, value)

    def _initialize(self):
        super(OrderInfoViewModel, self)._initialize()
        self._addStringProperty('frontName', '')
