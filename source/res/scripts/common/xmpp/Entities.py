# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/common/xmpp/Entities.py
# Compiled at: 2011-06-29 16:12:36
from xmpp.Stanzas import getAttr, getChild, jidAttr
import Event
from debug_utils import *
from wotdecorators import noexcept
TYPE_NONE = 0
TYPE_SESSION = 1
TYPE_MUC = 2

class Entity:
    count = 0

    def __init__(self, type, id):
        Entity.count += 1
        self.type = type
        self.connection = None
        self.id = id
        self.eventDisconnected = Event.Event()
        return

    def __del__(self):
        Entity.count -= 1

    def onStanza(self, stanza):
        pass

    def onDisconnected(self):
        self.connection = None
        self.eventDisconnected()
        return

    def onConnected(self):
        pass

    def connect(self, connection):
        if connection:
            self.connection = connection
            self.onConnected()


class Session(Entity):

    def __init__(self, connection, clan_conference):
        Entity.__init__(self, connection, TYPE_SESSION)
        self.clan_conference = clan_conference
        self.eventMessage = Event.Event()
        self.eventFriendOnline = Event.Event()
        self.eventFriendOffline = Event.Event()


class MUC(Entity):

    def __init__(self, id, room):
        Entity.__init__(self, TYPE_MUC, id)
        self.room_jid = room
        self.eventMessage = Event.Event()
        self.eventUserOnline = Event.Event()
        self.eventUserOffline = Event.Event()
