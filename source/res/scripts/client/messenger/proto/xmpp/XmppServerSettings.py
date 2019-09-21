# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/proto/xmpp/XmppServerSettings.py
import random
import types
from debug_utils import LOG_ERROR
from gui.shared.utils import getPlayerDatabaseID
from messenger.proto.interfaces import IProtoSettings
from messenger.proto.xmpp.gloox_constants import CONNECTION_IMPL_TYPE
from messenger.proto.xmpp.jid import ContactJID
from soft_exception import SoftException
_NUMBER_OF_ITEMS_IN_SAMPLE = 2

def _makeSample(*args):
    queue = []
    for seq in args:
        count = min(len(seq), _NUMBER_OF_ITEMS_IN_SAMPLE)
        queue.extend(random.sample(seq, count))

    return queue


def _validateConnection(record):
    result = True
    if len(record) == 2:
        host, port = record
        if not host:
            result = False
        if not isinstance(port, types.IntType):
            result = False
    else:
        result = False
    return result


class ConnectionsIterator(object):

    def __init__(self, base=None, alt=None, bosh=None):
        super(ConnectionsIterator, self).__init__()
        self.__tcp = _makeSample(base or [], alt or [])
        self.__bosh = _makeSample(bosh or [])

    def __iter__(self):
        return self

    def __len__(self):
        return len(self.__tcp) + len(self.__bosh)

    def clear(self):
        self.__tcp = []
        self.__bosh = []

    def hasNext(self):
        return len(self.__tcp) > 0 or len(self.__bosh) > 0

    def next(self):
        if self.__tcp:
            cType = CONNECTION_IMPL_TYPE.TCP
            host, port = self.__tcp.pop(0)
        elif self.__bosh:
            cType = CONNECTION_IMPL_TYPE.BOSH
            host, port = self.__bosh.pop(0)
        else:
            raise StopIteration
        return (cType, host, port)


class XmppServerSettings(IProtoSettings):
    __slots__ = ('enabled', 'connections', 'domain', 'port', 'resource', 'altConnections', 'boshConnections', 'mucServices')

    def __init__(self):
        super(XmppServerSettings, self).__init__()
        self.clear()

    def __repr__(self):
        return 'XmppServerSettings(enabled = {0!r:s}, connections = {1!r:s}, altConnections = {2!r:s}, boshConnections = {3!r:s}, domain = {4:>s}, port = {5:n}, resource = {6:>s}, mucServices = {7:>s})'.format(self.enabled, self.connections, self.altConnections, self.boshConnections, self.domain, self.port, self.resource, self.mucServices)

    @property
    def userRoomsService(self):
        from messenger.proto import XMPP_MUC_CHANNEL_TYPE
        usersService = self.getChannelByType(XMPP_MUC_CHANNEL_TYPE.USERS)
        if usersService:
            return usersService['hostname']
        raise SoftException('users room service is not set')

    def update(self, data):
        if 'xmpp_connections' in data:
            self.connections = filter(_validateConnection, data['xmpp_connections'])
        else:
            self.connections = []
        if 'xmpp_alt_connections' in data:
            self.altConnections = filter(_validateConnection, data['xmpp_alt_connections'])
        else:
            self.altConnections = []
        if 'xmpp_bosh_connections' in data:
            self.boshConnections = filter(_validateConnection, data['xmpp_bosh_connections'])
        else:
            self.boshConnections = []
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
            self.resource = ''
        if 'xmpp_enabled' in data:
            self.enabled = data['xmpp_enabled']
            if self.enabled and not self.connections and not self.altConnections and not self.boshConnections and not self.domain:
                LOG_ERROR('Can not find host to connection. XMPP is disabled', self.connections, self.altConnections, self.domain)
                self.enabled = False
        else:
            self.enabled = False
        if 'xmpp_muc_services' in data:
            for service in data['xmpp_muc_services']:
                self.mucServices[service['type']] = service

        self.mucServices = self.mucServices or {}

    def clear(self):
        self.enabled = False
        self.connections = []
        self.altConnections = []
        self.boshConnections = []
        self.domain = None
        self.port = -1
        self.resource = ''
        self.mucServices = {}
        return

    def isEnabled(self):
        return self.enabled

    def getFullJID(self, databaseID=None):
        if databaseID is None:
            databaseID = getPlayerDatabaseID()
        if not databaseID:
            raise SoftException("Player's databaseID can not be empty")
        jid = ContactJID()
        jid.setNode(databaseID)
        jid.setDomain(self.domain)
        jid.setResource(self.resource)
        return jid

    def getConnectionsIterator(self):
        iterator = ConnectionsIterator(self.connections, self.altConnections, self.boshConnections)
        if not iterator.hasNext():
            iterator = ConnectionsIterator([(self.domain, self.port)])
        return iterator

    def isMucServiceAllowed(self, service='', hostname=''):
        if not self.enabled:
            return False
        for serviceType, serviceData in self.mucServices.iteritems():
            if serviceType == service or hostname and hostname in serviceData['hostname']:
                return serviceData['enabled']

        return False

    def getChannelByType(self, channelType):
        return self.mucServices[channelType] if channelType in self.mucServices else None
