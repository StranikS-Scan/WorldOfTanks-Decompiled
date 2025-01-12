# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/dialogs/ExchangeDialogMeta.py
import operator
import Event
from adisp import adisp_async, adisp_process
from exchange.personal_discounts_constants import EXCHANGE_RATE_FREE_XP_NAME, EXCHANGE_RATE_GOLD_NAME, ExchangeDiscountType
from exchange.personal_discounts_helper import getDiscountsRequiredForExchange
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.view.dialogs import I18nConfirmDialogMeta
from gui.Scaleform.daapi.view.lobby.techtree.settings import UnlockStats
from gui.Scaleform.framework import ScopeTemplates
from gui.Scaleform.genConsts.CONFIRM_EXCHANGE_DIALOG_TYPES import CONFIRM_EXCHANGE_DIALOG_TYPES
from gui.Scaleform.genConsts.ICON_TEXT_FRAMES import ICON_TEXT_FRAMES
from gui.Scaleform.genConsts.TEXT_MANAGER_STYLES import TEXT_MANAGER_STYLES
from gui.Scaleform.locale.DIALOGS import DIALOGS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.managers.ColorSchemeManager import ColorSchemeManager
from gui.game_control.exchange_rates_with_discounts import getCurrentTime
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.lobby.exchange.exchange_rates_helper import MAX_SHOW_DISCOUNTS_INDEX, handleUserValuesInput, calculateMaxPossibleFreeXp
from gui.shared import events
from gui.shared.event_dispatcher import showExchangeXPDialogWindow
from gui.shared.formatters import icons, text_styles
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.processors import makeError
from gui.shared.gui_items.processors.common import GoldToCreditsExchanger
from gui.shared.money import Currency, Money
from gui.shared.utils import decorators
from gui.shared.utils.requesters.ItemsRequester import REQ_CRITERIA
from helpers import i18n, dependency
from skeletons.gui.game_control import IWalletController, IExchangeRatesWithDiscountsProvider
from skeletons.gui.shared import IItemsCache
from wg_async import wg_async, wg_await
STEP_SIZE = 1
I18N_NEEDGOLDTEXT_KEY = '{0:>s}/needGoldText'
I18N_NEEDITEMSTEXT_KEY = '{0:>s}/needItemsText'
I18N_GOLDNOTENOUGHTEXT_KEY = '{0:>s}/goldNotEnoughText'
I18N_EXCHANGENONEEDTEXT_KEY = '{0:>s}/exchangeNoNeedText'
I18N_NEEDITEMSSTEPPERTITLE_KEY = '{0:>s}/needItemsStepperTitle'
TEXT_COLOR_ID_XP = 'textColorXp'
TEXT_COLOR_ID_CREDITS = 'textColorCredits'

class InfoItemBase(object):

    @property
    def itemTypeName(self):
        raise NotImplementedError()

    @property
    def userName(self):
        raise NotImplementedError()

    @property
    def itemTypeID(self):
        raise NotImplementedError()

    def getExtraIconInfo(self):
        raise NotImplementedError()

    def getGUIEmblemID(self):
        raise NotImplementedError()


