# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/wot_plus/utils.py
from collections import defaultdict
import typing
from arena_bonus_type_caps import ARENA_BONUS_TYPE_CAPS as BONUS_CAPS
from constants import ARENA_BONUS_TYPE
from constants import QUEUE_TYPE, ARENA_BONUS_TYPE_TO_QUEUE_TYPE
from gui.impl.gen.view_models.views.lobby.battle_results.additional_bonus_model import WotPlusTypeEnum
from gui.prb_control.settings import PREBATTLE_TYPE_TO_QUEUE_TYPE
from gui.server_events import bonuses as wotp_b
from helpers import dependency
from renewable_subscription_common.schema import Features
from renewable_subscription_common.settings_constants import WotPlusTier
from renewable_subscription_common.settings_helpers import SubscriptionSettingsStorage
from skeletons.gui.game_control import IWotPlusController, IHangarGuiController, ISteamCompletionController
if typing.TYPE_CHECKING:
    from constants import PREBATTLE_TYPE
    from gui.server_events.bonuses import WoTPlusBonus
    from typing import Optional
WOT_PLUS_TIER_MAP = {WotPlusTier.NONE: WotPlusTypeEnum.NONE,
 WotPlusTier.CORE: WotPlusTypeEnum.CORE,
 WotPlusTier.PRO: WotPlusTypeEnum.PRO}

def _baseArgsProvider(storage):
    return tuple()


_FEATURE_TO_BONUS_ORDER_LIST = ((Features.GOLD_RESERVE, wotp_b.GoldBank, _baseArgsProvider),
 (Features.PASSIVE_CREW_XP, wotp_b.IdleCrewXP, _baseArgsProvider),
 (Features.BATTLE_BONUSES, wotp_b.WotPlusBattleBonuses, _baseArgsProvider),
 (Features.ADDITIONAL_XP, wotp_b.WotPlusAdditionalBonuses, _baseArgsProvider),
 (Features.FREE_EQUIPMENT_DEMOUNTING, wotp_b.FreeEquipmentDemounting, _baseArgsProvider),
 (Features.EXCLUDED_MAP, wotp_b.ExcludedMap, lambda storage: (storage.getExcludedMapsCount(),)),
 (Features.OPTIONAL_DEVICES_ASSISTANT, wotp_b.WotPlusOptionalDevicesAssistant, _baseArgsProvider),
 (Features.CREW_ASSISTANT, wotp_b.WotPlusOptionalDevicesAssistant, _baseArgsProvider),
 (Features.EXCLUSIVE_VEHICLE, wotp_b.WoTPlusExclusiveVehicle, _baseArgsProvider),
 (Features.DAILY_ATTENDANCE, wotp_b.AttendanceReward, _baseArgsProvider),
 (Features.BADGES, wotp_b.WotPlusBadges, _baseArgsProvider),
 (Features.PRO_BOOST, wotp_b.WotPlusProBoostBonus, _baseArgsProvider),
 (Features.SERVICE_RECORD_CUSTOMIZATION, wotp_b.WotPlusServiceCustomizationBonus, _baseArgsProvider),
 (Features.BATTLE_PASS, wotp_b.WotPlusProBattlePass, _baseArgsProvider))

def _updateList(bonusList, bunusClass, bonusArguments):
    incomingBonus = bunusClass(*bonusArguments)
    for i, existedBonus in enumerate(bonusList):
        if isinstance(existedBonus, bunusClass):
            if incomingBonus.isBetterThan(existedBonus):
                bonusList[i] = incomingBonus
            return

    bonusList.append(incomingBonus)


def _updateBonusList(bonusList, featureIDList, storage):
    for fID, bonusClass, argsProvider in _FEATURE_TO_BONUS_ORDER_LIST:
        if fID in featureIDList:
            _updateList(bonusList, bonusClass, argsProvider(storage))


def _getAvailableBonusesForTier(storage, tierID):
    bonuses = []
    _updateBonusList(bonuses, storage.getTierAvailableFeatures(tierID), storage)
    return bonuses


def getAvailableCoreBonuses(storage):
    return _getAvailableBonusesForTier(storage, WotPlusTier.CORE)


def getAvailableProBonuses(storage):
    return _getAvailableBonusesForTier(storage, WotPlusTier.PRO)


def getUniqueAvailableProBonuses(storage):
    bonuses = []
    _updateBonusList(bonuses, storage.getTierAvailableFeatures(WotPlusTier.PRO).difference(storage.getTierAvailableFeatures(WotPlusTier.CORE)), storage)
    return bonuses


def getSubscriptionAvailableBonuses(storage):
    bonuses = getAvailableCoreBonuses(storage)
    _updateBonusList(bonuses, storage.getTierAvailableFeatures(WotPlusTier.PRO), storage)
    return bonuses


