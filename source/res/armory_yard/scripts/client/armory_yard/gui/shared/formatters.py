# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: armory_yard/scripts/client/armory_yard/gui/shared/formatters.py
import typing
from copy import deepcopy
from armory_yard.gui.shared.bonus_packers import packBonuses, getArmoryYardBonusPacker
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.money import Currency
CURRENCIES_FORMATTERS = {Currency.GOLD: "<font color='#FFC363'>{}</font>",
 Currency.AYCOIN: "<font color='#E9E2BF'>{}</font>"}

def formatSpentCurrencies(currencies):
    included = [ backport.text(R.strings.armory_shop.notifications.description.dyn(currencyName)(), value=CURRENCIES_FORMATTERS[currencyName].format(currencyAmount)) for currencyName, currencyAmount in currencies if currencyAmount ]
    return '\n'.join(included)


def formatPurchaseItems(items, packer=None):
    formattedItems = [ backport.text(R.strings.armory_shop.notifications.purchaseContent(), product=bonus.getLabel(), count=bonus.getValue() if bonus.getValue() else 1) for bonus in packBonuses(items, packer) ]
    return '\n'.join(formattedItems)


def formatBundlePurchase(productId, items):
    items = deepcopy(items)
    _cutCompensation(items)
    vehicles = items.pop('vehicles')
    return backport.text(R.strings.armory_shop.notifications.bundleContent(), vehicles=formatPurchaseItems({'vehicles': vehicles}), items=formatPurchaseItems(items, getArmoryYardBonusPacker()))


def _cutCompensation(rewards):
    if 'vehicles' in rewards:
        creditCompensation = 0
        goldCompensation = 0
        for _, vehParams in rewards['vehicles'][0].iteritems():
            credit, gold = vehParams.get('customCompensation', (0, 0))
            creditCompensation += credit
            goldCompensation += gold

        if creditCompensation:
            rewards['credits'] = rewards['credits'] - creditCompensation
            if rewards['credits'] <= 0:
                del rewards['credits']
        if goldCompensation:
            rewards['gold'] = rewards['gold'] - goldCompensation
            if rewards['gold'] <= 0:
                del rewards['gold']
