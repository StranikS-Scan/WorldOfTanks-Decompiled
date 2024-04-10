# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/formatters/__init__.py
import logging
from itertools import combinations
from typing import Optional
from gui import makeHtmlString
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.Scaleform.genConsts.CURRENCIES_CONSTANTS import CURRENCIES_CONSTANTS
from gui.impl import backport
from gui.shared.gui_items.gui_item_economics import ActualPrice
from gui.impl.gen import R
from gui.shared.formatters import icons
from gui.shared.formatters import text_styles
from gui.shared.formatters import time_formatters
from gui.shared.formatters.icons import getRoleIcon
from gui.shared.formatters.currency import getBWFormatter, getStyle
from gui.shared.gui_items import GUI_ITEM_ECONOMY_CODE, GUI_ITEM_TYPE
from gui.shared.money import Money, Currency
from helpers import i18n, dependency, int2roman
from helpers.i18n import makeString
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.shared import IItemsCache
_logger = logging.getLogger(__name__)
__all__ = ('icons', 'text_styles', 'time_formatters')

@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def _checkPriceIsAllowed(price, itemsCache=None, checkGold=False):
    return itemsCache.items.stats.money >= (price if checkGold else price.replace(Currency.GOLD, 0))


def _getFormattedPrice(price, isBuying, checkGold):
    format_ = backport.getGoldFormat
    postfix = ''
    template = 'html_templates:lobby/quests/actions'
    fmtCurrency = {currencyName:'' for currencyName in Currency.ALL}
    if isBuying and not _checkPriceIsAllowed(price, checkGold=checkGold):
        postfix = 'Error'
    for currencyName in fmtCurrency:
        currencyValue = price.get(currencyName)
        if currencyValue is not None:
            fmtCurrency[currencyName] = makeHtmlString(template, currencyName + postfix, {'value': format_(currencyValue)})

    for firstCurrency, secondCurrency in combinations(Currency.BY_WEIGHT, 2):
        if price.isCurrencyDefined(firstCurrency) and price.isCurrencyDefined(secondCurrency):
            return i18n.makeString(TOOLTIPS.ACTIONPRICE_EXCHANGE_CURRENCYOR, credits=fmtCurrency[secondCurrency], gold=fmtCurrency[firstCurrency])

    for currencyName in Currency.BY_WEIGHT:
        if price.isCurrencyDefined(currencyName):
            return fmtCurrency[currencyName]

    return


def formatActionPrices(oldPrice, newPrice, isBuying, checkGold=False):
    oldPrice = Money.makeFromMoneyTuple(oldPrice)
    if not oldPrice.isDefined():
        oldPrice = Money(credits=0)
    newPrice = Money.makeFromMoneyTuple(newPrice)
    if not newPrice.isDefined():
        newPrice = Money.makeFrom(oldPrice.getCurrency(), 0)
    return (_getFormattedPrice(oldPrice, isBuying, checkGold), _getFormattedPrice(newPrice, isBuying, checkGold))


def formatPrice(price, reverse=False, currency=Currency.CREDITS, useIcon=False, useStyle=False, ignoreZeros=False, justValue=False):
    outPrice = []
    currencies = [ c for c in Currency.ALL if price.get(c) is not None ]
    if not currencies:
        currencies = [currency]
    for c in currencies:
        value = price.get(c, 0)
        if value == 0 and ignoreZeros and not (c == Currency.CREDITS and not price.getSetCurrencies()):
            continue
        cFormatted = formatPriceValue(value, c, useStyle=useStyle)
        if useIcon:
            cIdentifier = makeHtmlString('html_templates:lobby/iconText', c)
            cSpace = ' ' if reverse else ''
        elif justValue:
            cIdentifier = ''
            cSpace = ''
        else:
            cIdentifier = makeString('#menu:price/{}'.format(c))
            cSpace = ' ' if reverse else ': '
        outPrice.append(''.join((cFormatted, cSpace, cIdentifier) if reverse else (cIdentifier, cSpace, cFormatted)))

    return ', '.join(outPrice)


def formatPriceValue(value, currency, useStyle=False):
    formatter = getBWFormatter(currency)
    cFormatted = formatter(value)
    if useStyle:
        styler = getStyle(currency)
        cFormatted = styler(cFormatted) if styler else cFormatted
    return cFormatted


def formatPriceForCurrency(money, currencyName):
    return formatPrice(Money(money.get(currencyName)))


def formatGoldPrice(gold, reverse=False):
    return formatPrice(Money(gold=gold), reverse=reverse, currency=Currency.GOLD)


def getGlobalRatingFmt(globalRating):
    return backport.getIntegralFormat(globalRating) if globalRating >= 0 else '--'


def moneyWithIcon(money, currType=None):
    if currType is None:
        currType = money.getCurrency()
    style = getattr(text_styles, currType)
    icon = getattr(icons, currType)
    value = money.get(currType)
    formatter = getBWFormatter(currType)
    if style is not None and icon is not None and value is not None:
        return style(formatter(value)) + icon()
    else:
        _logger.error('Unsupported currency for displaying with icon: %s', currType)
        return formatter(value)


def getMoneyVO(moneyObj):
    return tuple(((c, v) for c, v in moneyObj.iteritems()))


def getMoneyVOWithReason(errorMsg, moneyObj):
    result = []
    for c, v in moneyObj.iteritems():
        if errorMsg == GUI_ITEM_ECONOMY_CODE.getCurrencyError(c):
            result.append(('%sError' % c, v))
        result.append((c, v))

    return tuple(result)


