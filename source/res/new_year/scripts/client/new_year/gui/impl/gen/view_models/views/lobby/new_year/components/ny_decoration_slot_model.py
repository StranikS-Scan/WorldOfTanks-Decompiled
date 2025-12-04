# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/gen/view_models/views/lobby/new_year/components/ny_decoration_slot_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class NyDecorationSlotModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=10, commands=0):
        super(NyDecorationSlotModel, self).__init__(properties=properties, commands=commands)

    def getToyID(self):
        return self._getNumber(0)

    def setToyID(self, value):
        self._setNumber(0, value)

    def getImageName(self):
        return self._getString(1)

    def setImageName(self, value):
        self._setString(1, value)

    def getTitle(self):
        return self._getResource(2)

    def setTitle(self, value):
        self._setResource(2, value)

    def getDescription(self):
        return self._getResource(3)

    def setDescription(self, value):
        self._setResource(3, value)

    def getAtmosphereBonus(self):
        return self._getNumber(4)

    def setAtmosphereBonus(self, value):
        self._setNumber(4, value)

    def getType(self):
        return self._getString(5)

    def setType(self, value):
        self._setString(5, value)

    def getRank(self):
        return self._getNumber(6)

    def setRank(self, value):
        self._setNumber(6, value)

    def getGoldPrice(self):
        return self._getNumber(7)

    def setGoldPrice(self, value):
        self._setNumber(7, value)

    def getIsPremium(self):
        return self._getBool(8)

    def setIsPremium(self, value):
        self._setBool(8, value)

    def getIsSelected(self):
        return self._getBool(9)

    def setIsSelected(self, value):
        self._setBool(9, value)

    def _initialize(self):
        super(NyDecorationSlotModel, self)._initialize()
        self._addNumberProperty('toyID', 0)
        self._addStringProperty('imageName', '')
        self._addResourceProperty('title', R.invalid())
        self._addResourceProperty('description', R.invalid())
        self._addNumberProperty('atmosphereBonus', 0)
        self._addStringProperty('type', '')
        self._addNumberProperty('rank', 1)
        self._addNumberProperty('goldPrice', 0)
        self._addBoolProperty('isPremium', False)
        self._addBoolProperty('isSelected', False)
