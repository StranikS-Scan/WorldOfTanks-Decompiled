# Embedded file name: scripts/client/gui/shared/utils/requesters/abstract.py
from adisp import async, process
from helpers import isPlayerAccount
from debug_utils import LOG_ERROR
from gui.shared.utils import code2str

class RequesterAbstract(object):
    """
    Abstract requester for server data caches. Contains cache
    member dict, common request and response methods.
    """

    def __init__(self):
        self.__synced = False
        self.__cache = dict()

    def _response(self, resID, value, callback):
        """
        Common server response method. Must be called ANYWAY after
        server operation will complete.
        
        @param resID: request result id
        @param value: requested value
        @param callback: function to be called after operation will complete
        """
        self.__synced = resID >= 0
        if resID < 0:
            LOG_ERROR('[class %s] There is error while getting data from cache: %s[%d]' % (self.__class__.__name__, code2str(resID), resID))
            return callback(dict())
        callback(dict(value))

    @async
    def _requestCache(self, callback = None):
        """
        Empty request method. Just call response without
        any data requesting.
        """
        self._response(0, {}, callback)

    @async
    @process
    def request(self, callback = None):
        """
        Public request method. Validate player entity to request
        possibility and itself as single callback argument.
        """
        self.__synced = False
        if not isPlayerAccount():
            yield lambda callback: callback(None)
            LOG_ERROR('[class %s] Player is not account.' % self.__class__.__name__)
        else:
            self.__cache = yield self._requestCache()
        callback(self)

    def isSynced(self):
        return self.__synced

    def clear(self):
        self.__cache.clear()

    def getCacheValue(self, key, defaultValue = None):
        """
        Public interface method to get value from cache.
        
        @param key: value's key in cache
        @param defaultValue: default value if key does not exist
        @return: value
        """
        return self.__cache.get(key, defaultValue)
