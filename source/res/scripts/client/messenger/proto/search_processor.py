import weakref
import BigWorld
from interfaces import ISearchHandler
from interfaces import ISearchProcessor
from debug_utils import LOG_DEBUG
from debug_utils import LOG_ERROR
from soft_exception import SoftException
class SearchProcessor(ISearchProcessor):
    def __init__(self):
        super(SearchProcessor, self).__init__()
        self._handlers = set()
        self._lastRequestID = None

    def __del__(self):
        LOG_DEBUG('SearchProcessor deleted:', self)

    def init(self):
        pass

    def fini(self):
        self._lastRequestID = None
        self._handlers.clear()

    def addHandler(self, handler):
        if isinstance(handler, ISearchHandler):
            self._handlers.add(weakref.ref(handler))
            return
        else:
            raise SoftException('Handler must implement ISearchHandler')

    def removeHandler(self, handler):
        handlerRef = weakref.ref(handler)
        if handlerRef in self._handlers:
            self._handlers.remove(handlerRef)

    def find(self, token, **kwargs):
        raise NotImplementedError('Routine SearchProcessor.find must be implemented')

    def getSearchResultLimit(self):
        raise NotImplementedError('Routine SearchProcessor.getSearchResultLimit must be implemented')

    def getSearchCoolDown(self):
        raise NotImplementedError('Routine SearchProcessor.getSearchCoolDown must be implemented')

    def _makeRequestID(self):
        return BigWorld.player().acquireRequestID()

    def _invokeHandlerMethod(self, methodName, *args):
        for handlerRef in self._handlers.copy():
            handler = handlerRef()
            if handler:
                method = getattr(handler, methodName, None)
                if method and callable(method):
                    method(*args)
                    continue
                else:
                    LOG_ERROR('Method is not found', handler, methodName)
                    continue

    def _onSearchTokenComplete(self, requestID, result):
        if self._lastRequestID != requestID:
            return
        else:
            self._invokeHandlerMethod('onSearchComplete', result)
            return

    def _onSearchFailed(self, reason):
        self._invokeHandlerMethod('onSearchFailed', reason)

    def _onExcludeFromSearch(self, entity):
        self._invokeHandlerMethod('onExcludeFromSearch', entity)


