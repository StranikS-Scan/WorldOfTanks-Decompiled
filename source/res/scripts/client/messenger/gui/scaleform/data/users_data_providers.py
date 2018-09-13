# Embedded file name: scripts/client/messenger/gui/Scaleform/data/users_data_providers.py
from debug_utils import LOG_DEBUG
from gui.Scaleform.framework.entities.DAAPIDataProvider import DAAPIDataProvider
from messenger import g_settings
from messenger.proto.bw import find_criteria
from messenger.proto.events import g_messengerEvents
from messenger.storage import storage_getter

def makeEmptyUserItem():
    return {'uid': 0L,
     'userName': '',
     'chatRoster': 0,
     'online': False,
     'himself': False,
     'displayName': '',
     'colors': [0, 0]}


def makeUserItem(user):
    return {'uid': user.getID(),
     'userName': user.getName(),
     'chatRoster': user.getRoster(),
     'online': user.isOnline(),
     'himself': user.isCurrentPlayer(),
     'displayName': user.getFullName(),
     'colors': g_settings.getColorScheme('rosters').getColors(user.getGuiType())}


def getUsersCmp():

    def comparator(user, other):
        return cmp(user.getName().lower(), other.getName().lower())

    return comparator


class UsersDataProvider(DAAPIDataProvider):

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

    def init(self, flashObject, onlineMode = None):
        self.setFlashObject(flashObject)
        usersEvents = g_messengerEvents.users
        usersEvents.onUsersRosterReceived += self._onUsersRosterReceived
        usersEvents.onUserRosterChanged += self._onUserRosterChanged
        self._criteria.setOnlineMode(onlineMode)
        self.buildList()
        self.refresh()

    def fini(self):
        self._dispose()
        self._list = []
        self._criteria = None
        usersEvents = g_messengerEvents.users
        usersEvents.onUsersRosterReceived -= self._onUsersRosterReceived
        usersEvents.onUserRosterChanged -= self._onUserRosterChanged
        return

    def getOnlineMode(self):
        return self._criteria.getOnlineMode()

    def setOnlineMode(self, onlineMode):
        if self._criteria.setOnlineMode(onlineMode):
            self.buildList()
            self.refresh()

    def _getRosterList(self):
        return self.usersStorage.getList(self._criteria)

    def _onUsersRosterReceived(self):
        self.buildList()
        self.refresh()

    def _onUserRosterChanged(self, action, user):
        self.buildList()
        self.refresh()

    def _makeUserItem(self, user):
        return makeUserItem(user)


class FriendsDataProvider(UsersDataProvider):

    def __init__(self):
        super(FriendsDataProvider, self).__init__(find_criteria.BWFriendFindCriteria())

    def init(self, flashObject, onlineMode = None):
        super(FriendsDataProvider, self).init(flashObject, onlineMode)
        g_messengerEvents.users.onUserRosterStatusUpdated += self._onUserRosterStatusUpdated

    def fini(self):
        super(FriendsDataProvider, self).fini()
        g_messengerEvents.users.onUserRosterStatusUpdated -= self._onUserRosterStatusUpdated

    def _onUserRosterStatusUpdated(self, _):
        self.buildList()
        self.refresh()


class IgnoredDataProvider(UsersDataProvider):

    def __init__(self):
        super(IgnoredDataProvider, self).__init__(find_criteria.BWIgnoredFindCriteria())


class MutedDataProvider(UsersDataProvider):

    def __init__(self):
        super(MutedDataProvider, self).__init__(find_criteria.BWMutedFindCriteria())


class ClanMembersDataProvider(UsersDataProvider):

    def __init__(self):
        super(ClanMembersDataProvider, self).__init__(find_criteria.BWOnlineFindCriteria())

    def init(self, flashObject, onlineMode = None):
        super(ClanMembersDataProvider, self).init(flashObject, onlineMode)
        usersEvents = g_messengerEvents.users
        usersEvents.onClanMembersListChanged += self._onClanMembersListChanged
        usersEvents.onUserRosterStatusUpdated += self._onUserRosterStatusUpdated

    def fini(self):
        super(ClanMembersDataProvider, self).fini()
        usersEvents = g_messengerEvents.users
        usersEvents.onClanMembersListChanged -= self._onClanMembersListChanged
        usersEvents.onUserRosterStatusUpdated -= self._onUserRosterStatusUpdated

    def _getRosterList(self):
        return self.usersStorage.getList(self._criteria, iterator=self.usersStorage.getClanMembersIterator())

    def _onClanMembersListChanged(self):
        self.buildList()
        self.refresh()

    def _onUserRosterStatusUpdated(self, user):
        if self.usersStorage.isClanMember(user.getID()):
            self.buildList()
            self.refresh()
