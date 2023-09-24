# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crew/dialogs/price_card_model.py
from enum import Enum
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.dialogs.dialog_template_generic_tooltip_view_model import DialogTemplateGenericTooltipViewModel
from gui.impl.gen.view_models.views.dialogs.sub_views.currency_view_model import CurrencyViewModel

class CardType(Enum):
    DEFAULT = 'default'
    RESET = 'reset'
    RETRAIN = 'retrain'
    RECRUIT = 'recruit'


class CardState(Enum):
    DEFAULT = ''
    DISABLED = 'disabled'
    SELECTED = 'selected'


class PriceCardModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=9, commands=0):
        super(PriceCardModel, self).__init__(properties=properties, commands=commands)

    @property
    def price(self):
        return self._getViewModel(0)

    @staticmethod
    def getPriceType():
        return CurrencyViewModel

    @property
    def tooltip(self):
        return self._getViewModel(1)

    @staticmethod
    def getTooltipType():
        return DialogTemplateGenericTooltipViewModel

    def getId(self):
        return self._getString(2)

    def setId(self, value):
        self._setString(2, value)

    def getIcon(self):
        return self._getString(3)

    def setIcon(self, value):
        self._setString(3, value)

    def getTitle(self):
        return self._getString(4)

    def setTitle(self, value):
        self._setString(4, value)

    def getCardState(self):
        return CardState(self._getString(5))

    def setCardState(self, value):
        self._setString(5, value.value)

    def getCardType(self):
        return CardType(self._getString(6))

    def setCardType(self, value):
        self._setString(6, value.value)

    def getDescription(self):
        return self._getString(7)

    def setDescription(self, value):
        self._setString(7, value)

    def getKwargs(self):
        return self._getString(8)

    def setKwargs(self, value):
        self._setString(8, value)

    def _initialize(self):
        super(PriceCardModel, self)._initialize()
        self._addViewModelProperty('price', CurrencyViewModel())
        self._addViewModelProperty('tooltip', DialogTemplateGenericTooltipViewModel())
        self._addStringProperty('id', '')
        self._addStringProperty('icon', '')
        self._addStringProperty('title', '')
        self._addStringProperty('cardState')
        self._addStringProperty('cardType')
        self._addStringProperty('description', '')
        self._addStringProperty('kwargs', '')
