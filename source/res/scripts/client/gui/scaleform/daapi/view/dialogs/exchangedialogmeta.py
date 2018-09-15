# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/dialogs/ExchangeDialogMeta.py
import math
import operator
import BigWorld
import Event
from adisp import async
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.view.dialogs import I18nConfirmDialogMeta
from gui.Scaleform.daapi.view.lobby.techtree.settings import UnlockStats
from gui.Scaleform.framework import ScopeTemplates
from gui.Scaleform.genConsts.CONFIRM_EXCHANGE_DIALOG_TYPES import CONFIRM_EXCHANGE_DIALOG_TYPES
from gui.Scaleform.genConsts.ICON_TEXT_FRAMES import ICON_TEXT_FRAMES
from gui.Scaleform.genConsts.TEXT_MANAGER_STYLES import TEXT_MANAGER_STYLES
from gui.Scaleform.locale.DIALOGS import DIALOGS
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.managers.ColorSchemeManager import ColorSchemeManager
from gui.shared import events
from gui.shared.formatters import icons, text_styles
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.processors.common import FreeXPExchanger, GoldToCreditsExchanger
from gui.shared.money import Currency
from gui.shared.utils import decorators, CLIP_ICON_PATH
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

class _ExchangeDialogMeta(I18nConfirmDialogMeta):
    itemsCache = dependency.descriptor(IItemsCache)
    wallet = dependency.descriptor(IWalletController)

    def __init__(self, typeCompactDescr, key):
        self.__typeCompactDescr = typeCompactDescr
        self.onInvalidate = Event.Event()
        self.onCloseDialog = Event.Event()
        self.colorManager = ColorSchemeManager()
        super(_ExchangeDialogMeta, self).__init__(key, scope=ScopeTemplates.LOBBY_SUB_SCOPE)
        self.wallet.onWalletStatusChanged += self._onStatsChanged

    def destroy(self):
        """
        destroy operation after exchange dialog close
        """
        self.wallet.onWalletStatusChanged -= self._onStatsChanged
        self.onInvalidate.clear()
        self.onCloseDialog.clear()

    def getEventType(self):
        """
        EventType to open ConfirmExchangeDialog
        :return:<str> eventType "showExchangeDialog"
        """
        return events.ShowDialogEvent.SHOW_EXCHANGE_DIALOG

    def getTypeCompDescr(self):
        """
        Gets item compact descriptor
        :return: <int> item compact descriptor
        """
        return self.__typeCompactDescr

    def submit(self, gold, valueToExchange, callback=None):
        """
        Submit exchange operation, send request to exchange and call callback after response received
        :param gold: <int> gold value
        :param valueToExchange: <int> credits or xp value to exchange
        :param callback: <function>
        """
        raise NotImplementedError()

    def getExchangeRate(self):
        """
        Get exchange rate rate for defined currency
        May return shop.exchangeRate for gold exchange
        or shop.freeXPConversion[0] for xp exchange
        :return: <int> exchange rate for defined currency
        """
        raise NotImplementedError()

    def getType(self):
        """
        :return: <str> confirm exchange dialog type for unique name for _ExchangeDialogBusinessHandler
        """
        raise NotImplementedError()

    def makeVO(self):
        """
        Makes VO for ConfirmExchangeDialog
        :return: <obj>
        """
        item = self.itemsCache.items.getItemByCD(self.getTypeCompDescr())
        resToExchange = self._getResourceToExchange()
        extraData = None
        if item.itemTypeID == GUI_ITEM_TYPE.GUN and item.isClipGun():
            extraData = CLIP_ICON_PATH
        state, stateMsg = self.__getState(resToExchange)
        return {'title': self.getTitle(),
         'exchangeBtnText': self.getButtonLabels()[0]['label'],
         'cancelBtnText': self.getButtonLabels()[1]['label'],
         'state': state,
         'lockExchangeMessage': stateMsg,
         'iconExtraInfo': extraData,
         'iconModuleType': item.itemTypeName,
         'icon': self.__getItemIcon(item),
         'iconType': self.__getItemIconType(item),
         'itemName': text_styles.middleTitle(item.userName),
         'needItemsText': self.__getResourceToExchangeTxt(resToExchange),
         'needGoldText': self.__getGoldToExchangeTxt(resToExchange),
         'exchangeBlockData': self.__getExchangeBlockData(resToExchange)}

    def _onStatsChanged(self, *args):
        """
        call onInvalidate Event on account stats changes
        """
        self.onInvalidate()

    def _getDefaultExchangeRate(self):
        """
        Gets shop default exchange rate for defined currency
        :return: <int>
        """
        raise NotImplementedError()

    def _getResourceToExchange(self):
        """
        # calculate necessary resource for exchange (credits, xp, ...)
        :return: <int>
        """
        raise NotImplementedError()

    def _getCurrencyIconStr(self):
        """
        Gets html currency icon
        :return: <str>
        """
        raise NotImplementedError()

    def _getCurrencyIconPath(self):
        """
        Gets currency icon path
        :return: <str>
        """
        raise NotImplementedError()

    def _getCurrencyFormat(self):
        """
        Gets text_style format for resource to exchange text
        :return: <function>
        """
        raise NotImplementedError()

    def _getColorScheme(self):
        """
        Gets color scheme ID for itemsText
        :return: <str>
        """
        raise NotImplementedError()

    def _getRateToColorScheme(self):
        """
        Gets color scheme ID for rateToTextColor field
        :return: <str>
        """
        raise NotImplementedError()

    def _getExchangeRateItemsIcon(self):
        """
        :return: <str> frame for  GUI rateToIcon field
        """
        raise NotImplementedError()

    def _getMaxExchangeValue(self):
        """
        Calculates max available resource value for exchange
        :return: <int>
        """
        raise NotImplementedError()

    def _getRGB(self, colorId):
        """
        :param colorId:  <str>
        :return: <obj> RGB color scheme
        """
        return self.colorManager.getColorScheme(colorId).get('rgb')

    def _makeString(self, key, ctx=None):
        """
        :param key: <str> localization key
        :param ctx: <obj> lcalisation context
        :return: <str> localized value
        """
        ctx = ctx or {}
        i18nKey = key.format(self._key)
        return super(_ExchangeDialogMeta, self)._makeString(i18nKey, ctx)

    def __getExchangeBlockData(self, resToExchange):
        """
        Makes VO for exchangeBlockData field
        :param resToExchange: <int> resource value for exchange
        :return: <obj>
        """
        goldStepperTitleStr = i18n.makeString(DIALOGS.CONFIRMEXCHANGEDIALOG_GOLDITEMSSTEPPERTITLE)
        goldStepperTitleFmt = text_styles.main(goldStepperTitleStr)
        exchangeHeaderData = {'labelText': i18n.makeString(MENU.EXCHANGE_RATE),
         'rateFromIcon': ICON_TEXT_FRAMES.GOLD,
         'rateToIcon': self._getExchangeRateItemsIcon(),
         'rateFromTextColor': self._getRGB(TEXT_COLOR_ID_XP),
         'rateToTextColor': self._getRGB(self._getRateToColorScheme())}
        needItemsStepperTitle = text_styles.main(self._makeString(I18N_NEEDITEMSSTEPPERTITLE_KEY))
        return {'goldStepperTitle': goldStepperTitleFmt,
         'needItemsIcon': self._getCurrencyIconPath(),
         'needItemsStepperTitle': needItemsStepperTitle,
         'goldIcon': RES_ICONS.MAPS_ICONS_LIBRARY_GOLDICON_2,
         'defaultExchangeRate': self._getDefaultExchangeRate(),
         'exchangeRate': self.getExchangeRate(),
         'defaultGoldValue': self.__getGoldToExchange(resToExchange),
         'goldStepSize': STEP_SIZE,
         'maxGoldValue': self._getMaxExchangeValue(),
         'goldTextColorId': TEXT_MANAGER_STYLES.GOLD_TEXT,
         'itemsTextColorId': self._getColorScheme(),
         'exchangeHeaderData': {'labelText': '',
                                'rateFromIcon': ICON_TEXT_FRAMES.GOLD,
                                'rateToIcon': self._getExchangeRateItemsIcon(),
                                'rateFromTextColor': self._getRGB(TEXT_COLOR_ID_XP),
                                'rateToTextColor': self._getRGB(self._getRateToColorScheme())}}

    def __getState(self, resToExchange):
        """
        Gets state and reason for exchange possibility
        :param resToExchange: <int> resource for exchange
        :return: <tuple(state:<int>, reason<str>)>
        """
        if resToExchange <= 0:
            return (CONFIRM_EXCHANGE_DIALOG_TYPES.EXCHANGE_NOT_NEEED_STATE, text_styles.success(self._makeString(I18N_EXCHANGENONEEDTEXT_KEY)))
        elif not self.__isEnoughGold(resToExchange):
            goldToExchange = self.__getGoldToExchange(resToExchange)
            fmtGold = ''.join((text_styles.gold(BigWorld.wg_getGoldFormat(goldToExchange)), icons.gold()))
            return (CONFIRM_EXCHANGE_DIALOG_TYPES.NOT_ENOUGH_GOLD_STATE, text_styles.error(self._makeString(I18N_GOLDNOTENOUGHTEXT_KEY, {'gold': fmtGold})))
        else:
            return (CONFIRM_EXCHANGE_DIALOG_TYPES.NORMAL_STATE, '')

    def __isEnoughGold(self, resToExchange):
        """
        Checks if enough gold for exchange operation
        :param resToExchange: <int> resource for exchange
        :return: <bool>
        """
        return self.__getGoldToExchange(resToExchange) <= self.itemsCache.items.stats.gold

    def __getResourceToExchangeTxt(self, resToExchange):
        """
        :param resToExchange: <int> resource for exchange
        :return: <str> formatted needed resource to exchange text
        """
        if resToExchange > 0:
            resource = BigWorld.wg_getIntegralFormat(resToExchange)
            resStr = self._getCurrencyFormat()(resource) + self._getCurrencyIconStr()
            return text_styles.error(self._makeString(I18N_NEEDITEMSTEXT_KEY, {'value': resStr}))

    def __getGoldToExchangeTxt(self, resToExchange):
        """
        :param resToExchange: <int> resource for exchange
        :return: formatted needed gold to exchange text
        """
        if resToExchange > 0:
            goldToExchange = self.__getGoldToExchange(resToExchange)
            fmtGold = ''.join((text_styles.gold(BigWorld.wg_getGoldFormat(goldToExchange)), icons.gold()))
            return text_styles.main(self._makeString(I18N_NEEDGOLDTEXT_KEY, {'gold': fmtGold}))

    def __getGoldToExchange(self, resToExchange):
        """
        :param resToExchange: <int> resource for exchange
        :return: <int> gold for exchange
        """
        return int(math.ceil(float(resToExchange) / self.getExchangeRate())) if resToExchange > 0 else 0

    def __getItemIconType(self, item):
        """
        Gets item icon type for Flash component
        :param item: <GUIItem>
        :return: <int> icon type
        """
        return CONFIRM_EXCHANGE_DIALOG_TYPES.VEHICLE_ICON if item.itemTypeID == GUI_ITEM_TYPE.VEHICLE else CONFIRM_EXCHANGE_DIALOG_TYPES.MODULE_ICON

    def __getItemIcon(self, item):
        """
        Gets item icon frame for Flash component
        :param item: <GUIItem>
        :return:
        """
        if item.itemTypeID == GUI_ITEM_TYPE.VEHICLE:
            icon = item.type
            if item.isElite:
                icon += '_elite'
            return icon
        else:
            return item.getGUIEmblemID()


