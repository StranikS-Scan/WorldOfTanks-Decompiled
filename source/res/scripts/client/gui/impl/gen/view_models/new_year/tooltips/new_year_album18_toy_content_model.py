# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/new_year/tooltips/new_year_album18_toy_content_model.py
from gui.impl.gen.view_models.new_year.tooltips.new_year_album_toy_content_model import NewYearAlbumToyContentModel

class NewYearAlbum18ToyContentModel(NewYearAlbumToyContentModel):
    __slots__ = ()

    def getShards(self):
        return self._getNumber(7)

    def setShards(self, value):
        self._setNumber(7, value)

    def _initialize(self):
        super(NewYearAlbum18ToyContentModel, self)._initialize()
        self._addNumberProperty('shards', 0)
