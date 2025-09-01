# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/wot_plus_controller.py
import logging
import typing
from enum import Enum
import AccountCommands
import BigWorld
import constants
from BWUtil import AsyncReturn
from Event import Event
from PlayerEvents import g_playerEvents
from constants import RENEWABLE_SUBSCRIPTION_CONFIG
from gui import SystemMessages
from gui.Scaleform.daapi.view.lobby.missions.awards_formatters import CurtailingAwardsComposer
from gui.game_control.wot_plus_assistant import WotPlusAssistant
from gui.impl import backport
from gui.impl.gen import R
from gui.platform.products_fetcher.user_subscriptions.controller import SubscriptionStatus
from gui.platform.products_fetcher.user_subscriptions.user_subscription import UserSubscription, SUBSCRIPTION_CANCEL_STATUSES, SubscriptionRequestPlatform
from gui.server_events import settings
from gui.server_events.awards_formatters import AWARDS_SIZES
from gui.server_events.bonuses import GoldBank, IdleCrewXP, ExcludedMap, FreeEquipmentDemounting, WoTPlusExclusiveVehicle, AttendanceReward, SimpleBonus, WotPlusBattleBonuses, WotPlusBadges, WotPlusAdditionalBonuses, WotPlusOptionalDevicesAssistant
from gui.shared.gui_items.artefacts import OptionalDevice
from gui.shared.utils.requesters.ItemsRequester import REQ_CRITERIA
from helpers import dependency
from helpers.CallbackDelayer import CallbackDelayer
from helpers.time_utils import ONE_MINUTE
from items.vehicles import getItemByCompactDescr
from messenger.m_constants import SCH_CLIENT_MSG_TYPE
from piggy_bank_common.settings_constants import PIGGY_BANK_PDATA_KEY
from renewable_subscription_common.settings_constants import IDLE_CREW_XP_PDATA_KEY, SUBSCRIPTION_DURATION_LENGTH, IDLE_CREW_VEH_INV_ID, RS_EXPIRATION_TIME, WotPlusState
from shared_utils.account_helpers.diff_utils import synchronizeDicts
from skeletons.gui.game_control import IWotPlusController, ISteamCompletionController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.platform.product_fetch_controller import IUserSubscriptionsFetchController
from skeletons.gui.shared import IItemsCache
from skeletons.gui.system_messages import ISystemMessages
from wg_async import wg_async, wg_await
from wotdecorators import condition
if typing.TYPE_CHECKING:
    from typing import Dict, Optional, Callable, Any, List, Tuple
    from gui.shared.gui_items import ItemsCollection
    from gui.game_control.account_completion import SteamCompletionController
    from gui.server_events.bonuses import WoTPlusBonus
    from items.vehicles import VehicleType
    from gui.platform.products_fetcher.user_subscriptions.controller import UserSubscriptionsFetchController
    from gui.platform.products_fetcher.user_subscriptions.fetch_result import UserSubscriptionFetchResult
    from gui.shared.gui_items.Vehicle import Vehicle
    from renewable_subscription_common.optional_devices_usage_config import VehicleLoadout
    from Account import Account
_logger = logging.getLogger(__name__)
_SECONDS_IN_DAY = 86400

class NotificationTypeTemplate(Enum):
    PASSIVE_XP = ('PassiveXpEnabledMessage', 'PassiveXpDisabledMessage')
    GOLD_RESERVES = ('GoldReserveEnabledMessage', 'GoldReserveDisabledMessage')
    DAILY_ATTENDACES = ('DailyAttendancesEnabledMessage', 'DailyAttendancesDisabledMessage')
    FREE_DEMOUNT = ('WotPlusFreeDemountUnlockMessage', 'WotPlusFreeDemountExpireMessage')
    EXCLUDED_MAPS = ('BonusExcludedMapAvailable', 'BonusExcludedMapUnavailable')
    BATTLE_BONUSES = ('BattleBonusesEnabledMessage', 'BattleBonusesDisabledMessage')
    BADGE = ('BadgeEnabledMessage', 'BadgeDisabledMessage')
    ADDITIONAL_XP = ('AdditionalXpEnabledMessage', 'AdditionalXpDisabledMessage')
    OPTIONAL_DEVICES_ASSISTANT = ('OptionalDevicesAssistantEnabledMessage', 'OptionalDevicesAssistantDisabledMessage')
    CREW_ASSISTANT = ('CrewAssistantEnabledMessage', 'CrewAssistantDisabledMessage')

    @property
    def getEnable(self):
        return self.value[0]

    @property
    def getDisable(self):
        return self.value[1]


