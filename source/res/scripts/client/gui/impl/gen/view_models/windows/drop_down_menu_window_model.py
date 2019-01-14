# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/windows/drop_down_menu_window_model.py
from frameworks.wulf import ViewModel
from frameworks.wulf import View

class DropDownMenuWindowModel(ViewModel):
    __slots__ = ()

    def getContent(self):
        return self._getView(0)

    def setContent(self, value):
        self._setView(0, value)

    def getX(self):
        return self._getReal(1)

    def setX(self, value):
        self._setReal(1, value)

    def getY(self):
        return self._getReal(2)

    def setY(self, value):
        self._setReal(2, value)

    def getTargetWidth(self):
        return self._getReal(3)

    def setTargetWidth(self, value):
        self._setReal(3, value)

    def getTargetHeight(self):
        return self._getReal(4)

    def setTargetHeight(self, value):
        self._setReal(4, value)

    def _initialize(self):
        super(DropDownMenuWindowModel, self)._initialize()
        self._addViewProperty('content')
        self._addRealProperty('x', 0.0)
        self._addRealProperty('y', 0.0)
        self._addRealProperty('targetWidth', 0.0)
        self._addRealProperty('targetHeight', 0.0)
