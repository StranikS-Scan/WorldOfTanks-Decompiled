# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/notification/listeners.py
import json
import logging
import time
import weakref
from collections import defaultdict
from functools import partial
from typing import TYPE_CHECKING
import WWISE
from PlayerEvents import g_playerEvents
from account_helpers import AccountSettings
from account_helpers.AccountSettings import INTEGRATED_AUCTION_NOTIFICATIONS, IS_BATTLE_PASS_MARATHON_STARTED, TRADING_CARAVAN_NOTIFICATIONS, PROGRESSIVE_REWARD_VISITED, RESOURCE_WELL_END_SHOWN, RESOURCE_WELL_NOTIFICATIONS, RESOURCE_WELL_START_SHOWN, SENIORITY_AWARDS_COINS_REMINDER_SHOWN_TIMESTAMP, ArmoryYard, REFERRAL_PROGRAM_PGB_FULL, BIRTHDAY_2023_INTRO_SHOWN, BattleMatters
from adisp import adisp_process
from armory_yard_constants import State
from battle_pass_common import FinalReward
from chat_shared import SYS_MESSAGE_TYPE
from collector_vehicle import CollectorVehicleConsts
from constants import ARENA_BONUS_TYPE, AUTO_MAINTENANCE_RESULT, DAILY_QUESTS_CONFIG, DOG_TAGS_CONFIG, MAPS_TRAINING_ENABLED_KEY, PLAYER_SUBSCRIPTIONS_CONFIG, PremiumConfigs, SwitchState
from debug_utils import LOG_DEBUG, LOG_ERROR
from gui import SystemMessages
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.view.lobby.referral_program.referral_program_helpers import isReferralProgramEnabled
from gui.Scaleform.locale.CLANS import CLANS
from gui.SystemMessages import SM_TYPE
from gui.battle_pass.battle_pass_helpers import getStyleInfoForChapter
from gui.clans.clan_account_profile import SYNC_KEYS
from gui.clans.clan_helpers import ClanListener, isInClanEnterCooldown
from gui.clans.settings import CLAN_APPLICATION_STATES
from gui.collection.account_settings import isCollectionRenewSeen, isCollectionStartedSeen, isCollectionsUpdatedEntrySeen, setCollectionStartedSeen
from gui.collection.collections_constants import COLLECTIONS_RENEW_EVENT_TYPE, COLLECTIONS_UPDATED_ENTRY_EVENT_TYPE, COLLECTION_START_EVENT_TYPE
from gui.collection.collections_helpers import getCollectionFullFeatureName
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.lobby.premacc.premacc_helpers import PiggyBankConstants, getDeltaTimeHelper
from gui.integrated_auction.constants import AUCTION_FINISH_EVENT_TYPE, AUCTION_FINISH_STAGE_SEEN, AUCTION_STAGE_START_SEEN, AUCTION_START_EVENT_TYPE
from gui.limited_ui.lui_rules_storage import LuiRules
from gui.platform.base.statuses.constants import StatusTypes
from gui.prb_control import prbInvitesProperty
from gui.prb_control.entities.listener import IGlobalListener
from gui.server_events import settings as settings_records
from gui.server_events.recruit_helper import getAllRecruitsInfo
from gui.shared import events, g_eventBus
from gui.shared.formatters import text_styles, time_formatters
from gui.shared.money import Currency
from gui.shared.notifications import NotificationPriorityLevel
from gui.shared.system_factory import collectAllNotificationsListeners, registerNotificationsListeners
from gui.shared.utils import showInvitationInWindowsBar
from gui.shared.utils.scheduled_notifications import SimpleNotifier
from gui.shared.view_helpers.UsersInfoHelper import UsersInfoHelper
from gui.shop_sales_event.constants import TRADING_CARAVAN_REFILL_SEEN, TRADING_CARAVAN_REFILL_EVENT_TYPE
from gui.wgcg.clan.contexts import GetClanInfoCtx
from gui.wgnc import g_wgncEvents, g_wgncProvider, wgnc_settings
from gui.wgnc.settings import WGNC_DATA_PROXY_TYPE
from helpers import dependency, i18n, time_utils
from helpers.events_handler import EventsHandler
from helpers.time_utils import getTimestampByStrDate
from messenger import MessengerEntry
from messenger.formatters import TimeFormatter
from messenger.m_constants import PROTO_TYPE, SCH_CLIENT_MSG_TYPE, USER_ACTION_ID
from messenger.proto import proto_getter
from messenger.proto.events import g_messengerEvents
from messenger.proto.xmpp.xmpp_constants import XMPP_ITEM_TYPE
from notification.decorators import BattlePassLockButtonDecorator, BattlePassSwitchChapterReminderDecorator, C11nMessageDecorator, C2DProgressionStyleDecorator, ClanAppActionDecorator, ClanAppsDecorator, ClanInvitesActionDecorator, ClanInvitesDecorator, ClanSingleAppDecorator, ClanSingleInviteDecorator, CollectionsLockButtonDecorator, EmailConfirmationReminderMessageDecorator, FriendshipRequestDecorator, IntegratedAuctionStageFinishDecorator, IntegratedAuctionStageStartDecorator, LockButtonMessageDecorator, MapboxButtonDecorator, MessageDecorator, MissingEventsDecorator, PrbInviteDecorator, ProgressiveRewardDecorator, RecruitReminderMessageDecorator, ResourceWellLockButtonDecorator, ResourceWellStartDecorator, SeniorityAwardsDecorator, WGNCPopUpDecorator, WinbackSelectableRewardReminderDecorator, WotPlusIntroViewMessageDecorator, BattleMattersReminderDecorator, C11nProgressiveItemDecorator, TradingCaravanRefillDecorator
from notification.settings import NOTIFICATION_TYPE, NotificationData
from shared_utils import first
from skeletons.gui.battle_matters import IBattleMattersController
from skeletons.gui.game_control import IBattlePassController, IBootcampController, ICollectionsSystemController, IEventsNotificationsController, IGameSessionController, ILimitedUIController, IResourceWellController, ISeniorityAwardsController, ISteamCompletionController, IWinbackController, IArmoryYardController, IReferralProgramController, IWotPlusController
from skeletons.gui.goodies import IGoodiesCache
from skeletons.gui.impl import INotificationWindowController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.login_manager import ILoginManager
from skeletons.gui.platform.wgnp_controllers import IWGNPSteamAccRequestController
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from skeletons.gui.system_messages import ISystemMessages
from tutorial.control.game_vars import getVehicleByIntCD
from wg_async import wg_async, wg_await
if TYPE_CHECKING:
    from typing import List, Dict, Optional, Any, Type
    from notification.NotificationsModel import NotificationsModel
    from gui.platform.wgnp.steam_account.statuses import SteamAccEmailStatus
    from collections_common import Collection
_logger = logging.getLogger(__name__)

class _FeatureState(object):
    OFF = 0
    ON = 1


_FUNCTION = 'function'
SERVER_CMD_BP_GAMEMODE_ENABBLED = 'cmd_bp_gamemode_enabled'
SERVER_CMD_BP_EXTRA_FINISH = 'cmd_bp_extra_finish'
SERVER_CMD_BP_EXTRA_WILL_END_SOON = 'cmd_bp_extra_will_end_soon'

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

    @classmethod
    def getDailyQuestsState(cls):
        return cls.__lobbyContext.getServerSettings().getDailyQuestConfig().get('enabled', False)

    @classmethod
    def getCollectorVehicleState(cls):
        return cls.__lobbyContext.getServerSettings().isCollectorVehicleEnabled()

    @classmethod
    def getDogTagsUnlockingState(cls):
        return cls.__lobbyContext.getServerSettings().isDogTagEnabled()

    @classmethod
    def getPlayerSubscriptionsState(cls):
        return cls.__lobbyContext.getServerSettings().isPlayerSubscriptionsEnabled()

    @classmethod
    def getMapsTrainingState(cls):
        return cls.__lobbyContext.getServerSettings().isMapsTrainingEnabled()


_FEATURES_DATA = {PremiumConfigs.DAILY_BONUS: {_FeatureState.ON: (R.strings.system_messages.daily_xp_bonus.switch_on.title(), R.strings.system_messages.daily_xp_bonus.switch_on.body(), SystemMessages.SM_TYPE.FeatureSwitcherOn),
                              _FeatureState.OFF: (R.strings.system_messages.daily_xp_bonus.switch_off.title(), R.strings.system_messages.daily_xp_bonus.switch_off.body(), SystemMessages.SM_TYPE.FeatureSwitcherOff),
                              _FUNCTION: _StateExtractor.getAdditionalBonusState},
 PremiumConfigs.PREM_SQUAD: {_FeatureState.ON: (R.strings.system_messages.squad_bonus.switch_on.title(), R.strings.system_messages.squad_bonus.switch_on.body(), SystemMessages.SM_TYPE.FeatureSwitcherOn),
                             _FeatureState.OFF: (R.strings.system_messages.squad_bonus.switch_off.title(), R.strings.system_messages.squad_bonus.switch_off.body(), SystemMessages.SM_TYPE.FeatureSwitcherOff),
                             _FUNCTION: _StateExtractor.getSquadPremiumState},
 PremiumConfigs.IS_PREFERRED_MAPS_ENABLED: {_FeatureState.ON: (R.strings.system_messages.maps_black_list.switch_on.title(), R.strings.system_messages.maps_black_list.switch_on.body(), SystemMessages.SM_TYPE.FeatureSwitcherOn),
                                            _FeatureState.OFF: (R.strings.system_messages.maps_black_list.switch_off.title(), R.strings.system_messages.maps_black_list.switch_off.body(), SystemMessages.SM_TYPE.FeatureSwitcherOff),
                                            _FUNCTION: _StateExtractor.getPreferredMapsState},
 PremiumConfigs.PIGGYBANK: {_FeatureState.ON: (R.strings.system_messages.piggybank.switch_on.title(), R.strings.system_messages.piggybank.switch_on.body(), SystemMessages.SM_TYPE.FeatureSwitcherOn),
                            _FeatureState.OFF: (R.strings.system_messages.piggybank.switch_off.title(), R.strings.system_messages.piggybank.switch_off.body(), SystemMessages.SM_TYPE.FeatureSwitcherOff),
                            _FUNCTION: _StateExtractor.getPiggyBankState},
 PremiumConfigs.PREM_QUESTS: {_FeatureState.ON: (R.strings.system_messages.premium_quests.switch_on.title(), R.strings.system_messages.premium_quests.switch_on.body(), SystemMessages.SM_TYPE.FeatureSwitcherOn),
                              _FeatureState.OFF: (R.strings.system_messages.premium_quests.switch_off.title(), R.strings.system_messages.premium_quests.switch_off.body(), SystemMessages.SM_TYPE.FeatureSwitcherOff),
                              _FUNCTION: _StateExtractor.getPremQuestsState},
 DAILY_QUESTS_CONFIG: {_FeatureState.ON: (R.strings.system_messages.daily_quests.switch_on.title(), R.strings.system_messages.daily_quests.switch_on.body(), SystemMessages.SM_TYPE.FeatureSwitcherOn),
                       _FeatureState.OFF: (R.strings.system_messages.daily_quests.switch_off.title(), R.strings.system_messages.daily_quests.switch_off.body(), SystemMessages.SM_TYPE.FeatureSwitcherOff),
                       _FUNCTION: _StateExtractor.getDailyQuestsState},
 CollectorVehicleConsts.CONFIG_NAME: {_FeatureState.ON: (R.strings.system_messages.collectorVehicle.switch_on.title(), R.strings.system_messages.collectorVehicle.switch_on.body(), SystemMessages.SM_TYPE.FeatureSwitcherOn),
                                      _FeatureState.OFF: (R.strings.system_messages.collectorVehicle.switch_off.title(), R.strings.system_messages.collectorVehicle.switch_off.body(), SystemMessages.SM_TYPE.FeatureSwitcherOff),
                                      _FUNCTION: _StateExtractor.getCollectorVehicleState},
 DOG_TAGS_CONFIG: {_FeatureState.ON: (R.strings.system_messages.dog_tags.switch_on.title(), R.strings.system_messages.dog_tags.switch_on.body(), SystemMessages.SM_TYPE.FeatureSwitcherOn),
                   _FeatureState.OFF: (R.strings.system_messages.dog_tags.switch_off.title(), R.strings.system_messages.dog_tags.switch_off.body(), SystemMessages.SM_TYPE.FeatureSwitcherOff),
                   _FUNCTION: _StateExtractor.getDogTagsUnlockingState},
 PLAYER_SUBSCRIPTIONS_CONFIG: {_FeatureState.ON: (R.strings.system_messages.player_subscriptions.switch_on.title(), R.strings.system_messages.player_subscriptions.switch_on.body(), SystemMessages.SM_TYPE.FeatureSwitcherOn),
                               _FeatureState.OFF: (R.strings.system_messages.player_subscriptions.switch_off.title(), R.strings.system_messages.player_subscriptions.switch_off.body(), SystemMessages.SM_TYPE.FeatureSwitcherOff),
                               _FUNCTION: _StateExtractor.getPlayerSubscriptionsState},
 MAPS_TRAINING_ENABLED_KEY: {_FeatureState.ON: (R.strings.system_messages.maps_training.switch.title(), R.strings.system_messages.maps_training.switch_on.body(), SystemMessages.SM_TYPE.FeatureSwitcherOn),
                             _FeatureState.OFF: (R.strings.system_messages.maps_training.switch.title(), R.strings.system_messages.maps_training.switch_off.body(), SystemMessages.SM_TYPE.FeatureSwitcherOff),
                             _FUNCTION: _StateExtractor.getMapsTrainingState}}