class WotPlusController(IWotPlusController, CallbackDelayer):
    _lobbyContext = dependency.descriptor(ILobbyContext)
    _steamCompletionCtrl = dependency.descriptor(ISteamCompletionController)
    _itemsCache = dependency.descriptor(IItemsCache)
    _systemMessages = dependency.descriptor(ISystemMessages)
    _userSubscriptionsFetchController = dependency.descriptor(IUserSubscriptionsFetchController)
    ifAccount = condition('_account')
    _SUBSCRIPTION_INVALIDATE_TIMEOUT = ONE_MINUTE * 5

    def __init__(self):
        super(WotPlusController, self).__init__()
        self._cache = {}
        self._account = None
        self._message = None
        self._state = WotPlusState.INACTIVE
        self._hasSteamSubscription = False
        self._assistant = WotPlusAssistant()
        self.onDataChanged = Event()
        self.onAttendanceUpdated = Event()
        self.onPendingRentChanged = Event()
        self.onEnabledStatusChanged = Event()
        self._invalidationInProgress = False
        return

    def init(self):
        g_playerEvents.onClientUpdated += self._onClientUpdate
        g_playerEvents.onRenewableSubscriptionStatusChanged += self._onRenewableSubscriptionStatusChanged
        self._assistant.heatCache()

    def fini(self):
        self._assistant.destroy()
        g_playerEvents.onClientUpdated -= self._onClientUpdate
        g_playerEvents.onRenewableSubscriptionStatusChanged -= self._onRenewableSubscriptionStatusChanged

    def onLobbyStarted(self, _):
        self._lobbyContext.getServerSettings().onServerSettingsChange += self._onServerSettingsChange
        self.processSwitchNotifications()

    def onAccountBecomePlayer(self):
        self._account = BigWorld.player()

    def onAccountBecomeNonPlayer(self):
        self._lobbyContext.getServerSettings().onServerSettingsChange -= self._onServerSettingsChange
        self._account = None
        self._cancelScheduledInvalidation()
        return

    def onDisconnected(self):
        self._invalidationInProgress = False
        self._assistant.clear()
        self._lobbyContext.getServerSettings().onServerSettingsChange -= self._onServerSettingsChange
        self._cache.clear()

    def selectIdleCrewXPVehicle(self, vehicleInvID, successCallback=None, errorCallback=None):

        def _onIdleCrewXPVehicleSelected(_, requestID, errorStr, errorMsg=None):
            if AccountCommands.isCodeValid(requestID):
                _logger.debug('[WotPlusController] _onIdleCrewXPVehicleSelected SUCCESS')
                if successCallback:
                    successCallback()
                return
            if requestID == AccountCommands.RES_NOT_AVAILABLE:
                self._systemMessages.pushMessage(backport.text(R.strings.messenger.serviceChannelMessages.wotPlus.passiveXP.isDisabled.title()), type=SystemMessages.SM_TYPE.Warning)
            _logger.warning((errorStr, errorMsg))
            if errorCallback:
                errorCallback()

        if vehicleInvID is None:
            vehicleInvID = -1
        self._account._doCmdInt(AccountCommands.CMD_IDLE_CREW_XP_SELECT_VEHICLE, vehicleInvID, callback=_onIdleCrewXPVehicleSelected)
        return

    def isEnabled(self):
        return self._cache.get('isEnabled', False)

    def isFreeToDemount(self, device):
        gs = self._lobbyContext.getServerSettings()
        if not gs.isFreeEquipmentDemountingEnabled():
            return False
        if device.isDeluxe and not gs.isFreeDeluxeEquipmentDemountingEnabled():
            return False
        if device.isModernized:
            if device.level > 1:
                return False
        return self.isEnabled()

    def getState(self):
        return self._state

    def hasSteamSubscription(self):
        return self._hasSteamSubscription

    def getExpiryTime(self):
        return self._cache.get(RS_EXPIRATION_TIME, 0)

    def getNextBillingTime(self):
        fetchResult = self._userSubscriptionsFetchController._fetchResult
        if fetchResult.isProductsReady:
            for subscriptionProduct in fetchResult.products:
                if subscriptionProduct.nextBillingTime and subscriptionProduct.status == SubscriptionStatus.ACTIVE:
                    return subscriptionProduct.nextBillingTime

        return None

    def getStartTime(self):
        return self.getExpiryTime() - SUBSCRIPTION_DURATION_LENGTH

    def getGoldReserve(self):
        return self._cache.get('piggyBank', {}).get('gold')

    def hasVehicleCrewIdleXP(self, vehicleInvID):
        return self._cache.get(IDLE_CREW_XP_PDATA_KEY, {}).get(IDLE_CREW_VEH_INV_ID) == vehicleInvID

    def getVehicleIDWithIdleXP(self):
        return self._cache.get(IDLE_CREW_XP_PDATA_KEY, {}).get(IDLE_CREW_VEH_INV_ID)

    def getExclusiveVehicles(self):
        return self._itemsCache.items.getVehicles(REQ_CRITERIA.VEHICLE.WOT_PLUS_VEHICLE)

    def getActiveExclusiveVehicle(self):
        vehicleInfo = self._lobbyContext.getServerSettings().getWotPlusExclusiveVehicleInfo()
        return getItemByCompactDescr(vehicleInfo['vehTypeCompDescr']) if vehicleInfo else None

    def getActiveExclusiveVehicleName(self):
        vehicle = self.getActiveExclusiveVehicle()
        return vehicle.userString if vehicle is not None else ''

    def getEnabledBonuses(self):
        serverSettings = self._lobbyContext.getServerSettings()
        mapsConfig = serverSettings.getPreferredMapsConfig()
        enabledBonuses = []
        if serverSettings.isOptionalDevicesAssistantEnabled() or serverSettings.isCrewAssistantEnabled():
            enabledBonuses.append(WotPlusOptionalDevicesAssistant())
        if serverSettings.isRenewableSubGoldReserveEnabled():
            enabledBonuses.append(GoldBank())
        if serverSettings.isRenewableSubPassiveCrewXPEnabled():
            enabledBonuses.append(IdleCrewXP())
        if serverSettings.isDailyAttendancesEnabled():
            enabledBonuses.append(AttendanceReward())
        if serverSettings.isWotPlusBattleBonusesEnabled():
            enabledBonuses.append(WotPlusBattleBonuses())
        if serverSettings.isAdditionalWoTPlusEnabled():
            enabledBonuses.append(WotPlusAdditionalBonuses())
        if serverSettings.isWoTPlusExclusiveVehicleEnabled():
            enabledBonuses.append(WoTPlusExclusiveVehicle())
        if serverSettings.isWotPlusExcludedMapEnabled():
            enabledBonuses.append(ExcludedMap(mapsConfig['wotPlusSlots']))
        if serverSettings.isFreeEquipmentDemountingEnabled():
            enabledBonuses.append(FreeEquipmentDemounting())
        if serverSettings.isBadgesEnabled():
            enabledBonuses.append(WotPlusBadges())
        return enabledBonuses

    def hasOptDeviceAssistLoadout(self, vehicle):
        return self._assistant.optDeviceAssistant.vehicleHasLoadout(vehicle) if self.isEnabled() else False

    def getOptDeviceAssistPresets(self, vehicle):
        return self._assistant.optDeviceAssistant.getPopularOptDevicesPresets(vehicle) if self.isEnabled() else tuple()

    def getMostPopularOptDevicesLoadout(self, vehicle):
        return self._assistant.optDeviceAssistant.getMostPopularLoadout(vehicle)

    def isCrewAssistEnabled(self):
        return self.isEnabled() and self._assistant.crewAssistant.isEnabled()

    def hasCrewAssistOrderSets(self, vehIntCD, tankmanRole):
        return self._assistant.crewAssistant.hasOrderSets(vehIntCD, tankmanRole) if self.isEnabled() else (False, False)

    def getCrewAssistOrderSets(self, vehicle, tankmanRole):
        return self._assistant.crewAssistant.getOrderSets(vehicle, tankmanRole) if self.isEnabled() else {}

    def validateCrewAssistOrderSets(self, orderSets):
        return self._assistant.crewAssistant.validateOrderSets(orderSets)

    @ifAccount
    def toggleWotPlusDev(self):
        self._account._doCmdInt(AccountCommands.CMD_TOGGLE_RENEWABLE_SUB_DEV, 0, self._onCmdResponseReceived)

    @ifAccount
    def giveAttendanceRewardDev(self):
        self._account._doCmdInt(AccountCommands.CMD_GIVE_ATTENDANCE_REWARD_DEV, 0, self._onCmdResponseReceived)

    def setWotPlusStateDev(self, state):
        self._state = WotPlusState(state)
        self._userSubscriptionsFetchController.reset()
        self.onEnabledStatusChanged(self.isEnabled())
        self.onDataChanged(self._cache)

    @ifAccount
    def activateWotPlusDev(self, expirySecondsInFuture=_SECONDS_IN_DAY):
        self._account._doCmdInt(AccountCommands.CMD_ACTIVATE_RENEWABLE_SUB_DEV, expirySecondsInFuture, self._onCmdResponseReceived)

    def simulateNewGameDay(self):
        self._account._doCmdInt(AccountCommands.CMD_WOT_PLUS_NEW_GAME_DAY, 0, self._onCmdResponseReceived)

    @ifAccount
    def setReservesDev(self, creditsVal, goldVal):
        self._account._doCmdInt2(AccountCommands.CMD_SET_RESERVES_PIGGY_BANK_DEV, creditsVal, goldVal, self._onCmdResponseReceived)

    @ifAccount
    def smashPiggyBankDev(self):
        self._account._doCmdInt(AccountCommands.CMD_SMASH_PIGGY_BANK_DEV, 6, self._onCmdResponseReceived)

    def isWotPlusEnabled(self):
        isWotPlusEnabled = self._lobbyContext.getServerSettings().isRenewableSubEnabled()
        if not isWotPlusEnabled:
            return False
        playerHasActiveWotPlus = self.isEnabled()
        if playerHasActiveWotPlus:
            return True
        isWotPlusEnabledForSteam = self._lobbyContext.getServerSettings().isWotPlusEnabledForSteam()
        isSteamAccount = self._steamCompletionCtrl.isSteamAccount
        return False if not isWotPlusEnabledForSteam and isSteamAccount else True

    def onDailyAttendanceUpdate(self):
        with settings.wotPlusSettings() as dt:
            dt.increaseDailyAttendance()
        self.onAttendanceUpdated()

    def isDailyAttendanceQuest(self, questID):
        dailyAttendancePrefix = self._lobbyContext.getServerSettings().getDailyAttendanceQuestPrefix()
        return questID.startswith(dailyAttendancePrefix)

    def getFormattedDailyAttendanceBonuses(self, bonuses):
        composer = CurtailingAwardsComposer(displayedAwardsCount=constants.WoTPlusDailyAttendance.MAXIMUM_DISPLAYED_REWARDS)
        return composer.getFormattedBonuses(bonuses, AWARDS_SIZES.BIG)

    def processSwitchNotifications(self):
        serverSettings = self._lobbyContext.getServerSettings()
        isWotPlusEnabled = self.isWotPlusEnabled()
        isGoldReserveEnabled = serverSettings.isRenewableSubGoldReserveEnabled()
        isPassiveXpEnabled = serverSettings.isRenewableSubPassiveCrewXPEnabled()
        isFreeDemountingEnabled = serverSettings.isFreeEquipmentDemountingEnabled()
        isExcludedMapEnabled = serverSettings.isWotPlusExcludedMapEnabled()
        isDailyAttendancesEnabled = serverSettings.isDailyAttendancesEnabled()
        isBattleBonusesEnabled = serverSettings.isWotPlusBattleBonusesEnabled()
        isBadgesEnabled = serverSettings.isBadgesEnabled()
        isAdditionalXPEnabled = serverSettings.isAdditionalWoTPlusEnabled()
        isOptionalDevicesAssistantEnabled = serverSettings.isOptionalDevicesAssistantEnabled()
        isCrewAssistantEnabled = serverSettings.isCrewAssistantEnabled()
        with settings.wotPlusSettings() as dt:
            dt.setWotPlusEnabledState(isWotPlusEnabled)
            hasSubscription = self.isEnabled()
            if not isWotPlusEnabled and not hasSubscription:
                return
            if hasSubscription and not dt.isFirstTime:
                if not isWotPlusEnabled:
                    self._systemMessages.proto.serviceChannel.pushClientMessage({}, SCH_CLIENT_MSG_TYPE.WOTPLUS_FEATURE_DISABLED)
                else:
                    self._notifyClient(dt.isGoldReserveEnabled, isGoldReserveEnabled, NotificationTypeTemplate.GOLD_RESERVES)
                    self._notifyClient(dt.isPassiveXpEnabled, isPassiveXpEnabled, NotificationTypeTemplate.PASSIVE_XP)
                    self._notifyClient(dt.isFreeDemountingEnabled, isFreeDemountingEnabled, NotificationTypeTemplate.FREE_DEMOUNT)
                    self._notifyClient(dt.isExcludedMapEnabled, isExcludedMapEnabled, NotificationTypeTemplate.EXCLUDED_MAPS)
                    self._notifyClient(dt.isDailyAttendancesEnabled, isDailyAttendancesEnabled, NotificationTypeTemplate.DAILY_ATTENDACES)
                    self._notifyClient(dt.isBattleBonusesEnabled, isBattleBonusesEnabled, NotificationTypeTemplate.BATTLE_BONUSES)
                    self._notifyClient(dt.isBadgesEnabled, isBadgesEnabled, NotificationTypeTemplate.BADGE)
                    self._notifyClient(dt.isAdditionalXPEnabled, isAdditionalXPEnabled, NotificationTypeTemplate.ADDITIONAL_XP)
                    self._notifyClient(dt.isOptionalDevicesAssistantEnabled, isOptionalDevicesAssistantEnabled, NotificationTypeTemplate.OPTIONAL_DEVICES_ASSISTANT)
                    self._notifyClient(dt.isCrewAssistantEnabled, isCrewAssistantEnabled, NotificationTypeTemplate.CREW_ASSISTANT)
            dt.setIsFirstTime(not hasSubscription)
            dt.setGoldReserveEnabledState(isGoldReserveEnabled)
            dt.setPassiveXpState(isPassiveXpEnabled)
            dt.setFreeDemountingState(isFreeDemountingEnabled)
            dt.setExcludedMapState(isExcludedMapEnabled)
            dt.setDailyAttendancesState(isDailyAttendancesEnabled)
            dt.setBattleBonusesState(isBattleBonusesEnabled)
            dt.setBadgesEnabled(isBadgesEnabled)
            dt.setAdditionalXPEnabled(isAdditionalXPEnabled)
            dt.setOptionalDevicesAssistantEnabled(isOptionalDevicesAssistantEnabled)
            dt.setCrewAssistantEnabled(isCrewAssistantEnabled)

    def _notifyClient(self, lastSeenStatus, currentStatus, notifications):
        if lastSeenStatus != currentStatus:
            notification = notifications.getEnable if currentStatus else notifications.getDisable
            self._systemMessages.proto.serviceChannel.pushClientMessage(notification, SCH_CLIENT_MSG_TYPE.WOTPLUS_SWITCH)

    @wg_async
    def _resolveSubscriptionAndSteamState(self, clearCache=False):
        if self._invalidationInProgress:
            _logger.debug('Wot plus is waiting for another subscription invalidation, skipping')
            return
        else:
            self._invalidationInProgress = True
            self._state = WotPlusState.ACTIVE if self.isEnabled() else WotPlusState.INACTIVE
            self._hasSteamSubscription = False
            if constants.IS_CHINA or constants.IS_CT:
                _logger.warning('Subscriptions are not available for the current realm: %s', constants.CURRENT_REALM)
                return
            if not self.isEnabled():
                return
            fetchResult = yield wg_await(self._userSubscriptionsFetchController.getSubscriptions(clearCache))
            userSubscriptions = fetchResult.products
            if not fetchResult.isProductsReady:
                return
            activeSubscriptions = [ subscription for subscription in userSubscriptions if subscription.status == SubscriptionStatus.ACTIVE ]
            if not activeSubscriptions:
                hasCancelled = any((subscription.status in SUBSCRIPTION_CANCEL_STATUSES for subscription in userSubscriptions))
                if hasCancelled:
                    self._state = WotPlusState.CANCELLED
            self._hasSteamSubscription = any((userSubscription.platform == SubscriptionRequestPlatform.STEAM for userSubscription in userSubscriptions))
            raise AsyncReturn(None)
            return

    def shouldRedirectToSteam(self):
        return self._steamCompletionCtrl.isSteamAccount if not self._userSubscriptionsFetchController._fetchResult.isProductsReady else self.hasSteamSubscription()

    def _onClientUpdate(self, diff, _):
        itemDiff = {}
        if IDLE_CREW_XP_PDATA_KEY in diff:
            itemDiff[IDLE_CREW_XP_PDATA_KEY] = diff[IDLE_CREW_XP_PDATA_KEY]
        if PIGGY_BANK_PDATA_KEY in diff:
            itemDiff[PIGGY_BANK_PDATA_KEY] = diff[PIGGY_BANK_PDATA_KEY]
        if itemDiff:
            synchronizeDicts(itemDiff, self._cache)
            self.onDataChanged(itemDiff)

    def _onServerSettingsChange(self, diff):
        if RENEWABLE_SUBSCRIPTION_CONFIG in diff:
            self.processSwitchNotifications()

    def _onCmdResponseReceived(self, resultID, requestID, errorStr, errorMsg=None):
        if not AccountCommands.isCodeValid(requestID):
            _logger.error('Received invalid response: resultId: %s, requestId: %s, error: %s, message: %s', resultID, requestID, errorStr, errorMsg)

    def _onRenewableSubscriptionStatusChanged(self):
        previousState = self.isEnabled()
        synchronizeDicts(self._account.renewableSubscription, self._cache)
        _logger.debug('Renewable subscription state updated, cache is synchronized = %s', self._cache)
        currentState = self.isEnabled()
        stateChanged = previousState != currentState
        _logger.debug('Renewable subscription state is changed, prev = %s, current = %s', previousState, currentState)
        self._invalidateSubscriptionState(stateChanged)

    def _scheduleInvalidation(self):
        _logger.debug('Scheduling subscription invalidation for %s seconds', self._SUBSCRIPTION_INVALIDATE_TIMEOUT)
        self.delayCallback(self._SUBSCRIPTION_INVALIDATE_TIMEOUT, self._invalidateSubscriptionState)

    def _cancelScheduledInvalidation(self):
        _logger.debug('Canceling scheduled subscription invalidation')
        self.stopCallback(self._invalidateSubscriptionState)

    def _invalidateSubscriptionState(self, stateChanged=False):
        _logger.debug('Invalidating subscription')
        if self._invalidationInProgress:
            return
        try:
            self._resolveSubscriptionAndSteamState(clearCache=True)
        finally:
            self._invalidationInProgress = False

        self.onDataChanged(self._cache)
        if stateChanged:
            self._refreshAssistance()
            self.onEnabledStatusChanged(self.isEnabled())
        self._scheduleInvalidation()

    def _refreshAssistance(self):
        if self.isEnabled():
            self._assistant.start()
            self._assistant.subscriptionValidated()
        else:
            self._assistant.clearWithCacheDelete()