def getItemPricesVO(*itemPrices):
    resultVO = []
    for itemPrice in itemPrices:
        action = itemPrice.getActionPrcAsMoney()
        if action.isDefined():
            vo = {'price': getMoneyVO(itemPrice.price),
             'defPrice': getMoneyVO(itemPrice.defPrice),
             'action': getMoneyVO(action)}
            resultVO.append(vo)
        resultVO.append({'price': getMoneyVO(itemPrice.price)})

    return resultVO


def updateActionInViewModel(currency, actionPriceModel, itemPrice):
    currencyAction = itemPrice.getActionPrcAsMoney().get(currency)
    currencyValue = itemPrice.price.get(currency)
    actionPriceModel.setAction(currencyAction)
    defValue = itemPrice.defPrice.get(currency)
    setNewMethodName = 'setNew' + currency.title()
    setOldMethodName = 'setOld' + currency.title()
    if hasattr(actionPriceModel, setNewMethodName):
        setNewValueMethod = getattr(actionPriceModel, setNewMethodName)
        setNewValueMethod(currencyValue)
    else:
        _logger.error("ActionPriceModel doesn't support method %s", setNewMethodName)
    if hasattr(actionPriceModel, setOldMethodName):
        setOldValueMethod = getattr(actionPriceModel, setOldMethodName)
        setOldValueMethod(defValue)
    else:
        _logger.error("ActionPriceModel doesn't support method %s", setOldMethodName)


def getItemPricesVOWithReason(reason, *itemPrices):
    resultVO = []
    for itemPrice in itemPrices:
        action = itemPrice.getActionPrcAsMoney()
        if action.isDefined():
            vo = {'price': getMoneyVOWithReason(reason, itemPrice.price),
             'defPrice': getMoneyVO(itemPrice.defPrice),
             'action': getMoneyVO(action)}
            resultVO.append(vo)
        resultVO.append({'price': getMoneyVOWithReason(reason, itemPrice.price)})

    return resultVO


def getItemUnlockPricesVO(*unlockProps):
    resultVO = []
    for unlockProp in unlockProps:
        if unlockProp.discount:
            resultVO.append({'price': ((CURRENCIES_CONSTANTS.XP_COST, unlockProp.xpCost),),
             'defPrice': ((CURRENCIES_CONSTANTS.XP_COST, unlockProp.xpFullCost),),
             'action': ((CURRENCIES_CONSTANTS.XP_COST, unlockProp.discount),)})
        resultVO.append({'price': ((CURRENCIES_CONSTANTS.XP_COST, unlockProp.xpCost),)})

    return resultVO


def getUnlockDiscountXpVO(unlockProps, xpType):
    return {'cost': unlockProps.xpCost,
     'fullCost': unlockProps.xpFullCost,
     'xpType': xpType}


def getItemSellPricesVO(sellCurrency, *sellPrices):
    return [ {'price': getMoneyVO(sellPrice) or ((sellCurrency, 0),)} for sellPrice in sellPrices ]


def getItemRestorePricesVO(*prices):
    return [ {'price': getMoneyVO(price)} for price in prices ]


def chooseItemPriceVO(priceType, price):
    itemPrice = None
    if priceType == ActualPrice.RESTORE_PRICE:
        itemPrice = getItemRestorePricesVO(price)
    if priceType == ActualPrice.RENT_PRICE:
        itemPrice = getItemPricesVO(price)
    elif priceType == ActualPrice.BUY_PRICE:
        itemPrice = getItemPricesVO(price)
    return itemPrice


def formatPurchaseItems(purchaseItems):
    formattedItems = []
    items = set((purchaseItem.item for purchaseItem in purchaseItems if not purchaseItem.isFromInventory and purchaseItem.selected))
    for item in items:
        count = sum((purchaseItem.item.intCD == item.intCD and not purchaseItem.isFromInventory and purchaseItem.selected for purchaseItem in purchaseItems))
        if item.itemTypeID == GUI_ITEM_TYPE.STYLE and item.isProgression:
            c11nService = dependency.instance(ICustomizationService)
            ctx = {'styleName': item.userName,
             'level': int2roman(c11nService.getCurrentProgressionStyleLevel())}
            resource = R.strings.messenger.serviceChannelMessages.sysMsg.customization.item.progressionStyle
        else:
            ctx = {'itemType': item.userType,
             'itemName': item.userName,
             'count': count}
            resource = R.strings.messenger.serviceChannelMessages.sysMsg.customization.item
        formattedItem = backport.text(resource(), **ctx)
        formattedItems.append(formattedItem)

    return ', \n'.join(formattedItems) + '.'


def getRoleTextWithIcon(role, roleLabel):
    return text_styles.concatStylesToSingleLine(getRoleIcon(roleLabel), makeHtmlString('html_templates:vehicleRoles', 'roleMain', {'message': getRoleText(roleLabel)})) if role else ''


def getRoleTextWithLabel(role, roleLabel):
    roleStr = ''
    if role:
        roleText = backport.text(R.strings.dialogs.vehicleSellDialog.vehicle.role())
        roleStr = text_styles.main(''.join([roleText, getRoleText(roleLabel)]))
    return roleStr


def getRoleText(roleLabel):
    return backport.text(R.strings.menu.roleExp.roleName.dyn(roleLabel)(), groupName=backport.text(R.strings.menu.roleExp.roleGroupName.dyn(roleLabel)()))


def calculateWinRate(wins, battles, precision=0):
    return round(100.0 * wins / battles, precision) if battles > 0 else 0.0
