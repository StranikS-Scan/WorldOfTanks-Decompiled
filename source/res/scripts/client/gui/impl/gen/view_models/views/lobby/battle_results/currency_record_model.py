# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_results/currency_record_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.battle_results.currency_value_model import CurrencyValueModel

class CurrencyRecordModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(CurrencyRecordModel, self).__init__(properties=properties, commands=commands)

    @property
    def firstValue(self):
        return self._getViewModel(0)

    @staticmethod
    def getFirstValueType():
        return CurrencyValueModel

    @property
    def secondValue(self):
        return self._getViewModel(1)

    @staticmethod
    def getSecondValueType():
        return CurrencyValueModel

    def getLabel(self):
        return self._getResource(2)

    def setLabel(self, value):
        self._setResource(2, value)

    def _initialize(self):
        super(CurrencyRecordModel, self)._initialize()
        self._addViewModelProperty('firstValue', CurrencyValueModel())
        self._addViewModelProperty('secondValue', CurrencyValueModel())
        self._addResourceProperty('label', R.invalid())