class _ExchangeSubmitterBase(object):

    def __init__(self, exchangeItem):
        self._exchangeItem = exchangeItem

    @property
    def type(self):
        return self._getType()

    @property
    def infoItem(self):
        return self._getInfoItem()

    @property
    def resourceToExchange(self):
        return self._getResourceToExchange()

    @property
    def currencyIconStr(self):
        return self._getCurrencyIconStr()

    @property
    def needItemsType(self):
        return self._getNeedItemsType()

    @property
    def currencyIconPath(self):
        return self._getCurrencyIconPath()

    @property
    def currencyFormat(self):
        return self._getCurrencyFormat()

    @property
    def colorScheme(self):
        return self._getColorScheme()

    @property
    def rateToColorScheme(self):
        return self._getRateToColorScheme()

    @property
    def exchangeRateItemsIcon(self):
        return self._getExchangeRateItemsIcon()

    @property
    def maxExchangeValue(self):
        return self._getMaxExchangeValue()

    @property
    def itemCD(self):
        return self._exchangeItem.itemCD

    def destroy(self):
        pass

    def submit(self, gold, valueToExchange, callback=None):
        raise NotImplementedError()

    def _getType(self):
        raise NotImplementedError()

    def _getInfoItem(self):
        raise NotImplementedError()

    def _getResourceToExchange(self):
        raise NotImplementedError()

    def _getCurrencyIconStr(self):
        raise NotImplementedError()

    def _getNeedItemsType(self):
        raise NotImplementedError()

    def _getCurrencyIconPath(self):
        raise NotImplementedError()

    def _getCurrencyFormat(self):
        raise NotImplementedError()

    def _getColorScheme(self):
        raise NotImplementedError()

    def _getRateToColorScheme(self):
        raise NotImplementedError()

    def _getExchangeRateItemsIcon(self):
        raise NotImplementedError()

    def _getMaxExchangeValue(self):
        raise NotImplementedError()


class _ExchangeRate(object):
    itemsCache = dependency.descriptor(IItemsCache)
    exchangeRatesProvider = dependency.descriptor(IExchangeRatesWithDiscountsProvider)

    @property
    def exchangeRate(self):
        return self._getExchangeRate()

    @property
    def baseExchangeRate(self):
        return self._getBaseExchangeRate()

    @property
    def isExchangeRateDiscountAvailable(self):
        return self._isExchangeRateDiscountAvailable()

    @property
    def exchangeRateDiscount(self):
        return self._getExchangeRateDiscount()

    @property
    def isExchangeRateDiscountLimited(self):
        return self._isExchangeRateDiscountLimited()

    @property
    def exchangeRateDiscountLimit(self):
        return self._getExchangeRateDiscountLimit()

    def discountsAmountAppliedForExchange(self, goldAmount):
        return self._discountsAmountAppliedForExchange(goldAmount)

    def getGoldToExchange(self, resourceForExchangeAm):
        return self._getGoldToExchange(resourceForExchangeAm)

    def getResourceAmountToExchangeForGold(self, goldAmount):
        return self._getResourceAmountToExchangeForGold(goldAmount)

    def calculateResourceToExchange(self, resourceAmount):
        return self._calculateResourceToExchange(resourceAmount)

    @property
    def _exchangeRate(self):
        return self.exchangeRatesProvider.get(self.getExchangeType())

    def _isExchangeRateDiscountAvailable(self):
        return self._exchangeRate.isDiscountAvailable()

    def _getExchangeRateDiscount(self):
        return self._exchangeRate.discountInfo

    def _getGoldToExchange(self, resourceForExchangeAm):
        return self._exchangeRate.calculateGoldToExchange(resourceForExchangeAm)

    def _isExchangeRateDiscountLimited(self):
        discount = self._getExchangeRateDiscount()
        return discount.discountType == ExchangeDiscountType.LIMITED if self._isExchangeRateDiscountAvailable() and discount is not None else False

    def _discountsAmountAppliedForExchange(self, goldAmount):
        return len(getDiscountsRequiredForExchange(self._exchangeRate.allPersonalLimitedDiscounts, goldAmount, getCurrentTime()))

    def _getExchangeRateDiscountLimit(self):
        discount = self._getExchangeRateDiscount()
        return discount.amountOfDiscount if self._isExchangeRateDiscountAvailable() and discount is not None else 0

    def _getExchangeRate(self):
        return self._exchangeRate.discountRate.resourceRateValue

    def _getBaseExchangeRate(self):
        return self._exchangeRate.unlimitedRateAfterMainDiscount.resourceRateValue

    def _getMainResourceAmountForGold(self, goldAmount):
        return self._getResourceAmountToExchangeForGold(goldAmount)

    def getExchangeType(self):
        raise NotImplementedError()

    def _getResourceAmountToExchangeForGold(self, goldAmount):
        return self._exchangeRate.calculateExchange(goldAmount)

    def _calculateResourceToExchange(self, resourceAmount):
        return self._exchangeRate.calculateResourceToExchange(resourceAmount)


