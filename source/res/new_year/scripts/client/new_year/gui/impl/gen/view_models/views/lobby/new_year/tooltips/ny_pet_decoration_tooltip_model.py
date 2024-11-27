# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/gen/view_models/views/lobby/new_year/tooltips/ny_pet_decoration_tooltip_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class NyPetDecorationTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=7, commands=0):
        super(NyPetDecorationTooltipModel, self).__init__(properties=properties, commands=commands)

    def getName(self):
        return self._getResource(0)

    def setName(self, value):
        self._setResource(0, value)

    def getDecorationType(self):
        return self._getString(1)

    def setDecorationType(self, value):
        self._setString(1, value)

    def getDecorationTypeIcon(self):
        return self._getResource(2)

    def setDecorationTypeIcon(self, value):
        self._setResource(2, value)

    def getDescription(self):
        return self._getResource(3)

    def setDescription(self, value):
        self._setResource(3, value)

    def getIcon(self):
        return self._getResource(4)

    def setIcon(self, value):
        self._setResource(4, value)

    def getIsLocked(self):
        return self._getBool(5)

    def setIsLocked(self, value):
        self._setBool(5, value)

    def getPrice(self):
        return self._getNumber(6)

    def setPrice(self, value):
        self._setNumber(6, value)

    def _initialize(self):
        super(NyPetDecorationTooltipModel, self)._initialize()
        self._addResourceProperty('name', R.invalid())
        self._addStringProperty('decorationType', '')
        self._addResourceProperty('decorationTypeIcon', R.invalid())
        self._addResourceProperty('description', R.invalid())
        self._addResourceProperty('icon', R.invalid())
        self._addBoolProperty('isLocked', True)
        self._addNumberProperty('price', 0)
