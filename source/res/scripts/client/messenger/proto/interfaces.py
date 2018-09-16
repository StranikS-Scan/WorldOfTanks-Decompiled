# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/proto/interfaces.py


class IProtoPlugin(object):
    __slots__ = ('__weakref__',)

    def connect(self, scope):
        pass

    def disconnect(self):
        pass

    def view(self, scope):
        pass

    def goToReplay(self):
        pass

    def setFilters(self, msgFilterChain):
        pass

    def init(self):
        pass

    def clear(self):
        pass

    def isConnected(self):
        return False


class IProtoSettings(object):

    def update(self, data):
        pass

    def clear(self):
        pass

    def isEnabled(self):
        return False


class IProtoLimits(object):

    def getMessageMaxLength(self):
        raise NotImplementedError

    def getBroadcastCoolDown(self):
        raise NotImplementedError

    def getHistoryMaxLength(self):
        raise NotImplementedError


class IBattleCommandFactory(object):

    def createByName(self, name):
        return None

    def createByNameTarget(self, name, targetID):
        return None

    def createByCellIdx(self, cellIdx):
        return None

    def create4Reload(self, isCassetteClip, timeLeft, quantity):
        return None

    def createSPGAimAreaCommand(self, desiredShotPosition, cellIdx, reloadTime):
        return None


class IUnitCommandFactory(object):

    def createByCellIdx(self, cellIdx):
        return None


class IEntityFindCriteria(object):

    def filter(self, entity):
        return False


class ISearchHandler(object):

    def onSearchComplete(self, result):
        pass

    def onSearchFailed(self, reason):
        pass

    def onExcludeFromSearch(self, entity):
        pass


class ISearchProcessor(object):

    def addHandler(self, handler):
        pass

    def removeHandler(self, handler):
        pass

    def find(self, token, **kwargs):
        pass

    def getSearchResultLimit(self):
        pass


class IChatMessage(object):

    def getMessage(self):
        pass


class IChatError(IChatMessage):

    def getTitle(self):
        pass

    def isModal(self):
        return False


class IVOIPChatProvider(object):

    def getChannelParams(self):
        pass

    def requestCredentials(self, reset=0):
        pass

    def logVivoxLogin(self):
        pass


class IVOIPChatController(object):

    def start(self):
        raise NotImplementedError

    def stop(self):
        raise NotImplementedError

    def isReady(self):
        raise NotImplementedError

    def isPlayerSpeaking(self, accountDBID):
        raise NotImplementedError

    def isVOIPEnabled(self):
        raise NotImplementedError

    def isVivox(self):
        raise NotImplementedError

    def isYY(self):
        raise NotImplementedError

    def invalidateInitialization(self):
        raise NotImplementedError

    def requestCaptureDevices(self, firstTime=False, callback=None):
        raise NotImplementedError


class IUserSearchLimits(object):

    def getMaxResultSize(self):
        raise NotImplementedError

    def getRequestCooldown(self):
        raise NotImplementedError
