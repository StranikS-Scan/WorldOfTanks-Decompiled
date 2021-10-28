# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/halloween/shop_bundle_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.halloween.price_model import PriceModel
from gui.impl.gen.view_models.views.lobby.halloween.shop_bonus_group_model import ShopBonusGroupModel

class ShopBundleModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=6, commands=0):
        super(ShopBundleModel, self).__init__(properties=properties, commands=commands)

    @property
    def price(self):
        return self._getViewModel(0)

    def getId(self):
        return self._getString(1)

    def setId(self, value):
        self._setString(1, value)

    def getAmount(self):
        return self._getNumber(2)

    def setAmount(self, value):
        self._setNumber(2, value)

    def getCountdownValue(self):
        return self._getNumber(3)

    def setCountdownValue(self, value):
        self._setNumber(3, value)

    def getShowAnimation(self):
        return self._getBool(4)

    def setShowAnimation(self, value):
        self._setBool(4, value)

    def getBonusGroups(self):
        return self._getArray(5)

    def setBonusGroups(self, value):
        self._setArray(5, value)

    def _initialize(self):
        super(ShopBundleModel, self)._initialize()
        self._addViewModelProperty('price', PriceModel())
        self._addStringProperty('id', '')
        self._addNumberProperty('amount', 0)
        self._addNumberProperty('countdownValue', 0)
        self._addBoolProperty('showAnimation', False)
        self._addArrayProperty('bonusGroups', Array())
