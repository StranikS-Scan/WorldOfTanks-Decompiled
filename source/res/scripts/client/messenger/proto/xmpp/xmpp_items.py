# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/proto/xmpp/xmpp_items.py
import time
from messenger.m_constants import USER_TAG as _TAG
from messenger.proto.xmpp.gloox_constants import PRESENCE, SUBSCRIPTION as _SUB, SUBSCRIPTION_NAMES as _SUB_NAMES
from messenger.proto.xmpp.jid import makeContactJID
from messenger.proto.xmpp.resources import ResourceDictionary
from messenger.proto.xmpp.xmpp_constants import XMPP_ITEM_TYPE

class ContactItem(object):
    """
    Base contact class. Represents a contact that is not friend, not blocked, etc.
    """
    __slots__ = ('_jid', '_sub', '_tags', '_trusted', '_resources')

    def __init__(self, jid, trusted=False, tags=None, resources=None):
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

    def isOnline(self, isOnlineInBW=False):
        return isOnlineInBW or self.getPresence() not in PRESENCE.OFFLINE

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
        return ContactItem(self._jid) if newItem is None else newItem

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
    """
    Represents a contact that is friend.
    """
    __slots__ = ('_groups', '_sub')

    def __init__(self, jid, groups=None, sub=None, resources=None, trusted=True):
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
        """
        Returns a new item that can replace the existing one based on the current state and the
        desired (given) new state.
        Note that the current item can be replaced with:
            - RosterBlockItem - when the friendship is added.
            - RosterTmpBlockItem - when the temporary block is added.
            - ContactItem - when the friendship is canceled.
        
        :param newItem: an instance of TmpBlockItem class if temporary block should be added or
                        an instance of BlockItem class if permanent block should be added or
                        an instance of ContactItem or None if friendship should be canceled.
        :return: RosterBlockItem, RosterTmpBlockItem or ContactItem.
        """
        if newItem:
            if newItem.getItemType() == XMPP_ITEM_TYPE.BLOCK_ITEM:
                return RosterBlockItem(self._jid, RosterItem(self._jid, sub=self._sub, groups=self._groups))
            if newItem.getItemType() == XMPP_ITEM_TYPE.TMP_BLOCK_ITEM:
                return RosterTmpBlockItem(self._jid, RosterItem(self._jid, sub=self._sub, groups=self._groups))
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
    """
    Represents a contact that is blocked permanently (added to the permanent XMPP ignore list).
    """

    def __init__(self, jid, trusted=True):
        super(BlockItem, self).__init__(jid, trusted, tags={_TAG.IGNORED})

    @classmethod
    def getItemType(cls):
        return XMPP_ITEM_TYPE.BLOCK_ITEM

    def isOnline(self, isOnlineInBW=False):
        return False

    def setTrusted(self, value):
        super(BlockItem, self).setTrusted(value)
        if not self._trusted:
            self._tags.add(_TAG.CACHED)
        else:
            self._tags.discard(_TAG.CACHED)

    def _setResource(self, jid, resource):
        pass


class TmpBlockItem(ContactItem):
    """
    Represents a contact that is temporary blocked (added to the temporary ignore list.)
    """

    def __init__(self, jid, trusted=True):
        super(TmpBlockItem, self).__init__(jid, trusted, tags={_TAG.IGNORED_TMP})

    @classmethod
    def getItemType(cls):
        return XMPP_ITEM_TYPE.TMP_BLOCK_ITEM

    def isOnline(self, isOnlineInBW=False):
        return super(TmpBlockItem, self).isOnline(isOnlineInBW)

    def setTrusted(self, value):
        super(TmpBlockItem, self).setTrusted(value)
        if not self._trusted:
            self._tags.add(_TAG.CACHED)
        else:
            self._tags.discard(_TAG.CACHED)

    def _setResource(self, jid, resource):
        pass


class RosterBlockItem(BlockItem):
    """
    Represents a roster contact (friend) that is blocked permanently.
    """
    __slots__ = ('_rosterItem',)

    def __init__(self, jid, rosterItem=None, trusted=True):
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


