# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/notification/listeners.py
import collections
from collections import defaultdict
import weakref
from adisp import process
from debug_utils import LOG_DEBUG, LOG_ERROR
from gui.LobbyContext import g_lobbyContext
from gui.Scaleform.locale.CLANS import CLANS
from gui.clans.clan_account_profile import SYNC_KEYS
from gui.clans.clan_helpers import ClanListener, isInClanEnterCooldown
from gui.clans.contexts import GetClanInfoCtx
from gui.clans.settings import CLAN_APPLICATION_STATES
from gui.prb_control import prbInvitesProperty
from gui.prb_control.entities.listener import IGlobalListener
from gui.shared.notifications import MsgCustomEvents
from gui.shared.utils import showInvitationInWindowsBar
from gui.shared.view_helpers.UsersInfoHelper import UsersInfoHelper
from gui.wgnc import g_wgncProvider, g_wgncEvents, wgnc_settings
from gui.wgnc.settings import WGNC_DATA_PROXY_TYPE
from helpers import time_utils
from messenger.m_constants import PROTO_TYPE, USER_ACTION_ID
from messenger.proto import proto_getter
from messenger.proto.events import g_messengerEvents
from messenger.proto.xmpp.xmpp_constants import XMPP_ITEM_TYPE
from notification import tutorial_helper
from notification.decorators import MessageDecorator, PrbInviteDecorator, FriendshipRequestDecorator, WGNCPopUpDecorator, ClanAppsDecorator, ClanInvitesDecorator, ClanAppActionDecorator, ClanInvitesActionDecorator, ClanSingleAppDecorator, ClanSingleInviteDecorator
from notification.settings import NOTIFICATION_TYPE, NOTIFICATION_BUTTON_STATE

class _NotificationListener(object):

    def __init__(self):
        super(_NotificationListener, self).__init__()
        self._model = lambda : None

    def start(self, model):
        self._model = weakref.ref(model)
        return True

    def stop(self):
        self._model = lambda : None

    def request(self):
        pass


class _WGNCNotificationListener(_NotificationListener):

    def onProviderEnabled(self):
        pass


class ServiceChannelListener(_NotificationListener):

    @proto_getter(PROTO_TYPE.BW)
    def proto(self):
        return None

    def start(self, model):
        result = super(ServiceChannelListener, self).start(model)
        if result:
            channel = g_messengerEvents.serviceChannel
            channel.onServerMessageReceived += self.__onMessageReceived
            channel.onClientMessageReceived += self.__onMessageReceived
            serviceChannel = self.proto.serviceChannel
            messages = serviceChannel.getReadMessages()
            addNotification = model.collection.addItem
            for clientID, (_, formatted, settings) in messages:
                addNotification(MessageDecorator(clientID, formatted, settings))

            serviceChannel.handleUnreadMessages()
        return result

    def stop(self):
        super(ServiceChannelListener, self).stop()
        channel = g_messengerEvents.serviceChannel
        channel.onServerMessageReceived -= self.__onMessageReceived
        channel.onClientMessageReceived -= self.__onMessageReceived

    def __onMessageReceived(self, clientID, formatted, settings):
        model = self._model()
        if model:
            model.addNotification(MessageDecorator(clientID, formatted, settings))


