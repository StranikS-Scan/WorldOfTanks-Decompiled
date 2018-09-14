# Embedded file name: scripts/client/messenger/proto/xmpp/contacts/block_tasks.py
from shared_utils import findFirst
from messenger.m_constants import USER_ACTION_ID, USER_TAG, PROTO_TYPE, CLIENT_ACTION_ID
from messenger.proto.xmpp import entities, errors
from messenger.proto.xmpp.contacts.tasks import TASK_RESULT, ContactTask, SeqTask, IQTask
from messenger.proto.xmpp.extensions import blocking_cmd
from messenger.proto.xmpp.find_criteria import ItemsFindCriteria
from messenger.proto.xmpp.jid import ContactJID
from messenger.proto.xmpp.log_output import g_logOutput, CLIENT_LOG_AREA
from messenger.proto.xmpp.xmpp_constants import XMPP_ITEM_TYPE
from messenger.proto.xmpp.xmpp_items import BlockItem

def _syncBlockItem(storage, jid, name = '', dbID = 0, clanInfo = None):
    dbID = jid.getDatabaseID()
    user = storage.getUser(dbID, PROTO_TYPE.XMPP)
    if user:
        if user.isCurrentPlayer():
            return None
        if user.getItemType() == XMPP_ITEM_TYPE.BLOCKING_LIST:
            user.update(name=name, clanInfo=clanInfo, trusted=True)
        else:
            user.update(name=name, clanInfo=clanInfo, item=BlockItem(jid))
        user.addTags({USER_TAG.MUTED})
    else:
        user = entities.XMPPUserEntity(dbID, name=name, clanInfo=clanInfo, item=BlockItem(jid), tags={USER_TAG.MUTED})
        storage.setUser(user)
    return user


class _BlockItemTask(ContactTask):

    def sync(self, name, groups, sub = None, clanInfo = None):
        return self._result


class BlockListResultTask(SeqTask):

    def result(self, pyGlooxTag):
        handler = blocking_cmd.BlockListHandler()
        storage = self.usersStorage
        for jid, info in handler.handleTag(pyGlooxTag):
            _syncBlockItem(storage, jid, **info)

        self.usersStorage.removeTags({USER_TAG.CACHED}, ItemsFindCriteria(XMPP_ITEM_TYPE.BLOCKING_LIST))
        self._result = TASK_RESULT.REMOVE

    def _doRun(self, client):
        self._iqID = client.sendIQ(blocking_cmd.BlockListQuery())


class AddBlockItemTask(_BlockItemTask):

    def set(self, pyGlooxTag):
        result = blocking_cmd.BlockItemHandler().handleTag(pyGlooxTag)
        jid, info = findFirst(None, result, ('', {}))
        if jid != self._jid:
            return
        else:
            user = _syncBlockItem(self.usersStorage, self._jid, **info)
            if user:
                g_logOutput.debug(CLIENT_LOG_AREA.BLOCK_LIST, 'Block item is added', jid, info)
                self._doNotify(USER_ACTION_ID.IGNORED_ADDED, user)
                self._doNotify(USER_ACTION_ID.MUTE_SET, user, False)
            self._result = TASK_RESULT.REMOVE
            return

    def _doRun(self, client):
        self._iqID = client.sendIQ(blocking_cmd.BlockItemQuery(self._jid))

    def _getError(self, pyGlooxTag):
        return errors.createServerActionError(CLIENT_ACTION_ID.ADD_IGNORED, pyGlooxTag)


class RemoveBlockItemTask(_BlockItemTask):

    def set(self, pyGlooxTag):
        result = blocking_cmd.UnblockItemHandler().handleTag(pyGlooxTag)
        jid, info = findFirst(None, result, ('', {}))
        if jid != self._jid:
            return
        else:
            user = self._getUser()
            if user and user.getItemType() in XMPP_ITEM_TYPE.BLOCKING_LIST:
                user.update(item=None)
                user.removeTags({USER_TAG.MUTED})
                g_logOutput.debug(CLIENT_LOG_AREA.BLOCK_LIST, 'Block item is removed', jid, info)
                self._doNotify(USER_ACTION_ID.IGNORED_REMOVED, user)
                self._doNotify(USER_ACTION_ID.MUTE_UNSET, user, False)
                if user.isFriend():
                    self._doNotify(USER_ACTION_ID.FRIEND_ADDED, user, False)
            self._result = TASK_RESULT.REMOVE
            return

    def _doRun(self, client):
        self._iqID = client.sendIQ(blocking_cmd.UnblockItemQuery(self._jid))

    def _getError(self, pyGlooxTag):
        return errors.createServerActionError(CLIENT_ACTION_ID.REMOVE_IGNORED, pyGlooxTag)


class SyncBlockItemTask(IQTask):
    __slots__ = ('_handlers',)

    def __init__(self):
        super(SyncBlockItemTask, self).__init__()
        block = blocking_cmd.BlockItemHandler().getFilterString()
        unblock = blocking_cmd.UnblockItemHandler().getFilterString()
        self._handlers = {block: AddBlockItemTask,
         unblock: RemoveBlockItemTask}

    def set(self, pyGlooxTag):
        for xPath, clazz in self._handlers.iteritems():
            result = pyGlooxTag.filterXPath(xPath)
            if not result:
                continue
            jid = result[0].findAttribute('jid')
            if jid:
                return clazz(ContactJID(jid)).set(pyGlooxTag)

        return self._result
