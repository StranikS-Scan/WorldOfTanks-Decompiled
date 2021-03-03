# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/processors/market_items.py
import logging
import BigWorld
from gui import SystemMessages
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.gui_items.processors import Processor, makeI18nError
from gui.shared.money import Money
from gui.shared.formatters import moneyWithIcon
from messenger import g_settings
_logger = logging.getLogger(__name__)

class MarketItemNextOpenProcessor(Processor):

    def __init__(self, marketItem):
        super(MarketItemNextOpenProcessor, self).__init__()
        self.__marketItem = marketItem

    def _errorHandler(self, code, errStr='', ctx=None):
        defaultKey = 'marketItems/nextOpen/server_error'
        return makeI18nError('/'.join((defaultKey, errStr)), defaultKey)

    def _successHandler(self, code, ctx=None):
        reRollCount = ctx.get('reRollCount', 0)
        if reRollCount > 1:
            priceType, price = self.__marketItem.getReRollPrice(reRollCount - 1)
            kwargs = {priceType: price}
            fmt = g_settings.htmlTemplates.format('blackMarketItemNextOpenPrice', ctx={'currency': moneyWithIcon(Money(**kwargs))})
            msgType = SystemMessages.SM_TYPE.BlackMarketItemNextOpen
        else:
            fmt = backport.text(R.strings.messenger.serviceChannelMessages.blackMarketItemFirstOpen.text())
            msgType = SystemMessages.SM_TYPE.Information
        if fmt is not None:
            SystemMessages.pushMessage(fmt, msgType)
        return super(MarketItemNextOpenProcessor, self)._successHandler(code, ctx)

    def _request(self, callback):
        marketItemID = self.__marketItem.getID()
        _logger.debug('Make server request to next open market item by id: %r', marketItemID)
        BigWorld.player().tokens.marketItemNext(marketItemID, lambda code, errStr, ext: self._response(code, callback, ctx=ext, errStr=errStr))


class MarketItemNextOpenRecordsProcessor(Processor):

    def _errorHandler(self, code, errStr='', ctx=None):
        defaultKey = 'marketItems/nextOpenRecords/server_error'
        return makeI18nError('/'.join((defaultKey, errStr)), defaultKey)

    def _request(self, callback):
        BigWorld.player().tokens.getMarketItemNextRecords(lambda code, errStr, ext: self._response(code, callback, ctx=ext, errStr=errStr))
