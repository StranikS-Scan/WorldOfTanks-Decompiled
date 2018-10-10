# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/proto/migration/contacts.py
from messenger.m_constants import CLIENT_ERROR_ID, CLIENT_ACTION_ID
from messenger.proto.events import g_messengerEvents
from messenger.proto.migration.proxy import MigrationProxy
from messenger.proto.shared_errors import ClientActionError
from messenger_common_chat2 import MESSENGER_ACTION_IDS
from gui.shared.rq_cooldown import REQUEST_SCOPE
from gui.shared.events import CoolDownEvent, coolDownEventParams

class ContactsManagerProxy(MigrationProxy):
    __slots__ = ()

    def isGroupSupported(self):
        return False

    def isNoteSupported(self):
        return False

    def isBidiFriendshipSupported(self):
        return False

    def addFriend(self, dbID, name, group=None):
        raise NotImplementedError

    def approveFriendship(self, dbID):
        raise NotImplementedError

    def removeFriend(self, dbID):
        raise NotImplementedError

    def addIgnored(self, dbID, name):
        raise NotImplementedError

    def addTmpIgnored(self, dbID, name):
        raise NotImplementedError

    def removeIgnored(self, dbID):
        raise NotImplementedError

    def removeTmpIgnored(self, dbID):
        raise NotImplementedError

    def setMuted(self, dbID, name):
        raise NotImplementedError

    def unsetMuted(self, dbID):
        raise NotImplementedError

    def addGroup(self, name):
        raise NotImplementedError

    def renameGroup(self, oldName, newName):
        raise NotImplementedError

    def removeGroup(self, name, isForced=False):
        raise NotImplementedError

    def moveFriendToGroup(self, dbID, add, exclude=None):
        raise NotImplementedError

    def requestFriendship(self, dbID):
        raise NotImplementedError

    def cancelFriendship(self, dbID):
        raise NotImplementedError

    def createPrivateChannel(self, uid, name):
        raise NotImplementedError

    def setNote(self, dbID, note):
        raise NotImplementedError

    def removeNote(self, dbID):
        raise NotImplementedError

    def getUserSearchProcessor(self):
        raise NotImplementedError

    def getUserSearchCooldownInfo(self):
        raise NotImplementedError


def _showClientActionError(actionID, errorID=CLIENT_ERROR_ID.NOT_SUPPORTED):
    g_messengerEvents.onErrorReceived(ClientActionError(actionID, errorID))


class BWContactsManagerProxy(ContactsManagerProxy):
    __slots__ = ()

    def addFriend(self, dbID, name, group=None):
        self._proto.users.addFriend(dbID, name)
        return True

    def removeFriend(self, dbID):
        self._proto.users.removeFriend(dbID)
        return True

    def addIgnored(self, dbID, name):
        self._proto.users.addIgnored(dbID, name)
        return True

    def addTmpIgnored(self, dbID, name):
        _showClientActionError(CLIENT_ACTION_ID.ADD_IGNORED)
        return False

    def removeIgnored(self, dbID):
        self._proto.users.removeIgnored(dbID)
        return True

    def removeTmpIgnored(self, dbID):
        _showClientActionError(CLIENT_ACTION_ID.REMOVE_IGNORED)
        return False

    def setMuted(self, dbID, name):
        self._proto.users.setMuted(dbID, name)
        return True

    def unsetMuted(self, dbID):
        self._proto.users.unsetMuted(dbID)
        return True

    def addGroup(self, name):
        _showClientActionError(CLIENT_ACTION_ID.ADD_GROUP)
        return False

    def renameGroup(self, oldName, newName):
        _showClientActionError(CLIENT_ACTION_ID.CHANGE_GROUP)
        return False

    def removeGroup(self, name, isForced=False):
        _showClientActionError(CLIENT_ACTION_ID.CHANGE_GROUP)
        return False

    def moveFriendToGroup(self, dbID, add, exclude=None):
        _showClientActionError(CLIENT_ACTION_ID.CHANGE_GROUP)
        return False

    def requestFriendship(self, dbID):
        _showClientActionError(CLIENT_ACTION_ID.RQ_FRIENDSHIP)
        return False

    def approveFriendship(self, dbID):
        _showClientActionError(CLIENT_ACTION_ID.APPROVE_FRIENDSHIP)
        return False

    def cancelFriendship(self, dbID):
        _showClientActionError(CLIENT_ACTION_ID.CANCEL_FRIENDSHIP)
        return False

    def createPrivateChannel(self, uid, name):
        self._proto.users.createPrivateChannel(uid, name)
        return True

    def setNote(self, dbID, note):
        _showClientActionError(CLIENT_ACTION_ID.SET_NOTE)
        return False

    def removeNote(self, dbID):
        _showClientActionError(CLIENT_ACTION_ID.REMOVE_NOTE)
        return False

    def getUserSearchProcessor(self):
        from messenger.proto.bw_chat2.search_processor import SearchUsersProcessor
        return SearchUsersProcessor()

    def getUserSearchCooldownInfo(self):
        coolDown = coolDownEventParams(CoolDownEvent.BW_CHAT2, REQUEST_SCOPE.BW_CHAT2, MESSENGER_ACTION_IDS.FIND_USERS_BY_NAME)
        return coolDown


