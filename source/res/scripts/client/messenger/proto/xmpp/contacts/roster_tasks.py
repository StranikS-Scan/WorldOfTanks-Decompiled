# Embedded file name: scripts/client/messenger/proto/xmpp/contacts/roster_tasks.py
from messenger.m_constants import USER_ACTION_ID, USER_TAG, PROTO_TYPE, CLIENT_ACTION_ID
from messenger.proto.events import g_messengerEvents
from messenger.proto.xmpp import entities, errors
from messenger.proto.xmpp.contacts.tasks import TASK_RESULT, ContactTask, SeqTask
from messenger.proto.xmpp.find_criteria import ItemsFindCriteria
from messenger.proto.xmpp.gloox_constants import SUBSCRIPTION as _SUB, ROSTER_CONTEXT
from messenger.proto.xmpp.log_output import CLIENT_LOG_AREA, g_logOutput
from messenger.proto.xmpp.xmpp_constants import XMPP_ITEM_TYPE
from messenger.proto.xmpp.xmpp_items import RosterItem

def _syncRosterItem(storage, jid, name, groups, to, from_):
    dbID = jid.getDatabaseID()
    user = storage.getUser(dbID, PROTO_TYPE.XMPP)
    if user:
        if user.isCurrentPlayer():
            return None
        if user.getItemType() == XMPP_ITEM_TYPE.ROSTER_ITEM:
            user.update(name=name, groups=groups, to=to, from_=from_, trusted=True)
        else:
            user.update(name=name, item=RosterItem(jid, groups, to, from_, resources=user.getItem().getResources()))
    else:
        user = entities.XMPPUserEntity(dbID, name=name, item=RosterItem(jid, groups, to, from_))
        storage.setUser(user)
    return user


def _syncEmptyGroups(storage, groups, woEvent = False):
    isGroupExists = storage.isGroupExists
    addEmptyGroup = storage.addEmptyGroup
    included = set()
    for group in groups:
        if not isGroupExists(group):
            addEmptyGroup(group)
            included.add(group)

    if included and not woEvent:
        g_messengerEvents.users.onEmptyGroupsChanged(included, set())


class RosterResultTask(SeqTask):

    def run(self):
        pass

    def sync(self, seq):
        storage = self.usersStorage
        for jid, name, groups, to, from_ in seq:
            _syncRosterItem(storage, jid, name, groups, to, from_)

        storage.removeTags({USER_TAG.CACHED}, ItemsFindCriteria((XMPP_ITEM_TYPE.ROSTER_ITEM,)))


class RosterItemTask(ContactTask):
    __slots__ = ('_groups',)

    def __init__(self, jid, name = '', groups = None):
        super(RosterItemTask, self).__init__(jid, name)
        self._groups = groups or set()

    def clear(self):
        self._groups = set()
        super(RosterItemTask, self).clear()

    def getContext(self):
        return ROSTER_CONTEXT.PUSH_ROSTER_ITEM

    def _doSync(self, name, groups = None, to = _SUB.OFF, from_ = _SUB.OFF):
        return _syncRosterItem(self.usersStorage, self._jid, name, groups, to, from_)


class SyncSubscriptionTask(RosterItemTask):

    def _doSync(self, name, groups = None, to = _SUB.OFF, from_ = _SUB.OFF):
        user = self._getUser()
        if user:
            prevSub = user.getSubscription()
            isOnline = user.isOnline()
        else:
            prevSub = None
            isOnline = False
        user = super(SyncSubscriptionTask, self)._doSync(name, groups, to, from_)
        nextSub = user.getSubscription()
        if prevSub and prevSub != nextSub:
            self._doNotify(USER_ACTION_ID.SUBSCRIPTION_CHANGED, user, nextRev=False)
            if isOnline != user.isOnline():
                g_messengerEvents.users.onUserStatusUpdated(user)
        return user

    def _doRun(self, client):
        user = self._getUser()
        if user:
            user.addTags({USER_TAG.SUB_IN_PROCESS})


class AddRosterItemTask(RosterItemTask):

    def _doSync(self, name, groups = None, to = _SUB.OFF, from_ = _SUB.OFF):
        user = super(AddRosterItemTask, self)._doSync(name, groups, to, from_)
        if user:
            g_logOutput.debug(CLIENT_LOG_AREA.ROSTER, 'Item is added to roster', user)
            self._doNotify(USER_ACTION_ID.FRIEND_ADDED, user)

    def _doRun(self, client):
        client.setContactToRoster(self._jid, self._name, self._groups)

    def _getError(self, pyGlooxTag):
        return errors.createServerActionError(CLIENT_ACTION_ID.ADD_FRIEND, pyGlooxTag)


