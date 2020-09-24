# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/websocket/client.py
import logging
import typing
import BigWorld
import Event
from gui.shared.utils import backoff
from .constants import ConnectionStatus, OpCode
_logger = logging.getLogger(__name__)
try:
    import _websocket
except ImportError:
    _logger.error('CPython implementation of websocket is not found')

    class _websocket(object):

        class PyClient(object):

            def __init__(self, _):
                super(_websocket.PyClient, self).__init__()

            def open(self, _):
                return False

            def close(self):
                pass

            def terminate(self):
                pass

            def send(self, code, message):
                pass


_BACK_OFF_MIN_DELAY = 60
_BACK_OFF_MAX_DELAY = 1200
_BACK_OFF_MODIFIER = 30
_BACK_OFF_EXP_RANDOM_FACTOR = 5

class Listener(object):
    __slots__ = ('__em', 'onOpened', 'onFailed', 'onClosed', 'onMessage')

    def __init__(self):
        super(Listener, self).__init__()
        self.__em = Event.EventManager()
        self.onOpened = Event.Event(self.__em)
        self.onFailed = Event.Event(self.__em)
        self.onClosed = Event.Event(self.__em)
        self.onMessage = Event.Event(self.__em)

    def clear(self):
        self.__em.clear()

    def _cOnOpened(self, server):
        self.onOpened(server)

    def _cOnFailed(self, server, code, reason):
        self.onFailed(server, code, reason)

    def _cOnClosed(self, server, code, reason):
        self.onClosed(server, code, reason)

    def _cOnMessage(self, code, payload):
        self.onMessage(OpCode(code), payload)


class _Reconnection(object):
    __slots__ = ('__client', '__callbackID', '__expBackOff')

    def __init__(self, client):
        super(_Reconnection, self).__init__()
        self.__client = client
        self.__callbackID = None
        self.__expBackOff = backoff.ExpBackoff(_BACK_OFF_MIN_DELAY, _BACK_OFF_MAX_DELAY, _BACK_OFF_MODIFIER, _BACK_OFF_EXP_RANDOM_FACTOR)
        return

    def init(self):
        listener = self.__client.listener
        listener.onOpened += self.__onOpened
        listener.onFailed += self.__onFailed
        listener.onClosed += self.__onClosed

    def clear(self):
        if self.__callbackID is not None:
            _logger.debug('Reconnection. Re-connection to %s is canceled', self.__client.url)
            BigWorld.cancelCallback(self.__callbackID)
            self.__callbackID = None
        self.__expBackOff.reset()
        listener = self.__client.listener
        listener.onOpened -= self.__onOpened
        listener.onFailed -= self.__onFailed
        listener.onClosed -= self.__onClosed
        return

    def __doNextOpen(self):
        self.__callbackID = None
        self.__client.open(self.__client.url)
        return

    def __onOpened(self, server):
        _logger.debug('Reconnection. Server connection is opened: server = %s', server)
        self.__expBackOff.reset()

    def __onFailed(self, server, code, reason):
        _logger.debug('Reconnection. Server connection to %s is failed: server = %s, code = %d, reason = %s', self.__client.url, server, code, reason)
        delay = self.__expBackOff.next()
        _logger.debug('Reconnection. Re-connection to %s will be invoked after %d seconds', self.__client.url, delay)
        self.__callbackID = BigWorld.callback(delay, self.__doNextOpen)

    def __onClosed(self, server, code, reason):
        _logger.debug('Reconnection. Server connection with %s is closed: server = %s, code = %d, reason = %s', self.__client.url, server, code, reason)
        delay = self.__expBackOff.next()
        _logger.debug('Reconnection. Re-connection to %s will be invoked after %d seconds', self.__client.url, delay)
        self.__callbackID = BigWorld.callback(delay, self.__doNextOpen)


class Client(object):
    __slots__ = ('__weakref__', '__impl', '__reconnection', '__isReadyToDestroy')

    def __init__(self):
        super(Client, self).__init__()
        self.__impl = _websocket.PyClient(Listener())
        self.__reconnection = None
        self.__isReadyToDestroy = False
        return

    @property
    def status(self):
        return ConnectionStatus(self.__impl.status)

    @property
    def url(self):
        return self.__impl.url

    @property
    def listener(self):
        return self.__impl.listener

    @property
    def isReadyToDestroy(self):
        return self.__isReadyToDestroy

    @property
    def raw(self):
        return self.__impl

    def open(self, url, reconnect=False):
        self.__clearReconnection()
        if reconnect:
            self.__reconnection = _Reconnection(self.__impl)
            self.__reconnection.init()
        return self.__impl.open(url)

    def close(self):
        self.__clearReconnection()
        self.__impl.close()

    def sendText(self, message):
        self.__impl.send(OpCode.Text.value, message)

    def sendBinary(self, message):
        self.__impl.send(OpCode.Binary.value, message)

    def terminate(self):
        self.__clearReconnection()
        self.__impl.listener.clear()
        self.__impl.terminate()
        self.__isReadyToDestroy = True

    def __clearReconnection(self):
        if self.__reconnection is not None:
            self.__reconnection.clear()
            self.__reconnection = None
        return
