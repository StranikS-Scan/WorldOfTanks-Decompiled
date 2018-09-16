# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/windows/context_menu_window_model.py
from frameworks.wulf import ViewModel

class ContextMenuWindowModel(ViewModel):
    __slots__ = ()

    def getX(self):
        return self._getNumber(0)

    def setX(self, value):
        self._setNumber(0, value)

    def getY(self):
        return self._getNumber(1)

    def setY(self, value):
        self._setNumber(1, value)

    def getContent(self):
        return self._getView(2)

    def setContent(self, value):
        self._setView(2, value)

    def _initialize(self):
        super(ContextMenuWindowModel, self)._initialize()
        self._addNumberProperty('x', 10)
        self._addNumberProperty('y', 10)
        self._addViewProperty('content')
