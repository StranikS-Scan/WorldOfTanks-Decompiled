# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/collection/item_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class ItemState(Enum):
    NEW = 'new'
    RECEIVED = 'received'
    UNRECEIVED = 'unreceived'


class ItemModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(ItemModel, self).__init__(properties=properties, commands=commands)

    def getItemId(self):
        return self._getNumber(0)

    def setItemId(self, value):
        self._setNumber(0, value)

    def getState(self):
        return ItemState(self._getString(1))

    def setState(self, value):
        self._setString(1, value.value)

    def getReceivedImagePath(self):
        return self._getString(2)

    def setReceivedImagePath(self, value):
        self._setString(2, value)

    def getUnreceivedImagePath(self):
        return self._getString(3)

    def setUnreceivedImagePath(self, value):
        self._setString(3, value)

    def _initialize(self):
        super(ItemModel, self)._initialize()
        self._addNumberProperty('itemId', 0)
        self._addStringProperty('state')
        self._addStringProperty('receivedImagePath', '')
        self._addStringProperty('unreceivedImagePath', '')
