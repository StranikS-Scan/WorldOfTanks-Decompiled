# Embedded file name: scripts/client/gui/Scaleform/daapi/view/dialogs/ExchangeDialogMeta.py
import math
import Event
import operator
import BigWorld
from adisp import async
from gui.Scaleform.genConsts.TEXT_MANAGER_STYLES import TEXT_MANAGER_STYLES
from gui.shared.gui_items import GUI_ITEM_TYPE
from helpers import i18n
from gui import game_control
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.shared import events
from gui.shared.utils import decorators, CLIP_ICON_PATH
from gui.shared.ItemsCache import g_itemsCache
from gui.shared.utils.requesters.ItemsRequester import REQ_CRITERIA
from gui.shared.gui_items.processors.common import FreeXPExchanger, GoldToCreditsExchanger
from gui.shared.formatters import icons, text_styles
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.DIALOGS import DIALOGS
from gui.Scaleform.daapi.view.dialogs import I18nConfirmDialogMeta
from gui.Scaleform.daapi.view.lobby.techtree.settings import UnlockStats
from gui.Scaleform.framework import ScopeTemplates
from gui.Scaleform.genConsts.CONFIRM_EXCHANGE_DIALOG_TYPES import CONFIRM_EXCHANGE_DIALOG_TYPES
from gui.Scaleform.genConsts.ICON_TEXT_FRAMES import ICON_TEXT_FRAMES
STEP_SIZE = 1
I18N_NEEDGOLDTEXT_KEY = '{0:>s}/needGoldText'
I18N_NEEDITEMSTEXT_KEY = '{0:>s}/needItemsText'
I18N_GOLDNOTENOUGHTEXT_KEY = '{0:>s}/goldNotEnoughText'
I18N_EXCHANGENONEEDTEXT_KEY = '{0:>s}/exchangeNoNeedText'
I18N_NEEDITEMSSTEPPERTITLE_KEY = '{0:>s}/needItemsStepperTitle'

