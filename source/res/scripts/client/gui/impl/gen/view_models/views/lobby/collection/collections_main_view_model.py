# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/collection/collections_main_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.collection.collection_model import CollectionModel

class CollectionsMainViewModel(ViewModel):
    __slots__ = ('onOpenCollection', 'onClose', 'setCompletionWasShown', 'onSetNewCollectionShown')

    def __init__(self, properties=2, commands=4):
        super(CollectionsMainViewModel, self).__init__(properties=properties, commands=commands)

    def getIsViewActive(self):
        return self._getBool(0)

    def setIsViewActive(self, value):
        self._setBool(0, value)

    def getCollections(self):
        return self._getArray(1)

    def setCollections(self, value):
        self._setArray(1, value)

    @staticmethod
    def getCollectionsType():
        return CollectionModel

    def _initialize(self):
        super(CollectionsMainViewModel, self)._initialize()
        self._addBoolProperty('isViewActive', False)
        self._addArrayProperty('collections', Array())
        self.onOpenCollection = self._addCommand('onOpenCollection')
        self.onClose = self._addCommand('onClose')
        self.setCompletionWasShown = self._addCommand('setCompletionWasShown')
        self.onSetNewCollectionShown = self._addCommand('onSetNewCollectionShown')
