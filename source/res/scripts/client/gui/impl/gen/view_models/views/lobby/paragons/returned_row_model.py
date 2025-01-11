# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/paragons/returned_row_model.py
from frameworks.wulf import ViewModel

class ReturnedRowModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=5, commands=0):
        super(ReturnedRowModel, self).__init__(properties=properties, commands=commands)

    def getName(self):
        return self._getString(0)

    def setName(self, value):
        self._setString(0, value)

    def getCount(self):
        return self._getNumber(1)

    def setCount(self, value):
        self._setNumber(1, value)

    def getIcon(self):
        return self._getString(2)

    def setIcon(self, value):
        self._setString(2, value)

    def getOverlayIcon(self):
        return self._getString(3)

    def setOverlayIcon(self, value):
        self._setString(3, value)

    def getIntCD(self):
        return self._getNumber(4)

    def setIntCD(self, value):
        self._setNumber(4, value)

    def _initialize(self):
        super(ReturnedRowModel, self)._initialize()
        self._addStringProperty('name', '')
        self._addNumberProperty('count', 0)
        self._addStringProperty('icon', '')
        self._addStringProperty('overlayIcon', '')
        self._addNumberProperty('intCD', 0)
