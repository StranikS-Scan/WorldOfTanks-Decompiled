# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/proto/xmpp/messages/muc.py
from gui.shared import utils
from messenger import g_settings
from messenger.m_constants import CLIENT_ACTION_ID, CLIENT_ERROR_ID
from messenger.proto.events import g_messengerEvents
from messenger.proto.shared_errors import ClientActionError
from messenger.proto.xmpp import jid as jid_entity, entities, errors
from messenger.proto.xmpp.errors import ClientChannelError
from messenger.proto.xmpp.extensions import chat as chat_ext
from messenger.proto.xmpp.extensions import disco
from messenger.proto.xmpp.gloox_constants import IQ_TYPE, PRESENCE, ERROR_TYPE, MESSAGE_TYPE
from messenger.proto.xmpp.gloox_wrapper import ClientHolder
from messenger.proto.xmpp.log_output import g_logOutput, CLIENT_LOG_AREA as _LOG
from messenger.proto.xmpp.messages.provider import ChatProvider
from messenger.proto.xmpp.xmpp_constants import MUC_STATUS, CHANNEL_ERROR_ID

class ENTRY_STEP(object):
    UNDEFINED = 0
    SEND_PRESENCE = 1
    SET_DATA_FORM = 2
    GET_DISCO_INFO = 3
    PASSWORD_REQUIRED = 4


class ACTION_RESULT(object):
    DO_NOTHING = 0
    ADD_TO_STORAGE = 1
    REMOVE_FROM_STORAGE = 2
    SHOW_ROOM = 4


class _RoomAction(ClientHolder):
    __slots__ = ('_room', '_iqID', '_step', '_result')

    def __init__(self, room, initResult=ACTION_RESULT.DO_NOTHING):
        super(_RoomAction, self).__init__()
        self._room = room
        self._iqID = ''
        self._step = ENTRY_STEP.UNDEFINED
        self._result = initResult

    def clear(self, full=True):
        if self._room is not None:
            if full:
                self._room.clear()
            self._room = None
        self._iqID = ''
        self._step = ENTRY_STEP.UNDEFINED
        return

    def getRoom(self):
        return self._room

    def getRoomJID(self):
        return self._room.getID()

    def getRoomName(self):
        return self._room.getName()

    def getStep(self):
        return self._step

    def getResult(self):
        return self._result

    def isRunning(self):
        return self._step != ENTRY_STEP.UNDEFINED

    def isUserAction(self):
        return True

    def validate(self, *args, **kwargs):
        raise NotImplementedError

    def start(self):
        assert self._room is not None, 'Room must be defined'
        assert self._step == ENTRY_STEP.UNDEFINED
        self._doStart()
        return

    def setPresence(self, jid, dbID, nickname, presence, mucInfo):
        result = False
        if self._step == ENTRY_STEP.UNDEFINED:
            return result
        else:
            if jid.getBareJID() == self._room.getID():
                result = True
                if presence in PRESENCE.OFFLINE:
                    self._room.removeMember(jid)
                    if jid == self._getUserJID():
                        self._leave(mucInfo)
                else:
                    if not dbID and mucInfo is not None and MUC_STATUS.SELF_PRESENCE in mucInfo.statuses:
                        dbID = utils.getPlayerDatabaseID()
                    self._room.addMember(entities.XMPPMUCOccupant(jid, nickname, dbID, presence, mucInfo))
                    if jid == self._getUserJID():
                        self._join(mucInfo)
            return result

    def setPresenceError(self, jid, pyGlooxTag):
        result = False
        if jid.getBareJID() == self._room.getID():
            result = True
            if jid == self._getUserJID():
                self._setPresenceError(pyGlooxTag)
        return result

    def setPassword(self, password):
        result = False
        if self._step == ENTRY_STEP.PASSWORD_REQUIRED:
            result = True
            self._room.setPassword(password)
            self._sendPresence(chat_ext.MUCEntryQuery(self._getUserJID()))
        return result

    def setIQ(self, iqID, iqType, tag):
        result = False
        if self._step == ENTRY_STEP.UNDEFINED:
            return result
        if iqID == self._iqID:
            result = True
            if iqType == IQ_TYPE.RESULT:
                self._setIQResult(tag)
            elif iqType == IQ_TYPE.ERROR:
                self._setIQError(tag)
        return result

    def _doStart(self):
        raise NotImplementedError

    def _getActionID(self):
        raise NotImplementedError

    def _getUserJID(self):
        jid = jid_entity.JID(self._room.getID())
        jid.setResource(utils.getPlayerName())
        return jid

    def _sendIQ(self, query):
        self._iqID = self.client().sendIQ(query)

    def _sendPresence(self, presence):
        self.client().sendMUCPresence(presence, self._room.getPassword())

    def _remove(self):
        self._step = ENTRY_STEP.UNDEFINED
        self._result = ACTION_RESULT.REMOVE_FROM_STORAGE

    def _join(self, mucInfo):
        pass

    def _leave(self, mucInfo):
        pass

    def _setPresenceError(self, tag):
        error = errors.createServerActionPresenceError(self._getActionID(), tag)
        if error is not None:
            if error.getErrorType() == ERROR_TYPE.AUTH and error.getCondition() == 'not-authorized' and self._step != ENTRY_STEP.PASSWORD_REQUIRED:
                self._step = ENTRY_STEP.PASSWORD_REQUIRED
                g_messengerEvents.channels.onConnectingToSecureChannel(self._room)
            else:
                g_messengerEvents.onErrorReceived(error)
                self._remove()
        else:
            self._remove()
        return

    def _setIQResult(self, tag):
        pass

    def _setIQError(self, tag):
        error = errors.createServerActionIQError(self._getActionID(), tag)
        if error is not None:
            g_messengerEvents.onErrorReceived(error)
        self._remove()
        return