class _GoldToCreditsExchangeRate(_ExchangeRate):

    def getExchangeType(self):
        return EXCHANGE_RATE_GOLD_NAME


class _XpTranslationExchangeRate(_ExchangeRate):

    def getExchangeType(self):
        return EXCHANGE_RATE_FREE_XP_NAME


class _ExchangeDialogMeta(I18nConfirmDialogMeta):
    itemsCache = dependency.descriptor(IItemsCache)
    wallet = dependency.descriptor(IWalletController)

    def __init__(self, submitterParams, key):
        self.__submitter = self._getSubmitterType()(submitterParams)
        self.onInvalidate = Event.Event()
        self.onCloseDialog = Event.Event()
        self.colorManager = ColorSchemeManager()
        super(_ExchangeDialogMeta, self).__init__(key, scope=ScopeTemplates.LOBBY_SUB_SCOPE)
        self.wallet.onWalletStatusChanged += self._onStatsChanged

    def destroy(self):
        self.wallet.onWalletStatusChanged -= self._onStatsChanged
        self.onInvalidate.clear()
        self.onCloseDialog.clear()
        self.__submitter.destroy()

    @adisp_async
    @adisp_process
    def submit(self, gold, valueToExchange, callback=None):
        submitter = self._getSubmitter()
        result = yield submitter.submit(gold, valueToExchange)
        if callback is not None:
            callback(result)
        return

    def getType(self):
        submitter = self._getSubmitter()
        return submitter.type

    def getExchangeType(self):
        submitter = self._getSubmitter()
        return submitter.getExchangeType()

    def getEventType(self):
        return events.ShowDialogEvent.SHOW_EXCHANGE_DIALOG

    def getResourceAmountToExchangeForGold(self, goldAmount):
        submitter = self._getSubmitter()
        return submitter.getResourceAmountToExchangeForGold(goldAmount)

    def calculateResourceToExchange(self, resourceAmount):
        submitter = self._getSubmitter()
        return submitter.calculateResourceToExchange(resourceAmount)

    def getExchangeProvider(self):
        submitter = self._getSubmitter()
        return submitter.exchangeRatesProvider.get(submitter.getExchangeType())

    def getTypeCompDescr(self):
        submitter = self._getSubmitter()
        return submitter.itemCD

    def getResourceToExchange(self):
        submitter = self._getSubmitter()
        return submitter.resourceToExchange

    def discountsAmountAppliedForExchange(self, goldAmount):
        submitter = self._getSubmitter()
        return submitter.discountsAmountAppliedForExchange(goldAmount)

    def makeVO(self):
        submitter = self._getSubmitter()
        item = submitter.infoItem
        resToExchange = submitter.resourceToExchange
        state, stateMsg = self._getState(resToExchange)
        return {'title': self.getTitle(),
         'exchangeBtnText': self.getButtonLabels()[0]['label'],
         'cancelBtnText': self.getButtonLabels()[1]['label'],
         'state': state,
         'lockExchangeMessage': stateMsg,
         'iconExtraInfo': item.getExtraIconInfo(),
         'iconModuleType': item.itemTypeName,
         'icon': self._getItemIcon(item),
         'iconType': self._getItemIconType(item),
         'itemName': text_styles.middleTitle(item.userName),
         'needItemsText': self._getResourceToExchangeTxt(resToExchange),
         'needItemsType': self._needItemsType(),
         'needGoldText': self._getGoldToExchangeTxt(resToExchange),
         'exchangeBlockData': self._getExchangeBlockData(resToExchange)}

    def _getSubmitterType(self):
        raise NotImplementedError()

    def _getSubmitter(self):
        return self.__submitter

    def _onStatsChanged(self, *args):
        self.onInvalidate()

    def _getRGB(self, colorId):
        return self.colorManager.getColorScheme(colorId).get('rgb')

    def _makeString(self, key, ctx=None):
        ctx = ctx or {}
        i18nKey = key.format(self._key)
        return super(_ExchangeDialogMeta, self)._makeString(i18nKey, ctx)

    def _getExchangeBlockData(self, resToExchange):
        submitter = self._getSubmitter()
        goldStepperTitleStr = i18n.makeString(DIALOGS.CONFIRMEXCHANGEDIALOG_GOLDITEMSSTEPPERTITLE)
        goldStepperTitleFmt = text_styles.main(goldStepperTitleStr)
        needItemsStepperTitle = text_styles.main(self._makeString(I18N_NEEDITEMSSTEPPERTITLE_KEY))
        maxGold, maxNeedItems = handleUserValuesInput(selectedGold=submitter.maxExchangeValue, selectedCurrency=0, exchangeProvider=self.getExchangeProvider())
        goldForExchange = self._getGoldToExchange(resToExchange)
        return {'goldStepperTitle': goldStepperTitleFmt,
         'needItemsIcon': submitter.currencyIconPath,
         'needItemsStepperTitle': needItemsStepperTitle,
         'goldIcon': RES_ICONS.MAPS_ICONS_LIBRARY_GOLDICON_2,
         'defaultExchangeRate': submitter.baseExchangeRate,
         'exchangeRate': submitter.exchangeRate,
         'discountLimit': submitter.exchangeRateDiscountLimit,
         'isDiscountAvailable': submitter.exchangeRate != submitter.baseExchangeRate,
         'maxDiscountsAppliedForMoreInfo': MAX_SHOW_DISCOUNTS_INDEX,
         'isDiscountLimited': submitter.isExchangeRateDiscountLimited,
         'limitRestrictionsBtnText': backport.text(R.strings.personal_exchange_rates.common.limitRestrictions()),
         'discountLimitText': backport.text(R.strings.personal_exchange_rates.common.limitExceeded()),
         'discountLimitOverExceededText': backport.text(R.strings.personal_exchange_rates.common.limitOverExceeded()),
         'defaultGoldValue': goldForExchange,
         'goldStepSize': STEP_SIZE,
         'maxGoldValue': maxGold,
         'maxNeedItemsValue': maxNeedItems,
         'goldTextColorId': TEXT_MANAGER_STYLES.GOLD_TEXT,
         'itemsTextColorId': submitter.colorScheme,
         'exchangeHeaderData': {'labelText': MENU.EXCHANGE_RATE,
                                'rateFromIcon': ICON_TEXT_FRAMES.GOLD,
                                'rateToIcon': submitter.exchangeRateItemsIcon,
                                'rateFromTextColor': self._getRGB(TEXT_COLOR_ID_XP),
                                'rateToTextColor': self._getRGB(submitter.rateToColorScheme)}}

    def _getState(self, resToExchange):
        if resToExchange <= 0:
            return (CONFIRM_EXCHANGE_DIALOG_TYPES.EXCHANGE_NOT_NEEED_STATE, text_styles.success(self._makeString(I18N_EXCHANGENONEEDTEXT_KEY)))
        if not self._isEnoughGold(resToExchange):
            goldToExchange = self._getGoldToExchange(resToExchange)
            fmtGold = ''.join((text_styles.gold(backport.getGoldFormat(goldToExchange)), icons.gold()))
            return (CONFIRM_EXCHANGE_DIALOG_TYPES.NOT_ENOUGH_GOLD_STATE, text_styles.error(self._makeString(I18N_GOLDNOTENOUGHTEXT_KEY, {'gold': fmtGold})))
        return (CONFIRM_EXCHANGE_DIALOG_TYPES.NORMAL_STATE, '')

    def _isEnoughGold(self, resToExchange):
        return self._getGoldToExchange(resToExchange) <= self.itemsCache.items.stats.gold

    def _getResourceToExchangeTxt(self, resToExchange):
        if resToExchange > 0:
            resource = backport.getIntegralFormat(resToExchange)
            submitter = self._getSubmitter()
            resStr = submitter.currencyFormat(resource) + submitter.currencyIconStr
            return text_styles.error(self._makeString(I18N_NEEDITEMSTEXT_KEY, {'value': resStr}))

    def _needItemsType(self):
        submitter = self._getSubmitter()
        return submitter.needItemsType

    def _getGoldToExchangeTxt(self, resToExchange):
        if resToExchange > 0:
            goldToExchange = self._getGoldToExchange(resToExchange)
            fmtGold = ''.join((text_styles.gold(backport.getGoldFormat(goldToExchange)), icons.gold()))
            return text_styles.main(self._makeString(I18N_NEEDGOLDTEXT_KEY, {'gold': fmtGold}))

    def _getGoldToExchange(self, resToExchange):
        if resToExchange > 0:
            submitter = self._getSubmitter()
            return submitter.getGoldToExchange(resToExchange)

    def _getItemIconType(self, item):
        return CONFIRM_EXCHANGE_DIALOG_TYPES.VEHICLE_ICON if item.itemTypeID == GUI_ITEM_TYPE.VEHICLE else CONFIRM_EXCHANGE_DIALOG_TYPES.MODULE_ICON

    def _getItemIcon(self, item):
        if item.itemTypeID == GUI_ITEM_TYPE.VEHICLE:
            icon = item.type
            if item.isElite:
                icon += '_elite'
            return icon
        else:
            return item.getGUIEmblemID()


