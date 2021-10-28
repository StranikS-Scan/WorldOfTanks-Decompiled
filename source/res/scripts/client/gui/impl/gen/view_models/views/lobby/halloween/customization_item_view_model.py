# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/halloween/customization_item_view_model.py
from gui.impl.gen.view_models.common.simple_price_model import SimplePriceModel
from gui.impl.gen.view_models.views.lobby.halloween.base_customization_item_view_model import BaseCustomizationItemViewModel

class CustomizationItemViewModel(BaseCustomizationItemViewModel):
    __slots__ = ()

    def __init__(self, properties=10, commands=0):
        super(CustomizationItemViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def price(self):
        return self._getViewModel(6)

    def getIsHistorical(self):
        return self._getBool(7)

    def setIsHistorical(self, value):
        self._setBool(7, value)

    def getWarehouseCount(self):
        return self._getNumber(8)

    def setWarehouseCount(self, value):
        self._setNumber(8, value)

    def getDecalSize(self):
        return self._getNumber(9)

    def setDecalSize(self, value):
        self._setNumber(9, value)

    def _initialize(self):
        super(CustomizationItemViewModel, self)._initialize()
        self._addViewModelProperty('price', SimplePriceModel())
        self._addBoolProperty('isHistorical', False)
        self._addNumberProperty('warehouseCount', 0)
        self._addNumberProperty('decalSize', 0)
