# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/new_year/components/new_year_album_side_bar_button_model.py
from frameworks.wulf import ViewModel

class NewYearAlbumSideBarButtonModel(ViewModel):
    __slots__ = ()

    def getCurrentValue(self):
        return self._getNumber(0)

    def setCurrentValue(self, value):
        self._setNumber(0, value)

    def getTotalValue(self):
        return self._getNumber(1)

    def setTotalValue(self, value):
        self._setNumber(1, value)

    def getIsSelected(self):
        return self._getBool(2)

    def setIsSelected(self, value):
        self._setBool(2, value)

    def getCollectionName(self):
        return self._getString(3)

    def setCollectionName(self, value):
        self._setString(3, value)

    def _initialize(self):
        super(NewYearAlbumSideBarButtonModel, self)._initialize()
        self._addNumberProperty('currentValue', 0)
        self._addNumberProperty('totalValue', 0)
        self._addBoolProperty('isSelected', False)
        self._addStringProperty('collectionName', '')
