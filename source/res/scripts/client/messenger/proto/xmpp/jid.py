# Embedded file name: scripts/client/messenger/proto/xmpp/jid.py
import types
from messenger import g_settings

class BareJID(object):
    __slots__ = ('_node', '_domain')

    def __init__(self, jid = None):
        super(BareJID, self).__init__()
        self.setJID(jid)

    def setJID(self, jid):
        tail = ''
        if not jid:
            self._node, self._domain = ('', '')
        elif type(jid) in types.StringTypes:
            if jid.find('@') + 1:
                self._node, jid = jid.split('@', 1)
                self._node = self._node.lower()
            else:
                self._node = ''
            if jid.find('/') + 1:
                self._domain, tail = jid.split('/', 1)
            else:
                self._domain = jid
            self._domain = self._domain.lower()
        elif isinstance(jid, BareJID):
            self._node, self._domain, tail = jid.getNode(), jid.getDomain(), jid.getResource()
        else:
            raise (ValueError, 'JID can be specified as string or as instance of JID class.')
        return tail

    def getBareJID(self):
        return self

    def getNode(self):
        return self._node

    def setNode(self, node):
        if node is None:
            self._node = ''
        if type(node) in types.StringTypes:
            self._node = node.lower()
        else:
            self._node = node
        return

    def getDomain(self):
        return self._domain

    def setDomain(self, domain):
        raise domain or AssertionError('Domain no empty')
        self._domain = domain.lower()

    def getResource(self):
        return ''

    def setResource(self, resource):
        pass

    def __str__(self):
        if self._node:
            jid = '{0}@{1}'.format(self._node, self._domain)
        else:
            jid = self._domain
        return jid

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return self.__str__() == str(other)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __nonzero__(self):
        return self.__str__() != ''

    def __hash__(self):
        return hash(self.__str__())


class JID(BareJID):
    __slots__ = ('_resource',)

    def __init__(self, jid = None):
        super(JID, self).__init__(jid)

    def setJID(self, jid):
        self._resource = super(JID, self).setJID(jid)

    def getBareJID(self):
        return BareJID(self)

    def getResource(self):
        return self._resource

    def setResource(self, resource):
        self._resource = resource or ''

    def __str__(self):
        jid = super(JID, self).__str__()
        if self._resource:
            jid = '{0}/{1}'.format(jid, self._resource)
        return jid


class _DatabaseIDGetter(object):

    def getDatabaseID(self):
        value = getattr(self, '_node')
        if value:
            try:
                result = long(value)
            except ValueError:
                result = 0L

        else:
            result = 0L
        return result


class ContactBareJID(BareJID, _DatabaseIDGetter):

    def __hash__(self):
        return self.getDatabaseID()


class ContactJID(JID, _DatabaseIDGetter):

    def getBareJID(self):
        return ContactBareJID(self)

    def __hash__(self):
        return self.getDatabaseID()


def makeContactJID(dbID):
    jid = ContactBareJID()
    jid.setNode(long(dbID))
    jid.setDomain(g_settings.server.XMPP.domain)
    return jid
