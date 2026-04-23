# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/dialogs/sub_views/content/hb_multi_price.py
from gui.impl.gen import R
from historical_battles.gui.impl.dialogs.sub_views.common.hb_multi_price import HBMultiPrice
from historical_battles.gui.impl.gen.view_models.views.dialogs.sub_views.hb_money_price_model import HbMoneyPriceModel

class HBMultiPriceContent(HBMultiPrice):
    _LAYOUT_DYN_ACC = R.views.historical_battles.dialogs.sub_views.content.HBMultiPriceContentView
    _VIEW_MODEL = HbMoneyPriceModel

    @property
    def viewModel(self):
        return self.getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(HBMultiPriceContent, self)._onLoading(*args, **kwargs)
        self.viewModel.setText(R.strings.hb_shop.common.pricePerOne())