class ExchangeCreditsMeta(_ExchangeDialogMeta):

    def __init__(self, itemCD, installVehicle=None, key='confirmExchangeDialog/exchangeCredits'):
        """
        # Meta for ConfirmExchangeDialog
        # allows to exchange gold for credits by purchasing item
        :param itemCD: <int> item compact descriptor
        :param installVehicle: <int> installed vehicle compact descriptor
        :param key: <str> localization key
        """
        super(ExchangeCreditsMeta, self).__init__(itemCD, key)
        item = self.itemsCache.items.getItemByCD(self.getTypeCompDescr())
        self.__installVehicleCD = installVehicle
        self.__isInstalled = False
        if item and item.itemTypeID != GUI_ITEM_TYPE.VEHICLE and self.__installVehicleCD:
            vehicle = self.itemsCache.items.getItemByCD(self.__installVehicleCD)
            self.__isInstalled = item.isInstalled(vehicle)
        self.__inventoryCount = 0
        if item:
            self.__inventoryCount = item.inventoryCount
        g_clientUpdateManager.addMoneyCallback(self._onStatsChanged)
        g_clientUpdateManager.addCallbacks({'shop.exchangeRate': self._onStatsChanged,
         'inventory.1': self.__checkInventory})

    def destroy(self):
        """
        destroy operation after exchange dialog close
        """
        self.__inventoryCount = None
        self.__installVehicleCD = None
        g_clientUpdateManager.removeObjectCallbacks(self)
        super(ExchangeCreditsMeta, self).destroy()
        return

    @async
    @decorators.process('transferMoney')
    def submit(self, gold, exchangedCredits, callback=None):
        """
        Submit exchange operation, send request to exchange and call callback after response received
        :param gold: <int> gold value
        :param exchangedCredits: <int> credits value to exchange
        :param callback: <function>
        """
        result = yield GoldToCreditsExchanger(gold).request()
        if callback is not None:
            callback(result)
        return

    def getType(self):
        """
        :return: <str> confirm exchange dialog type for unique name for _ExchangeDialogBusinessHandler
        """
        return CONFIRM_EXCHANGE_DIALOG_TYPES.TYPE_CREDITS_EXCHANGE

    def getExchangeRate(self):
        """
        :return: <int> exchange rate for gold
        """
        return self.itemsCache.items.shop.exchangeRate

    def _getDefaultExchangeRate(self):
        """
        Gets shop default exchange rate for gold
        :return: <int>
        """
        return self.itemsCache.items.shop.defaults.exchangeRate

    def _getCurrencyIconStr(self):
        """
        Gets html credits icon
        :return: <str>
        """
        return icons.credits()

    def _getCurrencyFormat(self):
        """
        Gets text_style format for credits to exchange text
        :return: <function>
        """
        return text_styles.credits

    def _getCurrencyIconPath(self):
        """
        Gets currency icon path
        :return: <str>
        """
        return RES_ICONS.MAPS_ICONS_LIBRARY_CREDITSICON_2

    def _getMaxExchangeValue(self):
        """
        Calculates max available gold value for exchange
        :return: <int>
        """
        return self.itemsCache.items.stats.actualGold

    def _getResourceToExchange(self):
        """
        # calculate necessary credits for exchange
        :return: <int>
        """
        item = self.itemsCache.items.getItemByCD(self.getTypeCompDescr())
        return item.buyPrices.itemPrice.price.getSignValue(Currency.CREDITS) - self.itemsCache.items.stats.credits

    def _getRateToColorScheme(self):
        """
        Gets color scheme ID for rateToTextColor field
        :return: <str>
        """
        return TEXT_COLOR_ID_CREDITS

    def _getColorScheme(self):
        """
        Gets color scheme ID for itemsText
        :return: <str>
        """
        return TEXT_MANAGER_STYLES.CREDITS_TEXT

    def _getExchangeRateItemsIcon(self):
        """
        :return: <str> frame for  GUI rateToIcon field
        """
        return ICON_TEXT_FRAMES.CREDITS

    def __checkInventory(self, *args):
        """
        Checks if item is already in inventory
        and call Event onCloseDialog
        """
        item = self.itemsCache.items.getItemByCD(self.getTypeCompDescr())
        if item is not None:
            if item.itemTypeID == GUI_ITEM_TYPE.VEHICLE and item.isInInventory or item.inventoryCount > self.__inventoryCount:
                self.onCloseDialog()
            elif self.__installVehicleCD:
                vehicle = self.itemsCache.items.getItemByCD(self.__installVehicleCD)
                if not self.__isInstalled and item.isInstalled(vehicle):
                    self.onCloseDialog()
        return


