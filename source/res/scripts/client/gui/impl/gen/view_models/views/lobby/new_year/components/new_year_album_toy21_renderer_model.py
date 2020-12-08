# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/components/new_year_album_toy21_renderer_model.py
from gui.impl.gen.view_models.views.lobby.new_year.components.new_year_album_toy_renderer_model import NewYearAlbumToyRendererModel

class NewYearAlbumToy21RendererModel(NewYearAlbumToyRendererModel):
    __slots__ = ()

    def __init__(self, properties=11, commands=0):
        super(NewYearAlbumToy21RendererModel, self).__init__(properties=properties, commands=commands)

    def getBonusValue(self):
        return self._getReal(8)

    def setBonusValue(self, value):
        self._setReal(8, value)

    def getIsInInventory(self):
        return self._getBool(9)

    def setIsInInventory(self, value):
        self._setBool(9, value)

    def getNewNumber(self):
        return self._getNumber(10)

    def setNewNumber(self, value):
        self._setNumber(10, value)

    def _initialize(self):
        super(NewYearAlbumToy21RendererModel, self)._initialize()
        self._addRealProperty('bonusValue', 0.0)
        self._addBoolProperty('isInInventory', False)
        self._addNumberProperty('newNumber', 0)
