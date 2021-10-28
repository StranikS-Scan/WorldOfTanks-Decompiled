# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/halloween/base_customization_item_view_model.py
from enum import Enum
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.simple_price_model import SimplePriceModel

class CustomizationTypeEnum(Enum):
    DECAL = 'decal'
    STYLE = 'style'


class BaseCustomizationItemViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=6, commands=0):
        super(BaseCustomizationItemViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def price(self):
        return self._getViewModel(0)

    def getId(self):
        return self._getNumber(1)

    def setId(self, value):
        self._setNumber(1, value)

    def getName(self):
        return self._getString(2)

    def setName(self, value):
        self._setString(2, value)

    def getIcon(self):
        return self._getString(3)

    def setIcon(self, value):
        self._setString(3, value)

    def getType(self):
        return CustomizationTypeEnum(self._getString(4))

    def setType(self, value):
        self._setString(4, value.value)

    def getIsBought(self):
        return self._getBool(5)

    def setIsBought(self, value):
        self._setBool(5, value)

    def _initialize(self):
        super(BaseCustomizationItemViewModel, self)._initialize()
        self._addViewModelProperty('price', SimplePriceModel())
        self._addNumberProperty('id', 0)
        self._addStringProperty('name', '')
        self._addStringProperty('icon', '')
        self._addStringProperty('type')
        self._addBoolProperty('isBought', False)
