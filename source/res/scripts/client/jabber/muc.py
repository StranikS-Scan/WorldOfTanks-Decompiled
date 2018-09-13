# Embedded file name: scripts/client/Jabber/MUC.py
import xmpp.Entities as XMPPEntities
import xmpp.Stanzas as XMPPStanzas
from xmpp.Stanzas import getAttr, getChild, jidAttr
from wotdecorators import noexcept

class MUC(XMPPEntities.MUC):

    def __init__(self, room):
        XMPPEntities.MUC.__init__(self, room, room)

    @noexcept
    def sendMessage(self, uMessage):
        if self.connection:
            self.connection.sendStanza(XMPPStanzas.mucMessage(self.connection.jid, self.room_jid, XMPPStanzas.xmlText(uMessage)))
            return True
        return False

    def onConnected(self):
        to = self.room_jid + u'/' + self.connection.credentials[0]
        self.connection.sendStanza(XMPPStanzas.mucPresence(self.connection.jid, to))

    def onStanza(self, stanza):
        XMPPEntities.MUC.onStanza(self, stanza)
        stanzaName = stanza['name']
        if stanzaName == 'message':
            self.__onStanzaMessage(stanza)
        elif stanzaName == 'presence':
            self.__onStanzaPresence(stanza)
        elif stanzaName == 'iq':
            self.__onStanzaInfoQuery(stanza)

    def __onStanzaMessage(self, stanza):
        from_jid = getAttr(stanza, 'from').encode('utf-8')
        user = jidAttr(from_jid, 'muc_user')
        messageType = getAttr(stanza, 'type')
        if messageType == 'error':
            return
        body = getChild(stanza, 'body')
        if not body:
            return
        self.eventMessage(user, body['data'].encode('utf-8'))

    def __onStanzaPresence(self, stanza):
        from_jid = getAttr(stanza, 'from').encode('utf8')
        user = jidAttr(from_jid, 'muc_user')
        presenceType = getAttr(stanza, 'type')
        if not presenceType:
            presenceType = 'available'
        self.eventUserOffline(user) if presenceType == 'unavailable' else self.eventUserOnline(user)

    def __onStanzaInfoQuery(self, stanza):
        pass
