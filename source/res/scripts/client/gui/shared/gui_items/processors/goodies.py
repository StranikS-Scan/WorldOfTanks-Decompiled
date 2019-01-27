# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/processors/goodies.py
import logging
import BigWorld
import AccountCommands
from gui.SystemMessages import SM_TYPE, CURRENCY_TO_SM_TYPE
from gui.shared.formatters import formatPrice
from gui.shared.gui_items.processors import Processor, makeI18nError, makeI18nSuccess, plugins as proc_plugs
from gui.shared.gui_items.gui_item_economics import ItemPrice
from gui.shared.money import Currency
from gui.shared.utils import code2str
_logger = logging.getLogger(__name__)

class BoosterProcessor(Processor):

    def __init__(self, booster, opType, plugins=None):
        super(BoosterProcessor, self).__init__(plugins or [])
        self.booster = booster
        self.opType = opType

    def _response(self, code, callback, ctx=None, errStr=''):
        if code < 0:
            _logger.error("Server responses an error [%s] while process %s '%s'", code2str(code), self.booster.boosterGuiType, str(self.booster))
            return callback(self._errorHandler(code, ctx=ctx, errStr=errStr))
        return callback(self._successHandler(code, ctx=ctx))

    def _getMsgCtx(self):
        raise NotImplementedError

    def _formMessage(self, msg):
        _logger.debug('Generating response for BoosterProcessor: %s %s', self.opType, msg)
        return 'booster_{opType}/{msg}'.format(opType=self.opType, msg=msg)

    def _errorHandler(self, code, errStr='', ctx=None):
        if not errStr:
            errStr = 'server_error' if code != AccountCommands.RES_CENTER_DISCONNECTED else 'server_error_centerDown'
        return makeI18nError(self._formMessage(errStr), defaultSysMsgKey=self._formMessage('server_error'), auxData={'errStr': errStr}, **self._getMsgCtx())


class BoosterActivator(BoosterProcessor):

    def __init__(self, booster):
        super(BoosterActivator, self).__init__(booster, 'activate', [proc_plugs.BoosterActivateValidator(booster)])

    def _getMsgCtx(self):
        return {'boosterName': self.booster.userName,
         'time': self.booster.getEffectTimeStr()}

    def _successHandler(self, code, ctx=None):
        return makeI18nSuccess(self._formMessage('success'), type=SM_TYPE.Information, **self._getMsgCtx())

    def _request(self, callback):
        _logger.debug('Make server request to activate booster, %s, %s', self.booster.boosterID, self.booster.userName)
        BigWorld.player().activateGoodie([self.booster.boosterID], lambda code, errStr: self._response(code, callback, errStr=errStr))


class BoosterTradeProcessor(BoosterProcessor):

    def __init__(self, booster, count, opType, plugs=None):
        super(BoosterTradeProcessor, self).__init__(booster, opType, plugs or [])
        self.count = count

    def _getMsgCtx(self):
        return {'boosterName': self.booster.userName,
         'count': BigWorld.wg_getIntegralFormat(int(self.count)),
         'money': formatPrice(self._getOpPrice().price)}

    def _getOpPrice(self):
        raise NotImplementedError


class BoosterBuyer(BoosterTradeProcessor):

    def __init__(self, booster, count, currency):
        super(BoosterBuyer, self).__init__(booster, count, 'buy')
        self.buyCurrency = currency
        self.addPlugins((proc_plugs.MoneyValidator(self._getOpPrice().price),))

    def _getOpPrice(self):
        minItemPrice = self.booster.buyPrices.getMinItemPriceByCurrency(self.buyCurrency)
        if minItemPrice is None:
            _logger.error('Attempt to buy booster %s for the invalid currency %s.', self.booster, self.buyCurrency)
            minItemPrice = self.booster.buyPrices.itemPrice
        return minItemPrice * self.count

    def _successHandler(self, code, ctx=None):
        sysMsgType = CURRENCY_TO_SM_TYPE.get(self.buyCurrency, SM_TYPE.PurchaseForCredits)
        return makeI18nSuccess(sysMsgKey=self._formMessage('success'), type=sysMsgType, **self._getMsgCtx())

    def _request(self, callback):
        _logger.debug('Make server request to buy booster: %s, %s, %s, %s', self.booster.boosterID, self.booster.buyPrices, self.count, self.buyCurrency)
        BigWorld.player().shop.buyGoodie(self.booster.boosterID, self.count, self.buyCurrency == Currency.GOLD, lambda code: self._response(code, callback))


class BoosterSeller(BoosterTradeProcessor):

    def __init__(self, booster, count):
        super(BoosterSeller, self).__init__(booster, count, 'sell')

    def _getOpPrice(self):
        sellPrice = self.booster.sellPrices.itemPrice
        if not sellPrice:
            _logger.error('Attempt to sell booster %s that is not sold.', self.booster)
        return sellPrice * self.count

    def _successHandler(self, code, ctx=None):
        return makeI18nSuccess(sysMsgKey=self._formMessage('success'), type=SM_TYPE.Selling, **self._getMsgCtx())

    def _request(self, callback):
        _logger.debug('Make server request to sell booster: %s, %s', self.booster, self.count)
        BigWorld.player().inventory.sellGoodie(self.booster.boosterID, self.count, lambda code: self._response(code, callback))
