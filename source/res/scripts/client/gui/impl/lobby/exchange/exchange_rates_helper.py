# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/exchange/exchange_rates_helper.py
import typing
from account_helpers import AccountSettings
from account_helpers.AccountSettings import EXCHANGE_GOLD_RATE_DISCOUNT_ANIMATION_SHOWED, EXCHANGE_XP_RATE_DISCOUNT_ANIMATION_SHOWED
from exchange.personal_discounts_constants import EXCHANGE_RATE_GOLD_NAME, EXCHANGE_RATE_FREE_XP_NAME, EXCHANGE_NAME_TO_GAME_PARAM_NAME, MAX_DISCOUNT_VALUE, ExchangeRate, ExchangeDiscountType
from exchange.personal_discounts_helper import sortExchangeRatesDiscounts
from gui.SystemMessages import SM_TYPE
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.exchange.discount_presentation import DiscountPresentation
from gui.shared.gui_items.processors import makeI18nSuccess
from gui.shared.money import Currency
from helpers import dependency, time_utils
from skeletons.gui.game_control import IExchangeRatesWithDiscountsProvider, IExchangeRateWithDiscounts
from skeletons.gui.impl import IGuiLoader
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from typing import Optional, Tuple, Dict, List
    from gui.SystemMessages import ResultMsg
    from exchange.personal_discounts_constants import ExchangeDiscountInfo
MAX_SHOW_DISCOUNTS_INDEX = 5
DISCOUNT_ANIMATION_TIME = 15.0
EXCHANGE_RATE_NAME_TO_CURRENCIES = {EXCHANGE_RATE_GOLD_NAME: (Currency.GOLD, Currency.CREDITS),
 EXCHANGE_RATE_FREE_XP_NAME: (Currency.FREE_XP, Currency.GOLD)}
NEED_ITEMS_TYPE_TO_EXCHANGE_RATE = {Currency.CREDITS: EXCHANGE_RATE_GOLD_NAME,
 Currency.FREE_XP: EXCHANGE_RATE_FREE_XP_NAME}
EXCHANGE_RATE_TO_UI_KEY = {EXCHANGE_RATE_FREE_XP_NAME: EXCHANGE_XP_RATE_DISCOUNT_ANIMATION_SHOWED,
 EXCHANGE_RATE_GOLD_NAME: EXCHANGE_GOLD_RATE_DISCOUNT_ANIMATION_SHOWED}

def getCurrentTime():
    return time_utils.getCurrentLocalServerTimestamp()


def isDiscountViewed(discountType):
    return isGoldExchangeRateDiscountViewed() if discountType == EXCHANGE_RATE_GOLD_NAME else isExperienceTranslationRateDiscountViewed()


def getRateNameFromCurrencies(currencies):
    return next((key for key, val in EXCHANGE_RATE_NAME_TO_CURRENCIES.items() if val == currencies), None)


def setDiscountViewed(exchangeRate, forced=False):
    _setDiscountViewed(exchangeRate, EXCHANGE_RATE_TO_UI_KEY.get(exchangeRate), forced=forced)


def isGoldExchangeRateDiscountViewed():
    return _isDiscountViewed(EXCHANGE_RATE_GOLD_NAME)


def isExperienceTranslationRateDiscountViewed():
    return _isDiscountViewed(EXCHANGE_RATE_FREE_XP_NAME)


@dependency.replace_none_kwargs(exchangeDiscountCtr=IExchangeRatesWithDiscountsProvider)
def _setDiscountViewed(exchangeName, uiFlag, forced=False, exchangeDiscountCtr=None):
    discount = exchangeDiscountCtr.get(exchangeName).bestPersonalDiscount
    if discount is not None:
        viewedTime = 0 if forced else getCurrentTime()
        AccountSettings.setUIFlag(uiFlag, (_getDiscountUID(discount), viewedTime))
    return


@dependency.replace_none_kwargs(exchangeDiscountCtr=IExchangeRatesWithDiscountsProvider)
def _isDiscountViewed(exchangeName, exchangeDiscountCtr=None):
    discount = exchangeDiscountCtr.get(exchangeName).bestPersonalDiscount
    if discount is None:
        return True
    else:
        viewedData = AccountSettings.getUIFlag(EXCHANGE_RATE_TO_UI_KEY.get(exchangeName))
        if not viewedData:
            return False
        lastViewedUID, viewedTime = viewedData
        return True if _getDiscountUID(discount) == lastViewedUID and viewedTime + DISCOUNT_ANIMATION_TIME < getCurrentTime() else False


