# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/collection/collection_item_preview_model.py
from frameworks.wulf import ViewModel

class CollectionItemPreviewModel(ViewModel):
    __slots__ = ('onClosePreview',)

    def __init__(self, properties=5, commands=1):
        super(CollectionItemPreviewModel, self).__init__(properties=properties, commands=commands)

    def getName(self):
        return self._getString(0)

    def setName(self, value):
        self._setString(0, value)

    def getType(self):
        return self._getString(1)

    def setType(self, value):
        self._setString(1, value)

    def getDescription(self):
        return self._getString(2)

    def setDescription(self, value):
        self._setString(2, value)

    def getSmallImage(self):
        return self._getString(3)

    def setSmallImage(self, value):
        self._setString(3, value)

    def getLargeImage(self):
        return self._getString(4)

    def setLargeImage(self, value):
        self._setString(4, value)

    def _initialize(self):
        super(CollectionItemPreviewModel, self)._initialize()
        self._addStringProperty('name', '')
        self._addStringProperty('type', '')
        self._addStringProperty('description', '')
        self._addStringProperty('smallImage', '')
        self._addStringProperty('largeImage', '')
        self.onClosePreview = self._addCommand('onClosePreview')
