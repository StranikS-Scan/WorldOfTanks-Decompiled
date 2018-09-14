# Embedded file name: scripts/client/messenger/proto/interfaces.py


class IProtoPlugin(object):
    __slots__ = ('__weakref__',)

    def connect(self, scope):
        pass

    def disconnect(self):
        pass

    def view(self, scope):
        pass

    def setFilters(self, msgFilterChain):
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
        return 0


class IChatMessage(object):

    def getMessage(self):
        return ''


class IChatError(IChatMessage):

    def getTitle(self):
        return ''

    def isModal(self):
        return False


class IVOIPChatProvider(object):

    def getChannelParams(self):
        return ('', '')

    def requestCredentials(self, reset = 0):
        pass

    def logVivoxLogin(self):
        pass
