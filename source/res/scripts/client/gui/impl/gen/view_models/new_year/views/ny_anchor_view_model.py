# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/new_year/views/ny_anchor_view_model.py
from frameworks.wulf import Resource
from frameworks.wulf import ViewModel

class NyAnchorViewModel(ViewModel):
    __slots__ = ()

    def getIcon(self):
        return self._getResource(0)

    def setIcon(self, value):
        self._setResource(0, value)

    def getTypeIcon(self):
        return self._getResource(1)

    def setTypeIcon(self, value):
        self._setResource(1, value)

    def getIsSelected(self):
        return self._getBool(2)

    def setIsSelected(self, value):
        self._setBool(2, value)

    def getIsVisible(self):
        return self._getBool(3)

    def setIsVisible(self, value):
        self._setBool(3, value)

    def getIsBetterAvailable(self):
        return self._getBool(4)

    def setIsBetterAvailable(self, value):
        self._setBool(4, value)

    def getIsMaxLevel(self):
        return self._getBool(5)

    def setIsMaxLevel(self, value):
        self._setBool(5, value)

    def getIsEmpty(self):
        return self._getBool(6)

    def setIsEmpty(self, value):
        self._setBool(6, value)

    def getIsFir(self):
        return self._getBool(7)

    def setIsFir(self, value):
        self._setBool(7, value)

    def _initialize(self):
        super(NyAnchorViewModel, self)._initialize()
        self._addResourceProperty('icon', Resource.INVALID)
        self._addResourceProperty('typeIcon', Resource.INVALID)
        self._addBoolProperty('isSelected', False)
        self._addBoolProperty('isVisible', False)
        self._addBoolProperty('isBetterAvailable', False)
        self._addBoolProperty('isMaxLevel', False)
        self._addBoolProperty('isEmpty', False)
        self._addBoolProperty('isFir', False)
