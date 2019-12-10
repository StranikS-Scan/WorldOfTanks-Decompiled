# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/components/new_year_album_toy_old_renderer_model.py
from gui.impl.gen.view_models.views.lobby.new_year.components.new_year_album_toy_renderer_model import NewYearAlbumToyRendererModel

class NewYearAlbumToyOldRendererModel(NewYearAlbumToyRendererModel):
    __slots__ = ()

    def __init__(self, properties=8, commands=0):
        super(NewYearAlbumToyOldRendererModel, self).__init__(properties=properties, commands=commands)

    def getShards(self):
        return self._getNumber(6)

    def setShards(self, value):
        self._setNumber(6, value)

    def getIsCanCraft(self):
        return self._getBool(7)

    def setIsCanCraft(self, value):
        self._setBool(7, value)

    def _initialize(self):
        super(NewYearAlbumToyOldRendererModel, self)._initialize()
        self._addNumberProperty('shards', 0)
        self._addBoolProperty('isCanCraft', False)
