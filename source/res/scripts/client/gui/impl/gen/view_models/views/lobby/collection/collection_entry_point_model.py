# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/collection/collection_entry_point_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class CollectionState(Enum):
    COMPLETED = 'completed'
    DISABLED = 'disabled'
    ACTIVE = 'active'


class CollectionEntryPointModel(ViewModel):
    __slots__ = ('onClick',)

    def __init__(self, properties=4, commands=1):
        super(CollectionEntryPointModel, self).__init__(properties=properties, commands=commands)

    def getState(self):
        return CollectionState(self._getString(0))

    def setState(self, value):
        self._setString(0, value.value)

    def getNewReceivedItems(self):
        return self._getNumber(1)

    def setNewReceivedItems(self, value):
        self._setNumber(1, value)

    def getFinishDateStamp(self):
        return self._getNumber(2)

    def setFinishDateStamp(self, value):
        self._setNumber(2, value)

    def getCollectionName(self):
        return self._getString(3)

    def setCollectionName(self, value):
        self._setString(3, value)

    def _initialize(self):
        super(CollectionEntryPointModel, self)._initialize()
        self._addStringProperty('state')
        self._addNumberProperty('newReceivedItems', 0)
        self._addNumberProperty('finishDateStamp', 0)
        self._addStringProperty('collectionName', '')
        self.onClick = self._addCommand('onClick')
