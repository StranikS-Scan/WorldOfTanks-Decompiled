# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/notification/listeners.py
import json
import logging
import time
import uuid
import weakref
from abc import ABCMeta
from collections import defaultdict
from functools import partial
import WWISE
from account_helpers.AccountSettings import BattleMatters, INTEGRATED_AUCTION_NOTIFICATIONS, IS_BATTLE_PASS_EXTRA_START_NOTIFICATION_SEEN, IS_BATTLE_PASS_START_NOTIFICATION_SEEN, LOOT_BOXES_WAS_FINISHED, LOOT_BOXES_WAS_STARTED, PROGRESSIVE_REWARD_VISITED, RECRUITS_NOTIFICATIONS, SENIORITY_AWARDS_COINS_REMINDER_SHOWN_TIMESTAMP, VEH_SKILL_TREE_POPUP_SHOWN, VEH_SKILL_TREE_RECORDED_NOFITICATION_NODE
from account_helpers.settings_core.settings_constants import SeniorityAwardsStorageKeys
from gui.Scaleform.locale.SYSTEM_MESSAGES import SYSTEM_MESSAGES
from gui.server_events.finders import PM_SWITCHER_CAMPAIGN, PM_CAMPAIGNS_IDS
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework.entities.View import ViewKey
from gui.impl.lobby.gf_notifications import GFNotificationTemplates
from gui.impl.lobby.gf_notifications.cache import getCache
from gui.impl.lobby.vehicle_hub.sub_presenters.veh_skill_tree.utils import getCheapestAvailablePerk
from helpers.events_handler import EventsHandler
from helpers.time_utils import getTimestampByStrDate
from typing import TYPE_CHECKING
from PlayerEvents import g_playerEvents
from account_helpers import AccountSettings
from adisp import adisp_process
from chat_shared import SYS_MESSAGE_TYPE
from collector_vehicle import CollectorVehicleConsts
from constants import ARENA_BONUS_TYPE, AUTO_MAINTENANCE_RESULT, DAILY_QUESTS_CONFIG, DOG_TAGS_CONFIG, MAPS_TRAINING_ENABLED_KEY, PLAYER_SUBSCRIPTIONS_CONFIG, Configs, PremiumConfigs, SwitchState
from debug_utils import LOG_DEBUG, LOG_ERROR
from exchange.personal_discounts_constants import EXCHANGE_RATE_FREE_XP_NAME, EXCHANGE_RATE_GOLD_NAME, ExchangeRateShowFormat
from gui import SystemMessages
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.genConsts.PERSONAL_EXCHANGE_RATES import PERSONAL_EXCHANGE_RATES
from gui.Scaleform.locale.CLANS import CLANS
from gui.SystemMessages import SM_TYPE
from gui.clans.clan_account_profile import SYNC_KEYS
from gui.clans.clan_helpers import ClanListener, isInClanEnterCooldown
from gui.clans.settings import CLAN_APPLICATION_STATES
from gui.collection.account_settings import isCollectionRenewSeen, isCollectionStartedSeen, isCollectionsUpdatedEntrySeen, setCollectionStartedSeen
from gui.collection.collections_constants import COLLECTIONS_RENEW_EVENT_TYPE, COLLECTIONS_UPDATED_ENTRY_EVENT_TYPE, COLLECTION_START_EVENT_TYPE
from gui.game_control.seniority_awards_controller import WDR_CURRENCY
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.lobby.premacc.premacc_helpers import PiggyBankConstants, getDeltaTimeHelper
from gui.impl.lobby.seniority_awards.seniority_awards_helper import isSeniorityAwardsSystemNotificationShowed, setSeniorityAwardEventStateSetting
from gui.integrated_auction.constants import AUCTION_FINISH_EVENT_TYPE, AUCTION_FINISH_STAGE_SEEN, AUCTION_STAGE_START_SEEN, AUCTION_START_EVENT_TYPE
from gui.limited_ui.lui_rules_storage import LUI_RULES
from gui.lootbox_system.base.common import NotificationPathPart, getTextResource
from gui.lootbox_system.base.utils import getIsStartFinishNotificationsVisible
from gui.lootbox_system.base.views_loaders import findActiveWindow
from gui.platform.base.statuses.constants import StatusTypes
from gui.prb_control import prbInvitesProperty
from gui.prb_control.entities.listener import IGlobalListener
from gui.prestige.prestige_helpers import MAX_GRADE_ID, isFirstEntryNotificationShown, mapGradeIDToUI, setFirstEntryNotificationShown
from gui.server_events.recruit_helper import getAllRecruitsInfo
from gui.shared import events, g_eventBus
from gui.shared.formatters import text_styles, time_formatters
from gui.shared.notifications import NotificationPriorityLevel
from gui.shared.system_factory import collectAllNotificationsListeners, registerNotificationsListeners
from gui.shared.utils import showInvitationInWindowsBar
from gui.shared.utils.scheduled_notifications import SimpleNotifier
from gui.shared.view_helpers.UsersInfoHelper import UsersInfoHelper
from gui.wgcg.clan.contexts import GetClanInfoCtx
from gui.wgnc import g_wgncEvents, g_wgncProvider, wgnc_settings
from gui.wgnc.settings import WGNC_DATA_PROXY_TYPE
from helpers import dependency, i18n, time_utils
from messenger import MessengerEntry
from messenger.formatters import TimeFormatter
from messenger.m_constants import PROTO_TYPE, SCH_CLIENT_MSG_TYPE, USER_ACTION_ID
from messenger.proto import proto_getter
from messenger.proto.events import g_messengerEvents
from messenger.proto.xmpp.xmpp_constants import XMPP_ITEM_TYPE
from notification.decorators import BattleMattersReminderDecorator, BattlePassLockButtonDecorator, BattlePassSwitchChapterReminderDecorator, C11nMessageDecorator, C11nProgressiveItemDecorator, C2DProgressionStyleDecorator, ClanAppActionDecorator, ClanAppsDecorator, ClanInvitesActionDecorator, ClanInvitesDecorator, ClanSingleAppDecorator, ClanSingleInviteDecorator, CollectionCustomMessageDecorator, CollectionsLockButtonDecorator, EmailConfirmationReminderMessageDecorator, ExchangeRateDiscountDecorator, FriendshipRequestDecorator, IntegratedAuctionStageFinishDecorator, IntegratedAuctionStageStartDecorator, LockButtonMessageDecorator, LootBoxSystemDecorator, LowPriorityDecorator, MapboxButtonDecorator, MessageDecorator, MissingEventsDecorator, PostProgressionDecorator, PrbInviteDecorator, PrestigeFirstEntryDecorator, PrestigeLvlUpDecorator, ProgressiveRewardDecorator, RecruitReminderMessageDecorator, SeniorityAwardsDecorator, WGNCPopUpDecorator, WinbackSelectableRewardReminderDecorator, PersonalMission3QuestDecorator, VehSkillTreePerkAvailableDecorator
from notification.settings import NOTIFICATION_TYPE, NotificationData
from personal_missions import PM_BRANCH
from shared_utils import first
from skeletons.account_helpers.settings_core import ISettingsCache
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.battle_matters import IBattleMattersController
from skeletons.gui.game_control import IBattlePassController, ICollectionsSystemController, IEasyTankEquipController, IEventsNotificationsController, IExchangeRatesWithDiscountsProvider, IGameSessionController, ILimitedUIController, ILootBoxSystemController, ISeniorityAwardsController, ISteamCompletionController, IWinbackController
from skeletons.gui.goodies import IGoodiesCache
from skeletons.gui.impl import INotificationWindowController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.login_manager import ILoginManager
from skeletons.gui.platform.wgnp_controllers import IWGNPSteamAccRequestController
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from uilogging.seniority_awards.constants import SeniorityAwardsLogSpaces
from uilogging.seniority_awards.loggers import CoinsNotificationLogger, RewardNotificationLogger, VehicleSelectionNotificationLogger
from weekly_quests_common.weekly_quests_schema import weeklyQuestsSchema
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
    def getWeeklyQuestsState(cls):
        return cls.__lobbyContext.getServerSettings().getConfigModel(weeklyQuestsSchema).enabled

    @classmethod
    def getNDQState(cls):
        return cls.__lobbyContext.getServerSettings().getDailyQuestConfig().get('ndqSwitch', False)

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
 Configs.WEEKLY_QUESTS_CONFIG.value: {_FeatureState.ON: (None, R.strings.system_messages.weekly_quests.switch_on.body(), SystemMessages.SM_TYPE.MediumInfo),
                                      _FeatureState.OFF: (None, R.strings.system_messages.weekly_quests.switch_off.body(), SystemMessages.SM_TYPE.ErrorSimple),
                                      _FUNCTION: _StateExtractor.getWeeklyQuestsState},
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
        return SM_TYPE.lookup(auxData[0]) == SM_TYPE.CollectionStart if auxData else None

    def __needToLowerPriority(self, messageType):
        excludedTypes = (SYS_MESSAGE_TYPE.premiumBought.index(), SYS_MESSAGE_TYPE.premiumExtended.index(), SYS_MESSAGE_TYPE.bonusExcludedMap.index())
        return messageType in excludedTypes and findActiveWindow(R.views.mono.lootbox.main()) is not None

    def __getMessageDecorator(self, settings, messageType, messageSubtype):
        if settings.decorator is not None:
            return settings.decorator
        if messageType == SYS_MESSAGE_TYPE.autoMaintenance.index():
            if messageSubtype in (AUTO_MAINTENANCE_RESULT.RENT_IS_OVER, AUTO_MAINTENANCE_RESULT.RENT_IS_ALMOST_OVER):
                return C11nMessageDecorator
        if messageType == SYS_MESSAGE_TYPE.customizationChanged.index():
            return C11nMessageDecorator
        elif messageType == SYS_MESSAGE_TYPE.customizationProgress.index():
            return C11nProgressiveItemDecorator
        elif messageType == SYS_MESSAGE_TYPE.personalMissionFailed.index():
            return LockButtonMessageDecorator
        elif messageType in {SYS_MESSAGE_TYPE.postProgressionUnlocked.index(), SYS_MESSAGE_TYPE.postProgressionCompleted.index()}:
            return PostProgressionDecorator
        elif messageType == SYS_MESSAGE_TYPE.prestigeLevelChanged.index():
            return PrestigeLvlUpDecorator
        elif messageType == SYS_MESSAGE_TYPE.battlePassReward.index():
            return BattlePassLockButtonDecorator
        elif messageSubtype in (SCH_CLIENT_MSG_TYPE.MAPBOX_PROGRESSION_REWARD, SCH_CLIENT_MSG_TYPE.MAPBOX_SURVEY_AVAILABLE):
            return MapboxButtonDecorator
        elif messageType == SYS_MESSAGE_TYPE.customization2dProgressionChanged.index():
            return C2DProgressionStyleDecorator
        elif self.__isCollectionsSysMessageTypes(messageType) or self.__isCollectionsSMType(settings):
            return CollectionsLockButtonDecorator
        elif messageType == SYS_MESSAGE_TYPE.personalMission3Quest.index():
            return PersonalMission3QuestDecorator
        else:
            return LowPriorityDecorator if self.__needToLowerPriority(messageType) else MessageDecorator


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

    def __onQueueUpdated(self, count):
        model = self._model()
        if model is not None:
            model.removeNotification(NOTIFICATION_TYPE.MISSING_EVENTS, MissingEventsDecorator.ENTITY_ID)
            if count > 0:
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
            if not progressiveConfig.isEnabled:
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
        if self.__currentStates[featureName] == newState:
            return
        else:
            msg = _FEATURES_DATA[featureName]
            featureState = _FeatureState.ON if newState else _FeatureState.OFF
            msgTitle, msgBody, msgType = msg[featureState]
            messageData = {'header': backport.text(msgTitle)} if msgTitle else None
            SystemMessages.pushMessage(type=msgType, text=backport.text(msgBody), messageData=messageData)
            return


