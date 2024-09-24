# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: tech_tree_trade_in/scripts/client/tech_tree_trade_in/gui/impl/lobby/meta_view/subviews/view_helpers.py
from enum import Enum
import typing
import BigWorld
from AccountCommands import isCodeValid
from debug_utils import LOG_DEBUG_DEV
from functools import partial
from helpers import dependency
from helpers.CallbackDelayer import CallbackDelayer
from constants import REQUEST_COOLDOWN
from tech_tree_trade_in.skeletons.gui.game_control import ITechTreeTradeInController, BranchType
from tech_tree_trade_in.helpers.server_operations import processOperationsLog
if typing.TYPE_CHECKING:
    from typing import Callable, Hashable, Optional

class ResponseType(Enum):
    CACHED = 0
    SERVER = 1


class RequestDataCache(CallbackDelayer):
    _COOLDOWN = 0

    def __init__(self):
        super(RequestDataCache, self).__init__()
        self.__cache = {}
        self.__previousRequestTime = 0
        self.__lastRequestedKey = None
        return

    def request(self, key, callback, onErrorCallback=None):
        self.__lastRequestedKey = key
        self.clearCallbacks()
        if key in self.__cache:
            LOG_DEBUG_DEV('%s: returning cached data for key %s' % (self.__class__.__name__, key))
            BigWorld.callback(0, partial(callback, key, self.__cache[key]))
            return ResponseType.CACHED
        delay = self.__getRequestDelay()
        LOG_DEBUG_DEV('%s: delaying server request for key %s for %s' % (self.__class__.__name__, key, delay))
        self.delayCallback(delay, partial(self.__performServerRequest, key, callback, onErrorCallback))
        return ResponseType.SERVER

    def _response(self, key, callback, onErrorCallback, response):
        LOG_DEBUG_DEV('%s: received data from server for key %s: %r' % (self.__class__.__name__, key, response))
        payload = None
        if len(response) == 4:
            _, resultId, errorCode, payload = response
        else:
            _, resultId, errorCode = response
        if not isCodeValid(resultId):
            LOG_DEBUG_DEV('TechTreeTradeIn: %s: error response from server for key %r: %r' % (self.__class__.__name__, key, errorCode))
            if onErrorCallback:
                onErrorCallback(key, errorCode)
            return
        else:
            data = self._preProcessResponse(key, payload)
            self.__cache[key] = data
            if self.__lastRequestedKey == key:
                callback(key, data)
            return

    def _request(self, key, callback, onErrorCallback):
        raise NotImplementedError

    def _preProcessResponse(self, key, response):
        return response

    def __getRequestDelay(self):
        return 0 if not self.__previousRequestTime else max(self._COOLDOWN - (BigWorld.time() - self.__previousRequestTime), 0)

    def __performServerRequest(self, key, callback, onErrorCallback):
        self.__previousRequestTime = BigWorld.time()
        LOG_DEBUG_DEV('%s: performing server request for key %s' % (self.__class__.__name__, key))
        self._request(key, callback, onErrorCallback)


class PriceRequestDataCache(RequestDataCache):
    __techTreeTradeInController = dependency.descriptor(ITechTreeTradeInController)
    _COOLDOWN = REQUEST_COOLDOWN.CMD_TRADE_IN_TREES_PRICE + 0.5

    def _request(self, key, callback, onErrorCallback):
        branchToTradeId, branchToReceiveId = key
        branchToTrade = self.__techTreeTradeInController.getBranchById(branchToTradeId, BranchType.BRANCHES_TO_TRADE)
        branchToReceive = self.__techTreeTradeInController.getBranchById(branchToReceiveId, BranchType.BRANCHES_TO_RECEIVE)
        BigWorld.player().TechTreeTradeInAccountComponent.requestTradeInPrice(branchToTrade.vehCDs, branchToReceive.vehCDs, partial(self._response, key, callback, onErrorCallback))


class SummaryRequestDataCache(RequestDataCache):
    __techTreeTradeInController = dependency.descriptor(ITechTreeTradeInController)
    _COOLDOWN = REQUEST_COOLDOWN.CMD_TRADE_IN_TREES_DRY_RUN + 0.5

    def _request(self, key, callback, onErrorCallback):
        branchToTradeId, branchToReceiveId = key
        branchToTrade, branchToReceive = self.__getBranchConfigs(branchToTradeId, branchToReceiveId)
        self.__techTreeTradeInController.requestTradeInDryRun(branchToTrade.branchId, branchToReceive.branchId, partial(self._response, key, callback, onErrorCallback))

    def _preProcessResponse(self, key, response):
        branchToTradeId, branchToReceiveId = key
        branchToTrade, branchToReceive = self.__getBranchConfigs(branchToTradeId, branchToReceiveId)
        return {'branchToTradeId': branchToTrade.branchId,
         'branchToReceiveId': branchToReceive.branchId,
         BranchType.BRANCHES_TO_TRADE: branchToTrade.vehCDs,
         BranchType.BRANCHES_TO_RECEIVE: branchToReceive.vehCDs,
         'operations': processOperationsLog(response)}

    def __getBranchConfigs(self, branchToTradeId, branchToReceiveId):
        branchToTrade = self.__techTreeTradeInController.getBranchById(branchToTradeId, BranchType.BRANCHES_TO_TRADE)
        branchToReceive = self.__techTreeTradeInController.getBranchById(branchToReceiveId, BranchType.BRANCHES_TO_RECEIVE)
        return (branchToTrade, branchToReceive)
