# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/wot_plus_controller.py
from __future__ import absolute_import
import logging
from time import time
import typing
from enum import Enum
import AccountCommands
import BigWorld
import constants
from BWUtil import AsyncReturn
from CurrentVehicle import g_currentVehicle
from Event import Event
from PlayerEvents import g_playerEvents
from constants import RENEWABLE_SUBSCRIPTION_ENTITLEMENTS
from debug_utils import LOG_ERROR_DEV
from gui import SystemMessages
from gui.Scaleform.daapi.view.lobby.missions.awards_formatters import CurtailingAwardsComposer
from gui.game_control.wot_plus.service_record_customization.service_record_customization import ServiceRecordAssetManager
from gui.game_control.wot_plus.wot_plus_assistant import WotPlusAssistant
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.page.header.wot_plus_subscription_model import WotPlusPeriodicityEnum
from gui.platform.products_fetcher.user_subscriptions.controller import SubscriptionStatus
from gui.platform.products_fetcher.user_subscriptions.user_subscription import UserSubscription, SUBSCRIPTION_CANCEL_STATUSES, SubscriptionRequestPlatform
from gui.server_events import settings
from gui.server_events.awards_formatters import AWARDS_SIZES
from gui.server_events.bonuses import SimpleBonus
from gui.shared.gui_items.artefacts import OptionalDevice
from gui.shared.utils.requesters.ItemsRequester import REQ_CRITERIA
from helpers import dependency
from helpers.CallbackDelayer import CallbackDelayer
from helpers.time_utils import ONE_MINUTE, ONE_DAY
from messenger.m_constants import SCH_CLIENT_MSG_TYPE
from piggy_bank_common.settings_constants import PIGGY_BANK_PDATA_KEY
from renewable_subscription_common.schema import renewableSubscriptionsConfigSchema
from renewable_subscription_common.settings_constants import IDLE_CREW_XP_PDATA_KEY, SUBSCRIPTION_DURATION_LENGTH, IDLE_CREW_VEH_INV_ID, RS_EXPIRATION_TIME, WotPlusState, RS_TIER, PRO_BOOST_PDATA_KEY, WotPlusTier, RS_SR_BACKGROUND, RS_SR_RIBBON, PRO_BOOST_ACTIVATION_TIME, PRO_BOOSTED_VEHICLE
from renewable_subscription_common.settings_helpers import SubscriptionSettingsStorage
from shared_utils import findFirst
from shared_utils.account_helpers.diff_utils import synchronizeDicts
from skeletons.gui.game_control import IWotPlusController, ISteamCompletionController
from skeletons.gui.platform.product_fetch_controller import IUserSubscriptionsFetchController
from skeletons.gui.shared import IItemsCache
from skeletons.gui.system_messages import ISystemMessages
from wg_async import wg_async, wg_await
from wotdecorators import condition
if typing.TYPE_CHECKING:
    from typing import Dict, Optional, Callable, Any, List, Tuple, Generator
    from gui.shared.gui_items import ItemsCollection
    from gui.game_control.account_completion import SteamCompletionController
    from gui.platform.products_fetcher.user_subscriptions.controller import UserSubscriptionsFetchController
    from gui.platform.products_fetcher.user_subscriptions.fetch_result import UserSubscriptionFetchResult
    from gui.shared.gui_items.Vehicle import Vehicle
    from renewable_subscription_common.optional_devices_usage_config import VehicleLoadout
    from Account import Account
_logger = logging.getLogger(__name__)

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
    SERVICE_RECORD = ('ServiceRecordCustomizationEnabledMessage', 'ServiceRecordCustomizationDisabledMessage')
    PRO_BOOST = ('WotPlusProBoostEnabledMessage', 'WotPlusProBoostDisabledMessage')
    BATTLE_PASS = ('WotPlusBattlePassEnabledMessage', 'WotPlusBattlePassDisabledMessage')

    @property
    def getEnable(self):
        return self.value[0]

    @property
    def getDisable(self):
        return self.value[1]


class _ProBoostMixin(object):
    ifAccount = condition('_account')

    def __init__(self):
        super(_ProBoostMixin, self).__init__()
        self._delay = CallbackDelayer()
        self.onProBoostCooldownIsFinished = Event()

    def startProBoostTimer(self, remainingTime):
        self._delay.delayCallback(remainingTime, self._callOnCooldownIsFinishedEvent)

    def stopProBoostTimer(self):
        self._delay.stopCallback(self._callOnCooldownIsFinishedEvent)

    def isProBoostTimerRunning(self):
        return self._delay.hasDelayedCallback(self._callOnCooldownIsFinishedEvent)

    def _callOnCooldownIsFinishedEvent(self):
        self.onProBoostCooldownIsFinished()


