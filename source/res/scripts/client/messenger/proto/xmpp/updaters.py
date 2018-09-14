# Embedded file name: scripts/client/messenger/proto/xmpp/updaters.py
from ConnectionManager import connectionManager
from debug_utils import LOG_DEBUG
from messenger import g_settings
from messenger.m_constants import PROTO_TYPE, USER_ROSTER_ACTION
from messenger.proto.bw.find_criteria import BWFriendFindCriteria
from messenger.proto.events import g_messengerEvents
from messenger.proto.interfaces import IEntityFindCriteria
from messenger.proto.xmpp.log_output import CLIENT_LOG_AREA, g_logOutput
from messenger.proto.xmpp.roster_items import RosterItem
from messenger.proto.xmpp.gloox_wrapper import GLOOX_EVENT, ClientEventsHandler
from messenger.proto.xmpp.gloox_wrapper import SUBSCRIPTION, PRESENCE
from messenger.proto.xmpp.jid import ContactBareJID
from messenger.storage import storage_getter, dyn_storage_getter

class _BW_ROSTER_GROUPS(object):
    FRIENDS = 'bw_friends'
    IGNORED = 'bw_ignored'
    MUTED = 'bw_muted'


GROUPS_SYNC_ENABLED = False

class _BWRosterFindCriteria(IEntityFindCriteria):

    def filter(self, user):
        return user.getRoster() != 0 or user.isCurrentPlayer()


