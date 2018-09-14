# Python 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/notification/listeners.py
import collections
import weakref
import operator
from account_helpers.settings_core.SettingsCore import g_settingsCore
from debug_utils import LOG_DEBUG
from gui.clans.clan_account_profile import SYNC_KEYS
from gui.clans.clan_helpers import ClanListener
from gui.clubs.settings import CLIENT_CLUB_STATE
from gui.clubs.club_helpers import ClubListener
from gui.prb_control.prb_helpers import GlobalListener, prbInvitesProperty
from gui.shared.notifications import MsgCustomEvents
from gui.shared.utils import showInvitationInWindowsBar
from gui.shared.view_helpers.UsersInfoHelper import UsersInfoHelper
from gui.wgnc.proxy_data import ClanApplicationItem
from gui.wgnc.settings import WGNC_DATA_PROXY_TYPE
from helpers import time_utils
from messenger.m_constants import PROTO_TYPE, USER_ACTION_ID
from messenger.proto import proto_getter
from messenger.proto.events import g_messengerEvents
from messenger.proto.xmpp.xmpp_constants import XMPP_ITEM_TYPE
from notification import tutorial_helper
from notification.decorators import MessageDecorator, PrbInviteDecorator, FriendshipRequestDecorator, WGNCPopUpDecorator, ClubInviteDecorator, ClubAppsDecorator, ClanAppsDecorator, ClanInvitesDecorator, ClanAppActionDecorator, ClanInvitesActionDecorator, ClanSingleAppDecorator, ClanSingleInviteDecorator
from notification.settings import NOTIFICATION_TYPE, NOTIFICATION_BUTTON_STATE
from gui.wgnc import g_wgncProvider, g_wgncEvents, wgnc_settings

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
        return result

    def stop(self):
        self.__fortInvitesData = None
        g_messengerEvents.serviceChannel.onCustomMessageDataReceived -= self.__onMsgReceived
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


class PrbInvitesListener(_NotificationListener, GlobalListener):

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

    def onPrbFunctionalInited(self):
        self.__updateInvites()

    def onPrbFunctionalFinished(self):
        self.__updateInvites()

    def onTeamStatesReceived(self, functional, team1State, team2State):
        self.__updateInvites()

    def onIntroUnitFunctionalInited(self):
        self.__updateInvites()

    def onIntroUnitFunctionalFinished(self):
        self.__updateInvites()

    def onUnitFunctionalInited(self):
        self.__updateInvites()

    def onUnitFunctionalFinished(self):
        self.__updateInvites()

    def onUnitFlagsChanged(self, flags, timeLeft):
        self.__updateInvites()

    def onPreQueueFunctionalInited(self):
        self.__updateInvites()

    def onPreQueueFunctionalFinished(self):
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
        if actionID in (USER_ACTION_ID.SUBSCRIPTION_CHANGED, USER_ACTION_ID.IGNORED_ADDED):
            self.__updateRequest(contact)
        elif actionID in (USER_ACTION_ID.FRIEND_ADDED, USER_ACTION_ID.FRIEND_REMOVED):
            self.__updateRequests()


class ClubsInvitesListener(_NotificationListener, ClubListener):

    def start(self, model):
        result = super(ClubsInvitesListener, self).start(model)
        self.startClubListening()
        self.__addClubInvites()
        self.__requestMyClub()
        return result

    def stop(self):
        self.stopClubListening()
        super(ClubsInvitesListener, self).stop()

    def onAccountClubStateChanged(self, state):
        model = self._model()
        if model and self.clubsState.getStateID() == CLIENT_CLUB_STATE.UNKNOWN:
            model.removeNotificationsByType(NOTIFICATION_TYPE.CLUB_INVITE)
            model.removeNotificationsByType(NOTIFICATION_TYPE.CLUB_APPS)
        else:
            self.__requestMyClub()

    def onAccountClubInvitesInited(self, invites):
        self.__addClubInvites()

    def onAccountClubInvitesChanged(self, added, removed, changed):
        model = self._model()
        if model is None:
            return
        else:
            if len(added):
                showInvitationInWindowsBar()
            for invite in removed:
                model.removeNotification(NOTIFICATION_TYPE.CLUB_INVITE, invite.getID())

            for invite in added:
                model.addNotification(ClubInviteDecorator(invite))

            for invite in changed:
                model.updateNotification(NOTIFICATION_TYPE.CLUB_INVITE, invite.getID(), invite, True)

            return

    def __requestMyClub(self):
        self.clubsCtrl.getProfile().requestMyClub(self.__onMyClubReceived)

    def __onMyClubReceived(self, club):
        model = self._model()
        if model is None:
            return
        else:
            model.removeNotificationsByType(NOTIFICATION_TYPE.CLUB_APPS)
            if club:
                limits = self.clubsCtrl.getLimits()
                if limits.canAcceptApplication(self.clubsCtrl.getProfile(), club).success:
                    activeApps = club.getApplicants(onlyActive=True)
                    if not self.clubsCtrl.isAppsNotificationShown() and len(activeApps):
                        model.addNotification(ClubAppsDecorator(club.getClubDbID(), activeApps))
                        self.clubsCtrl.markAppsNotificationShown()
            return

    def __addClubInvites(self):
        model = self._model()
        profile = self.clubsCtrl.getProfile()
        if model is None or not profile.isInvitesAvailable():
            return
        else:
            model.removeNotificationsByType(NOTIFICATION_TYPE.CLUB_INVITE)
            invites = profile.getInvites().values()
            invites = sorted(invites, cmp=lambda invite, other: cmp(invite.getTimestamp(), other.getTimestamp()))
            activeInvites = filter(operator.methodcaller('isActive'), invites)
            if len(activeInvites):
                showInvitationInWindowsBar()
            for invite in invites:
                model.addNotification(ClubInviteDecorator(invite))

            return