class _NotificationListener(object):

    def __init__(self):
        super(_NotificationListener, self).__init__()

        def model():
            pass

        self._model = model

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
        messageDecorator = self.__getMessageDecorator(settings, settings.messageType, settings.messageSubtype)
        notification = messageDecorator(clientID, formatted, settings, model)
        return notification

    def __isCollectionsSysMessageTypes(self, messageType):
        return messageType in (SYS_MESSAGE_TYPE.collectionsItems.index(), SYS_MESSAGE_TYPE.collectionsReward.index())

    def __isCollectionsSMType(self, settings):
        auxData = getattr(settings, 'auxData', (None,))
        return SM_TYPE.lookup(auxData[0]) in (SM_TYPE.CollectionsEntry, SM_TYPE.CollectionRenew, SM_TYPE.CollectionStart) if auxData else None

    def __getMessageDecorator(self, settings, messageType, messageSubtype):
        if settings.decorator is not None:
            return settings.decorator
        else:
            if messageType == SYS_MESSAGE_TYPE.autoMaintenance.index():
                if messageSubtype in (AUTO_MAINTENANCE_RESULT.RENT_IS_OVER, AUTO_MAINTENANCE_RESULT.RENT_IS_ALMOST_OVER):
                    return C11nMessageDecorator
            else:
                if messageType == SYS_MESSAGE_TYPE.customizationChanged.index():
                    return C11nMessageDecorator
                if messageType == SYS_MESSAGE_TYPE.customizationProgress.index():
                    return C11nProgressiveItemDecorator
                if messageType == SYS_MESSAGE_TYPE.personalMissionFailed.index():
                    return LockButtonMessageDecorator
                if messageType == SYS_MESSAGE_TYPE.battlePassReward.index():
                    return BattlePassLockButtonDecorator
                if messageSubtype in (SCH_CLIENT_MSG_TYPE.MAPBOX_PROGRESSION_REWARD, SCH_CLIENT_MSG_TYPE.MAPBOX_SURVEY_AVAILABLE):
                    return MapboxButtonDecorator
                if messageType == SYS_MESSAGE_TYPE.resourceWellNoVehicles.index():
                    return ResourceWellLockButtonDecorator
                if messageType == SYS_MESSAGE_TYPE.customization2dProgressionChanged.index():
                    return C2DProgressionStyleDecorator
                if self.__isCollectionsSysMessageTypes(messageType) or self.__isCollectionsSMType(settings):
                    return CollectionsLockButtonDecorator
            return MessageDecorator


class BaseReminderListener(_NotificationListener):

    def __init__(self, notificationType, notificationId):
        super(BaseReminderListener, self).__init__()
        self.__notificationType = notificationType
        self.__notificationId = notificationId

    def _notifyOrRemove(self, isAdding, isStateChanged=False, **ctx):
        if isAdding:
            return self._notify(isStateChanged, **ctx)
        self._removeNotification()
        return False

    def _createNotificationData(self, **ctx):
        return None

    def _createDecorator(self, notificationData):
        raise NotImplementedError

    def _getNotificationType(self):
        return self.__notificationType

    def _getNotificationId(self):
        return self.__notificationId

    def _cmpNotifications(self, new, prev):
        return False

    def _removeNotification(self):
        model = self._model()
        if model:
            model.removeNotification(self._getNotificationType(), self._getNotificationId())

    def _notify(self, isStateChanged=False, **ctx):
        model = self._model()
        if not model:
            return False
        data = self._createNotificationData(**ctx)
        notification = self._createDecorator(data)
        prevNotification = model.getNotification(self._getNotificationType(), notification.getID())
        if prevNotification is None:
            model.addNotification(notification)
            return True
        elif not self._cmpNotifications(notification, prevNotification):
            model.updateNotification(notification.getType(), notification.getID(), notification.getEntity(), isStateChanged)
            return True
        else:
            return False


class MissingEventsListener(_NotificationListener):
    __notificationMgr = dependency.descriptor(INotificationWindowController)

    def start(self, model):
        result = super(MissingEventsListener, self).start(model)
        self.__notificationMgr.onPostponedQueueUpdated += self.__onQueueUpdated
        return result

    def stop(self):
        super(MissingEventsListener, self).stop()
        self.__notificationMgr.onPostponedQueueUpdated -= self.__onQueueUpdated

    def __onQueueUpdated(self, count, isInBootcamp):
        model = self._model()
        if model is not None:
            model.removeNotification(NOTIFICATION_TYPE.MISSING_EVENTS, MissingEventsDecorator.ENTITY_ID)
            if not isInBootcamp and count > 0:
                model.addNotification(MissingEventsDecorator(count))
        return


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
            g_clientUpdateManager.addCallbacks({'inventory.1': self.__onInventoryUpdated})
            g_clientUpdateManager.addCallbacks({'stats.unlocks': self.__onInventoryUpdated})
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
            g_clientUpdateManager.removeObjectCallbacks(self)

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

    def __onInventoryUpdated(self, *_):
        self.__updateInvites()

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

    @adisp_process
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
            if wasVisited:
                return
            progressiveConfig = self.__lobbyContext.getServerSettings().getProgressiveRewardConfig()
            if not progressiveConfig.isEnabled or self.__bootcampController.isInBootcamp():
                return
            model.addNotification(ProgressiveRewardDecorator())
            return


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
                msgTitle, msgBody, msgType = msg[_FeatureState.ON]
                SystemMessages.pushMessage(type=msgType, text=backport.text(msgBody), messageData={'header': backport.text(msgTitle)})
            else:
                msgTitle, msgBody, msgType = msg[_FeatureState.OFF]
                SystemMessages.pushMessage(type=msgType, text=backport.text(msgBody), messageData={'header': backport.text(msgTitle)})


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
        maxAmount = config.get('creditsThreshold', PiggyBankConstants.MAX_AMOUNT)
        data = self.__itemsCache.items.stats.piggyBank
        if credits_ >= maxAmount:
            timeLeft = time_formatters.getTillTimeByResource(getDeltaTimeHelper(config, data), R.strings.premacc.piggyBankCard.timeLeft)
            SystemMessages.pushMessage(priority=NotificationPriorityLevel.MEDIUM, text=backport.text(R.strings.system_messages.piggyBank.piggyBankFull(), timeValue=timeLeft))

    def __onTankPremiumActiveChanged(self, isPremActive, *_):
        if not isPremActive:
            priority = NotificationPriorityLevel.LOW
            SystemMessages.pushMessage(priority=priority, text=backport.text(R.strings.messenger.serviceChannelMessages.piggyBank.onPause()))


