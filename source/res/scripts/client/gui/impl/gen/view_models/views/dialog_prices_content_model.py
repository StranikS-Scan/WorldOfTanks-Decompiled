# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/dialog_prices_content_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.value_price import ValuePrice

class DialogPricesContentModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(DialogPricesContentModel, self).__init__(properties=properties, commands=commands)

    @property
    def valueMain(self):
        return self._getViewModel(0)

    @staticmethod
    def getValueMainType():
        return ValuePrice

    @property
    def valueAdditional(self):
        return self._getViewModel(1)

    @staticmethod
    def getValueAdditionalType():
        return ValuePrice

    def getTooltipId(self):
        return self._getNumber(2)

    def setTooltipId(self, value):
        self._setNumber(2, value)

    def getHasAdditionalCost(self):
        return self._getBool(3)

    def setHasAdditionalCost(self, value):
        self._setBool(3, value)

    def _initialize(self):
        super(DialogPricesContentModel, self)._initialize()
        self._addViewModelProperty('valueMain', ValuePrice())
        self._addViewModelProperty('valueAdditional', ValuePrice())
        self._addNumberProperty('tooltipId', 0)
        self._addBoolProperty('hasAdditionalCost', False)
