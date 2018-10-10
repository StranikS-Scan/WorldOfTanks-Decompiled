# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/exchange/ExchangeXPWindow.py
import BigWorld
from gui import SystemMessages
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform import getVehicleTypeAssetPath, getNationsAssetPath, NATION_ICON_PREFIX_131x31
from gui.Scaleform.daapi.view.lobby.store.browser.ingameshop_helpers import isIngameShopEnabled
from gui.Scaleform.daapi.view.meta.ExchangeXpWindowMeta import ExchangeXpWindowMeta
from gui.Scaleform.genConsts.ICON_TEXT_FRAMES import ICON_TEXT_FRAMES
from gui.Scaleform.locale.DIALOGS import DIALOGS
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.ingame_shop import showBuyGoldForXpWebOverlay
from gui.shared.formatters import icons
from gui.shared.formatters.text_styles import builder
from gui.shared.gui_items.gui_item_economics import ItemPrice
from gui.shared.gui_items.processors.common import FreeXPExchanger
from gui.shared.money import Currency, Money
from gui.shared.utils.decorators import process
from helpers import i18n, dependency
from skeletons.gui.game_control import IWalletController
from skeletons.gui.shared import IItemsCache

class ExchangeXPWindow(ExchangeXpWindowMeta):
    itemsCache = dependency.descriptor(IItemsCache)
    wallet = dependency.descriptor(IWalletController)

    def __init__(self, ctx=None):
        super(ExchangeXPWindow, self).__init__(ctx)
        self.__isIngameShopEnabled = False

    def _populate(self):
        super(ExchangeXPWindow, self)._populate()
        self.__xpForFree = self.itemsCache.items.shop.freeXPConversionLimit
        self.as_setPrimaryCurrencyS(self.itemsCache.items.stats.actualGold)
        self.__setRates()
        self.as_totalExperienceChangedS(self.itemsCache.items.stats.actualFreeXP)
        self.__isIngameShopEnabled = isIngameShopEnabled()
        self.__prepareAndPassVehiclesData()
        self.as_setWalletStatusS(self.wallet.status, self.__isIngameShopEnabled)

    def _subscribe(self):
        g_clientUpdateManager.addCurrencyCallback(Currency.GOLD, self._setGoldCallBack)
        g_clientUpdateManager.addCallbacks({'shop.freeXPConversion': self.__setXPConversationCallBack,
         'shop.goodies': self.__discountChangedCallback,
         'goodies.4': self.__discountChangedCallback,
         'inventory.1': self.__vehiclesDataChangedCallBack,
         'stats.vehTypeXP': self.__vehiclesDataChangedCallBack,
         'stats.freeXP': self.__setFreeXPCallBack})
        self.wallet.onWalletStatusChanged += self.__setWalletCallback
        self.itemsCache.onSyncCompleted += self.__setXPConversationCallBack

    def __vehiclesDataChangedCallBack(self, _):
        self.__prepareAndPassVehiclesData()

    def __setFreeXPCallBack(self, value):
        self.as_totalExperienceChangedS(value)

    def __setXPConversationCallBack(self, *args):
        self.__setRates()

    def __setWalletCallback(self, status):
        self.as_setPrimaryCurrencyS(self.itemsCache.items.stats.actualGold)
        self.as_totalExperienceChangedS(self.itemsCache.items.stats.actualFreeXP)
        self.as_setWalletStatusS(status, self.__isIngameShopEnabled)

    def __prepareAndPassVehiclesData(self):
        values = []
        for vehicleCD in self.itemsCache.items.stats.eliteVehicles:
            try:
                vehicle = self.itemsCache.items.getItemByCD(vehicleCD)
                if not vehicle.xp:
                    continue
                values.append({'id': vehicle.intCD,
                 'vehicleType': getVehicleTypeAssetPath(vehicle.type),
                 'vehicleName': vehicle.shortUserName,
                 'xp': vehicle.xp,
                 'xpStrValue': BigWorld.wg_getIntegralFormat(vehicle.xp),
                 'isSelectCandidate': vehicle.isFullyElite,
                 'vehicleIco': vehicle.iconSmall,
                 'nationIco': getNationsAssetPath(vehicle.nationID, namePrefix=NATION_ICON_PREFIX_131x31)})
            except Exception:
                continue

        labelBuilder = builder().addStyledText('middleTitle', i18n.makeString(MENU.EXCHANGE_RATE))
        if self.__xpForFree is not None:
            labelBuilder.addStyledText(self.__getActionStyle(), i18n.makeString(MENU.EXCHANGEXP_AVAILABLE_FORFREE_LABEL))
            labelBuilder.addStyledText('expText', i18n.makeString(MENU.EXCHANGEXP_AVAILABLE_FORFREE_VALUE, icon=icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_ELITEXPICON_2), forFree=BigWorld.wg_getNiceNumberFormat(self.__xpForFree)))
        exchangeHeaderData = {'labelText': labelBuilder.render(),
         'rateFromIcon': ICON_TEXT_FRAMES.GOLD,
         'rateToIcon': ICON_TEXT_FRAMES.ELITE_XP,
         'rateFromTextColor': self.app.colorManager.getColorScheme('textColorGold').get('rgb'),
         'rateToTextColor': self.app.colorManager.getColorScheme('textColorCredits').get('rgb')}
        vehicleData = {'buyGoldAvailable': self.__isIngameShopEnabled,
         'isHaveElite': bool(values),
         'vehicleList': values,
         'tableHeader': self._getTableHeader(),
         'xpForFree': self.__xpForFree,
         'exchangeHeaderData': exchangeHeaderData}
        self.as_vehiclesDataChangedS(vehicleData)
        return

    def _getTableHeader(self):
        return [self._createTableBtnInfo('isSelectCandidate', 40, 2, DIALOGS.GATHERINGXPFORM_SORTBY_SELECTION, 'ascending', RES_ICONS.MAPS_ICONS_BUTTONS_TAB_SORT_BUTTON_OK), self._createTableBtnInfo('vehicleName', 179, 1, DIALOGS.GATHERINGXPFORM_SORTBY_VEHICLE, 'ascending', RES_ICONS.MAPS_ICONS_BUTTONS_TAB_SORT_BUTTON_TANK, sortType='string'), self._createTableBtnInfo('xp', 103, 0, DIALOGS.GATHERINGXPFORM_SORTBY_XP, 'descending', RES_ICONS.MAPS_ICONS_BUTTONS_TAB_SORT_BUTTON_XP)]

    def _createTableBtnInfo(self, btnID, buttonWidth, sortOrder, toolTip, defaultSortDirection, iconSource, sortType='numeric'):
        return {'id': btnID,
         'buttonWidth': buttonWidth,
         'sortOrder': sortOrder,
         'toolTip': toolTip,
         'defaultSortDirection': defaultSortDirection,
         'iconSource': iconSource,
         'sortType': sortType,
         'ascendingIconSource': '../maps/icons/buttons/tab_sort_button/ascendingSortArrow.png',
         'descendingIconSource': '../maps/icons/buttons/tab_sort_button/descendingSortArrow.png',
         'buttonHeight': 30}

    @process('exchangeVehiclesXP')
    def exchange(self, data):
        exchangeXP = data.exchangeXp
        vehTypeCompDescrs = list(data.selectedVehicles)
        eliteVcls = self.itemsCache.items.stats.eliteVehicles
        xps = self.itemsCache.items.stats.vehiclesXPs
        commonXp = 0
        for vehicleCD in vehTypeCompDescrs:
            if vehicleCD in eliteVcls:
                commonXp += xps.get(vehicleCD, 0)

        xpToExchange = min(commonXp, exchangeXP)
        money = self.itemsCache.items.stats.money
        price = self.__getConversionPrice(xpToExchange).price
        if money.gold < price.gold and self.__isIngameShopEnabled:
            showBuyGoldForXpWebOverlay(price.gold)
        else:
            result = yield FreeXPExchanger(xpToExchange, vehTypeCompDescrs, freeConversion=self.__xpForFree).request()
            if result.userMsg:
                SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)
            if result.success:
                self.destroy()

    def onWindowClose(self):
        self.destroy()

    def getSubmitButtonEnableState(self, selectedXPCount):
        if selectedXPCount == 0:
            return False
        money = self.itemsCache.items.stats.money
        price = self.__getConversionPrice(selectedXPCount).price
        return True if price.gold <= money.gold else self.__isIngameShopEnabled

    def _dispose(self):
        self.itemsCache.onSyncCompleted -= self.__setXPConversationCallBack
        self.wallet.onWalletStatusChanged -= self.__setWalletCallback
        g_clientUpdateManager.removeObjectCallbacks(self)
        super(ExchangeXPWindow, self)._dispose()

    def __discountChangedCallback(self, _):
        self.__setRates()
        newLimit = self.itemsCache.items.shop.freeXPConversionLimit
        if newLimit != self.__xpForFree:
            self.__xpForFree = newLimit
            self.__prepareAndPassVehiclesData()

    def __setRates(self):
        rate = self.itemsCache.items.shop.freeXPConversionWithDiscount
        defaultRate = self.itemsCache.items.shop.defaults.freeXPConversion
        self.as_exchangeRateS({'value': defaultRate[0],
         'actionValue': rate[0],
         'actionMode': self.itemsCache.items.shop.isXPConversionActionActive})

    def __getConversionPrice(self, xp):

        def computeCost(xp, rate, cost):
            return round(cost * xp / rate)

        rate, cost = self.itemsCache.items.shop.freeXPConversionWithDiscount
        defRate, defCost = self.itemsCache.items.shop.defaults.freeXPConversion
        return ItemPrice(Money(gold=computeCost(xp, rate, cost)), Money(gold=computeCost(xp, defRate, defCost)))

    def __getActionStyle(self):
        rate = self.itemsCache.items.shop.defaults.freeXPConversion
        actionRate = self.itemsCache.items.shop.freeXPConversionWithDiscount
        return 'statsText' if rate != actionRate and actionRate > 0 else 'alertText'