class BattlePassListener(_NotificationListener):
    __slots__ = ('__isStarted', '__isFinished', '__arenaBonusTypesEnabledState', '__arenaBonusTypesHandlers')
    __battlePassController = dependency.descriptor(IBattlePassController)
    __itemsCache = dependency.descriptor(IItemsCache)
    __notificationCtrl = dependency.descriptor(IEventsNotificationsController)
    __luiController = dependency.descriptor(ILimitedUIController)

    def __init__(self):
        super(BattlePassListener, self).__init__()
        self.__isStarted = None
        self.__isFinished = None
        self.__arenaBonusTypesEnabledState = None
        self.__arenaBonusTypesHandlers = None
        return

    def start(self, model):
        super(BattlePassListener, self).start(model)
        self.__isStarted = self.__battlePassController.isActive()
        self.__isFinished = self.__battlePassController.isSeasonFinished()
        self.__arenaBonusTypesHandlers = {ARENA_BONUS_TYPE.RANKED: self.__pushEnableChangeRanked,
         ARENA_BONUS_TYPE.BATTLE_ROYALE_SOLO: self.__pushBattleRoyaleEnableChange,
         ARENA_BONUS_TYPE.EPIC_BATTLE: self.__pushEpicBattleModeChanged,
         ARENA_BONUS_TYPE.COMP7: self.__pushComp7ModeChanged}
        self.__battlePassController.onSeasonStateChanged += self.__onSeasonStateChange
        self.__battlePassController.onBattlePassSettingsChange += self.__onBattlePassSettingsChange
        self.__notificationCtrl.onEventNotificationsChanged += self.__onEventNotification
        self.__initArenaBonusTypeEnabledStates()
        return True

    def stop(self):
        self.__battlePassController.onSeasonStateChanged -= self.__onSeasonStateChange
        self.__battlePassController.onBattlePassSettingsChange -= self.__onBattlePassSettingsChange
        self.__notificationCtrl.onEventNotificationsChanged -= self.__onEventNotification
        self.__arenaBonusTypesHandlers = None
        super(BattlePassListener, self).stop()
        return

    def __onEventNotification(self, added, removed=()):
        if not self.__battlePassController.isActive():
            return
        for eventNotification in added:
            msgType = eventNotification.eventType
            if msgType == SERVER_CMD_BP_GAMEMODE_ENABBLED:
                self.__notifyGamemodeEnabled(eventNotification)
            if msgType == SERVER_CMD_BP_EXTRA_FINISH:
                self.__notifyFinishExtra(eventNotification.data)
            if msgType == SERVER_CMD_BP_EXTRA_WILL_END_SOON:
                self.__notifyExtraWillEndSoon(eventNotification.data)

    def __onBattlePassSettingsChange(self, newMode, oldMode):
        self.__checkAndNotify(oldMode, newMode)
        if self.__battlePassController.isEnabled() and newMode == oldMode:
            self.__checkAndNotifyOtherBattleTypes()
        if self.__battlePassController.hasMarathon() and not AccountSettings.getSettings(IS_BATTLE_PASS_MARATHON_STARTED) and self.__battlePassController.isActive():
            AccountSettings.setSettings(IS_BATTLE_PASS_MARATHON_STARTED, True)
            chapterID = self.__battlePassController.getMarathonChapterID()
            if chapterID:
                self.__notifyStartExtra(chapterID)

    def __onSeasonStateChange(self):
        self.__checkAndNotify()

    def __notifyGamemodeEnabled(self, eventNotification):
        arenaBonusType = eventNotification.data
        header = backport.text(R.strings.system_messages.battlePass.gameModeEnabled.header(), seasonNum=self.__battlePassController.getSeasonNum())
        textRes = R.strings.system_messages.battlePass.gameModeEnabled.body.num(arenaBonusType)
        if not textRes.exists():
            _logger.warning('There is no text for given arenaBonusType: %d', arenaBonusType)
            return
        text = backport.text(textRes())
        SystemMessages.pushMessage(text=text, type=SystemMessages.SM_TYPE.BattlePassGameModeEnabled, messageData={'header': header})

    def __notifyStartExtra(self, chapterID):
        if not self.__luiController.isRuleCompleted(LuiRules.SYS_MSG_COLLECTION_START_BP):
            return
        header = backport.text(R.strings.system_messages.battlePass.marathonStarted.header())
        chapterName = backport.text(R.strings.battle_pass.chapter.fullName.num(chapterID)())
        SystemMessages.pushMessage(text=backport.text(R.strings.system_messages.battlePass.marathonStarted.body(), name=chapterName), priority=NotificationPriorityLevel.HIGH, type=SM_TYPE.BattlePassMarathonStart, messageData={'header': header})

    def __notifyFinishExtra(self, chapterID):
        if not self.__luiController.isRuleCompleted(LuiRules.SYS_MSG_COLLECTION_START_BP):
            return
        chapterID = int(chapterID)
        textRes = R.strings.battle_pass.chapter.fullName.num(chapterID)
        if not textRes.exists():
            _logger.warning('There is no text for given chapterID: %d', chapterID)
            return
        chapterName = backport.text(textRes())
        header = backport.text(R.strings.system_messages.battlePass.marathonFinish.header(), name=chapterName)
        text = backport.text(R.strings.system_messages.battlePass.marathonFinish.body(), name=chapterName)
        SystemMessages.pushMessage(text=text, type=SM_TYPE.BattlePassMarathonFinish, messageData={'header': header})

    def __notifyExtraWillEndSoon(self, chapterID):
        if not self.__luiController.isRuleCompleted(LuiRules.SYS_MSG_COLLECTION_START_BP):
            return
        chapterID = int(chapterID)
        textRes = R.strings.battle_pass.chapter.fullName.num(chapterID)
        if not textRes.exists() or not self.__battlePassController.isChapterExists(chapterID):
            _logger.warning('There is no text or config for given chapterID: %d', chapterID)
            return
        chapterName = backport.text(textRes())
        header = backport.text(R.strings.system_messages.battlePass.marathonWillEndSoon.header(), name=chapterName)
        text = backport.text(R.strings.system_messages.battlePass.marathonWillEndSoon.body(), name=chapterName)
        SystemMessages.pushMessage(text=text, type=SM_TYPE.BattlePassMarathonWillEndSoon, messageData={'header': header})

    def __checkAndNotifyOtherBattleTypes(self):
        supportedTypes = self.__battlePassController.getSupportedArenaBonusTypes()
        for arenaBonusType in supportedTypes:
            oldValue = self.__arenaBonusTypesEnabledState.get(arenaBonusType, False)
            newValue = self.__battlePassController.isGameModeEnabled(arenaBonusType)
            self.__arenaBonusTypesEnabledState[arenaBonusType] = newValue
            if oldValue != newValue and self.__luiController.isRuleCompleted(LuiRules.SYS_MSG_COLLECTION_START_BP):
                self.__pushEnableChangedForArenaBonusType(arenaBonusType, newValue)

    def __checkAndNotify(self, oldMode=None, newMode=None):
        isStarted = self.__battlePassController.isActive()
        isFinished = self.__battlePassController.isSeasonFinished()
        isModeChanged = oldMode is not None and newMode is not None and oldMode != newMode
        isReactivated = newMode == 'enabled' and oldMode == 'paused'
        isEnabledByLUI = self.__luiController.isRuleCompleted(LuiRules.SYS_MSG_COLLECTION_START_BP)
        needToPushStarted = self.__isStarted != isStarted and isStarted and not isReactivated
        if isEnabledByLUI:
            if needToPushStarted:
                self.__pushStarted()
            elif self.__isFinished != isFinished and isFinished or isModeChanged and newMode == 'disabled':
                self.__pushFinished()
            if isModeChanged:
                if newMode == 'paused':
                    self.__pushPause()
                elif isReactivated:
                    self.__pushEnabled()
        if needToPushStarted:
            self.__initArenaBonusTypeEnabledStates()
        self.__isStarted = isStarted
        self.__isFinished = isFinished
        return

    @staticmethod
    def __pushPause():
        SystemMessages.pushMessage(text=backport.text(R.strings.system_messages.battlePass.switch_pause.body()), type=SystemMessages.SM_TYPE.ErrorSimple, priority=NotificationPriorityLevel.HIGH)

    def __pushFinished(self):
        styles = []
        for chapterID in self.__battlePassController.getChapterIDs():
            if self.__battlePassController.getRewardType(chapterID) == FinalReward.STYLE:
                styleCD, styleLevel = getStyleInfoForChapter(chapterID)
                style = self.__itemsCache.items.getItemByCD(styleCD)
                if style.fullInventoryCount() and styleLevel != style.getMaxProgressionLevel():
                    styles.append(backport.text(R.strings.system_messages.battlePass.switch_disable.incompleteStyle(), styleName=style.userName))

        SystemMessages.pushMessage(text=backport.text(R.strings.system_messages.battlePass.switch_disable.body()), priority=NotificationPriorityLevel.HIGH, type=SystemMessages.SM_TYPE.BattlePassInfo, messageData={'header': backport.text(R.strings.system_messages.battlePass.switch_disable.title(), seasonNum=self.__battlePassController.getSeasonNum()),
         'additionalText': '\n'.join(styles)})

    def __pushStarted(self):
        SystemMessages.pushMessage(text=backport.text(R.strings.system_messages.battlePass.switch_started.style.body()), priority=NotificationPriorityLevel.HIGH, type=SystemMessages.SM_TYPE.BattlePassInfo, messageData={'header': backport.text(R.strings.system_messages.battlePass.switch_started.style.title(), seasonNum=self.__battlePassController.getSeasonNum()),
         'additionalText': ''})

    def __pushEnabled(self):
        expiryTime = self.__battlePassController.getSeasonFinishTime()
        SystemMessages.pushMessage(text=backport.text(R.strings.system_messages.battlePass.switch_enabled.body(), expiryTime=text_styles.titleFont(TimeFormatter.getLongDatetimeFormat(expiryTime))), priority=NotificationPriorityLevel.HIGH, type=SystemMessages.SM_TYPE.Warning)

    @staticmethod
    def __pushBattleRoyaleEnableChange(isEnabled):
        if not isEnabled:
            SystemMessages.pushMessage(text=backport.text(R.strings.system_messages.battlePass.switch_disable.battle_royale.body()), type=SystemMessages.SM_TYPE.Warning)

    def __pushEnableChangedForArenaBonusType(self, arenaBonusType, newValue):
        if arenaBonusType in self.__arenaBonusTypesHandlers:
            self.__arenaBonusTypesHandlers[arenaBonusType](newValue)

    @staticmethod
    def __pushEnableChangeRanked(isEnabled):
        if isEnabled:
            msg = backport.text(R.strings.system_messages.battlePass.switch_enabled.ranked.body())
            msgType = SystemMessages.SM_TYPE.Warning
        else:
            msg = backport.text(R.strings.system_messages.battlePass.switch_disable.ranked.body())
            msgType = SystemMessages.SM_TYPE.ErrorSimple
        SystemMessages.pushMessage(text=msg, type=msgType)

    def __initArenaBonusTypeEnabledStates(self):
        self.__arenaBonusTypesEnabledState = {}
        supportedTypes = self.__battlePassController.getSupportedArenaBonusTypes()
        for arenaBonusType in supportedTypes:
            self.__arenaBonusTypesEnabledState[arenaBonusType] = self.__battlePassController.isGameModeEnabled(arenaBonusType)

    @staticmethod
    def __pushEpicBattleModeChanged(isEnabled):
        if isEnabled:
            msg = backport.text(R.strings.system_messages.battlePass.switch_enabled.epicBattle.body())
            msgType = SystemMessages.SM_TYPE.Warning
        else:
            msg = backport.text(R.strings.system_messages.battlePass.switch_disable.epicBattle.body())
            msgType = SystemMessages.SM_TYPE.ErrorSimple
        SystemMessages.pushMessage(text=msg, type=msgType)

    @staticmethod
    def __pushComp7ModeChanged(isEnabled):
        if isEnabled:
            msg = backport.text(R.strings.system_messages.battlePass.switch_enabled.comp7.body())
            msgType = SystemMessages.SM_TYPE.Warning
        else:
            msg = backport.text(R.strings.system_messages.battlePass.switch_disable.comp7.body())
            msgType = SystemMessages.SM_TYPE.ErrorSimple
        SystemMessages.pushMessage(text=msg, type=msgType)


