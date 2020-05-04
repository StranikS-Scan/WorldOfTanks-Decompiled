# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/secret_event/pack_card_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.secret_event.price_model import PriceModel

class PackCardModel(ViewModel):
    __slots__ = ()
    BEGINNER = 'beginner'
    SPECIALIST = 'specialist'
    MASTER = 'master'

    def __init__(self, properties=5, commands=0):
        super(PackCardModel, self).__init__(properties=properties, commands=commands)

    @property
    def price(self):
        return self._getViewModel(0)

    def getId(self):
        return self._getString(1)

    def setId(self, value):
        self._setString(1, value)

    def getBuyCount(self):
        return self._getNumber(2)

    def setBuyCount(self, value):
        self._setNumber(2, value)

    def getOrderModifier(self):
        return self._getNumber(3)

    def setOrderModifier(self, value):
        self._setNumber(3, value)

    def getType(self):
        return self._getString(4)

    def setType(self, value):
        self._setString(4, value)

    def _initialize(self):
        super(PackCardModel, self)._initialize()
        self._addViewModelProperty('price', PriceModel())
        self._addStringProperty('id', '')
        self._addNumberProperty('buyCount', 0)
        self._addNumberProperty('orderModifier', 0)
        self._addStringProperty('type', '')
