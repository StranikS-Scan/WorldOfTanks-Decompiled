# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/windows/window_model.py
from frameworks.wulf.gui_constants import ResourceValue
from frameworks.wulf import ViewModel

class WindowModel(ViewModel):
    __slots__ = ('onClosed', 'onMinimazed')

    def getX(self):
        return self._getNumber(0)

    def setX(self, value):
        self._setNumber(0, value)

    def getY(self):
        return self._getNumber(1)

    def setY(self, value):
        self._setNumber(1, value)

    def getHeight(self):
        return self._getNumber(2)

    def setHeight(self, value):
        self._setNumber(2, value)

    def getWidth(self):
        return self._getNumber(3)

    def setWidth(self, value):
        self._setNumber(3, value)

    def getTitle(self):
        return self._getResource(4)

    def setTitle(self, value):
        self._setResource(4, value)

    def getCanMinimize(self):
        return self._getBool(5)

    def setCanMinimize(self, value):
        self._setBool(5, value)

    def getContent(self):
        return self._getView(6)

    def setContent(self, value):
        self._setView(6, value)

    def _initialize(self):
        self._addNumberProperty('x', 10)
        self._addNumberProperty('y', 10)
        self._addNumberProperty('height', 10)
        self._addNumberProperty('width', 10)
        self._addResourceProperty('title', ResourceValue.DEFAULT)
        self._addBoolProperty('canMinimize', False)
        self._addViewProperty('content')
        self.onClosed = self._addCommand('onClosed')
        self.onMinimazed = self._addCommand('onMinimazed')