class NDQSwitcherListener(_NotificationListener):
    slots = ('__currentState',)
    __lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self):
        super(NDQSwitcherListener, self).__init__()
        self.__currentState = None
        return

    def start(self, model):
        super(NDQSwitcherListener, self).start(model)
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChange
        self.__currentState = _StateExtractor.getNDQState()
        return True

    def stop(self):
        self.__currentState = None
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChange
        super(NDQSwitcherListener, self).stop()
        return

    def __onServerSettingsChange(self, diff):
        if DAILY_QUESTS_CONFIG in diff:
            newState = _StateExtractor.getNDQState()
            if newState != self.__currentState:
                SystemMessages.pushMessage(backport.text(R.strings.system_messages.newbie_daily_quests.switch_off.body()), type=SystemMessages.SM_TYPE.Warning)
                self.__currentState = newState


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
    __battlePass = dependency.descriptor(IBattlePassController)
    __itemsCache = dependency.descriptor(IItemsCache)
    __notificationCtrl = dependency.descriptor(IEventsNotificationsController)

    def __init__(self):
        super(BattlePassListener, self).__init__()
        self.__isStarted = None
        self.__isFinished = None
        self.__arenaBonusTypesEnabledState = None
        self.__arenaBonusTypesHandlers = None
        return

    def start(self, model):
        super(BattlePassListener, self).start(model)
        self.__isStarted = self.__battlePass.isActive()
        self.__isFinished = self.__battlePass.isSeasonFinished()
        self.__arenaBonusTypesHandlers = {ARENA_BONUS_TYPE.RANKED: self.__pushEnableChangeRanked,
         ARENA_BONUS_TYPE.BATTLE_ROYALE_SOLO: self.__pushBattleRoyaleEnableChange,
         ARENA_BONUS_TYPE.EPIC_BATTLE: self.__pushEpicBattleModeChanged,
         ARENA_BONUS_TYPE.COMP7: self.__pushComp7ModeChanged,
         ARENA_BONUS_TYPE.COMP7_LIGHT: self.__pushComp7LightModeChanged}
        self.__battlePass.onSeasonStateChanged += self.__onSeasonStateChange
        self.__battlePass.onBattlePassSettingsChange += self.__onBattlePassSettingsChange
        self.__notificationCtrl.onEventNotificationsChanged += self.__onEventNotification
        g_eventBus.addListener(events.BattlePassEvent.ON_PAUSE, self.__pushPause)
        self.__checkAndNotify()
        self.__initArenaBonusTypeEnabledStates()
        return True

    def stop(self):
        self.__battlePass.onSeasonStateChanged -= self.__onSeasonStateChange
        self.__battlePass.onBattlePassSettingsChange -= self.__onBattlePassSettingsChange
        self.__notificationCtrl.onEventNotificationsChanged -= self.__onEventNotification
        g_eventBus.removeListener(events.BattlePassEvent.ON_PAUSE, self.__pushPause)
        self.__arenaBonusTypesHandlers = None
        super(BattlePassListener, self).stop()
        return

    def __onEventNotification(self, added, removed=()):
        if not self.__battlePass.isActive():
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
        if self.__battlePass.isEnabled() and newMode == oldMode:
            self.__checkAndNotifyOtherBattleTypes()

    def __onSeasonStateChange(self):
        self.__checkAndNotify()

    def __notifyGamemodeEnabled(self, eventNotification):
        arenaBonusType = eventNotification.data
        if self.__battlePass.isHoliday():
            header = backport.text(R.strings.system_messages.battlePassH.gameModeEnabled.header(), seasonName=backport.text(R.strings.battle_pass.season.fullName.num(self.__battlePass.getSeasonNum())()))
        else:
            header = backport.text(R.strings.system_messages.battlePass.gameModeEnabled.header(), seasonNum=self.__battlePass.getSeasonNum())
        textRes = R.strings.system_messages.battlePass.gameModeEnabled.body.num(arenaBonusType)
        if not textRes.exists():
            _logger.warning('There is no text for given arenaBonusType: %d', arenaBonusType)
            return
        text = backport.text(textRes())
        SystemMessages.pushMessage(text=text, type=SystemMessages.SM_TYPE.BattlePassGameModeEnabled, messageData={'header': header})

    def __notifyStartExtra(self, chapterID):
        settings = AccountSettings.getSettings(IS_BATTLE_PASS_EXTRA_START_NOTIFICATION_SEEN)
        settings.add(chapterID)
        AccountSettings.setSettings(IS_BATTLE_PASS_EXTRA_START_NOTIFICATION_SEEN, settings)
        header = backport.text(R.strings.system_messages.battlePass.extraStarted.header())
        chapterName = backport.text(R.strings.battle_pass.chapter.fullName.num(chapterID)())
        SystemMessages.pushMessage(text=backport.text(R.strings.system_messages.battlePass.extraStarted.body(), name=chapterName), priority=NotificationPriorityLevel.HIGH, type=SM_TYPE.BattlePassExtraStart, messageData={'header': header})

    def __notifyFinishExtra(self, chapterID):
        chapterID = int(chapterID)
        textRes = R.strings.battle_pass.chapter.fullName.num(chapterID)
        if not textRes.exists():
            _logger.warning('There is no text for given chapterID: %d', chapterID)
            return
        chapterName = backport.text(textRes())
        header = backport.text(R.strings.system_messages.battlePass.extraFinish.header(), name=chapterName)
        text = backport.text(R.strings.system_messages.battlePass.extraFinish.body(), name=chapterName)
        SystemMessages.pushMessage(text=text, type=SM_TYPE.BattlePassExtraFinish, messageData={'header': header})

    def __notifyExtraWillEndSoon(self, chapterID):
        chapterID = int(chapterID)
        textRes = R.strings.battle_pass.chapter.fullName.num(chapterID)
        if not textRes.exists() or not self.__battlePass.isChapterExists(chapterID):
            _logger.warning('There is no text or config for given chapterID: %d', chapterID)
            return
        chapterName = backport.text(textRes())
        header = backport.text(R.strings.system_messages.battlePass.extraWillEndSoon.header(), name=chapterName)
        text = backport.text(R.strings.system_messages.battlePass.extraWillEndSoon.body(), name=chapterName)
        SystemMessages.pushMessage(text=text, type=SM_TYPE.BattlePassExtraWillEndSoon, messageData={'header': header}, savedData={'chapterID': chapterID})

    def __checkAndNotifyOtherBattleTypes(self):
        supportedTypes = self.__battlePass.getSupportedArenaBonusTypes()
        for arenaBonusType in supportedTypes:
            oldValue = self.__arenaBonusTypesEnabledState.get(arenaBonusType, False)
            newValue = self.__battlePass.isGameModeEnabled(arenaBonusType)
            self.__arenaBonusTypesEnabledState[arenaBonusType] = newValue
            if oldValue != newValue:
                self.__pushEnableChangedForArenaBonusType(arenaBonusType, newValue)

    def __checkAndNotify(self, oldMode=None, newMode=None):
        isStarted = self.__battlePass.isActive()
        isFinished = self.__battlePass.isSeasonFinished()
        isModeChanged = oldMode is not None and newMode is not None and oldMode != newMode
        isReactivated = newMode == 'enabled' and oldMode == 'paused'
        needToPushStarted = isStarted and not AccountSettings.getSettings(IS_BATTLE_PASS_START_NOTIFICATION_SEEN)
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
        if isStarted:
            for chapterID in self.__battlePass.getExtraChapterIDs():
                if chapterID not in AccountSettings.getSettings(IS_BATTLE_PASS_EXTRA_START_NOTIFICATION_SEEN):
                    self.__notifyStartExtra(chapterID)

        self.__isStarted = isStarted
        self.__isFinished = isFinished
        return

    def __pushPause(self, *_):
        SystemMessages.pushMessage(text=backport.text(R.strings.system_messages.battlePass.switch_pause.body()), type=SystemMessages.SM_TYPE.ErrorSimple, priority=NotificationPriorityLevel.HIGH)

    def __pushFinished(self):
        if self.__battlePass.isHoliday():
            header = backport.text(R.strings.system_messages.battlePassH.switch_disable.title(), seasonName=backport.text(R.strings.battle_pass.season.fullName.num(self.__battlePass.getSeasonNum())()))
            SystemMessages.pushMessage(text=backport.text(R.strings.system_messages.battlePassH.switch_disable.body()), priority=NotificationPriorityLevel.HIGH, type=SystemMessages.SM_TYPE.BattlePassDefault, messageData={'header': header,
             'additionalText': ''})

    def __pushStarted(self):
        if self.__battlePass.isHoliday():
            text = backport.text(R.strings.system_messages.battlePassH.switch_started.body())
            header = backport.text(R.strings.system_messages.battlePassH.switch_started.title(), seasonName=backport.text(R.strings.battle_pass.season.fullName.num(self.__battlePass.getSeasonNum())()))
        else:
            text = backport.text(R.strings.system_messages.battlePass.switch_started.body())
            header = backport.text(R.strings.system_messages.battlePass.switch_started.title(), seasonNum=self.__battlePass.getSeasonNum())
        SystemMessages.pushMessage(text=text, priority=NotificationPriorityLevel.HIGH, type=SystemMessages.SM_TYPE.BattlePassDefault, messageData={'header': header,
         'additionalText': ''})
        AccountSettings.setSettings(IS_BATTLE_PASS_START_NOTIFICATION_SEEN, True)

    def __pushEnabled(self):
        if self.__battlePass.isHoliday():
            text = backport.text(R.strings.system_messages.battlePassH.switch_enabled.body())
        else:
            expiryTime = self.__battlePass.getSeasonFinishTime()
            text = backport.text(R.strings.system_messages.battlePass.switch_enabled.body(), expiryTime=text_styles.titleFont(TimeFormatter.getLongDatetimeFormat(expiryTime)))
        SystemMessages.pushMessage(text=text, priority=NotificationPriorityLevel.HIGH, type=SystemMessages.SM_TYPE.Warning)

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
        supportedTypes = self.__battlePass.getSupportedArenaBonusTypes()
        for arenaBonusType in supportedTypes:
            self.__arenaBonusTypesEnabledState[arenaBonusType] = self.__battlePass.isGameModeEnabled(arenaBonusType)

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

    @staticmethod
    def __pushComp7LightModeChanged(isEnabled):
        if isEnabled:
            msg = backport.text(R.strings.system_messages.battlePass.switch_enabled.comp7Light.body())
            msgType = SystemMessages.SM_TYPE.Warning
        else:
            msg = backport.text(R.strings.system_messages.battlePass.switch_disable.comp7Light.body())
            msgType = SystemMessages.SM_TYPE.ErrorSimple
        SystemMessages.pushMessage(text=msg, type=msgType)


