# Embedded file name: scripts/client/messenger/proto/xmpp/contacts/sub_tasks.py
from messenger.m_constants import USER_TAG, USER_ACTION_ID, CLIENT_ACTION_ID
from messenger.proto.events import g_messengerEvents
from messenger.proto.xmpp import entities, errors
from messenger.proto.xmpp.contacts.roster_tasks import SyncSubscriptionTask
from messenger.proto.xmpp.contacts.tasks import TASK_RESULT, ContactTask
from messenger.proto.xmpp.gloox_constants import SUBSCRIPTION as _SUB
from messenger.proto.xmpp.log_output import g_logOutput, CLIENT_LOG_AREA
from messenger.proto.xmpp.xmpp_constants import XMPP_ITEM_TYPE
from messenger.proto.xmpp.xmpp_items import SubPendingItem

class AskSubscriptionTask(SyncSubscriptionTask):

    def sync(self, name, groups, to, from_):
        if to != _SUB.OFF:
            self._result = TASK_RESULT.REMOVE
        self._doSync(name, groups, to, from_)
        return self._result

    def _doRun(self, client):
        client.askSubscription(self._jid)

    def _getError(self, pyGlooxTag):
        return errors.createServerActionError(CLIENT_ACTION_ID.RQ_FRIENDSHIP, pyGlooxTag)


class _ChangeSubscriptionTask(SyncSubscriptionTask):
    __slots__ = ('_auto',)

    def __init__(self, jid, name = '', auto = False):
        super(_ChangeSubscriptionTask, self).__init__(jid, name)
        self._auto = auto


class ApproveSubscriptionTask(_ChangeSubscriptionTask):
    __slots__ = ('_tasks',)

    def __init__(self, jid, name = '', auto = False):
        super(ApproveSubscriptionTask, self).__init__(jid, name, auto)
        self._tasks = []

    def clone(self):
        return self._tasks

    def sync(self, name, groups, to, from_):
        if from_ == _SUB.ON:
            user = self._getUser()
            self._result = TASK_RESULT.REMOVE
            if user and not self._auto:
                user.removeTags({USER_TAG.SUB_IN_PROCESS})
                user.addTags({USER_TAG.SUB_APPROVED})
            if self._auto and to == _SUB.PENDING:
                self._tasks.append(AskSubscriptionTask(self._jid))
                self._result |= TASK_RESULT.CLONE
        self._doSync(name, groups, to, from_)
        return self._result

    def _doRun(self, client):
        user = self._getUser()
        if user:
            user.addTags({USER_TAG.SUB_IN_PROCESS})
            self._doNotify(USER_ACTION_ID.SUBSCRIPTION_CHANGED, user, nextRev=False)
        client.approveSubscription(self._jid)

    def _getError(self, pyGlooxTag):
        return errors.createServerActionError(CLIENT_ACTION_ID.APPROVE_FRIENDSHIP, pyGlooxTag)


class CancelSubscriptionTask(_ChangeSubscriptionTask):

    def isInstantaneous(self):
        return True

    def _doRun(self, client):
        user = self._getUser()
        if user:
            user.update(item=None)
            if not self._auto:
                user.addTags({USER_TAG.SUB_CANCELED})
            self._doNotify(USER_ACTION_ID.SUBSCRIPTION_CHANGED, user, nextRev=False)
        client.cancelSubscription(self._jid)
        return


class InboundSubscriptionTask(ContactTask):
    __slots__ = ('_tasks',)

    def __init__(self, jid, name = ''):
        super(InboundSubscriptionTask, self).__init__(jid, name)
        self._tasks = []

    def isInstantaneous(self):
        return True

    def clear(self):
        self._tasks = []
        super(InboundSubscriptionTask, self).clear()

    def clone(self):
        return self._tasks

    def run(self):
        self._result = TASK_RESULT.REMOVE
        contact = self._getUser()
        if not contact:
            contact = entities.XMPPUserEntity(self._jid.getDatabaseID(), name=self._name, item=SubPendingItem(self._jid))
            self.usersStorage.setUser(contact)
        else:
            contact.removeTags({USER_TAG.SUB_IN_PROCESS, USER_TAG.SUB_CANCELED, USER_TAG.SUB_APPROVED})
            if contact.isCurrentPlayer():
                return self._result
            itemType = contact.getItemType()
            if itemType in XMPP_ITEM_TYPE.BLOCKING_LIST:
                return self._cancel(contact)
            if itemType == XMPP_ITEM_TYPE.ROSTER_ITEM:
                return self._approve(contact)
            if itemType == XMPP_ITEM_TYPE.SUB_PENDING:
                return self._ignore(contact)
            contact.update(item=SubPendingItem(self._jid))
        g_logOutput.debug(CLIENT_LOG_AREA.SUBSCRIPTION, 'Inbound subscription received', contact)
        contact.removeTags({USER_TAG.WO_NOTIFICATION})
        g_messengerEvents.users.onFriendshipRequestReceived(contact)
        return self._result

    def _cancel(self, contact):
        g_logOutput.debug(CLIENT_LOG_AREA.SUBSCRIPTION, 'Cancels subscription automatically, contact is in the block list', contact)
        self._tasks.append(CancelSubscriptionTask(self._jid, auto=True))
        self._result |= TASK_RESULT.CLONE
        return self._result

    def _approve(self, contact):
        g_logOutput.debug(CLIENT_LOG_AREA.SUBSCRIPTION, 'Approves subscription automatically, contact is in the roster', contact)
        self._tasks.append(ApproveSubscriptionTask(self._jid, auto=True))
        if contact.getSubscription()[0] == _SUB.OFF:
            self._tasks.append(AskSubscriptionTask(self._jid))
        self._result |= TASK_RESULT.CLONE
        return self._result

    def _ignore(self, contact):
        contact.update(trusted=True)
        contact.addTags({USER_TAG.WO_NOTIFICATION})
        g_logOutput.debug(CLIENT_LOG_AREA.SUBSCRIPTION, 'Ignores inbound subscription', contact)
        g_messengerEvents.users.onUserActionReceived(USER_ACTION_ID.SUBSCRIPTION_CHANGED, contact)
        return self._result
