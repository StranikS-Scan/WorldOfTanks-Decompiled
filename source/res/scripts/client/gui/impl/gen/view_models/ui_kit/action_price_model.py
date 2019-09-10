# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/ui_kit/action_price_model.py
from frameworks.wulf import ViewModel

class ActionPriceModel(ViewModel):
    __slots__ = ()

    def getType(self):
        return self._getString(0)

    def setType(self, value):
        self._setString(0, value)

    def getIsEnough(self):
        return self._getBool(1)

    def setIsEnough(self, value):
        self._setBool(1, value)

    def getIsWithAction(self):
        return self._getBool(2)

    def setIsWithAction(self, value):
        self._setBool(2, value)

    def getAction(self):
        return self._getNumber(3)

    def setAction(self, value):
        self._setNumber(3, value)

    def getDefPrice(self):
        return self._getString(4)

    def setDefPrice(self, value):
        self._setString(4, value)

    def getPrice(self):
        return self._getString(5)

    def setPrice(self, value):
        self._setString(5, value)

    def getIsFree(self):
        return self._getBool(6)

    def setIsFree(self, value):
        self._setBool(6, value)

    def getFontNotEnoughIsEnabled(self):
        return self._getBool(7)

    def setFontNotEnoughIsEnabled(self, value):
        self._setBool(7, value)

    def getTooltipType(self):
        return self._getString(8)

    def setTooltipType(self, value):
        self._setString(8, value)

    def getKey(self):
        return self._getString(9)

    def setKey(self, value):
        self._setString(9, value)

    def getNewCredits(self):
        return self._getNumber(10)

    def setNewCredits(self, value):
        self._setNumber(10, value)

    def getNewGold(self):
        return self._getNumber(11)

    def setNewGold(self, value):
        self._setNumber(11, value)

    def getNewCrystal(self):
        return self._getNumber(12)

    def setNewCrystal(self, value):
        self._setNumber(12, value)

    def getOldCredits(self):
        return self._getNumber(13)

    def setOldCredits(self, value):
        self._setNumber(13, value)

    def getOldGold(self):
        return self._getNumber(14)

    def setOldGold(self, value):
        self._setNumber(14, value)

    def getOldCrystal(self):
        return self._getNumber(15)

    def setOldCrystal(self, value):
        self._setNumber(15, value)

    def getIsBuying(self):
        return self._getBool(16)

    def setIsBuying(self, value):
        self._setBool(16, value)

    def getShowOldValue(self):
        return self._getBool(17)

    def setShowOldValue(self, value):
        self._setBool(17, value)

    def _initialize(self):
        super(ActionPriceModel, self)._initialize()
        self._addStringProperty('type', 'gold')
        self._addBoolProperty('isEnough', False)
        self._addBoolProperty('isWithAction', False)
        self._addNumberProperty('action', 0)
        self._addStringProperty('defPrice', '')
        self._addStringProperty('price', '')
        self._addBoolProperty('isFree', False)
        self._addBoolProperty('fontNotEnoughIsEnabled', True)
        self._addStringProperty('tooltipType', 'economics')
        self._addStringProperty('key', '')
        self._addNumberProperty('newCredits', 0)
        self._addNumberProperty('newGold', 0)
        self._addNumberProperty('newCrystal', 0)
        self._addNumberProperty('oldCredits', 0)
        self._addNumberProperty('oldGold', 0)
        self._addNumberProperty('oldCrystal', 0)
        self._addBoolProperty('isBuying', True)
        self._addBoolProperty('showOldValue', False)