class BattlePassSwitchChapterReminder(BaseReminderListener):
    __battlePassController = dependency.descriptor(IBattlePassController)
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

    def __removeListeners(self):
        self.__battlePassController.onChapterChanged -= self.__tryNotify
        self.__battlePassController.onBattlePassSettingsChange -= self.__tryNotify
        self.__battlePassController.onPointsUpdated -= self.__tryNotify

    def __tryNotify(self, *_):
        isAdding = not (self.__battlePassController.hasActiveChapter() or self.__battlePassController.isCompleted() or self.__battlePassController.isDisabled() or self.__battlePassController.isPaused())
        self._notifyOrRemove(isAdding)


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
        AccountSettings.onSettingsChanging += self.__onAccountSettingsChanging
        return result

    def stop(self):
        super(RecruitReminderListener, self).stop()
        AccountSettings.onSettingsChanging -= self.__onAccountSettingsChanging
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
        return new.getSavedData().get('count') == prev.getSavedData().get('count') and new.isNotify == prev.isNotify

    def __onAccountSettingsChanging(self, key, _):
        if key == RECRUITS_NOTIFICATIONS:
            self.__tryNotify(None)
        return

    def __tryNotify(self, _):
        recruits = getAllRecruitsInfo(sortByExpireTime=True)
        isAdding = len(recruits) > 0
        self._notifyOrRemove(isAdding, recruits=recruits)


class EmailConfirmationReminderListener(BaseReminderListener):
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
        if not self.__steamRegistrationCtrl.isSteamAccount:
            return
        status = yield wg_await(self.__wgnpSteamAccCtrl.getEmailStatus())
        if status.typeIs(StatusTypes.ADDED):
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
            if vehicle.typeDescr.eliteByProgression:
                continue
            if vehicle is not None and vehicle.postProgressionAvailability(unlockOnly=True):
                SystemMessages.pushMessage(text=backport.text(msgKey.single.body(), vehicle=vehicle.userName), type=SM_TYPE.InformationHeader, priority=NotificationPriorityLevel.HIGH, messageData={'header': backport.text(msgKey.title())})

        return


