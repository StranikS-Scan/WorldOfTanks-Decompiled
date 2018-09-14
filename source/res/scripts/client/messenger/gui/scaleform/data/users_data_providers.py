# Embedded file name: scripts/client/messenger/gui/Scaleform/data/users_data_providers.py
from debug_utils import LOG_DEBUG
from gui.Scaleform.framework.entities.DAAPIDataProvider import DAAPIDataProvider
from messenger import g_settings
from messenger.m_constants import USER_TAG
from messenger.proto import shared_find_criteria
from messenger.proto.events import g_messengerEvents
from messenger.storage import storage_getter

def makeEmptyUserItem():
    return {'dbID': 0L,
     'userName': '',
     'fullName': '',
     'tags': [],
     'isOnline': False,
     'colors': [0, 0],
     'clanAbbrev': ''}


def makeUserItem(user):
    return {'dbID': user.getID(),
     'userName': user.getName(),
     'fullName': user.getFullName(),
     'tags': list(user.getTags()),
     'isOnline': user.isOnline(),
     'colors': g_settings.getColorScheme('rosters').getColors(user.getGuiType()),
     'clanAbbrev': user.getClanAbbrev()}


def getUsersCmp():

    def comparator(user, other):
        return cmp(user.getName().lower(), other.getName().lower())

    return comparator


class UsersDataProvider(object):

    def __init__(self, criteria):
        super(UsersDataProvider, self).__init__()
        self._list = []
        self._criteria = criteria

    def __del__(self):
        LOG_DEBUG('UsersDataProvider deleted:', self)

    @storage_getter('users')
    def usersStorage(self):
        return None

    @property
    def collection(self):
        return self._list

    def emptyItem(self):
        return makeEmptyUserItem()

    def buildList(self):
        self._list = map(self._makeUserItem, sorted(self._getRosterList(), cmp=getUsersCmp()))

    def initialize(self, onlineMode = None):
        usersEvents = g_messengerEvents.users
        usersEvents.onUsersListReceived += self._onUsersReceived
        usersEvents.onUserActionReceived += self._onUserActionReceived
        self._criteria.setOnlineMode(onlineMode)
        self.buildList()
        self._refresh()

    def fini(self):
        self._list = []
        self._criteria = None
        usersEvents = g_messengerEvents.users
        usersEvents.onUsersListReceived -= self._onUsersReceived
        usersEvents.onUserActionReceived -= self._onUserActionReceived
        return

    def getOnlineMode(self):
        return self._criteria.getOnlineMode()

    def setOnlineMode(self, onlineMode):
        if self._criteria.setOnlineMode(onlineMode):
            self.buildList()
            self._refresh()

    def _refresh(self):
        pass

    def _getRosterList(self):
        return self.usersStorage.getList(self._criteria)

    def _onUsersReceived(self, _):
        self.buildList()
        self._refresh()

    def _onUserActionReceived(self, action, user):
        self.buildList()
        self._refresh()

    def _makeUserItem(self, user):
        return makeUserItem(user)


class DAAPIUsersDataProvider(UsersDataProvider, DAAPIDataProvider):

    def __init__(self, criteria):
        super(DAAPIUsersDataProvider, self).__init__(criteria)

    def init(self, flashObject, onlineMode = None):
        self.setFlashObject(flashObject)
        self.initialize(onlineMode)

    def fini(self):
        self._dispose()
        super(DAAPIUsersDataProvider, self).fini()

    def _refresh(self):
        self.refresh()
        super(DAAPIUsersDataProvider, self)._refresh()


class FriendsDataProvider(DAAPIUsersDataProvider):

    def __init__(self):
        super(FriendsDataProvider, self).__init__(shared_find_criteria.FriendsFindCriteria())

    def init(self, flashObject, onlineMode = None):
        events = g_messengerEvents.users
        events.onUserStatusUpdated += self._onUserStatusUpdated
        super(FriendsDataProvider, self).init(flashObject, onlineMode)

    def fini(self):
        events = g_messengerEvents.users
        events.onUserStatusUpdated -= self._onUserStatusUpdated
        super(FriendsDataProvider, self).fini()

    def _onUsersReceived(self, tags):
        if {USER_TAG.FRIEND, USER_TAG.MUTED} & tags:
            super(FriendsDataProvider, self)._onUsersReceived(tags)

    def _onUserStatusUpdated(self, _):
        self.buildList()
        self._refresh()


class IgnoredDataProvider(DAAPIUsersDataProvider):

    def __init__(self):
        super(IgnoredDataProvider, self).__init__(shared_find_criteria.IgnoredFindCriteria())

    def _onUsersReceived(self, tags):
        if USER_TAG.IGNORED in tags:
            super(IgnoredDataProvider, self)._onUsersReceived(tags)


class MutedDataProvider(DAAPIUsersDataProvider):

    def __init__(self):
        super(MutedDataProvider, self).__init__(shared_find_criteria.MutedFindCriteria())

    def _onUsersReceived(self, tags):
        if USER_TAG.MUTED in tags:
            super(MutedDataProvider, self)._onUsersReceived(tags)


class ClanMembersDataProvider(DAAPIUsersDataProvider):

    def __init__(self):
        super(ClanMembersDataProvider, self).__init__(shared_find_criteria.OnlineFindCriteria())

    def init(self, flashObject, onlineMode = None):
        super(ClanMembersDataProvider, self).init(flashObject, onlineMode)
        usersEvents = g_messengerEvents.users
        usersEvents.onClanMembersListChanged += self._onClanMembersListChanged
        usersEvents.onUserStatusUpdated += self._onUserStatusUpdated

    def fini(self):
        super(ClanMembersDataProvider, self).fini()
        usersEvents = g_messengerEvents.users
        usersEvents.onClanMembersListChanged -= self._onClanMembersListChanged
        usersEvents.onUserStatusUpdated -= self._onUserStatusUpdated

    def _getRosterList(self):
        return self.usersStorage.getList(self._criteria, iterator=self.usersStorage.getClanMembersIterator())

    def _onClanMembersListChanged(self):
        self.buildList()
        self.refresh()

    def _onUserStatusUpdated(self, user):
        if self.usersStorage.isClanMember(user.getID()):
            self.buildList()
            self.refresh()