class BattlePassSwitchChapterReminder(BaseReminderListener):
    __battlePassController = dependency.descriptor(IBattlePassController)
    __luiController = dependency.descriptor(ILimitedUIController)
    __ENTITY_ID = 0

    def __init__(self):
        super(BattlePassSwitchChapterReminder, self).__init__(NOTIFICATION_TYPE.BATTLE_PASS_SWITCH_CHAPTER_REMINDER, self.__ENTITY_ID)

    def start(self, model):
        result = super(BattlePassSwitchChapterReminder, self).start(model)
        if result:
            self.__addListeners()
            self.__tryNotify()
        return result

    def stop(self):
        self.__removeListeners()
        super(BattlePassSwitchChapterReminder, self).stop()

    def _createDecorator(self, _):
        return BattlePassSwitchChapterReminderDecorator(self._getNotificationId(), backport.text(R.strings.system_messages.battlePass.switchChapter.reminder()))

    def __addListeners(self):
        self.__battlePassController.onChapterChanged += self.__tryNotify
        self.__battlePassController.onBattlePassSettingsChange += self.__tryNotify
        self.__battlePassController.onPointsUpdated += self.__tryNotify
        self.__luiController.startObserve(LuiRules.BP_ENTRY, self.__updateBattlePassEntryVisibility)

    def __removeListeners(self):
        self.__battlePassController.onChapterChanged -= self.__tryNotify
        self.__battlePassController.onBattlePassSettingsChange -= self.__tryNotify
        self.__battlePassController.onPointsUpdated -= self.__tryNotify
        self.__luiController.stopObserve(LuiRules.BP_ENTRY, self.__updateBattlePassEntryVisibility)

    def __tryNotify(self, *_):
        isAdding = not (self.__battlePassController.hasActiveChapter() or self.__battlePassController.isCompleted() or self.__battlePassController.isDisabled())
        isAdding &= self.__luiController.isRuleCompleted(LuiRules.BP_ENTRY)
        self._notifyOrRemove(isAdding)

    def __updateBattlePassEntryVisibility(self, *_):
        self.__tryNotify()


class UpgradeTrophyDeviceListener(_NotificationListener):
    __slots__ = ('__enabled',)
    __lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self):
        super(UpgradeTrophyDeviceListener, self).__init__()
        self.__enabled = None
        return

    def start(self, model):
        super(UpgradeTrophyDeviceListener, self).start(model)
        self.__enabled = self.__lobbyContext.getServerSettings().isTrophyDevicesEnabled()
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChange
        return True

    def stop(self):
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChange
        super(UpgradeTrophyDeviceListener, self).stop()

    def __onServerSettingsChange(self, diff):
        if 'isTrophyDevicesEnabled' in diff and self.__enabled != diff['isTrophyDevicesEnabled']:
            self.__enabled = diff['isTrophyDevicesEnabled']
            if self.__enabled:
                SystemMessages.pushMessage(text=backport.text(R.strings.system_messages.upgradeTrophyDevice.switch_on.body()), priority=NotificationPriorityLevel.MEDIUM)
            else:
                SystemMessages.pushMessage(text=backport.text(R.strings.system_messages.upgradeTrophyDevice.switch_off.body()), type=SystemMessages.SM_TYPE.ErrorSimple, priority=NotificationPriorityLevel.MEDIUM)


class RecertificationFormStateListener(_NotificationListener):
    __slots__ = ('_state',)
    __goodiesCache = dependency.descriptor(IGoodiesCache)
    __lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self):
        super(RecertificationFormStateListener, self).__init__()
        self._state = None
        return

    def start(self, model):
        super(RecertificationFormStateListener, self).start(model)
        self._state = self._getState()
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChange
        return True

    def stop(self):
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChange
        super(RecertificationFormStateListener, self).stop()

    def _getState(self):
        return SwitchState.DISABLED.value if not self.__goodiesCache.getRecertificationForm(currency='gold').enabled else self.__lobbyContext.getServerSettings().recertificationFormState()

    def __onServerSettingsChange(self, diff):
        newSwitchState = diff.get('recertificationFormState')
        if newSwitchState is None:
            return
        else:
            newState = self._getState()
            if self._state == newState:
                return
            if self._state != SwitchState.DISABLED.value and newState != SwitchState.DISABLED.value:
                action = {'sentTime': time.time(),
                 'data': {'type': SYS_MESSAGE_TYPE.recertificationAvailability.index(),
                          'data': {'state': newState}}}
                MessengerEntry.g_instance.protos.BW.serviceChannel.onReceivePersonalSysMessage(action)
            self._state = newState
            return


class RecruitReminderListener(BaseReminderListener):
    __loginManager = dependency.descriptor(ILoginManager)
    __bootCampController = dependency.descriptor(IBootcampController)
    __eventsCache = dependency.descriptor(IEventsCache)
    __ENTITY_ID = 0
    _INCREASE_LIMIT_LOGIN = 5

    def __init__(self):
        super(RecruitReminderListener, self).__init__(NOTIFICATION_TYPE.RECRUIT_REMINDER, self.__ENTITY_ID)

    def start(self, model):
        result = super(RecruitReminderListener, self).start(model)
        if result:
            g_clientUpdateManager.addCallbacks({'tokens': self.__tryNotify})
            self.__eventsCache.onProgressUpdated += self.__tryNotify
            self.__tryNotify(None)
        return result

    def stop(self):
        super(RecruitReminderListener, self).stop()
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.__eventsCache.onProgressUpdated -= self.__tryNotify

    def _createNotificationData(self, recruits=None, **ctx):
        entityID = self._getNotificationId()
        recruitsCount = 0
        expiryTime = ''
        priorityLevel = NotificationPriorityLevel.LOW
        if recruits:
            recruitsCount = len(recruits)
            expiryTime = first(recruits).getExpiryTime()
            lc = self.__loginManager.getPreference('loginCount')
            if lc == self._INCREASE_LIMIT_LOGIN:
                priorityLevel = NotificationPriorityLevel.MEDIUM
        savedData = {'count': recruitsCount,
         'expiryTime': expiryTime}
        return NotificationData(entityID, savedData, priorityLevel, None)

    def _createDecorator(self, notificationData):
        rMessage = R.strings.messenger.serviceChannelMessages
        messageTemplate = rMessage.recruitReminderTermless.text()
        recruitsCount = notificationData.savedData.get('count')
        expiryTime = notificationData.savedData.get('expiryTime')
        if expiryTime:
            messageTemplate = rMessage.recruitReminder.text()
        message = backport.text(messageTemplate, count=recruitsCount, date=expiryTime)
        return RecruitReminderMessageDecorator(notificationData.entityID, message, notificationData.savedData, notificationData.priorityLevel)

    def _cmpNotifications(self, new, prev):
        return new.getSavedData().get('count') == prev.getSavedData().get('count')

    def __tryNotify(self, _):
        if self.__bootCampController.isInBootcamp():
            return
        recruits = getAllRecruitsInfo(sortByExpireTime=True)
        isAdding = len(recruits) > 0
        self._notifyOrRemove(isAdding, recruits=recruits)


class EmailConfirmationReminderListener(BaseReminderListener):
    __bootCampController = dependency.descriptor(IBootcampController)
    __wgnpSteamAccCtrl = dependency.descriptor(IWGNPSteamAccRequestController)
    __steamRegistrationCtrl = dependency.descriptor(ISteamCompletionController)
    __ENTITY_ID = 0

    def __init__(self):
        super(EmailConfirmationReminderListener, self).__init__(NOTIFICATION_TYPE.EMAIL_CONFIRMATION_REMINDER, self.__ENTITY_ID)

    def start(self, model):
        result = super(EmailConfirmationReminderListener, self).start(model)
        if result:
            g_playerEvents.onBattleResultsReceived += self.__tryNotify
            self.__wgnpSteamAccCtrl.statusEvents.subscribe(StatusTypes.CONFIRMED, self.__removeNotify)
            self.__wgnpSteamAccCtrl.statusEvents.subscribe(StatusTypes.ADD_NEEDED, self.__removeNotify)
            self.__tryNotify()
        return result

    def stop(self):
        super(EmailConfirmationReminderListener, self).stop()
        g_playerEvents.onBattleResultsReceived -= self.__tryNotify
        self.__wgnpSteamAccCtrl.statusEvents.unsubscribe(StatusTypes.CONFIRMED, self.__removeNotify)
        self.__wgnpSteamAccCtrl.statusEvents.unsubscribe(StatusTypes.ADD_NEEDED, self.__removeNotify)

    def _createDecorator(self, _):
        return EmailConfirmationReminderMessageDecorator(self._getNotificationId(), backport.text(R.strings.messenger.serviceChannelMessages.emailConfirmationReminder.text()))

    @wg_async
    def __tryNotify(self, *args):
        if self.__bootCampController.isInBootcamp() or not self.__steamRegistrationCtrl.isSteamAccount:
            return
        status = yield wg_await(self.__wgnpSteamAccCtrl.getEmailStatus())
        if not self.__bootCampController.isInBootcamp() and status.typeIs(StatusTypes.ADDED):
            self._notify()

    def __removeNotify(self, status=None):
        self._removeNotification()


class VehiclePostProgressionUnlockListener(_NotificationListener):
    __itemsCache = dependency.descriptor(IItemsCache)

    def start(self, model):
        super(VehiclePostProgressionUnlockListener, self).start(model)
        g_playerEvents.onVehicleBecomeElite += self.__onVehicleBecomeElite
        return True

    def stop(self):
        g_playerEvents.onVehicleBecomeElite -= self.__onVehicleBecomeElite
        super(VehiclePostProgressionUnlockListener, self).stop()

    def __onVehicleBecomeElite(self, *vehicleIntCDs):
        msgKey = R.strings.system_messages.vehiclePostProgression.vehiclesUnlockPostProgression
        for intCD in vehicleIntCDs:
            vehicle = self.__itemsCache.items.getItemByCD(intCD)
            if vehicle is not None and vehicle.postProgressionAvailability(unlockOnly=True):
                SystemMessages.pushMessage(text=backport.text(msgKey.single.body(), vehicle=vehicle.userName), type=SM_TYPE.InformationHeader, priority=NotificationPriorityLevel.HIGH, messageData={'header': backport.text(msgKey.title())})

        return


