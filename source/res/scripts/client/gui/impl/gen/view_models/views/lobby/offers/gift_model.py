# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/offers/gift_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class GiftModel(ViewModel):
    __slots__ = ()
    RENT_TYPE_NO = 'no_rent'
    RENT_TYPE_TIME = 'time'
    RENT_TYPE_BATTLES = 'battles'
    RENT_TYPE_WINS = 'wins'

    def __init__(self, properties=12, commands=0):
        super(GiftModel, self).__init__(properties=properties, commands=commands)

    def getId(self):
        return self._getNumber(0)

    def setId(self, value):
        self._setNumber(0, value)

    def getTitle(self):
        return self._getString(1)

    def setTitle(self, value):
        self._setString(1, value)

    def getDescription(self):
        return self._getString(2)

    def setDescription(self, value):
        self._setString(2, value)

    def getIcon(self):
        return self._getString(3)

    def setIcon(self, value):
        self._setString(3, value)

    def getCount(self):
        return self._getNumber(4)

    def setCount(self, value):
        self._setNumber(4, value)

    def getNationFlag(self):
        return self._getString(5)

    def setNationFlag(self, value):
        self._setString(5, value)

    def getHighlight(self):
        return self._getString(6)

    def setHighlight(self, value):
        self._setString(6, value)

    def getRentType(self):
        return self._getString(7)

    def setRentType(self, value):
        self._setString(7, value)

    def getRentValue(self):
        return self._getNumber(8)

    def setRentValue(self, value):
        self._setNumber(8, value)

    def getInventoryCount(self):
        return self._getNumber(9)

    def setInventoryCount(self, value):
        self._setNumber(9, value)

    def getIsDisabled(self):
        return self._getBool(10)

    def setIsDisabled(self, value):
        self._setBool(10, value)

    def getButtonLabel(self):
        return self._getResource(11)

    def setButtonLabel(self, value):
        self._setResource(11, value)

    def _initialize(self):
        super(GiftModel, self)._initialize()
        self._addNumberProperty('id', 0)
        self._addStringProperty('title', '')
        self._addStringProperty('description', '')
        self._addStringProperty('icon', '')
        self._addNumberProperty('count', 0)
        self._addStringProperty('nationFlag', '')
        self._addStringProperty('highlight', '')
        self._addStringProperty('rentType', '')
        self._addNumberProperty('rentValue', 0)
        self._addNumberProperty('inventoryCount', 0)
        self._addBoolProperty('isDisabled', False)
        self._addResourceProperty('buttonLabel', R.invalid())