class FortServiceChannelListener(_NotificationListener):

    def __init__(self):
        super(FortServiceChannelListener, self).__init__()
        self.__fortInvitesData = {}

    @proto_getter(PROTO_TYPE.BW)
    def proto(self):
        return None

    def start(self, model):
        result = super(FortServiceChannelListener, self).start(model)
        if result:
            g_messengerEvents.serviceChannel.onCustomMessageDataReceived += self.__onMsgReceived
            g_lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingChanged
        return result

    def stop(self):
        self.__fortInvitesData = None
        g_messengerEvents.serviceChannel.onCustomMessageDataReceived -= self.__onMsgReceived
        g_lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingChanged
        super(FortServiceChannelListener, self).stop()
        return

    def __onMsgReceived(self, clientID, eventData):
        eType, battleID = eventData
        if eType == MsgCustomEvents.FORT_BATTLE_INVITE:
            self.__fortInvitesData[battleID] = clientID
        elif eType == MsgCustomEvents.FORT_BATTLE_FINISHED:
            model = self._model()
            if model:
                storedClientID = self.__fortInvitesData.get(battleID, None)
                if storedClientID:
                    _, formatted, settings = self.proto.serviceChannel.getMessage(storedClientID)
                    if formatted and settings:
                        if formatted['savedData']['battleFinishTime'] - time_utils.getCurrentTimestamp() < 0:
                            buttonsStates = {}
                            buttonsLayout = formatted.get('buttonsLayout', [])
                            for layout in buttonsLayout:
                                buttonsStates[layout['type']] = NOTIFICATION_BUTTON_STATE.VISIBLE

                            formatted['buttonsStates'] = buttonsStates
                            model.updateNotification(NOTIFICATION_TYPE.MESSAGE, storedClientID, formatted, False)
                            del self.__fortInvitesData[battleID]
        return

    def __onServerSettingChanged(self, diff):
        if 'isFortsEnabled' in diff and not diff['isFortsEnabled']:
            model = self._model()
            if model:
                for battleID in self.__fortInvitesData.keys():
                    storedClientID = self.__fortInvitesData[battleID]
                    _, formatted, settings = self.proto.serviceChannel.getMessage(storedClientID)
                    if formatted and settings:
                        buttonsStates = {}
                        buttonsLayout = formatted.get('buttonsLayout', [])
                        for layout in buttonsLayout:
                            buttonsStates[layout['type']] = NOTIFICATION_BUTTON_STATE.VISIBLE

                        formatted['buttonsStates'] = buttonsStates
                        model.updateNotification(NOTIFICATION_TYPE.MESSAGE, storedClientID, formatted, False)
                        del self.__fortInvitesData[battleID]


class PrbInvitesListener(_NotificationListener, IGlobalListener):

    @prbInvitesProperty
    def prbInvites(self):
        return None

    def start(self, model):
        result = super(PrbInvitesListener, self).start(model)
        self.startGlobalListening()
        prbInvites = self.prbInvites
        if result and prbInvites:
            prbInvites.onInvitesListInited += self.__onInviteListInited
            prbInvites.onReceivedInviteListModified += self.__onInviteListModified
            if prbInvites.isInited():
                self.__addInvites()
        return result

    def stop(self):
        super(PrbInvitesListener, self).stop()
        self.stopGlobalListening()
        prbInvites = self.prbInvites
        if prbInvites:
            prbInvites.onInvitesListInited -= self.__onInviteListInited
            prbInvites.onReceivedInviteListModified -= self.__onInviteListModified

    def onPrbEntitySwitched(self):
        self.__updateInvites()

    def onTeamStatesReceived(self, entity, team1State, team2State):
        self.__updateInvites()

    def onUnitFlagsChanged(self, flags, timeLeft):
        self.__updateInvites()

    def onEnqueued(self, queueType, *args):
        self.__updateInvites()

    def onDequeued(self, queueType, *args):
        self.__updateInvites()

    def __onInviteListInited(self):
        if self.prbInvites.getUnreadCount() > 0:
            showInvitationInWindowsBar()
        self.__addInvites()

    def __onInviteListModified(self, added, changed, deleted):
        showInvitationInWindowsBar()
        model = self._model()
        if model is None:
            return
        else:
            for inviteID in added:
                invite = self.prbInvites.getInvite(inviteID)
                if invite:
                    model.addNotification(PrbInviteDecorator(invite))

            for inviteID in deleted:
                model.removeNotification(NOTIFICATION_TYPE.INVITE, inviteID)

            for inviteID in changed:
                invite = self.prbInvites.getInvite(inviteID)
                if invite:
                    model.updateNotification(NOTIFICATION_TYPE.INVITE, inviteID, invite, True)

            return

    def __addInvites(self):
        model = self._model()
        if model is None:
            return
        else:
            model.removeNotificationsByType(NOTIFICATION_TYPE.INVITE)
            invites = self.prbInvites.getReceivedInvites()
            invites = sorted(invites, cmp=lambda invite, other: cmp(invite.createTime, other.createTime))
            for invite in invites:
                model.addNotification(PrbInviteDecorator(invite))

            return

    def __updateInvites(self):
        model = self._model()
        if model:
            invites = self.prbInvites.getReceivedInvites()
            for invite in invites:
                model.updateNotification(NOTIFICATION_TYPE.INVITE, invite.clientID, invite, False)


