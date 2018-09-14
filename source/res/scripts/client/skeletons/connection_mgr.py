# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/skeletons/connection_mgr.py
from Event import Event

class IConnectionManager(object):
    onLoggedOn = None
    onConnected = None
    onRejected = None
    onDisconnected = None
    onKickedFromServer = None
    onKickWhileLoginReceived = None
    onQueued = None

    @property
    def serverUserName(self):
        raise NotImplementedError

    @property
    def serverUserNameShort(self):
        raise NotImplementedError

    @property
    def peripheryID(self):
        raise NotImplementedError

    @property
    def areaID(self):
        raise NotImplementedError

    @property
    def url(self):
        raise NotImplementedError

    @property
    def loginName(self):
        raise NotImplementedError

    @property
    def lastLoginName(self):
        raise NotImplementedError

    @property
    def databaseID(self):
        raise NotImplementedError

    def initiateConnection(self, params, password, serverName):
        raise NotImplementedError

    def stopRetryConnection(self):
        raise NotImplementedError

    def disconnect(self):
        raise NotImplementedError

    def setKickedFromServer(self, reason, isBan, expiryTime):
        raise NotImplementedError

    def isDisconnected(self):
        raise NotImplementedError

    def isStandalone(self):
        raise NotImplementedError

    def isConnected(self):
        raise NotImplementedError

    def checkClientServerVersions(self, clientVersion, serverVersion):
        raise NotImplementedError
