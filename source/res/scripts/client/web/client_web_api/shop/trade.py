# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web/client_web_api/shop/trade.py
from web.client_web_api.api import C2WHandler, c2w
from gui.Scaleform.framework.entities.EventSystemEntity import EventSystemEntity
from gui.shared import events
from helpers import dependency
from skeletons.gui.game_control import ITradeInController, IPersonalTradeInController

class TradeEventHandler(C2WHandler, EventSystemEntity):
    __tradeIn = dependency.descriptor(ITradeInController)
    __personalTradeIn = dependency.descriptor(IPersonalTradeInController)

    def init(self):
        super(TradeEventHandler, self).init()
        self.addListener(events.VehicleBuyEvent.VEHICLE_SELECTED, self.__onTradeOffSelectedChanged)
        self.__personalTradeIn.onActiveSaleVehicleChanged += self.__onPersonalTradeOffSelectedChanged
        self.__personalTradeIn.onActiveBuyVehicleChanged += self.__onPersonalTradeOffSelectedChanged

    def fini(self):
        self.removeListener(events.VehicleBuyEvent.VEHICLE_SELECTED, self.__onTradeOffSelectedChanged)
        self.__personalTradeIn.onActiveSaleVehicleChanged -= self.__onPersonalTradeOffSelectedChanged
        self.__personalTradeIn.onActiveBuyVehicleChanged -= self.__onPersonalTradeOffSelectedChanged
        super(TradeEventHandler, self).fini()

    @c2w(name='active_trade_off_update')
    def __onTradeOffSelectedChanged(self, *_):
        return {'id': self.__tradeIn.getActiveTradeOffVehicleCD()}

    @c2w(name='active_personal_trade_off_update')
    def __onPersonalTradeOffSelectedChanged(self, *_):
        return {'id_sale': self.__personalTradeIn.getActiveTradeInSaleVehicleCD(),
         'id_buy': self.__personalTradeIn.getActiveTradeInBuyVehicleCD()}
