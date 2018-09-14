# Embedded file name: scripts/client/messenger/proto/xmpp/contacts/__init__.py
from ConnectionManager import connectionManager
from PlayerEvents import g_playerEvents
from constants import IS_IGR_ENABLED
from messenger import g_settings
from messenger.m_constants import PROTO_TYPE, USER_ACTION_ID, CLIENT_ERROR_ID, USER_TAG, CLIENT_ACTION_ID, MESSENGER_SCOPE
from messenger.proto import notations
from messenger.proto.events import g_messengerEvents
from messenger.proto.shared_errors import ChatCoolDownError, ClientActionError, ClientError
from messenger.proto.shared_find_criteria import ProtoFindCriteria
from messenger.proto.xmpp import entities
from messenger.proto.xmpp.XmppCooldownManager import XmppCooldownManager
from messenger.proto.xmpp.contacts import block_tasks, roster_tasks, sub_tasks, note_tasks, sub_helper
from messenger.proto.xmpp.contacts.tasks import ContactTaskQueue, SeqTaskQueue
from messenger.proto.xmpp.decorators import xmpp_query, QUERY_SIGN, local_query
from messenger.proto.xmpp.errors import ClientContactError, ClientIntLimitError
from messenger.proto.xmpp.extensions.shared_queries import PresenceQuery
from messenger.proto.xmpp.find_criteria import ItemsFindCriteria, GroupFindCriteria, RqFriendshipCriteria, MutedOnlyFindCriteria
from messenger.proto.xmpp.gloox_constants import SUBSCRIPTION as _SUB, GLOOX_EVENT as _EVENT, PRESENCE, DISCONNECT_REASON
from messenger.proto.xmpp.gloox_wrapper import ClientEventsHandler, ClientHolder
from messenger.proto.xmpp.jid import makeContactJID, ContactJID
from messenger.proto.xmpp.log_output import g_logOutput, CLIENT_LOG_AREA as _LOG
from messenger.proto.xmpp.xmpp_constants import XMPP_ITEM_TYPE, CONTACT_LIMIT, CONTACT_ERROR_ID, LIMIT_ERROR_ID
from messenger.storage import storage_getter
from predefined_hosts import g_preDefinedHosts
_MAX_TRIES_FAILED_IN_LOBBY = 2
_MAX_TRIES_FAILED_IN_BATTLE = 1

class _UserPresence(ClientHolder):
    __slots__ = ('__scope',)

    def __init__(self):
        super(_UserPresence, self).__init__()
        self.__scope = MESSENGER_SCOPE.UNKNOWN

    def getUserScope(self):
        return self.__scope

    def switch(self, scope = None):
        if scope:
            self.__scope = scope
        self.sendPresence()

    def sendPresence(self, initial = False):
        client = self.client()
        if not client or not client.isConnected():
            return False
        if self.__scope == MESSENGER_SCOPE.BATTLE:
            if initial:
                seq = (PRESENCE.AVAILABLE, PRESENCE.DND)
            else:
                seq = (PRESENCE.DND,)
        elif self.__scope == MESSENGER_SCOPE.LOBBY:
            seq = (PRESENCE.AVAILABLE,)
        else:
            return False
        for presence in seq:
            if not initial and client.getClientPresence() == presence:
                continue
            query = self.__createQuery(presence)
            if IS_IGR_ENABLED:
                from gui.game_control import getIGRCtrl
                ctrl = getIGRCtrl()
                if ctrl:
                    query.setIgrID(ctrl.getRoomType())
            client.sendPresence(query)

        return True

    def addListeners(self):
        g_playerEvents.onIGRTypeChanged += self.__onIGRTypeChanged

    def removeListeners(self):
        g_playerEvents.onIGRTypeChanged -= self.__onIGRTypeChanged

    def __createQuery(self, presence):
        from gui.battle_control.arena_info import getArenaGuiTypeLabel
        query = PresenceQuery(presence)
        item = g_preDefinedHosts.byName(connectionManager.serverUserName)
        if item.url:
            query.setGameServerHost(item.url)
        if self.__scope == MESSENGER_SCOPE.BATTLE and presence == PRESENCE.DND:
            query.setArenaGuiLabel(getArenaGuiTypeLabel())
        return query

    def __onIGRTypeChanged(self, igrID, _):
        if not IS_IGR_ENABLED:
            return
        client = self.client()
        if client and client.isConnected():
            query = self.__createQuery(client.getClientPresence())
            query.setIgrID(igrID)
            client.sendPresence(query)


