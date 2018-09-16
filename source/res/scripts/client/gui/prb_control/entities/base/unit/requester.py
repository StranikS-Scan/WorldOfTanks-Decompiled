# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/base/unit/requester.py
from UnitBase import UNIT_ERROR
from debug_utils import LOG_ERROR
from gui.prb_control import prb_getters
from gui.prb_control.entities.base.requester import IUnitRequestProcessor

class UnitRequestProcessor(IUnitRequestProcessor):
    __slots__ = ('__requests', '__entity')

    def __init__(self, entity):
        super(UnitRequestProcessor, self).__init__()
        self.__requests = {}
        self.__entity = entity

    def init(self):
        unitMgr = prb_getters.getClientUnitMgr()
        if unitMgr:
            unitMgr.onUnitResponseReceived += self.unitMgr_onUnitResponseReceived
            unitMgr.onUnitErrorReceived += self.unitMgr_onUnitErrorReceived
        else:
            LOG_ERROR('Unit manager is not defined')

    def fini(self):
        unitMgr = prb_getters.getClientUnitMgr()
        if unitMgr:
            unitMgr.onUnitResponseReceived -= self.unitMgr_onUnitResponseReceived
            unitMgr.onUnitErrorReceived -= self.unitMgr_onUnitErrorReceived
        self.__requests.clear()
        self.__entity = None
        return

    def doRequest(self, ctx, methodName, *args, **kwargs):
        kwargs.pop('callback', None)
        if self._sendRequest(ctx, methodName, [], *args, **kwargs):
            ctx.startProcessing()
        return

    def doRequestChain(self, ctx, chain):
        if self._sendNextRequest(ctx, chain):
            ctx.startProcessing()

    def doRawRequest(self, methodName, *args, **kwargs):
        unitMgr = prb_getters.getClientUnitMgr()
        method = getattr(unitMgr, methodName)
        if callable(method):
            method(*args, **kwargs)
        else:
            LOG_ERROR('Name of method is invalid', methodName)

    def unitMgr_onUnitResponseReceived(self, requestID):
        self._onResponseReceived(requestID, True)

    def unitMgr_onUnitErrorReceived(self, requestID, unitMgrID, errorCode, errorStr):
        self._onResponseReceived(requestID, False)
        if errorCode != UNIT_ERROR.OK and self.__entity.getID() == unitMgrID:
            for listener in self.__entity.getListenersIterator():
                listener.onUnitErrorReceived(errorCode)

    def _sendRequest(self, ctx, methodName, chain, *args, **kwargs):
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
        methodName, args, kwargs = chain[0]
        return self._sendRequest(ctx, methodName, chain[1:], *args, **kwargs)

    def _onResponseReceived(self, requestID, result):
        if requestID > 0:
            ctx, chain = self.__requests.pop(requestID, (None, None))
            if ctx is not None:
                if result and chain:
                    self._sendNextRequest(ctx, chain)
                    return
                ctx.stopProcessing(result)
        else:
            while self.__requests:
                _, data = self.__requests.popitem()
                data[0].stopProcessing(False)

        return
