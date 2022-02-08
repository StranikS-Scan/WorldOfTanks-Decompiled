# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web/client_web_api/common.py
import logging
from Event import Event
from web.client_web_api.battle_pass import BattlePassEventHandler
from web.client_web_api.platform import PlatformEventHandler
from web.client_web_api.ranked import BrowsersBridgeC2W, RankedEventHandler
from web.client_web_api.reactive_comm import ReactiveCommunicationEventHandler
from web.client_web_api.shop.stats import BalanceEventHandler
from web.client_web_api.shop.telecom_rentals import TelecomTokenEventHandler
from web.client_web_api.shop.trade import TradeEventHandler
from web.client_web_api.util.vehicle import VehicleCompareEventHandler, VehicleStateEventHandler
_logger = logging.getLogger(__name__)

class WebEventSender(object):

    def __init__(self):
        self.onCallback = Event()
        self._handlers = self._createHandlers()

    def init(self):
        for handler in self._handlers:
            handler.init()

    def fini(self):
        for handler in self._handlers:
            handler.fini()

        self._handlers = None
        return

    def sendEvent(self, webEvent):
        self.onCallback(webEvent)
        _logger.debug('Client2Web event sent: %s', webEvent)

    def _createHandlers(self):
        return (BalanceEventHandler(self),
         TradeEventHandler(self),
         VehicleCompareEventHandler(self),
         VehicleStateEventHandler(self),
         ReactiveCommunicationEventHandler(self),
         PlatformEventHandler(self),
         RankedEventHandler(self),
         BrowsersBridgeC2W(self),
         TelecomTokenEventHandler(self),
         BattlePassEventHandler(self))