class CreateAction(_RoomAction):

    def __init__(self, roomJID, roomName, password='', initResult=ACTION_RESULT.DO_NOTHING):
        super(CreateAction, self).__init__(entities.XMPPMucChannelEntity(roomJID, roomName, password=password), initResult=initResult)

    def _doStart(self):
        self._step = ENTRY_STEP.SEND_PRESENCE
        self._sendPresence(chat_ext.MUCEntryQuery(self._getUserJID()))

    def _getActionID(self):
        return CLIENT_ACTION_ID.CREATE_USER_ROOM

    def _join(self, info):
        if info is not None:
            statuses = info.statuses
        else:
            statuses = ()
        if MUC_STATUS.SELF_PRESENCE in statuses and MUC_STATUS.CREATE_ROOM in statuses:
            self._step = ENTRY_STEP.SET_DATA_FORM
            self._sendIQ(chat_ext.UserRoomConfigurationFormSet(self._room.getID(), self._room.getName(), self._room.getPassword()))
        else:
            g_messengerEvents.onErrorReceived(ClientActionError(CLIENT_ACTION_ID.CREATE_USER_ROOM, CLIENT_ERROR_ID.GENERIC))
            self._result = ACTION_RESULT.DO_NOTHING
            self._sendPresence(chat_ext.MUCLeaveQuery(self._getUserJID()))
        return

    def _leave(self, resource):
        self.clear()

    def _setIQResult(self, tag):
        self._step = ENTRY_STEP.UNDEFINED
        self._result |= ACTION_RESULT.ADD_TO_STORAGE

    def _setIQError(self, tag):
        if self._step == ENTRY_STEP.SET_DATA_FORM:
            self._sendPresence(chat_ext.MUCLeaveQuery(self._getUserJID()))
        error = errors.createServerUserRoomCreationIQError(tag, self._room.getName())
        if error is not None:
            g_messengerEvents.onErrorReceived(error)
        self._remove()
        return


