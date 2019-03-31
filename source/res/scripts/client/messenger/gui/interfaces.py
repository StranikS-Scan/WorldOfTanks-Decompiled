# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/gui/interfaces.py
# Compiled at: 2011-05-19 16:52:43


class DispatcherProxyHolder(object):
    _dispatcherProxy = None


class MessengerWindowInterface(DispatcherProxyHolder):
    channels = property(lambda self: self._dispatcherProxy.channels)
    users = property(lambda self: self._dispatcherProxy.users)

    def show(self):
        pass

    def close(self):
        pass

    def editing(self):
        return False

    def populateUI(self, *args):
        pass

    def dispossessUI(self):
        pass

    def addChannelMessage(self, wrapper):
        """
        Adds message to channel
        @param wrapper: object hold message data
        """
        pass

    def addSystemMessage(self, message):
        """
        Adds system message to channel
        @param wrapper: object hold message data
        """
        pass

    def addChannel(self, channel):
        """
        Adds dummy channel
        @param channel: object hold channel data
        """
        return True

    def removeChannel(self, cid):
        """
        Remove dummy channel
        @param cid: channel id
        """
        return True

    def getChannelPage(self, cid):
        """
        Gets channel page by cid
        @param cid: channel id
        """
        pass

    def clear(self):
        """
        Clear player data, when disconnect
        """
        pass

    def showActionFailureMessage(self, message, title=None, modal=None):
        pass

    def setJoinedToLazyChannel(self, cid, joined):
        pass

    def refreshChannelList(self):
        pass


class MessengerPageInterface(DispatcherProxyHolder):
    channels = property(lambda self: self._dispatcherProxy.channels)
    users = property(lambda self: self._dispatcherProxy.users)
    invites = property(lambda self: self._dispatcherProxy.invites)

    def format(self, message, system=False):
        """
        Format message
        """
        return message.data

    def addMessage(self, message, format=True, system=False):
        pass

    def addSystemMessage(self, message):
        pass

    def addMember(self, member):
        """
        Adds member to message page
        """
        return True

    def addMembers(self, members):
        """
        Adds member to message page
        """
        return True

    def removeMember(self, uid):
        """
        Remove member from message page
        @param uid: member id
        """
        return True

    def removeMembers(self, members):
        """
        Remove members from message page
        @param members: member list
        """
        return True

    def setMemberStatus(self, uid, status):
        pass

    def open(self):
        pass

    def close(self):
        pass

    def clear(self):
        pass


class ProtocolPlugin(DispatcherProxyHolder):
    channels = property(lambda self: self._dispatcherProxy.channels)

    def connect(self):
        pass

    def disconnect(self):
        pass

    def broadcast(self, cid, message):
        return False