class SeniorityAwardsTokenListener(BaseReminderListener):
    __itemsCache = dependency.descriptor(IItemsCache)
    __seniorityAwardCtrl = dependency.descriptor(ISeniorityAwardsController)
    __bootCampController = dependency.descriptor(IBootcampController)
    __TYPE = NOTIFICATION_TYPE.SENIORITY_AWARDS_TOKENS
    __ENTITY_ID = 0
    __TEMPLATE = 'seniorityAwardsTokens'

    def __init__(self):
        super(SeniorityAwardsTokenListener, self).__init__(self.__TYPE, self.__ENTITY_ID)

    def start(self, model):
        result = super(SeniorityAwardsTokenListener, self).start(model)
        if result:
            self.__seniorityAwardCtrl.onUpdated += self.__onUpdated
            g_clientUpdateManager.addCallbacks({'cache.dynamicCurrencies.sacoin': self.__onBalanceUpdate})
            self.__tryNotify()
        return result

    def stop(self):
        super(SeniorityAwardsTokenListener, self).stop()
        self.__seniorityAwardCtrl.onUpdated -= self.__onUpdated
        g_clientUpdateManager.removeObjectCallbacks(self)

    def _createNotificationData(self, priority, **ctx):
        timestamp = time_utils.getServerUTCTime()
        count = self.__seniorityAwardCtrl.getSACoin()
        isClockOn = timestamp - self.__seniorityAwardCtrl.clockOnNotification > 0
        timeLeft = self.__seniorityAwardCtrl.timeLeft
        if isClockOn and timeLeft > 0:
            rTimeLeft = R.strings.seniority_awards.notifications.tokens.timer()
            timeLeftStr = time_formatters.getTillTimeByResource(timeLeft, R.strings.seniority_awards.notifications.tokens.timeLeft, removeLeadingZeros=True)
            finishTime = text_styles.tutorial(backport.text(rTimeLeft, timeLeft=timeLeftStr))
        else:
            finishTime = ''
        data = {'count': str(count),
         'finishTime': finishTime}
        return NotificationData(self._getNotificationId(), data, priority, None)

    def _createDecorator(self, data):
        return SeniorityAwardsDecorator(data.entityID, self._getNotificationType(), data.savedData, self._model(), self.__TEMPLATE, data.priorityLevel)

    def __onBalanceUpdate(self, *_):
        self.__tryNotify()

    def __onUpdated(self):
        self.__tryNotify()

    def __tryNotify(self):
        if self.__bootCampController.isInBootcamp():
            return
        else:
            coinsCount = self.__seniorityAwardCtrl.getSACoin()
            if coinsCount < 1 or not self.__seniorityAwardCtrl.isEnabled or self.__seniorityAwardCtrl.timeLeft <= 0:
                self._removeNotification()
                return
            lastShownTime = AccountSettings.getNotifications(SENIORITY_AWARDS_COINS_REMINDER_SHOWN_TIMESTAMP)
            if lastShownTime is None:
                if self.__seniorityAwardCtrl.isRewardReceived:
                    self.__updateLastShownTimestamp()
                return
            pendingReminderTimestamp = self.__seniorityAwardCtrl.pendingReminderTimestamp
            currentTimestamp = time_utils.getServerUTCTime()
            showByPending = bool(pendingReminderTimestamp and lastShownTime < pendingReminderTimestamp)
            showByInterval = bool(not pendingReminderTimestamp and currentTimestamp - lastShownTime >= time_utils.ONE_DAY * 30)
            if showByPending or showByInterval:
                priority = NotificationPriorityLevel.MEDIUM
            else:
                priority = NotificationPriorityLevel.LOW
            if self._notify(priority=priority):
                if priority != NotificationPriorityLevel.LOW:
                    WWISE.WW_eventGlobal(backport.sound(R.sounds.wdr_hangar_notification()))
                self.__updateLastShownTimestamp()
            return

    @staticmethod
    def __updateLastShownTimestamp():
        currentTimestamp = time_utils.getServerUTCTime()
        AccountSettings.setNotifications(SENIORITY_AWARDS_COINS_REMINDER_SHOWN_TIMESTAMP, currentTimestamp)


class SeniorityAwardsQuestListener(_NotificationListener):
    __TYPE = NOTIFICATION_TYPE.SENIORITY_AWARDS_QUEST
    __TEMPLATE = 'seniorityAwardsQuest22'
    __ENTITY_ID = 0
    __seniorityAwardCtrl = dependency.descriptor(ISeniorityAwardsController)

    def start(self, model):
        result = super(SeniorityAwardsQuestListener, self).start(model)
        self.__seniorityAwardCtrl.onUpdated += self.__tryNotify
        self.__tryNotify()
        return result

    def stop(self):
        super(SeniorityAwardsQuestListener, self).stop()
        self.__seniorityAwardCtrl.onUpdated -= self.__tryNotify

    def __tryNotify(self):
        model = self._model()
        if not model:
            return
        else:
            if self.__seniorityAwardCtrl.isNeedToShowRewardNotification:
                if not model.hasNotification(self.__TYPE, self.__ENTITY_ID):
                    model.addNotification(SeniorityAwardsDecorator(self.__ENTITY_ID, self.__TYPE, None, model, self.__TEMPLATE, NotificationPriorityLevel.MEDIUM, useCounterOnce=False))
                    WWISE.WW_eventGlobal(backport.sound(R.sounds.wdr_hangar_notification()))
            else:
                model.removeNotification(self.__TYPE, self.__ENTITY_ID)
            return


class ResourceWellListener(_NotificationListener):
    __RESOURCE_WELL_MESSAGES = R.strings.messenger.serviceChannelMessages.resourceWell
    __START_ENTITY_ID = 0
    __resourceWell = dependency.descriptor(IResourceWellController)
    __luiController = dependency.descriptor(ILimitedUIController)

    def __init__(self):
        super(ResourceWellListener, self).__init__()
        self.__isActive = False
        self.__isPaused = False
        self.__isFinished = False

    def start(self, model):
        result = super(ResourceWellListener, self).start(model)
        if result:
            self.__resourceWell.onEventUpdated += self.__onEventUpdated
            self.__tryNotify()
        return result

    def stop(self):
        self.__resourceWell.onEventUpdated -= self.__onEventUpdated
        super(ResourceWellListener, self).stop()

    def __onEventUpdated(self):
        self.__tryNotify()

    def __tryNotify(self):
        isActive = self.__resourceWell.isActive()
        isPaused = self.__resourceWell.isPaused()
        isFinished = self.__resourceWell.isFinished()
        isRuleCompleted = self.__luiController.isRuleCompleted(LuiRules.RESOURCE_WELL)
        season = self.__resourceWell.getSeason()
        settings = AccountSettings.getNotifications(RESOURCE_WELL_NOTIFICATIONS)
        settings.setdefault(RESOURCE_WELL_START_SHOWN, set())
        settings.setdefault(RESOURCE_WELL_END_SHOWN, set())
        if isRuleCompleted:
            if isActive and not self.__isActive and season not in settings[RESOURCE_WELL_START_SHOWN]:
                self.__pushStarted()
            elif isPaused and not self.__isPaused:
                self.__pushPaused()
            elif self.__isPaused and isActive:
                self.__pushEnabled()
            elif season in settings[RESOURCE_WELL_START_SHOWN] and isFinished and not self.__isFinished and season not in settings[RESOURCE_WELL_END_SHOWN]:
                self.__pushFinished()
        self.__isActive = isActive
        self.__isPaused = isPaused
        self.__isFinished = isFinished

    def __pushStarted(self):
        model = self._model()
        if model is not None:
            vehicle = text_styles.crystal(getVehicleByIntCD(self.__resourceWell.getRewardVehicle()).shortUserName)
            text = backport.text(self.__RESOURCE_WELL_MESSAGES.start.text(), vehicle=text_styles.crystal(vehicle))
            title = backport.text(self.__RESOURCE_WELL_MESSAGES.start.title())
            messageData = {'title': title,
             'text': text}
            model.addNotification(ResourceWellStartDecorator(message=messageData, entityID=self.__START_ENTITY_ID, model=model))
            self.__setNotificationShown(RESOURCE_WELL_START_SHOWN)
        return

    def __pushFinished(self):
        text = backport.text(self.__RESOURCE_WELL_MESSAGES.end.text())
        title = backport.text(self.__RESOURCE_WELL_MESSAGES.end.title())
        SystemMessages.pushMessage(text=text, type=SM_TYPE.ResourceWellEnd, messageData={'title': title})
        self.__setNotificationShown(RESOURCE_WELL_END_SHOWN)

    def __pushPaused(self):
        text = backport.text(self.__RESOURCE_WELL_MESSAGES.pause.text())
        SystemMessages.pushMessage(text=text, type=SM_TYPE.ErrorSimple, priority=NotificationPriorityLevel.HIGH)

    def __pushEnabled(self):
        text = backport.text(self.__RESOURCE_WELL_MESSAGES.enabled.text())
        SystemMessages.pushMessage(text=text, type=SM_TYPE.Warning, priority=NotificationPriorityLevel.HIGH)

    def __setNotificationShown(self, settingKey):
        settings = AccountSettings.getNotifications(RESOURCE_WELL_NOTIFICATIONS)
        settings.setdefault(RESOURCE_WELL_START_SHOWN, set())
        settings.setdefault(RESOURCE_WELL_END_SHOWN, set())
        settings[settingKey].add(self.__resourceWell.getSeason())
        AccountSettings.setNotifications(RESOURCE_WELL_NOTIFICATIONS, settings)


class IntegratedAuctionListener(_NotificationListener):
    __slots__ = ('__startNotifiers', '__finishNotifiers')
    __eventNotifications = dependency.descriptor(IEventsNotificationsController)
    __EVENT_TYPE_TO_SETTING = {AUCTION_START_EVENT_TYPE: AUCTION_STAGE_START_SEEN,
     AUCTION_FINISH_EVENT_TYPE: AUCTION_FINISH_STAGE_SEEN}
    __EVENT_TYPE_TO_DECORATOR = {AUCTION_START_EVENT_TYPE: IntegratedAuctionStageStartDecorator,
     AUCTION_FINISH_EVENT_TYPE: IntegratedAuctionStageFinishDecorator}
    __TIME_TO_SHOW_SOON = 2

    def __init__(self):
        self.__startNotifiers = {}
        self.__finishNotifiers = {}
        super(IntegratedAuctionListener, self).__init__()

    def start(self, model):
        result = super(IntegratedAuctionListener, self).start(model)
        if result:
            self.__eventNotifications.onEventNotificationsChanged += self.__onEventNotification
            self.__tryNotify(self.__eventNotifications.getEventsNotifications())
        return True

    def stop(self):
        self.__clearNotifiers()
        self.__eventNotifications.onEventNotificationsChanged -= self.__onEventNotification
        super(IntegratedAuctionListener, self).stop()

    def __clearNotifiers(self):
        for notifier in self.__startNotifiers.itervalues():
            notifier.stopNotification()
            notifier.clear()

        self.__startNotifiers.clear()
        for notifier in self.__finishNotifiers.itervalues():
            notifier.stopNotification()
            notifier.clear()

        self.__finishNotifiers.clear()

    def __onEventNotification(self, added, _):
        self.__tryNotify(added)

    def __tryNotify(self, notifications):
        for notification in notifications:
            if notification.eventType in (AUCTION_START_EVENT_TYPE, AUCTION_FINISH_EVENT_TYPE):
                notificationData = json.loads(notification.data)
                self.__addNotification(notificationData, notification.eventType)

    def __addNotification(self, data, eventType):
        model = self._model()
        if model is None:
            return
        else:
            settings = AccountSettings.getNotifications(INTEGRATED_AUCTION_NOTIFICATIONS)
            settingName = self.__EVENT_TYPE_TO_SETTING[eventType]
            notificationID = str(data['id'])
            if notificationID not in settings[settingName]:
                startDate = getTimestampByStrDate(str(data['startDate']))
                endDate = getTimestampByStrDate(str(data['endDate']))
                if startDate <= time_utils.getServerUTCTime() < endDate and self.__isNotificationNeeded(eventType):
                    decorator = self.__EVENT_TYPE_TO_DECORATOR.get(eventType)
                    if callable(decorator):
                        model.addNotification(decorator(entityID=int(notificationID)))
                        self.__setNotificationShown(settings, settingName, notificationID)
                        self.__removeNotifier(notificationID, eventType)
                elif startDate > time_utils.getServerUTCTime():
                    self.__addNotifier(notificationID, eventType, startDate)
            return

    def __addNotifier(self, notificationID, eventType, startDate):
        notifiers = self.__startNotifiers if eventType == AUCTION_START_EVENT_TYPE else self.__finishNotifiers
        if notificationID not in notifiers:
            notifiers[notificationID] = SimpleNotifier(partial(self.__getTimeToStart, startDate), self.__onNotifierUpdate)
            notifiers[notificationID].startNotification()

    def __removeNotifier(self, notificationID, eventType):
        notifiers = self.__startNotifiers if eventType == AUCTION_START_EVENT_TYPE else self.__finishNotifiers
        if notificationID in notifiers:
            notifiers[notificationID].stopNotification()
            notifiers[notificationID].clear()
            notifiers.pop(notificationID)

    def __onNotifierUpdate(self):
        self.__tryNotify(self.__eventNotifications.getEventsNotifications())

    def __getTimeToStart(self, startDate):
        return startDate - time_utils.getServerUTCTime()

    def __setNotificationShown(self, settings, settingName, notificationID):
        settings[settingName].add(notificationID)
        AccountSettings.setNotifications(INTEGRATED_AUCTION_NOTIFICATIONS, settings)

    def __isFinishNotificationActive(self):
        for notification in self.__eventNotifications.getEventsNotifications():
            if notification.eventType == AUCTION_FINISH_EVENT_TYPE:
                data = json.loads(notification.data)
                if self.__getTimeToStart(getTimestampByStrDate(str(data['startDate']))) <= self.__TIME_TO_SHOW_SOON:
                    return True

        return False

    def __isNotificationNeeded(self, eventType):
        return eventType == AUCTION_START_EVENT_TYPE and not self.__isFinishNotificationActive() or eventType == AUCTION_FINISH_EVENT_TYPE


