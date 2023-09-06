# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/skeletons/gui/web.py
import typing
if typing.TYPE_CHECKING:
    from gui.clans.clan_account_profile import MyClanAccountProfile

class IWebController(object):

    def addListener(self, listener):
        raise NotImplementedError

    def removeListener(self, listener):
        raise NotImplementedError

    def init(self):
        raise NotImplementedError

    def fini(self):
        raise NotImplementedError

    @property
    def isStarted(self):
        raise NotImplementedError

    def start(self, force=True):
        raise NotImplementedError

    def stop(self):
        raise NotImplementedError

    def invalidate(self):
        raise NotImplementedError

    def getClanDossier(self, clanDbID=None):
        raise NotImplementedError

    def login(self, callback):
        raise NotImplementedError

    def resyncLogin(self, forceLogin=False):
        raise NotImplementedError

    def sendRequest(self, ctx, callback=None, allowDelay=None):
        raise NotImplementedError

    def getStateID(self):
        raise NotImplementedError

    def isEnabled(self):
        raise NotImplementedError

    def isAvailable(self):
        raise NotImplementedError

    def getWebRequester(self):
        raise NotImplementedError

    def getAccountProfile(self):
        raise NotImplementedError

    def getLimits(self):
        raise NotImplementedError

    def getClanDbID(self):
        raise NotImplementedError

    def changeState(self, state):
        raise NotImplementedError

    def onStateUpdated(self):
        raise NotImplementedError

    def isLoggedOn(self):
        raise NotImplementedError

    def updateClanCommonDataCache(self, cache):
        raise NotImplementedError

    def clearClanCommonDataCache(self):
        raise NotImplementedError

    def getClanCommonData(self, clanDbID):
        raise NotImplementedError

    def requestUsers(self, dbIDs, callback):
        raise NotImplementedError

    def getAccessTokenData(self, force, callback=None):
        raise NotImplementedError
