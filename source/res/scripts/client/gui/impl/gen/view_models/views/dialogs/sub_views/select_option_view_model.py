# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/dialogs/sub_views/select_option_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.dialogs.sub_views.select_option_base_item_view_model import SelectOptionBaseItemViewModel

class SelectOptionViewModel(ViewModel):
    __slots__ = ('onClicked',)

    def __init__(self, properties=3, commands=1):
        super(SelectOptionViewModel, self).__init__(properties=properties, commands=commands)

    def getItems(self):
        return self._getArray(0)

    def setItems(self, value):
        self._setArray(0, value)

    def getSelectedIndexes(self):
        return self._getArray(1)

    def setSelectedIndexes(self, value):
        self._setArray(1, value)

    def getMessage(self):
        return self._getString(2)

    def setMessage(self, value):
        self._setString(2, value)

    def _initialize(self):
        super(SelectOptionViewModel, self)._initialize()
        self._addArrayProperty('items', Array())
        self._addArrayProperty('selectedIndexes', Array())
        self._addStringProperty('message', '')
        self.onClicked = self._addCommand('onClicked')
