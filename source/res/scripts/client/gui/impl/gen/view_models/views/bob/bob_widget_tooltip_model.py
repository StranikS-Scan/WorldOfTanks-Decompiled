# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/bob/bob_widget_tooltip_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel

class BobWidgetTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(BobWidgetTooltipModel, self).__init__(properties=properties, commands=commands)

    def getPersonalAwardPointsRemaining(self):
        return self._getNumber(0)

    def setPersonalAwardPointsRemaining(self, value):
        self._setNumber(0, value)

    def getBloggersNames(self):
        return self._getArray(1)

    def setBloggersNames(self, value):
        self._setArray(1, value)

    def getBloggersPoints(self):
        return self._getArray(2)

    def setBloggersPoints(self, value):
        self._setArray(2, value)

    def _initialize(self):
        super(BobWidgetTooltipModel, self)._initialize()
        self._addNumberProperty('personalAwardPointsRemaining', 0)
        self._addArrayProperty('bloggersNames', Array())
        self._addArrayProperty('bloggersPoints', Array())