class RosterUpdater(ClientEventsHandler):

    def __init__(self):
        super(RosterUpdater, self).__init__()
        self.__isBWRosterReceived = False

    @storage_getter('users')
    def usersStorage(self):
        return None

    @dyn_storage_getter('xmppRoster')
    def xmppRoster(self):
        return None

    def clear(self):
        self.__isBWRosterReceived = False

    def registerHandlers(self):
        client = self.client()
        users = g_messengerEvents.users
        users.onUsersRosterReceived += self.__me_onRosterReceived
        users.onUserRosterChanged += self.__me_onRosterUpdate
        client.registerHandler(GLOOX_EVENT.LOGIN, self.__handleLogin)
        client.registerHandler(GLOOX_EVENT.ROSTER_ITEM_SET, self.__handleRosterItemSet)
        client.registerHandler(GLOOX_EVENT.ROSTER_ITEM_REMOVED, self.__handleRosterItemRemoved)
        client.registerHandler(GLOOX_EVENT.ROSTER_RESOURCE_ADDED, self.__handleRosterResourceAdded)
        client.registerHandler(GLOOX_EVENT.ROSTER_RESOURCE_REMOVED, self.__handleRosterResourceRemoved)
        client.registerHandler(GLOOX_EVENT.SUBSCRIPTION_REQUEST, self.__handleSubscriptionRequest)

    def unregisterHandlers(self):
        client = self.client()
        users = g_messengerEvents.users
        users.onUsersRosterReceived -= self.__me_onRosterReceived
        users.onUserRosterChanged -= self.__me_onRosterUpdate
        client.unregisterHandler(GLOOX_EVENT.LOGIN, self.__handleLogin)
        client.unregisterHandler(GLOOX_EVENT.ROSTER_ITEM_SET, self.__handleRosterItemSet)
        client.unregisterHandler(GLOOX_EVENT.ROSTER_ITEM_REMOVED, self.__handleRosterItemRemoved)
        client.unregisterHandler(GLOOX_EVENT.ROSTER_RESOURCE_ADDED, self.__handleRosterResourceAdded)
        client.unregisterHandler(GLOOX_EVENT.ROSTER_RESOURCE_REMOVED, self.__handleRosterResourceRemoved)
        client.unregisterHandler(GLOOX_EVENT.SUBSCRIPTION_REQUEST, self.__handleSubscriptionRequest)

    def sync(self):
        if self.__isBWRosterReceived and self.client().isConnected():
            g_logOutput.debug(CLIENT_LOG_AREA.SYNC, 'Syncing XMPP rosters from BW')
            domain = g_settings.server.XMPP.domain
            contacts = set()
            for user in self.usersStorage.getList(_BWRosterFindCriteria()):
                jid = ContactBareJID()
                jid.setNode(user.getID())
                jid.setDomain(domain)
                contacts.add(jid)
                if user.isCurrentPlayer():
                    self.xmppRoster[jid].name = user.getName()
                    continue
                groups = self.__getBWRosterGroups(user)
                if self.xmppRoster.hasItem(jid):
                    if GROUPS_SYNC_ENABLED and groups ^ self.xmppRoster[jid].groups:
                        self.__setContactToXmppRoster(jid, user.getName(), groups)
                    if self.xmppRoster[jid].subscriptionTo == SUBSCRIPTION.OFF:
                        self.__setSubscribeTo(jid)
                else:
                    self.__addContactToXmppRoster(jid, user.getName(), groups)

            toRemove = set(self.xmppRoster.keys()).difference(contacts)
            for jid in toRemove:
                contact = self.xmppRoster[jid]
                if contact.subscriptionFrom != SUBSCRIPTION.OFF:
                    if contact.subscriptionTo == SUBSCRIPTION.ON:
                        self.__removeSubscribeTo(jid)
                else:
                    self.__removeContactFromXmppRoster(jid)

    def __getBWRosterGroups(self, user):
        groups = set()
        if user.isFriend():
            groups.add(_BW_ROSTER_GROUPS.FRIENDS)
        elif user.isIgnored():
            groups.add(_BW_ROSTER_GROUPS.IGNORED)
        if user.isMuted():
            groups.add(_BW_ROSTER_GROUPS.MUTED)
        return groups

    def __handleLogin(self):
        self.sync()

    def __handleRosterItemSet(self, jid, name, groups, to, from_):
        if self.__isBWRosterReceived:
            user = self.usersStorage.getUser(jid.getDatabaseID())
            if user or from_ != SUBSCRIPTION.OFF:
                self.__addToLocalXmppRoster(jid, name, groups, to, from_)
            else:
                self.__removeContactFromXmppRoster(jid)
        else:
            self.__addToLocalXmppRoster(jid, name, groups, to, from_)

    def __handleRosterItemRemoved(self, jid):
        if self.__isBWRosterReceived:
            user = self.usersStorage.getUser(jid.getDatabaseID())
            if user and user.getRoster():
                self.__addContactToXmppRoster(jid, user.getName(), self.__getBWRosterGroups(user))
            else:
                self.__removeFromLocalXmppRoster(jid)
        else:
            self.__removeFromLocalXmppRoster(jid)

    def __handleRosterResourceAdded(self, jid, priority, status, presence):
        if jid:
            self.xmppRoster[jid.getBareJID()].resources.update(jid.getResource(), priority, status, presence)

    def __handleRosterResourceRemoved(self, jid):
        if jid:
            result = self.xmppRoster[jid.getBareJID()].resources.remove(jid.getResource())
            if not result:
                g_logOutput.debug(CLIENT_LOG_AREA.SYNC, 'Resource is not in list', jid)

    def __handleSubscriptionRequest(self, jid, _):
        self.client().setSubscribeFrom(jid)

    def __me_onRosterReceived(self):
        g_logOutput.debug(CLIENT_LOG_AREA.SYNC, 'BW roster received')
        self.__isBWRosterReceived = True
        self.sync()

    def __me_onRosterUpdate(self, actionIdx, user):
        groups = self.__getBWRosterGroups(user)
        databaseID = user.getID()
        g_logOutput.debug(CLIENT_LOG_AREA.SYNC, 'BW roster update', groups, user)
        jid = ContactBareJID()
        jid.setNode(databaseID)
        jid.setDomain(g_settings.server.XMPP.domain)
        hasItem = self.xmppRoster.hasItem(jid)
        if len(groups):
            if hasItem:
                if GROUPS_SYNC_ENABLED and groups ^ self.xmppRoster[jid].groups:
                    self.__setContactToXmppRoster(jid, user.getName(), groups)
                self.__setSubscribeTo(jid)
            else:
                self.__addContactToXmppRoster(jid, user.getName(), groups)
        elif hasItem:
            self.__removeSubscribeTo(jid)
        if actionIdx == USER_ROSTER_ACTION.RemoveFromFriend and g_settings.server.useToShowOnline(PROTO_TYPE.XMPP) and not self.usersStorage.isClanMember(databaseID):
            user.update(isOnline=False)

    def __addToLocalXmppRoster(self, jid, name, groups, to, from_):
        if self.xmppRoster.hasItem(jid):
            g_logOutput.debug(CLIENT_LOG_AREA.SYNC, 'Updating item in local XMPP roster', jid, name, groups, to, from_)
            self.xmppRoster[jid].update(name, groups, to, from_)
        else:
            g_logOutput.debug(CLIENT_LOG_AREA.SYNC, 'Adding item to local XMPP roster', jid, name, groups, to, from_)
            self.xmppRoster[jid] = RosterItem(jid, name, groups, to, from_)

    def __removeFromLocalXmppRoster(self, jid):
        if self.xmppRoster.hasItem(jid):
            g_logOutput.debug(CLIENT_LOG_AREA.SYNC, 'Contact is removed from local XMPP roster', jid, self.xmppRoster[jid].name)
            self.xmppRoster.pop(jid).clear()
        else:
            g_logOutput.warning(CLIENT_LOG_AREA.SYNC, 'Roster item is not found', jid)

    def __addContactToXmppRoster(self, jid, userName = 'Unknown', groups = None):
        if not GROUPS_SYNC_ENABLED:
            groups = None
        client = self.client()
        g_logOutput.debug(CLIENT_LOG_AREA.SYNC, 'Adds contact from BW roster and sends request to add subscription', jid, userName, groups)
        client.setContactToRoster(jid, userName, groups)
        client.setSubscribeTo(jid)
        return

    def __setContactToXmppRoster(self, jid, userName = 'Unknown', groups = None):
        if not GROUPS_SYNC_ENABLED:
            groups = None
        g_logOutput.debug(CLIENT_LOG_AREA.SYNC, 'Adds contact from BW roster', jid, userName, groups)
        self.client().setContactToRoster(jid, userName, groups)
        return

    def __setSubscribeTo(self, jid):
        g_logOutput.debug(CLIENT_LOG_AREA.SYNC, 'Sends request to add subscription', jid)
        self.client().setSubscribeTo(jid)

    def __removeSubscribeTo(self, jid):
        g_logOutput.debug(CLIENT_LOG_AREA.SYNC, 'Sends request to remove subscription', jid)
        self.client().removeSubscribeTo(jid)

    def __removeContactFromXmppRoster(self, jid):
        g_logOutput.debug(CLIENT_LOG_AREA.SYNC, 'Removes contact from XMPP roster', jid)
        client = self.client()
        client.removeSubscribeTo(jid)
        client.removeContactFromRoster(jid)