class SeniorityAwardsTokenListener(BaseReminderListener):
    __slots__ = ('__uiCoinsNotificationLogger',)
    __itemsCache = dependency.descriptor(IItemsCache)
    __seniorityAwardCtrl = dependency.descriptor(ISeniorityAwardsController)
    __TYPE = NOTIFICATION_TYPE.SENIORITY_AWARDS_TOKENS
    __ENTITY_ID = 0
    __DAYS_BETWEEN_NOTIFICATIONS = 30
    __TEMPLATE = 'seniorityAwardsTokens'

    def __init__(self):
        super(SeniorityAwardsTokenListener, self).__init__(self.__TYPE, self.__ENTITY_ID)
        self.__uiCoinsNotificationLogger = CoinsNotificationLogger()

    def start(self, model):
        result = super(SeniorityAwardsTokenListener, self).start(model)
        if result:
            self.__seniorityAwardCtrl.onUpdated += self.__onUpdated
            g_clientUpdateManager.addCallbacks({'cache.dynamicCurrencies.{}'.format(WDR_CURRENCY): self.__onBalanceUpdate})
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
        coinsCount = self.__seniorityAwardCtrl.getSACoin()
        if coinsCount < 1 or not self.__seniorityAwardCtrl.isAvailable or self.__seniorityAwardCtrl.timeLeft <= 0:
            self._removeNotification()
            return
        else:
            lastShownTime = AccountSettings.getNotifications(SENIORITY_AWARDS_COINS_REMINDER_SHOWN_TIMESTAMP)
            if lastShownTime is None:
                self.__updateLastShownTimestamp()
                return
            pendingReminderTimestamp = self.__seniorityAwardCtrl.pendingReminderTimestamp
            currentTimestamp = time_utils.getServerUTCTime()
            showByPending = bool(pendingReminderTimestamp and lastShownTime < pendingReminderTimestamp)
            showByInterval = bool(not pendingReminderTimestamp and currentTimestamp - lastShownTime >= time_utils.ONE_DAY * self.__DAYS_BETWEEN_NOTIFICATIONS)
            if showByPending or showByInterval:
                priority = NotificationPriorityLevel.MEDIUM
                parentScreen = SeniorityAwardsLogSpaces.HANGAR
            else:
                priority = NotificationPriorityLevel.LOW
                parentScreen = SeniorityAwardsLogSpaces.NOTIFICATION_CENTER
            if self._notify(priority=priority):
                if priority != NotificationPriorityLevel.LOW:
                    WWISE.WW_eventGlobal(backport.sound(R.sounds.wdr_hangar_notification()))
                self.__updateLastShownTimestamp()
                self.__uiCoinsNotificationLogger.handleDisplayedAction(parentScreen)
            return

    @staticmethod
    def __updateLastShownTimestamp():
        currentTimestamp = time_utils.getServerUTCTime()
        AccountSettings.setNotifications(SENIORITY_AWARDS_COINS_REMINDER_SHOWN_TIMESTAMP, currentTimestamp)


class SeniorityAwardsQuestListener(_NotificationListener):
    __slots__ = ('__uiRewardNotificationLogger',)
    __TYPE = NOTIFICATION_TYPE.SENIORITY_AWARDS_QUEST
    __TEMPLATE = 'seniorityAwardsQuest22'
    __ENTITY_ID = 0
    __seniorityAwardCtrl = dependency.descriptor(ISeniorityAwardsController)
    __limitedUIController = dependency.descriptor(ILimitedUIController)

    def __init__(self):
        super(SeniorityAwardsQuestListener, self).__init__()
        self.__uiRewardNotificationLogger = RewardNotificationLogger()

    def start(self, model):
        result = super(SeniorityAwardsQuestListener, self).start(model)
        self.__seniorityAwardCtrl.onUpdated += self.__tryNotify
        self.__limitedUIController.startObserve(LUI_RULES.WDRNewbieReward, self.__NotifyHandler)
        self.__tryNotify()
        return result

    def stop(self):
        self.__seniorityAwardCtrl.onUpdated -= self.__tryNotify
        self.__limitedUIController.stopObserve(LUI_RULES.WDRNewbieReward, self.__NotifyHandler)
        super(SeniorityAwardsQuestListener, self).stop()

    def __NotifyHandler(self, *_):
        self.__tryNotify()

    def __tryNotify(self):
        model = self._model()
        if not model:
            return
        else:
            if self.__seniorityAwardCtrl.isNeedToShowRewardNotification:
                limitedUIRuleCompleted = self.__limitedUIController.isRuleCompleted(LUI_RULES.WDRNewbieReward)
                showRewardNotification = self.__seniorityAwardCtrl.showRewardHangarNotification
                isHangarNotification = showRewardNotification and limitedUIRuleCompleted
                priority = NotificationPriorityLevel.MEDIUM if isHangarNotification else NotificationPriorityLevel.LOW
                prevNotification = model.getNotification(self.__TYPE, self.__ENTITY_ID)
                if prevNotification:
                    if prevNotification.getPriorityLevel() == priority:
                        return
                    model.removeNotification(self.__TYPE, self.__ENTITY_ID)
                model.addNotification(SeniorityAwardsDecorator(self.__ENTITY_ID, self.__TYPE, None, model, self.__TEMPLATE, priority, useCounterOnce=False, isNotify=self.__seniorityAwardCtrl.isNeedToShowNotificationBullet))
                parentScreen = SeniorityAwardsLogSpaces.NOTIFICATION_CENTER
                if priority != NotificationPriorityLevel.LOW:
                    parentScreen = SeniorityAwardsLogSpaces.HANGAR
                    WWISE.WW_eventGlobal(backport.sound(R.sounds.wdr_hangar_notification()))
                self.__uiRewardNotificationLogger.handleDisplayedAction(parentScreen, limitedUIRuleCompleted, self.__seniorityAwardCtrl.isNeedToShowNotificationBullet)
            else:
                model.removeNotification(self.__TYPE, self.__ENTITY_ID)
            return


class SeniorityAwardsStateListener(_NotificationListener):
    __seniorityAwardCtrl = dependency.descriptor(ISeniorityAwardsController)

    def start(self, model):
        result = super(SeniorityAwardsStateListener, self).start(model)
        if result:
            self.__seniorityAwardCtrl.onUpdated += self.__checkLastEventState
            self.__checkLastEventState()
        return result

    def stop(self):
        self.__seniorityAwardCtrl.onUpdated -= self.__checkLastEventState
        super(SeniorityAwardsStateListener, self).stop()

    @staticmethod
    def __pushPause():
        SystemMessages.pushMessage(text=backport.text(R.strings.system_messages.seniorityAwards.switch_pause_on.body()), type=SystemMessages.SM_TYPE.ErrorSimple, priority=NotificationPriorityLevel.HIGH)

    @staticmethod
    def __pushPauseFinished():
        SystemMessages.pushMessage(text=backport.text(R.strings.system_messages.seniorityAwards.switch_pause_off.body()), type=SystemMessages.SM_TYPE.Warning, priority=NotificationPriorityLevel.HIGH)

    def __checkLastEventState(self):
        if self.__seniorityAwardCtrl.isEnabled:
            isActive = self.__seniorityAwardCtrl.isActive
            showedOnPause = isSeniorityAwardsSystemNotificationShowed(SeniorityAwardsStorageKeys.SENIORITY_AWARDS_ON_PAUSE_NOTIFICATION_SHOWED)
            if not isActive and not showedOnPause:
                self.__pushPause()
                setSeniorityAwardEventStateSetting(True)
            elif isActive and showedOnPause:
                self.__pushPauseFinished()
                setSeniorityAwardEventStateSetting(False)


