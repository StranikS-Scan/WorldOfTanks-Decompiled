# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/exchange/ExchangeXPWindow.py
import BigWorld
from gui import SystemMessages, game_control
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform import getVehicleTypeAssetPath, getNationsAssetPath, NATION_ICON_PREFIX_131x31
from gui.Scaleform.daapi.view.meta.ExchangeXpWindowMeta import ExchangeXpWindowMeta
from gui.Scaleform.locale.DIALOGS import DIALOGS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.shared import g_itemsCache
from gui.shared.formatters.text_styles import builder
from gui.shared.gui_items.processors.common import FreeXPExchanger
from gui.shared.utils.decorators import process
from helpers import i18n
from gui.Scaleform.locale.MENU import MENU
from gui.shared.formatters import icons

class ExchangeXPWindow(ExchangeXpWindowMeta):

    def _populate(self):
        super(ExchangeXPWindow, self)._populate()
        self.__xpForFree = g_itemsCache.items.shop.freeXPConversionLimit
        self.as_setPrimaryCurrencyS(g_itemsCache.items.stats.actualGold)
        self.__setRates()
        self.as_totalExperienceChangedS(g_itemsCache.items.stats.actualFreeXP)
        self.as_setWalletStatusS(game_control.g_instance.wallet.status)
        self.__prepareAndPassVehiclesData()

    def _subscribe(self):
        g_clientUpdateManager.addCallbacks({'stats.gold': self._setGoldCallBack,
         'shop.freeXPConversion': self.__setXPConversationCallBack,
         'shop.goodies': self.__discountChangedCallback,
         'goodies.4': self.__discountChangedCallback,
         'inventory.1': self.__vehiclesDataChangedCallBack,
         'stats.vehTypeXP': self.__vehiclesDataChangedCallBack,
         'stats.freeXP': self.__setFreeXPCallBack})
        game_control.g_instance.wallet.onWalletStatusChanged += self.__setWalletCallback
        g_itemsCache.onSyncCompleted += self.__setXPConversationCallBack

    def __vehiclesDataChangedCallBack(self, _):
        self.__prepareAndPassVehiclesData()

    def __setFreeXPCallBack(self, value):
        self.as_totalExperienceChangedS(value)

    def __setXPConversationCallBack(self, *args):
        self.__setRates()

    def __setWalletCallback(self, status):
        self.as_setPrimaryCurrencyS(g_itemsCache.items.stats.actualGold)
        self.as_totalExperienceChangedS(g_itemsCache.items.stats.actualFreeXP)
        self.as_setWalletStatusS(status)

    def __prepareAndPassVehiclesData(self):
        values = []
        for vehicleCD in g_itemsCache.items.stats.eliteVehicles:
            try:
                vehicle = g_itemsCache.items.getItemByCD(vehicleCD)
                if not vehicle.xp:
                    continue
                values.append({'id': vehicle.intCD,
                 'vehicleType': getVehicleTypeAssetPath(vehicle.type),
                 'vehicleName': vehicle.shortUserName,
                 'xp': vehicle.xp,
                 'isSelectCandidate': vehicle.isFullyElite,
                 'vehicleIco': vehicle.iconSmall,
                 'nationIco': getNationsAssetPath(vehicle.nationID, namePrefix=NATION_ICON_PREFIX_131x31)})
            except:
                continue

        labelBuilder = builder().addStyledText('middleTitle', i18n.makeString(MENU.EXCHANGE_RATE))
        if self.__xpForFree is not None:
            labelBuilder.addStyledText(self.__getActionStyle(), i18n.makeString(MENU.EXCHANGEXP_AVAILABLE_FORFREE_LABEL))
            labelBuilder.addStyledText('expText', i18n.makeString(MENU.EXCHANGEXP_AVAILABLE_FORFREE_VALUE, icon=icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_ELITEXPICON_2), forFree=BigWorld.wg_getNiceNumberFormat(self.__xpForFree)))
        vehicleData = {'isHaveElite': bool(values),
         'vehicleList': values,
         'tableHeader': self._getTableHeader(),
         'xpForFree': self.__xpForFree,
         'rateLabel': labelBuilder.render(),
         'xpAction': g_itemsCache.items.shop.isXPConversionActionActive}
        self.as_vehiclesDataChangedS(vehicleData)
        return

    def _getTableHeader(self):
        return [self._createTableBtnInfo('isSelectCandidate', 40, 2, DIALOGS.GATHERINGXPFORM_SORTBY_SELECTION, 'ascending', RES_ICONS.MAPS_ICONS_BUTTONS_TAB_SORT_BUTTON_OK), self._createTableBtnInfo('vehicleName', 179, 1, DIALOGS.GATHERINGXPFORM_SORTBY_VEHICLE, 'ascending', RES_ICONS.MAPS_ICONS_BUTTONS_TAB_SORT_BUTTON_TANK, sortType='string'), self._createTableBtnInfo('xp', 103, 0, DIALOGS.GATHERINGXPFORM_SORTBY_XP, 'descending', RES_ICONS.MAPS_ICONS_BUTTONS_TAB_SORT_BUTTON_STAR)]

    def _createTableBtnInfo(self, id, buttonWidth, sortOrder, toolTip, defaultSortDirection, iconSource, sortType = 'numeric'):
        return {'id': id,
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
        eliteVcls = g_itemsCache.items.stats.eliteVehicles
        xps = g_itemsCache.items.stats.vehiclesXPs
        commonXp = 0
        for vehicleCD in vehTypeCompDescrs:
            if vehicleCD in eliteVcls:
                commonXp += xps.get(vehicleCD, 0)

        xpToExchange = min(commonXp, exchangeXP)
        result = yield FreeXPExchanger(xpToExchange, vehTypeCompDescrs, freeConversion=self.__xpForFree).request()
        if len(result.userMsg):
            SystemMessages.g_instance.pushI18nMessage(result.userMsg, type=result.sysMsgType)
        if result.success:
            self.destroy()

    def onWindowClose(self):
        self.destroy()

    def _dispose(self):
        g_itemsCache.onSyncCompleted -= self.__setXPConversationCallBack
        game_control.g_instance.wallet.onWalletStatusChanged -= self.__setWalletCallback
        g_clientUpdateManager.removeObjectCallbacks(self)
        super(ExchangeXPWindow, self)._dispose()

    def __discountChangedCallback(self, _):
        self.__setRates()
        newLimit = g_itemsCache.items.shop.freeXPConversionLimit
        if newLimit != self.__xpForFree:
            self.__xpForFree = newLimit
            self.__prepareAndPassVehiclesData()

    def __setRates(self):
        rate = g_itemsCache.items.shop.freeXPConversionWithDiscount
        defaultRate = g_itemsCache.items.shop.defaults.freeXPConversion
        self.as_exchangeRateS(defaultRate[0], rate[0])

    def __getActionStyle(self):
        rate = g_itemsCache.items.shop.defaults.freeXPConversion
        actionRate = g_itemsCache.items.shop.freeXPConversionWithDiscount
        if rate != actionRate and actionRate > 0:
            return 'statsText'
        return 'alertText'
