# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/exchange/ExchangeXPWindow.py
import BigWorld
from PlayerEvents import g_playerEvents
from debug_utils import LOG_CURRENT_EXCEPTION, LOG_ERROR
from gui import SystemMessages, game_control
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform import getVehicleTypeAssetPath, getNationsAssetPath, NATION_ICON_PREFIX_131x31
from gui.Scaleform.daapi.view.lobby.exchange.BaseExchangeWindow import BaseExchangeWindow
from gui.Scaleform.daapi.view.meta.ExchangeXpWindowMeta import ExchangeXpWindowMeta
from gui.shared import g_itemsCache
from gui.shared.gui_items.processors.common import FreeXPExchanger
from gui.shared.utils.decorators import process
from gui.shared.utils.gui_items import VEHICLE_ELITE_STATE, getVehicleEliteState

class ExchangeXPWindow(BaseExchangeWindow, ExchangeXpWindowMeta):

    def _populate(self):
        super(ExchangeXPWindow, self)._populate()
        self.as_setPrimaryCurrencyS(g_itemsCache.items.stats.actualGold)
        rate = g_itemsCache.items.shop.freeXPConversion
        defaultRate = g_itemsCache.items.shop.defaults.freeXPConversion
        self.as_exchangeRateS(defaultRate[0], rate[0])
        self.as_totalExperienceChangedS(g_itemsCache.items.stats.actualFreeXP)
        self.as_setWalletStatusS(game_control.g_instance.wallet.status)
        self.__prepareAndPassVehiclesData()

    def _subscribe(self):
        g_clientUpdateManager.addCallbacks({'stats.gold': self._setGoldCallBack,
         'shop.freeXPConversion': self.__setXPConversationCallBack,
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
        rate = g_itemsCache.items.shop.freeXPConversion
        defaultRate = g_itemsCache.items.shop.defaults.freeXPConversion
        self.as_exchangeRateS(defaultRate[0], rate[0])

    def __setWalletCallback(self, status):
        self.as_setPrimaryCurrencyS(g_itemsCache.items.stats.actualGold)
        self.as_totalExperienceChangedS(g_itemsCache.items.stats.actualFreeXP)
        self.as_setWalletStatusS(status)

    def __prepareAndPassVehiclesData(self):
        values = []
        for vehicleCD in g_itemsCache.items.stats.eliteVehicles:
            try:
                vehicle = g_itemsCache.items.getItemByCD(vehicleCD)
            except:
                LOG_ERROR('Cannot get vehicle by intCD', vehicleCD)
                LOG_CURRENT_EXCEPTION()
                continue

            if not vehicle.xp:
                continue
            vehicleInfo = dict(id=vehicle.intCD, vehicleType=getVehicleTypeAssetPath(vehicle.type), vehicleName=vehicle.shortUserName, xp=vehicle.xp, isSelectCandidate=vehicle.isFullyElite, vehicleIco=vehicle.iconSmall, nationIco=getNationsAssetPath(vehicle.nationID, namePrefix=NATION_ICON_PREFIX_131x31))
            values.append(vehicleInfo)

        self.as_vehiclesDataChangedS(bool(values), values)

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
        result = yield FreeXPExchanger(xpToExchange, vehTypeCompDescrs).request()
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
