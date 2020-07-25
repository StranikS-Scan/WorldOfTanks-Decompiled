# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/common/multiple_items_content_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.common.confirmed_item_model import ConfirmedItemModel

class MultipleItemsContentModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(MultipleItemsContentModel, self).__init__(properties=properties, commands=commands)

    def getConfirmedItems(self):
        return self._getArray(0)

    def setConfirmedItems(self, value):
        self._setArray(0, value)

    def getItemsType(self):
        return self._getString(1)

    def setItemsType(self, value):
        self._setString(1, value)

    def _initialize(self):
        super(MultipleItemsContentModel, self)._initialize()
        self._addArrayProperty('confirmedItems', Array())
        self._addStringProperty('itemsType', '')
