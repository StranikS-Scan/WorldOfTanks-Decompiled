# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/common/xmpp/Connection.py
# Compiled at: 2011-06-29 16:12:36
import socket
import asyncore
import Event
from debug_utils import *
import Parser as XMPPParser

class SocketAdapter:

    def __init__(self):
        self.eventRead = Event.Event()
        self.eventWrite = Event.Event()
        self.eventConnected = Event.Event()
        self.eventDisconnected = Event.Event()


class AsyncoreSocketAdapter(SocketAdapter, asyncore.dispatcher):

    def __init__(self):
        SocketAdapter.__init__(self)
        asyncore.dispatcher.__init__(self)
        self.__buffer = ''

    def connect(self, host, port):
        try:
            self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
            asyncore.dispatcher.connect(self, (host, port))
        except:
            LOG_CURRENT_EXCEPTION()
            return False

        return True

    def close(self):
        asyncore.dispatcher.close(self)

    def send(self, stanza):
        self.__buffer += stanza.encode('utf-8')

    def recv(self, size):
        return asyncore.dispatcher.recv(self, size)

    def handle_close(self):
        self.eventDisconnected()

    def handle_connect(self):
        self.eventConnected()

    def handle_read(self):
        self.eventRead()

    def handle_write(self):
        if self.__buffer:
            sent = asyncore.dispatcher.send(self, self.__buffer)
            self.__buffer = self.__buffer[sent:]


RECV_BUFFER_SIZE = 2048

class Connection(object):
    RESOURCE = u'WOT'
    STANZA_ID_TEMPLATE = u'^%s_([0-9]+)_([0-9]+)$' % RESOURCE

    def __init__(self):
        self.host = (None, None)
        self.credentials = (None, None)
        self.jid = None
        self.socket = None
        self.parser = None
        self.eventConnected = Event.Event()
        self.eventStanza = Event.Event()
        self.eventServerDisconnected = Event.Event()
        return

    def connect(self, host, credentials):
        if self.socket:
            LOG_ERROR('XMPP: Connection: Unable to connect, an existing connection exists.')
            return False
        self.host = host
        self.credentials = credentials
        self.jid = (self.credentials[0] + u'@' + self.host[0]).lower() + u'/' + Connection.RESOURCE
        self.parser = XMPPParser.XMPPParser()
        self.socket = self.createSocketAdapter()
        self.socket.eventRead += self.__onSocketRead
        self.socket.eventConnected += self.__onSocketConnected
        self.socket.eventDisconnected += self.__onSocketDisconnected
        if not self.socket.connect(self.host[0], int(self.host[1])):
            LOG_ERROR("XMPP: Connection: Can't connect to xmpp server.")
            self.eventServerDisconnected()
            return False
        return True

    def disconnect(self):
        if not self.socket:
            LOG_ERROR('XMPP: Connection:disconnect: Unable to disconnect, not currently connected.')
            return False
        else:
            self.socket.eventRead -= self.__onSocketRead
            self.socket.eventConnected -= self.__onSocketConnected
            self.socket.eventDisconnected -= self.__onSocketDisconnected
            self.socket.close()
            self.socket = None
            self.host = (None, None)
            self.credentials = (None, None)
            self.jid = None
            self.socket = None
            self.parser = None
            if self.parser:
                self.parser.fini()
            self.parser = None
            return True

    def sendStanza(self, stanza):
        self.socket.send(stanza)

    def __onSocketConnected(self):
        self.eventConnected()

    def __onSocketDisconnected(self):
        self.eventServerDisconnected()

    def __onSocketRead(self):
        if not self.parser:
            LOG_ERROR('XMPP: Connection::onSocketRead: No parser available.')
            return
        else:
            data = self.socket.recv(RECV_BUFFER_SIZE)
            if not data:
                self.eventServerDisconnected()
                return
            self.parser.feedData(data)
            stanza = self.parser.pop()
            while 1:
                stanza and self.eventStanza(stanza)
                try:
                    stanza = self.parser.pop()
                except:
                    stanza = None

            return

    def createSocketAdapter(self):
        return AsyncoreSocketAdapter()
