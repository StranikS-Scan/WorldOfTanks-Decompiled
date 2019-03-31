# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/Jabber/Client.py
# Compiled at: 2011-06-29 16:12:36
from debug_utils import LOG_ERROR, LOG_CURRENT_EXCEPTION
from wotdecorators import noexcept
import xmpp.Client as XMPPClient
import xmpp.Entities as XMPPEntities
import MUC

class Client(XMPPClient.Client):

    def __init__(self):
        XMPPClient.Client.__init__(self)

    @noexcept
    def joinClanConference(self, uName):
        return self.joinConference(uName, XMPPClient.Client.CLAN_CONFERENCE_NAME)

    @noexcept
    def joinConference(self, uRoom, uConference):
        if not self.connection:
            return None
        room_jid = u'%s@%s.%s' % (uRoom, uConference, self.connection.host[0])
        entity = MUC.MUC(room_jid)
        if self.attachEntity(entity):
            return entity
        else:
            return None
