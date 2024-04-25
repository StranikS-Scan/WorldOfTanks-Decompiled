# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/dialogs/sub_views/common/hb_multi_price.py
import logging
import typing
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from helpers import dependency
from historical_battles.gui.impl.gen.view_models.views.common.multi_price_view_model import MultiPriceViewModel
from historical_battles.gui.impl.gen.view_models.views.common.simple_price_view_model import SimplePriceViewModel
from historical_battles.gui.impl.lobby.shop_views.utils import getCurrentCurrencyCount
from historical_battles.skeletons.gui.game_event_controller import IGameEventController
if typing.TYPE_CHECKING:
    from gui.impl.gen_utils import DynAccessor
_logger = logging.getLogger(__name__)

class HBMultiPrice(ViewImpl):
    _VIEW_MODEL = MultiPriceViewModel
    _LAYOUT_DYN_ACC = R.invalid
    _gameEventController = dependency.descriptor(IGameEventController)

    def __init__(self, prices=None, discounts=None):
        settings = ViewSettings(layoutID=self._LAYOUT_DYN_ACC())
        settings.model = self._VIEW_MODEL()
        super(HBMultiPrice, self).__init__(settings)
        self._prices = prices
        self._discounts = discounts
        self._count = 1

    @property
    def viewModel(self):
        return self.getViewModel()

    @property
    def count(self):
        return self._count

    def setCount(self, value):
        if self._count != value:
            self._count = value
            with self.viewModel.transaction():
                self._fillViewModel()

    def _onLoading(self, *args, **kwargs):
        super(HBMultiPrice, self)._onLoading(*args, **kwargs)
        self._fillViewModel()
        self._gameEventController.coins.onCoinsCountChanged += self._coinsCountChangeHandler

    def _finalize(self):
        self._gameEventController.coins.onCoinsCountChanged -= self._coinsCountChangeHandler
        super(HBMultiPrice, self)._finalize()

    def _coinsCountChangeHandler(self):
        with self.viewModel.transaction():
            self._fillViewModel()

    def _fillViewModel(self):
        priceVMs = self.viewModel.getPrices()
        priceVMs.clear()
        for price in self._prices:
            currencyType, currentCount = getCurrentCurrencyCount(price)
            if currencyType is None:
                _logger.error('Unknown virtual currency = %s', price.currency)
                continue
            priceVM = SimplePriceViewModel()
            priceVM.setType(currencyType)
            amount = self._count * price.amount
            priceVM.setValue(amount)
            isEnough = currentCount - amount >= 0
            priceVM.setIsEnough(isEnough)
            if self._discounts:
                discount = self._discounts.get(price.currency, None)
                priceVM.setIsDiscount(discount is not None)
            else:
                priceVM.setIsDiscount(False)
            priceVMs.addViewModel(priceVM)

        priceVMs.invalidate()
        return
