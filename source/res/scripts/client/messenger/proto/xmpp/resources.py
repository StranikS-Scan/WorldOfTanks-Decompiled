# Embedded file name: scripts/client/messenger/proto/xmpp/resources.py
from constants import IGR_TYPE
from gui.shared.utils.decorators import ReprInjector
from messenger.m_constants import USER_TAG
from messenger.proto.xmpp.gloox_constants import PRESENCES_ORDER, PRESENCE

@ReprInjector.simple('priority', 'message', 'presence')

class Resource(object):
    __slots__ = ('priority', 'message', 'presence')

    def __init__(self, priority = 0, message = 0, presence = PRESENCE.UNAVAILABLE):
        super(Resource, self).__init__()
        self.priority = priority
        self.message = message
        self.presence = presence

    def getTags(self):
        tags = set()
        if self.presence == PRESENCE.DND:
            tags.add(USER_TAG.PRESENCE_DND)
        return tags

    def replace(self, other):
        return other


@ReprInjector.withParent('igrID', 'igrRoomID')

class ResourceWithIGR(Resource):
    __slots__ = ('igrID', 'igrRoomID')

    def __init__(self, igrID = IGR_TYPE.NONE, igrRoomID = 0):
        super(ResourceWithIGR, self).__init__()
        self.igrID = igrID
        self.igrRoomID = igrRoomID

    def getTags(self):
        tags = super(ResourceWithIGR, self).getTags()
        if self.igrID == IGR_TYPE.BASE:
            tags.add(USER_TAG.IGR_BASE)
        elif self.igrID == IGR_TYPE.PREMIUM:
            tags.add(USER_TAG.IGR_PREMIUM)
        return tags

    def replace(self, other):
        if isinstance(other, ResourceWithIGR):
            self.igrID = other.igrID
            self.igrRoomID = other.igrRoomID
        else:
            self.priority = other.priority
            self.message = other.message
            self.presence = other.presence
        return self


def priorityComparator(resource, other):
    if resource.presence ^ other.presence:
        result = cmp(PRESENCES_ORDER.index(resource.presence), PRESENCES_ORDER.index(other.presence))
    elif resource.priority ^ other.priority:
        result = cmp(other.priority, resource.priority)
    else:
        result = cmp(resource.name, other.name)
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
        if len(self.__resources) > 0 and self.__highest is None:
            self.__highest = sorted(self.__resources.values(), cmp=priorityComparator)[0]
        return self.__highest
