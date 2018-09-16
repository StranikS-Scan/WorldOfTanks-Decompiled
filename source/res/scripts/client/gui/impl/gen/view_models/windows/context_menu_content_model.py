# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/windows/context_menu_content_model.py
import typing
from frameworks.wulf import Array
from frameworks.wulf import ViewModel

class ContextMenuContentModel(ViewModel):
    __slots__ = ('onItemClicked',)

    def getContextMenuList(self):
        return self._getArray(0)

    def setContextMenuList(self, value):
        self._setArray(0, value)

    def getItemsCount(self):
        return self._getNumber(1)

    def setItemsCount(self, value):
        self._setNumber(1, value)

    def getSeparatorsCount(self):
        return self._getNumber(2)

    def setSeparatorsCount(self, value):
        self._setNumber(2, value)

    def _initialize(self):
        self._addArrayProperty('contextMenuList', Array())
        self._addNumberProperty('itemsCount', 0)
        self._addNumberProperty('separatorsCount', 0)
        self.onItemClicked = self._addCommand('onItemClicked')
