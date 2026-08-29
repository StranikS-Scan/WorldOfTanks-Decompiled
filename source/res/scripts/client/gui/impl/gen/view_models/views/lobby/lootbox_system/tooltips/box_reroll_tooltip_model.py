# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/lootbox_system/tooltips/box_reroll_tooltip_model.py
from frameworks.wulf import Array, ViewModel

class BoxRerollTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(BoxRerollTooltipModel, self).__init__(properties=properties, commands=commands)

    def getCurrency(self):
        return self._getString(0)

    def setCurrency(self, value):
        self._setString(0, value)

    def getPrices(self):
        return self._getArray(1)

    def setPrices(self, value):
        self._setArray(1, value)

    @staticmethod
    def getPricesType():
        return int

    def getRerollAttempts(self):
        return self._getNumber(2)

    def setRerollAttempts(self, value):
        self._setNumber(2, value)

    def getEventName(self):
        return self._getString(3)

    def setEventName(self, value):
        self._setString(3, value)

    def _initialize(self):
        super(BoxRerollTooltipModel, self)._initialize()
        self._addStringProperty('currency', '')
        self._addArrayProperty('prices', Array())
        self._addNumberProperty('rerollAttempts', 0)
        self._addStringProperty('eventName', '')