class TradingCaravanListener(_NotificationListener):
    __slots__ = ('__startNotifiers',)
    __eventNotifications = dependency.descriptor(IEventsNotificationsController)
    __EVENT_TYPE_TO_SETTING = {TRADING_CARAVAN_REFILL_EVENT_TYPE: TRADING_CARAVAN_REFILL_SEEN}
    __EVENT_TYPE_TO_DECORATOR = {TRADING_CARAVAN_REFILL_EVENT_TYPE: TradingCaravanRefillDecorator}
    __luiController = dependency.descriptor(ILimitedUIController)

    def __init__(self):
        self.__startNotifiers = {}
        super(TradingCaravanListener, self).__init__()

    def start(self, model):
        result = super(TradingCaravanListener, self).start(model)
        if result:
            self.__eventNotifications.onEventNotificationsChanged += self.__onEventNotification
            self.__tryNotify(self.__eventNotifications.getEventsNotifications())
        return True

    def stop(self):
        self.__clearNotifiers()
        self.__eventNotifications.onEventNotificationsChanged -= self.__onEventNotification
        super(TradingCaravanListener, self).stop()

    def __clearNotifiers(self):
        for notifier in self.__startNotifiers.itervalues():
            notifier.stopNotification()
            notifier.clear()

        self.__startNotifiers.clear()

    def __onEventNotification(self, added, _):
        self.__tryNotify(added)

    def __tryNotify(self, notifications):
        for notification in notifications:
            if notification.eventType == TRADING_CARAVAN_REFILL_EVENT_TYPE and self.__luiController.isRuleCompleted(LuiRules.SHOP_SALES_ENTRY_POINT):
                notificationData = json.loads(notification.data)
                self.__addNotification(notificationData, notification.eventType)

    def __addNotification(self, data, eventType):
        model = self._model()
        if model is None:
            return
        else:
            settings = AccountSettings.getNotifications(TRADING_CARAVAN_NOTIFICATIONS)
            settingName = self.__EVENT_TYPE_TO_SETTING[eventType]
            notificationID = str(data['id'])
            if notificationID not in settings[settingName]:
                startDate = getTimestampByStrDate(str(data['startDate']))
                endDate = getTimestampByStrDate(str(data['endDate']))
                if startDate <= time_utils.getServerUTCTime() < endDate:
                    decorator = self.__EVENT_TYPE_TO_DECORATOR.get(eventType)
                    if callable(decorator):
                        text = backport.text(R.strings.messenger.serviceChannelMessages.tradingCaravan.refill.text())
                        model.addNotification(decorator(entityID=int(notificationID), message={'text': text}))
                        self.__setNotificationShown(settings, settingName, notificationID)
                        self.__removeNotifier(notificationID, eventType)
                elif startDate > time_utils.getServerUTCTime():
                    self.__addNotifier(notificationID, eventType, startDate)
            return

    def __addNotifier(self, notificationID, eventType, startDate):
        notifiers = self.__startNotifiers
        if notificationID not in notifiers:
            notifiers[notificationID] = SimpleNotifier(partial(self.__getTimeToStart, startDate), self.__onNotifierUpdate)
            notifiers[notificationID].startNotification()

    def __removeNotifier(self, notificationID, eventType):
        notifiers = self.__startNotifiers
        if notificationID in notifiers:
            notifiers[notificationID].stopNotification()
            notifiers[notificationID].clear()
            notifiers.pop(notificationID)

    def __onNotifierUpdate(self):
        self.__tryNotify(self.__eventNotifications.getEventsNotifications())

    def __getTimeToStart(self, startDate):
        return startDate - time_utils.getServerUTCTime()

    def __setNotificationShown(self, settings, settingName, notificationID):
        settings[settingName].add(notificationID)
        AccountSettings.setNotifications(TRADING_CARAVAN_NOTIFICATIONS, settings)


class CollectionsListener(_NotificationListener, EventsHandler):
    __collections = dependency.descriptor(ICollectionsSystemController)
    __eventNotifications = dependency.descriptor(IEventsNotificationsController)
    __limitedUIController = dependency.descriptor(ILimitedUIController)
    __NOTIFICATIONS = R.strings.collections.notifications
    __FEATURE_NAME_TO_LUI_ID = {'battle_pass_': LuiRules.SYS_MSG_COLLECTION_START_BP}

    def __init__(self):
        super(CollectionsListener, self).__init__()
        self.__postponedNotifications = None
        return

    def start(self, model):
        self.__postponedNotifications = []
        result = super(CollectionsListener, self).start(model)
        if result:
            self._subscribe()
            self.__tryNotify(self.__eventNotifications.getEventsNotifications())
        return True

    def stop(self):
        self._unsubscribe()
        self.__postponedNotifications = None
        super(CollectionsListener, self).stop()
        return

    def _subscribe(self):
        super(CollectionsListener, self)._subscribe()
        self.__limitedUIController.startObserve(LuiRules.SYS_MSG_COLLECTION_START_BP, self.__onLuiRuleCompleted)

    def _unsubscribe(self):
        self.__limitedUIController.stopObserve(LuiRules.SYS_MSG_COLLECTION_START_BP, self.__onLuiRuleCompleted)
        super(CollectionsListener, self)._unsubscribe()

    def _getEvents(self):
        return ((self.__eventNotifications.onEventNotificationsChanged, self.__onEventNotification), (self.__collections.onAvailabilityChanged, self.__onAvailabilityChanged), (self.__limitedUIController.onConfigChanged, self.__onLuiConfigChanged))

    def __onLuiConfigChanged(self):
        self.__tryNotifyPostponed()

    def __onLuiRuleCompleted(self, ruleID, *_):
        if ruleID in self.__FEATURE_NAME_TO_LUI_ID.values():
            self.__tryNotifyPostponed()

    def __onEventNotification(self, added, _):
        self.__tryNotify(added)

    def __onAvailabilityChanged(self, enabled):
        (self.__pushEnabled if enabled else self.__pushDisabled)()

    def __tryNotifyPostponed(self):
        if self.__postponedNotifications:
            notifications = self.__postponedNotifications[:]
            self.__postponedNotifications = []
            self.__tryNotify(notifications)

    def __tryNotify(self, notifications):
        for notification in notifications:
            self.__onCollectionsEvent(notification)

    def __onCollectionsEvent(self, notification):
        if notification.eventType == COLLECTION_START_EVENT_TYPE:
            self.__onCollectionStartEvent(notification)
        elif notification.eventType == COLLECTIONS_UPDATED_ENTRY_EVENT_TYPE:
            self.__onCollectionsUpdatedEntryEvent(notification)
        elif notification.eventType == COLLECTIONS_RENEW_EVENT_TYPE:
            self.__onCollectionsRenewEvent(notification)

    def __onCollectionStartEvent(self, notification):
        notificationData = json.loads(notification.data)
        collectionID = int(notificationData['collectionId'])
        collection = self.__collections.getCollection(collectionID)
        luiRuleID = self.__getLuiRuleIDByCollectionID(collection.name)
        if not self.__isLuiApplicable(luiRuleID):
            self.__postponeNotification(notification)
            return
        if not isCollectionStartedSeen(collectionID):
            self.__pushStarted(collection)
            setCollectionStartedSeen(collectionID)

    def __onCollectionsUpdatedEntryEvent(self, notification):
        luiRuleID = LuiRules.SYS_MSG_COLLECTIONS_UPDATED_ENTRY
        if not self.__isLuiApplicable(luiRuleID):
            self.__postponeNotification(notification)
            return
        if not isCollectionsUpdatedEntrySeen():
            self.__pushCollectionsCustomMessage(backport.text(self.__NOTIFICATIONS.updatedEntry.title()), backport.text(self.__NOTIFICATIONS.updatedEntry.text()), SM_TYPE.CollectionsEntry)

    def __onCollectionsRenewEvent(self, notification):
        notificationData = json.loads(notification.data)
        collections = (c for c in (self.__collections.getCollection(collectionID) for collectionID in notificationData['collectionsIds']) if c is not None)
        for collection in collections:
            if not isCollectionRenewSeen(collection.collectionId):
                self.__pushCollectionsCustomMessage(backport.text(self.__NOTIFICATIONS.renew.title(), feature=backport.text(self.__NOTIFICATIONS.feature.dyn(collection.name)()), season=backport.text(self.__NOTIFICATIONS.season.dyn(collection.name)())), backport.text(self.__NOTIFICATIONS.renew.text()), SM_TYPE.CollectionRenew, savedData={'collectionId': collection.collectionId})

    def __getLuiRuleIDByCollectionID(self, collectionID):
        for key in self.__FEATURE_NAME_TO_LUI_ID:
            if key in collectionID:
                return self.__FEATURE_NAME_TO_LUI_ID[key]

        return None

    def __isLuiApplicable(self, luiRuleID):
        return self.__limitedUIController.isInited and not (luiRuleID and luiRuleID in LuiRules and not self.__limitedUIController.isRuleCompleted(luiRuleID))

    def __postponeNotification(self, notification):
        if notification not in self.__postponedNotifications:
            self.__postponedNotifications.append(notification)

    @staticmethod
    def __pushCollectionsCustomMessage(title, text, messageType, savedData=None):
        SystemMessages.pushMessage(text=text, type=messageType, messageData={'title': title}, savedData=savedData)

    def __pushStarted(self, collection):
        feature = backport.text(self.__NOTIFICATIONS.feature.dyn(collection.name)())
        fullFeature = getCollectionFullFeatureName(collection)
        title = backport.text(self.__NOTIFICATIONS.eventStart.title(), feature=feature)
        text = backport.text(self.__NOTIFICATIONS.eventStart.text(), feature=fullFeature)
        SystemMessages.pushMessage(text=text, priority=NotificationPriorityLevel.HIGH, type=SystemMessages.SM_TYPE.CollectionStart, messageData={'title': title}, savedData={'collectionId': collection.collectionId})

    def __pushDisabled(self):
        SystemMessages.pushMessage(text=backport.text(self.__NOTIFICATIONS.eventDisabled.text()), priority=NotificationPriorityLevel.HIGH, type=SystemMessages.SM_TYPE.CollectionsDisabled)

    def __pushEnabled(self):
        SystemMessages.pushMessage(text=backport.text(self.__NOTIFICATIONS.eventEnabled.text()), priority=NotificationPriorityLevel.HIGH, type=SystemMessages.SM_TYPE.CollectionsEnabled)