class FriendshipRqsListener(_NotificationListener):

    @proto_getter(PROTO_TYPE.XMPP)
    def proto(self):
        return None

    def start(self, model):
        result = super(FriendshipRqsListener, self).start(model)
        g_messengerEvents.onPluginDisconnected += self.__me_onPluginDisconnected
        events = g_messengerEvents.users
        events.onFriendshipRequestsAdded += self.__me_onFriendshipRequestsAdded
        events.onFriendshipRequestsUpdated += self.__me_onFriendshipRequestsUpdated
        events.onUserActionReceived += self.__me_onUserActionReceived
        contacts = self.proto.contacts.getFriendshipRqs()
        for contact in contacts:
            self.__setRequest(contact)

        return result

    def stop(self):
        g_messengerEvents.onPluginDisconnected -= self.__me_onPluginDisconnected
        events = g_messengerEvents.users
        events.onFriendshipRequestsAdded -= self.__me_onFriendshipRequestsAdded
        events.onFriendshipRequestsUpdated -= self.__me_onFriendshipRequestsUpdated
        events.onUserActionReceived -= self.__me_onUserActionReceived
        super(FriendshipRqsListener, self).stop()

    def __setRequest(self, contact):
        model = self._model()
        if model:
            if contact.getProtoType() != PROTO_TYPE.XMPP:
                return
            if contact.getItemType() == XMPP_ITEM_TYPE.EMPTY_ITEM:
                return
            contactID = contact.getID()
            if model.hasNotification(NOTIFICATION_TYPE.FRIENDSHIP_RQ, contactID):
                model.updateNotification(NOTIFICATION_TYPE.FRIENDSHIP_RQ, contactID, contact, self.proto.contacts.canApproveFriendship(contact))
            else:
                model.addNotification(FriendshipRequestDecorator(contact))

    def __updateRequest(self, contact):
        model = self._model()
        if model:
            if contact.getProtoType() != PROTO_TYPE.XMPP:
                return
            model.updateNotification(NOTIFICATION_TYPE.FRIENDSHIP_RQ, contact.getID(), contact, False)

    def __updateRequests(self):
        contacts = self.proto.contacts.getFriendshipRqs()
        for contact in contacts:
            self.__updateRequest(contact)

    def __me_onPluginDisconnected(self, protoType):
        if protoType == PROTO_TYPE.XMPP:
            self.__updateRequests()

    def __me_onFriendshipRequestsAdded(self, contacts):
        for contact in contacts:
            self.__setRequest(contact)

    def __me_onFriendshipRequestsUpdated(self, contacts):
        for contact in contacts:
            self.__updateRequest(contact)

    def __me_onUserActionReceived(self, actionID, contact):
        if contact.getProtoType() != PROTO_TYPE.XMPP:
            return
        if actionID in (USER_ACTION_ID.SUBSCRIPTION_CHANGED, USER_ACTION_ID.IGNORED_ADDED, USER_ACTION_ID.TMP_IGNORED_ADDED):
            self.__updateRequest(contact)
        elif actionID in (USER_ACTION_ID.FRIEND_ADDED, USER_ACTION_ID.FRIEND_REMOVED):
            self.__updateRequests()


