# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/common/dialog_with_exchange.py
from gui.impl.gen.view_models.common.exchange_panel_model import ExchangePanelModel
from gui.impl.gen.view_models.common.price_item_model import PriceItemModel
from gui.impl.gen.view_models.windows.full_screen_dialog_window_model import FullScreenDialogWindowModel

class DialogWithExchange(FullScreenDialogWindowModel):
    __slots__ = ()

    def __init__(self, properties=14, commands=3):
        super(DialogWithExchange, self).__init__(properties=properties, commands=commands)

    @property
    def exchangePanel(self):
        return self._getViewModel(10)

    @property
    def lacksMoney(self):
        return self._getViewModel(11)

    def getBottomContentType(self):
        return self._getString(12)

    def setBottomContentType(self, value):
        self._setString(12, value)

    def getExchangeState(self):
        return self._getString(13)

    def setExchangeState(self, value):
        self._setString(13, value)

    def _initialize(self):
        super(DialogWithExchange, self)._initialize()
        self._addViewModelProperty('exchangePanel', ExchangePanelModel())
        self._addViewModelProperty('lacksMoney', PriceItemModel())
        self._addStringProperty('bottomContentType', '')
        self._addStringProperty('exchangeState', 'default')