class WotPlusController(IWotPlusController, _ProBoostMixin, CallbackDelayer):
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
        self._state = WotPlusState.INACTIVE
        self._billingPeriod = None
        self._hasSteamSubscription = False
        self._assistant = WotPlusAssistant()
        self._srcAssetManager = ServiceRecordAssetManager()
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
        self.stopProBoostTimer()
        if self._srcAssetManager is not None:
            self._srcAssetManager.clear()
            self._srcAssetManager = None
        return

    def onLobbyStarted(self, _):
        g_playerEvents.onConfigModelUpdated += self._onConfigModelUpdated
        self.processSwitchNotifications()
        self._invalidateProBoost()
        if self._srcAssetManager is not None:
            self._srcAssetManager.init()
        return

    def onAccountBecomePlayer(self):
        self._account = BigWorld.player()

    def onAccountBecomeNonPlayer(self):
        g_playerEvents.onConfigModelUpdated -= self._onConfigModelUpdated
        self._account = None
        self._cancelScheduledInvalidation()
        self.stopProBoostTimer()
        return

    def _invalidateProBoost(self):
        if PRO_BOOST_PDATA_KEY not in self._cache:
            return
        storage = self.getSettingsStorage()
        if not storage.isProBoostFeatureEnabled() or not storage.isProBoostFeatureAvailable():
            self.stopProBoostTimer()
            return
        proBoostActivationTime = self.getProBoostActivationTime()
        proBoostCooldown = storage.getProBoostCooldown()
        remainingTime = proBoostActivationTime + proBoostCooldown - int(time())
        if remainingTime <= 0:
            self.stopProBoostTimer()
            return
        self.startProBoostTimer(remainingTime)

    def onDisconnected(self):
        self._invalidationInProgress = False
        self._assistant.clear()
        g_playerEvents.onConfigModelUpdated -= self._onConfigModelUpdated
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

    def activateProBoostOnVehicle(self, vehicleInvID=-1, successCallback=None, errorCallback=None):

        def _onProBoostVehicleSelected(_, requestID, errorStr, errorMsg=None):
            if AccountCommands.isCodeValid(requestID):
                _logger.debug('[WotPlusController] _onProBoostVehicleSelected SUCCESS')
                if successCallback:
                    successCallback()
                return
            _logger.warning((errorStr, errorMsg))
            if errorCallback:
                errorCallback()

        subscriptionStorage = self.getSettingsStorage()
        if not subscriptionStorage.isProBoostFeatureEnabled() or not subscriptionStorage.isProBoostFeatureAvailable():
            return
        else:
            vehicle = self._itemsCache.items.getVehicle(vehicleInvID)
            if not vehicle.isInInventory:
                return
            vehicleCD = vehicle.intCD
            if not self.canBeProBoosted(vehicleCD):
                return
            if self.isProBoostTimerRunning():
                return
            self._account._doCmdInt(AccountCommands.CMD_WOT_PLUS_ACTIVATE_PRO_BOOST, vehicleInvID, callback=_onProBoostVehicleSelected)
            return

    def hasSubscription(self):
        return self.getTier() != WotPlusTier.NONE

    def getTier(self):
        return self._cache.get(RS_TIER, WotPlusTier.NONE)

    def getBillingPeriod(self):
        return self._billingPeriod

    def getProBoostedVehicleInvID(self):
        return self._cache.get(PRO_BOOST_PDATA_KEY, {}).get(PRO_BOOSTED_VEHICLE, 0)

    def getProBoostActivationTime(self):
        return self._cache.get(PRO_BOOST_PDATA_KEY, {}).get(PRO_BOOST_ACTIVATION_TIME, 0)

    def isFreeToDemount(self, device):
        settingsStorage = self.getSettingsStorage()
        if not settingsStorage.isFreeEquipmentDemountingAvailable():
            return False
        if device.isDeluxe and not settingsStorage.isFreeDeluxeEquipmentDemountingAvailable():
            return False
        if device.isModernized:
            if device.level > 1:
                return False
        return self.hasSubscription()

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

    def hasOptDeviceAssistLoadout(self, vehicle):
        return self._assistant.optDeviceAssistant.vehicleHasLoadout(vehicle) if self.hasSubscription() else False

    def getOptDeviceAssistPresets(self, vehicle):
        return self._assistant.optDeviceAssistant.getPopularOptDevicesPresets(vehicle) if self.hasSubscription() else tuple()

    def getMostPopularOptDevicesLoadout(self, vehicle):
        return self._assistant.optDeviceAssistant.getMostPopularLoadout(vehicle)

    def isCrewAssistEnabled(self):
        return self.hasSubscription() and self._assistant.crewAssistant.isEnabled()

    def hasCrewAssistOrderSets(self, vehIntCD, tankmanRole):
        return self._assistant.crewAssistant.hasOrderSets(vehIntCD, tankmanRole) if self.hasSubscription() else (False, False)

    def getCrewAssistOrderSets(self, vehIntCD, tankmanRole):
        return self._assistant.crewAssistant.getOrderSets(vehIntCD, tankmanRole) if self.hasSubscription() else {}

    def validateCrewAssistOrderSets(self, orderSets):
        return self._assistant.crewAssistant.validateOrderSets(orderSets)

    def getServiceRecordBackgroundID(self):
        return self._cache.get(RS_SR_BACKGROUND, 0) if self.getSettingsStorage().isServiceRecordCustomizationAvailable() else 0

    def getServiceRecordRibbonID(self):
        return self._cache.get(RS_SR_RIBBON, 0) if self.getSettingsStorage().isServiceRecordCustomizationAvailable() else 0

    def getSRCAssetManager(self):
        return self._srcAssetManager

    @ifAccount
    def toggleWotPlusDev(self, tier=WotPlusTier.CORE):
        availableTiers = (WotPlusTier.CORE, WotPlusTier.PRO)
        if tier not in availableTiers and not self.hasSubscription():
            LOG_ERROR_DEV('The selected tier is not supported. The supported tiers are ', availableTiers)
            return
        self._account._doCmdInt(AccountCommands.CMD_TOGGLE_RENEWABLE_SUB_DEV, tier, self._onCmdResponseReceived)

    @ifAccount
    def giveAttendanceRewardDev(self):
        self._account._doCmdInt(AccountCommands.CMD_GIVE_ATTENDANCE_REWARD_DEV, 0, self._onCmdResponseReceived)

    @ifAccount
    def activateProBoostOnCurrentVehicleDev(self):
        self._account._doCmdInt(AccountCommands.CMD_WOT_PLUS_ACTIVATE_PRO_BOOST_DEV, g_currentVehicle.invID, self._onCmdResponseReceived)

    @ifAccount
    def refreshProBoostCooldownDev(self):
        self._account._doCmdNoArgs(AccountCommands.CMD_WOT_PLUS_REFRESH_PRO_BOOST_COOLDOWN_DEV, self._onCmdResponseReceived)
        self.stopProBoostTimer()

    def setWotPlusStateDev(self, state):
        self._state = WotPlusState(state)
        self._userSubscriptionsFetchController.reset()
        self.onEnabledStatusChanged(self.hasSubscription())
        self.onDataChanged(self._cache)

    @ifAccount
    def simulateWGMoneyBalanceUpdate(self):
        self._account._doCmdNoArgs(AccountCommands.CMD_WOT_PLUS_SIMULATE_WG_MONEY_UPDATE, self._onCmdResponseReceived)

    @ifAccount
    def activateWotPlusDev(self, expirySecondsInFuture=ONE_DAY, entitlementName=RENEWABLE_SUBSCRIPTION_ENTITLEMENTS.CORE):
        self._account._doCmdIntStr(AccountCommands.CMD_ACTIVATE_RENEWABLE_SUB_DEV, expirySecondsInFuture, entitlementName, self._onCmdResponseReceived)

    def simulateNewGameDay(self):
        self._account._doCmdInt(AccountCommands.CMD_WOT_PLUS_NEW_GAME_DAY, 0, self._onCmdResponseReceived)

    @ifAccount
    def setReservesDev(self, creditsVal, goldVal):
        self._account._doCmdInt2(AccountCommands.CMD_SET_RESERVES_PIGGY_BANK_DEV, creditsVal, goldVal, self._onCmdResponseReceived)

    @ifAccount
    def smashPiggyBankDev(self):
        self._account._doCmdInt(AccountCommands.CMD_SMASH_PIGGY_BANK_DEV, 6, self._onCmdResponseReceived)

    def isWotPlusVisible(self):
        settingsStorage = self.getSettingsStorage()
        if not settingsStorage.isRenewableSubscriptionEnabled():
            return False
        playerHasActiveWotPlus = self.hasSubscription()
        if playerHasActiveWotPlus:
            return True
        return settingsStorage.isEnabledForSteam() if self._steamCompletionCtrl.isSteamAccount else True

    def onDailyAttendanceUpdate(self):
        with settings.wotPlusSettings() as dt:
            dt.increaseDailyAttendance()
        self.onAttendanceUpdated()

    def isDailyAttendanceQuest(self, questID):
        dailyAttendancePrefix = self.getSettingsStorage().getDailyAttendanceQuestPrefix()
        return False if dailyAttendancePrefix is None else questID.startswith(dailyAttendancePrefix)

    def getFormattedDailyAttendanceBonuses(self, bonuses):
        composer = CurtailingAwardsComposer(displayedAwardsCount=constants.WoTPlusDailyAttendance.MAXIMUM_DISPLAYED_REWARDS)
        return composer.getFormattedBonuses(bonuses, AWARDS_SIZES.BIG)

    def processSwitchNotifications(self):
        isWotPlusEnabled = self.isWotPlusVisible()
        settingsModel = self.getSettingsStorage()
        isGoldReserveEnabled = settingsModel.isGoldReserveFeatureEnabled()
        isPassiveXpEnabled = settingsModel.isPassiveCrewXPEnabled()
        isFreeDemountingEnabled = settingsModel.isFreeEquipmentDemountingEnabled()
        isExcludedMapEnabled = settingsModel.isExcludedMapFeatureEnabled()
        isDailyAttendancesEnabled = settingsModel.isDailyAttendanceFeatureEnabled()
        isBattleBonusesEnabled = settingsModel.isBattleBonusesEnabled()
        isBadgesEnabled = settingsModel.isBadgesEnabled()
        isAdditionalXPEnabled = settingsModel.isAdditionalXPBonusEnabled()
        isOptionalDevicesAssistantEnabled = settingsModel.isOptionalDevicesAssistantEnabled()
        isCrewAssistantEnabled = settingsModel.isCrewAssistantEnabled()
        isServiceRecordCustomizationEnabled = settingsModel.isServiceRecordCustomizationEnabled()
        isProBoostEnabled = settingsModel.isProBoostFeatureEnabled()
        isBattlePassEnabled = settingsModel.isBattlePassFeatureEnabled()
        with settings.wotPlusSettings() as dt:
            dt.setWotPlusEnabledState(isWotPlusEnabled)
            hasSubscription = self.hasSubscription()
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
                    self._notifyClient(dt.isServiceRecordCustomizationEnabled, isServiceRecordCustomizationEnabled, NotificationTypeTemplate.SERVICE_RECORD)
                    self._notifyClient(dt.isProBoostEnabled, isProBoostEnabled, NotificationTypeTemplate.PRO_BOOST)
                    self._notifyClient(dt.isBattlePassEnabled, isBattlePassEnabled, NotificationTypeTemplate.BATTLE_PASS)
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
            dt.setServiceRecordCustomizationEnabled(isServiceRecordCustomizationEnabled)
            dt.setProBoostEnabled(isProBoostEnabled)
            dt.setBattlePassEnabled(isBattlePassEnabled)

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
            self._hasSteamSubscription = False
            self._billingPeriod = None
            if constants.IS_CHINA or constants.IS_CT:
                _logger.warning('Subscriptions are not available for the current realm: %s', constants.CURRENT_REALM)
                return
            if not self.hasSubscription():
                return
            fetchResult = yield wg_await(self._userSubscriptionsFetchController.getSubscriptions(clearCache))
            userSubscriptions = fetchResult.products
            if not fetchResult.isProductsReady:
                return
            activeSubscriptions = [ subscription for subscription in userSubscriptions if subscription.status == SubscriptionStatus.ACTIVE ]
            subWithBilling = findFirst(lambda subscription: subscription.billingPeriod, activeSubscriptions)
            if subWithBilling is not None:
                self._billingPeriod = subWithBilling.billingPeriod
            if not activeSubscriptions:
                cancelledSubs = (s for s in userSubscriptions if s.status in SUBSCRIPTION_CANCEL_STATUSES)
                if cancelledSubs:
                    cancelledSub = max(cancelledSubs, key=lambda s: s.nextBillingTime)
                    self._billingPeriod = cancelledSub.billingPeriod
                    self._state = WotPlusState.CANCELLED
            self._hasSteamSubscription = any((userSubscription.platform == SubscriptionRequestPlatform.STEAM for userSubscription in userSubscriptions))
            raise AsyncReturn(None)
            return

    def shouldRedirectToSteam(self):
        return self._steamCompletionCtrl.isSteamAccount if not self._userSubscriptionsFetchController._fetchResult.isProductsReady else self.hasSteamSubscription()

    def getSettingsStorage(self):
        return SubscriptionSettingsStorage(tierID=self._cache.get(RS_TIER, WotPlusTier.NONE))

    def canBeProBoosted(self, vehicleCD):
        if vehicleCD is None:
            return False
        else:
            subscriptionStorage = self.getSettingsStorage()
            return subscriptionStorage.isVehicleProBoostCompatible(vehicleCD) and not subscriptionStorage.hasVehicleProBoostExcludedTags(vehicleCD)

    def _onClientUpdate(self, diff, _):
        itemDiff = {}
        if IDLE_CREW_XP_PDATA_KEY in diff:
            itemDiff[IDLE_CREW_XP_PDATA_KEY] = diff[IDLE_CREW_XP_PDATA_KEY]
        if PIGGY_BANK_PDATA_KEY in diff:
            itemDiff[PIGGY_BANK_PDATA_KEY] = diff[PIGGY_BANK_PDATA_KEY]
        if PRO_BOOST_PDATA_KEY in diff:
            itemDiff[PRO_BOOST_PDATA_KEY] = diff[PRO_BOOST_PDATA_KEY]
        if itemDiff:
            synchronizeDicts(itemDiff, self._cache)
            self.onDataChanged(itemDiff)

    def _onCmdResponseReceived(self, resultID, requestID, errorStr, errorMsg=None):
        if not AccountCommands.isCodeValid(requestID):
            _logger.error('Received invalid response: resultId: %s, requestId: %s, error: %s, message: %s', resultID, requestID, errorStr, errorMsg)

    def _onRenewableSubscriptionStatusChanged(self):
        previousState = self.hasSubscription()
        synchronizeDicts(self._account.renewableSubscription, self._cache)
        _logger.debug('Renewable subscription state updated, cache is synchronized = %s', self._cache)
        currentState = self.hasSubscription()
        stateChanged = previousState != currentState
        _logger.debug('Renewable subscription state is changed, prev = %s, current = %s', previousState, currentState)
        self._invalidateSubscriptionState(stateChanged)

    def _scheduleInvalidation(self):
        _logger.debug('Scheduling subscription invalidation for %s seconds', self._SUBSCRIPTION_INVALIDATE_TIMEOUT)
        self.delayCallback(self._SUBSCRIPTION_INVALIDATE_TIMEOUT, self._invalidateCallback)

    def _cancelScheduledInvalidation(self):
        _logger.debug('Canceling scheduled subscription invalidation')
        self.stopCallback(self._invalidateCallback)

    @wg_async
    def _invalidateSubscriptionState(self, stateChanged=False):
        _logger.debug('Invalidating subscription')
        self._state = WotPlusState.ACTIVE if self.hasSubscription() else WotPlusState.INACTIVE
        try:
            yield wg_await(self._resolveSubscriptionAndSteamState(clearCache=True))
        finally:
            self._invalidationInProgress = False

        self.onDataChanged(self._cache)
        if stateChanged:
            self._refreshAssistance()
            self._invalidateProBoost()
            self.onEnabledStatusChanged(self.hasSubscription())
        self._scheduleInvalidation()

    def _invalidateCallback(self):
        self._invalidateSubscriptionState()

    def _refreshAssistance(self):
        if self.hasSubscription():
            self._assistant.start()
            self._assistant.subscriptionValidated()
        else:
            self._assistant.clearWithCacheDelete()

    def _onConfigModelUpdated(self, gpKey):
        if renewableSubscriptionsConfigSchema.gpKey == gpKey:
            self._invalidateProBoost()
            self.processSwitchNotifications()
