# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/exchange/exchange_gold_window.py
import logging
from gui.shared.utils.decorators import adisp_process
from exchange.personal_discounts_constants import EXCHANGE_RATE_GOLD_NAME
from frameworks.wulf import ViewSettings
from gui.impl.gen.view_models.views.lobby.exchange.exchange_rate_gold_model import ExchangeRateGoldModel
from gui.impl.lobby.exchange.base_exchange_window import BaseExchangeWindow
from gui.shared.gui_items.processors.common import GoldToCreditsExchanger
_logger = logging.getLogger(__name__)

class ExchangeGoldView(BaseExchangeWindow):
    __slots__ = ()

    def __init__(self, layoutID, ctx=None, *args, **kwargs):
        settings = ViewSettings(layoutID, model=ExchangeRateGoldModel(), args=args, kwargs=kwargs)
        super(ExchangeGoldView, self).__init__(settings, exchangeRateType=EXCHANGE_RATE_GOLD_NAME, ctx=ctx)

    @property
    def viewModel(self):
        return self.getViewModel()

    @adisp_process('transferMoney')
    def _onExchange(self, data):
        gold = data.get('gold', 0)
        if gold < 1:
            _logger.debug("Parameter 'gold' is missed for gold to silver exchange")
            return
        result = yield GoldToCreditsExchanger(gold).request()
        self._processResult(result, gold)
