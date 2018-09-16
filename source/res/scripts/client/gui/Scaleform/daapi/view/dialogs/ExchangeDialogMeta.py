# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/dialogs/ExchangeDialogMeta.py
import math
import operator
import BigWorld
import Event
from adisp import async, process
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.view.dialogs import I18nConfirmDialogMeta
from gui.Scaleform.daapi.view.lobby.techtree.settings import UnlockStats
from gui.Scaleform.framework import ScopeTemplates
from gui.Scaleform.genConsts.CONFIRM_EXCHANGE_DIALOG_TYPES import CONFIRM_EXCHANGE_DIALOG_TYPES
from gui.Scaleform.genConsts.ICON_TEXT_FRAMES import ICON_TEXT_FRAMES
from gui.Scaleform.genConsts.TEXT_MANAGER_STYLES import TEXT_MANAGER_STYLES
from gui.Scaleform.locale.DIALOGS import DIALOGS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.managers.ColorSchemeManager import ColorSchemeManager
from gui.shared import events
from gui.shared.formatters import icons, text_styles
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.processors.common import FreeXPExchanger, GoldToCreditsExchanger
from gui.shared.money import Currency, Money
from gui.shared.utils import decorators
from gui.shared.utils.requesters.ItemsRequester import REQ_CRITERIA
from helpers import i18n, dependency
from skeletons.gui.game_control import IWalletController
from skeletons.gui.shared import IItemsCache
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

    @property
    def type(self):
        return self._getType()

    @property
    def infoItem(self):
        return self._getInfoItem()

    @property
    def exchangeRate(self):
        return self._getExchangeRate()

    @property
    def defaultExchangeRate(self):
        return self._getDefaultExchangeRate()

    @property
    def resourceToExchange(self):
        return self._getResourceToExchange()

    @property
    def currencyIconStr(self):
        return self._getCurrencyIconStr()

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

    def __init__(self, exchangeItem):
        self._exchangeItem = exchangeItem

    def destroy(self):
        pass

    def submit(self, gold, valueToExchange, callback=None):
        raise NotImplementedError()

    def _getType(self):
        raise NotImplementedError()

    def _getInfoItem(self):
        raise NotImplementedError()

    def _getExchangeRate(self):
        raise NotImplementedError()

    def _getDefaultExchangeRate(self):
        raise NotImplementedError()

    def _getResourceToExchange(self):
        raise NotImplementedError()

    def _getCurrencyIconStr(self):
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

    @async
    @process
    def submit(self, gold, valueToExchange, callback=None):
        submitter = self._getSubmitter()
        result = yield submitter.submit(gold, valueToExchange)
        if callback is not None:
            callback(result)
        return

    def getType(self):
        submitter = self._getSubmitter()
        return submitter.type

    def getEventType(self):
        return events.ShowDialogEvent.SHOW_EXCHANGE_DIALOG

    def getExchangeRate(self):
        submitter = self._getSubmitter()
        return submitter.exchangeRate

    def getTypeCompDescr(self):
        submitter = self._getSubmitter()
        return submitter.itemCD

    def makeVO(self):
        submitter = self._getSubmitter()
        item = submitter.infoItem
        resToExchange = submitter.resourceToExchange
        state, stateMsg = self.__getState(resToExchange)
        return {'title': self.getTitle(),
         'exchangeBtnText': self.getButtonLabels()[0]['label'],
         'cancelBtnText': self.getButtonLabels()[1]['label'],
         'state': state,
         'lockExchangeMessage': stateMsg,
         'iconExtraInfo': item.getExtraIconInfo(),
         'iconModuleType': item.itemTypeName,
         'icon': self.__getItemIcon(item),
         'iconType': self.__getItemIconType(item),
         'itemName': text_styles.middleTitle(item.userName),
         'needItemsText': self.__getResourceToExchangeTxt(resToExchange),
         'needGoldText': self.__getGoldToExchangeTxt(resToExchange),
         'exchangeBlockData': self.__getExchangeBlockData(resToExchange)}

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

    def __getExchangeBlockData(self, resToExchange):
        submitter = self._getSubmitter()
        goldStepperTitleStr = i18n.makeString(DIALOGS.CONFIRMEXCHANGEDIALOG_GOLDITEMSSTEPPERTITLE)
        goldStepperTitleFmt = text_styles.main(goldStepperTitleStr)
        needItemsStepperTitle = text_styles.main(self._makeString(I18N_NEEDITEMSSTEPPERTITLE_KEY))
        return {'goldStepperTitle': goldStepperTitleFmt,
         'needItemsIcon': submitter.currencyIconPath,
         'needItemsStepperTitle': needItemsStepperTitle,
         'goldIcon': RES_ICONS.MAPS_ICONS_LIBRARY_GOLDICON_2,
         'defaultExchangeRate': submitter.defaultExchangeRate,
         'exchangeRate': submitter.exchangeRate,
         'defaultGoldValue': self.__getGoldToExchange(resToExchange),
         'goldStepSize': STEP_SIZE,
         'maxGoldValue': submitter.maxExchangeValue,
         'goldTextColorId': TEXT_MANAGER_STYLES.GOLD_TEXT,
         'itemsTextColorId': submitter.colorScheme,
         'exchangeHeaderData': {'labelText': '',
                                'rateFromIcon': ICON_TEXT_FRAMES.GOLD,
                                'rateToIcon': submitter.exchangeRateItemsIcon,
                                'rateFromTextColor': self._getRGB(TEXT_COLOR_ID_XP),
                                'rateToTextColor': self._getRGB(submitter.rateToColorScheme)}}

    def __getState(self, resToExchange):
        if resToExchange <= 0:
            return (CONFIRM_EXCHANGE_DIALOG_TYPES.EXCHANGE_NOT_NEEED_STATE, text_styles.success(self._makeString(I18N_EXCHANGENONEEDTEXT_KEY)))
        if not self.__isEnoughGold(resToExchange):
            goldToExchange = self.__getGoldToExchange(resToExchange)
            fmtGold = ''.join((text_styles.gold(BigWorld.wg_getGoldFormat(goldToExchange)), icons.gold()))
            return (CONFIRM_EXCHANGE_DIALOG_TYPES.NOT_ENOUGH_GOLD_STATE, text_styles.error(self._makeString(I18N_GOLDNOTENOUGHTEXT_KEY, {'gold': fmtGold})))
        return (CONFIRM_EXCHANGE_DIALOG_TYPES.NORMAL_STATE, '')

    def __isEnoughGold(self, resToExchange):
        return self.__getGoldToExchange(resToExchange) <= self.itemsCache.items.stats.gold

    def __getResourceToExchangeTxt(self, resToExchange):
        if resToExchange > 0:
            resource = BigWorld.wg_getIntegralFormat(resToExchange)
            submitter = self._getSubmitter()
            resStr = submitter.currencyFormat(resource) + submitter.currencyIconStr
            return text_styles.error(self._makeString(I18N_NEEDITEMSTEXT_KEY, {'value': resStr}))

    def __getGoldToExchangeTxt(self, resToExchange):
        if resToExchange > 0:
            goldToExchange = self.__getGoldToExchange(resToExchange)
            fmtGold = ''.join((text_styles.gold(BigWorld.wg_getGoldFormat(goldToExchange)), icons.gold()))
            return text_styles.main(self._makeString(I18N_NEEDGOLDTEXT_KEY, {'gold': fmtGold}))

    def __getGoldToExchange(self, resToExchange):
        if resToExchange > 0:
            submitter = self._getSubmitter()
            return int(math.ceil(float(resToExchange) / submitter.exchangeRate))

    def __getItemIconType(self, item):
        return CONFIRM_EXCHANGE_DIALOG_TYPES.VEHICLE_ICON if item.itemTypeID == GUI_ITEM_TYPE.VEHICLE else CONFIRM_EXCHANGE_DIALOG_TYPES.MODULE_ICON

    def __getItemIcon(self, item):
        if item.itemTypeID == GUI_ITEM_TYPE.VEHICLE:
            icon = item.type
            if item.isElite:
                icon += '_elite'
            return icon
        else:
            return item.getGUIEmblemID()


