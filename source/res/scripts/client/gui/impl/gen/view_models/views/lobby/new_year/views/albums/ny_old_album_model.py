# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/albums/ny_old_album_model.py
from gui.impl.gen.view_models.views.lobby.new_year.views.albums.ny_open_album_model import NyOpenAlbumModel

class NyOldAlbumModel(NyOpenAlbumModel):
    __slots__ = ('onBuyFullCollection',)

    def __init__(self, properties=13, commands=5):
        super(NyOldAlbumModel, self).__init__(properties=properties, commands=commands)

    def getTotalShardsPrice(self):
        return self._getNumber(11)

    def setTotalShardsPrice(self, value):
        self._setNumber(11, value)

    def getFullCollectionCost(self):
        return self._getNumber(12)

    def setFullCollectionCost(self, value):
        self._setNumber(12, value)

    def _initialize(self):
        super(NyOldAlbumModel, self)._initialize()
        self._addNumberProperty('totalShardsPrice', 0)
        self._addNumberProperty('fullCollectionCost', 0)
        self.onBuyFullCollection = self._addCommand('onBuyFullCollection')
