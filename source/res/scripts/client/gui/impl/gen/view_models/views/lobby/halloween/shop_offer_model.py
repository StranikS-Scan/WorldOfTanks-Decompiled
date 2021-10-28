# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/halloween/shop_offer_model.py
from enum import Enum
from frameworks.wulf import Array
from gui.impl.gen import R
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.halloween.shop_bonus_model import ShopBonusModel

class OfferTypeEnum(Enum):
    PREMIUM = 'premium'
    KEYS = 'keys'
    RENTAL_VEHICLES = 'rentalVehicles'
    BONUSES = 'bonuses'


class ShopOfferModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=5, commands=0):
        super(ShopOfferModel, self).__init__(properties=properties, commands=commands)

    def getType(self):
        return OfferTypeEnum(self._getString(0))

    def setType(self, value):
        self._setString(0, value.value)

    def getIcon(self):
        return self._getResource(1)

    def setIcon(self, value):
        self._setResource(1, value)

    def getAmount(self):
        return self._getNumber(2)

    def setAmount(self, value):
        self._setNumber(2, value)

    def getBonuses(self):
        return self._getArray(3)

    def setBonuses(self, value):
        self._setArray(3, value)

    def getVehicles(self):
        return self._getArray(4)

    def setVehicles(self, value):
        self._setArray(4, value)

    def _initialize(self):
        super(ShopOfferModel, self)._initialize()
        self._addStringProperty('type')
        self._addResourceProperty('icon', R.invalid())
        self._addNumberProperty('amount', 0)
        self._addArrayProperty('bonuses', Array())
        self._addArrayProperty('vehicles', Array())