class _ClanNotificationsCommonListener(_NotificationListener, ClanListener):

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
        else:
            newReceivedItemType = self._getNewReceivediItemType()
            itemsByType = []
            for notification in g_wgncProvider.getNotMarkedNots():
                proxyDataItem = notification.getProxyItemByType(newReceivedItemType)
                if proxyDataItem is None:
                    continue
                itemsByType.append(proxyDataItem)

            itemsByTypeCount = len(itemsByType)
            LOG_DEBUG('Clan WGNC new notifications count with type = %d: %d' % (newReceivedItemType, itemsByTypeCount))
            if itemsByTypeCount:
                if itemsByTypeCount > 1:
                    self._addMultiNotification(itemsByType)
                else:
                    self._addSingleNotification(itemsByType[0])
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
        elif self._getNewReceivediItemType() == item.getType():
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

    def _getNewReceivediItemType(self):
        raise NotImplementedError

    def _addSingleNotification(self, item):
        raise NotImplementedError

    def _addMultiNotification(self, items, count = None):
        raise NotImplementedError

    def _getMultiNotification(self):
        raise NotImplementedError

    def _canBeShown(self):
        return self.clansCtrl.isEnabled() and g_settingsCore.getSetting('receiveClanInvitesNotifications')

    def _updateAllNotifications(self):
        pass

    def _removeAllNotifications(self):
        pass


class _ClanAppsListener(_ClanNotificationsCommonListener, UsersInfoHelper):

    def __init__(self):
        super(_ClanAppsListener, self).__init__()
        self.__pendingNotifications = {}

    def stop(self):
        super(_ClanAppsListener, self).stop()
        self.__pendingNotifications = {}

    def onClanAppStateChanged(self, appId, state):
        model = self._model()
        clanSingleAppDecorator = model.getNotification(NOTIFICATION_TYPE.CLAN_APP, appId)
        if clanSingleAppDecorator:
            clanSingleAppDecorator.setState(state)
            model.updateNotification(NOTIFICATION_TYPE.CLAN_APP, appId, clanSingleAppDecorator.getEntity(), False)

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
            if userDBID in self.__pendingNotifications:
                clazz, args = self.__pendingNotifications[userDBID]
                self._model().addNotification(clazz(userName=userName, *args))
                del self.__pendingNotifications[userDBID]

    def _onProxyDataItemShow(self, notID, item):
        isProcessed = super(_ClanAppsListener, self)._onProxyDataItemShow(notID, item)
        if not isProcessed:
            itemType = item.getType()
            if itemType == WGNC_DATA_PROXY_TYPE.CLAN_INVITE_ACCEPTED:
                self.__addUserNotification(ClanInvitesActionDecorator, (item.getInviteId(), 'inviteAccepted'), item)
                isProcessed = True
            elif itemType == WGNC_DATA_PROXY_TYPE.CLAN_INVITE_DECLINED:
                self.__addUserNotification(ClanInvitesActionDecorator, (item.getInviteId(), 'inviteDeclined'), item)
                isProcessed = True
        return isProcessed

    def _getNewReceivediItemType(self):
        return wgnc_settings.WGNC_DATA_PROXY_TYPE.CLAN_APP

    def _addSingleNotification(self, item):
        self.__addUserNotification(ClanSingleAppDecorator, (item.getID(), item), item)

    def _addMultiNotification(self, items, count = None):
        count = int(len(items) if items else count)
        self._model().addNotification(ClanAppsDecorator(self.clansCtrl.getAccountProfile().getClanDbID(), count))

    def _getMultiNotification(self):
        return self._model().getNotification(NOTIFICATION_TYPE.CLAN_APPS, self.clansCtrl.getAccountProfile().getClanDbID())

    def _updateAllNotifications(self):
        model = self._model()
        for notifications in model.collection.getListIterator((NOTIFICATION_TYPE.CLAN_APP, NOTIFICATION_TYPE.CLAN_APPS)):
            model.updateNotification(notifications.getType(), notifications.getID(), notifications.getEntity(), False)

    def _removeAllNotifications(self):
        model = self._model()
        for notDecorator in model.collection.getListIterator((NOTIFICATION_TYPE.CLAN_APP, NOTIFICATION_TYPE.CLAN_APPS, NOTIFICATION_TYPE.CLAN_INVITE_ACTION)):
            model.removeNotification(notDecorator.getType(), notDecorator.getID())

    def _canBeShown(self):
        canBeShown = super(_ClanAppsListener, self)._canBeShown()
        profile = self.clansCtrl.getAccountProfile()
        return profile.isInClan() and profile.getMyClanPermissions().canHandleClanInvites() and canBeShown

    def __addUserNotification(self, clazz, args, item):
        userDatabaseID = item.getAccountID()
        userName = self.getUserName(userDatabaseID)
        if not userName:
            self.__pendingNotifications[userDatabaseID] = (clazz, args)
            self.syncUsersInfo()
        else:
            self._model().addNotification(clazz(userName=userName, *args))


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

    def _getNewReceivediItemType(self):
        return wgnc_settings.WGNC_DATA_PROXY_TYPE.CLAN_INVITE

    def _addSingleNotification(self, item):
        self._model().addNotification(ClanSingleInviteDecorator(item.getID(), item))

    def _addMultiNotification(self, items, count = None):
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
        for decoratorType in ():
            self._model().removeNotificationsByType(decoratorType)

        model = self._model()
        for notDecorator in model.collection.getListIterator((NOTIFICATION_TYPE.CLAN_INVITE, NOTIFICATION_TYPE.CLAN_INVITES, NOTIFICATION_TYPE.CLAN_APP_ACTION)):
            model.removeNotification(notDecorator.getType(), notDecorator.getID())

    def _canBeShown(self):
        isCtrlrEnabled = super(_ClanPersonalInvitesListener, self)._canBeShown()
        profile = self.clansCtrl.getAccountProfile()
        return not profile.isInClan() and isCtrlrEnabled


