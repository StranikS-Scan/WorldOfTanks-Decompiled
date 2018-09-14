# Embedded file name: scripts/client/messenger/proto/xmpp/resources.py
from constants import IGR_TYPE, WG_GAMES
from gui.shared.utils.decorators import ReprInjector
from messenger.m_constants import USER_TAG
from messenger.proto.xmpp.gloox_constants import PRESENCES_ORDER, PRESENCE
from messenger.proto.xmpp.wrappers import WGExtsInfo
from messenger import g_settings

@ReprInjector.simple('priority', 'message', 'presence', ('__wgExts', 'exts'))

class Resource(object):
    __slots__ = ('priority', 'message', 'presence', '__wgExts', '__order')

    def __init__(self, priority = 0, message = 0, presence = PRESENCE.UNAVAILABLE, wgExts = None):
        super(Resource, self).__init__()
        self.priority = priority
        self.message = message
        self.presence = presence
        self.__wgExts = wgExts or WGExtsInfo(None, None, None)
        self.__order = PRESENCES_ORDER.index(self.presence)
        return

    def getTags(self):
        tags = set()
        if self.presence == PRESENCE.DND:
            tags.add(USER_TAG.PRESENCE_DND)
        info = self.__wgExts.client
        if info:
            if info.igrID == IGR_TYPE.BASE:
                tags.add(USER_TAG.IGR_BASE)
            elif info.igrID == IGR_TYPE.PREMIUM:
                tags.add(USER_TAG.IGR_PREMIUM)
        info = self.__wgExts.ban
        if info and info.isBanned(game=WG_GAMES.TANKS):
            tags.add(USER_TAG.BAN_CHAT)
        return tags

    def getClientInfo(self):
        return self.__wgExts.client

    def getClanInfo(self):
        return self.__wgExts.clan

    def getBanInfo(self):
        return self.__wgExts.ban

    def getOrder(self):
        return self.__order

    def replace(self, other):
        return other


def priorityComparator(resItem, otherItem):
    resource = resItem[1]
    other = otherItem[1]
    if resource.presence ^ other.presence:
        result = cmp(PRESENCES_ORDER.index(resource.presence), PRESENCES_ORDER.index(other.presence))
    elif resource.priority ^ other.priority:
        result = cmp(other.priority, resource.priority)
    else:
        result = 0
    return result


class ResourceDictionary(object):
    __slots__ = ('__resources', '__highest')

    def __init__(self):
        super(ResourceDictionary, self).__init__()
        self.__resources = {}
        self.__highest = None
        return

    def clear(self):
        self.__resources.clear()
        self.__highest = None
        return

    def setResource(self, jid, resource):
        name = jid.getResource()
        if name in self.__resources:
            old = self.__resources[name]
            self.__resources[name] = old.replace(resource)
        else:
            self.__resources[name] = resource
        self.__highest = None
        return

    def removeResource(self, jid):
        result = False
        name = jid.getResource()
        if name in self.__resources:
            self.__resources.pop(name)
            self.__highest = None
            result = True
        return result

    def getTags(self):
        resource = self.getHighestPriority()
        if resource:
            return resource.getTags()
        else:
            return set()

    def isEmpty(self):
        return not self.__resources

    def getHighestPriority(self):
        self.__initHighestData()
        if self.__highest:
            return self.__highest[1]
        else:
            return None

    def getHighestPriorityID(self):
        self.__initHighestData()
        if self.__highest:
            return self.__highest[0]
        else:
            return None

    def __initHighestData(self):
        if len(self.__resources) > 0 and self.__highest is None:
            wotId = g_settings.server.XMPP.resource
            if wotId in self.__resources:
                self.__highest = (wotId, self.__resources[wotId])
            elif self.__highest is None:
                self.__highest = sorted(self.__resources.items(), cmp=priorityComparator)[0]
        return