class _ClanNotificationsCommonListener(_WGNCNotificationListener, ClanListener):

    def __init__(self):
        super(_ClanNotificationsCommonListener, self).__init__()
        self.__startTime = None
        return

    def start(self, model):
        result = super(_ClanNotificationsCommonListener, self).start(model)
        self.startClanListening()
        g_wgncEvents.onProxyDataItemShowByDefault += self._onProxyDataItemShow
        self.__startTime = time_utils.getCurrentTimestamp()
        if not self._canBeShown():
            return
        storedItems = self._getStoredReceivedItems()
        itemsByTypeCount = len(storedItems)
        LOG_DEBUG('Clan WGNC new notifications count with type "%d": %d' % (self._getNewReceivedItemType(), itemsByTypeCount))
        if itemsByTypeCount:
            if itemsByTypeCount > 1:
                self._addMultiNotification(storedItems)
            else:
                self._addSingleNotification(storedItems[0])
        return result

    def stop(self):
        self.stopClanListening()
        g_wgncEvents.onProxyDataItemShowByDefault -= self._onProxyDataItemShow
        super(_ClanNotificationsCommonListener, self).stop()

    def onAccountClanProfileChanged(self, profile):
        """
        Perform necessarily checking in case of user entrance into clan or leaving from clan
        :param profile:
        """
        pass

    def onClanStateChanged(self, oldStateID, newStateID):
        super(_ClanNotificationsCommonListener, self).onClanStateChanged(oldStateID, newStateID)
        model = self._model()
        if model:
            if not self.clansCtrl.isEnabled():
                self._removeAllNotifications()
            else:
                self._updateAllNotifications()

    def _onProxyDataItemShow(self, notID, item):
        if not self._canBeShown():
            return True
        elif self._getNewReceivedItemType() == item.getType():
            model = self._model()
            if self.__startTime:
                if time_utils.getCurrentTimestamp() - self.__startTime < 5:
                    multiNot = self._getMultiNotification()
                    if multiNot:
                        model.updateNotification(multiNot.getType(), multiNot.getID(), multiNot.getEntity() + 1, False)
                    else:
                        self._addSingleNotification(item)
                else:
                    self.__startTime = None
                    self._addSingleNotification(item)
            else:
                self._addSingleNotification(item)
            return True
        else:
            return False

    def _getStoredReceivedItems(self):
        """
        Gets items received when user was offline or during the battle session
        :return: list of gui.wgnc.proxy_data._ProxyDataItem
        """
        return self._getNotMarkedItemsByType(self._getNewReceivedItemType())

    def _getNotMarkedItemsByType(self, itemType):
        """
        Gets not marked items by required type and marks them
        :param itemType: wgnc_settings.WGNC_DATA_PROXY_TYPE.*
        :return: list of gui.wgnc.proxy_data._ProxyDataItem
        """
        itemsByType = []
        for notification in g_wgncProvider.getNotMarkedNots():
            proxyDataItem = notification.getProxyItemByType(itemType)
            if proxyDataItem is None:
                continue
            notification.marked = True
            itemsByType.append(proxyDataItem)

        return itemsByType

    def _getNewReceivedItemType(self):
        raise NotImplementedError

    def _addSingleNotification(self, item):
        raise NotImplementedError

    def _addMultiNotification(self, items, count=None):
        raise NotImplementedError

    def _getMultiNotification(self):
        raise NotImplementedError

    def _canBeShown(self):
        return self.clansCtrl.isEnabled() and self.clansCtrl.getAccountProfile() is not None and self.settingsCore.getSetting('receiveClanInvitesNotifications')

    def _updateAllNotifications(self):
        pass

    def _removeAllNotifications(self):
        pass

    def _removeNotifications(self, notificationList):
        model = self._model()
        for notDecorator in model.collection.getListIterator(notificationList):
            model.removeNotification(notDecorator.getType(), notDecorator.getID())


