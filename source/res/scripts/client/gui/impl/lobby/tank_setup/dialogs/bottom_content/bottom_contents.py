# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/tank_setup/dialogs/bottom_content/bottom_contents.py
from gui.impl.common.base_sub_model_view import BaseSubModelView
from gui.impl.lobby.tank_setup.configurations.base import BaseDealPanel
from gui.impl.wrappers.user_compound_price_model import BuyPriceModelBuilder
from gui.shared.gui_items.fitting_item import canBuyWithGoldExchange
from gui.shared.gui_items.processors.vehicle import VehicleAutoRepairProcessor
from gui.shared.money import Money
from helpers import dependency
from gui.shared.utils import decorators
from skeletons.gui.shared import IItemsCache

class AmmunitionBuyBottomContent(BaseSubModelView):

    def __init__(self, viewModel, vehicle, items):
        super(AmmunitionBuyBottomContent, self).__init__(viewModel)
        self.__items = items
        self.__vehicle = vehicle

    def onLoading(self, *args, **kwargs):
        super(AmmunitionBuyBottomContent, self).onLoading(*args, **kwargs)
        self.update()

    def update(self):
        super(AmmunitionBuyBottomContent, self).update()
        BaseDealPanel.updateDealPanelPrice(self.__vehicle, self.__items, self._viewModel)


class PriceBottomContent(BaseSubModelView):
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, viewModel, price, defPrice=None):
        super(PriceBottomContent, self).__init__(viewModel)
        self.__price = price
        self.__defPrice = defPrice

    def onLoading(self, *args, **kwargs):
        super(PriceBottomContent, self).onLoading(*args, **kwargs)
        self.update()

    def update(self, price=None, defPrice=None):
        super(PriceBottomContent, self).update()
        self.__price = price if price is not None else self.__price
        self.__defPrice = defPrice if price is not None else self.__defPrice
        with self._viewModel.transaction() as model:
            price = model.getPrice()
            defPrice = model.getDefPrice()
            price.clear()
            defPrice.clear()
            if self.__price:
                BuyPriceModelBuilder.fillPriceModel(priceModel=model, price=self.__price, defPrice=self.__defPrice)
            isEnabled = not self.__price.isDefined() or canBuyWithGoldExchange(self.__price, self.__itemsCache.items.stats.money, self.__itemsCache.items.shop.exchangeRate)
            model.setIsDisabled(not isEnabled)
        return


class NeedRepairBottomContent(PriceBottomContent):

    def __init__(self, viewModel, vehicle):
        self.__vehicle = vehicle
        self.__price = Money(credits=self.__vehicle.repairCost)
        self.__autoRepair = self.__vehicle.isAutoRepair
        super(NeedRepairBottomContent, self).__init__(viewModel, self.__price)

    def _addListeners(self):
        super(NeedRepairBottomContent, self)._addListeners()
        self._viewModel.onAutoRenewalChanged += self.__updateAutoRepair

    def _removeListeners(self):
        self._viewModel.onAutoRenewalChanged -= self.__updateAutoRepair
        super(NeedRepairBottomContent, self)._removeListeners()

    def update(self, price=None, defPrice=None):
        super(NeedRepairBottomContent, self).update(price, defPrice)
        self._viewModel.setIsAutoRenewalEnabled(self.__autoRepair)

    def __updateAutoRepair(self, args):
        repair = args.get('value', self.__autoRepair)
        if repair != self.__autoRepair:
            self.__autoRepair = repair
            self._viewModel.setIsAutoRenewalEnabled(repair)

    @decorators.adisp_process('loadStats')
    def processAutoRepair(self):
        if self.__autoRepair != self.__vehicle.isAutoRepair:
            yield VehicleAutoRepairProcessor(self.__vehicle, self.__autoRepair).request()
