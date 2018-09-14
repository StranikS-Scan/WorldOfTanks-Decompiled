# Embedded file name: scripts/client/messenger/gui/Scaleform/view/ContactsTreeComponent.py
from helpers.i18n import makeString
from gui.Scaleform.daapi.view.meta.ContactsTreeComponentMeta import ContactsTreeComponentMeta
from gui.Scaleform.locale.MESSENGER import MESSENGER
from messenger.gui.Scaleform.data.contacts_data_provider import ContactsDataProvider
from messenger.gui.Scaleform.view import ACCOUNT_NAME_MIN_CHARS_LENGTH, ACCOUNT_NAME_MAX_CHARS_LENGTH
import Event

class ContactsTreeComponent(ContactsTreeComponentMeta):
    LIST_EMPTY_STATE = 'listEmptyState'

    def __init__(self):
        super(ContactsTreeComponent, self).__init__()
        self._mainDP = ContactsDataProvider()
        self.onListStateChanged = Event.Event()
        self.onGroupToggled = Event.Event()

    def getMainDP(self):
        return self._mainDP

    def onGroupSelected(self, mainGroup, groupData):
        groupName = groupData.groupName
        self._mainDP.toggleGroup(mainGroup, groupName)
        self.onGroupToggled(mainGroup, groupName, not groupData.currentOpened)

    def searchLocalContact(self, searchFilter):
        if self._mainDP.setSearchFilter(searchFilter):
            self._mainDP.refresh()
            self._setSearchInfo()
        else:
            self._updateListState()

    def showContacts(self, onlineMode = True, showVisibleOthers = None, showFriends = True, showEmptyGroups = True, showGroupMenu = True):
        self._mainDP.setOnlineMode(onlineMode)
        self._mainDP.setOthersVisible(showVisibleOthers)
        self._mainDP.setFriendsVisible(showFriends)
        self._mainDP.setShowEmptyGroups(showEmptyGroups)
        self._mainDP.setFriendsGroupMutable(showGroupMenu)
        self._mainDP.buildList()
        self._mainDP.refresh()
        self._updateListState()

    def hasDisplayingContacts(self):
        return self._mainDP.hasDisplayingContacts()

    def _populate(self):
        super(ContactsTreeComponent, self)._populate()
        self._mainDP.setFlashObject(self.as_getMainDPS())
        self._mainDP.addContactsListeners()
        self._mainDP.onTotalStatusChanged += self.__onTotalStatusChanged
        self.as_setInitDataS({'accMinChars': ACCOUNT_NAME_MIN_CHARS_LENGTH,
         'accMaxChars': ACCOUNT_NAME_MAX_CHARS_LENGTH})

    def _dispose(self):
        if self._mainDP:
            self._mainDP.destroy()
            self._mainDP.removeContactsListeners()
            self._mainDP.onTotalStatusChanged -= self.__onTotalStatusChanged
            self._mainDP = None
        super(ContactsTreeComponent, self)._dispose()
        return

    def _updateListState(self):
        isListEmpty = self._mainDP.isEmpty()
        if isListEmpty:
            self.as_updateInfoMessageS(False, makeString(MESSENGER.MESSENGER_CONTACTS_SEARCHUSERS_LISTEMPTYPROMPT_TITLE), makeString(MESSENGER.MESSENGER_CONTACTS_SEARCHUSERS_LISTEMPTYPROMPT_DESCR), False)
        elif self._mainDP.pyLength():
            self.as_updateInfoMessageS(True, '', '', False)
        else:
            self.as_updateInfoMessageS(False, makeString(MESSENGER.MESSENGER_CONTACTS_SEARCHUSERS_NOONLINECONTACTS_TITLE), makeString(MESSENGER.MESSENGER_CONTACTS_SEARCHUSERS_NOONLINECONTACTS_DESCR), False)
        self.onListStateChanged(ContactsTreeComponent.LIST_EMPTY_STATE, isListEmpty)

    def _setSearchInfo(self):
        if self._mainDP.pyLength():
            self.as_updateInfoMessageS(True, '', '', False)
        else:
            self.as_updateInfoMessageS(True, makeString(MESSENGER.MESSENGER_CONTACTS_SEARCHUSERS_SEARCHFAIL_TITLE), makeString(MESSENGER.MESSENGER_CONTACTS_SEARCHUSERS_SEARCHFAIL_DESCR), False)
        self.onListStateChanged(ContactsTreeComponent.LIST_EMPTY_STATE, False)

    def __onTotalStatusChanged(self):
        self._updateListState()
