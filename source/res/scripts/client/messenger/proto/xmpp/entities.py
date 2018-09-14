# Embedded file name: scripts/client/messenger/proto/xmpp/entities.py
from messenger.m_constants import PROTO_TYPE, USER_TAG, GAME_ONLINE_STATUS
from messenger.proto.entities import UserEntity, ChannelEntity, MemberEntity
from messenger.proto.xmpp.gloox_constants import MESSAGE_TYPE
from messenger.proto.xmpp.wrappers import XMPPChannelData
from messenger.proto.xmpp.xmpp_items import createItem

class XMPPUserEntity(UserEntity):
    __slots__ = ('_item', '_gos')

    def __init__(self, databaseID, name = None, tags = None, clanInfo = None, item = None):
        super(XMPPUserEntity, self).__init__(databaseID, name, tags, clanInfo)
        self._item = item or createItem(databaseID)
        self._gos = GAME_ONLINE_STATUS.UNDEFINED

    def __repr__(self):
        return 'XMPPUserEntity(dbID={0!r:s}, fullName={1:>s}, tags={2!r:s}, item={3!r:s}, isOnline={4!r:s}, clanInfo={5!r:s})'.format(self._databaseID, self.getFullName(), self.getTags(), self._item, self.isOnline(), self._clanInfo)

    def getResourceID(self):
        return self._item.getResources().getHighestPriorityID()

    def getClientInfo(self):
        return self._item.getClientInfo()

    def clear(self):
        self._gos = GAME_ONLINE_STATUS.UNDEFINED
        super(XMPPUserEntity, self).clear()

    def getPersistentState(self):
        state = None
        tags = USER_TAG.filterToStoreTags(self.getTags())
        if self._databaseID and (self._item.isTrusted() or tags):
            state = (self._name, self._item.getItemType(), tags if tags else None)
        return state

    def setPersistentState(self, state):
        result = False
        if len(state) == 3:
            self._name, itemType, tags = state
            self._item = createItem(self._databaseID, itemType, trusted=False)
            if tags:
                self.addTags(tags)
            result = True
        return result

    def getProtoType(self):
        return PROTO_TYPE.XMPP

    def setSharedProps(self, other):
        result = super(XMPPUserEntity, self).setSharedProps(other)
        if result and other.getProtoType() == PROTO_TYPE.XMPP:
            if USER_TAG.CACHED in self.getTags():
                self.update(name=other.getName(), item=other.getItem())
            elif USER_TAG.CACHED in other.getTags() and other.isMuted():
                self.addTags({USER_TAG.MUTED})
        if USER_TAG.filterSharedTags(self._tags):
            self._gos = other.getGOS()
        return result

    def getTags(self):
        tags = super(XMPPUserEntity, self).getTags()
        tags.update(self._item.getTags())
        return tags

    def removeTags(self, tags):
        super(XMPPUserEntity, self).removeTags(tags)
        if self._item.removeTags(tags):
            self._item = createItem(self._databaseID)

    def getGroups(self):
        return self._item.getGroups()

    def getGOS(self):
        return self._gos

    def isOnline(self):
        return self._item.isOnline(self._gos & GAME_ONLINE_STATUS.ONLINE > 0)

    def update(self, **kwargs):
        if 'item' in kwargs:
            self._item = self._item.replace(kwargs['item'])
        if 'gosBit' in kwargs and USER_TAG.filterSharedTags(self._tags):
            self._gos = GAME_ONLINE_STATUS.update(self._gos, kwargs['gosBit'])
        self._item.update(**kwargs)
        super(XMPPUserEntity, self).update(**kwargs)

    def getJID(self):
        return self._item.getJID()

    def getSubscription(self):
        return self._item.getSubscription()

    def getItemType(self):
        return self._item.getItemType()

    def getItem(self):
        return self._item


class _XMPPChannelEntity(ChannelEntity):
    __slots__ = ('_jid',)

    def __init__(self, jid, data):
        super(_XMPPChannelEntity, self).__init__(data)
        self._jid = jid

    def getID(self):
        return self._jid

    def getProtoType(self):
        return PROTO_TYPE.XMPP


class XMPPChatChannelEntity(_XMPPChannelEntity):
    __slots__ = ('_isStored',)

    def __init__(self, jid, name = ''):
        super(XMPPChatChannelEntity, self).__init__(str(jid), XMPPChannelData(name, MESSAGE_TYPE.CHAT))
        self._isStored = False

    def getPersistentState(self):
        state = None
        if self._isStored:
            state = tuple(self._data)
        return state

    def setPersistentState(self, state):
        if len(state) == 2:
            self._data = XMPPChannelData(*state)
            self._isStored = True
        else:
            self._isStored = False
        return self._isStored

    def isPrivate(self):
        return True

    def getName(self):
        return self._data.name

    def getFullName(self):
        return self.getName()

    def setStored(self, flag):
        self._isStored = flag

    def setJoined(self, isJoined):
        self._isJoined = isJoined
        self.onConnectStateChanged(self)

    def clear(self):
        self._isStored = False
        super(XMPPChatChannelEntity, self).clear()


class XMPPMucChannelEntity(_XMPPChannelEntity):

    def __init__(self, jid, name = ''):
        super(XMPPMucChannelEntity, self).__init__(str(jid), XMPPChannelData(name, MESSAGE_TYPE.GROUPCHAT))

    def getFullName(self):
        return self._data.name


class XMPPMemberEntity(MemberEntity):

    def getProtoType(self):
        return PROTO_TYPE.XMPP

    def setOnline(self, value):
        self.setStatus(value)

    def isOnline(self):
        return self.getStatus()