class SeniorityAwardsVehicleSelectionListener(BaseReminderListener):
    __slots__ = ('__uiVehicleSelectionNotificationLogger',)
    __seniorityAwardCtrl = dependency.descriptor(ISeniorityAwardsController)
    __TYPE = NOTIFICATION_TYPE.SENIORITY_AWARDS_VEHICLE_SELECTION
    __ENTITY_ID = 0
    __PRIORITY = NotificationPriorityLevel.LOW
    __TEMPLATE = 'seniorityAwardsVehicleSelection'

    def __init__(self):
        super(SeniorityAwardsVehicleSelectionListener, self).__init__(self.__TYPE, self.__ENTITY_ID)
        self.__uiVehicleSelectionNotificationLogger = VehicleSelectionNotificationLogger()

    def start(self, model):
        result = super(SeniorityAwardsVehicleSelectionListener, self).start(model)
        if result:
            self.__seniorityAwardCtrl.onUpdated += self.__onUpdated
            self.__seniorityAwardCtrl.onVehicleSelectionChanged += self.__onVehicleSelectionChanged
            self.__tryNotify()
        return result

    def stop(self):
        super(SeniorityAwardsVehicleSelectionListener, self).stop()
        self.__seniorityAwardCtrl.onUpdated -= self.__onUpdated
        self.__seniorityAwardCtrl.onVehicleSelectionChanged -= self.__onVehicleSelectionChanged

    def _createNotificationData(self, priority, **ctx):
        vehiclesCanSelect = self.__seniorityAwardCtrl.getVehiclesForSelectionCount
        allVehiclesForSelection = len(self.__seniorityAwardCtrl.getAvailableVehicleSelectionRewards())
        data = {'count': str(min(vehiclesCanSelect, allVehiclesForSelection))}
        return NotificationData(self._getNotificationId(), data, priority, None)

    def _createDecorator(self, data):
        return SeniorityAwardsDecorator(data.entityID, self._getNotificationType(), data.savedData, self._model(), self.__TEMPLATE, data.priorityLevel)

    def __onUpdated(self):
        self.__tryNotify()

    def __onVehicleSelectionChanged(self, *args):
        self.__tryNotify()

    def __tryNotify(self):
        if self.__seniorityAwardCtrl.isVehicleSelectionAvailable:
            if self._notify(priority=self.__PRIORITY):
                self.__uiVehicleSelectionNotificationLogger.handleDisplayedAction()
        else:
            self._removeNotification()


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


class CollectionsListener(_NotificationListener, EventsHandler):
    __collections = dependency.descriptor(ICollectionsSystemController)
    __eventNotifications = dependency.descriptor(IEventsNotificationsController)
    __NOTIFICATIONS = R.strings.collections.notifications
    __COLLECTION_ENTRY_ENTITY_ID = 0

    def start(self, model):
        result = super(CollectionsListener, self).start(model)
        if result:
            self._subscribe()
            self.__tryNotify(self.__eventNotifications.getEventsNotifications())
        return True

    def stop(self):
        self._unsubscribe()
        super(CollectionsListener, self).stop()

    def _getEvents(self):
        return ((self.__eventNotifications.onEventNotificationsChanged, self.__onEventNotification), (self.__collections.onAvailabilityChanged, self.__onAvailabilityChanged))

    def __onEventNotification(self, added, _):
        self.__tryNotify(added)

    def __onAvailabilityChanged(self, enabled):
        (self.__pushEnabled if enabled else self.__pushDisabled)()

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
        if not isCollectionStartedSeen(collectionID):
            self.__pushStarted(collection)
            setCollectionStartedSeen(collectionID)

    def __onCollectionsUpdatedEntryEvent(self, notification):
        if not isCollectionsUpdatedEntrySeen():
            self.__pushCollectionsCustomMessage(backport.text(self.__NOTIFICATIONS.updatedEntry.title()), backport.text(self.__NOTIFICATIONS.updatedEntry.text()), 'CollectionsEntrySysMessage', NOTIFICATION_TYPE.COLLECTIONS_ENTRY, self.__COLLECTION_ENTRY_ENTITY_ID)

    def __onCollectionsRenewEvent(self, notification):
        notificationData = json.loads(notification.data)
        collections = (c for c in (self.__collections.getCollection(collectionID) for collectionID in notificationData['collectionsIds']) if c is not None)
        for collection in collections:
            if not isCollectionRenewSeen(collection.collectionId):
                self.__pushCollectionsCustomMessage(backport.text(self.__NOTIFICATIONS.renew.title(), feature=backport.text(self.__NOTIFICATIONS.feature.dyn(collection.name)()), season=backport.text(self.__NOTIFICATIONS.season.dyn(collection.name)())), backport.text(self.__NOTIFICATIONS.renew.text()), 'CollectionRenewSysMessage', NOTIFICATION_TYPE.COLLECTIONS_RENEW, collection.collectionId, savedData={'collectionId': collection.collectionId})

    def __pushCollectionsCustomMessage(self, title, text, messageType, notificationType, entityID, savedData=None):
        model = self._model()
        if not model.hasNotification(notificationType, entityID):
            message = {'title': title,
             'text': text}
            notification = CollectionCustomMessageDecorator(entityID=entityID, message=message, messageType=messageType, notificationType=notificationType, savedData=savedData, model=model)
            model.addNotification(notification)

    def __pushStarted(self, collection):
        feature = backport.text(self.__NOTIFICATIONS.feature.dyn(collection.name)())
        title = backport.text(self.__NOTIFICATIONS.eventStart.title(), feature=feature)
        text = backport.text(self.__NOTIFICATIONS.eventStart.text(), feature=feature)
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
        self.__winbackController.onConfigUpdated += self.__tryNotify

    def __removeListeners(self):
        self.__itemsCache.onSyncCompleted -= self.__tryNotify
        self.__winbackController.onStateUpdated -= self.__tryNotify
        self.__winbackController.onConfigUpdated -= self.__tryNotify

    def __tryNotify(self, *_):
        isAdding = self.__winbackController.hasWinbackOfferToken() and self.__winbackController.isFinished() and self.__winbackController.winbackConfig.isProgressionEnabled
        self._notifyOrRemove(isAdding)


class BattleMattersTaskReminderListener(BaseReminderListener, EventsHandler):
    __bmCtrl = dependency.descriptor(IBattleMattersController)
    __gameSession = dependency.descriptor(IGameSessionController)
    __TYPE = NOTIFICATION_TYPE.BATTLE_MATTERS_TASK_REMINDER
    __ENTITY_ID = 0
    __TEMPLATE = 'BattleMattersTaskReminder'
    __BATTLES_WITHOUT_PROGRESS_PERIOD = 6

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
        isAdding = self.__bmCtrl.isActive() and self.__bmCtrl.getCurrentQuest() is not None
        needToPopUp = self.__bmCtrl.progressWatcher.isJustBackFromBattle(reset=True) and (self.__isLongTimeWithoutProgress() or not self.__isShowedToday())
        priority = NotificationPriorityLevel.LOW
        if isAdding and needToPopUp:
            priority = NotificationPriorityLevel.MEDIUM
            AccountSettings.setBattleMattersSetting(BattleMatters.REMINDER_LAST_DISPLAY_TIME, time_utils.getServerUTCTime())
        self._notifyOrRemove(isAdding, priority=priority)
        return

    def __isLongTimeWithoutProgress(self):
        battlesWithoutProgress = self.__bmCtrl.progressWatcher.getBattlesCountWithoutProgress()
        return battlesWithoutProgress > 0 and battlesWithoutProgress % self.__BATTLES_WITHOUT_PROGRESS_PERIOD == 0

    def __isShowedToday(self):
        lastDisplayTime = AccountSettings.getBattleMattersSetting(BattleMatters.REMINDER_LAST_DISPLAY_TIME)
        return self.__isToday(lastDisplayTime)

    @staticmethod
    def __isToday(timestamp):
        todayStart, todayEnd = time_utils.getDayTimeBoundsForLocal(time_utils.getServerUTCTime())
        return todayStart <= timestamp <= todayEnd


