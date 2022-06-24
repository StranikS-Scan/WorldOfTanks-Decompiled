# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/ui_kit/list_model.py
import typing
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
T = typing.TypeVar('T')

class ListModel(ViewModel, typing.Generic[T]):
    __slots__ = ('onSelectionChanged', 'onItemClicked')

    def __init__(self, properties=2, commands=2):
        super(ListModel, self).__init__(properties=properties, commands=commands)

    def getItems(self):
        return self._getArray(0)

    def setItems(self, value):
        self._setArray(0, value)

    @staticmethod
    def getItemsType():
        return T

    def getSelectedIndices(self):
        return self._getArray(1)

    def setSelectedIndices(self, value):
        self._setArray(1, value)

    @staticmethod
    def getSelectedIndicesType():
        return int

    def _initialize(self):
        super(ListModel, self)._initialize()
        self._addArrayProperty('items', Array())
        self._addArrayProperty('selectedIndices', Array())
        self.onSelectionChanged = self._addCommand('onSelectionChanged')
        self.onItemClicked = self._addCommand('onItemClicked')
