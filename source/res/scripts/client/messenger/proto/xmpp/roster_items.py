# Embedded file name: scripts/client/messenger/proto/xmpp/roster_items.py
from collections import defaultdict
from debug_utils import LOG_DEBUG
from messenger.proto.xmpp.resources import ResourceDictionary
from messenger.proto.xmpp.gloox_wrapper import SUBSCRIPTION, PRESENCE
from messenger.proto.xmpp.gloox_wrapper import SUBSCRIPTION_NAMES

class RosterItem(object):

    def __init__(self, jid, name = 'Unknown', groups = None, subscriptionTo = SUBSCRIPTION.OFF, subscriptionFrom = SUBSCRIPTION.OFF):
        self.__jid = jid
        self.__name = name
        self.__groups = groups or set()
        self.__subscriptionTo = subscriptionTo
        self.__subscriptionFrom = subscriptionFrom
        self.__resources = ResourceDictionary()

    def clear(self):
        self.__resources.clear()

    def update(self, name, groups, to, from_):
        self.__name = name
        self.__groups = groups
        self.__subscriptionTo = to
        self.__subscriptionFrom = from_

    @property
    def jid(self):
        """Contact bare JID, i.e. in format "user@domain" (without resource)."""
        return self.__jid

    @property
    def resources(self):
        return self.__resources

    @property
    def presence(self):
        """
        Returns presence state for RosterItem, basing on registered resources
        (top priority resource is used)
        """
        result = PRESENCE.UNKNOWN
        resource = self.__resources.priority()
        if resource is not None:
            result = resource.presence
        return result

    @property
    def name(self):
        """Custom contact name chosen by user."""
        return self.__name

    @name.setter
    def name(self, value):
        self.__name = value

    @property
    def groups(self):
        """List of groups (strings) which contact belongs to."""
        return self.__groups

    @groups.setter
    def groups(self, value):
        self.__groups = value or []

    @property
    def subscriptionTo(self):
        """
        Presence subscription status in direction "contact TO user".
        One of SUBSCRIPTION_* values is returned.
        """
        return self.__subscriptionTo

    @subscriptionTo.setter
    def subscriptionTo(self, value):
        self.__subscriptionTo = value

    @property
    def subscriptionFrom(self):
        """
        Presence subscription status in direction "FROM user to contact".
        One of SUBSCRIPTION_* values is returned.
        """
        return self.__subscriptionFrom

    @subscriptionFrom.setter
    def subscriptionFrom(self, value):
        self.__subscriptionFrom = value

    def __repr__(self):
        return 'RosterItem(jid={0}, name={1}, groups={2}, resource={3}, to/from={4}/{5})'.format(self.__jid, self.__name, self.__groups, self.__resources.priority(), SUBSCRIPTION_NAMES[self.__subscriptionTo], SUBSCRIPTION_NAMES[self.__subscriptionFrom])


class RosterItemStorage(defaultdict):

    def __missing__(self, key):
        self[key] = value = RosterItem(key)
        return value

    def hasItem(self, jid):
        return jid in self

    def log(self):
        result = ['XMPPClient:RosterItemsLog, Client is connected to XMPP.XMPP roster is:']
        for jid, item in self.iteritems():
            result.append(repr(item))

        LOG_DEBUG('\n'.join(result))
