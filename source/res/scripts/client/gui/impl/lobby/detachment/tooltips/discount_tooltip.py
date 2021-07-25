# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/detachment/tooltips/discount_tooltip.py
import typing
from frameworks.wulf import View, ViewSettings
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.detachment.tooltips.discount_tooltip_model import DiscountTooltipModel
from helpers.dependency import descriptor
from skeletons.gui.shared import IItemsCache
from uilogging.detachment.loggers import DynamicGroupTooltipLogger
if typing.TYPE_CHECKING:
    from gui.shared.gui_items.gui_item_economics import ItemPrice

class DiscountTooltip(View):
    __slots__ = ('__itemPrice', '__info')
    __itemsCache = descriptor(IItemsCache)
    uiLogger = DynamicGroupTooltipLogger()

    def __init__(self, itemPrice, info=None):
        settings = ViewSettings(R.views.lobby.detachment.tooltips.DiscountTooltip())
        settings.model = DiscountTooltipModel()
        super(DiscountTooltip, self).__init__(settings)
        self.__itemPrice = itemPrice
        self.__info = info

    def _initialize(self):
        super(DiscountTooltip, self)._initialize()
        self.uiLogger.tooltipOpened()
        g_clientUpdateManager.addMoneyCallback(self._onMoneyUpdate)

    def _finalize(self):
        self.uiLogger.tooltipClosed(self.__class__.__name__)
        self.uiLogger.reset()
        g_clientUpdateManager.removeObjectCallbacks(self)
        super(DiscountTooltip, self)._finalize()

    def _onLoading(self):
        vm = self.getViewModel()
        if self.__info:
            vm.setInfo(self.__info)
        currency = self.__itemPrice.getCurrency()
        vm.setType(currency)
        vm.setCurrentValue(int(self.__itemPrice.price.get(currency)))
        vm.setDefaultValue(int(self.__itemPrice.defPrice.get(currency)))
        self.__updateIsEnough(vm)

    def _onMoneyUpdate(self, _):
        with self.getViewModel().transaction() as vm:
            self.__updateIsEnough(vm)

    def __updateIsEnough(self, vm):
        money = self.__itemsCache.items.stats.money
        itemPrice = self.__itemPrice
        vm.setIsCurrentEnough(not money.getShortage(itemPrice.price))
        vm.setIsDefaultEnough(not money.getShortage(itemPrice.defPrice))
