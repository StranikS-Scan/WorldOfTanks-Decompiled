# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/gui/Scaleform/view/lobby/ContactsListPopover.py
from account_helpers.AccountSettings import AccountSettings, CONTACTS
from debug_utils import LOG_DEBUG, LOG_WARNING
from gui.Scaleform.genConsts.CONTACTS_ALIASES import CONTACTS_ALIASES
from gui.impl import backport
from gui.impl.gen import R
from helpers import dependency
from messenger.gui.Scaleform.meta.ContactsListPopoverMeta import ContactsListPopoverMeta
from messenger import normalizeGroupId
from messenger.gui.Scaleform.view.lobby.ContactsCMListener import ContactsCMListener
from messenger.m_constants import PROTO_TYPE
from messenger.proto import proto_getter
from messenger.proto.events import g_messengerEvents
from messenger.storage import storage_getter
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.lobby_context import ILobbyContext

class ContactsListPopover(ContactsListPopoverMeta, ContactsCMListener):
    settingsCore = dependency.descriptor(ISettingsCore)
    lobbyContext = dependency.descriptor(ILobbyContext)

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
        targetGroup = normalizeGroupId(groupData.targetGroup)
        excludeGroup = normalizeGroupId(groupData.excludeGroup)
        targetParentGroup = normalizeGroupId(groupData.targetParentGroup)
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
        targetGroup = normalizeGroupId(groupData.targetGroup)
        excludeGroup = normalizeGroupId(groupData.excludeGroup)
        excludeParentGroup = normalizeGroupId(groupData.excludeParentGroup)
        targetParentGroup = normalizeGroupId(groupData.targetParentGroup)
        if (targetGroup == CONTACTS_ALIASES.GROUP_FRIENDS_CATEGORY_ID or targetParentGroup == CONTACTS_ALIASES.GROUP_FRIENDS_CATEGORY_ID) and (excludeGroup == CONTACTS_ALIASES.GROUP_FRIENDS_CATEGORY_ID or excludeParentGroup == CONTACTS_ALIASES.GROUP_FRIENDS_CATEGORY_ID):
            if targetGroup != excludeGroup:
                self.__moveToGroupProcess(dbID, targetGroup, None)
        return

    def getContactListSettings(self):
        settings = self.settingsCore.serverSettings.getSection(CONTACTS, AccountSettings.getFilterDefault(CONTACTS))
        onlineMode = None if settings['showOfflineUsers'] else True
        showOthers = bool(settings['showOthersCategory'])
        return (onlineMode, showOthers)

    def _onRegisterFlashComponent(self, viewPy, alias):
        super(ContactsListPopover, self)._onRegisterFlashComponent(viewPy, alias)
        if alias == CONTACTS_ALIASES.CONTACTS_TREE:
            tree = self.pyTree
            if tree:
                g_messengerEvents.users.onEmptyGroupsChanged += self.__onEmptyGroupsChanged
                tree.onGroupToggled += self.__onGroupToggled
                onlineMode, showOthers = self.getContactListSettings()
                tree.showContacts(onlineMode=onlineMode, showVisibleOthers=showOthers, showEmptyGroups=True)
                myDP = tree.getMainDP()
                openedGroups = self.usersStorage.getOpenedGroups()
                for categoryId, groupsSet in openedGroups.iteritems():
                    for groupName in groupsSet:
                        myDP.toggleGroup(categoryId, groupName)

    def onWindowClose(self):
        self.destroy()

    def isEnabledInRoaming(self, uid):
        roaming = self.lobbyContext.getServerSettings().roaming
        return not roaming.isInRoaming() and not roaming.isPlayerInRoaming(uid)

    def addToFriends(self, uid, name):
        LOG_DEBUG('addToFriends: ', uid)
        self.proto.contacts.addFriend(uid, name)

    def addToIgnored(self, uid, name):
        LOG_DEBUG('addToIgnored: ', uid)
        self.proto.contacts.addIgnored(uid, name)

    def as_showWaitingS(self, msg, props):
        return super(ContactsListPopover, self).as_showWaitingS(backport.text(R.strings.waiting.messenger.subscribe()), props)

    def _populate(self):
        super(ContactsListPopover, self)._populate()
        self.startListenContextMenu()
        g_messengerEvents.onPluginConnected += self.__onPluginConnected
        g_messengerEvents.onPluginDisconnected += self.__onPluginDisconnected
        self.settingsCore.onSettingsChanged += self.__onSettingsChanged
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
        self.settingsCore.onSettingsChanged -= self.__onSettingsChanged
        self.stopListenContextMenu()
        g_messengerEvents.users.onEmptyGroupsChanged -= self.__onEmptyGroupsChanged
        g_messengerEvents.onPluginConnected -= self.__onPluginConnected
        g_messengerEvents.onPluginDisconnected -= self.__onPluginDisconnected
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
        isChanged = False
        onlineMode, showOthers = self.getContactListSettings()
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
