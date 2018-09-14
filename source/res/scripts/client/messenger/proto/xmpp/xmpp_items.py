# Embedded file name: scripts/client/messenger/proto/xmpp/xmpp_items.py
import time
from messenger.m_constants import USER_TAG as _TAG
from messenger.proto.xmpp.gloox_constants import PRESENCE, SUBSCRIPTION as _SUB, SUBSCRIPTION_NAMES as _SUB_NAMES
from messenger.proto.xmpp.jid import makeContactJID
from messenger.proto.xmpp.resources import ResourceDictionary
from messenger.proto.xmpp.xmpp_constants import XMPP_ITEM_TYPE

class ContactItem(object):
    __slots__ = ('_jid', '_sub', '_tags', '_trusted', '_resources')

    def __init__(self, jid, trusted = False, tags = None, resources = None):
        self._jid = jid
        self._sub = (_SUB.OFF, _SUB.OFF)
        self._tags = tags or set()
        self._resources = resources or ResourceDictionary()
        self.setTrusted(trusted)

    def __repr__(self):
        return '{0}({1})'.format(self.__class__.__name__, self._jid)

    @classmethod
    def getItemType(self):
        return XMPP_ITEM_TYPE.EMPTY_ITEM

    def clear(self):
        self._resources.clear()

    def isTrusted(self):
        return self._trusted

    def setTrusted(self, value):
        self._trusted = value

    def getJID(self):
        return self._jid

    def getTags(self):
        return self._tags

    def removeTags(self, tags):
        return self.getItemType() != XMPP_ITEM_TYPE.EMPTY_ITEM and not self._trusted and _TAG.CACHED in tags

    def isOnline(self, isOnlineInBW = False):
        return isOnlineInBW or self.getPresence() not in [PRESENCE.UNAVAILABLE, PRESENCE.UNKNOWN]

    def getPresence(self):
        resource = self._resources.getHighestPriority()
        if resource is not None:
            result = resource.presence
        else:
            result = PRESENCE.UNKNOWN
        return result

    def getResources(self):
        return self._resources

    def getGroups(self):
        return set()

    def getSubscription(self):
        return self._sub

    def getSubscriptionTo(self):
        return self._sub[0]

    def getSubscriptionFrom(self):
        return self._sub[1]

    def getClientInfo(self):
        resource = self._resources.getHighestPriority()
        if resource is not None:
            clientInfo = resource.getClientInfo()
        else:
            clientInfo = None
        return clientInfo

    def update(self, **kwargs):
        if 'trusted' in kwargs:
            self.setTrusted(kwargs['trusted'])
        if 'jid' in kwargs and 'resource' in kwargs:
            jid = kwargs['jid']
            resource = kwargs['resource']
            if resource:
                self._setResource(jid, resource)
            else:
                self._removeResource(jid)

    def replace(self, newItem):
        if newItem is None:
            return ContactItem(self._jid)
        else:
            return newItem

    def _setResource(self, jid, resource):
        self._resources.setResource(jid, resource)

    def _removeResource(self, jid):
        self._resources.removeResource(jid)


_SUB_TAGS = {_TAG.SUB_NONE,
 _TAG.SUB_PENDING_IN,
 _TAG.SUB_PENDING_OUT,
 _TAG.SUB_TO,
 _TAG.SUB_FROM}
_SUB_TO_TAGS = {(_SUB.OFF, _SUB.OFF): {_TAG.SUB_NONE},
 (_SUB.ON, _SUB.OFF): {_TAG.SUB_TO},
 (_SUB.OFF, _SUB.ON): {_TAG.SUB_FROM},
 (_SUB.ON, _SUB.ON): {_TAG.SUB_TO, _TAG.SUB_FROM},
 (_SUB.PENDING, _SUB.OFF): {_TAG.SUB_PENDING_OUT},
 (_SUB.PENDING, _SUB.ON): {_TAG.SUB_PENDING_OUT, _TAG.SUB_FROM},
 (_SUB.OFF, _SUB.PENDING): {_TAG.SUB_PENDING_IN},
 (_SUB.ON, _SUB.PENDING): {_TAG.SUB_PENDING_IN, _TAG.SUB_TO},
 (_SUB.PENDING, _SUB.PENDING): {_TAG.SUB_PENDING_IN, _TAG.SUB_PENDING_OUT}}