class _ExchangeItem(object):
    itemsCache = dependency.descriptor(IItemsCache)

    @property
    def itemCD(self):
        return self._cd

    @property
    def infoItem(self):
        return self._getInfoItem()

    def __init__(self, cd):
        super(_ExchangeItem, self).__init__()
        self._cd = cd

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


class _ExchangeCreditsSubmitter(_ExchangeSubmitterBase):
    itemsCache = dependency.descriptor(IItemsCache)

    @async
    @decorators.process('transferMoney')
    def submit(self, gold, valueToExchange, callback=None):
        result = yield GoldToCreditsExchanger(gold).request()
        if callback is not None:
            callback(result)
        return

    def _getType(self):
        return CONFIRM_EXCHANGE_DIALOG_TYPES.TYPE_CREDITS_EXCHANGE

    def _getInfoItem(self):
        return self._exchangeItem.infoItem

    def _getExchangeRate(self):
        return self.itemsCache.items.shop.exchangeRate

    def _getDefaultExchangeRate(self):
        return self.itemsCache.items.shop.defaults.exchangeRate

    def _getResourceToExchange(self):

        def _getPrice(itemCD):
            item = self.itemsCache.items.getItemByCD(itemCD)
            return item.buyPrices.itemPrice.price

        price = self._exchangeItem.doAction(_getPrice, Money)
        return price.get(Currency.CREDITS, 0) - self.itemsCache.items.stats.credits

    def _getCurrencyIconStr(self):
        return icons.credits()

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

    def __init__(self):
        super(_ExchangeCreditsSubscriber, self).__init__()
        g_clientUpdateManager.addMoneyCallback(self._onStatsChanged)
        g_clientUpdateManager.addCallback('shop.exchangeRate', self._onStatsChanged)

    def destroy(self):
        g_clientUpdateManager.removeObjectCallbacks(self)

    def _onStatsChanged(self, *args):
        raise NotImplementedError()


