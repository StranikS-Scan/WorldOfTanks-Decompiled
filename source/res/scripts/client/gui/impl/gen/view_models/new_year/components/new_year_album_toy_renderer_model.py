# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/new_year/components/new_year_album_toy_renderer_model.py
from frameworks.wulf import Resource
from frameworks.wulf import ViewModel

class NewYearAlbumToyRendererModel(ViewModel):
    __slots__ = ()

    def getToyID(self):
        return self._getNumber(0)

    def setToyID(self, value):
        self._setNumber(0, value)

    def getPassepartoutImage(self):
        return self._getResource(1)

    def setPassepartoutImage(self, value):
        self._setResource(1, value)

    def getEmptyPassepartoutImage(self):
        return self._getResource(2)

    def setEmptyPassepartoutImage(self, value):
        self._setResource(2, value)

    def getIsInCollection(self):
        return self._getBool(3)

    def setIsInCollection(self, value):
        self._setBool(3, value)

    def getToyImage(self):
        return self._getResource(4)

    def setToyImage(self, value):
        self._setResource(4, value)

    def _initialize(self):
        super(NewYearAlbumToyRendererModel, self)._initialize()
        self._addNumberProperty('toyID', 0)
        self._addResourceProperty('passepartoutImage', Resource.INVALID)
        self._addResourceProperty('emptyPassepartoutImage', Resource.INVALID)
        self._addBoolProperty('isInCollection', False)
        self._addResourceProperty('toyImage', Resource.INVALID)
