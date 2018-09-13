# Embedded file name: scripts/common/xmpp/Client.py
import base64
import hashlib
import re
import random
import xmpp.Connection as XMPPConnection
import xmpp.Stanzas as XMPPStanzas
import xmpp.Entities as XMPPEntities
from xmpp.Stanzas import getAttr, getChild, jidAttr
import Event
from debug_utils import *
from wotdecorators import noexcept

class Client:
    STATE_OFFLINE = 0
    STATE_CONNECT_TCP = 1
    STATE_CONNECT_XMPP = 2
    STATE_AUTHENTICATING = 3
    STATE_ONLINE = 4
    CLAN_CONFERENCE_NAME = u'conference'

    def __init__(self):
        self.clan_conference_host = None
        self.bare_jid = None
        self.connection = None
        self.state = Client.STATE_OFFLINE
        self.entities = {}
        self.tasks = {}
        self.eventDisconnected = Event.Event()
        self.eventConnected = Event.Event()
        return

    @noexcept
    def connect(self, host, credentials):
        LOG_NESTE('XMPP: Connecting to XMPP %s:%s: %s' % (host[0], host[1], credentials[0]))
        if self.connection:
            LOG_ERROR('XMPP: Client::connect: An existing connection exists')
            return False
        if not (host[0] and host[1] and credentials[0] and credentials[1]):
            LOG_ERROR('XMPP: Connection: Wrong host or credentials have been provided.')
            return False
        self.clan_conference_host = (Client.CLAN_CONFERENCE_NAME + u'.' + host[0]).lower()
        self.bare_jid = (credentials[0] + u'@' + host[0]).lower()
        self.__updateState(Client.STATE_CONNECT_TCP)
        self.connection = self.createConnection()
        self.connection.eventConnected += self.__onConnected
        self.connection.eventServerDisconnected += self.__onServerDisconnected
        self.connection.eventStanza += self.__onStanza
        if not self.connection.connect(host, credentials):
            return False
        return True

    @noexcept
    def disconnect(self):
        if not self.connection:
            return
        else:
            for entity in self.entities.values():
                entity.onDisconnected()

            self.connection.eventConnected -= self.__onConnected
            self.connection.eventServerDisconnected -= self.__onServerDisconnected
            self.connection.eventStanza -= self.__onStanza
            self.connection.disconnect()
            self.connection = None
            self.__updateState(Client.STATE_OFFLINE)
            self.entities = {}
            self.clan_conference_host = None
            self.bare_jid = None
            return

    def createConnection(self):
        return XMPPConnection.Connection()

    def __updateState(self, newState):
        oldState = self.state
        self.state = newState

    def __onStateOnline(self, stanza):
        stanzaName = stanza['name']
        stanzaFrom = getAttr(stanza, 'from') or u''
        stanzaId = getAttr(stanza, 'id') or u''
        bare_jid = jidAttr(stanzaFrom, 'bare')
        entity = self.entities.get(bare_jid)
        if entity:
            entity.onStanza(stanza)
        try:
            match = re.match(XMPPConnection.Connection.STANZA_ID_TEMPLATE, stanzaId)
            if match:
                self.tasks[int(match.group(1))].digest(stanza, int(match.group(2)))
        except:
            LOG_CURRENT_EXCEPTION()

        if stanzaName == 'stream:error':
            child = getChild(stanza, 'system-shutdown')
            if child:
                LOG_ERROR('XMPP: Stream error: %s' % stanza)
                self.__onServerDisconnected()
                return

    def __onStateAuthenticating(self, stanza):
        stanzaName = stanza['name']
        stanzaID = getAttr(stanza, 'id')
        stanzaType = getAttr(stanza, 'type')
        if stanzaName == 'challenge':
            self.__onStanzaAuthChallenge(stanza)
        elif stanzaName == 'success':
            self.connection.parser.newParser()
            self.connection.sendStanza(XMPPStanzas.STREAM_START % self.connection.host[0])
        elif stanzaName == 'stream:features':
            self.connection.sendStanza(XMPPStanzas.BIND_RESOURCE % XMPPConnection.Connection.RESOURCE)
        elif stanzaName == 'iq':
            if stanzaType == 'result':
                if stanzaID == 'bind_2':
                    self.connection.sendStanza(XMPPStanzas.SESSION)
                elif stanzaID == 'sess_1':
                    self.__updateState(Client.STATE_ONLINE)
                    self.eventConnected()
                    self.connection.sendStanza(XMPPStanzas.presence())
        else:
            LOG_ERROR('Unhandled stanza name:', stanzaName, stanza)

    def __onStanzaAuthChallenge(self, nextStanza):

        def H(s):
            return hashlib.md5(s).digest()

        def HEXH(s):
            return hashlib.md5(s).hexdigest()

        def HEXKD(k, s):
            return HEXH('%s:%s' % (k, s))

        challenge = base64.b64decode(nextStanza['data'])
        if challenge.startswith('rspauth'):
            self.connection.sendStanza(XMPPStanzas.AUTHENTICATION_MD5_END)
        else:
            nonce = challenge.split('nonce=')[1].split('"')[1]
            cnonce = ''
            for i in range(32):
                cnonce += '%x' % random.randint(0, 15)

            userHash = H(':'.join((self.connection.credentials[0], self.connection.host[0], self.connection.credentials[1])))
            A1 = ':'.join((userHash, nonce, cnonce))
            A2 = 'AUTHENTICATE:xmpp/%s' % self.connection.host[0]
            tmpJoin = ':'.join((nonce,
             '00000001',
             cnonce,
             'auth',
             HEXH(A2)))
            response = HEXKD(HEXH(A1), tmpJoin)
            authBody = XMPPStanzas.AUTHENTICATION_MD5_BODY % (self.connection.credentials[0],
             self.connection.host[0],
             nonce,
             cnonce,
             self.connection.host[0],
             response)
            self.connection.sendStanza(XMPPStanzas.AUTHENTICATION_MD5_RESPONSE % base64.b64encode(authBody))

    def __onConnected(self):
        self.__updateState(Client.STATE_CONNECT_XMPP)
        self.connection.sendStanza(u"<?xml version='1.0'?>" + XMPPStanzas.STREAM_START % self.connection.host[0])

    def __onServerDisconnected(self):
        LOG_NESTE('XMPP: Jabber server has closed connection.')
        self.disconnect()
        self.eventDisconnected()

    def __onStanza(self, stanza):
        stanzaName = stanza['name']
        if self.state == Client.STATE_CONNECT_XMPP:
            if stanzaName == 'stream:features':
                self.__updateState(Client.STATE_AUTHENTICATING)
                b64 = base64.b64encode('\x00%s\x00%s' % (self.connection.credentials[0], self.connection.credentials[1]))
                self.connection.sendStanza(XMPPStanzas.AUTHENTICATION_PLAIN % b64)
        elif self.state == Client.STATE_AUTHENTICATING:
            self.__onStateAuthenticating(stanza)
        elif self.state == Client.STATE_ONLINE:
            self.__onStateOnline(stanza)
        else:
            LOG_ERROR('Unhandled state (%d) stanza' % self.state, stanza)

    def attachEntity(self, entity):
        if entity.id in self.entities:
            return False
        self.entities[entity.id] = entity
        entity.connect(self.connection)
        return True

    def addTask(self, task):
        if not task or not task.valid():
            LOG_ERROR("Can't validate task:", task, task.validation)
            return False
        self.__subscribeTask(task)
        self.tasks[task.id] = task
        task.connect(self.connection)
        return True

    def __removeTask(self, task):
        detached = self.tasks.pop(task.id)
        if not detached:
            LOG_ERROR("XMPP: Can't remove task %s from entity's task list" % task)
            return
        detached.disconnect()
        self.__unsubscribeTask(task)

    def __subscribeTask(self, task):
        task.eventSucceeded += self.__onTaskSucceeded
        task.eventFailed += self.__onTaskFailed

    def __unsubscribeTask(self, task):
        task.eventSucceeded -= self.__onTaskSucceeded
        task.eventFailed -= self.__onTaskFailed

    def __onTaskSucceeded(self, task):
        self.__removeTask(task)

    def __onTaskFailed(self, task):
        self.__removeTask(task)
