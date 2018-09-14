# Embedded file name: scripts/client/messenger/gui/Scaleform/data/contacts_cm_handlers.py
from gui.shared import events, EVENT_BUS_SCOPE
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.framework.entities.EventSystemEntity import EventSystemEntity
from gui.Scaleform.daapi.view.lobby.user_cm_handlers import BaseUserCMHandler
from gui.Scaleform.managers.context_menu.AbstractContextMenuHandler import AbstractContextMenuHandler
from gui.Scaleform.locale.MESSENGER import MESSENGER
from messenger.m_constants import USER_TAG

class CONTACTS_ACTION_ID(object):
    EDIT_GROUP = 'editGroup'
    REMOVE_GROUP = 'removeGroup'
    REMOVE_FROM_GROUP = 'removeFromGroup'
    CREATE_CONTACT_NOTE = 'createContactNote'
    EDIT_CONTACT_NOTE = 'editContactNote'
    REMOVE_CONTACT_NOTE = 'removeContactNote'
    REJECT_FRIENDSHIP = 'rejectFriendship'


class SimpleContactsCMHandler(AbstractContextMenuHandler, EventSystemEntity):

    def __init__(self, cmProxy, ctx = None):
        super(SimpleContactsCMHandler, self).__init__(cmProxy, ctx, {CONTACTS_ACTION_ID.EDIT_GROUP: 'editGroup',
         CONTACTS_ACTION_ID.REMOVE_GROUP: 'removeGroup'})

    def editGroup(self):
        self.fireEvent(events.ContactsEvent(events.ContactsEvent.EDIT_GROUP, ctx={'targetGroupName': self.targetGroupName}), scope=EVENT_BUS_SCOPE.LOBBY)

    def removeGroup(self):
        self.fireEvent(events.ContactsEvent(events.ContactsEvent.REMOVE_GROUP, ctx={'targetGroupName': self.targetGroupName}), scope=EVENT_BUS_SCOPE.LOBBY)

    def _generateOptions(self, ctx = None):
        return [self._makeItem(CONTACTS_ACTION_ID.EDIT_GROUP, MESSENGER.MESSENGER_CONTACTS_CONTEXTMENU_EDITGROUP), self._makeItem(CONTACTS_ACTION_ID.REMOVE_GROUP, MESSENGER.MESSENGER_CONTACTS_CONTEXTMENU_REMOVEGROUP)]

    def _initFlashValues(self, ctx):
        self.targetGroupName = ctx.targetGroupName

    def _clearFlashValues(self):
        self.targetGroupName = None
        return


class PlayerContactsCMHandler(BaseUserCMHandler):

    def __init__(self, cmProxy, ctx = None):
        super(PlayerContactsCMHandler, self).__init__(cmProxy, ctx)

    def createContactNote(self):
        self.fireEvent(events.ContactsEvent(events.ContactsEvent.CREATE_CONTACT_NOTE, ctx={'databaseID': self.databaseID,
         'userName': self.userName}), scope=EVENT_BUS_SCOPE.LOBBY)

    def editContactNote(self):
        self.fireEvent(events.ContactsEvent(events.ContactsEvent.EDIT_CONTACT_NOTE, ctx={'databaseID': self.databaseID,
         'userName': self.userName}), scope=EVENT_BUS_SCOPE.LOBBY)

    def removeContactNote(self):
        if self.proto.contacts.isNoteSupported():
            self.proto.contacts.removeNote(self.databaseID)

    def removeFromGroup(self):
        self.proto.contacts.moveFriendToGroup(self.databaseID, None, self.targetGroupName)
        return

    def rejectFriendship(self):
        self.proto.contacts.cancelFriendship(self.databaseID)

    def _getHandlers(self):
        handlers = super(PlayerContactsCMHandler, self)._getHandlers()
        handlers.update({CONTACTS_ACTION_ID.CREATE_CONTACT_NOTE: 'createContactNote',
         CONTACTS_ACTION_ID.EDIT_CONTACT_NOTE: 'editContactNote',
         CONTACTS_ACTION_ID.REMOVE_CONTACT_NOTE: 'removeContactNote',
         CONTACTS_ACTION_ID.REMOVE_FROM_GROUP: 'removeFromGroup',
         CONTACTS_ACTION_ID.REJECT_FRIENDSHIP: 'rejectFriendship'})
        return handlers

    def _initFlashValues(self, ctx):
        super(PlayerContactsCMHandler, self)._initFlashValues(ctx)
        self.targetGroupName = ctx.targetGroupName

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
        if self.proto.contacts.isNoteSupported():
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