class RemoveRosterItemTask(RosterItemTask):

    def _doSync(self, name, groups = None, to = _SUB.OFF, from_ = _SUB.OFF):
        user = self._getUser()
        if not user or user.isCurrentPlayer():
            return user
        else:
            if user.getItemType() == XMPP_ITEM_TYPE.ROSTER_ITEM:
                user.update(item=None)
                _syncEmptyGroups(self.usersStorage, self._groups)
                g_logOutput.debug(CLIENT_LOG_AREA.ROSTER, 'Roster item is removed', user)
                self._doNotify(USER_ACTION_ID.FRIEND_REMOVED, user)
            return user

    def _doRun(self, client):
        client.removeContactFromRoster(self._jid)

    def getContext(self):
        return ROSTER_CONTEXT.REMOVE_ROSTER_ITEM

    def _getError(self, pyGlooxTag):
        return errors.createServerActionError(CLIENT_ACTION_ID.REMOVE_FRIEND, pyGlooxTag)


class EmptyGroupsTask(RosterItemTask):

    def isInstantaneous(self):
        return True

    def _doRun(self, client):
        _syncEmptyGroups(self.usersStorage, self._groups)


class ChangeRosterItemGroupsTask(RosterItemTask):
    __slots__ = ('_exclude',)

    def __init__(self, jid, name = '', groups = None, exclude = None):
        super(ChangeRosterItemGroupsTask, self).__init__(jid, name, groups)
        self._exclude = exclude or set()

    def clear(self):
        self._groups = None
        self._exclude = None
        super(ChangeRosterItemGroupsTask, self).clear()
        return

    def sync(self, name, groups, to, from_):
        if self._groups != groups:
            return self._result
        self._result = TASK_RESULT.REMOVE
        user = self._doSync(name, groups, to, from_)
        if user:
            _syncEmptyGroups(self.usersStorage, self._exclude, True)
            self._doNotify(USER_ACTION_ID.GROUPS_CHANGED, user)
        return self._result

    def _doRun(self, client):
        client.setContactToRoster(self._jid, self._name, self._groups)

    def _getError(self, pyGlooxTag):
        return errors.createServerActionError(CLIENT_ACTION_ID.CHANGE_GROUP, pyGlooxTag)


class _RosterItemsGroupsChain(object):

    def next(self, chain):
        if not chain:
            raise AssertionError('Chain can not be empty.')
            self._chain = chain
            raise self._chain and (len(self._chain[0]) == 3 or AssertionError)
        return self._chain.pop(0)


class RemoveRosterItemsGroupsChain(RemoveRosterItemTask, _RosterItemsGroupsChain):

    def __init__(self, queue):
        jid, name, groups = self.next(queue)
        super(RemoveRosterItemsGroupsChain, self).__init__(jid, name, groups)

    def sync(self, name, groups, to, from_):
        user = self._doSync(name, groups, to, from_)
        if user:
            if user.getItemType() == XMPP_ITEM_TYPE.ROSTER_ITEM:
                actionID = USER_ACTION_ID.GROUPS_CHANGED
            else:
                actionID = USER_ACTION_ID.FRIEND_REMOVED
            self._doNotify(actionID, user)
        self._result = TASK_RESULT.REMOVE | TASK_RESULT.CLONE
        return self._result

    def clone(self):
        if self._chain:
            tasks = [RemoveRosterItemsGroupsChain(self._chain)]
        else:
            tasks = []
        return tasks

    def getContext(self):
        if self._groups:
            context = ROSTER_CONTEXT.PUSH_ROSTER_ITEM
        else:
            context = ROSTER_CONTEXT.REMOVE_ROSTER_ITEM
        return context

    def _doRun(self, client):
        if self._groups:
            client.setContactToRoster(self._jid, self._name, self._groups)
        else:
            client.removeContactFromRoster(self._jid)

    def _doSync(self, name, groups = None, to = _SUB.OFF, from_ = _SUB.OFF):
        if self._groups:
            user = _syncRosterItem(self.usersStorage, self._jid, name, groups, to, from_)
        else:
            user = super(RemoveRosterItemsGroupsChain, self)._doSync(name, groups, to, from_)
        return user


class ChangeRosterItemsGroupsChain(ChangeRosterItemGroupsTask, _RosterItemsGroupsChain):

    def __init__(self, queue):
        jid, name, groups = self.next(queue)
        super(ChangeRosterItemsGroupsChain, self).__init__(jid, name, groups)

    def sync(self, name, groups, to, from_):
        user = self._doSync(name, groups, to, from_)
        if user:
            self._doNotify(USER_ACTION_ID.GROUPS_CHANGED, user)
        self._result = TASK_RESULT.CLONE | TASK_RESULT.REMOVE
        return self._result

    def clone(self):
        if self._chain:
            tasks = [ChangeRosterItemsGroupsChain(self._chain)]
        else:
            tasks = []
        return tasks