class _ExchangeItem(object):
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, cd, count=1):
        super(_ExchangeItem, self).__init__()
        self._cd = cd
        self._count = count

    @property
    def itemCD(self):
        return self._cd

    @property
    def count(self):
        return self._count

    @property
    def infoItem(self):
        return self._getInfoItem()

    def doAction(self, action, resultType):
        raise NotImplementedError

    def _getInfoItem(self):
        raise NotImplementedError


class _SingleExchangeItem(_ExchangeItem):

    def doAction(self, action, resultType):
        return action(self._cd)

    def _getInfoItem(self):
        item = self.itemsCache.items.getItemByCD(self._cd)
        return item


class _MultipleExchangeItem(_ExchangeItem):

    def __init__(self, itemsCDs, infoItem):
        super(_MultipleExchangeItem, self).__init__(itemsCDs)
        self.__infoItem = infoItem

    def doAction(self, action, resultType):
        return sum([ action(itemCD) for itemCD in self._cd ], resultType())

    def _getInfoItem(self):
        return self.__infoItem


class _WebProductInfoItem(InfoItemBase):

    def __init__(self, name):
        self.__name = name

    @property
    def itemTypeName(self):
        pass

    @property
    def itemTypeID(self):
        return None

    @property
    def userName(self):
        return self.__name

    def getExtraIconInfo(self):
        return None

    def getGUIEmblemID(self):
        pass


