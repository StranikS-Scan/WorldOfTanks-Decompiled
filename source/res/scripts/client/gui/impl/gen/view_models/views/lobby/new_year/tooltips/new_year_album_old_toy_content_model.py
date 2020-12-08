# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/tooltips/new_year_album_old_toy_content_model.py
from gui.impl.gen.view_models.views.lobby.new_year.tooltips.new_year_album_toy_content_model import NewYearAlbumToyContentModel

class NewYearAlbumOldToyContentModel(NewYearAlbumToyContentModel):
    __slots__ = ()

    def __init__(self, properties=14, commands=0):
        super(NewYearAlbumOldToyContentModel, self).__init__(properties=properties, commands=commands)

    def getShards(self):
        return self._getNumber(13)

    def setShards(self, value):
        self._setNumber(13, value)

    def _initialize(self):
        super(NewYearAlbumOldToyContentModel, self)._initialize()
        self._addNumberProperty('shards', 0)
