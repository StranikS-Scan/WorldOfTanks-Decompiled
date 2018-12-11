# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/new_year/components/new_year_album_toy19_renderer_model.py
from gui.impl.gen.view_models.new_year.components.new_year_album_toy_renderer_model import NewYearAlbumToyRendererModel

class NewYearAlbumToy19RendererModel(NewYearAlbumToyRendererModel):
    __slots__ = ()

    def getIsNew(self):
        return self._getBool(5)

    def setIsNew(self, value):
        self._setBool(5, value)

    def getNewNumber(self):
        return self._getNumber(6)

    def setNewNumber(self, value):
        self._setNumber(6, value)

    def _initialize(self):
        super(NewYearAlbumToy19RendererModel, self)._initialize()
        self._addBoolProperty('isNew', False)
        self._addNumberProperty('newNumber', 0)