class PrestigeListener(_NotificationListener):
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __itemsCache = dependency.descriptor(IItemsCache)
    __PRESTIGE_MESSAGES = R.strings.messenger.serviceChannelMessages.prestige
    __START_ENTITY_ID = 0

    def start(self, model):
        result = super(PrestigeListener, self).start(model)
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChange
        g_playerEvents.onVehicleBecomeElite += self.__onVehicleBecomeElite
        if result:
            self.__tryNotify()
        return result

    def stop(self):
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChange
        g_playerEvents.onVehicleBecomeElite -= self.__onVehicleBecomeElite
        super(PrestigeListener, self).stop()

    def __onServerSettingsChange(self, diff):
        prestigeChanged = diff.get('prestige_config')
        if not prestigeChanged:
            return
        model = self._model()
        config = self.__lobbyContext.getServerSettings().prestigeConfig
        if not config.isEnabled and model:
            model.removeNotification(NOTIFICATION_TYPE.PRESTIGE_FIRST_ENTRY, self.__START_ENTITY_ID)

    def __onVehicleBecomeElite(self, *vehicleIntCDs):
        msgKey = R.strings.system_messages.vehicleMilestones.vanityAvailable
        config = self.__lobbyContext.getServerSettings().prestigeMilestonesConfig
        for intCD in vehicleIntCDs:
            vehicle = self.__itemsCache.items.getItemByCD(intCD)
            if vehicle is None or not vehicle.postProgressionAvailability(unlockOnly=True):
                continue
            if intCD not in config.milestones:
                continue
            SystemMessages.pushMessage(text=backport.text(msgKey.text(), vehicle=vehicle.userName), type=SM_TYPE.InformationHeader, priority=NotificationPriorityLevel.HIGH, messageData={'header': backport.text(msgKey.title())})

        return

    def __tryNotify(self):
        model = self._model()
        if model is None:
            return
        else:
            config = self.__lobbyContext.getServerSettings().prestigeConfig
            if not config.isEnabled:
                return
            prestigeVehicle = self.__itemsCache.items.getAccountDossier().getPrestigeStats().getVehicles()
            if not prestigeVehicle:
                setFirstEntryNotificationShown()
                return
            if isFirstEntryNotificationShown():
                return
            text = backport.text(self.__PRESTIGE_MESSAGES.firstEntry.text())
            title = backport.text(self.__PRESTIGE_MESSAGES.firstEntry.title())
            gradeType, grade = mapGradeIDToUI(MAX_GRADE_ID)
            messageData = {'title': title,
             'text': text}
            linkageData = {'type': gradeType.value,
             'grade': grade,
             'lvl': None}
            model.addNotification(PrestigeFirstEntryDecorator(message=messageData, linkageData=linkageData, entityID=self.__START_ENTITY_ID, model=model))
            setFirstEntryNotificationShown()
            return


class BaseExchangeRateWithDiscountsListener(BaseReminderListener):
    __metaclass__ = ABCMeta
    __TEMPLATE = 'ExchangeRatePersonalDiscount'
    __ENTITY_ID = 0
    __PRIORITY_LEVEL = NotificationPriorityLevel.LOW
    _TYPE = None
    _EXCHANGE_TYPE = None
    __NOTIFICATION_FORMAT_MAPPING = {ExchangeRateShowFormat.COEFFICIENT: PERSONAL_EXCHANGE_RATES.NOTIFICATION_TYPE_FACTOR,
     ExchangeRateShowFormat.INTEGER: PERSONAL_EXCHANGE_RATES.NOTIFICATION_TYPE_INT,
     ExchangeRateShowFormat.TEMPORARY: PERSONAL_EXCHANGE_RATES.NOTIFICATION_TYPE_TEMP,
     ExchangeRateShowFormat.LIMITED: PERSONAL_EXCHANGE_RATES.NOTIFICATION_TYPE_FACTOR}
    __exchangeRatesProvider = dependency.descriptor(IExchangeRatesWithDiscountsProvider)

    def __init__(self):
        self.__discount = None
        super(BaseExchangeRateWithDiscountsListener, self).__init__(self._TYPE, self.__ENTITY_ID)
        return

    def start(self, model):
        result = super(BaseExchangeRateWithDiscountsListener, self).start(model)
        self._exchangeRate.onUpdated += self._onUpdate
        self.__tryNotify()
        return result

    def stop(self):
        self._exchangeRate.onUpdated -= self._onUpdate
        super(BaseExchangeRateWithDiscountsListener, self).stop()

    @property
    def _exchangeRate(self):
        return self.__exchangeRatesProvider.get(self._EXCHANGE_TYPE)

    @property
    def _discountTypeName(self):
        raise NotImplementedError

    @property
    def _discountPercent(self):
        return self._exchangeRate.exchangeDiscountPercent

    def _createNotificationData(self, priority, **ctx):
        data = {'type': self._discountTypeName,
         'format': self.__discountShowFormat,
         'endTime': self.__discountEndTime,
         'discountPercent': self._discountPercent}
        return NotificationData(self._getNotificationId(), data, priority, None)

    def _createDecorator(self, data):
        decorator = ExchangeRateDiscountDecorator(data.entityID, self._getNotificationType(), data.savedData, self._model(), self.__TEMPLATE, data.priorityLevel)
        return decorator

    def _onUpdate(self):
        self.__tryNotify()

    @property
    def __discountInformation(self):
        return self._exchangeRate.discountInfo

    @property
    def __discountShowFormat(self):
        return self.__NOTIFICATION_FORMAT_MAPPING.get(self.__discountInformation.showFormat, ExchangeRateShowFormat.COEFFICIENT)

    @property
    def __discountEndTime(self):
        return self.__discountInformation.discountLifetime

    def __tryNotify(self):
        if self.__discount is None or self.__discountInformation is None or self.__discount != self.__discountInformation.tokenName:
            self.__discount = self.__discountInformation.tokenName if self.__discountInformation is not None else None
            self._notifyOrRemove(self._exchangeRate.isDiscountAvailable(), isStateChanged=True, priority=self.__PRIORITY_LEVEL)
        return


class GoldExchangeRatesDiscountsListener(BaseExchangeRateWithDiscountsListener):
    _TYPE = NOTIFICATION_TYPE.EXCHANGE_RATE_GOLD_DISCOUNT
    _EXCHANGE_TYPE = EXCHANGE_RATE_GOLD_NAME

    @property
    def _discountTypeName(self):
        return PERSONAL_EXCHANGE_RATES.EXCHANGE_TYPE_GOLD


class XpTranslationRatesDiscountsListener(BaseExchangeRateWithDiscountsListener):
    _TYPE = NOTIFICATION_TYPE.EXCHANGE_RATE_XP_DISCOUNT
    _EXCHANGE_TYPE = EXCHANGE_RATE_FREE_XP_NAME

    @property
    def _discountTypeName(self):
        return PERSONAL_EXCHANGE_RATES.EXCHANGE_TYPE_EXP


class EasyTankEquipStateListener(_NotificationListener):
    __easyTankEquipCtrl = dependency.descriptor(IEasyTankEquipController)

    def __init__(self):
        super(EasyTankEquipStateListener, self).__init__()
        self.__isAvailable = self.__easyTankEquipCtrl.config.enabled

    def start(self, model):
        result = super(EasyTankEquipStateListener, self).start(model)
        if result:
            self.__easyTankEquipCtrl.onUpdated += self.__checkLastState
            self.__checkLastState()
        return result

    def stop(self):
        self.__easyTankEquipCtrl.onUpdated -= self.__checkLastState
        super(EasyTankEquipStateListener, self).stop()

    @staticmethod
    def __pushPause():
        SystemMessages.pushMessage(text=backport.text(R.strings.system_messages.easyTankEquip.switch_pause_on.body()), type=SystemMessages.SM_TYPE.ErrorSimple, priority=NotificationPriorityLevel.HIGH)

    @staticmethod
    def __pushPauseFinished():
        SystemMessages.pushMessage(text=backport.text(R.strings.system_messages.easyTankEquip.switch_pause_off.body()), type=SystemMessages.SM_TYPE.Warning, priority=NotificationPriorityLevel.HIGH)

    def __checkLastState(self):
        if self.__isAvailable != self.__easyTankEquipCtrl.config.enabled:
            if self.__easyTankEquipCtrl.config.enabled is False:
                self.__pushPause()
            else:
                self.__pushPauseFinished()
            self.__isAvailable = self.__easyTankEquipCtrl.config.enabled


