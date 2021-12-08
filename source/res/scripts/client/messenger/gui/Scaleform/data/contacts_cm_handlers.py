# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/gui/Scaleform/data/contacts_cm_handlers.py
from gifts.gifts_common import GiftEventID
from gui.Scaleform.daapi.view.lobby.user_cm_handlers import BaseUserCMHandler
from gui.Scaleform.framework.entities.EventSystemEntity import EventSystemEntity
from gui.Scaleform.framework.managers.context_menu import AbstractContextMenuHandler
from gui.Scaleform.genConsts.CONTACTS_ACTION_CONSTS import CONTACTS_ACTION_CONSTS
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.MESSENGER import MESSENGER
from gui.shared import events, EVENT_BUS_SCOPE
from helpers import dependency
from messenger.m_constants import USER_TAG
from new_year.ny_navigation_helper import externalSwitchToGiftSystemView
from skeletons.gui.game_control import IGiftSystemController
from skeletons.new_year import INewYearController
from uilogging.ny.loggers import NyGiftSystemContextMenuLogger

class SimpleContactsCMHandler(AbstractContextMenuHandler, EventSystemEntity):

    def __init__(self, cmProxy, ctx=None):
        super(SimpleContactsCMHandler, self).__init__(cmProxy, ctx, {CONTACTS_ACTION_CONSTS.EDIT_GROUP: 'editGroup',
         CONTACTS_ACTION_CONSTS.REMOVE_GROUP: 'removeGroup'})

    def editGroup(self):
        self.fireEvent(events.ContactsEvent(events.ContactsEvent.EDIT_GROUP, ctx={'targetGroupName': self.targetGroupName}), scope=EVENT_BUS_SCOPE.LOBBY)

    def removeGroup(self):
        self.fireEvent(events.ContactsEvent(events.ContactsEvent.REMOVE_GROUP, ctx={'targetGroupName': self.targetGroupName}), scope=EVENT_BUS_SCOPE.LOBBY)

    def _generateOptions(self, ctx=None):
        return [self._makeItem(CONTACTS_ACTION_CONSTS.EDIT_GROUP, MESSENGER.MESSENGER_CONTACTS_CONTEXTMENU_EDITGROUP), self._makeItem(CONTACTS_ACTION_CONSTS.REMOVE_GROUP, MESSENGER.MESSENGER_CONTACTS_CONTEXTMENU_REMOVEGROUP)]

    def _initFlashValues(self, ctx):
        self.targetGroupName = ctx.targetGroupName

    def _clearFlashValues(self):
        self.targetGroupName = None
        return


class PlayerContactsCMHandler(BaseUserCMHandler):
    __giftsController = dependency.descriptor(IGiftSystemController)
    __nyController = dependency.descriptor(INewYearController)

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

    def sendGift(self):
        externalSwitchToGiftSystemView()
        NyGiftSystemContextMenuLogger().logClick()

    def _generateOptions(self, ctx=None):
        options = super(PlayerContactsCMHandler, self)._generateOptions(ctx)
        self._addSendGiftInfo(options, self._getUseCmInfo())
        return options

    def _getHandlers(self):
        handlers = super(PlayerContactsCMHandler, self)._getHandlers()
        handlers.update({CONTACTS_ACTION_CONSTS.CREATE_CONTACT_NOTE: 'createContactNote',
         CONTACTS_ACTION_CONSTS.EDIT_CONTACT_NOTE: 'editContactNote',
         CONTACTS_ACTION_CONSTS.REMOVE_CONTACT_NOTE: 'removeContactNote',
         CONTACTS_ACTION_CONSTS.REMOVE_FROM_GROUP: 'removeFromGroup',
         CONTACTS_ACTION_CONSTS.REJECT_FRIENDSHIP: 'rejectFriendship',
         CONTACTS_ACTION_CONSTS.NY_SEND_GIFT: 'sendGift'})
        return handlers

    def _initFlashValues(self, ctx):
        super(PlayerContactsCMHandler, self)._initFlashValues(ctx)
        self.targetGroupName = ctx.targetGroupName
        self.showUserNotes = getattr(ctx, 'showUserNotes', True)

    def _clearFlashValues(self):
        super(PlayerContactsCMHandler, self)._clearFlashValues()
        self.targetGroupName = None
        return

    def _addRejectFriendshipInfo(self, option, userCMInfo):
        if not userCMInfo.isFriend:
            if self.proto.contacts.isBidiFriendshipSupported():
                if userCMInfo.getTags() and USER_TAG.SUB_PENDING_IN in userCMInfo.getTags():
                    option.append(self._makeItem(CONTACTS_ACTION_CONSTS.REJECT_FRIENDSHIP, MENU.contextmenu(CONTACTS_ACTION_CONSTS.REJECT_FRIENDSHIP)))
        return option

    def _addContactsNoteInfo(self, options, userCMInfo):
        if self.showUserNotes and self.proto.contacts.isNoteSupported():
            userNote = userCMInfo.getNote()
            if userNote:
                options.extend([self._makeItem(CONTACTS_ACTION_CONSTS.EDIT_CONTACT_NOTE, MENU.contextmenu(CONTACTS_ACTION_CONSTS.EDIT_CONTACT_NOTE)), self._makeItem(CONTACTS_ACTION_CONSTS.REMOVE_CONTACT_NOTE, MENU.contextmenu(CONTACTS_ACTION_CONSTS.REMOVE_CONTACT_NOTE))])
            else:
                options.append(self._makeItem(CONTACTS_ACTION_CONSTS.CREATE_CONTACT_NOTE, MENU.contextmenu(CONTACTS_ACTION_CONSTS.CREATE_CONTACT_NOTE)))
        return options

    def _addRemoveFromGroupInfo(self, options, isIgnored):
        if self.proto.contacts.isGroupSupported():
            if self.targetGroupName:
                options.append(self._makeItem(CONTACTS_ACTION_CONSTS.REMOVE_FROM_GROUP, MESSENGER.MESSENGER_CONTACTS_CONTEXTMENU_REMOVEFROMGROUP))
        return options

    def _addSendGiftInfo(self, options, userCMInfo):
        eventHub = self.__giftsController.getEventHub(GiftEventID.NY_HOLIDAYS)
        if self.__nyController.isEnabled() and eventHub and eventHub.getSettings().isEnabled and userCMInfo.isAnySub:
            isEnabled = self.prbEntity is None or not self.prbEntity.isInQueue()
            options.insert(0, self._makeItem(CONTACTS_ACTION_CONSTS.NY_SEND_GIFT, MENU.contextmenu(CONTACTS_ACTION_CONSTS.NY_SEND_GIFT), iconType=CONTACTS_ACTION_CONSTS.NY_SEND_GIFT, linkage='NYContextMenuItemUI', optInitData={'enabled': isEnabled}))
        return options
