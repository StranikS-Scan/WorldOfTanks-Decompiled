# Embedded file name: scripts/client/messenger/proto/events.py
import Event

class _ChannelsSharedEvents(object):

    def __init__(self):
        super(_ChannelsSharedEvents, self).__init__()
        self.__eventManager = Event.EventManager()
        self.onChannelInited = Event.Event(self.__eventManager)
        self.onPlayerEnterChannelByAction = Event.Event(self.__eventManager)
        self.onChannelDestroyed = Event.Event(self.__eventManager)
        self.onConnectingToSecureChannel = Event.Event(self.__eventManager)
        self.onChannelInfoUpdated = Event.Event(self.__eventManager)
        self.onConnectStateChanged = Event.Event(self.__eventManager)
        self.onMessageReceived = Event.Event(self.__eventManager)
        self.onHistoryReceived = Event.Event(self.__eventManager)
        self.onCommandReceived = Event.Event(self.__eventManager)

    def clear(self):
        self.__eventManager.clear()


class ChannelEvents(object):
    __slots__ = ('onConnectStateChanged', 'onChannelInfoUpdated', 'onMembersListChanged', 'onMemberStatusChanged', '__eventManager')

    def __init__(self):
        super(ChannelEvents, self).__init__()
        self.__eventManager = Event.EventManager()
        self.onConnectStateChanged = Event.Event(self.__eventManager)
        self.onChannelInfoUpdated = Event.Event(self.__eventManager)
        self.onMembersListChanged = Event.Event(self.__eventManager)
        self.onMemberStatusChanged = Event.Event(self.__eventManager)

    def clear(self):
        self.__eventManager.clear()


class MemberEvents(object):
    __slots__ = ('onMemberStatusChanged', '__eventManager')

    def __init__(self):
        super(MemberEvents, self).__init__()
        self.__eventManager = Event.EventManager()
        self.onMemberStatusChanged = Event.Event(self.__eventManager)

    def clear(self):
        self.__eventManager.clear()


class _VOIPSharedEvents(object):

    def __init__(self):
        super(_VOIPSharedEvents, self).__init__()
        self.__eventManager = Event.EventManager()
        self.onCredentialReceived = Event.Event()
        self.onChannelEntered = Event.Event(self.__eventManager)
        self.onChannelLeft = Event.Event(self.__eventManager)

    def clear(self):
        self.__eventManager.clear()


class _UsersSharedEvents(object):
    __slots__ = ('__eventManager', 'onUsersListReceived', 'onFriendsReceived', 'onIgnoredReceived', 'onMutedReceived', 'onUserActionReceived', 'onUserStatusUpdated', 'onEmptyGroupsChanged', 'onClanMembersListChanged', 'onFindUsersComplete', 'onFindUsersFailed', 'onNotesListReceived', 'onFriendshipRequestsAdded', 'onFriendshipRequestsUpdated')

    def __init__(self):
        super(_UsersSharedEvents, self).__init__()
        self.__eventManager = Event.EventManager()
        self.onFriendsReceived = Event.Event()
        self.onIgnoredReceived = Event.Event()
        self.onMutedReceived = Event.Event()
        self.onUsersListReceived = Event.Event()
        self.onUserActionReceived = Event.Event(self.__eventManager)
        self.onEmptyGroupsChanged = Event.Event(self.__eventManager)
        self.onUserStatusUpdated = Event.Event(self.__eventManager)
        self.onClanMembersListChanged = Event.Event(self.__eventManager)
        self.onFindUsersComplete = Event.Event(self.__eventManager)
        self.onFindUsersFailed = Event.Event(self.__eventManager)
        self.onFriendshipRequestsAdded = Event.Event(self.__eventManager)
        self.onFriendshipRequestsUpdated = Event.Event(self.__eventManager)
        self.onNotesListReceived = Event.Event(self.__eventManager)

    def clear(self):
        self.__eventManager.clear()


class _ServiceChannelEvents(object):
    __slots__ = ('__eventManager', 'onServerMessageReceived', 'onCustomMessageDataReceived', 'onClientMessageReceived', 'onChatMessageReceived')

    def __init__(self):
        super(_ServiceChannelEvents, self).__init__()
        self.__eventManager = Event.EventManager()
        self.onServerMessageReceived = Event.Event(self.__eventManager)
        self.onCustomMessageDataReceived = Event.Event(self.__eventManager)
        self.onClientMessageReceived = Event.Event(self.__eventManager)
        self.onChatMessageReceived = Event.Event(self.__eventManager)

    def clear(self):
        self.__eventManager.clear()


class _MessengerEvents(object):
    __slots__ = ('__channels', '__users', '__serviceChannel', '__voip', 'onErrorReceived', 'onWarningReceived', 'onPluginConnected', 'onPluginDisconnected', 'onPluginConnectFailed')

    def __init__(self):
        super(_MessengerEvents, self).__init__()
        self.__channels = _ChannelsSharedEvents()
        self.__users = _UsersSharedEvents()
        self.__serviceChannel = _ServiceChannelEvents()
        self.__voip = _VOIPSharedEvents()
        self.onErrorReceived = Event.Event()
        self.onWarningReceived = Event.Event()
        self.onPluginConnected = Event.Event()
        self.onPluginDisconnected = Event.Event()
        self.onPluginConnectFailed = Event.Event()

    @property
    def channels(self):
        return self.__channels

    @property
    def users(self):
        return self.__users

    @property
    def serviceChannel(self):
        return self.__serviceChannel

    @property
    def voip(self):
        return self.__voip

    def clear(self):
        self.__channels.clear()
        self.__users.clear()
        self.__serviceChannel.clear()
        self.__voip.clear()
        self.onErrorReceived.clear()
        self.onWarningReceived.clear()


g_messengerEvents = _MessengerEvents()
