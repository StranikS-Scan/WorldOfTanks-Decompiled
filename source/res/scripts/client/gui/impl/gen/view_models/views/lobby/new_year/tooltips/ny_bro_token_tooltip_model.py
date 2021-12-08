# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/tooltips/ny_bro_token_tooltip_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel

class NyBroTokenTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(NyBroTokenTooltipModel, self).__init__(properties=properties, commands=commands)

    def getCurrentCount(self):
        return self._getNumber(0)

    def setCurrentCount(self, value):
        self._setNumber(0, value)

    def getTotalCount(self):
        return self._getNumber(1)

    def setTotalCount(self, value):
        self._setNumber(1, value)

    def getRebootTimer(self):
        return self._getNumber(2)

    def setRebootTimer(self, value):
        self._setNumber(2, value)

    def getAmountRequired(self):
        return self._getArray(3)

    def setAmountRequired(self, value):
        self._setArray(3, value)

    def _initialize(self):
        super(NyBroTokenTooltipModel, self)._initialize()
        self._addNumberProperty('currentCount', 0)
        self._addNumberProperty('totalCount', 0)
        self._addNumberProperty('rebootTimer', 0)
        self._addArrayProperty('amountRequired', Array())
