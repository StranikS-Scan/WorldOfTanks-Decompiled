# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/bm2021/tooltips/black_market_info_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.bm2021.tooltips.black_market_info_tooltip_model import BlackMarketInfoTooltipModel
from gui.impl.gen.view_models.views.lobby.bm2021.tooltips.currency_model import CurrencyModel
from gui.impl.pub import ViewImpl
from gui.impl.lobby.loot_box.loot_box_helper import getObtainableVehicles
from items.utils import getItemDescrByCompactDescr

class BlackMarketInfoTooltip(ViewImpl):
    __slots__ = ('__item',)

    def __init__(self, item):
        settings = ViewSettings(R.views.lobby.bm2021.tooltips.BlackMarketInfoTooltip())
        settings.model = BlackMarketInfoTooltipModel()
        super(BlackMarketInfoTooltip, self).__init__(settings)
        self.__item = item

    @property
    def viewModel(self):
        return super(BlackMarketInfoTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        obtainableVehicles = getObtainableVehicles(self.__item)
        rerollAttempts = min(len(obtainableVehicles), self.__item.getReRollCount())
        with self.viewModel.transaction() as vm:
            vm.setSlotsNumber(rerollAttempts)
            vehicleNames = vm.getVehicleList()
            for vehicleCD in self.__item.getBonusVehicles():
                vehicleInfo = getItemDescrByCompactDescr(vehicleCD)
                vehicleNames.addString(vehicleInfo.userString)

            vehicleNames.invalidate()
            prices = vm.getPrices()
            for attemptNum in range(1, rerollAttempts):
                priceType, price = self.__item.getReRollPrice(attemptNum)
                currencyModel = CurrencyModel()
                currencyModel.setType(priceType)
                currencyModel.setAmount(price)
                prices.addViewModel(currencyModel)

            prices.invalidate()
