# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web/client_web_api/shop/trade.py
from web.client_web_api.api import C2WHandler, c2w
from gui.Scaleform.framework.entities.EventSystemEntity import EventSystemEntity
from gui.shared import events
from helpers import dependency
from skeletons.gui.game_control import ITradeInController

class TradeEventHandler(C2WHandler, EventSystemEntity):
    __tradeIn = dependency.descriptor(ITradeInController)

    def init(self):
        super(TradeEventHandler, self).init()
        self.addListener(events.VehicleBuyEvent.VEHICLE_SELECTED, self.__onTradeOffSelectedChanged)

    def fini(self):
        self.removeListener(events.VehicleBuyEvent.VEHICLE_SELECTED, self.__onTradeOffSelectedChanged)
        super(TradeEventHandler, self).fini()

    @c2w(name='active_trade_off_update')
    def __onTradeOffSelectedChanged(self, *_):
        return {'id': self.__tradeIn.getActiveTradeOffVehicleCD()}
