# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/wgcg/requests.py
import types
import weakref
from client_request_lib.exceptions import ResponseCodes
from debug_utils import LOG_WARNING, LOG_DEBUG
from gui.clans import formatters as clan_fmts
from gui.clans.settings import DEFAULT_COOLDOWN, REQUEST_TIMEOUT
from gui.shared.rq_cooldown import RequestCooldownManager, REQUEST_SCOPE
from gui.shared.utils.requesters.RequestsController import RequestsController
from gui.shared.utils.requesters.abstract import Response, ClientRequestsByIDProcessor
from gui.wgcg.advent_calendar.handlers import AdventCalendarRequestHandlers
from gui.wgcg.base.handlers import BaseRequestHandlers
from gui.wgcg.clan.handlers import ClanRequestHandlers
from gui.wgcg.elen.handlers import ElenRequestHandlers
from gui.wgcg.agate.handlers import AgateRequestHandlers
from gui.wgcg.utils.handlers import UtilsRequestHandlers
from gui.wgcg.hof.handlers import HofRequestHandlers
from gui.wgcg.mapbox.handlers import MapboxRequestHandlers
from gui.wgcg.promo_screens.handlers import PromoScreensRequestHandlers
from gui.wgcg.rank.handlers import RankRequestHandlers
from gui.wgcg.settings import WebRequestDataType
from gui.wgcg.external_battle_handlers import BaseExternalBattleUnitRequestHandlers
from gui.wgcg.craftmachine.handlers import CraftmachineRequestHandlers
from gui.wgcg.gift_system.handlers import GiftSystemRequestHandlers
from gui.wgcg.friends_service.handlers import FriendServiceRequestHandlers
from gui.wgcg.uilogging.handlers import UILoggingRequestHandlers

class WgcgRequestResponse(Response):

    def isSuccess(self):
        return self.getCode() in (ResponseCodes.NO_ERRORS, ResponseCodes.STRONGHOLD_NOT_FOUND)

    def getCode(self):
        return self.code

    def clone(self, data=None):
        return WgcgRequestResponse(self.code, self.txtStr, data or self.data)


class WgcgRequester(ClientRequestsByIDProcessor):

    def __init__(self, sender):
        super(WgcgRequester, self).__init__(sender, WgcgRequestResponse)

    def doRequestEx(self, ctx, callback, methodName, *args, **kwargs):
        LOG_DEBUG('WgcgRequester, do request:')
        LOG_DEBUG('   ctx        :', ctx)
        LOG_DEBUG('   methodName :', methodName)
        LOG_DEBUG('   Args       :', args)
        LOG_DEBUG('   Kwargs     :', kwargs)
        return super(WgcgRequester, self).doRequestEx(ctx, callback, methodName, *args, **kwargs)

    def _getSenderMethod(self, sender, methodName):
        if isinstance(methodName, types.TupleType):
            storageName, methodName = methodName
            sender = getattr(sender, storageName, None)
        return super(WgcgRequester, self)._getSenderMethod(sender, methodName)

    def _doCall(self, method, *args, **kwargs):
        requestID = self._idsGenerator.next()

        def _callback(data, statusCode, responseCode, headers):
            ctx = self._requests[requestID]
            response = self._makeResponse(responseCode, '', data, ctx, extraCode=statusCode, headers=headers)
            self._onResponseReceived(requestID, response)

        method(_callback, *args, **kwargs)
        return requestID


class WgcgCooldownManager(RequestCooldownManager):

    def __init__(self):
        super(WgcgCooldownManager, self).__init__(REQUEST_SCOPE.WGCG, DEFAULT_COOLDOWN)

    def lookupName(self, rqTypeID):
        if WebRequestDataType.hasValue(rqTypeID):
            requestName = clan_fmts.getRequestUserName(rqTypeID)
        else:
            requestName = str(rqTypeID)
            LOG_WARNING('Request type is not found', rqTypeID)
        return requestName

    def getDefaultCoolDown(self):
        return DEFAULT_COOLDOWN

    def adjust(self, rqTypeID, coolDown=None):
        self.process(rqTypeID, coolDown)


class WgcgRequestsController(RequestsController):

    def __init__(self, webCtrl, requester, cooldown=WgcgCooldownManager()):
        super(WgcgRequestsController, self).__init__(requester, cooldown)
        self.__webCtrl = weakref.proxy(webCtrl)
        self.__handlers = dict()
        self.__handlers.update(AdventCalendarRequestHandlers(requester).get())
        self.__handlers.update(BaseRequestHandlers(requester).get())
        self.__handlers.update(ClanRequestHandlers(requester, self.__webCtrl).get())
        self.__handlers.update(BaseExternalBattleUnitRequestHandlers(requester).get())
        self.__handlers.update(ElenRequestHandlers(requester).get())
        self.__handlers.update(HofRequestHandlers(requester).get())
        self.__handlers.update(RankRequestHandlers(requester).get())
        self.__handlers.update(PromoScreensRequestHandlers(requester).get())
        self.__handlers.update(UtilsRequestHandlers(requester).get())
        self.__handlers.update(CraftmachineRequestHandlers(requester).get())
        self.__handlers.update(MapboxRequestHandlers(requester).get())
        self.__handlers.update(GiftSystemRequestHandlers(requester).get())
        self.__handlers.update(FriendServiceRequestHandlers(requester).get())
        self.__handlers.update(UILoggingRequestHandlers(requester).get())
        self.__handlers.update(AgateRequestHandlers(requester).get())

    def fini(self):
        super(WgcgRequestsController, self).fini()
        self.__handlers = None
        return

    def _getHandlerByRequestType(self, requestTypeID):
        return self.__handlers.get(requestTypeID) if self.__handlers else None

    def _getRequestTimeOut(self):
        return REQUEST_TIMEOUT
