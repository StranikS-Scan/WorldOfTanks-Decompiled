# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web/common.py
import typing
from gui.game_control.wallet import WalletController
from gui.shared.money import Currency
from skeletons.gui.shared.utils.requesters import IStatsRequester
from helpers import dependency
from skeletons.gui.game_control import IShopSalesEventController as IShopSales
if typing.TYPE_CHECKING:
    from typing import Dict, Union
    from gui.shared.money import Money

def getBalance(stats):
    actualMoney = stats.actualMoney.toDict()
    balanceData = {Currency.currencyExternalName(currency):actualMoney.get(currency, 0) for currency in Currency.ALL}
    balanceData.update(stats.dynamicCurrencies)
    balanceData[Currency.currencyExternalName(Currency.FREE_XP)] = stats.freeXP
    return balanceData


def getWalletCurrencyStatuses(stats):
    statuses = {Currency.currencyExternalName(currencyCode):WalletController.STATUS.getKeyByValue(statusCode).lower() for currencyCode, statusCode in stats.currencyStatuses.iteritems() if currencyCode in Currency.EXTENDED}
    statuses.update({currencyCode:WalletController.STATUS.getKeyByValue(statusCode).lower() for currencyCode, statusCode in stats.dynamicCurrencyStatuses.iteritems()})
    return statuses


@dependency.replace_none_kwargs(shopSales=IShopSales)
def formatShopSalesInfo(shopSales=None):
    return {'enabled': shopSales.isEnabled,
     'forbidden': shopSales.isForbidden,
     'dates': {'active': {'from': shopSales.activePhaseStartTime,
                          'to': shopSales.activePhaseFinishTime},
               'end': shopSales.eventFinishTime},
     'reroll': {'price': shopSales.reRollPrice.toSignDict()},
     'bundle': {'id': shopSales.currentBundleID,
                'rerolls': shopSales.currentBundleReRolls}}
