# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/dialogs/buy_block_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.detachment.common.price_model import PriceModel

class BuyBlockModel(ViewModel):
    __slots__ = ()
    FREE = 'free'
    SCHOOL = 'school'
    ACADEMY = 'academy'
    TRAINING = 'training'

    def __init__(self, properties=4, commands=0):
        super(BuyBlockModel, self).__init__(properties=properties, commands=commands)

    @property
    def priceModel(self):
        return self._getViewModel(0)

    def getType(self):
        return self._getString(1)

    def setType(self, value):
        self._setString(1, value)

    def getPercentExp(self):
        return self._getNumber(2)

    def setPercentExp(self, value):
        self._setNumber(2, value)

    def getNegativePercentExp(self):
        return self._getNumber(3)

    def setNegativePercentExp(self, value):
        self._setNumber(3, value)

    def _initialize(self):
        super(BuyBlockModel, self)._initialize()
        self._addViewModelProperty('priceModel', PriceModel())
        self._addStringProperty('type', '')
        self._addNumberProperty('percentExp', 0)
        self._addNumberProperty('negativePercentExp', 0)