class RosterTmpBlockItem(TmpBlockItem):
    """
    Represents a roster contact (friend) that is temporary blocked.
    """
    __slots__ = ('_rosterItem',)

    def __init__(self, jid, rosterItem=None, trusted=True):
        super(RosterTmpBlockItem, self).__init__(jid, trusted)
        self._rosterItem = rosterItem or RosterItem(jid)

    @classmethod
    def getItemType(cls):
        return XMPP_ITEM_TYPE.ROSTER_TMP_BLOCK_ITEM

    def getTags(self):
        tags = super(RosterTmpBlockItem, self).getTags()
        tags.update(self._rosterItem.getTags())
        return tags

    def getRosterGroups(self):
        return self._rosterItem.getGroups()

    def getSubscription(self):
        return self._rosterItem.getSubscription()

    def update(self, **kwargs):
        super(RosterTmpBlockItem, self).update(**kwargs)
        self._rosterItem.update(**kwargs)

    def replace(self, newItem):
        """
        Returns a new item that can replace the existing one based on the current state and the
        desired (given) new state.
        Note that the current item can be replaced with:
            - TmpBlockItem - when the friendship is canceled.
            - RosterItem - when the temporary block is removed.
        
        :param newItem: None if temporary block should be removed or an instance of ContactItem
                        if friendship should be canceled.
        :return: TmpBlockItem or RosterItem item.
        """
        if newItem is None:
            newItem = self._rosterItem
        elif newItem.getItemType() == XMPP_ITEM_TYPE.EMPTY_ITEM:
            newItem = TmpBlockItem(self._jid, self.isTrusted())
        else:
            newItem = super(RosterTmpBlockItem, self).replace(newItem)
        return newItem


class SubPendingItem(ContactItem):
    """
    Represents a contact with an active friendship subscription(not approved friendship request).
    """
    __slots__ = ('_receivedAt',)

    def __init__(self, jid, trusted=True, tags=None, receivedAt=None):
        super(SubPendingItem, self).__init__(jid, trusted, tags)
        self._receivedAt = receivedAt or time.time()

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

    def replace(self, newItem):
        """
        Returns a new item that can replace the existing one based on the current state and the
        desired (given) new state.
        Note that the current item can be replaced with:
            - ContactItem - when the pending subscription is canceled.
            - SubPendingTmpBlockItem - when the temporary block is added.
        
        :param newItem: an instance of TmpBlockItem class if temporary block should be added or
                        an instance of ContactItem or None if pending subscription should be
                        canceled.
        :return: ContactItem or SubPendingTmpBlockItem item.
        """
        return SubPendingTmpBlockItem(self._jid, SubPendingItem(self._jid, trusted=self.isTrusted(), tags=self.getTags(), receivedAt=self.receivedAt())) if newItem and newItem.getItemType() == XMPP_ITEM_TYPE.TMP_BLOCK_ITEM else super(SubPendingItem, self).replace(newItem)


class SubPendingTmpBlockItem(TmpBlockItem):
    """
    Represents a contact with an active friendship subscription(not approved friendship request)
    that is temporary blocked (added to the tmp ignore list).
    """
    __slots__ = ('_pendingItem',)

    def __init__(self, jid, pendingItem=None, trusted=True):
        self._pendingItem = pendingItem or SubPendingItem(jid)
        super(SubPendingTmpBlockItem, self).__init__(jid, trusted)

    @classmethod
    def getItemType(cls):
        return XMPP_ITEM_TYPE.SUB_PENDING_TMP_BLOCK_ITEM

    def getTags(self):
        tags = super(SubPendingTmpBlockItem, self).getTags()
        tags.update(self._pendingItem.getTags())
        return tags

    def setTrusted(self, value):
        super(SubPendingTmpBlockItem, self).setTrusted(value)
        self._pendingItem.setTrusted(value)

    def update(self, **kwargs):
        super(SubPendingTmpBlockItem, self).update(**kwargs)
        self._pendingItem.update(**kwargs)

    def replace(self, newItem):
        """
        Returns a new item that can replace the existing one based on the current state and the
        desired (given) new state.
        Note that the current item can be replaced with:
            - TmpBlockItem - when the pending subscription is canceled.
            - SubPendingItem - when the temporary block is removed.
        
        :param newItem: None if temporary block should be removed or an instance of ContactItem
                        if pending subscription should be canceled.
        :return: TmpBlockItem or SubPendingItem item.
        """
        if newItem is None:
            newItem = self._pendingItem
        elif newItem.getItemType() == XMPP_ITEM_TYPE.EMPTY_ITEM:
            newItem = TmpBlockItem(self._jid, self.isTrusted())
        else:
            newItem = super(SubPendingTmpBlockItem, self).replace(newItem)
        return newItem

    def receivedAt(self):
        return self._pendingItem.receivedAt()


_SUPPORTED_ITEMS = (RosterItem,
 BlockItem,
 TmpBlockItem,
 SubPendingItem,
 SubPendingTmpBlockItem,
 RosterBlockItem,
 RosterTmpBlockItem)
_SUPPORTED_ITEM_TYPE_TO_CLASS = dict(((clazz.getItemType(), clazz) for clazz in _SUPPORTED_ITEMS))

def createItem(databaseID, itemType=XMPP_ITEM_TYPE.EMPTY_ITEM, trusted=True):
    jid = makeContactJID(databaseID)
    if itemType in _SUPPORTED_ITEM_TYPE_TO_CLASS:
        clazz = _SUPPORTED_ITEM_TYPE_TO_CLASS[itemType]
        item = clazz(jid, trusted=trusted)
    else:
        item = ContactItem(jid)
    return item