class LootBoxSystemListener(_NotificationListener):
    __slots__ = ('__isActive', '__isLootBoxesWasStarted')
    __lootBoxes = dependency.descriptor(ILootBoxSystemController)
    __nameRes = 'eventName/lowerCase'.split('/')
    __START_ENTITY_ID = 0

    def __init__(self):
        super(LootBoxSystemListener, self).__init__()
        self.__isAvailable = None
        return

    def start(self, model):
        result = super(LootBoxSystemListener, self).start(model)
        self.__lootBoxes.onStatusChanged += self.__onStatusChanged
        self.__lootBoxes.onBoxesAvailabilityChanged += self.__onAvailabilityChanged
        if result:
            self.__tryNotify()
        return True

    def stop(self):
        self.__lootBoxes.onStatusChanged -= self.__onStatusChanged
        self.__lootBoxes.onBoxesAvailabilityChanged -= self.__onAvailabilityChanged
        super(LootBoxSystemListener, self).stop()

    def __tryNotify(self):
        self.__onStatusChanged()
        self.__onAvailabilityChanged()

    def __onStatusChanged(self):
        for eventName in self.__lootBoxes.eventNames:
            isActive = self.__lootBoxes.isActive(eventName)
            isVisible = getIsStartFinishNotificationsVisible(eventName)
            isLootBoxesWasStarted = self.__lootBoxes.getSetting(eventName, LOOT_BOXES_WAS_STARTED)
            isLootBoxesWasFinished = self.__lootBoxes.getSetting(eventName, LOOT_BOXES_WAS_FINISHED)
            if isActive and isVisible and not isLootBoxesWasStarted:
                self.__pushStarted(eventName)
            if not isActive and isVisible and isLootBoxesWasStarted and not isLootBoxesWasFinished:
                self.__pushFinished(eventName, self.__lootBoxes.getBoxesCount(eventName))

    def __onAvailabilityChanged(self):
        if self.__isAvailable is not None and self.__isAvailable != self.__lootBoxes.isLootBoxesAvailable:
            if self.__lootBoxes.isLootBoxesAvailable:
                for eventName in self.__lootBoxes.getActiveEvents():
                    self.__pushLootBoxesEnabled(eventName)

            else:
                for eventName in self.__lootBoxes.getActiveEvents():
                    self.__pushLootBoxesDisabled(eventName)

        self.__isAvailable = self.__lootBoxes.isLootBoxesAvailable
        return

    def __pushStarted(self, eventName):
        res = 'serviceChannelMessages/start'.split('/')
        model = self._model()
        if model is not None:
            _, finish = self.__lootBoxes.getActiveTime(eventName)
            localFinishTime = time_utils.makeLocalServerTime(finish)
            eventNameText = backport.text(getTextResource(self.__nameRes, eventName)())
            messageData = {'header': backport.text(getTextResource(res + [NotificationPathPart.HEADER], eventName)(), eventName=eventNameText),
             'text': backport.text(getTextResource(res + [NotificationPathPart.TEXT], eventName)(), date=TimeFormatter.getShortDateFormat(localFinishTime))}
            model.addNotification(LootBoxSystemDecorator(message=messageData, entityID=self.__START_ENTITY_ID, model=model, savedData={'eventName': eventName}))
            self.__lootBoxes.setSetting(eventName, LOOT_BOXES_WAS_STARTED, True)
        return

    def __pushFinished(self, eventName, boxesCount):
        res = 'serviceChannelMessages/finish'.split('/')
        eventNameText = backport.text(getTextResource(self.__nameRes, eventName)())
        SystemMessages.pushMessage(text=backport.text(R.strings.lootbox_system.helpers.doubleBreakLine()) + backport.text(getTextResource(res + [NotificationPathPart.TEXT], eventName)()) if boxesCount > 0 else '', priority=NotificationPriorityLevel.MEDIUM, type=SystemMessages.SM_TYPE.LootBoxSystemFinish, messageData={'header': backport.text(getTextResource(res + [NotificationPathPart.HEADER], eventName)(), eventName=eventNameText)})
        self.__lootBoxes.setSetting(eventName, LOOT_BOXES_WAS_FINISHED, True)

    @staticmethod
    def __pushLootBoxesEnabled(eventName):
        res = 'serviceChannelMessages/lootBoxesEnabled'.split('/')
        SystemMessages.pushMessage(text=backport.text(getTextResource(res + [NotificationPathPart.TEXT], eventName)()), priority=NotificationPriorityLevel.HIGH, type=SystemMessages.SM_TYPE.LootBoxSystemEnabled, messageData={'header': backport.text(getTextResource(res + [NotificationPathPart.HEADER], eventName)())})

    @staticmethod
    def __pushLootBoxesDisabled(eventName):
        res = 'serviceChannelMessages/lootBoxesDisabled'.split('/')
        SystemMessages.pushMessage(text=backport.text(getTextResource(res + [NotificationPathPart.TEXT], eventName)()), priority=NotificationPriorityLevel.HIGH, type=SystemMessages.SM_TYPE.LootBoxSystemDisabled, messageData={'header': backport.text(getTextResource(res + [NotificationPathPart.HEADER], eventName)())})


class PM3NotificationListener(_NotificationListener):
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __settingsCache = dependency.descriptor(ISettingsCache)
    __eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self):
        super(PM3NotificationListener, self).__init__()
        self.__currentDisabledOperations = set()
        self.__currentDisabledMissions = set()

    def start(self, model):
        result = super(PM3NotificationListener, self).start(model)
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChange
        self.__settingsCache.onSyncCompleted += self.__onSettingsCacheSynced
        self.__currentDisabledOperations = set(self.__eventsCache.getPersonalMissions().getDisabledPMOperations())
        self.__currentDisabledMissions = set(self.__lobbyContext.getServerSettings().getDisabledPersonalMissions())
        return result

    def stop(self):
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChange
        self.__settingsCache.onSyncCompleted -= self.__onSettingsCacheSynced
        super(PM3NotificationListener, self).stop()

    def __onSettingsCacheSynced(self):
        self.__currentDisabledMissions = set(self.__lobbyContext.getServerSettings().getDisabledPersonalMissions())

    def __onServerSettingsChange(self, diff):
        if 'isPM3QuestEnabled' in diff and 'isPM2QuestEnabled' in diff and 'isRegularQuestEnabled' in diff:
            self.__allCampaignsSwitcherNotify(diff)
        else:
            self.__campaignSwitcherNotify(diff)
        if diff.get('disabledPMOperations') is not None:
            self.__operationSwitcherNotify(diff)
        if diff.get('disabledPersonalMissions') is not None:
            self.__missionSwitcherNotify(diff)
        return

    @staticmethod
    def __pushMessage(text, priority, messageType, title):
        SystemMessages.pushMessage(text=text, type=messageType, priority=priority, messageData={'title': title})

    def __allCampaignsSwitcherNotify(self, diff):
        if all((diff['isPM3QuestEnabled'], diff['isPM2QuestEnabled'], diff['isRegularQuestEnabled'])):
            SystemMessages.pushI18nMessage(SYSTEM_MESSAGES.PERSONALMISSION_SWITCHERNOTIFICATION_ALLCAMPAIGNSON, type=SystemMessages.SM_TYPE.Information, priority=NotificationPriorityLevel.HIGH)
        if not any((diff['isPM3QuestEnabled'], diff['isPM2QuestEnabled'], diff['isRegularQuestEnabled'])):
            SystemMessages.pushI18nMessage(SYSTEM_MESSAGES.PERSONALMISSION_SWITCHERNOTIFICATION_ALLCAMPAIGNSOFF, type=SystemMessages.SM_TYPE.ErrorSimple, priority=NotificationPriorityLevel.HIGH)

    def __campaignSwitcherNotify(self, diff):
        for campaignSwitcher in PM_SWITCHER_CAMPAIGN:
            if campaignSwitcher in diff:
                branch = PM_SWITCHER_CAMPAIGN[campaignSwitcher]
                campaignName = self.__eventsCache.getPersonalMissions().getAllCampaigns(branches=PM_BRANCH.ALL)[PM_CAMPAIGNS_IDS[branch]].getUserName()
                if not diff[campaignSwitcher]:
                    message = SYSTEM_MESSAGES.PERSONALMISSION_SWITCHERNOTIFICATION_CAMPAIGNOFF
                    iconType = SystemMessages.SM_TYPE.ErrorSimple
                else:
                    iconType = SystemMessages.SM_TYPE.Information
                    message = SYSTEM_MESSAGES.PERSONALMISSION_SWITCHERNOTIFICATION_CAMPAIGNON
                SystemMessages.pushI18nMessage(message, type=iconType, priority=NotificationPriorityLevel.HIGH, campaignName=campaignName)

    def __getCampaignName(self, operation):
        return self.__eventsCache.getPersonalMissions().getAllCampaigns(PM_BRANCH.ALL)[operation.getCampaignID()].getUserName()

    def __operationSwitcherNotify(self, diff):
        newDisabledOperations = set(self.__eventsCache.getPersonalMissions().getDisabledPMOperations())
        disabledOperationsToNotify = newDisabledOperations - self.__currentDisabledOperations
        newEnabledOperations = self.__currentDisabledOperations - newDisabledOperations
        allOperations = self.__eventsCache.getPersonalMissions().getAllOperations(PM_BRANCH.ALL)
        self.__currentDisabledOperations = newDisabledOperations
        for operationID in disabledOperationsToNotify:
            operation = allOperations.get(operationID)
            if not operation:
                _logger.error('Wrong disabled personal mission operationID "%s"', operationID)
                continue
            campaignName = self.__getCampaignName(operation)
            SystemMessages.pushI18nMessage(SYSTEM_MESSAGES.PERSONALMISSION_SWITCHERNOTIFICATION_OPERATIONOFF, type=SystemMessages.SM_TYPE.ErrorSimple, piority=NotificationPriorityLevel.MEDIUM, operationName=operation.getShortUserName(), campaignName=campaignName)

        for operationID in newEnabledOperations:
            operation = allOperations.get(operationID)
            if operation is None:
                _logger.error('Wrong enabled personal mission operationID "%s"', operationID)
                continue
            campaignName = self.__eventsCache.getPersonalMissions().getAllCampaigns(PM_BRANCH.ALL)[operation.getCampaignID()].getUserName()
            SystemMessages.pushI18nMessage(SYSTEM_MESSAGES.PERSONALMISSION_SWITCHERNOTIFICATION_OPERATIONON, type=SystemMessages.SM_TYPE.Information, priority=NotificationPriorityLevel.MEDIUM, operationName=operation.getShortUserName(), campaignName=campaignName)

        return

    def __missionSwitcherNotify(self, diff):
        newDisabledMissions = set(diff.get('disabledPersonalMissions', {}))
        newDisabledMissionsToNotify = newDisabledMissions - self.__currentDisabledMissions
        newEnabledMissions = self.__currentDisabledMissions - newDisabledMissions
        allMissions = self.__eventsCache.getPersonalMissions().getAllQuests(PM_BRANCH.ALL)
        allOperations = self.__eventsCache.getPersonalMissions().getAllOperations(PM_BRANCH.ALL)
        for missionID in newDisabledMissionsToNotify:
            mission = allMissions.get(missionID)
            if not mission:
                _logger.error('Wrong disabled personal mission ID "%s"', missionID)
                continue
            operation = allOperations.get(mission.getOperationID())
            SystemMessages.pushI18nMessage(SYSTEM_MESSAGES.PERSONALMISSION_SWITCHERNOTIFICATION_MISSIONOFF, type=SystemMessages.SM_TYPE.ErrorSimple, priority=NotificationPriorityLevel.MEDIUM, operationName=operation.getShortUserName(), missionName=mission.getShortUserName())

        for missionID in newEnabledMissions:
            mission = allMissions.get(missionID)
            if mission is None:
                _logger.error('Wrong enabled personal mission ID "%s"', missionID)
                continue
            operation = allOperations.get(mission.getOperationID())
            SystemMessages.pushI18nMessage(SYSTEM_MESSAGES.PERSONALMISSION_SWITCHERNOTIFICATION_MISSIONON, type=SystemMessages.SM_TYPE.Information, priority=NotificationPriorityLevel.MEDIUM, operationName=operation.getShortUserName(), missionName=mission.getShortUserName())

        self.__currentDisabledMissions = newDisabledMissions
        return


