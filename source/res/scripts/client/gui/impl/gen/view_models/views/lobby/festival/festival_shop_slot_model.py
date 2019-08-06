# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/festival/festival_shop_slot_model.py
from frameworks.wulf import ViewModel

class FestivalShopSlotModel(ViewModel):
    __slots__ = ()

    def getPackageID(self):
        return self._getNumber(0)

    def setPackageID(self, value):
        self._setNumber(0, value)

    def getIcon(self):
        return self._getString(1)

    def setIcon(self, value):
        self._setString(1, value)

    def getModifierIcon(self):
        return self._getString(2)

    def setModifierIcon(self, value):
        self._setString(2, value)

    def getTitle(self):
        return self._getString(3)

    def setTitle(self, value):
        self._setString(3, value)

    def getDescription(self):
        return self._getString(4)

    def setDescription(self, value):
        self._setString(4, value)

    def getCounter(self):
        return self._getNumber(5)

    def setCounter(self, value):
        self._setNumber(5, value)

    def getPrice(self):
        return self._getNumber(6)

    def setPrice(self, value):
        self._setNumber(6, value)

    def getIsMoneyEnough(self):
        return self._getBool(7)

    def setIsMoneyEnough(self, value):
        self._setBool(7, value)

    def _initialize(self):
        super(FestivalShopSlotModel, self)._initialize()
        self._addNumberProperty('packageID', 0)
        self._addStringProperty('icon', '')
        self._addStringProperty('modifierIcon', '')
        self._addStringProperty('title', '')
        self._addStringProperty('description', '')
        self._addNumberProperty('counter', 0)
        self._addNumberProperty('price', 0)
        self._addBoolProperty('isMoneyEnough', False)