class WinbackSelectableRewardReminder(BaseReminderListener):
    __winbackController = dependency.descriptor(IWinbackController)
    __itemsCache = dependency.descriptor(IItemsCache)
    __ENTITY_ID = 0

    def __init__(self):
        super(WinbackSelectableRewardReminder, self).__init__(NOTIFICATION_TYPE.WINBACK_SELECTABLE_REWARD_AVAILABLE, self.__ENTITY_ID)

    def start(self, model):
        result = super(WinbackSelectableRewardReminder, self).start(model)
        if result:
            self.__addListeners()
            self.__tryNotify()
        return result

    def stop(self):
        self.__removeListeners()
        super(WinbackSelectableRewardReminder, self).stop()

    def _createDecorator(self, _):
        return WinbackSelectableRewardReminderDecorator(self._getNotificationId())

    def __addListeners(self):
        self.__itemsCache.onSyncCompleted += self.__tryNotify
        self.__winbackController.onStateUpdated += self.__tryNotify

    def __removeListeners(self):
        self.__itemsCache.onSyncCompleted -= self.__tryNotify
        self.__winbackController.onStateUpdated -= self.__tryNotify

    def __tryNotify(self, *_):
        isAdding = self.__winbackController.hasWinbackOfferToken() and self.__winbackController.isFinished()
        self._notifyOrRemove(isAdding)


class ArmoryYardListener(_NotificationListener):
    __armoryYardCtrl = dependency.descriptor(IArmoryYardController)
    __limitedUIController = dependency.descriptor(ILimitedUIController)
    __armoryYardText = R.strings.armory_yard.notifications
    __systemMessages = dependency.descriptor(ISystemMessages)
    __lastTimeErrorShown = 0
    __timeDelay = 2
    ARMORY_YARD_TEXT = R.strings.armory_yard.notifications

    def start(self, model):
        super(ArmoryYardListener, self).start(model)
        if not self.__limitedUIController.isRuleCompleted(LuiRules.ARMORY_YARD_ENTRY_POINT):
            self.__limitedUIController.startObserve(LuiRules.ARMORY_YARD_ENTRY_POINT, self.__onLuiRuleCompleted)
        else:
            self.__subscribe()
        return True

    def stop(self):
        if not self.__limitedUIController.isRuleCompleted(LuiRules.ARMORY_YARD_ENTRY_POINT):
            self.__limitedUIController.stopObserve(LuiRules.ARMORY_YARD_ENTRY_POINT, self.__onLuiRuleCompleted)
        else:
            self.__unsubscribe()
        super(ArmoryYardListener, self).stop()

    def __onLuiRuleCompleted(self, *_):
        self.__limitedUIController.stopObserve(LuiRules.ARMORY_YARD_ENTRY_POINT, self.__onLuiRuleCompleted)
        self.__subscribe()

    def __subscribe(self):
        self.__armoryYardCtrl.onCheckNotify += self.__onCheckNotify
        self.__armoryYardCtrl.onAnnouncement += self.__announcement
        self.__armoryYardCtrl.onPayed += self.__payed
        self.__armoryYardCtrl.onServerSwitchChange += self.__switchChange
        self.__armoryYardCtrl.onStyleQuestEnds += self.__onStyleQuestEnds
        self.__armoryYardCtrl.onProgressUpdated += self.__checkChapter
        self.__armoryYardCtrl.onQuestsUpdated += self.__checkChapter
        self.__armoryYardCtrl.onCollectReward += self.__collectReward
        self.__armoryYardCtrl.onPayedError += self.__payedError
        self.__armoryYardCtrl.onBundleOutTime += self.__bundleOutTime
        self.__lastTimeErrorShown = 0
        self.__onCheckNotify()

    def __unsubscribe(self):
        self.__armoryYardCtrl.onCheckNotify -= self.__onCheckNotify
        self.__armoryYardCtrl.onAnnouncement -= self.__announcement
        self.__armoryYardCtrl.onPayed -= self.__payed
        self.__armoryYardCtrl.onServerSwitchChange -= self.__switchChange
        self.__armoryYardCtrl.onStyleQuestEnds -= self.__onStyleQuestEnds
        self.__armoryYardCtrl.onProgressUpdated -= self.__checkChapter
        self.__armoryYardCtrl.onQuestsUpdated -= self.__checkChapter
        self.__armoryYardCtrl.onCollectReward -= self.__collectReward
        self.__armoryYardCtrl.onPayedError -= self.__payedError
        self.__armoryYardCtrl.onBundleOutTime -= self.__bundleOutTime
        self.__lastTimeErrorShown = 0

    def __getHeader(self):
        return backport.text(self.ARMORY_YARD_TEXT.title())

    def __collectReward(self):
        SystemMessages.pushMessage(text=backport.text(self.ARMORY_YARD_TEXT.collectRewards()), type=SystemMessages.SM_TYPE.InformationHeader, priority=NotificationPriorityLevel.MEDIUM, messageData={'header': backport.text(self.ARMORY_YARD_TEXT.rewards.title())})

    def __switchChange(self):
        if self.__armoryYardCtrl.getState() != State.DISABLED:
            _, endDate = self.__armoryYardCtrl.getSeasonInterval()
            SystemMessages.pushMessage(text=backport.text(self.ARMORY_YARD_TEXT.switcher.enabled(), endDate=backport.getDateTimeFormat(endDate)), type=SystemMessages.SM_TYPE.InformationHeader, priority=NotificationPriorityLevel.MEDIUM, messageData={'header': self.__getHeader()})
        else:
            SystemMessages.pushMessage(text=backport.text(self.ARMORY_YARD_TEXT.switcher.disabled()), type=SystemMessages.SM_TYPE.ErrorHeader, priority=NotificationPriorityLevel.HIGH, messageData={'header': self.__getHeader()})

    def __announcement(self, startDate, chapterInfo=None):
        if chapterInfo is None:
            if not AccountSettings.getArmoryYard(ArmoryYard.EVENT_ANNOUNCEMENT):
                AccountSettings.setArmoryYard(ArmoryYard.EVENT_ANNOUNCEMENT, True)
                SystemMessages.pushMessage(text=backport.text(self.ARMORY_YARD_TEXT.announcement.event(), startDate=backport.getDateTimeFormat(startDate)), type=SystemMessages.SM_TYPE.InformationHeader, priority=NotificationPriorityLevel.MEDIUM, messageData={'header': self.__getHeader()})
        else:
            key = '%s_%s' % (ArmoryYard.ANNOUNCEMENT_CHAPTER_PREFIX, chapterInfo.ID)
            if not AccountSettings.getArmoryYard(key):
                AccountSettings.setArmoryYard(key, True)
                SystemMessages.pushMessage(text=backport.text(self.ARMORY_YARD_TEXT.announcement.chapter(), count=chapterInfo.ordinalNumber, chapter_name=backport.text(R.strings.armory_yard.mainView.chapter.index.dyn('c_%d' % chapterInfo.ordinalNumber)()), startDate=backport.getDateTimeFormat(startDate)), type=SystemMessages.SM_TYPE.InformationHeader, priority=NotificationPriorityLevel.MEDIUM, messageData={'header': self.__getHeader()})
        return

    def __payed(self, count, price=None):
        messageResID = self.ARMORY_YARD_TEXT.payed.single() if count == 1 else self.ARMORY_YARD_TEXT.payed.multiple()
        SystemMessages.pushMessage(text=backport.text(messageResID, count=count), type=SystemMessages.SM_TYPE.InformationHeader, priority=NotificationPriorityLevel.MEDIUM, messageData={'header': self.__getHeader()})
        if price is None:
            return
        else:
            messagePriceGoldResID = self.ARMORY_YARD_TEXT.payed.priceGold()
            SystemMessages.pushMessage(text=backport.text(messagePriceGoldResID, price=backport.getGoldFormat(price.getSignValue(Currency.GOLD))), type=SystemMessages.SM_TYPE.FinancialTransactionWithGold, priority=NotificationPriorityLevel.MEDIUM)
            return

    def __payedError(self):
        currentTime = time_utils.getServerUTCTime()
        if currentTime - self.__lastTimeErrorShown < self.__timeDelay:
            return
        self.__lastTimeErrorShown = currentTime
        SystemMessages.pushMessage(text=backport.text(self.ARMORY_YARD_TEXT.payed.error()), type=SystemMessages.SM_TYPE.ErrorHeader, priority=NotificationPriorityLevel.HIGH, messageData={'header': self.__getHeader()})

    def __bundleOutTime(self):
        SystemMessages.pushMessage(text=backport.text(self.ARMORY_YARD_TEXT.bundleOutTime()), type=SystemMessages.SM_TYPE.ErrorHeader, priority=NotificationPriorityLevel.HIGH, messageData={'header': self.__getHeader()})

    def __checkState(self):
        state = self.__armoryYardCtrl.getState()
        armoryIsActiveMessageWasShown = AccountSettings.getArmoryYard(State.ACTIVE.value)
        currentStateMessageWasShown = AccountSettings.getArmoryYard(state.value)
        if not self.__armoryYardCtrl.isActive() or currentStateMessageWasShown and armoryIsActiveMessageWasShown:
            return
        AccountSettings.setArmoryYard(state.value, True)
        if not armoryIsActiveMessageWasShown:
            SystemMessages.pushMessage(text=backport.text(self.ARMORY_YARD_TEXT.active()), type=SystemMessages.SM_TYPE.ArmoryYardMain, priority=NotificationPriorityLevel.MEDIUM, messageData={'header': self.__getHeader()})
            AccountSettings.setArmoryYard(State.ACTIVE.value, True)
        if state == State.POSTPROGRESSION and not currentStateMessageWasShown and not self.__armoryYardCtrl.isCompleted():
            SystemMessages.pushMessage(text=backport.text(self.ARMORY_YARD_TEXT.postProgression()), type=SystemMessages.SM_TYPE.ArmoryYardPostprogression, priority=NotificationPriorityLevel.MEDIUM, messageData={'header': self.__getHeader()})

    def __checkChapter(self):
        if self.__armoryYardCtrl.getState() != State.ACTIVE:
            return
        nowTime = time_utils.getServerUTCTime()
        for cycle in self.__armoryYardCtrl.serverSettings.getCurrentSeason().getAllCycles().values():
            key = '%s_%s' % (ArmoryYard.START_CHAPTER_PREFIX, cycle.ID)
            if cycle.startDate <= nowTime < cycle.endDate and not AccountSettings.getArmoryYard(key):
                AccountSettings.setArmoryYard(key, True)
                SystemMessages.pushMessage(text=backport.text(self.ARMORY_YARD_TEXT.started.chapter.untitled()), type=SystemMessages.SM_TYPE.ArmoryYardOpenChapter, priority=NotificationPriorityLevel.MEDIUM, messageData={'header': self.__getHeader()})

    def __onCheckNotify(self):
        if not self.__armoryYardCtrl.isEnabled():
            return
        self.__armoryYardCtrl.checkAnnouncement()
        self.__checkState()
        self.__checkChapter()

    def __onStyleQuestEnds(self, endDate):
        if not AccountSettings.getArmoryYard(ArmoryYard.STYLE_QUEST_ENDS):
            AccountSettings.setArmoryYard(ArmoryYard.STYLE_QUEST_ENDS, True)
            SystemMessages.pushMessage(text=backport.text(self.ARMORY_YARD_TEXT.styleQuest(), endDate=backport.getDateTimeFormat(endDate)), type=SystemMessages.SM_TYPE.InformationHeader, priority=NotificationPriorityLevel.MEDIUM, messageData={'header': self.__getHeader()})