class RestoreExchangeCreditsMeta(ExchangeCreditsMeta):
    """
    Meta for ConfirmExchangeDialog
    allows to exchange gold for credits by restoring vehicle
    :param itemCD: <int> vehicle compact descriptor
    :param key: <str> localization key
    """

    def __init__(self, itemCD, key='confirmExchangeDialog/restoreExchangeCredits'):
        super(RestoreExchangeCreditsMeta, self).__init__(itemCD, key=key)

    def _getResourceToExchange(self):
        """
        # calculate necessary credits for exchange by restoring vehicle
        :return: <int> credits
        """
        item = self.itemsCache.items.getItemByCD(self.getTypeCompDescr())
        credits = item.restorePrice.getSignValue(Currency.CREDITS)
        return credits - self.itemsCache.items.stats.credits


class ExchangeXpMeta(_ExchangeDialogMeta):
    """
    Meta for ConfirmExchangeDialog
    allows to exchange gold for freeXp for item unlock
    :param itemCD: <int> item compact descriptor
    :param parentCD: <int> root vehicle compact descriptor
    :param xpCost: <int> xp price to unlock item
    """

    def __init__(self, itemCD, parentCD, xpCost):
        super(ExchangeXpMeta, self).__init__(itemCD, 'confirmExchangeDialog/exchangeXp')
        self._parentCD = parentCD
        self._xpCost = xpCost
        g_clientUpdateManager.addCurrencyCallback(Currency.GOLD, self._onStatsChanged)
        g_clientUpdateManager.addCallbacks({'shop.freeXPConversion': self._onStatsChanged,
         'inventory.1': self._onStatsChanged,
         'stats.vehTypeXP': self._onStatsChanged,
         'stats.freeXP': self._onStatsChanged,
         'stats.unlocks': self.__checkUnlcoks})

    def destroy(self):
        """
        destroy operation after exchange dialog close
        """
        g_clientUpdateManager.removeObjectCallbacks(self)
        self._parentCD = None
        self._xpCost = None
        super(ExchangeXpMeta, self).destroy()
        return

    @async
    @decorators.process('exchangeVehiclesXP')
    def submit(self, gold, xpToExchange, callback=None):
        """
        Submit exchange operation, send request to exchange and call callback after response received
        :param gold: <int> gold value
        :param xpToExchange: <int> xp value to exchange
        :param callback: <function>
        """
        criteria = REQ_CRITERIA.VEHICLE.FULLY_ELITE | ~REQ_CRITERIA.IN_CD_LIST([self._parentCD])
        eliteVehicles = self.itemsCache.items.getVehicles(criteria).keys()
        result = yield FreeXPExchanger(xpToExchange, eliteVehicles).request()
        if callback is not None:
            callback(result)
        return

    def getType(self):
        """
        :return: <str> confirm exchange dialog type for unique name for _ExchangeDialogBusinessHandler
        """
        return CONFIRM_EXCHANGE_DIALOG_TYPES.TYPE_XP_EXCHANGE

    def getExchangeRate(self):
        """
        :return: <int> exchange rate for xp
        """
        return self.itemsCache.items.shop.freeXPConversion[0]

    def _getDefaultExchangeRate(self):
        """
        Gets shop default exchange rate for xp
        :return: <int>
        """
        return self.itemsCache.items.shop.defaults.freeXPConversion[0]

    def _getResourceToExchange(self):
        """
        # calculate necessary xp for exchange
        :return: <int>
        """
        item = self.itemsCache.items.getItemByCD(self.getTypeCompDescr())
        stats = self.itemsCache.items.stats
        unlockStats = UnlockStats(stats.unlocks, stats.vehiclesXPs, stats.freeXP)
        if item.isUnlocked:
            return 0
        else:
            return self._xpCost - unlockStats.getVehTotalXP(self._parentCD)

    def _getCurrencyIconStr(self):
        """
        Gets html currency icon
        :return: <str>
        """
        return icons.freeXP()

    def _getCurrencyIconPath(self):
        """
        Gets currency icon path
        :return: <str>
        """
        return RES_ICONS.MAPS_ICONS_LIBRARY_ELITEXPICON_2

    def _getCurrencyFormat(self):
        """
        Gets text_style format for resource to exchange text
        :return: <function>
        """
        return text_styles.expText

    def _getMaxExchangeValue(self):
        """
        Calculates max available resource value for exchange
        :return: <int>
        """
        eliteVehicles = self.itemsCache.items.getVehicles(REQ_CRITERIA.VEHICLE.FULLY_ELITE).values()
        result = sum(map(operator.attrgetter('xp'), eliteVehicles))
        return min(int(result / self.getExchangeRate()), self.itemsCache.items.stats.actualGold)

    def _getRateToColorScheme(self):
        """
        Gets color scheme ID for rateToTextColor field
        :return: <str>
        """
        return TEXT_COLOR_ID_XP

    def _getColorScheme(self):
        """
        Gets color scheme ID for itemsText
        :return: <str>
        """
        return TEXT_MANAGER_STYLES.STATS_TEXT

    def _getExchangeRateItemsIcon(self):
        """
        :return: <str> frame for  GUI rateToIcon field
        """
        return ICON_TEXT_FRAMES.ELITE_XP

    def __checkUnlcoks(self, *args):
        """
        Checks if item is already unlocked
        and call Event onCloseDialog
        """
        item = self.itemsCache.items.getItemByCD(self.getTypeCompDescr())
        if item is not None and item.isUnlocked:
            self.onCloseDialog()
        return
