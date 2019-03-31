# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/common/xmpp/Task.py
# Compiled at: 2011-06-29 16:12:36
import Event
from debug_utils import *
import Connection

class Task:
    ids = 0
    count = 0
    STANZA_ID_FORMAT = Connection.Connection.RESOURCE + u'_%d_%d'

    @staticmethod
    def nextId():
        Task.ids += 1
        return Task.ids

    def __init__(self, params):
        Task.count += 1
        self.id = Task.nextId()
        self.subId = 0
        self.params = params
        self.connection = None
        self.validation = set()
        self.lastError = ''
        self.eventSucceeded = Event.Event()
        self.eventFailed = Event.Event()
        self.eventError = Event.Event()
        return

    def __del__(self):
        Task.count -= 1

    def __str__(self):
        return u'Task %d: state=%d, params:%s, lastError:%s, ' % (self.id,
         self.subId,
         self.params,
         self.lastError)

    def nextSubId(self):
        self.subId += 1
        return self.subId

    def stanzaId(self):
        return Task.STANZA_ID_FORMAT % (self.id, self.subId)

    def onConnected(self):
        pass

    def onDisconnected(self):
        pass

    def valid(self):
        return set(self.validation).issubset(set(self.params.keys()))

    def connect(self, connection):
        self.connection = connection
        self.onConnected()

    def disconnect(self):
        self.connection = None
        self.onDisconnected()
        return

    def digest(self, stanza, subId):
        pass