class ReferralProgramListener(_NotificationListener):
    __referralProgramController = dependency.descriptor(IReferralProgramController)

    def start(self, model):
        result = super(ReferralProgramListener, self).start(model)
        if result:
            self.__addListeners()
            self.__tryNotify()
        return result

    def stop(self):
        self.__removeListeners()
        super(ReferralProgramListener, self).stop()

    def __addListeners(self):
        self.__referralProgramController.onReferralProgramEnabled += self.__tryNotify
        self.__referralProgramController.onPointsChanged += self.__tryNotify

    def __removeListeners(self):
        self.__referralProgramController.onReferralProgramEnabled -= self.__tryNotify
        self.__referralProgramController.onPointsChanged -= self.__tryNotify

    def __tryNotify(self):
        if not isReferralProgramEnabled():
            return
        scoresLimitReached = self.__referralProgramController.isScoresLimitReached()
        prevPgbFullValue = AccountSettings.getNotifications(REFERRAL_PROGRAM_PGB_FULL)
        if scoresLimitReached and not prevPgbFullValue:
            self.__pushReferralProgramPGBFull()
        AccountSettings.setNotifications(REFERRAL_PROGRAM_PGB_FULL, scoresLimitReached)

    @staticmethod
    def __pushReferralProgramPGBFull():
        text = backport.text(R.strings.messenger.serviceChannelMessages.referralProgramPGBFull.text())
        SystemMessages.pushMessage(text=text, type=SM_TYPE.ReferralProgramPGBFull, priority=NotificationPriorityLevel.MEDIUM)


class WotPlusIntroViewListener(_NotificationListener):
    __wotPlusCtrl = dependency.descriptor(IWotPlusController)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    ATTENDANCE_NOTIFICATION_LIMIT = 11

    def start(self, model):
        result = super(WotPlusIntroViewListener, self).start(model)
        self.__addListeners()
        self._updateNotification()
        return result

    def stop(self):
        self.__delListeners()
        super(WotPlusIntroViewListener, self).stop()

    def _updateNotification(self, *_, **__):
        model = self._model()
        if self._shouldNotify() and not self._alreadyNotified():
            model.addNotification(WotPlusIntroViewMessageDecorator())
        elif not self._shouldNotify() and self._alreadyNotified():
            model.removeNotification(NOTIFICATION_TYPE.WOT_PLUS_INTRO, WotPlusIntroViewMessageDecorator.ENTITY_ID)

    @staticmethod
    def _limitReached():
        with settings_records.wotPlusSettings() as dt:
            return dt.amountOfDailyAttendance >= WotPlusIntroViewListener.ATTENDANCE_NOTIFICATION_LIMIT

    def _shouldNotify(self):
        serverSettings = self.__lobbyContext.getServerSettings()
        return self.__wotPlusCtrl.isWotPlusEnabled() and self.__wotPlusCtrl.isEnabled() and serverSettings.isDailyAttendancesEnabled() and not self._limitReached()

    def _alreadyNotified(self):
        return self._model().hasNotification(NOTIFICATION_TYPE.WOT_PLUS_INTRO, WotPlusIntroViewMessageDecorator.ENTITY_ID)

    def __addListeners(self):
        self.__wotPlusCtrl.onDataChanged += self._updateNotification
        self.__wotPlusCtrl.onAttendanceUpdated += self._updateNotification
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self._updateNotification

    def __delListeners(self):
        self.__wotPlusCtrl.onDataChanged -= self._updateNotification
        self.__wotPlusCtrl.onAttendanceUpdated -= self._updateNotification
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self._updateNotification


class BattleMattersTaskReminderListener(BaseReminderListener, EventsHandler):
    __bootCampController = dependency.descriptor(IBootcampController)
    __bmCtrl = dependency.descriptor(IBattleMattersController)
    __gameSession = dependency.descriptor(IGameSessionController)
    __TYPE = NOTIFICATION_TYPE.BATTLE_MATTERS_TASK_REMINDER
    __ENTITY_ID = 0
    __TEMPLATE = 'BattleMattersTaskReminder'
    __MAX_BATTLES_WITHOUT_PROGRESS = 15

    def __init__(self):
        super(BattleMattersTaskReminderListener, self).__init__(self.__TYPE, self.__ENTITY_ID)

    def start(self, model):
        result = super(BattleMattersTaskReminderListener, self).start(model)
        if result:
            self._subscribe()
            self.__tryNotify()
        return result

    def stop(self):
        self._unsubscribe()
        super(BattleMattersTaskReminderListener, self).stop()

    def _getEvents(self):
        return ((self.__bmCtrl.progressWatcher.onStateChanged, self.__onStateChanged), (self.__bmCtrl.progressWatcher.onProgressReset, self.__onProgressReset), (self.__bmCtrl.progressWatcher.onBackFromBattle, self.__onBackFromBattle))

    def _createNotificationData(self, priority, **ctx):
        currentQuest = self.__bmCtrl.getCurrentQuest()
        data = {'questIndex': currentQuest.getOrder()}
        return NotificationData(self._getNotificationId(), data, priority, None)

    def _createDecorator(self, data):
        return BattleMattersReminderDecorator(data.entityID, self._getNotificationType(), data.savedData, self._model(), self.__TEMPLATE, data.priorityLevel)

    def __onStateChanged(self):
        self.__tryNotify()

    def __onProgressReset(self):
        self.__tryNotify()

    def __onBackFromBattle(self):
        self.__tryNotify()

    def __tryNotify(self):
        if self.__bootCampController.isInBootcamp():
            return
        else:
            isAdding = self.__bmCtrl.progressWatcher.isJustBackFromBattle(reset=True) and self.__bmCtrl.isActive() and self.__bmCtrl.getCurrentQuest() is not None and self.__isLongTimeWithoutProgress() and not self.__isShowedToday()
            priority = NotificationPriorityLevel.LOW
            if isAdding:
                if self.__bmCtrl.progressWatcher.isFirstBattleWithoutProgressInSession(reset=True):
                    priority = NotificationPriorityLevel.MEDIUM
                AccountSettings.setBattleMattersSetting(BattleMatters.REMINDER_LAST_DISPLAY_TIME, time_utils.getServerUTCTime())
            self._notifyOrRemove(isAdding, priority=priority)
            return

    def __isLongTimeWithoutProgress(self):
        battlesWithoutProgress = self.__bmCtrl.progressWatcher.getBattlesCountWithoutProgress()
        return battlesWithoutProgress >= self.__MAX_BATTLES_WITHOUT_PROGRESS

    def __isShowedToday(self):
        lastDisplayTime = AccountSettings.getBattleMattersSetting(BattleMatters.REMINDER_LAST_DISPLAY_TIME)
        return self.__isToday(lastDisplayTime) and (self.__gameSession.sessionStartedAt > lastDisplayTime or self.__bmCtrl.progressWatcher.isFirstBattleWithoutProgressInSession())

    @staticmethod
    def __isToday(timestamp):
        todayStart, todayEnd = time_utils.getDayTimeBoundsForLocal(time_utils.getServerUTCTime())
        return todayStart <= timestamp <= todayEnd


class Birthday2023Listener(_NotificationListener):
    __eventNotifications = dependency.descriptor(IEventsNotificationsController)

    def start(self, model):
        result = super(Birthday2023Listener, self).start(model)
        if result:
            self.__eventNotifications.onEventNotificationsChanged += self.__onEventNotification
            self.__tryNotify(self.__eventNotifications.getEventsNotifications())
        return True

    def stop(self):
        self.__eventNotifications.onEventNotificationsChanged -= self.__onEventNotification
        super(Birthday2023Listener, self).stop()

    def __onEventNotification(self, added, _):
        self.__tryNotify(added)

    def __tryNotify(self, notifications):
        for notification in notifications:
            if notification.eventType == 'birthday2023Start':
                introShown = AccountSettings.getSettings(BIRTHDAY_2023_INTRO_SHOWN)
                if introShown:
                    return
                from gui.shared.event_dispatcher import showBirthday2023Intro
                showBirthday2023Intro()


registerNotificationsListeners((ServiceChannelListener,
 MissingEventsListener,
 PrbInvitesListener,
 FriendshipRqsListener,
 _WGNCListenersContainer,
 ProgressiveRewardListener,
 SwitcherListener,
 TankPremiumListener,
 BattlePassListener,
 UpgradeTrophyDeviceListener,
 RecertificationFormStateListener,
 RecruitReminderListener,
 EmailConfirmationReminderListener,
 VehiclePostProgressionUnlockListener,
 BattlePassSwitchChapterReminder,
 ResourceWellListener,
 IntegratedAuctionListener,
 SeniorityAwardsQuestListener,
 SeniorityAwardsTokenListener,
 CollectionsListener,
 WinbackSelectableRewardReminder,
 ArmoryYardListener,
 ReferralProgramListener,
 WotPlusIntroViewListener,
 Birthday2023Listener,
 BattleMattersTaskReminderListener,
 TradingCaravanListener))

class NotificationsListeners(_NotificationListener):

    def __init__(self):
        super(NotificationsListeners, self).__init__()
        self.__listeners = collectAllNotificationsListeners()

    def start(self, model):
        for listener in self.__listeners:
            listener.start(model)

    def stop(self):
        for listener in self.__listeners:
            listener.stop()
