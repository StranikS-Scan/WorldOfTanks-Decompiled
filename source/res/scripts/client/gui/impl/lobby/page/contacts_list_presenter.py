# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/page/contacts_list_presenter.py
from __future__ import absolute_import
import typing
from gui.impl.gen.view_models.views.lobby.page.footer.contacts_list_model import ContactsListModel
from gui.impl.pub.view_component import ViewComponent
from messenger.m_constants import USER_TAG, USER_ACTION_ID
from messenger.proto.events import g_messengerEvents
from messenger.proto.shared_find_criteria import FriendsFindCriteria
from messenger.storage import storage_getter
if typing.TYPE_CHECKING:
    from messenger.proto.bw.entities import BWUserEntity
    from messenger.storage import UsersStorage

class ContactsListPresenter(ViewComponent[ContactsListModel]):

    def __init__(self):
        super(ContactsListPresenter, self).__init__(model=ContactsListModel)

    def _getEvents(self):
        return ((g_messengerEvents.users.onUsersListReceived, self.__onUsersListReceived), (g_messengerEvents.users.onUserActionReceived, self.__onUserActionReceived), (g_messengerEvents.users.onUserStatusUpdated, self.__onUserStatusUpdated))

    def _onLoading(self, *args, **kwargs):
        super(ContactsListPresenter, self)._onLoading(*args, **kwargs)
        self.__updateContactsCount()

    @storage_getter('users')
    def __usersStorage(self):
        return None

    def __onUsersListReceived(self, tags):
        if USER_TAG.FRIEND in tags:
            self.__updateContactsCount()

    def __onUserStatusUpdated(self, user):
        if user.isFriend():
            self.__updateContactsCount()

    def __onUserActionReceived(self, actionID, *args):
        if actionID in (USER_ACTION_ID.FRIEND_REMOVED,
         USER_ACTION_ID.IGNORED_ADDED,
         USER_ACTION_ID.TMP_IGNORED_ADDED,
         USER_ACTION_ID.FRIEND_ADDED):
            self.__updateContactsCount()

    def __updateContactsCount(self):
        friends = self.__usersStorage.getList(FriendsFindCriteria())
        onlineFriendsCount = sum((1 for friend in friends if friend.isOnline()))
        if onlineFriendsCount != self.getViewModel().getContactsCount():
            self.getViewModel().setContactsCount(onlineFriendsCount)