class _ClanAppsListener(_ClanNotificationsCommonListener, UsersInfoHelper):
    _TYPES_EXPECTED_USERS_NAMES = (NOTIFICATION_TYPE.CLAN_APP, NOTIFICATION_TYPE.CLAN_INVITE_ACTION)

    def __init__(self):
        super(_ClanAppsListener, self).__init__()
        self.__userNamePendingNotifications = defaultdict(set)

    def stop(self):
        super(_ClanAppsListener, self).stop()
        self.__userNamePendingNotifications = defaultdict(set)

    def onClanAppStateChanged(self, appId, state):
        self.__updateNotificationState(appId, state)

    def onAccountClanProfileChanged(self, profile):
        """
        Perform necessarily checking in case of user entrance into clan or leaving from clan
        :param profile:
        """
        if not profile.isInClan() or not profile.getMyClanPermissions().canHandleClanInvites():
            model = self._model()
            for notification in model.collection.getListIterator((NOTIFICATION_TYPE.CLAN_APP, NOTIFICATION_TYPE.CLAN_APPS)):
                model.removeNotification(notification.getType(), notification.getID())

    def onUserNamesReceived(self, names):
        for userDBID, userName in names.iteritems():
            if userDBID in self.__userNamePendingNotifications:
                model = self._model()
                for appId in self.__userNamePendingNotifications[userDBID]:
                    for nType in self._TYPES_EXPECTED_USERS_NAMES:
                        clanSingleAppDecorator = model.getNotification(nType, appId)
                        if clanSingleAppDecorator:
                            clanSingleAppDecorator.setUserName(userName)
                            model.updateNotification(nType, appId, clanSingleAppDecorator.getEntity(), False)

                self.__userNamePendingNotifications[userDBID] = set()

    def _onProxyDataItemShow(self, notID, item):
        isProcessed = super(_ClanAppsListener, self)._onProxyDataItemShow(notID, item)
        if not isProcessed:
            itemType = item.getType()
            if itemType == WGNC_DATA_PROXY_TYPE.CLAN_INVITE_ACCEPTED:
                self.__addUserNotification(ClanInvitesActionDecorator, (item.getID(), 'inviteAccepted'), item)
                isProcessed = True
            elif itemType == WGNC_DATA_PROXY_TYPE.CLAN_INVITE_DECLINED:
                self.__addUserNotification(ClanInvitesActionDecorator, (item.getID(), 'inviteDeclined'), item)
                isProcessed = True
            elif itemType == WGNC_DATA_PROXY_TYPE.CLAN_APP_ACCEPTED_FOR_MEMBERS:
                self.__updateNotificationState(item.getApplicationID(), CLAN_APPLICATION_STATES.ACCEPTED)
                isProcessed = True
            elif itemType == WGNC_DATA_PROXY_TYPE.CLAN_APP_DECLINED_FOR_MEMBERS:
                self.__updateNotificationState(item.getApplicationID(), CLAN_APPLICATION_STATES.DECLINED)
                isProcessed = True
        return isProcessed

    def _getNewReceivedItemType(self):
        return wgnc_settings.WGNC_DATA_PROXY_TYPE.CLAN_APP

    def _getStoredReceivedItems(self):
        storedClanAPPs = super(_ClanAppsListener, self)._getStoredReceivedItems()
        processedClamAPPs = self._getNotMarkedItemsByType(wgnc_settings.WGNC_DATA_PROXY_TYPE.CLAN_APP_ACCEPTED_FOR_MEMBERS)
        processedClamAPPs.extend(self._getNotMarkedItemsByType(wgnc_settings.WGNC_DATA_PROXY_TYPE.CLAN_APP_DECLINED_FOR_MEMBERS))
        for processedAPP in processedClamAPPs:
            for i in xrange(len(storedClanAPPs) - 1, -1, -1):
                storedAPP = storedClanAPPs[i]
                if processedAPP.getApplicationID() == storedAPP.getApplicationID():
                    del storedClanAPPs[i]

        return storedClanAPPs

    @process
    def _addSingleNotification(self, item):
        """
        Adds notification with type wgnc_settings.WGNC_DATA_PROXY_TYPE.CLAN_APP only!
        :param item: reference to gui.wgnc.proxy_data._ProxyDataItem
        """
        ctx = GetClanInfoCtx(item.getAccountID())
        self.__addUserNotification(ClanSingleAppDecorator, (item.getID(), item), item)
        accountResponse = yield self.clansCtrl.sendRequest(ctx)
        if accountResponse.isSuccess():
            accountInfo = ctx.getDataObj(accountResponse.data)
            isInCooldown = isInClanEnterCooldown(accountInfo.getClanCooldownTill())
            if isInCooldown:
                model = self._model()
                appId = item.getApplicationID()
                clanSingleAppDecorator = model.getNotification(NOTIFICATION_TYPE.CLAN_APP, appId)
                if clanSingleAppDecorator:
                    clanSingleAppDecorator.setClanEnterCooldown(isInCooldown)
                    model.updateNotification(NOTIFICATION_TYPE.CLAN_APP, appId, clanSingleAppDecorator.getEntity(), False)

    def _addMultiNotification(self, items, count=None):
        count = int(len(items) if items else count)
        self._model().addNotification(ClanAppsDecorator(self.clansCtrl.getAccountProfile().getClanDbID(), count))

    def _getMultiNotification(self):
        return self._model().getNotification(NOTIFICATION_TYPE.CLAN_APPS, self.clansCtrl.getAccountProfile().getClanDbID())

    def _updateAllNotifications(self):
        model = self._model()
        for notifications in model.collection.getListIterator((NOTIFICATION_TYPE.CLAN_APP, NOTIFICATION_TYPE.CLAN_APPS)):
            model.updateNotification(notifications.getType(), notifications.getID(), notifications.getEntity(), False)

    def _removeAllNotifications(self):
        self._removeNotifications((NOTIFICATION_TYPE.CLAN_APP, NOTIFICATION_TYPE.CLAN_APPS, NOTIFICATION_TYPE.CLAN_INVITE_ACTION))

    def _canBeShown(self):
        canBeShown = super(_ClanAppsListener, self)._canBeShown()
        profile = self.clansCtrl.getAccountProfile()
        return canBeShown and profile.isInClan() and profile.getMyClanPermissions().canHandleClanInvites()

    def __addUserNotification(self, clazz, args, item):
        """
        Adds notifications which requires user name requesting
        :param clazz: class of decorator
        :param args: arguments will be passed into constructor of clazz
        :param item: reference to corresponded gui.wgnc.proxy_data._ProxyDataItem
        """
        userDatabaseID = item.getAccountID()
        appId = item.getID()
        userName = self.getUserName(userDatabaseID)
        if not userName:
            self.__userNamePendingNotifications[userDatabaseID].add(appId)
            self.syncUsersInfo()
            userName = CLANS.CLANINVITE_NOTIFICATION_USERNAMEERROR
        notification = clazz(userName=userName, *args)
        notificationType = notification.getType()
        if notificationType not in self._TYPES_EXPECTED_USERS_NAMES:
            LOG_ERROR('Unexpected notification type "{}"'.format(notificationType))
        else:
            self._model().addNotification(notification)

    def __updateNotificationState(self, appId, state):
        model = self._model()
        clanSingleAppDecorator = model.getNotification(NOTIFICATION_TYPE.CLAN_APP, appId)
        if clanSingleAppDecorator:
            clanSingleAppDecorator.setState(state)
            model.updateNotification(NOTIFICATION_TYPE.CLAN_APP, appId, clanSingleAppDecorator.getEntity(), False)