class _WebProductExchangeItem(_ExchangeItem):

    def __init__(self, price, count, infoItem):
        super(_WebProductExchangeItem, self).__init__(None, count)
        self.__infoItem = infoItem
        self.__price = price
        return

    @property
    def price(self):
        return self.__price

    def _getInfoItem(self):
        return self.__infoItem

    def doAction(self, action, resultType):
        pass


class _SlotInfoItem(InfoItemBase):

    def __init__(self, name):
        self.__name = name

    @property
    def itemTypeName(self):
        pass

    @property
    def itemTypeID(self):
        return None

    @property
    def userName(self):
        return self.__name

    def getExtraIconInfo(self):
        return None

    def getGUIEmblemID(self):
        pass


class _SlotExchangeItem(_ExchangeItem):

    def __init__(self, price, count, infoItem):
        super(_SlotExchangeItem, self).__init__(None, count)
        self.__infoItem = infoItem
        self.__price = price
        return

    @property
    def price(self):
        return self.__price

    def _getInfoItem(self):
        return self.__infoItem

    def doAction(self, action, resultType):
        pass


class _ExchangeCreditsSubmitter(_ExchangeSubmitterBase, _GoldToCreditsExchangeRate):

    @adisp_async
    @decorators.adisp_process('transferMoney')
    def submit(self, gold, valueToExchange, callback=None):
        result = yield GoldToCreditsExchanger(gold).request()
        if callback is not None:
            callback(result)
        return

    def _getType(self):
        return CONFIRM_EXCHANGE_DIALOG_TYPES.TYPE_CREDITS_EXCHANGE

    def _getInfoItem(self):
        return self._exchangeItem.infoItem

    def _getResourceToExchange(self):

        def _getPrice(itemCD):
            item = self.itemsCache.items.getItemByCD(itemCD)
            return item.buyPrices.itemPrice.price

        price = self._exchangeItem.doAction(_getPrice, Money)
        return price.get(Currency.CREDITS, 0) * self._exchangeItem.count - self.itemsCache.items.stats.credits

    def _getCurrencyIconStr(self):
        return icons.credits()

    def _getNeedItemsType(self):
        return Currency.CREDITS

    def _getCurrencyIconPath(self):
        return RES_ICONS.MAPS_ICONS_LIBRARY_CREDITSICON_2

    def _getCurrencyFormat(self):
        return text_styles.credits

    def _getColorScheme(self):
        return TEXT_MANAGER_STYLES.CREDITS_TEXT

    def _getRateToColorScheme(self):
        return TEXT_COLOR_ID_CREDITS

    def _getExchangeRateItemsIcon(self):
        return ICON_TEXT_FRAMES.CREDITS

    def _getMaxExchangeValue(self):
        return self.itemsCache.items.stats.actualGold


