# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/new_year_album_page_old_view_model.py
from gui.impl.gen.view_models.views.lobby.new_year.views.new_year_album_page_view_model import NewYearAlbumPageViewModel

class NewYearAlbumPageOldViewModel(NewYearAlbumPageViewModel):
    __slots__ = ('onBuyFullCollection',)

    def __init__(self, properties=18, commands=8):
        super(NewYearAlbumPageOldViewModel, self).__init__(properties=properties, commands=commands)

    def getTotalShards(self):
        return self._getNumber(16)

    def setTotalShards(self, value):
        self._setNumber(16, value)

    def getCostFullCollection(self):
        return self._getNumber(17)

    def setCostFullCollection(self, value):
        self._setNumber(17, value)

    def _initialize(self):
        super(NewYearAlbumPageOldViewModel, self)._initialize()
        self._addNumberProperty('totalShards', 0)
        self._addNumberProperty('costFullCollection', 0)
        self.onBuyFullCollection = self._addCommand('onBuyFullCollection')
