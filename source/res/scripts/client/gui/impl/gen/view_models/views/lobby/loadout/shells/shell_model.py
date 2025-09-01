# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/loadout/shells/shell_model.py
from frameworks.wulf import Array, ViewModel
from gui.impl.gen.view_models.common.price_item_model import PriceItemModel
from gui.impl.gen.view_models.common.price_model import PriceModel
from gui.impl.gen.view_models.views.lobby.tank_setup.sub_views.shell_specification_model import ShellSpecificationModel

class ShellModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=16, commands=0):
        super(ShellModel, self).__init__(properties=properties, commands=commands)

    @property
    def totalPrice(self):
        return self._getViewModel(0)

    @staticmethod
    def getTotalPriceType():
        return PriceModel

    @property
    def price(self):
        return self._getViewModel(1)

    @staticmethod
    def getPriceType():
        return PriceModel

    @property
    def itemPrice(self):
        return self._getViewModel(2)

    @staticmethod
    def getItemPriceType():
        return PriceItemModel

    def getIntCD(self):
        return self._getNumber(3)

    def setIntCD(self, value):
        self._setNumber(3, value)

    def getInDepotCount(self):
        return self._getNumber(4)

    def setInDepotCount(self, value):
        self._setNumber(4, value)

    def getItemsCount(self):
        return self._getNumber(5)

    def setItemsCount(self, value):
        self._setNumber(5, value)

    def getValue(self):
        return self._getNumber(6)

    def setValue(self, value):
        self._setNumber(6, value)

    def getCount(self):
        return self._getNumber(7)

    def setCount(self, value):
        self._setNumber(7, value)

    def getDelta(self):
        return self._getNumber(8)

    def setDelta(self, value):
        self._setNumber(8, value)

    def getType(self):
        return self._getString(9)

    def setType(self, value):
        self._setString(9, value)

    def getBuyCount(self):
        return self._getNumber(10)

    def setBuyCount(self, value):
        self._setNumber(10, value)

    def getItemInstalledSetupIdx(self):
        return self._getNumber(11)

    def setItemInstalledSetupIdx(self, value):
        self._setNumber(11, value)

    def getIsMounted(self):
        return self._getBool(12)

    def setIsMounted(self, value):
        self._setBool(12, value)

    def getIsMountedMoreThanOne(self):
        return self._getBool(13)

    def setIsMountedMoreThanOne(self, value):
        self._setBool(13, value)

    def getKind(self):
        return self._getString(14)

    def setKind(self, value):
        self._setString(14, value)

    def getPropertiesList(self):
        return self._getArray(15)

    def setPropertiesList(self, value):
        self._setArray(15, value)

    @staticmethod
    def getPropertiesListType():
        return ShellSpecificationModel

    def _initialize(self):
        super(ShellModel, self)._initialize()
        self._addViewModelProperty('totalPrice', PriceModel())
        self._addViewModelProperty('price', PriceModel())
        self._addViewModelProperty('itemPrice', PriceItemModel())
        self._addNumberProperty('intCD', 0)
        self._addNumberProperty('inDepotCount', 0)
        self._addNumberProperty('itemsCount', 0)
        self._addNumberProperty('value', 0)
        self._addNumberProperty('count', 0)
        self._addNumberProperty('delta', 0)
        self._addStringProperty('type', '')
        self._addNumberProperty('buyCount', 0)
        self._addNumberProperty('itemInstalledSetupIdx', 0)
        self._addBoolProperty('isMounted', False)
        self._addBoolProperty('isMountedMoreThanOne', False)
        self._addStringProperty('kind', '')
        self._addArrayProperty('propertiesList', Array())
