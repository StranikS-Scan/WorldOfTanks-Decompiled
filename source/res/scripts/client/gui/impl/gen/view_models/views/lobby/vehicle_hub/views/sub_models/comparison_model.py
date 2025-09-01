# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/vehicle_hub/views/sub_models/comparison_model.py
from frameworks.wulf import ViewModel

class ComparisonModel(ViewModel):
    __slots__ = ('onAddToComparison',)
    ENABLED = 'enabled'
    DISABLED_FULL_BASKET = 'disabledFullBasket'
    DISABLED_ON_SERVER = 'disabledOnServer'
    CAN_NOT_COMPARE = 'canNotCompare'

    def __init__(self, properties=1, commands=1):
        super(ComparisonModel, self).__init__(properties=properties, commands=commands)

    def getStatus(self):
        return self._getString(0)

    def setStatus(self, value):
        self._setString(0, value)

    def _initialize(self):
        super(ComparisonModel, self)._initialize()
        self._addStringProperty('status', '')
        self.onAddToComparison = self._addCommand('onAddToComparison')
