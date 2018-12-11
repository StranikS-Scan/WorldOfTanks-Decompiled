# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/new_year/components/new_year_side_bar_button_model.py
from frameworks.wulf import Resource
from frameworks.wulf import ViewModel

class NewYearSideBarButtonModel(ViewModel):
    __slots__ = ()

    def getObjectName(self):
        return self._getString(0)

    def setObjectName(self, value):
        self._setString(0, value)

    def getTypeIcon(self):
        return self._getResource(1)

    def setTypeIcon(self, value):
        self._setResource(1, value)

    def getLabel(self):
        return self._getResource(2)

    def setLabel(self, value):
        self._setResource(2, value)

    def getIsSelected(self):
        return self._getBool(3)

    def setIsSelected(self, value):
        self._setBool(3, value)

    def getIsBetterAvailable(self):
        return self._getBool(4)

    def setIsBetterAvailable(self, value):
        self._setBool(4, value)

    def _initialize(self):
        super(NewYearSideBarButtonModel, self)._initialize()
        self._addStringProperty('objectName', '')
        self._addResourceProperty('typeIcon', Resource.INVALID)
        self._addResourceProperty('label', Resource.INVALID)
        self._addBoolProperty('isSelected', False)
        self._addBoolProperty('isBetterAvailable', False)
