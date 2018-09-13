# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/messengerBar/ContactsListButton.py
from debug_utils import LOG_DEBUG
from gui.Scaleform.daapi.view.meta.ContactsListButtonMeta import ContactsListButtonMeta
from messenger.proto.events import g_messengerEvents
from messenger.storage import storage_getter
from messenger.proto.bw import find_criteria

class ContactsListButton(ContactsListButtonMeta):

    def __init__(self):
        super(ContactsListButton, self).__init__()

    def _populate(self):
        super(ContactsListButton, self)._populate()
        usersEvents = g_messengerEvents.users
        usersEvents.onUsersRosterReceived += self._onUsersRosterReceived
        usersEvents.onUserRosterChanged += self._onUserRosterChanged
        usersEvents.onUserRosterStatusUpdated += self._onUserRosterStatusUpdated
        self.__setUsersCount()

    def _onUserRosterStatusUpdated(self, _):
        self.__setUsersCount()

    def _onUsersRosterReceived(self):
        self.__setUsersCount()

    def _onUserRosterChanged(self, action, user):
        self.__setUsersCount()

    def __setUsersCount(self):
        allFriendsList = self.usersStorage.getList(find_criteria.BWFriendFindCriteria())
        onlineFriendsCount = 0
        for friend in allFriendsList:
            if friend.isOnline():
                onlineFriendsCount += 1

        self.as_setContactsCountS(onlineFriendsCount)

    @storage_getter('users')
    def usersStorage(self):
        return None

    def _dispose(self):
        usersEvents = g_messengerEvents.users
        usersEvents.onUsersRosterReceived -= self._onUsersRosterReceived
        usersEvents.onUserRosterChanged -= self._onUserRosterChanged
        usersEvents.onUserRosterStatusUpdated -= self._onUserRosterStatusUpdated
        super(ContactsListButton, self)._dispose()
