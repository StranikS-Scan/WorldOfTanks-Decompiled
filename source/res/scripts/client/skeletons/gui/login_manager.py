# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/skeletons/gui/login_manager.py
import typing
if typing.TYPE_CHECKING:
    from constants import LGC_PUBLICATION

class ILoginManager(object):
    onConnectionInitiated = None
    onConnectionRejected = None

    @property
    def servers(self):
        raise NotImplementedError

    @property
    def lgcAvailable(self):
        raise NotImplementedError

    def getLgcPublication(self):
        raise NotImplementedError

    @property
    def isLgcSteam(self):
        raise NotImplementedError

    def tryPrepareLGCLogin(self):
        raise NotImplementedError

    def checkLgcCouldRetry(self, loginStatus):
        raise NotImplementedError

    def addOnLgcErrorListener(self, listener):
        raise NotImplementedError

    def removeOnLgcErrorListener(self, listener):
        raise NotImplementedError

    def init(self):
        raise NotImplementedError

    def fini(self):
        raise NotImplementedError

    def initiateLogin(self, email, password, serverName, isSocialToken2Login, rememberUser):
        raise NotImplementedError

    def initiateSocialLogin(self, socialNetworkName, serverName, rememberUser, isRegistration):
        raise NotImplementedError

    def tryLgcLogin(self, serverName=None):
        raise NotImplementedError

    def stopLgc(self):
        raise NotImplementedError

    def initiateRelogin(self, login, token2, serverName):
        raise NotImplementedError

    def getPreference(self, key):
        raise NotImplementedError

    def clearPreferences(self):
        raise NotImplementedError

    def clearToken2Preference(self):
        raise NotImplementedError

    def writePreferences(self):
        raise NotImplementedError

    def writePeripheryLifetime(self):
        raise NotImplementedError

    @staticmethod
    def getAvailableSocialNetworks():
        raise NotImplementedError
