# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/windows/pop_over_window_model.py
from gui.impl.gen.view_models.windows.window_model import WindowModel

class PopOverWindowModel(WindowModel):
    __slots__ = ()

    def getBoundX(self):
        return self._getNumber(4)

    def setBoundX(self, value):
        self._setNumber(4, value)

    def getBoundY(self):
        return self._getNumber(5)

    def setBoundY(self, value):
        self._setNumber(5, value)

    def getBoundWidth(self):
        return self._getNumber(6)

    def setBoundWidth(self, value):
        self._setNumber(6, value)

    def getBoundHeight(self):
        return self._getNumber(7)

    def setBoundHeight(self, value):
        self._setNumber(7, value)

    def getDirectionType(self):
        return self._getNumber(8)

    def setDirectionType(self, value):
        self._setNumber(8, value)

    def getIsCloseBtnVisible(self):
        return self._getBool(9)

    def setIsCloseBtnVisible(self, value):
        self._setBool(9, value)

    def _initialize(self):
        super(PopOverWindowModel, self)._initialize()
        self._addNumberProperty('boundX', 0)
        self._addNumberProperty('boundY', 0)
        self._addNumberProperty('boundWidth', 0)
        self._addNumberProperty('boundHeight', 0)
        self._addNumberProperty('directionType', 0)
        self._addBoolProperty('isCloseBtnVisible', True)
