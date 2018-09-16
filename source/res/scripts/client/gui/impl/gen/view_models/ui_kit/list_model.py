# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/ui_kit/list_model.py
import typing
from frameworks.wulf import Array
from frameworks.wulf import ViewModel

class ListModel(ViewModel):
    __slots__ = ('onSelectionChanged', 'onItemClicked')

    def getItems(self):
        return self._getArray(0)

    def setItems(self, value):
        self._setArray(0, value)

    def getSelectedIndex(self):
        return self._getNumber(1)

    def setSelectedIndex(self, value):
        self._setNumber(1, value)

    def _initialize(self):
        super(ListModel, self)._initialize()
        self._addArrayProperty('items', Array())
        self._addNumberProperty('selectedIndex', 0)
        self.onSelectionChanged = self._addCommand('onSelectionChanged')
        self.onItemClicked = self._addCommand('onItemClicked')
