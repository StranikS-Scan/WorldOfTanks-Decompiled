# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/tooltips/new_year_album_toy_content_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class NewYearAlbumToyContentModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=13, commands=0):
        super(NewYearAlbumToyContentModel, self).__init__(properties=properties, commands=commands)

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

    def getTypeName(self):
        return self._getString(3)

    def setTypeName(self, value):
        self._setString(3, value)

    def getIsInCollection(self):
        return self._getBool(4)

    def setIsInCollection(self, value):
        self._setBool(4, value)

    def getIsInInventory(self):
        return self._getBool(5)

    def setIsInInventory(self, value):
        self._setBool(5, value)

    def getToyIcon(self):
        return self._getResource(6)

    def setToyIcon(self, value):
        self._setResource(6, value)

    def getToyName(self):
        return self._getResource(7)

    def setToyName(self, value):
        self._setResource(7, value)

    def getToyDesc(self):
        return self._getResource(8)

    def setToyDesc(self, value):
        self._setResource(8, value)

    def getIsMount(self):
        return self._getBool(9)

    def setIsMount(self, value):
        self._setBool(9, value)

    def getIsMega(self):
        return self._getBool(10)

    def setIsMega(self, value):
        self._setBool(10, value)

    def getTotalBonus(self):
        return self._getReal(11)

    def setTotalBonus(self, value):
        self._setReal(11, value)

    def getToyBonus(self):
        return self._getReal(12)

    def setToyBonus(self, value):
        self._setReal(12, value)

    def _initialize(self):
        super(NewYearAlbumToyContentModel, self)._initialize()
        self._addStringProperty('rankNumber', '')
        self._addStringProperty('rankRoman', '')
        self._addStringProperty('setting', '')
        self._addStringProperty('typeName', '')
        self._addBoolProperty('isInCollection', False)
        self._addBoolProperty('isInInventory', False)
        self._addResourceProperty('toyIcon', R.invalid())
        self._addResourceProperty('toyName', R.invalid())
        self._addResourceProperty('toyDesc', R.invalid())
        self._addBoolProperty('isMount', False)
        self._addBoolProperty('isMega', False)
        self._addRealProperty('totalBonus', 0.0)
        self._addRealProperty('toyBonus', 0.0)
