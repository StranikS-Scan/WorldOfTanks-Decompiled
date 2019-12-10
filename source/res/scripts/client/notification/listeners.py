# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/notification/listeners.py
import collections
import weakref
from collections import defaultdict
from account_helpers import AccountSettings
from account_helpers.AccountSettings import PROGRESSIVE_REWARD_VISITED, SENIORITY_AWARDS_COUNTER
from chat_shared import SYS_MESSAGE_TYPE
from constants import AUTO_MAINTENANCE_RESULT, PremiumConfigs
from adisp import process
from debug_utils import LOG_DEBUG, LOG_ERROR
from gui.Scaleform.locale.CLANS import CLANS
from gui.Scaleform.locale.MESSENGER import MESSENGER
from gui.clans.clan_account_profile import SYNC_KEYS
from gui.clans.clan_helpers import ClanListener, isInClanEnterCooldown
from gui.clans.settings import CLAN_APPLICATION_STATES
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.impl import backport
from gui.impl.lobby.premacc.premacc_helpers import PiggyBankConstants, getDeltaTimeHelper
from gui.impl.gen import R
from gui.prb_control import prbInvitesProperty
from gui.prb_control.entities.listener import IGlobalListener
from gui.server_events import recruit_helper
from gui.shared import g_eventBus, events
from gui.shared.utils import showInvitationInWindowsBar
from gui.shared.view_helpers.UsersInfoHelper import UsersInfoHelper
from gui.shared.notifications import NotificationPriorityLevel
from gui.shared.formatters import time_formatters
from gui.wgcg.clan.contexts import GetClanInfoCtx
from gui.wgnc import g_wgncProvider, g_wgncEvents, wgnc_settings
from gui.wgnc.settings import WGNC_DATA_PROXY_TYPE
from gui import SystemMessages
from helpers import time_utils, i18n, dependency
from messenger.m_constants import PROTO_TYPE, USER_ACTION_ID
from messenger.proto import proto_getter
from messenger.proto.events import g_messengerEvents
from messenger.proto.xmpp.xmpp_constants import XMPP_ITEM_TYPE
from notification import tutorial_helper
from notification.decorators import MessageDecorator, PrbInviteDecorator, C11nMessageDecorator, FriendshipRequestDecorator, WGNCPopUpDecorator, ClanAppsDecorator, ClanInvitesDecorator, ClanAppActionDecorator, ClanInvitesActionDecorator, ClanSingleAppDecorator, ClanSingleInviteDecorator, ProgressiveRewardDecorator
from notification.settings import NOTIFICATION_TYPE, NOTIFICATION_BUTTON_STATE
from skeletons.gui.game_control import IBootcampController, IGameSessionController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.login_manager import ILoginManager
from skeletons.gui.shared import IItemsCache
from gui.Scaleform.daapi.view.lobby.hangar.seniority_awards import getSeniorityAwardsBoxesCount
from skeletons.new_year import INewYearController

class _FeatureState(object):
    OFF = 0
    ON = 1


_FUNCTION = 'function'

class _StateExtractor(object):
    __lobbyContext = dependency.descriptor(ILobbyContext)

    @classmethod
    def getAdditionalBonusState(cls):
        return cls.__lobbyContext.getServerSettings().getAdditionalBonusConfig().get('enabled')

    @classmethod
    def getPiggyBankState(cls):
        return cls.__lobbyContext.getServerSettings().getPiggyBankConfig().get('enabled')

    @classmethod
    def getPremQuestsState(cls):
        return cls.__lobbyContext.getServerSettings().getPremQuestsConfig().get('enabled')

    @classmethod
    def getSquadPremiumState(cls):
        return cls.__lobbyContext.getServerSettings().squadPremiumBonus.isEnabled

    @classmethod
    def getPreferredMapsState(cls):
        return cls.__lobbyContext.getServerSettings().isPreferredMapsEnabled()