class ExchangeCreditsSingleItemMeta(_ExchangeDialogMeta, _ExchangeCreditsSubscriber):

    def __init__(self, itemCD, installVehicle=None, key='confirmExchangeDialog/exchangeCredits'):
        super(ExchangeCreditsSingleItemMeta, self).__init__(_SingleExchangeItem(itemCD), key=key)
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


class ExchangeCreditsMultiItemsMeta(_ExchangeDialogMeta, _ExchangeCreditsSubscriber):

    def __init__(self, itemsCDs, infoItem, key='confirmExchangeDialog/exchangeCredits'):
        super(ExchangeCreditsMultiItemsMeta, self).__init__(_MultipleExchangeItem(itemsCDs, infoItem), key)

    def _getSubmitterType(self):
        return _ExchangeCreditsSubmitter


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


class _ExchangeXpSubmitter(_ExchangeSubmitterBase):
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, submitterParams):
        exchangeItem, parentCD, xpCost = submitterParams
        super(_ExchangeXpSubmitter, self).__init__(exchangeItem)
        self._parentCD = parentCD
        self._xpCost = xpCost

    def destroy(self):
        self._parentCD = None
        self._xpCost = None
        return

    @async
    @decorators.process('exchangeVehiclesXP')
    def submit(self, gold, xpToExchange, callback=None):
        criteria = REQ_CRITERIA.VEHICLE.FULLY_ELITE | ~REQ_CRITERIA.IN_CD_LIST([self._parentCD])
        eliteVehicles = self.itemsCache.items.getVehicles(criteria).keys()
        result = yield FreeXPExchanger(xpToExchange, eliteVehicles).request()
        if callback is not None:
            callback(result)
        return

    def _getType(self):
        return CONFIRM_EXCHANGE_DIALOG_TYPES.TYPE_XP_EXCHANGE

    def _getInfoItem(self):
        return self._exchangeItem.infoItem

    def _getExchangeRate(self):
        return self.itemsCache.items.shop.freeXPConversion[0]

    def _getDefaultExchangeRate(self):
        return self.itemsCache.items.shop.defaults.freeXPConversion[0]

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
        result = sum(map(operator.attrgetter('xp'), eliteVehicles))
        return min(int(result / self.exchangeRate), self.itemsCache.items.stats.actualGold)


class ExchangeXpMeta(_ExchangeDialogMeta):

    def __init__(self, itemCD, parentCD, xpCost):
        super(ExchangeXpMeta, self).__init__((_SingleExchangeItem(itemCD), parentCD, xpCost), key='confirmExchangeDialog/exchangeXp')
        g_clientUpdateManager.addCurrencyCallback(Currency.GOLD, self._onStatsChanged)
        g_clientUpdateManager.addCallbacks({'shop.freeXPConversion': self._onStatsChanged,
         'inventory.1': self._onStatsChanged,
         'stats.vehTypeXP': self._onStatsChanged,
         'stats.freeXP': self._onStatsChanged,
         'stats.unlocks': self.__checkUnlocks})

    def destroy(self):
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
