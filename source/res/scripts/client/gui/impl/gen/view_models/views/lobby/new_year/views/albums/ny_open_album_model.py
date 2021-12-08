# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/albums/ny_open_album_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.new_year.components.ny_album_decoration_model import NyAlbumDecorationModel

class NyOpenAlbumModel(ViewModel):
    __slots__ = ('onGoToRewards', 'onToyClick', 'onCollectionChange', 'onRankChange')

    def __init__(self, properties=11, commands=4):
        super(NyOpenAlbumModel, self).__init__(properties=properties, commands=commands)

    def getCurrentCollection(self):
        return self._getString(0)

    def setCurrentCollection(self, value):
        self._setString(0, value)

    def getCurrentRank(self):
        return self._getNumber(1)

    def setCurrentRank(self, value):
        self._setNumber(1, value)

    def getIsCollectionFull(self):
        return self._getBool(2)

    def setIsCollectionFull(self, value):
        self._setBool(2, value)

    def getCollectedToysCount(self):
        return self._getNumber(3)

    def setCollectedToysCount(self, value):
        self._setNumber(3, value)

    def getTotalToysCount(self):
        return self._getNumber(4)

    def setTotalToysCount(self, value):
        self._setNumber(4, value)

    def getNewToysCount(self):
        return self._getNumber(5)

    def setNewToysCount(self, value):
        self._setNumber(5, value)

    def getCurrentRankToysCount(self):
        return self._getNumber(6)

    def setCurrentRankToysCount(self, value):
        self._setNumber(6, value)

    def getTotalRankToysCount(self):
        return self._getNumber(7)

    def setTotalRankToysCount(self, value):
        self._setNumber(7, value)

    def getCurrentRomanRank(self):
        return self._getString(8)

    def setCurrentRomanRank(self, value):
        self._setString(8, value)

    def getCollectionTabs(self):
        return self._getArray(9)

    def setCollectionTabs(self, value):
        self._setArray(9, value)

    def getToys(self):
        return self._getArray(10)

    def setToys(self, value):
        self._setArray(10, value)

    def _initialize(self):
        super(NyOpenAlbumModel, self)._initialize()
        self._addStringProperty('currentCollection', '')
        self._addNumberProperty('currentRank', 0)
        self._addBoolProperty('isCollectionFull', False)
        self._addNumberProperty('collectedToysCount', 0)
        self._addNumberProperty('totalToysCount', 0)
        self._addNumberProperty('newToysCount', 0)
        self._addNumberProperty('currentRankToysCount', 0)
        self._addNumberProperty('totalRankToysCount', 0)
        self._addStringProperty('currentRomanRank', '')
        self._addArrayProperty('collectionTabs', Array())
        self._addArrayProperty('toys', Array())
        self.onGoToRewards = self._addCommand('onGoToRewards')
        self.onToyClick = self._addCommand('onToyClick')
        self.onCollectionChange = self._addCommand('onCollectionChange')
        self.onRankChange = self._addCommand('onRankChange')