_FEATURES_DATA = {PremiumConfigs.DAILY_BONUS: {_FeatureState.ON: (R.strings.system_messages.daily_xp_bonus.switch_on.title(), R.strings.system_messages.daily_xp_bonus.switch_on.body()),
                              _FeatureState.OFF: (R.strings.system_messages.daily_xp_bonus.switch_off.title(), R.strings.system_messages.daily_xp_bonus.switch_off.body()),
                              _FUNCTION: _StateExtractor.getAdditionalBonusState},
 PremiumConfigs.PREM_SQUAD: {_FeatureState.ON: (R.strings.system_messages.squad_bonus.switch_on.title(), R.strings.system_messages.squad_bonus.switch_on.body()),
                             _FeatureState.OFF: (R.strings.system_messages.squad_bonus.switch_off.title(), R.strings.system_messages.squad_bonus.switch_off.body()),
                             _FUNCTION: _StateExtractor.getSquadPremiumState},
 PremiumConfigs.IS_PREFERRED_MAPS_ENABLED: {_FeatureState.ON: (R.strings.system_messages.maps_black_list.switch_on.title(), R.strings.system_messages.maps_black_list.switch_on.body()),
                                            _FeatureState.OFF: (R.strings.system_messages.maps_black_list.switch_off.title(), R.strings.system_messages.maps_black_list.switch_off.body()),
                                            _FUNCTION: _StateExtractor.getPreferredMapsState},
 PremiumConfigs.PIGGYBANK: {_FeatureState.ON: (R.strings.system_messages.piggybank.switch_on.title(), R.strings.system_messages.piggybank.switch_on.body()),
                            _FeatureState.OFF: (R.strings.system_messages.piggybank.switch_off.title(), R.strings.system_messages.piggybank.switch_off.body()),
                            _FUNCTION: _StateExtractor.getPiggyBankState},
 PremiumConfigs.PREM_QUESTS: {_FeatureState.ON: (R.strings.system_messages.premium_quests.switch_on.title(), R.strings.system_messages.premium_quests.switch_on.body()),
                              _FeatureState.OFF: (R.strings.system_messages.premium_quests.switch_off.title(), R.strings.system_messages.premium_quests.switch_off.body()),
                              _FUNCTION: _StateExtractor.getPremQuestsState}}

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
                addNotification(self.__makeNotification(clientID, formatted, settings, model))

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
            model.addNotification(self.__makeNotification(clientID, formatted, settings, model))

    def __makeNotification(self, clientID, formatted, settings, model):
        messageDecorator = self.__getMessageDecorator(settings.messageType, settings.messageSubtype)
        notification = messageDecorator(clientID, formatted, settings, model)
        return notification

    def __getMessageDecorator(self, messageType, messageSubtype):
        if messageType == SYS_MESSAGE_TYPE.autoMaintenance.index():
            if messageSubtype in (AUTO_MAINTENANCE_RESULT.RENT_IS_OVER, AUTO_MAINTENANCE_RESULT.RENT_IS_ALMOST_OVER):
                return C11nMessageDecorator
        elif messageType == SYS_MESSAGE_TYPE.customizationChanged.index():
            return C11nMessageDecorator
        return MessageDecorator


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
        messengerEvents = g_messengerEvents.users
        messengerEvents.onFriendshipRequestsAdded += self.__me_onFriendshipRequestsAdded
        messengerEvents.onFriendshipRequestsUpdated += self.__me_onFriendshipRequestsUpdated
        messengerEvents.onUserActionReceived += self.__me_onUserActionReceived
        contacts = self.proto.contacts.getFriendshipRqs()
        for contact in contacts:
            self.__setRequest(contact)

        return result

    def stop(self):
        g_messengerEvents.onPluginDisconnected -= self.__me_onPluginDisconnected
        messengerEvents = g_messengerEvents.users
        messengerEvents.onFriendshipRequestsAdded -= self.__me_onFriendshipRequestsAdded
        messengerEvents.onFriendshipRequestsUpdated -= self.__me_onFriendshipRequestsUpdated
        messengerEvents.onUserActionReceived -= self.__me_onUserActionReceived
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

    def __me_onUserActionReceived(self, actionID, contact, shadowMode):
        if contact.getProtoType() != PROTO_TYPE.XMPP:
            return
        if actionID in (USER_ACTION_ID.SUBSCRIPTION_CHANGED, USER_ACTION_ID.IGNORED_ADDED):
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
        pass

    def onClanEnableChanged(self, enabled):
        super(_ClanNotificationsCommonListener, self).onClanEnableChanged(enabled)
        model = self._model()
        if model:
            if not self.webCtrl.isEnabled():
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
        return self._getNotMarkedItemsByType(self._getNewReceivedItemType())

    def _getNotMarkedItemsByType(self, itemType):
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
        return self.webCtrl.isEnabled() and self.webCtrl.getAccountProfile() is not None and self.settingsCore.getSetting('receiveClanInvitesNotifications')

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
        ctx = GetClanInfoCtx(item.getAccountID())
        self.__addUserNotification(ClanSingleAppDecorator, (item.getID(), item), item)
        accountResponse = yield self.webCtrl.sendRequest(ctx)
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
        self._model().addNotification(ClanAppsDecorator(self.webCtrl.getAccountProfile().getClanDbID(), count))

    def _getMultiNotification(self):
        return self._model().getNotification(NOTIFICATION_TYPE.CLAN_APPS, self.webCtrl.getAccountProfile().getClanDbID())

    def _updateAllNotifications(self):
        model = self._model()
        for notifications in model.collection.getListIterator((NOTIFICATION_TYPE.CLAN_APP, NOTIFICATION_TYPE.CLAN_APPS)):
            model.updateNotification(notifications.getType(), notifications.getID(), notifications.getEntity(), False)

    def _removeAllNotifications(self):
        self._removeNotifications((NOTIFICATION_TYPE.CLAN_APP, NOTIFICATION_TYPE.CLAN_APPS, NOTIFICATION_TYPE.CLAN_INVITE_ACTION))

    def _canBeShown(self):
        canBeShown = super(_ClanAppsListener, self)._canBeShown()
        profile = self.webCtrl.getAccountProfile()
        return canBeShown and profile.isInClan() and profile.getMyClanPermissions().canHandleClanInvites()

    def __addUserNotification(self, clazz, args, item):
        userDatabaseID = item.getAccountID()
        appId = item.getID()
        userName = self.getUserName(userDatabaseID)
        if not userName:
            self.__userNamePendingNotifications[userDatabaseID].add(appId)
            self.syncUsersInfo()
            userName = i18n.makeString(CLANS.CLANINVITE_NOTIFICATION_USERNAMEERROR)
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
            profile = self.webCtrl.getAccountProfile()
            if not profile.isInClan():
                self.__updateNotificationsByTypes((NOTIFICATION_TYPE.CLAN_INVITE,))

    def onAccountClanProfileChanged(self, profile):
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
        self._model().addNotification(ClanInvitesDecorator(self.webCtrl.getAccountProfile().getDbID(), count))

    def _getMultiNotification(self):
        return self._model().getNotification(NOTIFICATION_TYPE.CLAN_INVITES, self.webCtrl.getAccountProfile().getDbID())

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
        profile = self.webCtrl.getAccountProfile()
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