class _ClanPersonalInvitesListener(_ClanNotificationsCommonListener):
    _INVITES_ENTITY_ID = 1

    def onAccountWebVitalInfoChanged(self, fieldName, value):
        super(_ClanPersonalInvitesListener, self).onAccountWebVitalInfoChanged(fieldName, value)
        if SYNC_KEYS.CLAN_INFO == fieldName:
            profile = self.clansCtrl.getAccountProfile()
            if not profile.isInClan():
                self.__updateNotificationsByTypes((NOTIFICATION_TYPE.CLAN_INVITE,))

    def onAccountClanProfileChanged(self, profile):
        """
        Perform necessarily checking in case of user entrance into clan or leaving from clan
        :param profile:
        """
        if profile.isInClan():
            model = self._model()
            for notDecorator in model.collection.getListIterator((NOTIFICATION_TYPE.CLAN_INVITE, NOTIFICATION_TYPE.CLAN_INVITES)):
                model.removeNotification(notDecorator.getType(), notDecorator.getID())

    def onClanInvitesStateChanged(self, inviteIds, state):
        model = self._model()
        for inviteId in inviteIds:
            clanSingleInvDecorator = model.getNotification(NOTIFICATION_TYPE.CLAN_INVITE, inviteId)
            if clanSingleInvDecorator:
                clanSingleInvDecorator.setState(state)
                model.updateNotification(NOTIFICATION_TYPE.CLAN_INVITE, inviteId, clanSingleInvDecorator.getEntity(), False)

    def _onProxyDataItemShow(self, notID, item):
        isProcessed = super(_ClanPersonalInvitesListener, self)._onProxyDataItemShow(notID, item)
        if not isProcessed:
            itemType = item.getType()
            if itemType == WGNC_DATA_PROXY_TYPE.CLAN_APP_DECLINED:
                self._model().addNotification(ClanAppActionDecorator(item.getApplicationId(), 'appDeclined', (item.getClanName(), item.getClanTag())))
                isProcessed = True
            elif itemType == WGNC_DATA_PROXY_TYPE.CLAN_APP_ACCEPTED:
                self._model().addNotification(ClanAppActionDecorator(item.getApplicationId(), 'appAccepted', (item.getClanName(), item.getClanTag())))
                isProcessed = True
        return isProcessed

    def _getNewReceivedItemType(self):
        return wgnc_settings.WGNC_DATA_PROXY_TYPE.CLAN_INVITE

    def _addSingleNotification(self, item):
        self._model().addNotification(ClanSingleInviteDecorator(item.getID(), item))

    def _addMultiNotification(self, items, count=None):
        count = int(len(items) if items else count)
        self._model().addNotification(ClanInvitesDecorator(self.clansCtrl.getAccountProfile().getDbID(), count))

    def _getMultiNotification(self):
        return self._model().getNotification(NOTIFICATION_TYPE.CLAN_INVITES, self.clansCtrl.getAccountProfile().getDbID())

    def _updateAllNotifications(self):
        self.__updateNotificationsByTypes((NOTIFICATION_TYPE.CLAN_INVITE, NOTIFICATION_TYPE.CLAN_INVITES))

    def __updateNotificationsByTypes(self, notifTypes):
        model = self._model()
        for notDecorator in model.collection.getListIterator(notifTypes):
            model.updateNotification(notDecorator.getType(), notDecorator.getID(), notDecorator.getEntity(), False)

    def _removeAllNotifications(self):
        self._removeNotifications((NOTIFICATION_TYPE.CLAN_INVITE, NOTIFICATION_TYPE.CLAN_INVITES, NOTIFICATION_TYPE.CLAN_APP_ACTION))

    def _canBeShown(self):
        isCtrlrEnabled = super(_ClanPersonalInvitesListener, self)._canBeShown()
        profile = self.clansCtrl.getAccountProfile()
        return isCtrlrEnabled and not profile.isInClan()