class _VoipHandler(object):

    @storage_getter('users')
    def usersStorage(self):
        return None

    @storage_getter('playerCtx')
    def playerCtx(self):
        return None

    def addListeners(self):
        events = g_messengerEvents.voip
        events.onChannelEntered += self.__voip_onChannelEntered
        events.onChannelLeft += self.__voip_onChannelLeft

    def removeListeners(self):
        events = g_messengerEvents.voip
        events.onChannelEntered -= self.__voip_onChannelEntered
        events.onChannelLeft -= self.__voip_onChannelLeft

    def __voip_onChannelEntered(self, uri, _):
        if self.playerCtx.getCachedItem('lastVoipUri') != uri:
            self.usersStorage.removeTags({USER_TAG.MUTED}, MutedOnlyFindCriteria())
            g_messengerEvents.users.onUsersListReceived({USER_TAG.MUTED})
        else:
            self.playerCtx.setCachedItem('lastVoipUri', uri)

    def __voip_onChannelLeft(self):
        self.playerCtx.setCachedItem('lastVoipUri', '')
        self.usersStorage.removeTags({USER_TAG.MUTED}, MutedOnlyFindCriteria())
        g_messengerEvents.users.onUsersListReceived({USER_TAG.MUTED})


class ContactsManager(ClientEventsHandler):
    __slots__ = ('__seq', '__tasks', '__cooldown', '__presence', '__voip', '__rqRestrictions')

    def __init__(self):
        super(ContactsManager, self).__init__()
        self.__seq = SeqTaskQueue()
        self.__seq.suspend()
        self.__tasks = ContactTaskQueue([block_tasks.SyncBlockItemTask()])
        self.__cooldown = XmppCooldownManager()
        self.__subsBatch = sub_helper.InboundSubscriptionsBatch()
        self.__subsRestrictions = sub_helper.SubscriptionsRestrictions()
        self.__presence = _UserPresence()
        self.__presence.addListeners()
        self.__voip = _VoipHandler()
        self.__voip.addListeners()
        g_messengerEvents.onPluginConnectFailed += self.__me_onPluginConnectFailed
        self.usersStorage.onRestoredFromCache += self.__us_onRestoredFromCache
        g_settings.onUserPreferencesUpdated += self.__ms_onUserPreferencesUpdated

    @storage_getter('users')
    def usersStorage(self):
        return None

    @storage_getter('playerCtx')
    def playerCtx(self):
        return None

    def isInited(self):
        return self.__seq.isInited()

    def clear(self):
        g_settings.onUserPreferencesUpdated -= self.__ms_onUserPreferencesUpdated
        g_messengerEvents.onPluginConnectFailed -= self.__me_onPluginConnectFailed
        self.usersStorage.onRestoredFromCache -= self.__us_onRestoredFromCache
        self.__presence.removeListeners()
        self.__voip.removeListeners()
        self.__subsBatch.clear()
        super(ContactsManager, self).clear()

    def switch(self, scope):
        self.__presence.switch(scope)

    @notations.contacts(PROTO_TYPE.XMPP, log=False)
    def registerHandlers(self):
        register = self.client().registerHandler
        register(_EVENT.CONNECTED, self.__handleConnected)
        register(_EVENT.DISCONNECTED, self.__handleDisconnected)
        register(_EVENT.IQ, self.__handleIQ)
        register(_EVENT.ROSTER_QUERY, self.__handleRosterQuery)
        register(_EVENT.ROSTER_RESULT, self.__handleRosterResult)
        register(_EVENT.ROSTER_ITEM_SET, self.__handleRosterItemSet)
        register(_EVENT.ROSTER_ITEM_REMOVED, self.__handleRosterItemRemoved)
        register(_EVENT.PRESENCE, self.__handlePresence)
        register(_EVENT.SUBSCRIPTION_REQUEST, self.__handleSubscriptionRequest)

    @notations.contacts(PROTO_TYPE.XMPP, log=False)
    def unregisterHandlers(self):
        unregister = self.client().unregisterHandler
        unregister(_EVENT.CONNECTED, self.__handleConnected)
        unregister(_EVENT.DISCONNECTED, self.__handleDisconnected)
        unregister(_EVENT.IQ, self.__handleIQ)
        unregister(_EVENT.ROSTER_QUERY, self.__handleRosterQuery)
        unregister(_EVENT.ROSTER_RESULT, self.__handleRosterResult)
        unregister(_EVENT.ROSTER_ITEM_SET, self.__handleRosterItemSet)
        unregister(_EVENT.ROSTER_ITEM_REMOVED, self.__handleRosterItemRemoved)
        unregister(_EVENT.PRESENCE, self.__handlePresence)
        unregister(_EVENT.SUBSCRIPTION_REQUEST, self.__handleSubscriptionRequest)
        self.__tasks.clear()

    @xmpp_query(QUERY_SIGN.DATABASE_ID, QUERY_SIGN.ACCOUNT_NAME, QUERY_SIGN.OPT_GROUP_NAME)
    def addFriend(self, dbID, name, group = None):
        error = self.__checkCooldown(CLIENT_ACTION_ID.ADD_FRIEND)
        if error:
            return (False, error)
        else:
            if group:
                if not self.usersStorage.isGroupExists(group):
                    return (False, ClientContactError(CONTACT_ERROR_ID.GROUP_NOT_FOUND, group))
                groups = {group}
            else:
                groups = None
            contact = self.usersStorage.getUser(dbID, PROTO_TYPE.XMPP)
            tasks, itemType = [], XMPP_ITEM_TYPE.EMPTY_ITEM
            if contact:
                if contact.isCurrentPlayer():
                    return (False, ClientActionError(CLIENT_ACTION_ID.ADD_FRIEND, CLIENT_ERROR_ID.GENERIC))
                jid = contact.getJID()
                itemType = contact.getItemType()
                if itemType == XMPP_ITEM_TYPE.ROSTER_ITEM:
                    return (False, ClientContactError(CONTACT_ERROR_ID.ROSTER_ITEM_EXISTS, contact.getFullName()))
                subTo = contact.getSubscription()[0]
            else:
                jid = makeContactJID(dbID)
                subTo = _SUB.OFF
            result, error = self.__subsRestrictions.canAddFriends()
            if not result:
                return (False, error)
            if itemType == XMPP_ITEM_TYPE.BLOCK_ITEM:
                tasks.append(block_tasks.RemoveBlockItemTask(jid, name))
                tasks.append(roster_tasks.AddRosterItemTask(jid, name, groups))
            elif itemType == XMPP_ITEM_TYPE.ROSTER_BLOCK_ITEM:
                tasks.append(block_tasks.RemoveBlockItemTask(jid, name))
                task, exclude = None, set()
                rosterGroups = contact.getItem().getRosterGroups()
                for group in rosterGroups:
                    if self.usersStorage.isGroupEmpty(group):
                        exclude.add(group)

                if groups:
                    if groups != exclude:
                        task = roster_tasks.ChangeRosterItemGroupsTask(jid, name, groups, exclude)
                elif rosterGroups:
                    task = roster_tasks.ChangeRosterItemGroupsTask(jid, name, set(), exclude)
                if task:
                    tasks.append(task)
            elif itemType == XMPP_ITEM_TYPE.SUB_PENDING:
                tasks.append(sub_tasks.ApproveSubscriptionTask(jid, name))
                if groups:
                    tasks.append(roster_tasks.ChangeRosterItemGroupsTask(jid, name, groups))
            else:
                tasks.append(roster_tasks.AddRosterItemTask(jid, name, groups))
            if subTo == _SUB.OFF:
                tasks.append(sub_tasks.AskSubscriptionTask(jid))
            self.__cooldown.process(CLIENT_ACTION_ID.ADD_FRIEND)
            return self.__addTasks(CLIENT_ACTION_ID.ADD_FRIEND, jid, *tasks)

    @xmpp_query(QUERY_SIGN.DATABASE_ID)
    def removeFriend(self, dbID):
        error = self.__checkCooldown(CLIENT_ACTION_ID.REMOVE_FRIEND)
        if error:
            return (False, error)
        contact = self.usersStorage.getUser(dbID, PROTO_TYPE.XMPP)
        if not contact:
            return (False, ClientContactError(CONTACT_ERROR_ID.CONTACT_ITEM_NOT_FOUND))
        if contact.getItemType() != XMPP_ITEM_TYPE.ROSTER_ITEM:
            return (False, ClientContactError(CONTACT_ERROR_ID.ROSTER_ITEM_NOT_FOUND, contact.getFullName()))
        jid = contact.getJID()
        self.__cooldown.process(CLIENT_ACTION_ID.REMOVE_FRIEND)
        tasks = [roster_tasks.RemoveRosterItemTask(jid, contact.getName(), groups=contact.getGroups())]
        if note_tasks.canNoteAutoDelete(contact):
            tasks.append(note_tasks.RemoveNoteTask(jid))
        return self.__addTasks(CLIENT_ACTION_ID.REMOVE_FRIEND, jid, *tasks)

    @xmpp_query(QUERY_SIGN.DATABASE_ID, QUERY_SIGN.OPT_GROUP_NAME, QUERY_SIGN.OPT_GROUP_NAME)
    def moveFriendToGroup(self, dbID, include = None, exclude = None):
        error = self.__checkCooldown(CLIENT_ACTION_ID.CHANGE_GROUP)
        if error:
            return (False, error)
        else:
            contact = self.usersStorage.getUser(dbID, PROTO_TYPE.XMPP)
            if not contact:
                return (False, ClientContactError(CONTACT_ERROR_ID.CONTACT_ITEM_NOT_FOUND))
            if contact.getItemType() != XMPP_ITEM_TYPE.ROSTER_ITEM:
                return (False, ClientContactError(CONTACT_ERROR_ID.ROSTER_ITEM_NOT_FOUND, contact.getFullName()))
            groups = contact.getGroups()
            if include:
                if not self.usersStorage.isGroupExists(include):
                    return (False, ClientContactError(CONTACT_ERROR_ID.GROUP_NOT_FOUND, include))
                groups.add(include)
            if exclude:
                if not self.usersStorage.isGroupExists(exclude):
                    return (False, ClientContactError(CONTACT_ERROR_ID.GROUP_NOT_FOUND, exclude))
                groups.discard(exclude)
            if contact.getGroups() == groups:
                return (True, None)
            jid = contact.getJID()
            self.__cooldown.process(CLIENT_ACTION_ID.CHANGE_GROUP)
            return self.__addTasks(CLIENT_ACTION_ID.CHANGE_GROUP, jid, roster_tasks.ChangeRosterItemGroupsTask(jid, contact.getName(), groups, {exclude} if exclude else None))

    @xmpp_query(QUERY_SIGN.GROUP_NAME)
    def addGroup(self, name):
        error = self.__checkCooldown(CLIENT_ACTION_ID.ADD_GROUP)
        if error:
            return (False, error)
        elif self.usersStorage.isGroupExists(name):
            return (False, ClientContactError(CONTACT_ERROR_ID.GROUP_EXISTS, name))
        elif len(self.usersStorage.getGroups()) >= CONTACT_LIMIT.GROUPS_MAX_COUNT:
            return (False, ClientIntLimitError(LIMIT_ERROR_ID.MAX_GROUP, CONTACT_LIMIT.GROUPS_MAX_COUNT))
        else:
            self.usersStorage.addEmptyGroup(name)
            g_messengerEvents.users.onEmptyGroupsChanged({name}, None)
            self.__cooldown.process(CLIENT_ACTION_ID.ADD_GROUP)
            return (True, None)

    @xmpp_query(QUERY_SIGN.GROUP_NAME, QUERY_SIGN.GROUP_NAME)
    def renameGroup(self, oldName, newName):
        error = self.__checkCooldown(CLIENT_ACTION_ID.CHANGE_GROUP)
        if error:
            return (False, error)
        elif self.usersStorage.isGroupExists(newName):
            return (False, ClientContactError(CONTACT_ERROR_ID.GROUP_EXISTS))
        elif newName == oldName:
            return (False, ClientActionError(CLIENT_ACTION_ID.CHANGE_GROUP, CLIENT_ERROR_ID.GENERIC))
        elif self.usersStorage.isGroupEmpty(oldName):
            self.usersStorage.changeEmptyGroup(oldName, newName)
            g_messengerEvents.users.onEmptyGroupsChanged({newName}, {oldName})
            return (True, None)
        else:
            task = self.__makeChangeGroupsChain(oldName, newName)
            self.__cooldown.process(CLIENT_ACTION_ID.CHANGE_GROUP)
            return self.__addTasks(CLIENT_ACTION_ID.CHANGE_GROUP, task.getJID(), task)

    @xmpp_query(QUERY_SIGN.GROUP_NAME)
    def removeGroup(self, name, isForced = False):
        error = self.__checkCooldown(CLIENT_ACTION_ID.CHANGE_GROUP)
        if error:
            return (False, error)
        elif not self.usersStorage.isGroupExists(name):
            return (False, ClientContactError(CONTACT_ERROR_ID.GROUP_NOT_FOUND, name))
        elif self.usersStorage.isGroupEmpty(name):
            self.usersStorage.changeEmptyGroup(name)
            g_messengerEvents.users.onEmptyGroupsChanged(None, {name})
            return (True, None)
        else:
            if isForced:
                task = self.__makeRemoveItemsByGroupChain(name)
            else:
                task = self.__makeChangeGroupsChain(name)
            self.__cooldown.process(CLIENT_ACTION_ID.CHANGE_GROUP)
            return self.__addTasks(CLIENT_ACTION_ID.CHANGE_GROUP, task.getJID(), task)

    @xmpp_query(QUERY_SIGN.DATABASE_ID)
    def requestFriendship(self, dbID):
        error = self.__checkCooldown(CLIENT_ACTION_ID.RQ_FRIENDSHIP)
        if error:
            return (False, error)
        contact = self.usersStorage.getUser(dbID, PROTO_TYPE.XMPP)
        if not contact or contact.isCurrentPlayer():
            return (False, ClientContactError(CONTACT_ERROR_ID.CONTACT_ITEM_NOT_FOUND))
        itemType = contact.getItemType()
        if itemType == XMPP_ITEM_TYPE.BLOCK_ITEM:
            return (False, ClientContactError(CONTACT_ERROR_ID.BLOCK_ITEM_EXISTS, contact.getFullName()))
        if itemType != XMPP_ITEM_TYPE.ROSTER_ITEM:
            return (False, ClientContactError(CONTACT_ERROR_ID.ROSTER_ITEM_NOT_FOUND, contact.getFullName()))
        jid = contact.getJID()
        self.__cooldown.process(CLIENT_ACTION_ID.RQ_FRIENDSHIP)
        return self.__addTasks(CLIENT_ACTION_ID.RQ_FRIENDSHIP, jid, sub_tasks.AskSubscriptionTask(jid))

    def canApproveFriendship(self, contact):
        if not self.client() or not self.client().isConnected():
            return (False, ClientError(CLIENT_ERROR_ID.NOT_CONNECTED))
        return self.__subsRestrictions.canApproveFriendship(contact)

    def canCancelFriendship(self, contact):
        if not self.client() or not self.client().isConnected():
            return (False, ClientError(CLIENT_ERROR_ID.NOT_CONNECTED))
        return self.__subsRestrictions.canCancelFriendship(contact)

    @xmpp_query(QUERY_SIGN.DATABASE_ID)
    def approveFriendship(self, dbID):
        contact = self.usersStorage.getUser(dbID, PROTO_TYPE.XMPP)
        result, error = self.canApproveFriendship(contact)
        if not result:
            return (result, error)
        if contact.getItemType() == XMPP_ITEM_TYPE.ROSTER_ITEM:
            jid = contact.getJID()
            tasks = [sub_tasks.ApproveSubscriptionTask(jid)]
            if contact.getSubscription()[0] == _SUB.OFF:
                tasks.append(sub_tasks.AskSubscriptionTask(jid))
        else:
            jid = makeContactJID(dbID)
            tasks = (sub_tasks.ApproveSubscriptionTask(jid), sub_tasks.AskSubscriptionTask(jid))
        return self.__addTasks(CLIENT_ACTION_ID.APPROVE_FRIENDSHIP, jid, *tasks)

    @xmpp_query(QUERY_SIGN.DATABASE_ID)
    def cancelFriendship(self, dbID):
        contact = self.usersStorage.getUser(dbID, PROTO_TYPE.XMPP)
        result, error = self.canCancelFriendship(contact)
        if not result:
            return (result, error)
        jid = contact.getJID()
        tasks = [sub_tasks.CancelSubscriptionTask(jid)]
        if note_tasks.canNoteAutoDelete(contact):
            tasks.append(note_tasks.RemoveNoteTask(jid))
        return self.__addTasks(CLIENT_ACTION_ID.CANCEL_FRIENDSHIP, jid, *tasks)

    def getFriendshipRqs(self):
        return self.usersStorage.getList(RqFriendshipCriteria())

    @xmpp_query(QUERY_SIGN.DATABASE_ID, QUERY_SIGN.ACCOUNT_NAME)
    def addIgnored(self, dbID, name):
        error = self.__checkCooldown(CLIENT_ACTION_ID.ADD_IGNORED)
        if error:
            return (False, error)
        tasks, itemType = [], XMPP_ITEM_TYPE.EMPTY_ITEM
        contact = self.usersStorage.getUser(dbID, PROTO_TYPE.XMPP)
        if contact:
            if contact.isCurrentPlayer():
                return (False, ClientActionError(CLIENT_ACTION_ID.ADD_FRIEND, CLIENT_ERROR_ID.GENERIC))
            itemType = contact.getItemType()
            if itemType == XMPP_ITEM_TYPE.BLOCK_ITEM:
                return (False, ClientContactError(CONTACT_ERROR_ID.BLOCK_ITEM_EXISTS, contact.getFullName()))
        length = self.usersStorage.getCount(ItemsFindCriteria(XMPP_ITEM_TYPE.BLOCKING_LIST))
        if length >= CONTACT_LIMIT.BLOCK_MAX_COUNT:
            return (False, ClientIntLimitError(LIMIT_ERROR_ID.MAX_BLOCK_ITEMS, CONTACT_LIMIT.BLOCK_MAX_COUNT))
        if contact:
            jid = contact.getJID()
            if itemType == XMPP_ITEM_TYPE.SUB_PENDING:
                tasks.append(sub_tasks.CancelSubscriptionTask(jid))
        else:
            jid = makeContactJID(dbID)
        tasks.append(block_tasks.AddBlockItemTask(jid, name))
        if itemType == XMPP_ITEM_TYPE.ROSTER_ITEM:
            groups = contact.getGroups()
            if groups:
                tasks.append(roster_tasks.EmptyGroupsTask(jid, groups=groups))
        self.__cooldown.process(CLIENT_ACTION_ID.ADD_IGNORED)
        return self.__addTasks(CLIENT_ACTION_ID.ADD_IGNORED, jid, *tasks)

    @xmpp_query(QUERY_SIGN.DATABASE_ID)
    def removeIgnored(self, dbID):
        error = self.__checkCooldown(CLIENT_ACTION_ID.REMOVE_IGNORED)
        if error:
            return (False, error)
        contact = self.usersStorage.getUser(dbID, PROTO_TYPE.XMPP)
        if not contact:
            return (False, ClientContactError(CONTACT_ERROR_ID.CONTACT_ITEM_NOT_FOUND))
        itemType = contact.getItemType()
        if itemType not in XMPP_ITEM_TYPE.BLOCKING_LIST:
            return (False, ClientContactError(CONTACT_ERROR_ID.BLOCK_ITEM_NOT_FOUND, contact.getFullName()))
        jid = contact.getJID()
        tasks = [block_tasks.RemoveBlockItemTask(jid, contact.getName())]
        if itemType == XMPP_ITEM_TYPE.ROSTER_BLOCK_ITEM:
            tasks.append(roster_tasks.RemoveRosterItemTask(jid, contact.getName()))
        if note_tasks.canNoteAutoDelete(contact):
            tasks.append(note_tasks.RemoveNoteTask(jid))
        self.__cooldown.process(CLIENT_ACTION_ID.REMOVE_IGNORED)
        return self.__addTasks(CLIENT_ACTION_ID.REMOVE_IGNORED, jid, *tasks)

    @local_query(QUERY_SIGN.DATABASE_ID, QUERY_SIGN.ACCOUNT_NAME)
    def setMuted(self, dbID, name):
        error = self.__checkCooldown(CLIENT_ACTION_ID.SET_MUTE)
        if error:
            return (False, error)
        else:
            contact = self.usersStorage.getUser(dbID)
            if not contact:
                contact = entities.XMPPUserEntity(dbID, name=name, tags={USER_TAG.MUTED})
                self.usersStorage.setUser(contact)
            else:
                contact.addTags({USER_TAG.MUTED})
            g_messengerEvents.users.onUserActionReceived(USER_ACTION_ID.MUTE_SET, contact)
            self.__cooldown.process(CLIENT_ACTION_ID.SET_MUTE)
            return (True, None)

    @local_query(QUERY_SIGN.DATABASE_ID)
    def unsetMuted(self, dbID):
        error = self.__checkCooldown(CLIENT_ACTION_ID.UNSET_MUTE)
        if error:
            return (False, error)
        else:
            contact = self.usersStorage.getUser(dbID)
            if not contact:
                return (False, ClientContactError(CONTACT_ERROR_ID.CONTACT_ITEM_NOT_FOUND))
            if not contact.isMuted():
                return (False, ClientContactError(CONTACT_ERROR_ID.MUTED_ITEM_NOT_FOUND, contact.getFullName()))
            contact.removeTags({USER_TAG.MUTED})
            g_messengerEvents.users.onUserActionReceived(USER_ACTION_ID.MUTE_UNSET, contact)
            self.__cooldown.process(CLIENT_ACTION_ID.UNSET_MUTE)
            return (True, None)

    @xmpp_query(QUERY_SIGN.DATABASE_ID, QUERY_SIGN.NOTE_TEXT)
    def setNote(self, dbID, note):
        error = self.__checkCooldown(CLIENT_ACTION_ID.SET_NOTE)
        if error:
            return (False, error)
        contact = self.usersStorage.getUser(dbID)
        if not contact or not contact.getTags():
            return (False, ClientContactError(CONTACT_ERROR_ID.CONTACT_ITEM_NOT_FOUND))
        jid = makeContactJID(dbID)
        self.__cooldown.process(CLIENT_ACTION_ID.SET_NOTE)
        return self.__addTasks(CLIENT_ACTION_ID.SET_NOTE, jid, note_tasks.SetNoteTask(jid, note))

    @xmpp_query(QUERY_SIGN.DATABASE_ID)
    def removeNote(self, dbID):
        error = self.__checkCooldown(CLIENT_ACTION_ID.REMOVE_NOTE)
        if error:
            return (False, error)
        contact = self.usersStorage.getUser(dbID)
        if not contact or not contact.getTags():
            return (False, ClientContactError(CONTACT_ERROR_ID.CONTACT_ITEM_NOT_FOUND))
        if not contact.getNote():
            return (False, ClientContactError(CONTACT_ERROR_ID.NOTE_NOT_FOUND, name=contact.getFullName()))
        jid = makeContactJID(dbID)
        self.__cooldown.process(CLIENT_ACTION_ID.REMOVE_NOTE)
        return self.__addTasks(CLIENT_ACTION_ID.SET_NOTE, jid, note_tasks.RemoveNoteTask(jid))

    def __makeChangeGroupsChain(self, exclude, include = None):
        chain = []
        for contact in self.usersStorage.getList(GroupFindCriteria(exclude)):
            jid = contact.getJID()
            groups = contact.getGroups()
            groups.discard(exclude)
            if include:
                groups.add(include)
            chain.append((jid, contact.getName(), groups))

        return roster_tasks.ChangeRosterItemsGroupsChain(chain)

    def __makeRemoveItemsByGroupChain(self, name):
        chain = []
        for contact in self.usersStorage.getList(GroupFindCriteria(name)):
            groups = contact.getGroups()
            groups.discard(name)
            chain.append((contact.getJID(), contact.getName(), groups))

        return roster_tasks.RemoveRosterItemsGroupsChain(chain)

    def __addTasks(self, actionID, jid, *tasks):
        if self.__tasks.addTasks(jid, *tasks):
            self.__tasks.runFirstTask(jid)
        else:
            return (False, ClientActionError(actionID, CLIENT_ERROR_ID.LOCKED))
        return (True, None)

    def __checkCooldown(self, actionID):
        error = None
        if self.__cooldown.isInProcess(actionID):
            error = ChatCoolDownError(actionID, self.__cooldown.getDefaultCoolDown())
        return error

    def __handleConnected(self):
        self.__tasks.suspend()
        self.__seq.onInited += self.__onSeqsInited
        self.__seq.init(roster_tasks.RosterResultTask(), block_tasks.BlockListResultTask(), note_tasks.NotesListTask())

    def __handleDisconnected(self, reason, description):
        if reason == DISCONNECT_REASON.BY_REQUEST:
            self.__seq.suspend()
        self.__seq.fini()
        self.__tasks.clear()
        self.__subsBatch.clear()
        for contact in self.usersStorage.getList(ProtoFindCriteria(PROTO_TYPE.XMPP)):
            resources = contact.getItem().getResources()
            if not resources.isEmpty():
                resources.clear()
                g_messengerEvents.users.onUserStatusUpdated(contact)

    def __handleIQ(self, iqID, iqType, pyGlooxTag):
        if not self.__seq.handleIQ(iqID, iqType, pyGlooxTag):
            self.__tasks.handleIQ(iqID, iqType, pyGlooxTag)

    def __handleRosterQuery(self, iqID, jid, context):
        self.__tasks.setIQ(iqID, jid, context)

    def __handleRosterResult(self, generator):
        g_logOutput.debug(_LOG.ROSTER, 'Roster result is received')
        self.__seq.sync(0, generator())

    def __handleRosterItemSet(self, jid, name, groups, sub, clanInfo):
        g_logOutput.debug(_LOG.ROSTER, 'Roster push is received', jid, name, groups, sub, clanInfo)
        self.__tasks.sync(jid, name, groups, sub, clanInfo, defaultTask=roster_tasks.SyncSubscriptionTask)

    def __handleRosterItemRemoved(self, jid):
        self.__tasks.sync(jid, defaultTask=roster_tasks.RemoveRosterItemTask)

    def __handlePresence(self, jid, resource):
        jid = ContactJID(jid)
        dbID = jid.getDatabaseID()
        if not dbID:
            return
        else:
            user = self.usersStorage.getUser(dbID, PROTO_TYPE.XMPP)
            if resource.presence == PRESENCE.UNAVAILABLE:
                if user and not user.isCurrentPlayer():
                    user.update(jid=jid, resource=None, clanInfo=resource.getClanInfo())
                    g_logOutput.debug(_LOG.RESOURCE, 'Resource is removed', user.getName(), jid.getResource(), resource)
            elif resource.presence != PRESENCE.UNKNOWN:
                if not user:
                    user = entities.XMPPUserEntity(dbID)
                    self.usersStorage.setUser(user)
                if user.isCurrentPlayer():
                    self.playerCtx.setBanInfo(resource.getBanInfo())
                else:
                    user.update(jid=jid, resource=resource, clanInfo=resource.getClanInfo())
                    g_logOutput.debug(_LOG.RESOURCE, 'Resource is set', user.getName(), jid.getResource(), resource)
            if user:
                g_messengerEvents.users.onUserStatusUpdated(user)
            return

    def __handleSubscriptionRequest(self, subs):
        self.__subsBatch.addSubs(subs)
        if not self.__seq.isInited():
            return
        self.__subsRestrictions.setToUseCachedCounts(True)
        self.__subsBatch.process(self.__tasks)
        self.__subsRestrictions.setToUseCachedCounts(False)

    def __onSeqsInited(self):
        g_logOutput.debug(_LOG.GENERIC, 'Starts to process contacts tasks')
        self.__presence.sendPresence(True)
        self.__tasks.release()
        self.__tasks.onSeqTaskRequested += self.__onSeqTaskRequested
        self.__subsRestrictions.setToUseCachedCounts(True)
        self.__subsBatch.process(self.__tasks)
        self.__subsRestrictions.setToUseCachedCounts(False)
        g_messengerEvents.users.onUsersListReceived({USER_TAG.FRIEND, USER_TAG.IGNORED, USER_TAG.MUTED})

    def __onSeqTaskRequested(self, task):
        self.__seq.addMultiRq(task)

    def __me_onPluginConnectFailed(self, protoType, _, tries):
        if protoType != PROTO_TYPE.XMPP:
            return
        scope = self.__presence.getUserScope()
        if scope == MESSENGER_SCOPE.BATTLE:
            threshold = _MAX_TRIES_FAILED_IN_BATTLE
        else:
            threshold = _MAX_TRIES_FAILED_IN_LOBBY
        if tries == threshold:
            g_messengerEvents.users.onUsersListReceived({USER_TAG.CACHED,
             USER_TAG.FRIEND,
             USER_TAG.IGNORED,
             USER_TAG.MUTED})

    def __us_onRestoredFromCache(self, stateGenerator):
        if not g_settings.server.XMPP.isEnabled():
            return
        if stateGenerator:
            setUser = self.usersStorage.setUser
            isInited = self.__seq.isInited()
            for dbID, state in stateGenerator(PROTO_TYPE.XMPP):
                contact = entities.XMPPUserEntity(dbID)
                result = contact.setPersistentState(state)
                if result and (not isInited or contact.getItemType() == XMPP_ITEM_TYPE.SUB_PENDING):
                    setUser(contact)

        g_messengerEvents.users.onUsersListReceived({USER_TAG.CACHED,
         USER_TAG.FRIEND,
         USER_TAG.IGNORED,
         USER_TAG.MUTED})

    def __ms_onUserPreferencesUpdated(self):
        self.__seq.release()