class WGNCListener(_NotificationListener):

    def __init__(self):
        super(WGNCListener, self).__init__()
        self.__offset = 0

    def start(self, model):
        result = super(WGNCListener, self).start(model)
        g_wgncEvents.onItemShowByDefault += self.__onItemShowByDefault
        g_wgncEvents.onItemShowByAction += self.__onItemShowByAction
        g_wgncEvents.onItemUpdatedByAction += self.__onItemUpdatedByAction
        addNotification = model.collection.addItem
        for notification in g_wgncProvider.getMarkedNots():
            popUp = notification.getItemByType(wgnc_settings.WGNC_GUI_TYPE.POP_UP)
            if popUp is None:
                continue
            addNotification(WGNCPopUpDecorator(notification.notID, popUp))

        self.__offset = 0.1
        g_wgncProvider.showNoMarkedNots()
        g_wgncProvider.setEnabled(True)
        self.__offset = 0
        return result

    def stop(self):
        g_wgncEvents.onItemShowByDefault -= self.__onItemShowByDefault
        g_wgncEvents.onItemShowByAction -= self.__onItemShowByAction
        g_wgncEvents.onItemUpdatedByAction -= self.__onItemUpdatedByAction
        g_wgncProvider.setNotsAsMarked()
        super(WGNCListener, self).stop()

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


class BattleTutorialListener(_NotificationListener, GlobalListener):
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
        self.__serviceListener = ServiceChannelListener()
        self.__fortMsgsListener = FortServiceChannelListener()
        self.__invitesListener = PrbInvitesListener()
        self.__friendshipRqs = FriendshipRqsListener()
        self.__wgnc = WGNCListener()
        self.__clubsInvitesListener = ClubsInvitesListener()
        self.__clanAppsListener = _ClanAppsListener()
        self.__clanInvitesListener = _ClanPersonalInvitesListener()
        self.__tutorialListener = BattleTutorialListener()

    def start(self, model):
        self.__serviceListener.start(model)
        self.__fortMsgsListener.start(model)
        self.__invitesListener.start(model)
        self.__friendshipRqs.start(model)
        self.__wgnc.start(model)
        self.__clubsInvitesListener.start(model)
        self.__clanAppsListener.start(model)
        self.__clanInvitesListener.start(model)
        self.__tutorialListener.start(model)

    def stop(self):
        self.__serviceListener.stop()
        self.__fortMsgsListener.stop()
        self.__invitesListener.stop()
        self.__friendshipRqs.stop()
        self.__wgnc.stop()
        self.__clanAppsListener.stop()
        self.__clanInvitesListener.stop()
        self.__tutorialListener.stop()
