# Embedded file name: scripts/client/messenger/gui/Scaleform/view/ContactsListPopover.py
from debug_utils import LOG_DEBUG, LOG_WARNING
from gui.Scaleform.genConsts.CONTACTS_ALIASES import CONTACTS_ALIASES
from helpers.i18n import makeString
from gui.Scaleform.locale.WAITING import WAITING
from messenger.gui.Scaleform.meta.ContactsListPopoverMeta import ContactsListPopoverMeta
from messenger.gui.Scaleform.view.ContactsCMListener import ContactsCMListener
from messenger.m_constants import PROTO_TYPE
from messenger.proto import proto_getter
from gui.LobbyContext import g_lobbyContext
from messenger.proto.events import g_messengerEvents
from account_helpers.settings_core.SettingsCore import g_settingsCore
from account_helpers.AccountSettings import AccountSettings, CONTACTS
from messenger.storage import storage_getter

class ContactsListPopover(ContactsListPopoverMeta, ContactsCMListener):

    def __init__(self, ctx = None):
        super(ContactsListPopover, self).__init__(ctx)

    @proto_getter(PROTO_TYPE.MIGRATION)
    def proto(self):
        return None

    @storage_getter('users')
    def usersStorage(self):
        return None

    @property
    def pyTree(self):
        tree = None
        if CONTACTS_ALIASES.CONTACTS_TREE in self.components:
            tree = self.components[CONTACTS_ALIASES.CONTACTS_TREE]
        return tree

    def changeGroup(self, contactDbID, contactName, groupData):
        contactDbID = long(contactDbID)
        targetGroup = groupData.targetGroup
        excludeGroup = groupData.excludeGroup
        targetParentGroup = groupData.targetParentGroup
        if targetGroup == CONTACTS_ALIASES.GROUP_FRIENDS_CATEGORY_ID or targetParentGroup == CONTACTS_ALIASES.GROUP_FRIENDS_CATEGORY_ID:
            if excludeGroup in CONTACTS_ALIASES.CAN_MOVE_TO_FRIENDS_GROUPS_IDS:
                self.__moveToFriendProcess(contactDbID, contactName, targetGroup)
            elif targetGroup != excludeGroup:
                self.__moveToGroupProcess(contactDbID, targetGroup, excludeGroup)
            else:
                LOG_WARNING('Action can not be resolved', contactDbID, targetGroup, excludeGroup, targetParentGroup)
        elif targetGroup == CONTACTS_ALIASES.IGNORED_GROUP_RESERVED_ID:
            if excludeGroup != CONTACTS_ALIASES.IGNORED_GROUP_RESERVED_ID:
                self.addToIgnored(contactDbID, contactName)
        else:
            LOG_WARNING('Action can not be resolved', contactDbID, targetGroup, excludeGroup, targetParentGroup)

    def copyIntoGroup(self, dbID, groupData):
        targetGroup = groupData.targetGroup
        excludeGroup = groupData.excludeGroup
        excludeParentGroup = groupData.excludeParentGroup
        targetParentGroup = groupData.targetParentGroup
        if (targetGroup == CONTACTS_ALIASES.GROUP_FRIENDS_CATEGORY_ID or targetParentGroup == CONTACTS_ALIASES.GROUP_FRIENDS_CATEGORY_ID) and (excludeGroup == CONTACTS_ALIASES.GROUP_FRIENDS_CATEGORY_ID or excludeParentGroup == CONTACTS_ALIASES.GROUP_FRIENDS_CATEGORY_ID):
            if targetGroup != excludeGroup:
                self.__moveToGroupProcess(dbID, targetGroup, None)
        return

    def _onRegisterFlashComponent(self, viewPy, alias):
        super(ContactsListPopover, self)._onRegisterFlashComponent(viewPy, alias)
        if alias == CONTACTS_ALIASES.CONTACTS_TREE:
            tree = self.pyTree
            if tree:
                g_messengerEvents.users.onEmptyGroupsChanged += self.__onEmptyGroupsChanged
                tree.onGroupToggled += self.__onGroupToggled
                settings = g_settingsCore.serverSettings.getSection(CONTACTS, AccountSettings.getFilterDefault(CONTACTS))
                onlineMode = None if settings['showOfflineUsers'] else True
                showOthers = bool(settings['showOthersCategory'])
                tree.showContacts(onlineMode=onlineMode, showVisibleOthers=showOthers, showEmptyGroups=True)
                myDP = tree.getMainDP()
                openedGroups = self.usersStorage.getOpenedGroups()
                for categoryId, groupsSet in openedGroups.iteritems():
                    for groupName in groupsSet:
                        myDP.toggleGroup(categoryId, groupName)

        return

    def onWindowClose(self):
        self.destroy()

    def isEnabledInRoaming(self, uid):
        roaming = g_lobbyContext.getServerSettings().roaming
        return not roaming.isInRoaming() and not roaming.isPlayerInRoaming(uid)

    def addToFriends(self, uid, name):
        LOG_DEBUG('addToFriends: ', uid)
        self.proto.contacts.addFriend(uid, name)

    def addToIgnored(self, uid, name):
        LOG_DEBUG('addToIgnored: ', uid)
        self.proto.contacts.addIgnored(uid, name)

    def as_showWaitingS(self, msg, props):
        return super(ContactsListPopover, self).as_showWaitingS(makeString(WAITING.MESSENGER_SUBSCRIBE), props)

    def as_hideWaitingS(self):
        return super(ContactsListPopover, self).as_hideWaitingS()

    def _populate(self):
        super(ContactsListPopover, self)._populate()
        self.startListenContextMenu()
        g_messengerEvents.onPluginConnected += self.__onPluginConnected
        g_messengerEvents.onPluginDisconnected += self.__onPluginDisconnected
        g_settingsCore.onSettingsChanged += self.__onSettingsChanged
        if self.proto.isConnected():
            self.as_hideWaitingS()
        else:
            self.as_showWaitingS(None, None)
        self.as_setInitInfoS({'isGroupSupported': self.proto.contacts.isGroupSupported()})
        return

    def _dispose(self):
        tree = self.pyTree
        if tree:
            tree.onGroupToggled -= self.__onGroupToggled
        g_settingsCore.onSettingsChanged -= self.__onSettingsChanged
        self.stopListenContextMenu()
        g_messengerEvents.users.onEmptyGroupsChanged -= self.__onEmptyGroupsChanged
        g_messengerEvents.onPluginConnected -= self.__onPluginConnected
        g_messengerEvents.onPluginDisconnected -= self.__onPluginDisconnected
        g_settingsCore.onSettingsChanged -= self.__onSettingsChanged
        super(ContactsListPopover, self)._dispose()

    def _onEditGroup(self, event):
        targetGroupName = event.ctx.get('targetGroupName', None)
        if targetGroupName is not None:
            self.as_editGroupS(targetGroupName)
        return

    def _onRemoveGroup(self, event):
        targetGroupName = event.ctx.get('targetGroupName', None)
        if targetGroupName is not None:
            self.as_removeGroupS(targetGroupName)
        return

    def _onCreateContactNote(self, event):
        userName = event.ctx.get('userName', None)
        databaseID = event.ctx.get('databaseID', None)
        self.as_createContactNoteS(userName, databaseID)
        return

    def _onEditContactNote(self, event):
        userName = event.ctx.get('userName', None)
        databaseID = event.ctx.get('databaseID', None)
        self.as_editContactNoteS(userName, databaseID)
        return

    def __moveToFriendProcess(self, dbID, contactName, targetGroup):
        if targetGroup == CONTACTS_ALIASES.GROUP_FRIENDS_CATEGORY_ID:
            targetGroup = None
        contact = self.usersStorage.getUser(dbID)
        if contact and contact.isFriend():
            if targetGroup:
                self.proto.contacts.moveFriendToGroup(dbID, targetGroup)
        else:
            self.proto.contacts.addFriend(dbID, contactName, targetGroup)
        return

    def __moveToGroupProcess(self, dbID, targetGroupId, excludeGroupId):
        if targetGroupId == CONTACTS_ALIASES.GROUP_FRIENDS_CATEGORY_ID:
            targetGroupId = None
        elif excludeGroupId == CONTACTS_ALIASES.GROUP_FRIENDS_CATEGORY_ID:
            excludeGroupId = None
        self.proto.contacts.moveFriendToGroup(long(dbID), targetGroupId, excludeGroupId)
        return

    def __onPluginConnected(self, protoType):
        if protoType == PROTO_TYPE.MIGRATION:
            self.as_hideWaitingS()

    def __onPluginDisconnected(self, protoType):
        if protoType == PROTO_TYPE.MIGRATION:
            self.as_showWaitingS(None, None)
        return

    def __onGroupToggled(self, categoryID, groupName, isOpened):
        self.usersStorage.setOpenedGroups(categoryID, groupName, isOpened)

    def __onEmptyGroupsChanged(self, include, exclude):
        if include:
            for group in include:
                self.usersStorage.setOpenedGroups(CONTACTS_ALIASES.GROUP_FRIENDS_CATEGORY_ID, group, True)

        if exclude:
            for group in exclude:
                self.usersStorage.setOpenedGroups(CONTACTS_ALIASES.GROUP_FRIENDS_CATEGORY_ID, group, False)

    def __onSettingsChanged(self, diff):
        isChanged, onlineMode, showOthers = False, True, False
        tree = self.pyTree
        if 'showOthersCategory' in diff:
            value = diff['showOthersCategory']
            if tree:
                showOthers = bool(value)
                isChanged = True
        if 'showOfflineUsers' in diff:
            value = diff['showOfflineUsers']
            if tree:
                onlineMode = None if value else True
                isChanged = True
        if isChanged and tree:
            tree.showContacts(onlineMode=onlineMode, showVisibleOthers=showOthers, showEmptyGroups=True)
        return
