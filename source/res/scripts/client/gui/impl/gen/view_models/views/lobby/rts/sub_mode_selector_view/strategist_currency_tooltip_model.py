# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/rts/sub_mode_selector_view/strategist_currency_tooltip_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.rts.rts_currency_view_model import RtsCurrencyViewModel

class StrategistCurrencyTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(StrategistCurrencyTooltipModel, self).__init__(properties=properties, commands=commands)

    @property
    def currency(self):
        return self._getViewModel(0)

    def getDescription(self):
        return self._getString(1)

    def setDescription(self, value):
        self._setString(1, value)

    def getInstructions(self):
        return self._getString(2)

    def setInstructions(self, value):
        self._setString(2, value)

    def getExchangeText(self):
        return self._getString(3)

    def setExchangeText(self, value):
        self._setString(3, value)

    def _initialize(self):
        super(StrategistCurrencyTooltipModel, self)._initialize()
        self._addViewModelProperty('currency', RtsCurrencyViewModel())
        self._addStringProperty('description', '')
        self._addStringProperty('instructions', '')
        self._addStringProperty('exchangeText', '')