class JoinAction(_RoomAction):

    def _doStart(self):
        self._step = ENTRY_STEP.GET_DISCO_INFO
        self._sendIQ(disco.DiscoInfoQuery(self._room.getID()))

    def _getActionID(self):
        return CLIENT_ACTION_ID.JOIN_USER_ROOM

    def _join(self, info):
        self._step = ENTRY_STEP.UNDEFINED
        self._result |= ACTION_RESULT.ADD_TO_STORAGE

    def _leave(self, resource):
        self._remove()

    def _setIQResult(self, tag):
        if self._step == ENTRY_STEP.GET_DISCO_INFO:
            identity, features = disco.DiscoInfoHandler().handleTag(tag)
            if identity is None or identity.category != 'conference':
                g_logOutput.warning(_LOG.MESSAGE, 'Room info is not found', tag.getXml())
                self.clear()
                return
            self._room.setName(identity.name)
            self._step = ENTRY_STEP.SEND_PRESENCE
            self._sendPresence(chat_ext.MUCEntryQuery(self._getUserJID()))
        return


class LeaveAction(_RoomAction):

    def _doStart(self):
        self._step = ENTRY_STEP.SEND_PRESENCE
        self._sendPresence(chat_ext.MUCLeaveQuery(self._getUserJID()))

    def _getActionID(self):
        return CLIENT_ACTION_ID.LEAVE_USER_ROOM

    def _leave(self, resource):
        self._remove()

    def _join(self, resource):
        self.clear()