def _getDiscountUID(discount):
    return discount.tokenName if discount.isPersonal else hash(str(discount.discountLifetime) + discount.exchangeType + str(discount.resourceRateValue) + str(discount.goldRateValue) + discount.discountType)


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def getExchangeRate(exchangeName, default=False, itemsCache=None):
    currencyValuePath = EXCHANGE_NAME_TO_GAME_PARAM_NAME.get(exchangeName, None)
    requester = itemsCache.items.shop
    if currencyValuePath is not None:
        if default:
            requester = getattr(requester, 'defaults')
        value = getattr(requester, currencyValuePath)
        return value
    else:
        return


def convertToGuiLimit(discount, amount):
    return amount * discount.resourceRateValue


def getAllLimitedDiscountsAmount(allDiscounts):
    allDiscountsAmount = 0
    for discount in allDiscounts:
        if discount.discountType == ExchangeDiscountType.LIMITED:
            allDiscountsAmount += convertToGuiLimit(discount, discount.amountOfDiscount)

    return allDiscountsAmount


def getShowFormatRate(discount):
    return (discount.goldRateValue, discount.resourceRateValue) if discount.exchangeType == EXCHANGE_RATE_GOLD_NAME else (discount.resourceRateValue, discount.goldRateValue)


@dependency.replace_none_kwargs(exchangeProvider=IExchangeRatesWithDiscountsProvider)
def convertGoldToGuiLimit(discount, goldAmount, exchangeProvider=None):
    if discount.isPersonal:
        if discount.exchangeType == EXCHANGE_RATE_GOLD_NAME:
            return exchangeProvider.goldToCredits.calculateExchange(goldAmount)
        if discount.exchangeType == EXCHANGE_RATE_FREE_XP_NAME:
            return exchangeProvider.freeXpTranslation.calculateResourceToExchange(goldAmount)[0]
    return goldAmount


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def handleUserValuesInput(selectedGold=0, selectedCurrency=0, validateGold=True, exchangeProvider=None, itemsCache=None):
    exchanger = exchangeProvider
    if validateGold and selectedGold and itemsCache.items.stats.gold < selectedGold:
        return (0, 0)
    if selectedGold >= MAX_DISCOUNT_VALUE or selectedCurrency >= MAX_DISCOUNT_VALUE:
        selectedGold, selectedCurrency = exchanger.calculateResourceToExchange(MAX_DISCOUNT_VALUE)
    elif selectedGold > 0:
        selectedCurrency = exchanger.calculateExchange(selectedGold)
        if selectedCurrency > MAX_DISCOUNT_VALUE:
            selectedGold, selectedCurrency = exchanger.calculateResourceToExchange(MAX_DISCOUNT_VALUE)
    elif selectedCurrency > 0:
        selectedGold, selectedCurrency = exchanger.calculateResourceToExchange(selectedCurrency)
    else:
        selectedGold, selectedCurrency = (0, 0)
    if selectedCurrency > MAX_DISCOUNT_VALUE:
        selectedGold -= 1
        selectedCurrency = exchanger.calculateExchange(selectedGold)
    return (selectedGold, selectedCurrency)


@dependency.replace_none_kwargs(itemsCache=IItemsCache, exchangeProvider=IExchangeRatesWithDiscountsProvider)
def calculateMaxPossibleFreeXp(xpFromVehicles, validateGold=True, itemsCache=None, exchangeProvider=None):
    goldRequiredForVehXpExchange, xpFromAllVehicles = exchangeProvider.freeXpTranslation.calculateResourceToExchange(xpFromVehicles)
    if xpFromAllVehicles > xpFromVehicles and goldRequiredForVehXpExchange > 0:
        goldRequiredForVehXpExchange -= 1
    gold = min(goldRequiredForVehXpExchange, itemsCache.items.stats.gold) if validateGold else goldRequiredForVehXpExchange
    maxAvailableXpForGold = exchangeProvider.freeXpTranslation.calculateExchange(gold)
    return maxAvailableXpForGold


def showAllPersonalDiscountsWindow(exchangeRateType, selectedValue):
    from gui.impl.lobby.exchange.all_personal_discounts_window import AllPersonalDiscountsWindow
    view = R.views.lobby.personal_exchange_rates.AllPersonalExchangesView()
    guiLoader = dependency.instance(IGuiLoader)
    window = guiLoader.windowsManager.getViewByLayoutID(view)
    if window is not None:
        return
    else:
        window = AllPersonalDiscountsWindow(layoutID=view, exchangeRateType=exchangeRateType, selectedValue=selectedValue)
        window.load()
        return