class _ExchangeCreditsSubscriber(object):
    __exchangeRatesProvider = dependency.descriptor(IExchangeRatesWithDiscountsProvider)

    def __init__(self):
        super(_ExchangeCreditsSubscriber, self).__init__()
        self.__exchangeRatesProvider.goldToCredits.onUpdated += self._onStatsChanged
        g_clientUpdateManager.addMoneyCallback(self._onStatsChanged)
        g_clientUpdateManager.addCallback('shop.exchangeRate', self._onStatsChanged)

    def destroy(self):
        self.__exchangeRatesProvider.goldToCredits.onUpdated -= self._onStatsChanged
        g_clientUpdateManager.removeObjectCallbacks(self)

    def _onStatsChanged(self, *args):
        raise NotImplementedError()


class ExchangeCreditsSingleItemMeta(_ExchangeDialogMeta, _ExchangeCreditsSubscriber):

    def __init__(self, itemCD, installVehicle=None, key='confirmExchangeDialog/exchangeCredits', count=1):
        super(ExchangeCreditsSingleItemMeta, self).__init__(_SingleExchangeItem(itemCD, count=count), key=key)
        submitter = self._getSubmitter()
        item = self.itemsCache.items.getItemByCD(submitter.itemCD)
        self.__installVehicleCD = installVehicle
        self.__isInstalled = False
        if item and item.itemTypeID != GUI_ITEM_TYPE.VEHICLE and self.__installVehicleCD:
            vehicle = self.itemsCache.items.getItemByCD(self.__installVehicleCD)
            self.__isInstalled = item.isInstalled(vehicle)
        self.__inventoryCount = 0
        if item:
            self.__inventoryCount = item.inventoryCount
        g_clientUpdateManager.addCallback('inventory.1', self.__checkInventory)

    def destroy(self):
        self.__inventoryCount = None
        self.__installVehicleCD = None
        g_clientUpdateManager.removeObjectCallbacks(self)
        super(ExchangeCreditsSingleItemMeta, self).destroy()
        return

    def _getSubmitterType(self):
        return _ExchangeCreditsSubmitter

    def __checkInventory(self, *args):
        submitter = self._getSubmitter()
        item = self.itemsCache.items.getItemByCD(submitter.itemCD)
        if item is not None:
            if item.itemTypeID == GUI_ITEM_TYPE.VEHICLE and item.isInInventory or item.inventoryCount > self.__inventoryCount:
                self.onCloseDialog()
            elif self.__installVehicleCD:
                vehicle = self.itemsCache.items.getItemByCD(self.__installVehicleCD)
                if not self.__isInstalled and item.isInstalled(vehicle):
                    self.onCloseDialog()
        return


