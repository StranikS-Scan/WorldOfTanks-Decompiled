# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/gen/view_models/views/dialogs/sub_views/exchange_coins_model.py
from frameworks.wulf import ViewModel
from historical_battles.gui.impl.gen.view_models.views.dialogs.sub_views.exchange_coins_side_model import ExchangeCoinsSideModel

class ExchangeCoinsModel(ViewModel):
    __slots__ = ('onStepperValueChanged',)

    def __init__(self, properties=5, commands=1):
        super(ExchangeCoinsModel, self).__init__(properties=properties, commands=commands)

    @property
    def left(self):
        return self._getViewModel(0)

    @staticmethod
    def getLeftType():
        return ExchangeCoinsSideModel

    @property
    def right(self):
        return self._getViewModel(1)

    @staticmethod
    def getRightType():
        return ExchangeCoinsSideModel

    def getStepperMaxValue(self):
        return self._getNumber(2)

    def setStepperMaxValue(self, value):
        self._setNumber(2, value)

    def getStepperMinValue(self):
        return self._getNumber(3)

    def setStepperMinValue(self, value):
        self._setNumber(3, value)

    def getStepperValue(self):
        return self._getNumber(4)

    def setStepperValue(self, value):
        self._setNumber(4, value)

    def _initialize(self):
        super(ExchangeCoinsModel, self)._initialize()
        self._addViewModelProperty('left', ExchangeCoinsSideModel())
        self._addViewModelProperty('right', ExchangeCoinsSideModel())
        self._addNumberProperty('stepperMaxValue', 0)
        self._addNumberProperty('stepperMinValue', 0)
        self._addNumberProperty('stepperValue', 0)
        self.onStepperValueChanged = self._addCommand('onStepperValueChanged')
