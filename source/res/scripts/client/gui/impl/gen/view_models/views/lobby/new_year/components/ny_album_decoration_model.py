# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/components/ny_album_decoration_model.py
from frameworks.wulf import ViewModel

class NyAlbumDecorationModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=6, commands=0):
        super(NyAlbumDecorationModel, self).__init__(properties=properties, commands=commands)

    def getToyID(self):
        return self._getNumber(0)

    def setToyID(self, value):
        self._setNumber(0, value)

    def getIsInCollection(self):
        return self._getBool(1)

    def setIsInCollection(self, value):
        self._setBool(1, value)

    def getToyImageName(self):
        return self._getString(2)

    def setToyImageName(self, value):
        self._setString(2, value)

    def getIsNew(self):
        return self._getBool(3)

    def setIsNew(self, value):
        self._setBool(3, value)

    def getToyType(self):
        return self._getString(4)

    def setToyType(self, value):
        self._setString(4, value)

    def getIsMega(self):
        return self._getBool(5)

    def setIsMega(self, value):
        self._setBool(5, value)

    def _initialize(self):
        super(NyAlbumDecorationModel, self)._initialize()
        self._addNumberProperty('toyID', 0)
        self._addBoolProperty('isInCollection', False)
        self._addStringProperty('toyImageName', '')
        self._addBoolProperty('isNew', False)
        self._addStringProperty('toyType', '')
        self._addBoolProperty('isMega', False)
