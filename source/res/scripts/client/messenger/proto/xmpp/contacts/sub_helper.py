# Embedded file name: scripts/client/messenger/proto/xmpp/contacts/sub_helper.py
from messenger import g_settings
from messenger.m_constants import USER_TAG, PROTO_TYPE
from messenger.proto.events import g_messengerEvents
from messenger.proto.xmpp import entities
from messenger.proto.xmpp.contacts.sub_tasks import CancelSubscriptionTask, ApproveSubscriptionTask, AskSubscriptionTask
from messenger.proto.xmpp.errors import ClientContactError, ClientIntLimitError
from messenger.proto.xmpp.find_criteria import ItemsFindCriteria
from messenger.proto.xmpp.gloox_constants import SUBSCRIPTION as _SUB
from messenger.proto.xmpp.log_output import g_logOutput, CLIENT_LOG_AREA as _LOG
from messenger.proto.xmpp.xmpp_constants import XMPP_ITEM_TYPE, CONTACT_ERROR_ID, LIMIT_ERROR_ID, CONTACT_LIMIT
from messenger.proto.xmpp.xmpp_items import SubPendingItem
from messenger.storage import storage_getter
_INBOUND_SUB_REMOVE_TAGS = {USER_TAG.SUB_IN_PROCESS, USER_TAG.SUB_CANCELED, USER_TAG.SUB_APPROVED}

class InboundSubscriptionsBatch(object):
    __slots__ = ('_subs', '_cancelTasks', '_approveTasks', '_newRqs', '_oldRqs')

    def __init__(self):
        super(InboundSubscriptionsBatch, self).__init__()
        self._subs = []
        self._cancelTasks = {}
        self._approveTasks = {}
        self._newRqs = []
        self._oldRqs = []

    @storage_getter('users')
    def usersStorage(self):
        return None

    def clear(self):
        self._subs = []
        self._reset()

    def addSubs(self, subs):
        self._subs.extend(subs)

    def process(self, taskQueue):
        self._validate()
        self._populate(taskQueue)

    def _reset(self):
        self._cancelTasks.clear()
        self._approveTasks.clear()
        self._newRqs = []
        self._oldRqs = []

    def _cancel(self, jid, _):
        self._cancelTasks[jid] = (CancelSubscriptionTask(jid, auto=True),)
        return True

    def _approve(self, jid, contact):
        if contact.getSubscription()[0] == _SUB.OFF:
            tasks = (ApproveSubscriptionTask(jid, auto=True), AskSubscriptionTask(jid))
        else:
            tasks = (ApproveSubscriptionTask(jid, auto=True),)
        self._approveTasks[jid] = tasks
        return True

    def _ignore(self, contact):
        contact.update(trusted=True)
        contact.addTags({USER_TAG.WO_NOTIFICATION})
        self._oldRqs.append(contact)
        return True

    def _validate(self):
        self._reset()
        ignoreSubRq = not g_settings.userPrefs.receiveFriendshipRequest
        getter = self.usersStorage.getUser
        setter = self.usersStorage.setUser
        while self._subs:
            jid, name, _, wgexts = self._subs.pop(0)
            dbID, clanInfo, isProcessed = jid.getDatabaseID(), wgexts.clan, False
            contact = getter(dbID, PROTO_TYPE.XMPP)
            if not contact:
                contact = entities.XMPPUserEntity(dbID, name=name, clanInfo=clanInfo, item=SubPendingItem(jid))
                setter(contact)
                if ignoreSubRq:
                    isProcessed = self._cancel(jid, contact)
            else:
                contact.removeTags(_INBOUND_SUB_REMOVE_TAGS)
                contact.update(clanInfo=clanInfo)
                if contact.isCurrentPlayer():
                    continue
                itemType = contact.getItemType()
                if itemType == XMPP_ITEM_TYPE.ROSTER_ITEM:
                    isProcessed = self._approve(jid, contact)
                elif ignoreSubRq:
                    isProcessed = self._cancel(jid, contact)
                elif itemType in XMPP_ITEM_TYPE.BLOCKING_LIST:
                    isProcessed = self._cancel(jid, contact)
                elif itemType == XMPP_ITEM_TYPE.SUB_PENDING:
                    isProcessed = self._ignore(contact)
                else:
                    contact.update(item=SubPendingItem(jid))
            if not isProcessed:
                contact.removeTags({USER_TAG.WO_NOTIFICATION})
                self._newRqs.append(contact)

    def _populate(self, taskQueue):
        jids = []
        while self._cancelTasks:
            jid, tasks = self._cancelTasks.popitem()
            jids.append(jid)
            if taskQueue.addTasks(jid, *tasks):
                taskQueue.runFirstTask(jid)

        if jids:
            g_logOutput.debug(_LOG.SUBSCRIPTION, 'Inbound subscriptions are canceled automatically', jids[:10])
            jids = []
        while self._approveTasks:
            jid, tasks = self._approveTasks.popitem()
            jids.append(jid)
            if taskQueue.addTasks(jid, *tasks):
                taskQueue.runFirstTask(jid)

        if jids:
            g_logOutput.debug(_LOG.SUBSCRIPTION, 'Inbound subscriptions are approved automatically', jids[:10])
        if self._newRqs:
            g_logOutput.debug(_LOG.SUBSCRIPTION, 'New inbound subscriptions are received', self._newRqs[:10])
            g_messengerEvents.users.onFriendshipRequestsAdded(self._newRqs)
        if self._oldRqs:
            g_logOutput.debug(_LOG.SUBSCRIPTION, 'Inbound subscriptions are ignored to display', self._oldRqs[:10])
            g_messengerEvents.users.onFriendshipRequestsUpdated(self._oldRqs)


