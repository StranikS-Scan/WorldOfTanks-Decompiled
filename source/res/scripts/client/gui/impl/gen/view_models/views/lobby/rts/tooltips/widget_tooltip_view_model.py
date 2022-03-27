# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/rts/tooltips/widget_tooltip_view_model.py
from frameworks.wulf import ViewModel

class WidgetTooltipViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(WidgetTooltipViewModel, self).__init__(properties=properties, commands=commands)

    def getTimeToActive(self):
        return self._getNumber(0)

    def setTimeToActive(self, value):
        self._setNumber(0, value)

    def getTimeToEnd(self):
        return self._getNumber(1)

    def setTimeToEnd(self, value):
        self._setNumber(1, value)

    def getCurrent(self):
        return self._getNumber(2)

    def setCurrent(self, value):
        self._setNumber(2, value)

    def getTotal(self):
        return self._getNumber(3)

    def setTotal(self, value):
        self._setNumber(3, value)

    def _initialize(self):
        super(WidgetTooltipViewModel, self)._initialize()
        self._addNumberProperty('timeToActive', 0)
        self._addNumberProperty('timeToEnd', 0)
        self._addNumberProperty('current', 0)
        self._addNumberProperty('total', 0)
