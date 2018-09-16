# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/buy_vehicle_view/additional_equipment_slot_model.py
import typing
from frameworks.wulf import Array
from frameworks.wulf import ViewModel

class AdditionalEquipmentSlotModel(ViewModel):
    __slots__ = ('onSelectedChange',)

    def getIsBtnEnabled(self):
        return self._getBool(0)

    def setIsBtnEnabled(self, value):
        self._setBool(0, value)

    def getIsSelected(self):
        return self._getBool(1)

    def setIsSelected(self, value):
        self._setBool(1, value)

    def getActionPrices(self):
        return self._getArray(2)

    def setActionPrices(self, value):
        self._setArray(2, value)

    def getDisabledTooltip(self):
        return self._getString(3)

    def setDisabledTooltip(self, value):
        self._setString(3, value)

    def _initialize(self):
        self._addBoolProperty('isBtnEnabled', False)
        self._addBoolProperty('isSelected', False)
        self._addArrayProperty('actionPrices', Array())
        self._addStringProperty('disabledTooltip', '')
        self.onSelectedChange = self._addCommand('onSelectedChange')