class SubscriptionsRestrictions(object):
    __slots__ = ('_useCachedCounts', '_cachedRosterCount')

    def __init__(self):
        super(SubscriptionsRestrictions, self).__init__()
        self._useCachedCounts = False
        self._cachedRosterCount = 0

    @storage_getter('users')
    def usersStorage(self):
        return None

    def setToUseCachedCounts(self, flag):
        if self._useCachedCounts == flag:
            return
        self._useCachedCounts = flag
        if self._useCachedCounts:
            self._cachedRosterCount = self._getRosterCount()
        else:
            self._cachedRosterCount = 0

    def canAddFriends(self):
        if self._useCachedCounts:
            length = self._cachedRosterCount
        else:
            length = self._getRosterCount()
        if length >= CONTACT_LIMIT.ROSTER_MAX_COUNT:
            return (False, ClientIntLimitError(LIMIT_ERROR_ID.MAX_ROSTER_ITEMS, CONTACT_LIMIT.ROSTER_MAX_COUNT))
        else:
            return (True, None)

    def canApproveFriendship(self, contact):
        if not contact:
            return (False, ClientContactError(CONTACT_ERROR_ID.CONTACT_ITEM_NOT_FOUND))
        tags = contact.getTags()
        if USER_TAG.SUB_APPROVED in tags:
            return (False, ClientContactError(CONTACT_ERROR_ID.FRIENDSHIP_APPROVED, contact.getFullName()))
        if contact.getItemType() == XMPP_ITEM_TYPE.ROSTER_ITEM:
            if USER_TAG.SUB_FROM in contact.getTags():
                return (False, ClientContactError(CONTACT_ERROR_ID.FRIENDSHIP_APPROVED, contact.getFullName()))
            else:
                return (True, None)
        if contact.getItemType() == XMPP_ITEM_TYPE.SUB_PENDING:
            if USER_TAG.SUB_IN_PROCESS in tags:
                return (False, ClientContactError(CONTACT_ERROR_ID.FRIENDSHIP_RQ_PROCESS, contact.getFullName()))
            if USER_TAG.SUB_CANCELED in tags:
                return (False, ClientContactError(CONTACT_ERROR_ID.FRIENDSHIP_CANCELED, contact.getFullName()))
            result, error = self.canAddFriends()
            if not result:
                return (False, error)
            return (True, None)
        else:
            return (False, ClientContactError(CONTACT_ERROR_ID.CONTACT_ITEM_NOT_FOUND))

    def canCancelFriendship(self, contact):
        if not contact:
            return (False, ClientContactError(CONTACT_ERROR_ID.CONTACT_ITEM_NOT_FOUND))
        tags = contact.getTags()
        if USER_TAG.SUB_APPROVED in tags:
            return (False, ClientContactError(CONTACT_ERROR_ID.FRIENDSHIP_APPROVED, contact.getFullName()))
        elif USER_TAG.SUB_FROM in tags:
            return (False, ClientContactError(CONTACT_ERROR_ID.FRIENDSHIP_APPROVED, contact.getFullName()))
        elif USER_TAG.SUB_IN_PROCESS in tags:
            return (False, ClientContactError(CONTACT_ERROR_ID.FRIENDSHIP_RQ_PROCESS, contact.getFullName()))
        elif USER_TAG.SUB_CANCELED in tags:
            return (False, ClientContactError(CONTACT_ERROR_ID.FRIENDSHIP_CANCELED, contact.getFullName()))
        elif contact.getItemType() == XMPP_ITEM_TYPE.ROSTER_ITEM:
            return (False, ClientContactError(CONTACT_ERROR_ID.ROSTER_ITEM_EXISTS, contact.getFullName()))
        else:
            return (True, None)

    def _getRosterCount(self):
        return self.usersStorage.getCount(ItemsFindCriteria((XMPP_ITEM_TYPE.ROSTER_ITEM,)))
