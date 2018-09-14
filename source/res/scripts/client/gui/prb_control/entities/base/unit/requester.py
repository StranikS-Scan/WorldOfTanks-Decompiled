# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/base/unit/requester.py
from UnitBase import UNIT_ERROR
from debug_utils import LOG_ERROR
from gui.prb_control import prb_getters

class UnitRequestProcessor(object):
    """
    Unit requests processor
    """
    __slots__ = ('__requests', '__entity')

    def __init__(self, entity):
        super(UnitRequestProcessor, self).__init__()
        self.__requests = {}
        self.__entity = entity

    def init(self):
        """
        Initializes processor and adds required subscriptions
        """
        unitMgr = prb_getters.getClientUnitMgr()
        if unitMgr:
            unitMgr.onUnitResponseReceived += self.unitMgr_onUnitResponseReceived
            unitMgr.onUnitErrorReceived += self.unitMgr_onUnitErrorReceived
        else:
            LOG_ERROR('Unit manager is not defined')

    def fini(self):
        """
        Finalizes processor and removes required subscriptions
        """
        unitMgr = prb_getters.getClientUnitMgr()
        if unitMgr:
            unitMgr.onUnitResponseReceived -= self.unitMgr_onUnitResponseReceived
            unitMgr.onUnitErrorReceived -= self.unitMgr_onUnitErrorReceived
        self.__requests.clear()
        self.__entity = None
        return

    def doRequest(self, ctx, methodName, *args, **kwargs):
        """
        Sends unit request with context given
        Args:
            ctx: request context
            methodName: method name to call
            *args: method args
            **kwargs: method kwargs
        """
        if self._sendRequest(ctx, methodName, [], *args, **kwargs):
            ctx.startProcessing()

    def doRequestChain(self, ctx, chain):
        """
        Sends unit request with context given and further chain provided
        Args:
            ctx: request context
            chain: further requests chain, as (methodName, args, kwargs) list
        """
        if self._sendNextRequest(ctx, chain):
            ctx.startProcessing()

    def doRawRequest(self, methodName, *args, **kwargs):
        """
        Sends request directly to unit manager
        Args:
            methodName: method name
            *args: call args
            **kwargs: call kwargs
        """
        unitMgr = prb_getters.getClientUnitMgr()
        method = getattr(unitMgr, methodName)
        if callable(method):
            method(*args, **kwargs)
        else:
            LOG_ERROR('Name of method is invalid', methodName)

    def unitMgr_onUnitResponseReceived(self, requestID):
        """
        Listener for event on unit manager's response received
        Args:
            requestID: received request's response ID
        """
        self._onResponseReceived(requestID, True)

    def unitMgr_onUnitErrorReceived(self, requestID, unitMgrID, unitIdx, errorCode, errorStr):
        """
        Listener for event on unit manager's error received
        Args:
            requestID: received request's response ID
            unitMgrID: unit manager ID
            unitIdx: unit index
            errorCode: error's code
            errorStr: error's message
        """
        self._onResponseReceived(requestID, False)
        if errorCode != UNIT_ERROR.OK and self.__entity.getID() == unitMgrID and self.__entity.getUnitIdx() == unitIdx:
            for listener in self.__entity.getListenersIterator():
                listener.onUnitErrorReceived(errorCode)

    def _sendRequest(self, ctx, methodName, chain, *args, **kwargs):
        """
        Sends request to unit manager with given context to proper method
        Args:
            ctx: request contex
            methodName: routine to invoke
            chain: further opertaion's chain
            *args: routine's args
            **kwargs: routine's kwargs
        """
        unitMgr = prb_getters.getClientUnitMgr()
        result = False
        method = getattr(unitMgr, methodName)
        if callable(method):
            requestID = method(*args, **kwargs)
            if requestID > 0:
                self.__requests[requestID] = (ctx, chain)
                result = True
            else:
                LOG_ERROR('Request ID can not be null')
        else:
            LOG_ERROR('Name of method is invalid', methodName)
        return result

    def _sendNextRequest(self, ctx, chain):
        """
        Sends next chained request in chain to unit manager with given context
        Args:
            ctx: request contex
            chain: further opertaion's chain
        """
        methodName, args, kwargs = chain[0]
        return self._sendRequest(ctx, methodName, chain[1:], *args, **kwargs)

    def _onResponseReceived(self, requestID, result):
        """
        Responses processor method
        Args:
            requestID: received request's response ID
            result: opertaion's result
        """
        if requestID > 0:
            ctx, chain = self.__requests.pop(requestID, (None, None))
            if ctx is not None:
                if result and chain:
                    self._sendNextRequest(ctx, chain)
                    return
                ctx.stopProcessing(result)
        else:
            while len(self.__requests):
                _, data = self.__requests.popitem()
                data[0].stopProcessing(False)

        return
