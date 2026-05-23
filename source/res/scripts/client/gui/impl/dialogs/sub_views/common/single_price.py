# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/dialogs/sub_views/common/single_price.py
import typing
from frameworks.wulf import ViewSettings
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl.backport.backport_tooltip import createBackportTooltipContent
from gui.impl.dialogs.dialog_template_utils import toString
from gui.impl.gen import R
from gui.impl.gen.view_models.views.dialogs.dialog_template_generic_tooltip_view_model import TooltipType
from gui.impl.gen.view_models.views.dialogs.sub_views.currency_view_model import CurrencyType, CurrencySize
from gui.impl.gen.view_models.views.dialogs.sub_views.single_price_view_model import SinglePriceViewModel
from gui.impl.pub import ViewImpl
from helpers import dependency
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from typing import Optional, Union
    from gui.shared.gui_items.gui_item_economics import ItemPrice
    from gui.impl.gen_utils import DynAccessor
    from gui.shared.money import Money

def _convertMoneyToTuple(money):
    return (money.credits, money.gold, money.crystal)


class SinglePrice(ViewImpl):
    __slots__ = ('__text', '__price', '__size', '__currencyTypeClass')
    LAYOUT_DYN_ACCESSOR = R.views.dialogs.sub_views.common.SinglePrice
    _itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, text, price, size=CurrencySize.SMALL, layoutID=None, currencyTypeClass=CurrencyType):
        settings = ViewSettings(layoutID or self.LAYOUT_DYN_ACCESSOR())
        settings.model = SinglePriceViewModel()
        super(SinglePrice, self).__init__(settings)
        self.__text = text
        self.__price = price
        self.__size = size
        self.__currencyTypeClass = currencyTypeClass

    @property
    def viewModel(self):
        return self.getViewModel()

    def updatePrice(self, newPrice):
        self.__price = newPrice
        self.__updateViewModel()

    def setSize(self, newSize):
        self.__size = newSize
        self.__updateViewModel()

    def setText(self, newText):
        self.__text = newText
        self.__updateViewModel()

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.dialogs.common.DialogTemplateGenericTooltip():
            if self.__price.isActionPrice():
                specialAlias = (None,
                 None,
                 _convertMoneyToTuple(self.__price.price),
                 _convertMoneyToTuple(self.__price.defPrice),
                 True,
                 False,
                 None,
                 True)
                return createBackportTooltipContent(specialAlias=TOOLTIPS_CONSTANTS.ACTION_PRICE, specialArgs=specialAlias)
            shortage = self._itemsCache.items.stats.money.getShortage(self.__price.price)
            if bool(shortage):
                currency = shortage.getCurrency()
                return createBackportTooltipContent(TOOLTIPS_CONSTANTS.NOT_ENOUGH_MONEY, (shortage.get(currency), currency))
        return super(SinglePrice, self).createToolTipContent(event, contentID)

    def _onLoading(self, *args, **kwargs):
        super(SinglePrice, self)._onLoading(*args, **kwargs)
        g_clientUpdateManager.addMoneyCallback(self._moneyChangeHandler)
        self.__updateViewModel()

    def _finalize(self):
        super(SinglePrice, self)._finalize()
        g_clientUpdateManager.removeObjectCallbacks(self)

    def _moneyChangeHandler(self, *_):
        self.__updateViewModel()

    def __updateViewModel(self):
        with self.viewModel.transaction() as vm:
            vm.setText(toString(self.__text))
            isDiscount = self.__price.isActionPrice()
            isEnough = bool(self._itemsCache.items.stats.money.getShortage(self.__price.price))
            vm.tooltip.setType(TooltipType.BACKPORT if isDiscount or isEnough else TooltipType.ABSENT)
            cost = vm.cost
            currency = self.__price.getCurrency()
            cost.setType(self.__currencyTypeClass(currency))
            cost.setSize(self.__size)
            cost.setValue(int(self.__price.price.get(currency)))
            cost.setIsDiscount(isDiscount)
            cost.setDiscountValue(self.__price.getActionPrc())
            cost.setIsEnough(not isEnough)
