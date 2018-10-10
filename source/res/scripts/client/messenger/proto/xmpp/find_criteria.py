# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/proto/xmpp/find_criteria.py
from messenger.m_constants import PROTO_TYPE, USER_TAG
from messenger.proto.interfaces import IEntityFindCriteria
from messenger.proto.xmpp.gloox_constants import MESSAGE_TYPE
from messenger.proto.xmpp.xmpp_constants import XMPP_ITEM_TYPE

class ItemsFindCriteria(IEntityFindCriteria):
    __slots__ = ('__itemTypes',)

    def __init__(self, itemTypes):
        super(ItemsFindCriteria, self).__init__()
        self.__itemTypes = itemTypes

    def filter(self, entity):
        return entity.getProtoType() == PROTO_TYPE.XMPP and entity.getItemType() in self.__itemTypes


class GroupFindCriteria(ItemsFindCriteria):
    __slots__ = ('__groups',)

    def __init__(self, group):
        super(GroupFindCriteria, self).__init__(XMPP_ITEM_TYPE.ROSTER_ITEMS)
        self.__groups = {group}

    def filter(self, entity):
        return super(GroupFindCriteria, self).filter(entity) and entity.getGroups() & self.__groups


class RqFriendshipCriteria(IEntityFindCriteria):

    def filter(self, entity):
        if entity.getProtoType() == PROTO_TYPE.XMPP and entity.getItemType() in XMPP_ITEM_TYPE.SUB_PENDING_ITEMS:
            tags = entity.getTags()
            result = USER_TAG.SUB_PENDING_IN in tags and USER_TAG.WO_NOTIFICATION not in tags
        else:
            result = False
        return result


class MutedOnlyFindCriteria(IEntityFindCriteria):

    def filter(self, entity):
        return entity.getProtoType() == PROTO_TYPE.XMPP and entity.isMuted() and not entity.isIgnored()


class XMPPChannelFindCriteria(IEntityFindCriteria):

    def __init__(self, msgType=None):
        super(XMPPChannelFindCriteria, self).__init__()
        self.__msgType = msgType

    def filter(self, entity):
        return entity.getProtoType() == PROTO_TYPE.XMPP and (self.__msgType is None or entity.getMessageType() == self.__msgType)


class XMPPChannelByJIDFindCriteria(IEntityFindCriteria):

    def __init__(self, jid):
        super(XMPPChannelByJIDFindCriteria, self).__init__()
        self.__jid = str(jid)

    def filter(self, channel):
        return channel.getProtoType() == PROTO_TYPE.XMPP and channel.getID() == self.__jid


class XMPPChannelByNameFindCriteria(IEntityFindCriteria):

    def __init__(self, name):
        super(XMPPChannelByNameFindCriteria, self).__init__()
        self.__name = name

    def filter(self, channel):
        return channel.getProtoType() == PROTO_TYPE.XMPP and channel.getName() == self.__name


class XmppClanChannelCriteria(IEntityFindCriteria):

    def filter(self, channel):
        return channel.getProtoType() is PROTO_TYPE.XMPP and channel.getMessageType() == MESSAGE_TYPE.GROUPCHAT and channel.isClan()