class SkillTreePerkAvailableListener(BaseReminderListener):
    __itemsCache = dependency.descriptor(IItemsCache)
    __ENTITY_ID = 0

    def __init__(self):
        super(SkillTreePerkAvailableListener, self).__init__(NOTIFICATION_TYPE.VEH_SKILL_TREE_PERK_AVAILABLE, self.__ENTITY_ID)

    def start(self, model):
        result = super(SkillTreePerkAvailableListener, self).start(model)
        if result:
            g_clientUpdateManager.addCallbacks({'stats.vehTypeXP': self.__onVehicleXPUpdated})
            self.__tryNotify()

    def stop(self):
        super(SkillTreePerkAvailableListener, self).stop()
        g_clientUpdateManager.removeObjectCallbacks(self)

    def _notifyOrRemove(self, isAdding, isStateChanged=False, **ctx):
        if isAdding:
            return super(SkillTreePerkAvailableListener, self)._notifyOrRemove(isAdding, isStateChanged, **ctx)
        self._removeNotification(**ctx)
        return False

    def _removeNotification(self, **ctx):
        model = self._model()
        if model:
            data = self._createNotificationData(**ctx)
            notification = self._createDecorator(data)
            model.removeNotification(self._getNotificationType(), notification.getID())

    def _createNotificationData(self, priority, vehCD, nodeID, **ctx):
        gfDataID = str(uuid.uuid4())
        getCache().setPayload(gfDataID, {'vehCD': vehCD,
         'nodeID': nodeID})
        data = {'gfDataID': gfDataID}
        return NotificationData(vehCD, data, priority, None)

    def _createDecorator(self, data):
        return VehSkillTreePerkAvailableDecorator(data.entityID, data.savedData, self._model(), GFNotificationTemplates.SKILL_TREE_PERK_AVAILABLE_NOTIFICATION, data.priorityLevel)

    def __onVehicleXPUpdated(self, diff):
        self.__processVehicles(diff)

    def __tryNotify(self):
        self.__processVehicles(self.__itemsCache.items.inventory.getIventoryVehiclesCDs())

    def __processVehicles(self, vehCDs):
        currentViewVehicleCD = self.__getCurrentViewVehicleCD()
        for vehCD in vehCDs:
            self.__processVehicle(vehCD, currentViewVehicleCD == vehCD)

    def __processVehicle(self, vehCD, isCurrentViewVehicle):
        vehicle = self.__itemsCache.items.getItemByCD(vehCD)
        postProgression = vehicle.postProgression
        if postProgression.isVehSkillTree():
            isAdding = False
            nodeID = None
            priority = NotificationPriorityLevel.LOW
            if not isCurrentViewVehicle:
                cheapestPerk = getCheapestAvailablePerk(vehicle)
                recordedCheapestNodeIDs = AccountSettings.getUIFlag(VEH_SKILL_TREE_RECORDED_NOFITICATION_NODE)
                recordedCheapestNodeID = recordedCheapestNodeIDs.get(vehCD)
                if cheapestPerk is not None and cheapestPerk.getPrice().xp <= vehicle.xp and (recordedCheapestNodeID is None or recordedCheapestNodeID == cheapestPerk.stepID):
                    isAdding = True
                    nodeID = cheapestPerk.stepID
                    if recordedCheapestNodeID is None:
                        recordedCheapestNodeIDs[vehCD] = nodeID
                        AccountSettings.setUIFlag(VEH_SKILL_TREE_RECORDED_NOFITICATION_NODE, recordedCheapestNodeIDs)
                    if vehCD not in AccountSettings.getUIFlag(VEH_SKILL_TREE_POPUP_SHOWN):
                        priority = NotificationPriorityLevel.HIGH
            self._notifyOrRemove(isAdding, priority=priority, vehCD=vehCD, nodeID=nodeID)
        return

    @staticmethod
    def __getCurrentViewVehicleCD():
        appLoader = dependency.instance(IAppLoader)
        view = appLoader.getApp().containerManager.getViewByKey(ViewKey(VIEW_ALIAS.VEHICLE_HUB))
        return view.content.vehicleCtx.intCD if view is not None else None


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
 IntegratedAuctionListener,
 SeniorityAwardsStateListener,
 SeniorityAwardsQuestListener,
 SeniorityAwardsTokenListener,
 CollectionsListener,
 WinbackSelectableRewardReminder,
 BattleMattersTaskReminderListener,
 PrestigeListener,
 SeniorityAwardsVehicleSelectionListener,
 NDQSwitcherListener,
 XpTranslationRatesDiscountsListener,
 GoldExchangeRatesDiscountsListener,
 LootBoxSystemListener,
 EasyTankEquipStateListener,
 PM3NotificationListener,
 SkillTreePerkAvailableListener))

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
