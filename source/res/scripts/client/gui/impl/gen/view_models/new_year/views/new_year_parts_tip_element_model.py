# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/new_year/views/new_year_parts_tip_element_model.py
from frameworks.wulf import Resource
from frameworks.wulf import ViewModel

class NewYearPartsTipElementModel(ViewModel):
    __slots__ = ()
    PARTS_ENOUGH = 0
    PARTS_NOT_ENOUGH = 1
    DECORATION_NOT_SELECTED = 2

    def getDecorationTypeIcon(self):
        return self._getResource(0)

    def setDecorationTypeIcon(self, value):
        self._setResource(0, value)

    def getPartsCountLeft(self):
        return self._getNumber(1)

    def setPartsCountLeft(self, value):
        self._setNumber(1, value)

    def getCurrentState(self):
        return self._getNumber(2)

    def setCurrentState(self, value):
        self._setNumber(2, value)

    def _initialize(self):
        super(NewYearPartsTipElementModel, self)._initialize()
        self._addResourceProperty('decorationTypeIcon', Resource.INVALID)
        self._addNumberProperty('partsCountLeft', 0)
        self._addNumberProperty('currentState', 0)
