# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/gui/Scaleform/data/contacts_cm_handlers.py
from gui.Scaleform.daapi.view.lobby.user_cm_handlers import BaseUserCMHandler
from gui.Scaleform.framework.entities.EventSystemEntity import EventSystemEntity
from gui.Scaleform.framework.managers.context_menu import AbstractContextMenuCollectEventsHandler
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.MESSENGER import MESSENGER
from gui.shared import events, EVENT_BUS_SCOPE
from gui.shared.system_factory import registerLobbyContexMenuHandler
from gui.shared.system_factory import collectLobbyContexMenuHandler
from messenger import normalizeGroupId
from messenger.m_constants import USER_TAG

class CONTACTS_ACTION_ID(object):
    EDIT_GROUP = 'editGroup'
    REMOVE_GROUP = 'removeGroup'
    REMOVE_FROM_GROUP = 'removeFromGroup'
    CREATE_CONTACT_NOTE = 'createContactNote'
    EDIT_CONTACT_NOTE = 'editContactNote'
    REMOVE_CONTACT_NOTE = 'removeContactNote'
    REJECT_FRIENDSHIP = 'rejectFriendship'


def editGroup(cm):
    cm.fireEvent(events.ContactsEvent(events.ContactsEvent.EDIT_GROUP, ctx={'targetGroupName': cm.targetGroupName}), scope=EVENT_BUS_SCOPE.LOBBY)


def removeGroup(cm):
    cm.fireEvent(events.ContactsEvent(events.ContactsEvent.REMOVE_GROUP, ctx={'targetGroupName': cm.targetGroupName}), scope=EVENT_BUS_SCOPE.LOBBY)


registerLobbyContexMenuHandler(CONTACTS_ACTION_ID.EDIT_GROUP, editGroup)
registerLobbyContexMenuHandler(CONTACTS_ACTION_ID.REMOVE_GROUP, removeGroup)

class SimpleContactsCMHandler(AbstractContextMenuCollectEventsHandler, EventSystemEntity):

    def _getContexMenuHandler(self):
        return collectLobbyContexMenuHandler

    def _generateOptions(self, ctx=None):
        return [self._makeItem(CONTACTS_ACTION_ID.EDIT_GROUP, MESSENGER.MESSENGER_CONTACTS_CONTEXTMENU_EDITGROUP), self._makeItem(CONTACTS_ACTION_ID.REMOVE_GROUP, MESSENGER.MESSENGER_CONTACTS_CONTEXTMENU_REMOVEGROUP)]

    def _initFlashValues(self, ctx):
        self.targetGroupName = normalizeGroupId(ctx.targetGroupName)

    def _clearFlashValues(self):
        self.targetGroupName = None
        return


def createContactNote(cm):
    cm.fireEvent(events.ContactsEvent(events.ContactsEvent.CREATE_CONTACT_NOTE, ctx={'databaseID': cm.databaseID,
     'userName': cm.userName}), scope=EVENT_BUS_SCOPE.LOBBY)


def editContactNote(cm):
    cm.fireEvent(events.ContactsEvent(events.ContactsEvent.EDIT_CONTACT_NOTE, ctx={'databaseID': cm.databaseID,
     'userName': cm.userName}), scope=EVENT_BUS_SCOPE.LOBBY)


def removeContactNote(cm):
    if cm.proto.contacts.isNoteSupported():
        cm.proto.contacts.removeNote(cm.databaseID)


def removeFromGroup(cm):
    cm.proto.contacts.moveFriendToGroup(cm.databaseID, None, cm.targetGroupName)
    return


def rejectFriendship(cm):
    cm.proto.contacts.cancelFriendship(cm.databaseID)


registerLobbyContexMenuHandler(CONTACTS_ACTION_ID.CREATE_CONTACT_NOTE, createContactNote)
registerLobbyContexMenuHandler(CONTACTS_ACTION_ID.EDIT_CONTACT_NOTE, editContactNote)
registerLobbyContexMenuHandler(CONTACTS_ACTION_ID.REMOVE_CONTACT_NOTE, removeContactNote)
registerLobbyContexMenuHandler(CONTACTS_ACTION_ID.REMOVE_FROM_GROUP, removeFromGroup)
registerLobbyContexMenuHandler(CONTACTS_ACTION_ID.REJECT_FRIENDSHIP, rejectFriendship)

class PlayerContactsCMHandler(BaseUserCMHandler):

    def _initFlashValues(self, ctx):
        super(PlayerContactsCMHandler, self)._initFlashValues(ctx)
        self.targetGroupName = normalizeGroupId(ctx.targetGroupName)
        self.showUserNotes = getattr(ctx, 'showUserNotes', True)

    def _clearFlashValues(self):
        super(PlayerContactsCMHandler, self)._clearFlashValues()
        self.targetGroupName = None
        return

    def _addRejectFriendshipInfo(self, option, userCMInfo):
        if not userCMInfo.isFriend:
            if self.proto.contacts.isBidiFriendshipSupported():
                if userCMInfo.getTags() and USER_TAG.SUB_PENDING_IN in userCMInfo.getTags():
                    option.append(self._makeItem(CONTACTS_ACTION_ID.REJECT_FRIENDSHIP, MENU.contextmenu(CONTACTS_ACTION_ID.REJECT_FRIENDSHIP)))
        return option

    def _addContactsNoteInfo(self, options, userCMInfo):
        if self.showUserNotes and self.proto.contacts.isNoteSupported():
            userNote = userCMInfo.getNote()
            if userNote:
                options.extend([self._makeItem(CONTACTS_ACTION_ID.EDIT_CONTACT_NOTE, MENU.contextmenu(CONTACTS_ACTION_ID.EDIT_CONTACT_NOTE)), self._makeItem(CONTACTS_ACTION_ID.REMOVE_CONTACT_NOTE, MENU.contextmenu(CONTACTS_ACTION_ID.REMOVE_CONTACT_NOTE))])
            else:
                options.append(self._makeItem(CONTACTS_ACTION_ID.CREATE_CONTACT_NOTE, MENU.contextmenu(CONTACTS_ACTION_ID.CREATE_CONTACT_NOTE)))
        return options

    def _addRemoveFromGroupInfo(self, options, isIgnored):
        if self.proto.contacts.isGroupSupported():
            if self.targetGroupName:
                options.append(self._makeItem(CONTACTS_ACTION_ID.REMOVE_FROM_GROUP, MESSENGER.MESSENGER_CONTACTS_CONTEXTMENU_REMOVEFROMGROUP))
        return options
