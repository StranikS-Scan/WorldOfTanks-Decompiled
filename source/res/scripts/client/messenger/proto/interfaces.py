# Embedded file name: scripts/client/messenger/proto/interfaces.py


class IProtoPlugin(object):

    def connect(self, scope):
        pass

    def disconnect(self):
        pass

    def view(self, scope):
        pass

    def clear(self):
        pass


class IProtoSettings(object):

    def update(self, data):
        pass

    def clear(self):
        pass

    def isEnabled(self):
        return False


class IEntityFindCriteria(object):

    def filter(self, entity):
        return False


class ISearchHandler(object):

    def onSearchComplete(self, result):
        pass

    def onSearchFailed(self, reason):
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


class IServerError(object):

    def getTitle(self):
        return ''

    def getMessage(self):
        return ''

    def isModal(self):
        return False


class IIncomingMessageFilter(object):

    def filter(self, message):
        pass


class IOutgoingMessageFilter(object):

    def filter(self, message):
        pass
