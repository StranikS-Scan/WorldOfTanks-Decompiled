# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/albums/ny_album_collection_tab_model.py
from frameworks.wulf import ViewModel

class NyAlbumCollectionTabModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(NyAlbumCollectionTabModel, self).__init__(properties=properties, commands=commands)

    def getTitle(self):
        return self._getString(0)

    def setTitle(self, value):
        self._setString(0, value)

    def getSelectedRank(self):
        return self._getNumber(1)

    def setSelectedRank(self, value):
        self._setNumber(1, value)

    def _initialize(self):
        super(NyAlbumCollectionTabModel, self)._initialize()
        self._addStringProperty('title', '')
        self._addNumberProperty('selectedRank', 1)