class RecruitNotificationListener(_NotificationListener):
    loginManager = dependency.descriptor(ILoginManager)
    _INCREASE_LIMIT_LOGIN = 5

    def start(self, model):
        result = super(RecruitNotificationListener, self).start(model)
        if model is not None and model.getFirstEntry():
            recruits = recruit_helper.getAllRecruitsInfo(sortByExpireTime=True)
            for recruitInfo in recruits:
                if recruitInfo.getExpiryTimeStamp() > 0:
                    self.__pushMessage(len(recruits), recruitInfo.getExpiryTime())
                    break

        return result

    def __pushMessage(self, count, time):
        priority = NotificationPriorityLevel.LOW
        if self.loginManager.getPreference('loginCount') == self._INCREASE_LIMIT_LOGIN:
            priority = NotificationPriorityLevel.MEDIUM
        if time:
            message = i18n.makeString(MESSENGER.SERVICECHANNELMESSAGES_RECRUITREMINDER_TEXT, count=count, date=time)
        else:
            message = i18n.makeString(MESSENGER.SERVICECHANNELMESSAGES_RECRUITREMINDERTERMLESS_TEXT, count=count)
        SystemMessages.pushMessage(message, SystemMessages.SM_TYPE.RecruitReminder, priority=priority)


class ProgressiveRewardListener(_NotificationListener):
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __bootcampController = dependency.descriptor(IBootcampController)

    def __init__(self):
        super(ProgressiveRewardListener, self).__init__()
        self.__isEnabled = None
        return

    def start(self, model):
        super(ProgressiveRewardListener, self).start(model)
        self.__isEnabled = self.__lobbyContext.getServerSettings().getProgressiveRewardConfig().isEnabled
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChange
        g_eventBus.addListener(events.ProgressiveRewardEvent.WIDGET_WAS_SHOWN, self.__widgetWasShown)
        self.__update()
        return True

    def stop(self):
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChange
        g_eventBus.removeListener(events.ProgressiveRewardEvent.WIDGET_WAS_SHOWN, self.__widgetWasShown)
        super(ProgressiveRewardListener, self).stop()

    def __widgetWasShown(self, _):
        model = self._model()
        if model is None:
            return
        else:
            model.removeNotification(NOTIFICATION_TYPE.PROGRESSIVE_REWARD, ProgressiveRewardDecorator.ENTITY_ID)
            if self.__seniorityAwardsIsActive():
                AccountSettings.setCounters(SENIORITY_AWARDS_COUNTER, 1)
            else:
                AccountSettings.setNotifications(PROGRESSIVE_REWARD_VISITED, True)
            return

    def __onServerSettingsChange(self, diff):
        if 'progressive_reward_config' in diff:
            isEnabled = diff['progressive_reward_config'].get('isEnabled', self.__isEnabled)
            if isEnabled != self.__isEnabled:
                priority = NotificationPriorityLevel.MEDIUM
                if isEnabled:
                    SystemMessages.pushMessage(backport.text(R.strings.system_messages.progressiveReward.switch_on()), priority=priority)
                else:
                    SystemMessages.pushMessage(backport.text(R.strings.system_messages.progressiveReward.switch_off()), priority=priority)
                self.__isEnabled = isEnabled
            self.__update()

    def __update(self):
        model = self._model()
        if model is None:
            return
        else:
            model.removeNotificationsByType(NOTIFICATION_TYPE.PROGRESSIVE_REWARD)
            wasVisited = AccountSettings.getNotifications(PROGRESSIVE_REWARD_VISITED)
            if self.__seniorityAwardsIsActive():
                wasVisited = wasVisited and AccountSettings.getCounters(SENIORITY_AWARDS_COUNTER)
            if wasVisited:
                return
            progressiveConfig = self.__lobbyContext.getServerSettings().getProgressiveRewardConfig()
            if not progressiveConfig.isEnabled or self.__bootcampController.isInBootcamp():
                return
            model.addNotification(ProgressiveRewardDecorator())
            return

    def __seniorityAwardsIsActive(self):
        return getSeniorityAwardsBoxesCount() > 0


