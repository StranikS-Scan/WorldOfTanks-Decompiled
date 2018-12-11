# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/new_year/tooltips/new_year_album_toy_content_model.py
from frameworks.wulf import Resource
from frameworks.wulf import ViewModel

class NewYearAlbumToyContentModel(ViewModel):
    __slots__ = ()

    def getRankNumber(self):
        return self._getString(0)

    def setRankNumber(self, value):
        self._setString(0, value)

    def getRankRoman(self):
        return self._getString(1)

    def setRankRoman(self, value):
        self._setString(1, value)

    def getSetting(self):
        return self._getString(2)

    def setSetting(self, value):
        self._setString(2, value)

    def getIsInCollection(self):
        return self._getBool(3)

    def setIsInCollection(self, value):
        self._setBool(3, value)

    def getToyIcon(self):
        return self._getResource(4)

    def setToyIcon(self, value):
        self._setResource(4, value)

    def getToyName(self):
        return self._getResource(5)

    def setToyName(self, value):
        self._setResource(5, value)

    def getToyDesc(self):
        return self._getResource(6)

    def setToyDesc(self, value):
        self._setResource(6, value)

    def _initialize(self):
        super(NewYearAlbumToyContentModel, self)._initialize()
        self._addStringProperty('rankNumber', '')
        self._addStringProperty('rankRoman', '')
        self._addStringProperty('setting', '')
        self._addBoolProperty('isInCollection', False)
        self._addResourceProperty('toyIcon', Resource.INVALID)
        self._addResourceProperty('toyName', Resource.INVALID)
        self._addResourceProperty('toyDesc', Resource.INVALID)
