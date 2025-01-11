# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: armory_yard/scripts/client/armory_yard/gui/shared/formatters.py
import typing
from copy import deepcopy
from armory_yard.gui.shared.bonus_packers import packBonuses, getArmoryYardBonusPacker
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.money import Currency
from gui.shared.formatters.currency import getBWFormatter
CURRENCIES_FORMATTERS = {Currency.GOLD: "<font color='#FFC363'>{}</font>",
 Currency.AYCOIN: "<font color='#E9E2BF'>{}</font>"}
ITEMS_FORMATTER = "<font color='#CED9D9'>{}</font>"
_ITEMS_WITHOUT_PIECES = frozenset({'freeXP',
 'credits',
 'premium_universal',
 'crystal'})
_BULLET = u' \u2022 '

def formatSpentCurrencies(currencies):
    included = [ backport.text(R.strings.armory_shop.notifications.description.dyn(currencyName)(), value=CURRENCIES_FORMATTERS[currencyName].format(currencyAmount)) for currencyName, currencyAmount in currencies if currencyAmount ]
    return '\n'.join(included)


def formatPurchaseItems(items, packer=None, skipCount=False, isBundle=False, isVehicle=False):
    formattedItems = []
    prefix = _BULLET if not isVehicle and (isBundle or len(items) > 2) else ''
    for bonus in packBonuses(items, packer):
        count = bonus.getValue() or 1
        if skipCount:
            backportText = R.strings.armory_shop.notifications.purchaseContent.withoutCount()
        elif bonus.getName() in _ITEMS_WITHOUT_PIECES:
            backportText = R.strings.armory_shop.notifications.purchaseContent.withoutPieces()
            count = ITEMS_FORMATTER.format(getBWFormatter(bonus.getName())(count))
        else:
            backportText = R.strings.armory_shop.notifications.purchaseContent()
        label = bonus.getLabel()
        formattedItems.append(prefix + backport.text(backportText, product=ITEMS_FORMATTER.format(label) if skipCount else label, count=count))

    if isVehicle:
        header = backport.text(R.strings.armory_shop.notifications.vehicle())
        return _BULLET + header + ', '.join(formattedItems)
    return '\n'.join(formattedItems)


def formatBundlePurchase(productId, items):
    items = deepcopy(items)
    _cutCompensation(items)
    vehicles = items.pop('vehicles')
    return backport.text(R.strings.armory_shop.notifications.bundleContent(), vehicles=formatPurchaseItems({'vehicles': vehicles}, skipCount=True, isBundle=True, isVehicle=True), items=formatPurchaseItems(items, getArmoryYardBonusPacker()), isBundle=True)


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