class ExchangeCreditsSingleItemModalMeta(ExchangeCreditsSingleItemMeta):

    def getEventType(self):
        return events.ShowDialogEvent.SHOW_EXCHANGE_DIALOG_MODAL


class ExchangeCreditsMultiItemsMeta(_ExchangeDialogMeta, _ExchangeCreditsSubscriber):

    def __init__(self, itemsCDs, infoItem, key='confirmExchangeDialog/exchangeCredits'):
        super(ExchangeCreditsMultiItemsMeta, self).__init__(_MultipleExchangeItem(itemsCDs, infoItem), key)

    def _getSubmitterType(self):
        return _ExchangeCreditsSubmitter


class _ExchangeCreditsForSlotSubmitter(_ExchangeCreditsSubmitter):

    def _getResourceToExchange(self):
        return self._exchangeItem.count * self._exchangeItem.price - self.itemsCache.items.stats.credits


class ExchangeCreditsForSlotMeta(_ExchangeDialogMeta, _ExchangeCreditsSubscriber):

    def __init__(self, name, count, price, key='confirmExchangeDialog/exchangeCredits'):
        infoItem = _SlotInfoItem(name)
        super(ExchangeCreditsForSlotMeta, self).__init__(_SlotExchangeItem(price, count, infoItem), key)

    def _getSubmitterType(self):
        return _ExchangeCreditsForSlotSubmitter


class _WebProductCreditsExchangeSubmitter(_ExchangeCreditsSubmitter):

    def _getResourceToExchange(self):
        return self._exchangeItem.count * self._exchangeItem.price - self.itemsCache.items.stats.credits


class ExchangeCreditsWebProductMeta(_ExchangeDialogMeta, _ExchangeCreditsSubscriber):
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, name, count, price, key='confirmExchangeDialog/exchangeCredits'):
        infoItem = _WebProductInfoItem(name)
        super(ExchangeCreditsWebProductMeta, self).__init__(_WebProductExchangeItem(price, count, infoItem), key)

    def _getItemIconType(self, item):
        return CONFIRM_EXCHANGE_DIALOG_TYPES.PLATFORM_PACK_ICON

    def _getSubmitterType(self):
        return _WebProductCreditsExchangeSubmitter


class _RestoreExchangeCreditsSubmitter(_ExchangeCreditsSubmitter):

    def _getResourceToExchange(self):

        def _getRestorePrice(itemCD):
            item = self.itemsCache.items.getItemByCD(itemCD)
            return item.restorePrice.getSignValue(Currency.CREDITS)

        credit = self._exchangeItem.doAction(_getRestorePrice, Money)
        return credit - self.itemsCache.items.stats.credits


class RestoreExchangeCreditsMeta(ExchangeCreditsSingleItemMeta):

    def __init__(self, itemCD, key='confirmExchangeDialog/restoreExchangeCredits'):
        super(RestoreExchangeCreditsMeta, self).__init__(itemCD, key=key)

    def _getSubmitterType(self):
        return _RestoreExchangeCreditsSubmitter