class XMPPContactsManagerProxy(ContactsManagerProxy):
    __slots__ = ()

    def isGroupSupported(self):
        return True

    def isNoteSupported(self):
        return True

    def isBidiFriendshipSupported(self):
        return True

    def addFriend(self, dbID, name, group=None):
        result, error = self._proto.contacts.addFriend(dbID, name, group)
        if not result:
            g_messengerEvents.onErrorReceived(error)
        return result

    def approveFriendship(self, dbID):
        result, error = self._proto.contacts.approveFriendship(dbID)
        if not result:
            g_messengerEvents.onErrorReceived(error)
        return result

    def removeFriend(self, dbID):
        result, error = self._proto.contacts.removeFriend(dbID)
        if not result:
            g_messengerEvents.onErrorReceived(error)
        return result

    def addIgnored(self, dbID, name):
        result, error = self._proto.contacts.addIgnored(dbID, name)
        if not result:
            g_messengerEvents.onErrorReceived(error)
        return result

    def addTmpIgnored(self, dbID, name):
        result, error = self._proto.contacts.addTmpIgnored(dbID, name)
        if not result:
            g_messengerEvents.onErrorReceived(error)
        return result

    def removeIgnored(self, dbID):
        result, error = self._proto.contacts.removeIgnored(dbID)
        if not result:
            g_messengerEvents.onErrorReceived(error)
        return result

    def removeTmpIgnored(self, dbID):
        result, error = self._proto.contacts.removeTmpIgnored(dbID)
        if not result:
            g_messengerEvents.onErrorReceived(error)
        return result

    def setMuted(self, dbID, name):
        result, error = self._proto.contacts.setMuted(dbID, name)
        if not result:
            g_messengerEvents.onErrorReceived(error)
        return result

    def unsetMuted(self, dbID):
        result, error = self._proto.contacts.unsetMuted(dbID)
        if not result:
            g_messengerEvents.onErrorReceived(error)
        return result

    def addGroup(self, name):
        result, error = self._proto.contacts.addGroup(name)
        if not result:
            g_messengerEvents.onErrorReceived(error)
        return result

    def renameGroup(self, oldName, newName):
        result, error = self._proto.contacts.renameGroup(oldName, newName)
        if not result:
            g_messengerEvents.onErrorReceived(error)
        return result

    def removeGroup(self, name, isForced=False):
        result, error = self._proto.contacts.removeGroup(name, isForced)
        if not result:
            g_messengerEvents.onErrorReceived(error)
        return result

    def moveFriendToGroup(self, dbID, add, exclude=None):
        result, error = self._proto.contacts.moveFriendToGroup(dbID, add, exclude)
        if not result:
            g_messengerEvents.onErrorReceived(error)
        return result

    def requestFriendship(self, dbID):
        result, error = self._proto.contacts.requestFriendship(dbID)
        if not result:
            g_messengerEvents.onErrorReceived(error)
        return result

    def cancelFriendship(self, dbID):
        result, error = self._proto.contacts.cancelFriendship(dbID)
        if not result:
            g_messengerEvents.onErrorReceived(error)
        return result

    def createPrivateChannel(self, dbID, name):
        result, _ = self._proto.messages.startChatSession(dbID, name)
        return result

    def setNote(self, dbID, note):
        result, error = self._proto.contacts.setNote(dbID, note)
        if not result:
            g_messengerEvents.onErrorReceived(error)
        return result

    def removeNote(self, dbID):
        result, error = self._proto.contacts.removeNote(dbID)
        if not result:
            g_messengerEvents.onErrorReceived(error)
        return result

    def getUserSearchProcessor(self):
        from messenger.proto.xmpp.xmpp_search_processors import SearchUsersProcessor
        return SearchUsersProcessor()

    def getUserSearchCooldownInfo(self):
        coolDown = coolDownEventParams(CoolDownEvent.XMPP, REQUEST_SCOPE.XMPP, CLIENT_ACTION_ID.FIND_USERS_BY_PREFIX)
        return coolDown
