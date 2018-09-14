# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/processors/goodies.py
import BigWorld
import AccountCommands
from debug_utils import LOG_DEBUG, LOG_ERROR
from gui.SystemMessages import SM_TYPE
from gui.shared.formatters import formatPrice
from gui.shared.gui_items.processors import Processor, makeI18nError, makeI18nSuccess, plugins
from gui.shared.money import Money
from gui.shared.utils import code2str

class BoosterProcessor(Processor):

    def __init__(self, booster, opType, plugins=list()):
        super(BoosterProcessor, self).__init__(plugins)
        self.booster = booster
        self.opType = opType

    def _response(self, code, callback, ctx=None, errStr=''):
        if code < 0:
            LOG_ERROR("Server responses an error [%s] while process %s '%s'" % (code2str(code), self.booster.boosterGuiType, str(self.booster)))
            return callback(self._errorHandler(code, ctx=ctx, errStr=errStr))
        return callback(self._successHandler(code, ctx=ctx))

    def _getMsgCtx(self):
        raise NotImplemented

    def _formMessage(self, msg):
        LOG_DEBUG('Generating response for BoosterProcessor: ', self.opType, msg)
        return 'booster_%(opType)s/%(msg)s' % {'opType': self.opType,
         'msg': msg}

    def _errorHandler(self, code, errStr='', ctx=None):
        if not len(errStr):
            if code != AccountCommands.RES_CENTER_DISCONNECTED:
                msg = 'server_error'
            else:
                msg = 'server_error_centerDown'
        else:
            msg = errStr
        return makeI18nError(self._formMessage(msg), **self._getMsgCtx())


class BoosterActivator(BoosterProcessor):

    def __init__(self, booster):
        super(BoosterActivator, self).__init__(booster, 'activate', [plugins.BoosterActivateValidator(booster)])

    def _getMsgCtx(self):
        return {'boosterName': self.booster.userName,
         'time': self.booster.getEffectTimeStr()}

    def _successHandler(self, code, ctx=None):
        return makeI18nSuccess(self._formMessage('success'), type=SM_TYPE.Information, **self._getMsgCtx())

    def _request(self, callback):
        LOG_DEBUG('Make server request to activate booster', self.booster.boosterID, self.booster.userName)
        BigWorld.player().activateGoodie([self.booster.boosterID], lambda code, errStr: self._response(code, callback, errStr=errStr))


class BoosterTradeProcessor(BoosterProcessor):

    def __init__(self, booster, count, opType, plugs=list()):
        super(BoosterTradeProcessor, self).__init__(booster, opType, plugs)
        self.count = count

    def _getMsgCtx(self):
        return {'boosterName': self.booster.userName,
         'count': BigWorld.wg_getIntegralFormat(int(self.count)),
         'money': formatPrice(self._getOpPrice())}

    def _getOpPrice(self):
        raise NotImplemented


class BoosterBuyer(BoosterTradeProcessor):
    """
    Booster buy processor
    :param booster: booster <Booster>
    :param count: count of boosters <int>
    :param buyForGold: is booster buying for gold or credits <bool>
    """

    def __init__(self, booster, count, buyForGold):
        super(BoosterBuyer, self).__init__(booster, count, 'buy')
        self.buyForGold = buyForGold
        self.addPlugins((plugins.MoneyValidator(self._getOpPrice()),))

    def _getOpPrice(self):
        price = self.booster.buyPrice
        return self.count * Money(gold=price.gold) if self.buyForGold else self.count * Money(credits=price.credits)

    def _successHandler(self, code, ctx=None):
        sysMsgType = SM_TYPE.PurchaseForGold if self.buyForGold else SM_TYPE.PurchaseForCredits
        return makeI18nSuccess(self._formMessage('success'), type=sysMsgType, **self._getMsgCtx())

    def _request(self, callback):
        LOG_DEBUG('Make server request to buy booster', self.booster.boosterID, self.booster.buyPrice, self.count, self.buyForGold)
        BigWorld.player().shop.buyGoodie(self.booster.boosterID, self.count, self.buyForGold, lambda code: self._response(code, callback))


class BoosterSeller(BoosterTradeProcessor):

    def __init__(self, booster, count):
        super(BoosterSeller, self).__init__(booster, count, 'sell')

    def _getOpPrice(self):
        return (self.booster.sellPrice[0] * self.count, self.booster.sellPrice[1] * self.count)

    def _successHandler(self, code, ctx=None):
        return makeI18nSuccess(self._formMessage('success'), type=SM_TYPE.Selling, **self._getMsgCtx())

    def _request(self, callback):
        LOG_DEBUG('Make server request to sell booster', self.booster, self.count)
        BigWorld.player().inventory.sellGoodie(self.booster.boosterID, self.count, lambda code: self._response(code, callback))
