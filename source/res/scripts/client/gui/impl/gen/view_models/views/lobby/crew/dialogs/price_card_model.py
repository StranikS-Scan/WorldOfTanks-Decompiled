# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crew/dialogs/price_card_model.py
from enum import Enum
from frameworks.wulf import Array, ViewModel
from gui.impl.gen.view_models.views.dialogs.dialog_template_generic_tooltip_view_model import DialogTemplateGenericTooltipViewModel
from gui.impl.gen.view_models.views.dialogs.sub_views.currency_view_model import CurrencyViewModel
from gui.impl.gen.view_models.views.lobby.crew.common.dynamic_tooltip_model import DynamicTooltipModel
from gui.impl.gen.view_models.views.lobby.crew.dialogs.list_price_model import ListPriceModel

class CardType(Enum):
    DEFAULT = 'default'
    RESET = 'reset'
    RETRAIN = 'retrain'


class CardState(Enum):
    DEFAULT = ''
    DISABLED = 'disabled'
    SELECTED = 'selected'


class PriceCardModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=12, commands=0):
        super(PriceCardModel, self).__init__(properties=properties, commands=commands)

    @property
    def price(self):
        return self._getViewModel(0)

    @staticmethod
    def getPriceType():
        return CurrencyViewModel

    @property
    def priceTooltip(self):
        return self._getViewModel(1)

    @staticmethod
    def getPriceTooltipType():
        return DialogTemplateGenericTooltipViewModel

    @property
    def cardTooltip(self):
        return self._getViewModel(2)

    @staticmethod
    def getCardTooltipType():
        return DynamicTooltipModel

    def getId(self):
        return self._getString(3)

    def setId(self, value):
        self._setString(3, value)

    def getIcon(self):
        return self._getString(4)

    def setIcon(self, value):
        self._setString(4, value)

    def getTitle(self):
        return self._getString(5)

    def setTitle(self, value):
        self._setString(5, value)

    def getCardState(self):
        return CardState(self._getString(6))

    def setCardState(self, value):
        self._setString(6, value.value)

    def getCardType(self):
        return CardType(self._getString(7))

    def setCardType(self, value):
        self._setString(7, value.value)

    def getDescription(self):
        return self._getString(8)

    def setDescription(self, value):
        self._setString(8, value)

    def getKwargs(self):
        return self._getString(9)

    def setKwargs(self, value):
        self._setString(9, value)

    def getSelectedOptionIdx(self):
        return self._getNumber(10)

    def setSelectedOptionIdx(self, value):
        self._setNumber(10, value)

    def getPriceList(self):
        return self._getArray(11)

    def setPriceList(self, value):
        self._setArray(11, value)

    @staticmethod
    def getPriceListType():
        return ListPriceModel

    def _initialize(self):
        super(PriceCardModel, self)._initialize()
        self._addViewModelProperty('price', CurrencyViewModel())
        self._addViewModelProperty('priceTooltip', DialogTemplateGenericTooltipViewModel())
        self._addViewModelProperty('cardTooltip', DynamicTooltipModel())
        self._addStringProperty('id', '')
        self._addStringProperty('icon', '')
        self._addStringProperty('title', '')
        self._addStringProperty('cardState')
        self._addStringProperty('cardType')
        self._addStringProperty('description', '')
        self._addStringProperty('kwargs', '')
        self._addNumberProperty('selectedOptionIdx', -1)
        self._addArrayProperty('priceList', Array())
