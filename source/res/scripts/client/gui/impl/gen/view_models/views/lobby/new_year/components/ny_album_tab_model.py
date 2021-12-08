# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/components/ny_album_tab_model.py
from gui.impl.gen.view_models.views.lobby.new_year.components.new_year_tab_model import NewYearTabModel

class NyAlbumTabModel(NewYearTabModel):
    __slots__ = ()

    def __init__(self, properties=7, commands=0):
        super(NyAlbumTabModel, self).__init__(properties=properties, commands=commands)

    def getCurrentValue(self):
        return self._getNumber(4)

    def setCurrentValue(self, value):
        self._setNumber(4, value)

    def getTotalValue(self):
        return self._getNumber(5)

    def setTotalValue(self, value):
        self._setNumber(5, value)

    def getCollectionName(self):
        return self._getString(6)

    def setCollectionName(self, value):
        self._setString(6, value)

    def _initialize(self):
        super(NyAlbumTabModel, self)._initialize()
        self._addNumberProperty('currentValue', 0)
        self._addNumberProperty('totalValue', 0)
        self._addStringProperty('collectionName', '')