@dependency.replace_none_kwargs(exchangeProvider=IExchangeRatesWithDiscountsProvider)
def fillAllDiscountsModel(allDiscountsModel, allLimitedDiscounts, selectedPrice, exchangeProvider=None):
    if not allLimitedDiscounts:
        return allDiscountsModel
    exchanger = exchangeProvider.get(allLimitedDiscounts[0].exchangeType)
    selectedResource = exchanger.calculateExchange(selectedPrice)
    lastElementId = len(allLimitedDiscounts) - 1
    for numberId, personalDiscount in enumerate(allLimitedDiscounts):
        discountModel = DiscountPresentation()
        isTheLast = lastElementId == numberId
        discountAmount = personalDiscount.amountOfDiscount * personalDiscount.resourceRateValue
        if isTheLast:
            discountModel.setSelectedAmountOfDiscount(selectedResource)
        else:
            discountModel.setSelectedAmountOfDiscount(min(selectedResource, discountAmount))
        discountModel.setWholeAmountOfDiscount(discountAmount)
        discountModel.exchangeRate.setGoldRateValue(personalDiscount.goldRateValue)
        discountModel.exchangeRate.setResourceRateValue(personalDiscount.resourceRateValue)
        allDiscountsModel.addViewModel(discountModel)
        if selectedResource - discountAmount <= 0:
            break
        selectedResource -= discountAmount

    return allDiscountsModel


def createSystemExchangeNotification(discounts, goldAmount, defaultRate, baseRate, isPersonalUnlimRate, exchangeType):
    text = ''
    if exchangeType == EXCHANGE_RATE_GOLD_NAME:
        successInfo = R.strings.personal_exchange_rates.exchange.information()
        fromRate = 'goldRateValue'
        toRate = 'resourceRateValue'
    else:
        successInfo = R.strings.personal_exchange_rates.exchangeXP.information()
        fromRate = 'resourceRateValue'
        toRate = 'goldRateValue'
    exchangedWithDiscounts = 0
    for discount in sortExchangeRatesDiscounts(discounts.keys()):
        exchanged = discounts.get(discount)
        exchangedWithDiscounts += exchanged
        text += backport.text(successInfo, gold=int(exchanged), res=int(exchanged * discount.resourceRateValue))
        if exchanged == discount.amountOfDiscount and discounts:
            text += '\n' + backport.text(R.strings.personal_exchange_rates.exchange.personalExchangeRates.exceeded(), rateFrom=getattr(discount, fromRate), rateTo=getattr(discount, toRate))
            text += ';\n\n' if exchangedWithDiscounts != goldAmount else '.'
        text += '\n' + backport.text(R.strings.personal_exchange_rates.exchange.personalExchangeRate(), rateFrom=getattr(discount, fromRate), rateTo=getattr(discount, toRate))

    if exchangedWithDiscounts < goldAmount:
        goldExchanged = goldAmount - exchangedWithDiscounts
        resExchanged = goldExchanged * baseRate.resourceRateValue
        text += backport.text(successInfo, gold=int(goldExchanged), res=int(resExchanged))
        if baseRate != defaultRate:
            source = R.strings.personal_exchange_rates.exchange.generalExchangeRate()
            if isPersonalUnlimRate:
                source = R.strings.personal_exchange_rates.exchange.personalExchangeRate()
            text += '\n' + backport.text(source, rateFrom=getattr(baseRate, fromRate), rateTo=getattr(baseRate, toRate))
        else:
            text += '\n' + backport.text(R.strings.personal_exchange_rates.exchange.defaultExchangeRate(), rateFrom=getattr(defaultRate, fromRate), rateTo=getattr(defaultRate, toRate))
    message = makeI18nSuccess(sysMsgKey='exchange/success/information', information=text, type=SM_TYPE.FinancialTransactionWithGold)
    return message


def handleAndRoundStepperInput(params, exchangeRate, validateGold=True):
    userSelectedCurrency = params.get('currency', 0)
    userSelectedGold = params.get('gold', 0)
    upperSelectedGold, upperSelectedCurrency = handleUserValuesInput(selectedGold=userSelectedGold, selectedCurrency=userSelectedCurrency, validateGold=validateGold, exchangeProvider=exchangeRate)
    selectedGold, selectedCurrency = upperSelectedGold, upperSelectedCurrency
    if userSelectedCurrency and userSelectedCurrency != upperSelectedCurrency:
        downSelectedGold, downSelectedCurrency = handleUserValuesInput(selectedGold=upperSelectedGold - 1, selectedCurrency=0, validateGold=validateGold, exchangeProvider=exchangeRate)
        isRoundedToZero = downSelectedGold == 0 and selectedGold != 0
        if not isRoundedToZero and userSelectedCurrency - downSelectedCurrency < upperSelectedCurrency - userSelectedCurrency:
            selectedGold, selectedCurrency = downSelectedGold, downSelectedCurrency
    return (selectedGold, selectedCurrency)
