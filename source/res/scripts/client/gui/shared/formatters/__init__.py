# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/formatters/__init__.py
import logging
import BigWorld
from gui.shared.formatters import icons
from gui.shared.formatters import text_styles
from gui.shared.formatters import time_formatters
from gui.shared.formatters.currency import getBWFormatter
from gui.shared.gui_items import GUI_ITEM_ECONOMY_CODE
from gui.shared.money import Money, Currency
from helpers.i18n import makeString
from gui.impl.gen.view_models.ui_kit.action_price_model import ActionPriceModel
_logger = logging.getLogger(__name__)
__all__ = ('icons', 'text_styles', 'time_formatters')

def formatPrice(price, reverse=False, defaultCurrency=Currency.CREDITS):
    outPrice = []
    currencies = price.getSetCurrencies(byWeight=False)
    if not currencies:
        currencies = [defaultCurrency]
    for currency in currencies:
        formatter = getBWFormatter(currency)
        cname = makeString('#menu:price/{}'.format(currency)) + ': '
        value = price.get(currency, 0)
        cformatted = formatter(value) if formatter else value
        outPrice.append(''.join((cformatted, ' ', cname) if reverse else (cname, ' ', cformatted)))

    return ', '.join(outPrice)


def formatPriceForCurrency(money, currencyName):
    return formatPrice(Money(money.get(currencyName)))


def formatGoldPrice(gold, reverse=False):
    return formatPrice(Money(gold=gold), reverse, defaultCurrency=Currency.GOLD)


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
                    defPrice = BigWorld.wg_getIntegralFormat(itemPrice.defPrice.get(currency))
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
