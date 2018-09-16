# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/proto/search_processor.py
import weakref
import BigWorld
from interfaces import ISearchHandler, ISearchProcessor
from debug_utils import LOG_DEBUG, LOG_ERROR
from soft_exception import SoftException

class SearchProcessor(ISearchProcessor):

    def __init__(self):
        super(SearchProcessor, self).__init__()
        self._handlers = set()
        self._lastRequestID = None
        return

    def __del__(self):
        LOG_DEBUG('SearchProcessor deleted:', self)

    def init(self):
        pass

    def fini(self):
        self._lastRequestID = None
        self._handlers.clear()
        return

    def addHandler(self, handler):
        if isinstance(handler, ISearchHandler):
            self._handlers.add(weakref.ref(handler))
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

    def _invokeHandlerMethod--- This code section failed: ---

  86       0	SETUP_LOOP        '109'
           3	LOAD_FAST         'self'
           6	LOAD_ATTR         '_handlers'
           9	LOAD_ATTR         'copy'
          12	CALL_FUNCTION_0   ''
          15	GET_ITER          ''
          16	FOR_ITER          '108'
          19	STORE_FAST        'handlerRef'

  87      22	LOAD_FAST         'handlerRef'
          25	CALL_FUNCTION_0   ''
          28	STORE_FAST        'handler'

  89      31	LOAD_FAST         'handler'
          34	POP_JUMP_IF_FALSE '16'

  90      37	LOAD_GLOBAL       'getattr'
          40	LOAD_FAST         'handler'
          43	LOAD_FAST         'methodName'
          46	LOAD_CONST        ''
          49	CALL_FUNCTION_3   ''
          52	STORE_FAST        'method'

  92      55	LOAD_FAST         'method'
          58	POP_JUMP_IF_FALSE '86'
          61	LOAD_GLOBAL       'callable'
          64	LOAD_FAST         'method'
          67	CALL_FUNCTION_1   ''
        70_0	COME_FROM         '58'
          70	POP_JUMP_IF_FALSE '86'

  93      73	LOAD_FAST         'method'
          76	LOAD_FAST         'args'
          79	CALL_FUNCTION_VAR_0 ''
          82	POP_TOP           ''
          83	JUMP_ABSOLUTE     '105'

  95      86	LOAD_GLOBAL       'LOG_ERROR'
          89	LOAD_CONST        'Method is not found'
          92	LOAD_FAST         'handler'
          95	LOAD_FAST         'methodName'
          98	CALL_FUNCTION_3   ''
         101	POP_TOP           ''
         102	CONTINUE          '16'
         105	JUMP_BACK         '16'
         108	POP_BLOCK         ''
       109_0	COME_FROM         '0'
         109	LOAD_CONST        ''
         112	RETURN_VALUE      ''

Syntax error at or near 'POP_BLOCK' token at offset 108

    def _onSearchTokenComplete(self, requestID, result):
        if self._lastRequestID != requestID:
            return
        self._invokeHandlerMethod('onSearchComplete', result)

    def _onSearchFailed(self, reason):
        self._invokeHandlerMethod('onSearchFailed', reason)

    def _onExcludeFromSearch(self, entity):
        self._invokeHandlerMethod('onExcludeFromSearch', entity)