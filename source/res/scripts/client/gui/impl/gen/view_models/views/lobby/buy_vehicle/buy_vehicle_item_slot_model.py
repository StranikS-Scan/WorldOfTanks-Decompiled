# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/buy_vehicle/buy_vehicle_item_slot_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.ui_kit.action_price_model import ActionPriceModel
from gui.impl.gen.view_models.ui_kit.list_model import ListModel

class BuyVehicleItemSlotModel(ViewModel):
    __slots__ = ('onSelectedChange',)

    def __init__(self, properties=4, commands=1):
        super(BuyVehicleItemSlotModel, self).__init__(properties=properties, commands=commands)

    @property
    def actionPrices(self):
        return self._getViewModel(0)

    def getIsEnabled(self):
        return self._getBool(1)

    def setIsEnabled(self, value):
        self._setBool(1, value)

    def getIsSelected(self):
        return self._getBool(2)

    def setIsSelected(self, value):
        self._setBool(2, value)

    def getTooltipId(self):
        return self._getString(3)

    def setTooltipId(self, value):
        self._setString(3, value)

    def _initialize(self):
        super(BuyVehicleItemSlotModel, self)._initialize()
        self._addViewModelProperty('actionPrices', ListModel())
        self._addBoolProperty('isEnabled', False)
        self._addBoolProperty('isSelected', False)
        self._addStringProperty('tooltipId', '')
        self.onSelectedChange = self._addCommand('onSelectedChange')