class _ExchangeXpSubmitter(_ExchangeSubmitterBase, _XpTranslationExchangeRate):

    def __init__(self, submitterParams):
        exchangeItem, parentCD, xpCost = submitterParams
        super(_ExchangeXpSubmitter, self).__init__(exchangeItem)
        self._parentCD = parentCD
        self._xpCost = xpCost

    def destroy(self):
        self._parentCD = None
        self._xpCost = None
        return

    @adisp_async
    @wg_async
    def submit(self, gold, xpToExchange, callback=None):
        isOk, result, xpExchanged = yield wg_await(showExchangeXPDialogWindow(self.getResourceAmountToExchangeForGold(gold)))
        if xpExchanged < xpToExchange:
            result = makeError(auxData=[result])
        if callback is not None:
            callback(result if isOk else None)
        return

    def _getType(self):
        return CONFIRM_EXCHANGE_DIALOG_TYPES.TYPE_XP_EXCHANGE

    def _getInfoItem(self):
        return self._exchangeItem.infoItem

    def _getResourceToExchange(self):

        def _getUnlockState(itemCD):
            item = self.itemsCache.items.getItemByCD(itemCD)
            return item.isUnlocked

        unlockState = self._exchangeItem.doAction(_getUnlockState, bool)
        if unlockState:
            return 0
        stats = self.itemsCache.items.stats
        unlockStats = UnlockStats(stats.unlocks, stats.vehiclesXPs, stats.freeXP)
        return self._xpCost - unlockStats.getVehTotalXP(self._parentCD)

    def _getCurrencyIconStr(self):
        return icons.freeXP()

    def _getNeedItemsType(self):
        return Currency.FREE_XP

    def _getCurrencyIconPath(self):
        return RES_ICONS.MAPS_ICONS_LIBRARY_ELITEXPICON_2

    def _getCurrencyFormat(self):
        return text_styles.expText

    def _getColorScheme(self):
        return TEXT_MANAGER_STYLES.STATS_TEXT

    def _getRateToColorScheme(self):
        return TEXT_COLOR_ID_XP

    def _getExchangeRateItemsIcon(self):
        return ICON_TEXT_FRAMES.ELITE_XP

    def _getMaxExchangeValue(self):
        eliteVehicles = self.itemsCache.items.getVehicles(REQ_CRITERIA.VEHICLE.FULLY_ELITE).values()
        maxAvailableXpForGold = calculateMaxPossibleFreeXp(sum(map(operator.attrgetter('xp'), eliteVehicles)))
        return min(self.getGoldToExchange(maxAvailableXpForGold), self.itemsCache.items.stats.actualGold)


class ExchangeXpMeta(_ExchangeDialogMeta):
    __exchangeRatesProvider = dependency.descriptor(IExchangeRatesWithDiscountsProvider)

    def __init__(self, itemCD, parentCD, xpCost):
        super(ExchangeXpMeta, self).__init__((_SingleExchangeItem(itemCD), parentCD, xpCost), key='confirmExchangeDialog/exchangeXp')
        self.__exchangeRatesProvider.freeXpTranslation.onUpdated += self._onStatsChanged
        g_clientUpdateManager.addCurrencyCallback(Currency.GOLD, self._onStatsChanged)
        g_clientUpdateManager.addCallbacks({'shop.freeXPConversion': self._onStatsChanged,
         'inventory.1': self._onStatsChanged,
         'stats.vehTypeXP': self._onStatsChanged,
         'stats.freeXP': self._onStatsChanged,
         'stats.unlocks': self.__checkUnlocks})

    def destroy(self):
        self.__exchangeRatesProvider.freeXpTranslation.onUpdated -= self._onStatsChanged
        g_clientUpdateManager.removeObjectCallbacks(self)
        super(ExchangeXpMeta, self).destroy()

    def _getSubmitterType(self):
        return _ExchangeXpSubmitter

    def __checkUnlocks(self, *args):
        submitter = self._getSubmitter()
        item = self.itemsCache.items.getItemByCD(submitter.itemCD)
        if item is not None and item.isUnlocked:
            self.onCloseDialog()
        return
