# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/currency_reserves/currency_reserves_view_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.currency_reserves.currency_reserve_model import CurrencyReserveModel

class CurrencyReservesViewModel(ViewModel):
    __slots__ = ('onClose',)

    def __init__(self, properties=3, commands=1):
        super(CurrencyReservesViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def creditReserve(self):
        return self._getViewModel(0)

    @staticmethod
    def getCreditReserveType():
        return CurrencyReserveModel

    @property
    def goldReserve(self):
        return self._getViewModel(1)

    @staticmethod
    def getGoldReserveType():
        return CurrencyReserveModel

    def getTimeToOpen(self):
        return self._getNumber(2)

    def setTimeToOpen(self, value):
        self._setNumber(2, value)

    def _initialize(self):
        super(CurrencyReservesViewModel, self)._initialize()
        self._addViewModelProperty('creditReserve', CurrencyReserveModel())
        self._addViewModelProperty('goldReserve', CurrencyReserveModel())
        self._addNumberProperty('timeToOpen', 0)
        self.onClose = self._addCommand('onClose')