class SwitcherListener(_NotificationListener):
    slots = ('__currentStates',)
    __lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self):
        super(SwitcherListener, self).__init__()
        self.__currentStates = {}

    def start(self, model):
        super(SwitcherListener, self).start(model)
        self.__fillCurrentStates()
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChange
        return True

    def stop(self):
        self.__currentStates = None
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChange
        super(SwitcherListener, self).stop()
        return

    def __onServerSettingsChange(self, diff):
        for feature, data in _FEATURES_DATA.iteritems():
            if feature in diff:
                isEnabled = data[_FUNCTION]()
                self.__addMessage(feature, isEnabled)
                self.__currentStates[feature] = isEnabled

    def __fillCurrentStates(self):
        for featureName, value in _FEATURES_DATA.iteritems():
            self.__currentStates[featureName] = value[_FUNCTION]()

    def __addMessage(self, featureName, newState):
        if self.__currentStates[featureName] != newState:
            msg = _FEATURES_DATA[featureName]
            if newState:
                SystemMessages.pushMessage(type=SystemMessages.SM_TYPE.PremiumFeatureOn, text=backport.text(msg[_FeatureState.ON][1]), messageData={'header': backport.text(msg[_FeatureState.ON][0])})
            else:
                SystemMessages.pushMessage(type=SystemMessages.SM_TYPE.PremiumFeatureOff, text=backport.text(msg[_FeatureState.OFF][1]), messageData={'header': backport.text(msg[_FeatureState.OFF][0])})


