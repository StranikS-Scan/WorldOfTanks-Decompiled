# Embedded file name: scripts/client/messenger/proto/xmpp/contacts/sub_tasks.py
from messenger.m_constants import USER_TAG, USER_ACTION_ID, CLIENT_ACTION_ID
from messenger.proto.xmpp import errors
from messenger.proto.xmpp.contacts.roster_tasks import SyncSubscriptionTask
from messenger.proto.xmpp.contacts.tasks import TASK_RESULT
from messenger.proto.xmpp.gloox_constants import SUBSCRIPTION as _SUB

class AskSubscriptionTask(SyncSubscriptionTask):

    def sync(self, name, groups, sub = None, clanInfo = None):
        if sub[0] != _SUB.OFF:
            self._result = TASK_RESULT.REMOVE
        self._doSync(name, groups, sub, clanInfo)
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

    def sync(self, name, groups, sub = None, clanInfo = None):
        if sub[1] == _SUB.ON:
            user = self._getUser()
            self._result = TASK_RESULT.REMOVE
            if user and not self._auto:
                user.removeTags({USER_TAG.SUB_IN_PROCESS})
                user.addTags({USER_TAG.SUB_APPROVED})
            if self._auto and sub[0] == _SUB.PENDING:
                self._tasks.append(AskSubscriptionTask(self._jid))
                self._result |= TASK_RESULT.CLONE
        self._doSync(name, groups, sub, clanInfo)
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