@dependency.replace_none_kwargs(wotPlusController=IWotPlusController)
def getExcludedMapsPromoData(wotPlusController=None):
    storage = wotPlusController.getSettingsStorage()
    if not storage.isRenewableSubscriptionEnabled():
        return (False, 0)
    maxCount = 0
    if storage.isExcludedMapFeatureEnabled():
        for _, tierSettings in storage.reverseIterTiers():
            excludedMapFeature = tierSettings.excludedMapFeature
            if excludedMapFeature.available:
                maxCount = max(maxCount, excludedMapFeature.count)

    return (wotPlusController.hasSubscription(), maxCount)


@dependency.replace_none_kwargs(wotPlusController=IWotPlusController)
def getAdditionalXPPromoData(wotPlusController=None):
    storage = wotPlusController.getSettingsStorage()
    maxCount = 0
    if storage.isAdditionalXPBonusEnabled():
        for _, tierSettings in storage.reverseIterTiers():
            additionalXPFeature = tierSettings.additionalXPBonusFeature
            if additionalXPFeature.available:
                maxCount = max(maxCount, additionalXPFeature.applyCount)

    return maxCount


@dependency.replace_none_kwargs(wotPlusController=IWotPlusController)
def hasFreeDeluxeEquipDemountPromo(wotPlusController=None):
    storage = wotPlusController.getSettingsStorage()
    if not storage.isRenewableSubscriptionEnabled():
        return False
    for _, tierSettings in storage.reverseIterTiers():
        freeEquipmentDemountingFeature = tierSettings.freeEquipmentDemountingFeature
        enabledAndAvailable = freeEquipmentDemountingFeature.enabled and freeEquipmentDemountingFeature.available
        if enabledAndAvailable and freeEquipmentDemountingFeature.deluxeEnabled:
            return True

    return False


@dependency.replace_none_kwargs(wotPlusController=IWotPlusController)
def hasFreeEquipDemountPromo(wotPlusController=None):
    storage = wotPlusController.getSettingsStorage()
    if not storage.isRenewableSubscriptionEnabled():
        return False
    for _, tierSettings in storage.reverseIterTiers():
        freeEquipmentDemountingFeature = tierSettings.freeEquipmentDemountingFeature
        if freeEquipmentDemountingFeature.enabled and freeEquipmentDemountingFeature.available:
            return True

    return False


@dependency.replace_none_kwargs(wotPlusController=IWotPlusController, steamCompletionCtrl=ISteamCompletionController)
def shouldRedirectToSteamInfoPage(wotPlusController=None, steamCompletionCtrl=None):
    return steamCompletionCtrl.isSteamAccount and wotPlusController.getTier() != WotPlusTier.PRO


@dependency.replace_none_kwargs(wotPlusController=IWotPlusController)
def getPassiveCrewXPPerMinuteFromAllTiers(wotPlusController=None):
    storage = wotPlusController.getSettingsStorage()
    if not storage.isPassiveCrewXPEnabled():
        return 0.0
    xpPerMinute = storage.getCrewXPPerMinute()
    if xpPerMinute and storage.isPassiveCrewXPAvailable():
        return xpPerMinute
    maxXP = 0.0
    for _, tierSettings in storage.iterTier():
        if tierSettings.passiveCrewXPFeature.available:
            maxXP = max(maxXP, tierSettings.passiveCrewXPFeature.xpPerMinute)

    return maxXP


class ProBoostUtils(object):
    _QUEUE_TYPE_TO_ARENA_BONUS_TYPES = None

    @classmethod
    @dependency.replace_none_kwargs(hangarGuiCtrl=IHangarGuiController)
    def isGameModeCompatibleForProBoost(cls, hangarGuiCtrl=None):
        bonusType = hangarGuiCtrl.currentGuiProvider.getSuggestedBonusType()
        if bonusType != ARENA_BONUS_TYPE.UNKNOWN:
            return BONUS_CAPS.checkAny(bonusType, BONUS_CAPS.WOT_PLUS_PRO_BOOST)
        from gui.prb_control.dispatcher import g_prbLoader
        dispatcher = g_prbLoader.getDispatcher()
        if not dispatcher:
            return False
        prbEntity = dispatcher.getEntity()
        if not prbEntity:
            return False
        queueType = prbEntity.getQueueType()
        if queueType == QUEUE_TYPE.UNKNOWN:
            prbType = prbEntity.getEntityType()
            queueTypes = PREBATTLE_TYPE_TO_QUEUE_TYPE.get(prbType)
            if not queueTypes:
                return False
        else:
            queueTypes = [queueType]
        if not cls._QUEUE_TYPE_TO_ARENA_BONUS_TYPES:
            cls._QUEUE_TYPE_TO_ARENA_BONUS_TYPES = defaultdict(set)
            for abt, qbt in ARENA_BONUS_TYPE_TO_QUEUE_TYPE.iteritems():
                cls._QUEUE_TYPE_TO_ARENA_BONUS_TYPES[qbt].add(abt)

        for queueType in queueTypes:
            arenaBonusTypes = cls._QUEUE_TYPE_TO_ARENA_BONUS_TYPES.get(queueType)
            if not arenaBonusTypes:
                continue
            for abType in arenaBonusTypes:
                if BONUS_CAPS.checkAny(abType, BONUS_CAPS.WOT_PLUS_PRO_BOOST):
                    return True

        return False
