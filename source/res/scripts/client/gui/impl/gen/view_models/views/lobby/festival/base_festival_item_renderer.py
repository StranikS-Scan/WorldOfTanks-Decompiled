# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/festival/base_festival_item_renderer.py
from frameworks.wulf import ViewModel

class BaseFestivalItemRenderer(ViewModel):
    __slots__ = ()

    def getId(self):
        return self._getNumber(0)

    def setId(self, value):
        self._setNumber(0, value)

    def getResId(self):
        return self._getString(1)

    def setResId(self, value):
        self._setString(1, value)

    def getType(self):
        return self._getString(2)

    def setType(self, value):
        self._setString(2, value)

    def _initialize(self):
        super(BaseFestivalItemRenderer, self)._initialize()
        self._addNumberProperty('id', 0)
        self._addStringProperty('resId', '')
        self._addStringProperty('type', '')
