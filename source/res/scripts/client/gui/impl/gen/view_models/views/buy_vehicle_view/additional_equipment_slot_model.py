# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/buy_vehicle_view/additional_equipment_slot_model.py
import typing
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.ui_kit.list_model import ListModel

class AdditionalEquipmentSlotModel(ViewModel):
    __slots__ = ('onSelectedChange',)

    @property
    def actionPrices(self):
        return self._getViewModel(0)

    def getIsBtnEnabled(self):
        return self._getBool(1)

    def setIsBtnEnabled(self, value):
        self._setBool(1, value)

    def getIsSelected(self):
        return self._getBool(2)

    def setIsSelected(self, value):
        self._setBool(2, value)

    def getDisabledTooltip(self):
        return self._getString(3)

    def setDisabledTooltip(self, value):
        self._setString(3, value)

    def _initialize(self):
        super(AdditionalEquipmentSlotModel, self)._initialize()
        self._addViewModelProperty('actionPrices', ListModel())
        self._addBoolProperty('isBtnEnabled', False)
        self._addBoolProperty('isSelected', False)
        self._addStringProperty('disabledTooltip', '')
        self.onSelectedChange = self._addCommand('onSelectedChange')