class _WGNCListener(_WGNCNotificationListener):

    def __init__(self):
        super(_WGNCListener, self).__init__()
        self.__offset = 0

    def start(self, model):
        result = super(_WGNCListener, self).start(model)
        g_wgncEvents.onItemShowByDefault += self.__onItemShowByDefault
        g_wgncEvents.onItemShowByAction += self.__onItemShowByAction
        g_wgncEvents.onItemUpdatedByAction += self.__onItemUpdatedByAction
        addNotification = model.collection.addItem
        for notification in g_wgncProvider.getMarkedNots():
            popUp = notification.getItemByType(wgnc_settings.WGNC_GUI_TYPE.POP_UP)
            if popUp is None:
                continue
            addNotification(WGNCPopUpDecorator(notification.notID, popUp, receivedAt=notification.order))

        self.__offset = 0.1
        return result

    def onProviderEnabled(self):
        self.__offset = 0

    def stop(self):
        g_wgncEvents.onItemShowByDefault -= self.__onItemShowByDefault
        g_wgncEvents.onItemShowByAction -= self.__onItemShowByAction
        g_wgncEvents.onItemUpdatedByAction -= self.__onItemUpdatedByAction
        super(_WGNCListener, self).stop()

    def __onItemShowByDefault(self, notID, item):
        model = self._model()
        if model and item.getType() == wgnc_settings.WGNC_GUI_TYPE.POP_UP:
            model.addNotification(WGNCPopUpDecorator(notID, item, self.__offset))

    def __onItemShowByAction(self, notID, target):
        g_wgncProvider.showNotItemByName(notID, target)

    def __onItemUpdatedByAction(self, notID, item):
        model = self._model()
        if model and item.getType() == wgnc_settings.WGNC_GUI_TYPE.POP_UP:
            model.updateNotification(NOTIFICATION_TYPE.WGNC_POP_UP, notID, item, False)


