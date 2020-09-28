# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/postbattle/widget_model.py
from frameworks.wulf import ViewModel

class WidgetModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(WidgetModel, self).__init__(properties=properties, commands=commands)

    def getType(self):
        return self._getString(0)

    def setType(self, value):
        self._setString(0, value)

    def getQuantity(self):
        return self._getNumber(1)

    def setQuantity(self, value):
        self._setNumber(1, value)

    def getIsDisabled(self):
        return self._getBool(2)

    def setIsDisabled(self, value):
        self._setBool(2, value)

    def _initialize(self):
        super(WidgetModel, self)._initialize()
        self._addStringProperty('type', '')
        self._addNumberProperty('quantity', 1)
        self._addBoolProperty('isDisabled', False)
