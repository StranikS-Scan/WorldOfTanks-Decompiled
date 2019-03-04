# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/formatters/__init__.py
import logging
from itertools import combinations
import BigWorld
from gui import makeHtmlString
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.Scaleform.genConsts.CURRENCIES_CONSTANTS import CURRENCIES_CONSTANTS
from gui.impl.gen.view_models.ui_kit.action_price_model import ActionPriceModel
from gui.shared.economics import ActualPrice
from gui.shared.formatters import icons
from gui.shared.formatters import text_styles
from gui.shared.formatters import time_formatters
from gui.shared.formatters.currency import getBWFormatter, getStyle
from gui.shared.gui_items import GUI_ITEM_ECONOMY_CODE
from gui.shared.money import Money, Currency
from helpers import i18n, dependency
from helpers.i18n import makeString
from skeletons.gui.shared import IItemsCache
_logger = logging.getLogger(__name__)
__all__ = ('icons', 'text_styles', 'time_formatters')

@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def _checkPriceIsAllowed(price, itemsCache=None):
    isPurchaseAllowed = itemsCache.items.stats.isIngameShopEnabled
    if isPurchaseAllowed:
        for currencyType in Currency.ALL:
            if price.get(currencyType):
                isPurchaseAllowed &= currencyType == Currency.GOLD

    return itemsCache.items.stats.money >= price or isPurchaseAllowed


def _getFormattedPrice(price):
    format_ = BigWorld.wg_getGoldFormat
    postfix = ''
    template = 'html_templates:lobby/quests/actions'
    fmtCurrency = {currencyName:'' for currencyName in Currency.ALL}
    if not _checkPriceIsAllowed(price):
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


def formatActionPrices(oldPrice, newPrice):
    oldPrice = Money.makeFromMoneyTuple(oldPrice)
    if not oldPrice.isDefined():
        oldPrice = Money(credits=0)
    newPrice = Money.makeFromMoneyTuple(newPrice)
    if not newPrice.isDefined():
        newPrice = Money.makeFrom(oldPrice.getCurrency(), 0)
    return (_getFormattedPrice(oldPrice), _getFormattedPrice(newPrice))


def formatPrice(price, reverse=False, currency=Currency.CREDITS, useIcon=False, useStyle=False, ignoreZeros=False):
    outPrice = []
    currencies = [ c for c in Currency.ALL if price.get(c) is not None ]
    if not currencies:
        currencies = [currency]
    for c in currencies:
        value = price.get(c, 0)
        if value == 0 and ignoreZeros:
            continue
        formatter = getBWFormatter(c)
        cFormatted = formatter(value) if formatter else value
        if useStyle:
            styler = getStyle(c)
            cFormatted = styler(cFormatted) if styler else cFormatted
        if useIcon:
            cIdentifier = makeHtmlString('html_templates:lobby/iconText', c)
            cSpace = ' ' if reverse else ''
        else:
            cIdentifier = makeString('#menu:price/{}'.format(c))
            cSpace = ' ' if reverse else ': '
        outPrice.append(''.join((cFormatted, cSpace, cIdentifier) if reverse else (cIdentifier, cSpace, cFormatted)))

    return ', '.join(outPrice)


def formatPriceForCurrency(money, currencyName):
    return formatPrice(Money(money.get(currencyName)))


def formatGoldPrice(gold, reverse=False):
    return formatPrice(Money(gold=gold), reverse, currency=Currency.GOLD)


def getGlobalRatingFmt(globalRating):
    return BigWorld.wg_getIntegralFormat(globalRating) if globalRating >= 0 else '--'


def moneyWithIcon(money, currType=None, statsMoney=None):
    from gui.Scaleform.daapi.view.lobby.store.browser.ingameshop_helpers import isIngameShopEnabled
    if currType is None:
        currType = money.getCurrency()
    if statsMoney and not isIngameShopEnabled() and statsMoney.get(currType) < money.get(currType):
        style = getattr(text_styles, 'error')
    else:
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
        if errorMsg == GUI_ITEM_ECONOMY_CODE.getMoneyError(c):
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


def getItemPricesViewModel(statsMoney, *itemPrices):
    result = []
    for itemPrice in itemPrices:
        priceModels = []
        if itemPrice.isDefined():
            for currency in Currency.ALL:
                currencyValue = itemPrice.price.get(currency)
                if currencyValue is not None:
                    actionPriceModel = ActionPriceModel()
                    isEnough = statsMoney.get(currency) >= currencyValue
                    actionPriceModel.setIsEnough(isEnough)
                    currencyAction = itemPrice.getActionPrcAsMoney().get(currency)
                    hasAction = currencyAction is not None
                    if hasAction:
                        updateActionInViewModel(currency, actionPriceModel, itemPrice)
                    actionPriceModel.setType(currency)
                    actionPriceModel.setIsWithAction(hasAction)
                    actionPriceModel.setPrice(BigWorld.wg_getIntegralFormat(currencyValue))
                    defPrice = BigWorld.wg_getIntegralFormat(itemPrice.defPrice.get(currency, 0))
                    actionPriceModel.setDefPrice(defPrice)
                    priceModels.append(actionPriceModel)

        else:
            actionPriceModel = ActionPriceModel()
            actionPriceModel.setIsFree(True)
            priceModels.append(actionPriceModel)
        if priceModels:
            result.append(priceModels)

    return result


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


def getItemRentOrRestorePricesVO(*prices):
    return [ {'price': getMoneyVO(price)} for price in prices ]


def chooseItemPriceVO(priceType, price):
    itemPrice = None
    if priceType == ActualPrice.RENT_PRICE or priceType == ActualPrice.RESTORE_PRICE:
        itemPrice = getItemRentOrRestorePricesVO(price)
    elif priceType == ActualPrice.BUY_PRICE:
        itemPrice = getItemPricesVO(price)
    return itemPrice
