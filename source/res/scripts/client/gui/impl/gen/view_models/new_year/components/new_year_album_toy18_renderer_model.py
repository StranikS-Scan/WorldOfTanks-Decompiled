# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/new_year/components/new_year_album_toy18_renderer_model.py
from gui.impl.gen.view_models.new_year.components.new_year_album_toy_renderer_model import NewYearAlbumToyRendererModel

class NewYearAlbumToy18RendererModel(NewYearAlbumToyRendererModel):
    __slots__ = ()

    def getShards(self):
        return self._getNumber(5)

    def setShards(self, value):
        self._setNumber(5, value)

    def getIsCanCraft(self):
        return self._getBool(6)

    def setIsCanCraft(self, value):
        self._setBool(6, value)

    def getIsNew(self):
        return self._getBool(7)

    def setIsNew(self, value):
        self._setBool(7, value)

    def _initialize(self):
        super(NewYearAlbumToy18RendererModel, self)._initialize()
        self._addNumberProperty('shards', 0)
        self._addBoolProperty('isCanCraft', False)
        self._addBoolProperty('isNew', False)