class _ExchangeDialogMeta(I18nConfirmDialogMeta):

    def __init__(self, key, typeCompactDescr):
        self.__typeCompactDescr = typeCompactDescr
        self.onInvalidate = Event.Event()
        self.onCloseDialog = Event.Event()
        self._items = g_itemsCache.items
        super(_ExchangeDialogMeta, self).__init__(key, scope=ScopeTemplates.LOBBY_SUB_SCOPE)
        game_control.g_instance.wallet.onWalletStatusChanged += self._onStatsChanged

    def destroy(self):
        self._items = None
        game_control.g_instance.wallet.onWalletStatusChanged -= self._onStatsChanged
        self.onInvalidate.clear()
        self.onCloseDialog.clear()
        return

    def getEventType(self):
        return events.ShowDialogEvent.SHOW_EXCHANGE_DIALOG

    def getTypeCompDescr(self):
        return self.__typeCompactDescr

    def submit(self, gold, valueToExchange, callback = None):
        raise NotImplementedError()

    def getExchangeRate(self):
        raise NotImplementedError()

    def getType(self):
        raise NotImplementedError()

    def makeVO(self):
        item = self._items.getItemByCD(self.getTypeCompDescr())
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
         'icon': self.__getIcon(item) if self.__getIconType(item) == CONFIRM_EXCHANGE_DIALOG_TYPES.VEHICLE_ICON else item.getGUIEmblemID(),
         'iconType': self.__getIconType(item),
         'itemName': text_styles.middleTitle(item.userName),
         'needItemsText': self.__getResourceToExchangeTxt(resToExchange),
         'needGoldText': self.__getGoldToExchangeTxt(resToExchange),
         'exchangeBlockData': self.__getExchangeBlockData(resToExchange)}

    def _getCurrencyTxt(self, strResource):
        return text_styles.error(self._makeString(I18N_NEEDITEMSTEXT_KEY.format(self._key), {'value': strResource}))

    def _getExchangeTxt(self, strGold):
        return text_styles.main(self._makeString(I18N_NEEDGOLDTEXT_KEY.format(self._key), {'gold': strGold}))

    def _getResourceStepperTxt(self):
        return text_styles.main(self._makeString(I18N_NEEDITEMSSTEPPERTITLE_KEY.format(self._key), {}))

    def _getNoNeedExchangeStateTxt(self):
        return text_styles.success(self._makeString(I18N_EXCHANGENONEEDTEXT_KEY.format(self._key), {}))

    def _getNotEnoughGoldStateTxt(self, strGold):
        return text_styles.error(self._makeString(I18N_GOLDNOTENOUGHTEXT_KEY.format(self._key), {'gold': strGold}))

    def _onStatsChanged(self, *args):
        self.onInvalidate()

    def _getStepSize(self):
        return STEP_SIZE

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

    def _getExchangeRateItemsIcon(self):
        raise NotImplementedError()

    def _getMaxExchangeValue(self):
        raise NotImplementedError()

    def __getExchangeBlockData(self, resToExchange):
        goldStepperTitleStr = i18n.makeString(DIALOGS.CONFIRMEXCHANGEDIALOG_GOLDITEMSSTEPPERTITLE)
        goldStepperTitleFmt = text_styles.main(goldStepperTitleStr)
        return {'exchangeRateItemsIcon': self._getExchangeRateItemsIcon(),
         'goldStepperTitle': goldStepperTitleFmt,
         'needItemsIcon': self._getCurrencyIconPath(),
         'needItemsStepperTitle': self._getResourceStepperTxt(),
         'goldIcon': RES_ICONS.MAPS_ICONS_LIBRARY_GOLDICON_2,
         'defaultExchangeRate': self._getDefaultExchangeRate(),
         'exchangeRate': self.getExchangeRate(),
         'defaultGoldValue': self.__getGoldToExchange(resToExchange),
         'goldStepSize': self._getStepSize(),
         'maxGoldValue': self._getMaxExchangeValue(),
         'goldTextColorId': TEXT_MANAGER_STYLES.GOLD_TEXT,
         'itemsTextColorId': self._getColorScheme()}

    def __getState(self, resToExchange):
        if resToExchange <= 0:
            return (CONFIRM_EXCHANGE_DIALOG_TYPES.EXCHANGE_NOT_NEEED_STATE, self._getNoNeedExchangeStateTxt())
        elif not self.__isEnoughGold(resToExchange):
            goldToExchange = self.__getGoldToExchange(resToExchange)
            fmtGold = self.__getGoldValueWithIcon(goldToExchange)
            return (CONFIRM_EXCHANGE_DIALOG_TYPES.NOT_ENOUGH_GOLD_STATE, self._getNotEnoughGoldStateTxt(fmtGold))
        else:
            return (CONFIRM_EXCHANGE_DIALOG_TYPES.NORMAL_STATE, '')

    def __isEnoughGold(self, resToExchange):
        return self.__getGoldToExchange(resToExchange) <= self._items.stats.gold

    def __getResourceToExchangeTxt(self, resToExchange):
        if resToExchange > 0:
            resource = BigWorld.wg_getIntegralFormat(resToExchange)
            resStr = self._getCurrencyFormat()(resource) + self._getCurrencyIconStr()
            return self._getCurrencyTxt(resStr)
        return ''

    def __getGoldToExchangeTxt(self, resToExchange):
        if resToExchange > 0:
            goldToExchange = self.__getGoldToExchange(resToExchange)
            fmtGold = self.__getGoldValueWithIcon(goldToExchange)
            return self._getExchangeTxt(fmtGold)
        return ''

    def __getGoldValueWithIcon(self, gold):
        return ''.join(text_styles.gold(BigWorld.wg_getGoldFormat(gold)) + icons.gold())

    def __getGoldToExchange(self, resToExchange):
        if resToExchange > 0:
            return int(math.ceil(float(resToExchange) / self.getExchangeRate()))
        return 0

    def __getIconType(self, item):
        if item.itemTypeID == GUI_ITEM_TYPE.VEHICLE:
            return CONFIRM_EXCHANGE_DIALOG_TYPES.VEHICLE_ICON
        return CONFIRM_EXCHANGE_DIALOG_TYPES.MODULE_ICON

    def __getIcon(self, item):
        if item.itemTypeID == GUI_ITEM_TYPE.VEHICLE:
            icon = item.type
            if item.isElite:
                icon += '_elite'
            return icon
        if item.itemTypeID not in (GUI_ITEM_TYPE.OPTIONALDEVICE, GUI_ITEM_TYPE.SHELL, GUI_ITEM_TYPE.EQUIPMENT):
            return str(item.level)
        return item.icon