class OnlineStatusUpdater(ClientEventsHandler):

    @storage_getter('users')
    def usersStorage(self):
        return None

    @dyn_storage_getter('xmppRoster')
    def xmppRoster(self):
        return None

    def registerHandlers(self):
        client = self.client()
        users = g_messengerEvents.users
        users.onUsersRosterReceived += self.__me_onRosterReceived
        client.registerHandler(GLOOX_EVENT.DISCONNECTED, self.__handleDisconnect)
        client.registerHandler(GLOOX_EVENT.ROSTER_RESOURCE_ADDED, self.__handleRosterResourceAdded)
        client.registerHandler(GLOOX_EVENT.ROSTER_RESOURCE_REMOVED, self.__handleRosterResourceRemoved)

    def unregisterHandlers(self):
        client = self.client()
        users = g_messengerEvents.users
        users.onUsersRosterReceived -= self.__me_onRosterReceived
        client.unregisterHandler(GLOOX_EVENT.DISCONNECTED, self.__handleDisconnect)
        client.unregisterHandler(GLOOX_EVENT.ROSTER_RESOURCE_ADDED, self.__handleRosterResourceAdded)
        client.unregisterHandler(GLOOX_EVENT.ROSTER_RESOURCE_REMOVED, self.__handleRosterResourceRemoved)

    def __updateUserOnlineStatus(self, user, presence):
        if user and user.isFriend():
            isInXMPP = presence not in [PRESENCE.UNAVAILABLE, PRESENCE.UNKNOWN]
            prevOnline = user.isOnline()
            user.update(isInXMPP=isInXMPP)
            if prevOnline is not user.isOnline():
                LOG_DEBUG("Player's status has been changed by XMPP", user)
                g_messengerEvents.users.onUserRosterStatusUpdated(user)

    def __handleDisconnect(self, reason, description):
        if connectionManager.isConnected():
            for user in self.usersStorage.getList(BWFriendFindCriteria(True)):
                prevOnline = user.isOnline()
                user.update(isInXMPP=False)
                if prevOnline is not user.isOnline():
                    LOG_DEBUG("Player's status has been changed by XMPP", user)
                    g_messengerEvents.users.onUserRosterStatusUpdated(user)

    def __handleRosterResourceAdded(self, jid, priority, status, presence):
        self.__updateUserOnlineStatus(self.usersStorage.getUser(jid.getDatabaseID()), presence)

    def __handleRosterResourceRemoved(self, jid):
        if self.xmppRoster.hasItem(jid):
            presence = self.xmppRoster[jid].presence
        else:
            presence = PRESENCE.UNKNOWN
        self.__updateUserOnlineStatus(self.usersStorage.getUser(jid.getDatabaseID()), presence)

    def __me_onRosterReceived(self):
        for jid, item in self.xmppRoster.iteritems():
            self.__updateUserOnlineStatus(self.usersStorage.getUser(jid.getDatabaseID()), item.presence)


class UpdatersCollection(object):

    def __init__(self):
        super(UpdatersCollection, self).__init__()
        self.__rosterUpdater = None
        self.__onlineUpdater = None
        return

    def init(self):
        self.__rosterUpdater = RosterUpdater()
        self.__rosterUpdater.registerHandlers()
        if g_settings.server.useToShowOnline(PROTO_TYPE.XMPP):
            self.__onlineUpdater = OnlineStatusUpdater()
            self.__onlineUpdater.registerHandlers()

    def fini(self):
        if self.__rosterUpdater:
            self.__rosterUpdater.unregisterHandlers()
            self.__rosterUpdater = None
        if self.__onlineUpdater:
            self.__onlineUpdater.unregisterHandlers()
            self.__onlineUpdater = None
        return
