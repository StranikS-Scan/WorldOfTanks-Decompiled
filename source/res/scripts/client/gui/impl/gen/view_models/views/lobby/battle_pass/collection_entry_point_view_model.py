# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_pass/collection_entry_point_view_model.py
from frameworks.wulf import ViewModel

class CollectionEntryPointViewModel(ViewModel):
    __slots__ = ('openCollection',)

    def __init__(self, properties=5, commands=1):
        super(CollectionEntryPointViewModel, self).__init__(properties=properties, commands=commands)

    def getCollectionItemCount(self):
        return self._getNumber(0)

    def setCollectionItemCount(self, value):
        self._setNumber(0, value)

    def getNewCollectionItemCount(self):
        return self._getNumber(1)

    def setNewCollectionItemCount(self, value):
        self._setNumber(1, value)

    def getMaxCollectionItemCount(self):
        return self._getNumber(2)

    def setMaxCollectionItemCount(self, value):
        self._setNumber(2, value)

    def getIsFirstEnter(self):
        return self._getBool(3)

    def setIsFirstEnter(self, value):
        self._setBool(3, value)

    def getIsCollectionsEnabled(self):
        return self._getBool(4)

    def setIsCollectionsEnabled(self, value):
        self._setBool(4, value)

    def _initialize(self):
        super(CollectionEntryPointViewModel, self)._initialize()
        self._addNumberProperty('collectionItemCount', 0)
        self._addNumberProperty('newCollectionItemCount', 0)
        self._addNumberProperty('maxCollectionItemCount', 0)
        self._addBoolProperty('isFirstEnter', False)
        self._addBoolProperty('isCollectionsEnabled', False)
        self.openCollection = self._addCommand('openCollection')
