# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/bm2021/dialogs/black_market_next_open_confirm_dialog_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.stats_model import StatsModel

class BlackMarketNextOpenConfirmDialogModel(ViewModel):
    __slots__ = ('onOpenVehicleList', 'onConfirm', 'onOpenExchange')

    def __init__(self, properties=4, commands=3):
        super(BlackMarketNextOpenConfirmDialogModel, self).__init__(properties=properties, commands=commands)

    @property
    def stats(self):
        return self._getViewModel(0)

    def getEndDate(self):
        return self._getNumber(1)

    def setEndDate(self, value):
        self._setNumber(1, value)

    def getNextOpenPrice(self):
        return self._getNumber(2)

    def setNextOpenPrice(self, value):
        self._setNumber(2, value)

    def getSlotsNumber(self):
        return self._getNumber(3)

    def setSlotsNumber(self, value):
        self._setNumber(3, value)

    def _initialize(self):
        super(BlackMarketNextOpenConfirmDialogModel, self)._initialize()
        self._addViewModelProperty('stats', StatsModel())
        self._addNumberProperty('endDate', 0)
        self._addNumberProperty('nextOpenPrice', 0)
        self._addNumberProperty('slotsNumber', 0)
        self.onOpenVehicleList = self._addCommand('onOpenVehicleList')
        self.onConfirm = self._addCommand('onConfirm')
        self.onOpenExchange = self._addCommand('onOpenExchange')