class _WGNCListenersContainer(_NotificationListener):

    def __init__(self):
        super(_WGNCListenersContainer, self).__init__()
        self.__wgncListener = _WGNCListener()
        self.__clanListeners = (_ClanAppsListener(), _ClanPersonalInvitesListener())

    def start(self, model):
        self.__wgncListener.start(model)
        g_wgncProvider.showNoMarkedNots()
        g_wgncProvider.setEnabled(True)
        for listener in self.__clanListeners:
            listener.start(model)

        self.__wgncListener.onProviderEnabled()
        return super(_WGNCListenersContainer, self).start(model)

    def stop(self):
        self.__wgncListener.stop()
        for listener in self.__clanListeners:
            listener.stop()

        g_wgncProvider.setEnabled(False)
        g_wgncProvider.setNotsAsMarked()
        super(_WGNCListenersContainer, self).stop()


class BattleTutorialListener(_NotificationListener, IGlobalListener):
    _messagesIDs = tutorial_helper.TutorialGlobalStorage(tutorial_helper.TUTORIAL_GLOBAL_VAR.SERVICE_MESSAGES_IDS, [])

    @proto_getter(PROTO_TYPE.BW)
    def proto(self):
        return None

    def start(self, model):
        self.startGlobalListening()
        return super(BattleTutorialListener, self).start(model)

    def stop(self):
        super(BattleTutorialListener, self).stop()
        self.stopGlobalListening()

    def onEnqueued(self, queueType, *args):
        self.__updateBattleResultMessage(True)

    def onDequeued(self, queueType, *args):
        self.__updateBattleResultMessage(False)

    def __updateBattleResultMessage(self, locked):
        model = self._model()
        if not model:
            return
        else:
            ids = self._messagesIDs
            if not isinstance(ids, collections.Iterable):
                return
            for messageID in ids:
                _, formatted, settings = self.proto.serviceChannel.getMessage(messageID)
                if formatted and settings:
                    if 'buttonsStates' not in formatted:
                        return
                    submit = formatted['buttonsStates'].get('submit')
                    if submit is None or submit != NOTIFICATION_BUTTON_STATE.HIDDEN:
                        if locked:
                            submit = NOTIFICATION_BUTTON_STATE.VISIBLE
                        else:
                            submit = NOTIFICATION_BUTTON_STATE.VISIBLE | NOTIFICATION_BUTTON_STATE.ENABLED
                        formatted['buttonsStates']['submit'] = submit
                    model.updateNotification(NOTIFICATION_TYPE.MESSAGE, messageID, formatted, False)

            return


class NotificationsListeners(_NotificationListener):

    def __init__(self):
        super(NotificationsListeners, self).__init__()
        self.__listeners = (ServiceChannelListener(),
         FortServiceChannelListener(),
         PrbInvitesListener(),
         FriendshipRqsListener(),
         _WGNCListenersContainer(),
         BattleTutorialListener())

    def start(self, model):
        for listener in self.__listeners:
            listener.start(model)

    def stop(self):
        for listener in self.__listeners:
            listener.stop()
