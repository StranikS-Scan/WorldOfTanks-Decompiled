# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/buy_vehicle_view/commander_slot_model.py
import typing
from frameworks.wulf import Array
from frameworks.wulf import ViewModel

class CommanderSlotModel(ViewModel):
    __slots__ = ()

    def getIdx(self):
        return self._getNumber(0)

    def setIdx(self, value):
        self._setNumber(0, value)

    def getIsSelected(self):
        return self._getBool(1)

    def setIsSelected(self, value):
        self._setBool(1, value)

    def getPercents(self):
        return self._getNumber(2)

    def setPercents(self, value):
        self._setNumber(2, value)

    def getTitle(self):
        return self._getString(3)

    def setTitle(self, value):
        self._setString(3, value)

    def getDefPrice(self):
        return self._getString(4)

    def setDefPrice(self, value):
        self._setString(4, value)

    def getIsFree(self):
        return self._getBool(5)

    def setIsFree(self, value):
        self._setBool(5, value)

    def getDiscount(self):
        return self._getNumber(6)

    def setDiscount(self, value):
        self._setNumber(6, value)

    def getSlotIsEnabled(self):
        return self._getBool(7)

    def setSlotIsEnabled(self, value):
        self._setBool(7, value)

    def getActionPrice(self):
        return self._getArray(8)

    def setActionPrice(self, value):
        self._setArray(8, value)

    def getShowBootcampAnim(self):
        return self._getBool(9)

    def setShowBootcampAnim(self, value):
        self._setBool(9, value)

    def _initialize(self):
        self._addNumberProperty('idx', 0)
        self._addBoolProperty('isSelected', False)
        self._addNumberProperty('percents', 0)
        self._addStringProperty('title', '')
        self._addStringProperty('defPrice', '')
        self._addBoolProperty('isFree', False)
        self._addNumberProperty('discount', 0)
        self._addBoolProperty('slotIsEnabled', True)
        self._addArrayProperty('actionPrice', Array())
        self._addBoolProperty('showBootcampAnim', False)