class ExchangeCreditsMeta(_ExchangeDialogMeta):

    def __init__(self, itemCD, installVehicle = None):
        super(ExchangeCreditsMeta, self).__init__('confirmExchangeDialog/exchangeCredits', itemCD)
        item = self._items.getItemByCD(self.getTypeCompDescr())
        self.__installVehicleCD = installVehicle
        self.__isInstalled = False
        if item and item.itemTypeID != GUI_ITEM_TYPE.VEHICLE and self.__installVehicleCD:
            vehicle = self._items.getItemByCD(self.__installVehicleCD)
            self.__isInstalled = item.isInstalled(vehicle)
        self.__inventoryCount = 0
        if item:
            self.__inventoryCount = item.inventoryCount
        g_clientUpdateManager.addCallbacks({'stats.credits': self._onStatsChanged,
         'stats.gold': self._onStatsChanged,
         'shop.exchangeRate': self._onStatsChanged,
         'inventory.1': self._checkInventory})

    def destroy(self):
        self.__inventoryCount = None
        self.__installVehicleCD = None
        g_clientUpdateManager.removeObjectCallbacks(self)
        super(ExchangeCreditsMeta, self).destroy()
        return

    @async
    @decorators.process('transferMoney')
    def submit(self, gold, exchangedCredits, callback = None):
        result = yield GoldToCreditsExchanger(gold).request()
        if callback is not None:
            callback(result)
        return

    def getType(self):
        return CONFIRM_EXCHANGE_DIALOG_TYPES.TYPE_CREDITS_EXCHANGE

    def getExchangeRate(self):
        return self._items.shop.exchangeRate

    def _getDefaultExchangeRate(self):
        return self._items.shop.defaults.exchangeRate

    def _getCurrencyIconStr(self):
        return icons.credits()

    def _checkInventory(self, *args):
        item = self._items.getItemByCD(self.getTypeCompDescr())
        if item:
            if item.itemTypeID == GUI_ITEM_TYPE.VEHICLE and item.isInInventory:
                self.onCloseDialog()
            elif item.inventoryCount > self.__inventoryCount:
                self.onCloseDialog()
            elif self.__installVehicleCD:
                vehicle = self._items.getItemByCD(self.__installVehicleCD)
                if not self.__isInstalled and item.isInstalled(vehicle):
                    self.onCloseDialog()

    def _getCurrencyFormat(self):
        return text_styles.credits

    def _getCurrencyIconPath(self):
        return RES_ICONS.MAPS_ICONS_LIBRARY_CREDITSICON_2

    def _getMaxExchangeValue(self):
        return self._items.stats.actualGold

    def _getResourceToExchange(self):
        item = self._items.getItemByCD(self.getTypeCompDescr())
        price = item.altPrice or item.buyPrice
        return price[0] - self._items.stats.credits

    def _getColorScheme(self):
        return TEXT_MANAGER_STYLES.CREDITS_TEXT

    def _getExchangeRateItemsIcon(self):
        return ICON_TEXT_FRAMES.CREDITS


class ExchangeXpMeta(_ExchangeDialogMeta):

    def __init__(self, itemCD, parentCD, xpCost):
        super(ExchangeXpMeta, self).__init__('confirmExchangeDialog/exchangeXp', itemCD)
        self._parentCD = parentCD
        self._xpCost = xpCost
        g_clientUpdateManager.addCallbacks({'stats.gold': self._onStatsChanged,
         'shop.freeXPConversion': self._onStatsChanged,
         'inventory.1': self._onStatsChanged,
         'stats.vehTypeXP': self._onStatsChanged,
         'stats.freeXP': self._onStatsChanged,
         'stats.unlocks': self._checkUnlcoks})

    def destroy(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        self._parentCD = None
        self._xpCost = None
        super(ExchangeXpMeta, self).destroy()
        return

    @async
    @decorators.process('exchangeVehiclesXP')
    def submit(self, gold, xpToExchange, callback = None):
        criteria = REQ_CRITERIA.VEHICLE.FULLY_ELITE | ~REQ_CRITERIA.IN_CD_LIST([self._parentCD])
        eliteVehicles = self._items.getVehicles(criteria).keys()
        result = yield FreeXPExchanger(xpToExchange, eliteVehicles).request()
        if callback is not None:
            callback(result)
        return

    def getType(self):
        return CONFIRM_EXCHANGE_DIALOG_TYPES.TYPE_XP_EXCHANGE

    def getExchangeRate(self):
        return self._items.shop.freeXPConversion[0]

    def _getDefaultExchangeRate(self):
        return self._items.shop.defaults.freeXPConversion[0]

    def _checkUnlcoks(self, *args):
        item = self._items.getItemByCD(self.getTypeCompDescr())
        if item and item.isUnlocked:
            self.onCloseDialog()

    def _getResourceToExchange(self):
        item = self._items.getItemByCD(self.getTypeCompDescr())
        stats = self._items.stats
        unlockStats = UnlockStats(stats.unlocks, stats.vehiclesXPs, stats.freeXP)
        if item.isUnlocked:
            return 0
        else:
            return self._xpCost - unlockStats.getVehTotalXP(self._parentCD)

    def _getCurrencyIconStr(self):
        return icons.freeXP()

    def _getCurrencyIconPath(self):
        return RES_ICONS.MAPS_ICONS_LIBRARY_ELITEXPICON_2

    def _getCurrencyFormat(self):
        return text_styles.expText

    def _getMaxExchangeValue(self):
        eliteVehicles = self._items.getVehicles(REQ_CRITERIA.VEHICLE.FULLY_ELITE).values()
        result = sum(map(operator.attrgetter('xp'), eliteVehicles))
        return min(int(result / self.getExchangeRate()), self._items.stats.actualGold)

    def _getColorScheme(self):
        return TEXT_MANAGER_STYLES.NEUTRAL_TEXT

    def _getExchangeRateItemsIcon(self):
        return ICON_TEXT_FRAMES.ELITE_XP
