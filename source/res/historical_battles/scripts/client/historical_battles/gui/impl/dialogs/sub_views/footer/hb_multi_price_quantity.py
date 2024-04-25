# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/dialogs/sub_views/footer/hb_multi_price_quantity.py
from gui.impl.dialogs.dialog_template_focus import IFocusPresenter
from gui.impl.gen import R
from historical_battles.gui.impl.dialogs.sub_views.footer.hb_multi_price import HBMultiPriceFooter
from historical_battles.gui.impl.gen.view_models.views.dialogs.sub_views.hb_money_price_model import HbMoneyPriceModel
from historical_battles.gui.impl.lobby.shop_views.utils import getCurrentCurrencyCount
MAX_BUY = 100

class HBMultiPriceQuantityFooter(HBMultiPriceFooter, IFocusPresenter):
    __slots__ = ()
    _LAYOUT_DYN_ACC = R.views.historical_battles.dialogs.sub_views.footer.HBMultiPriceQuantity
    _VIEW_MODEL = HbMoneyPriceModel
    focusElementCount = 1

    @property
    def viewModel(self):
        return self.getViewModel()

    def updateFocusIndex(self, value):
        self.viewModel.focus.setFocusedIndex(value)
        return value != -1 and self.viewModel.getStepperMaxValue() != 0

    def _onLoading(self, *args, **kwargs):
        super(HBMultiPriceQuantityFooter, self)._onLoading(*args, **kwargs)
        self.viewModel.onStepperValueChanged += self._stepperValueChangeHandler

    def _finalize(self):
        self.viewModel.onStepperValueChanged -= self._stepperValueChangeHandler
        super(HBMultiPriceQuantityFooter, self)._finalize()

    def _stepperValueChangeHandler(self, args):
        value = int(args.get('value', 1))
        self.setCount(value)

    def _fillViewModel(self):
        super(HBMultiPriceQuantityFooter, self)._fillViewModel()
        self._setStepperMaxValue()

    def _setStepperMaxValue(self):
        stepperMaxValue = MAX_BUY
        for price in self._prices:
            currencyType, currentCount = getCurrentCurrencyCount(price)
            if currencyType is None:
                continue
            stepperMaxValue = min(stepperMaxValue, int(currentCount / price.amount))

        self.viewModel.setStepperMaxValue(stepperMaxValue)
        return
