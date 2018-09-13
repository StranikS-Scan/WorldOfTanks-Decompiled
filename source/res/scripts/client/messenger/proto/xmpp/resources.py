# Embedded file name: scripts/client/messenger/proto/xmpp/resources.py
from messenger.proto.xmpp.gloox_wrapper import PRESENCES_ORDER, PRESENCES_NAMES
__author__ = 'd_dichkovsky'

class Resource(object):

    def __init__(self, name, priority, message, presence):
        self.__name = name
        self.__priority = priority
        self.__message = message
        self.__presence = presence

    @property
    def name(self):
        """
        Resource name.
        The name MUST be unique in scope of contact's bare JID (i.e.
        "user@domain/resource" is used as globally unique key).
        """
        return self.__name

    @property
    def priority(self):
        """
        Resource priority (an integer number).
        Exact value depends solely on contact's choice.
        """
        return self.__priority

    @priority.setter
    def priority(self, value):
        self.__priority = value

    @property
    def message(self):
        """Status message. Can be arbitrary text."""
        return self.__message

    @message.setter
    def message(self, value):
        self.__message = value

    @property
    def presence(self):
        """
        Contact's presence at given resource.
        One of PRESENCE_* values is returned.
        """
        return self.__presence

    @presence.setter
    def presence(self, value):
        self.__presence = value

    def update(self, priority, status, presence):
        self.__priority = priority
        self.__message = status
        self.__presence = presence

    def __cmp__(self, other):
        if self.presence ^ other.presence:
            result = cmp(PRESENCES_ORDER.index(self.presence), PRESENCES_ORDER.index(other.presence))
        elif self.priority ^ other.priority:
            result = cmp(other.priority, self.priority)
        else:
            result = cmp(self.name, other.name)
        return result

    def __repr__(self):
        return 'Resource(name={0}, priority={1}, presence={2})'.format(self.__name, self.__priority, PRESENCES_NAMES[self.__presence])


class ResourceDictionary(object):

    def __init__(self):
        super(ResourceDictionary, self).__init__()
        self.__resources = {}

    def clear(self):
        self.__resources.clear()

    def update(self, name, priority, status, presence):
        if name not in self.__resources:
            self.__resources[name] = Resource(name, priority, status, presence)
        else:
            self.__resources[name].update(priority, status, presence)
        return True

    def remove(self, name):
        result = False
        if name in self.__resources:
            self.__resources.pop(name)
            result = True
        return result

    def priority(self):
        result = None
        if len(self.__resources) > 0:
            result = sorted(self.__resources.values())[0]
        return result
