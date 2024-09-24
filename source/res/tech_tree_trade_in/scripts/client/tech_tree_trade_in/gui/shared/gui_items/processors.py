# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: tech_tree_trade_in/scripts/client/tech_tree_trade_in/gui/shared/gui_items/processors.py
import typing
import BigWorld
from gui.Scaleform.Waiting import Waiting
from gui.shared.gui_items.processors import Processor, makeSuccess, makeError
from debug_utils import LOG_DEBUG
from tech_tree_trade_in.gui.shared.event_dispatcher import pushTechTreeTradeInUnavailableNotification, pushTechTreeTradeInErrorNotification, pushTradeInCompleteNotification, pushTradeInDetailsNotification
from tech_tree_trade_in.helpers.server_operations import processOperationsLog
if typing.TYPE_CHECKING:
    from typing import Callable, Optional, Dict
    from gui.SystemMessages import ResultMsg

class TechTreeTradeInProcessor(Processor):

    def __init__(self, branchToTrade, branchToReceive, price):
        super(TechTreeTradeInProcessor, self).__init__(plugins=[])
        self.__branchToTrade = branchToTrade
        self.__branchToReceive = branchToReceive
        self.__price = price

    def _request(self, callback):
        Waiting.show('loading')
        BigWorld.player().TechTreeTradeInAccountComponent.requestTradeIn(self.__branchToTrade, self.__branchToReceive, self.__price, lambda code, errorStr='', ctx=None: self._response(code, callback, errorStr, ctx))
        return

    def _response(self, code, callback, errStr='', ctx=None):
        if code >= 0:
            LOG_DEBUG('TechTreeTradeIn: Server success response: code=%r, error=%r, ctx=%r' % (code, errStr, ctx))
            return callback(self._successHandler(code, ctx=ctx))
        LOG_DEBUG('TechTreeTradeIn: Server fail response: code=%r, error=%r, ctx=%r' % (code, errStr, ctx))
        return callback(self._errorHandler(code, errStr=errStr, ctx=ctx))

    def _successHandler(self, code, ctx=None):
        Waiting.hide('loading')
        data = processOperationsLog(ctx)
        pushTradeInCompleteNotification(self.__branchToTrade, self.__branchToReceive, data)
        pushTradeInDetailsNotification(data)
        return makeSuccess()

    def _errorHandler(self, code, errStr='', ctx=None):
        Waiting.hide('loading')
        if errStr == 'UNAVAILABLE':
            pushTechTreeTradeInUnavailableNotification()
        else:
            pushTechTreeTradeInErrorNotification()
        return makeError(msgData={'errStr': errStr})