class RosterItem(ContactItem):
    __slots__ = ('_groups', '_sub')

    def __init__(self, jid, groups = None, sub = None, resources = None, trusted = True):
        super(RosterItem, self).__init__(jid, trusted=trusted, tags={_TAG.FRIEND}, resources=resources)
        self._groups = groups or set()
        self._sub = sub or (_SUB.OFF, _SUB.OFF)
        self._updateSubTags()

    def __repr__(self):
        return 'RosterItem(jid={0}, groups={1}, resource={2}, sub={3}/{4})'.format(self._jid, self._groups, self._resources.getHighestPriority(), _SUB_NAMES[self._sub[0]], _SUB_NAMES[self._sub[1]])

    @classmethod
    def getItemType(cls):
        return XMPP_ITEM_TYPE.ROSTER_ITEM

    def update(self, **kwargs):
        super(RosterItem, self).update(**kwargs)
        if 'groups' in kwargs:
            self._groups = kwargs['groups']
        if 'sub' in kwargs:
            self._sub = kwargs['sub']
            self._updateSubTags()

    def replace(self, newItem):
        if newItem and newItem.getItemType() == XMPP_ITEM_TYPE.BLOCK_ITEM:
            return RosterBlockItem(self._jid, RosterItem(self._jid, sub=self._sub, groups=self._groups))
        else:
            return super(RosterItem, self).replace(newItem)

    def getJID(self):
        return self._jid

    def getGroups(self):
        return self._groups.copy()

    def getPresence(self):
        result = PRESENCE.UNKNOWN
        if self._sub[0] == _SUB.ON:
            result = super(RosterItem, self).getPresence()
        return result

    def getTags(self):
        tags = set()
        tags.update(super(RosterItem, self).getTags())
        if self._sub[0] == _SUB.ON:
            tags.update(self._resources.getTags())
        return tags

    def setTrusted(self, value):
        super(RosterItem, self).setTrusted(value)
        if not self._trusted:
            self._tags.add(_TAG.CACHED)
        else:
            self._tags.discard(_TAG.CACHED)

    def _updateSubTags(self):
        self._tags = self._tags.difference(_SUB_TAGS)
        if self._sub in _SUB_TO_TAGS:
            self._tags.update(_SUB_TO_TAGS[self._sub])


class BlockItem(ContactItem):

    def __init__(self, jid, trusted = True):
        super(BlockItem, self).__init__(jid, trusted, tags={_TAG.IGNORED})

    @classmethod
    def getItemType(cls):
        return XMPP_ITEM_TYPE.BLOCK_ITEM

    def isOnline(self, isOnlineInBW = False):
        return False

    def setTrusted(self, value):
        super(BlockItem, self).setTrusted(value)
        if not self._trusted:
            self._tags.add(_TAG.CACHED)
        else:
            self._tags.discard(_TAG.CACHED)

    def _setResource(self, jid, resource):
        pass


class RosterBlockItem(BlockItem):
    __slots__ = ('_rosterItem',)

    def __init__(self, jid, rosterItem = None, trusted = True):
        super(RosterBlockItem, self).__init__(jid, trusted)
        self._rosterItem = rosterItem or RosterItem(jid)

    @classmethod
    def getItemType(cls):
        return XMPP_ITEM_TYPE.ROSTER_BLOCK_ITEM

    def getRosterGroups(self):
        return self._rosterItem.getGroups()

    def getSubscription(self):
        return self._rosterItem.getSubscription()

    def update(self, **kwargs):
        super(RosterBlockItem, self).update(**kwargs)
        self._rosterItem.update(**kwargs)

    def replace(self, newItem):
        if newItem is None:
            newItem = self._rosterItem
        else:
            newItem = super(RosterBlockItem, self).replace(newItem)
        return newItem


class SubPendingItem(ContactItem):
    __slots__ = ('_receivedAt',)

    def __init__(self, jid, trusted = True, tags = None):
        super(SubPendingItem, self).__init__(jid, trusted, tags)
        self._receivedAt = time.time()

    @classmethod
    def getItemType(cls):
        return XMPP_ITEM_TYPE.SUB_PENDING

    def setTrusted(self, value):
        super(SubPendingItem, self).setTrusted(value)
        if self._trusted:
            self._tags = {_TAG.SUB_PENDING_IN}
        else:
            self._tags = {_TAG.CACHED}

    def receivedAt(self):
        return self._receivedAt


_SUPPORTED_ITEMS = (RosterItem,
 BlockItem,
 SubPendingItem,
 RosterBlockItem)
_SUPPORTED_ITEM_TYPE_TO_CLASS = dict(((clazz.getItemType(), clazz) for clazz in _SUPPORTED_ITEMS))

def createItem(databaseID, itemType = XMPP_ITEM_TYPE.EMPTY_ITEM, trusted = True):
    jid = makeContactJID(databaseID)
    if itemType in _SUPPORTED_ITEM_TYPE_TO_CLASS:
        clazz = _SUPPORTED_ITEM_TYPE_TO_CLASS[itemType]
        item = clazz(jid, trusted=trusted)
    else:
        item = ContactItem(jid)
    return item