class TankPremiumListener(_NotificationListener):
    __gameSession = dependency.descriptor(IGameSessionController)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __itemsCache = dependency.descriptor(IItemsCache)

    def start(self, model):
        super(TankPremiumListener, self).start(model)
        self.__addListeners()
        return True

    def stop(self):
        super(TankPremiumListener, self).stop()
        self.__removeListeners()

    def __addListeners(self):
        self.__gameSession.onPremiumNotify += self.__onTankPremiumActiveChanged
        g_clientUpdateManager.addCallbacks({PiggyBankConstants.PIGGY_BANK_CREDITS: self.__onPiggyBankCreditsChanged})

    def __removeListeners(self):
        self.__gameSession.onPremiumNotify -= self.__onTankPremiumActiveChanged
        g_clientUpdateManager.removeCallback(PiggyBankConstants.PIGGY_BANK_CREDITS, self.__onPiggyBankCreditsChanged)

    def __onPiggyBankCreditsChanged(self, credits_=None):
        config = self.__lobbyContext.getServerSettings().getPiggyBankConfig()
        maxAmount = config.get('threshold', PiggyBankConstants.MAX_AMOUNT)
        data = self.__itemsCache.items.stats.piggyBank
        if credits_ >= maxAmount:
            timeLeft = time_formatters.getTillTimeByResource(getDeltaTimeHelper(config, data), R.strings.premacc.piggyBankCard.timeLeft)
            SystemMessages.pushMessage(priority=NotificationPriorityLevel.MEDIUM, text=backport.text(R.strings.system_messages.piggyBank.piggyBankFull(), timeValue=timeLeft))

    def __onTankPremiumActiveChanged(self, isPremActive, *_):
        if not isPremActive:
            priority = NotificationPriorityLevel.LOW
            SystemMessages.pushMessage(priority=priority, text=backport.text(R.strings.messenger.serviceChannelMessages.piggyBank.onPause()))


class TalismanNotificationListener(_NotificationListener):
    _itemsCache = dependency.descriptor(IItemsCache)
    _nyController = dependency.descriptor(INewYearController)

    def __init__(self):
        super(TalismanNotificationListener, self).__init__()
        self.__freeTalismans = 0

    def start(self, model):
        result = super(TalismanNotificationListener, self).start(model)
        if self._nyController.getFreeTalisman():
            SystemMessages.pushMessage(backport.text(R.strings.ny.notification.freeTalisman()), SystemMessages.SM_TYPE.TalismanFree)
        if self._nyController.getTalismans(isInInventory=True) and not self._nyController.isTalismanToyTaken():
            SystemMessages.pushMessage(backport.text(R.strings.ny.notification.giftTalisman()), SystemMessages.SM_TYPE.TalismanGift)
        self.__freeTalismans = self._nyController.getFreeTalisman()
        self.__addListeners()
        return result

    def stop(self):
        super(TalismanNotificationListener, self).stop()
        self.__removeListeners()

    def __addListeners(self):
        g_clientUpdateManager.addCallbacks({'tokens': self.__onTokensChanged})

    def __removeListeners(self):
        g_clientUpdateManager.removeCallback('tokens', self.__onTokensChanged)

    def __onTokensChanged(self, _):
        if self._nyController.getFreeTalisman() > self.__freeTalismans:
            SystemMessages.pushMessage(backport.text(R.strings.ny.notification.freeTalisman()), SystemMessages.SM_TYPE.TalismanFree)
        self.__freeTalismans = self._nyController.getFreeTalisman()


class NotificationsListeners(_NotificationListener):

    def __init__(self):
        super(NotificationsListeners, self).__init__()
        self.__listeners = (ServiceChannelListener(),
         PrbInvitesListener(),
         FriendshipRqsListener(),
         _WGNCListenersContainer(),
         BattleTutorialListener(),
         RecruitNotificationListener(),
         ProgressiveRewardListener(),
         SwitcherListener(),
         TankPremiumListener(),
         TalismanNotificationListener())

    def start(self, model):
        for listener in self.__listeners:
            listener.start(model)

    def stop(self):
        for listener in self.__listeners:
            listener.stop()
