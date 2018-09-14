# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/messengerBar/ContactsListButton.py
from gui.Scaleform.daapi.view.meta.ContactsListButtonMeta import ContactsListButtonMeta
from messenger.m_constants import USER_ACTION_ID as _ACTION_ID, USER_TAG
from messenger.proto.events import g_messengerEvents
from messenger.proto.shared_find_criteria import FriendsFindCriteria
from messenger.storage import storage_getter

class ContactsListButton(ContactsListButtonMeta):

    def __init__(self):
        super(ContactsListButton, self).__init__()
        self.__friends = {}
        self.__count = 0

    @storage_getter('users')
    def usersStorage(self):
        return None

    def _populate(self):
        super(ContactsListButton, self)._populate()
        events = g_messengerEvents.users
        events.onUsersListReceived += self.__me_onUsersListReceived
        events.onUserActionReceived += self.__me_onUserActionReceived
        events.onUserStatusUpdated += self.__me_onUserStatusUpdated
        self.__setContactsCount()

    def _dispose(self):
        events = g_messengerEvents.users
        events.onUsersListReceived -= self.__me_onUsersListReceived
        events.onUserActionReceived -= self.__me_onUserActionReceived
        events.onUserStatusUpdated -= self.__me_onUserStatusUpdated
        super(ContactsListButton, self)._dispose()

    def __setContactsCount(self):
        self.__friends = dict(map(lambda friend: (friend.getID(), 1 if friend.isOnline() else 0), self.usersStorage.getList(FriendsFindCriteria())))
        self.__showContactsCount()

    def __showContactsCount(self):
        count = sum(self.__friends.values())
        if count != self.__count:
            self.__count = count
            self.as_setContactsCountS(self.__count)

    def __me_onUsersListReceived(self, tags):
        if USER_TAG.FRIEND in tags:
            self.__setContactsCount()

    def __me_onUserStatusUpdated(self, user):
        if user.isFriend():
            self.__friends[user.getID()] = 1 if user.isOnline() else 0
            self.__showContactsCount()

    def __me_onUserActionReceived(self, actionID, user):
        dbID = user.getID()
        if actionID in (_ACTION_ID.FRIEND_REMOVED, _ACTION_ID.IGNORED_ADDED):
            self.__friends.pop(dbID, None)
        elif actionID == _ACTION_ID.FRIEND_ADDED:
            self.__friends[dbID] = 1 if user.isOnline() else 0
        self.__showContactsCount()
        return
