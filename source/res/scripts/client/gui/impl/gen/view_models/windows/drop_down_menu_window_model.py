# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/windows/drop_down_menu_window_model.py
from frameworks.wulf import ViewModel

class DropDownMenuWindowModel(ViewModel):
    __slots__ = ()

    def getX(self):
        return self._getNumber(0)

    def setX(self, value):
        self._setNumber(0, value)

    def getY(self):
        return self._getNumber(1)

    def setY(self, value):
        self._setNumber(1, value)

    def getTargetWidth(self):
        return self._getNumber(2)

    def setTargetWidth(self, value):
        self._setNumber(2, value)

    def getTargetHeight(self):
        return self._getNumber(3)

    def setTargetHeight(self, value):
        self._setNumber(3, value)

    def getContent(self):
        return self._getView(4)

    def setContent(self, value):
        self._setView(4, value)

    def _initialize(self):
        super(DropDownMenuWindowModel, self)._initialize()
        self._addNumberProperty('x', 0)
        self._addNumberProperty('y', 0)
        self._addNumberProperty('targetWidth', 0)
        self._addNumberProperty('targetHeight', 0)
        self._addViewProperty('content')
