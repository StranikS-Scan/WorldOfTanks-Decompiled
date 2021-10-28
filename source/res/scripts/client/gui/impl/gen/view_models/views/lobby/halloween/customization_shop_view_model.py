# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/halloween/customization_shop_view_model.py
from enum import Enum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.simple_price_model import SimplePriceModel
from gui.impl.gen.view_models.views.lobby.halloween.customization_item_view_model import CustomizationItemViewModel
from gui.impl.gen.view_models.views.lobby.halloween.selected_item_view_model import SelectedItemViewModel
from gui.impl.gen.view_models.views.lobby.halloween.stepper_view_model import StepperViewModel

class BtnTypeEnum(Enum):
    TO_WAREHOUSE = 'toWarehouse'
    TO_CUSTOMIZATION = 'toCustomization'
    BUY_STYLE = 'buyStyle'
    BUY_DECAL = 'buyDecal'


class CustomizationShopViewModel(ViewModel):
    __slots__ = ('onClose', 'onBtnClick', 'onBack', 'onMoveSpace', 'onOverScene', 'onSelectedChange')

    def __init__(self, properties=4, commands=6):
        super(CustomizationShopViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def stepper(self):
        return self._getViewModel(0)

    @property
    def selectedItem(self):
        return self._getViewModel(1)

    @property
    def price(self):
        return self._getViewModel(2)

    def getCustomizationItems(self):
        return self._getArray(3)

    def setCustomizationItems(self, value):
        self._setArray(3, value)

    def _initialize(self):
        super(CustomizationShopViewModel, self)._initialize()
        self._addViewModelProperty('stepper', StepperViewModel())
        self._addViewModelProperty('selectedItem', SelectedItemViewModel())
        self._addViewModelProperty('price', SimplePriceModel())
        self._addArrayProperty('customizationItems', Array())
        self.onClose = self._addCommand('onClose')
        self.onBtnClick = self._addCommand('onBtnClick')
        self.onBack = self._addCommand('onBack')
        self.onMoveSpace = self._addCommand('onMoveSpace')
        self.onOverScene = self._addCommand('onOverScene')
        self.onSelectedChange = self._addCommand('onSelectedChange')