class MUCProvider(ChatProvider):
    __slots__ = ('__actions',)

    def __init__(self):
        super(MUCProvider, self).__init__()
        self.__actions = {}

    def clear(self):
        while self.__actions:
            _, action = self.__actions.popitem()
            action.clear()

        super(MUCProvider, self).clear()

    def release(self):
        if not g_settings.server.XMPP.isMucServiceAllowed():
            return
        for channel in self._getChannelsIterator(MESSAGE_TYPE.GROUPCHAT):
            self.joinToRoom(channel.getID(), channel.getPassword(), ACTION_RESULT.DO_NOTHING)

        super(MUCProvider, self).release()

    def suspend(self):
        for channel in self._getChannelsIterator(MESSAGE_TYPE.GROUPCHAT):
            channel.setJoined(False)
            channel.clearMembers()

        super(MUCProvider, self).suspend()
        self.clear()

    def createRoom(self, name, password='', initResult=ACTION_RESULT.SHOW_ROOM):
        roomJID = jid_entity.makeUserRoomJID()
        if not roomJID:
            return (False, ClientActionError(CLIENT_ACTION_ID.CREATE_USER_ROOM, CLIENT_ERROR_ID.NOT_SUPPORTED))
        else:
            exists = self.getChannelByName(name)
            if exists is not None:
                return (False, ClientChannelError(CHANNEL_ERROR_ID.NAME_ALREADY_EXISTS, name))
            if roomJID not in self.__actions:
                action = CreateAction(roomJID, name, password, initResult)
                self.__actions[roomJID] = action
                action.start()
            else:
                return (False, ClientActionError(CLIENT_ACTION_ID.CREATE_USER_ROOM, CLIENT_ERROR_ID.LOCKED))
            return (True, None)

    def joinToRoom(self, roomJID, password='', initResult=ACTION_RESULT.SHOW_ROOM):
        if not g_settings.server.XMPP.isMucServiceAllowed(roomJID.getDomain()):
            return (False, ClientActionError(CLIENT_ACTION_ID.JOIN_USER_ROOM, CLIENT_ERROR_ID.NOT_SUPPORTED))
        else:
            entry, exists = self._searchChannel(roomJID)
            if exists is not None:
                if exists.isJoined():
                    g_messengerEvents.channels.onPlayerEnterChannelByAction(exists)
                    return (True, None)
                entry = exists
            if roomJID not in self.__actions:
                if password:
                    entry.setPassword(password)
                action = JoinAction(entry, initResult)
                self.__actions[roomJID] = action
                action.start()
            else:
                action = self.__actions[roomJID]
                if not password or not action.setPassword(password):
                    return (False, ClientActionError(CLIENT_ACTION_ID.JOIN_USER_ROOM, CLIENT_ERROR_ID.LOCKED))
            return (True, None)

    def leaveFromRoom(self, roomJID):
        _, exists = self._searchChannel(roomJID)
        if exists is None:
            return (False, ClientActionError(CLIENT_ACTION_ID.LEAVE_USER_ROOM, CLIENT_ERROR_ID.GENERIC))
        elif not exists.isJoined():
            self._removeChannel(exists)
            return (True, None)
        else:
            entry = self.__actions.pop(roomJID, None)
            if entry is not None:
                entry.clear()
            action = LeaveAction(exists)
            self.__actions[roomJID] = action
            action.start()
            return

    def restore(self, jid, state):
        result = False
        if not g_settings.server.XMPP.isMucServiceAllowed():
            return result
        else:
            created, exists = self._searchChannel(jid_entity.JID(jid))
            if exists is None:
                result = created.setPersistentState(state)
                if result:
                    isConnected = self.client().isConnected()
                    if self._addChannel(created, isJoined=isConnected) and isConnected:
                        self.joinToRoom(created.getID(), created.getPassword(), ACTION_RESULT.DO_NOTHING)
            return result

    def addMessage(self, jid, message):
        accountDBID = message.accountDBID
        if accountDBID:
            contact = self.usersStorage.getUser(accountDBID)
            if contact is not None and contact.isIgnored():
                return
        super(MUCProvider, self).addMessage(jid, message)
        return

    def handlePresence(self, jid, resource):
        result = False
        if g_settings.server.XMPP.isMucServiceAllowed(jid.getDomain()):
            presence = resource.presence
            mucInfo = resource.getMucInfo()
            dbID = resource.getWgDatabaseID()
            nickname = resource.getWgNickname() or jid.getResource()
            for action in self.__actions.itervalues():
                result |= action.setPresence(jid, dbID, nickname, presence, mucInfo)

            if not result:
                if presence in PRESENCE.OFFLINE:
                    self.__removeMember(jid, dbID, nickname)
                else:
                    self.__addMember(jid, dbID, nickname, presence, mucInfo)
            self.__filterActions()
        return result

    def handlePresenceError(self, jid, pyGlooxTag):
        result = False
        for action in self.__actions.itervalues():
            result |= action.setPresenceError(jid, pyGlooxTag)

        self.__filterActions()
        return result

    def handleIQ(self, iqID, iqType, pyGlooxTag):
        result = False
        for action in self.__actions.itervalues():
            result |= action.setIQ(iqID, iqType, pyGlooxTag)

        self.__filterActions()
        return result

    def _searchChannel(self, jid, name=''):
        created = entities.XMPPMucChannelEntity(jid, name)
        exists = self.channelsStorage.getChannel(created)
        return (created, exists)

    def __addMember(self, jid, dbID, nickname, presence, mucInfo):
        _, found = self._searchChannel(jid.getBareJID())
        if found is not None:
            found.addMember(entities.XMPPMUCOccupant(jid, nickname, dbID, presence, mucInfo))
        return

    def __removeMember(self, jid, dbID, nickname):
        _, found = self._searchChannel(jid.getBareJID())
        if dbID:
            leave = utils.getPlayerDatabaseID() == dbID
        else:
            leave = utils.getPlayerName() == nickname
        if leave:
            self._removeChannel(found)
        else:
            found.removeMember(jid)

    def __filterActions(self):
        for jid, action in self.__actions.items()[:]:
            if action.isRunning():
                continue
            self.__actions.pop(jid)
            room = action.getRoom()
            result = action.getResult()
            if room is None and result != ACTION_RESULT.DO_NOTHING:
                g_logOutput.error(_LOG.MESSAGE, 'Action is failed', jid)
                continue
            if result & ACTION_RESULT.ADD_TO_STORAGE > 0:
                self._addChannel(room, byAction=result & ACTION_RESULT.SHOW_ROOM > 0)
            elif result & ACTION_RESULT.REMOVE_FROM_STORAGE > 0:
                self._removeChannel(room)
            action.clear(full=False)

        return
