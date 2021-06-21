# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/veh_post_porgression/models/purchase.py
from collections import namedtuple
from account_helpers import isLongDisconnectedFromCenter
from gui.veh_post_porgression.models.ext_money import ExtendedMoney
from gui.veh_post_porgression.models.ext_money import ExtendedCurrency as _ExtCurrency
from gui.veh_post_porgression.models.ext_money import ExtendedGuiItemEconomyCode as _ExtEconomyCode
from helpers import dependency
from skeletons.gui.game_control import IWalletController

def _exchangeCredits(balance, creditsRate):
    if balance.isSet(_ExtCurrency.GOLD):
        balance = balance.exchange(_ExtCurrency.GOLD, _ExtCurrency.CREDITS, creditsRate, default=0)
    return balance


class PurchaseCheckResult(namedtuple('PurchaseCheckResult', 'result, reason')):

    def __nonzero__(self):
        return self.result


VALID_CHECK_RESULT = PurchaseCheckResult(True, _ExtEconomyCode.UNDEFINED)

class PurchaseProvider(object):
    __wallet = dependency.descriptor(IWalletController)
    _EXCHANGE_PROCESSORS = {_ExtEconomyCode.NOT_ENOUGH_CREDITS: _exchangeCredits}

    @classmethod
    def isEnoughMoney(cls, balance, price):
        if not price.isDefined():
            return PurchaseCheckResult(False, _ExtEconomyCode.ITEM_NO_PRICE)
        if price.isXPCompound():
            return PurchaseCheckResult(False, _ExtEconomyCode.XP_COMPOUND_PRICE)
        shortage = balance.getShortage(price)
        if shortage:
            currency = shortage.getCurrency(byWeight=True)
            return PurchaseCheckResult(False, _ExtEconomyCode.getCurrencyError(currency))
        return VALID_CHECK_RESULT

    @classmethod
    def mayConsume(cls, balance, price):
        if isLongDisconnectedFromCenter():
            return PurchaseCheckResult(False, _ExtEconomyCode.CENTER_UNAVAILABLE)
        return PurchaseCheckResult(False, _ExtEconomyCode.WALLET_NOT_AVAILABLE) if not cls.__wallet.isAvailable else cls.isEnoughMoney(balance, price)

    @classmethod
    def mayConsumeWithExhange(cls, balance, price, creditsRate):
        if price.isCompound():
            return PurchaseCheckResult(False, _ExtEconomyCode.COMPOUND_PRICE)
        checkResult = cls.mayConsume(balance, price)
        if not checkResult and checkResult.reason in cls._EXCHANGE_PROCESSORS:
            balance = cls._EXCHANGE_PROCESSORS[checkResult.reason](balance, creditsRate)
            return cls.isEnoughMoney(balance, price)
        return checkResult
