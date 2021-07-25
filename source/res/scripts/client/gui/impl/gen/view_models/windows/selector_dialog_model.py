# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/windows/selector_dialog_model.py
from frameworks.wulf import Array
from gui.impl.gen import R
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.windows.selector_dialog_item_model import SelectorDialogItemModel

class SelectorDialogModel(ViewModel):
    __slots__ = ('onSelectItem',)

    def __init__(self, properties=2, commands=1):
        super(SelectorDialogModel, self).__init__(properties=properties, commands=commands)

    def getDescription(self):
        return self._getResource(0)

    def setDescription(self, value):
        self._setResource(0, value)

    def getItems(self):
        return self._getArray(1)

    def setItems(self, value):
        self._setArray(1, value)

    def _initialize(self):
        super(SelectorDialogModel, self)._initialize()
        self._addResourceProperty('description', R.invalid())
        self._addArrayProperty('items', Array())
        self.onSelectItem = self._addCommand('onSelectItem')
