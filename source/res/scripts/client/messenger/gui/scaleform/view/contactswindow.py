# Embedded file name: scripts/client/messenger/gui/Scaleform/view/ContactsWindow.py
from debug_utils import LOG_DEBUG
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView
from gui.Scaleform.framework.entities.View import View
from gui.Scaleform.locale.MESSENGER import MESSENGER
from gui.Scaleform.managers.windows_stored_data import DATA_TYPE, TARGET_ID
from gui.Scaleform.managers.windows_stored_data import stored_window
from helpers import i18n
from messenger.gui.Scaleform.data import users_data_providers, search_data_providers
from messenger.gui.Scaleform.meta.ContactsWindowMeta import ContactsWindowMeta
from messenger.m_constants import PROTO_TYPE
from messenger.proto import proto_getter
from messenger.proto.interfaces import ISearchHandler
from gui import game_control

@stored_window(DATA_TYPE.UNIQUE_WINDOW, TARGET_ID.CHAT_MANAGEMENT)

class ContactsWindow(View, AbstractWindowView, ContactsWindowMeta, ISearchHandler):

    def __init__(self, ctx = None):
        super(ContactsWindow, self).__init__()
        self._friendsDP = None
        self._clanDP = None
        self._ignoredDP = None
        self._mutedDP = None
        self._searchDP = None
        return

    def _populate(self):
        super(ContactsWindow, self)._populate()
        self._friendsDP = users_data_providers.FriendsDataProvider()
        self._friendsDP.init(self.as_getFriendsDPS())
        self._clanDP = users_data_providers.ClanMembersDataProvider()
        self._clanDP.init(self.as_getClanDPS(), None)
        self._ignoredDP = users_data_providers.IgnoredDataProvider()
        self._ignoredDP.init(self.as_getIgnoredDPS())
        self._mutedDP = users_data_providers.MutedDataProvider()
        self._mutedDP.init(self.as_getMutedDPS())
        self._searchDP = search_data_providers.SearchUsersDataProvider()
        self._searchDP.init(self.as_getSearchDPS(), [self])
        self.as_setSearchResultTextS(self.getSearchLimitLabel())
        return

    def _dispose(self):
        if self._friendsDP is not None:
            self._friendsDP.fini()
            self._friendsDP = None
        if self._clanDP is not None:
            self._clanDP.fini()
            self._clanDP = None
        if self._ignoredDP is not None:
            self._ignoredDP.fini()
            self._ignoredDP = None
        if self._mutedDP is not None:
            self._mutedDP.fini()
            self._mutedDP = None
        if self._searchDP is not None:
            self._searchDP.fini()
            self._searchDP = None
        super(ContactsWindow, self)._dispose()
        return

    @proto_getter(PROTO_TYPE.MIGRATION)
    def proto(self):
        return None

    def onWindowClose(self):
        self.destroy()

    def isEnabledInRoaming(self, uid):
        roamingCtrl = game_control.g_instance.roaming
        return not roamingCtrl.isInRoaming() and not roamingCtrl.isPlayerInRoaming(uid)

    def getSearchLimitLabel(self):
        return i18n.makeString(MESSENGER.DIALOGS_SEARCHCONTACT_LABELS_RESULT, self._searchDP.processor.getSearchResultLimit())

    def searchContact(self, criteria):
        LOG_DEBUG('search contact')
        if self._searchDP.find(criteria):
            self.as_frozenSearchActionS(True)

    def onSearchComplete(self, result):
        LOG_DEBUG('search complete')
        self.as_frozenSearchActionS(False)

    def onSearchFailed(self, reason):
        LOG_DEBUG('search failed')
        self.as_frozenSearchActionS(False)

    def addToFriends(self, uid, name):
        LOG_DEBUG('addToFriends: ', uid)
        self.proto.contacts.addFriend(uid, name)

    def addToIgnored(self, uid, name):
        LOG_DEBUG('addToIgnored: ', uid)
        self.proto.contacts.addIgnored(uid, name)
