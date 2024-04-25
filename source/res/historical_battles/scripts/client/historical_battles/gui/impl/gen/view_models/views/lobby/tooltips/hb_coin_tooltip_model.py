# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/gen/view_models/views/lobby/tooltips/hb_coin_tooltip_model.py
from frameworks.wulf import ViewModel
from historical_battles.gui.impl.gen.view_models.views.common.hb_coin_model import HbCoinModel

class HbCoinTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(HbCoinTooltipModel, self).__init__(properties=properties, commands=commands)

    @property
    def coin(self):
        return self._getViewModel(0)

    @staticmethod
    def getCoinType():
        return HbCoinModel

    def getInsufficientCoins(self):
        return self._getNumber(1)

    def setInsufficientCoins(self, value):
        self._setNumber(1, value)

    def _initialize(self):
        super(HbCoinTooltipModel, self)._initialize()
        self._addViewModelProperty('coin', HbCoinModel())
        self._addNumberProperty('insufficientCoins', 0)
