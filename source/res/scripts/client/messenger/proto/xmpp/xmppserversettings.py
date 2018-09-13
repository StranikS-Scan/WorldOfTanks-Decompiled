# Embedded file name: scripts/client/messenger/proto/xmpp/XmppServerSettings.py
from messenger.proto.interfaces import IProtoSettings
from messenger.proto.xmpp.jid import JID
import random
_NUMBER_OF_ITEMS_IN_SAMPLE = 2

def _makeSample(*args):
    queue = []
    for seq in args:
        count = min(len(seq), _NUMBER_OF_ITEMS_IN_SAMPLE)
        queue.extend(random.sample(seq, count))

    return queue


class XmppServerSettings(IProtoSettings):
    __slots__ = ('enabled', 'connections', 'domain', 'port', 'resource')

    def __init__(self):
        super(XmppServerSettings, self).__init__()
        self.clear()

    def __repr__(self):
        return 'XmppServerSettings(enabled = {0!r:s}, connections = {1!r:s}, domain = {2:>s}, port = {3:n}, resource = {4:>s})'.format(self.enabled, self.connections, self.domain, self.port, self.resource)

    def update(self, data):
        if 'xmpp_enabled' in data:
            self.enabled = data['xmpp_enabled']
        else:
            self.enabled = False
        if 'xmpp_connections' in data:
            self.connections = data['xmpp_connections']
        else:
            self.connections = []
        if 'xmpp_alt_connections' in data:
            self.altConnections = data['xmpp_alt_connections']
        else:
            self.altConnections = []
        if 'xmpp_host' in data:
            self.domain = data['xmpp_host']
        else:
            self.domain = ''
        if 'xmpp_port' in data:
            self.port = data['xmpp_port']
        else:
            self.port = -1
        if 'xmpp_resource' in data:
            self.resource = data['xmpp_resource']
        else:
            self.resource = -1

    def clear(self):
        self.enabled = False
        self.connections = []
        self.altConnections = []
        self.domain = None
        self.port = -1
        self.resource = ''
        self.__cQueue = []
        return

    def isEnabled(self):
        return self.enabled

    def getConnection(self, databaseID):
        if not databaseID:
            raise AssertionError("Player's databaseID can not be empty")
            host, port = (self.connections or self.altConnections) and self.__getNextConnection()
        else:
            host, port = self.domain, self.port
        jid = JID()
        jid.setNode(databaseID)
        jid.setDomain(self.domain)
        jid.setResource(self.resource)
        return (jid, host, port)

    def clearConnections(self):
        self.__cQueue = []

    def __getNextConnection(self):
        if not self.__cQueue:
            self.__cQueue = _makeSample(self.connections, self.altConnections)
        return self.__cQueue.pop(0)
