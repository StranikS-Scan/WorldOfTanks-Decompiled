# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/server_events/bonuses_wot_plus.py
import typing
from gui.server_events import bonuses as wotp_b
from renewable_subscription_common.schema import Features
from renewable_subscription_common.settings_constants import WotPlusTier
if typing.TYPE_CHECKING:
    from renewable_subscription_common.settings_helpers import SubscriptionSettingsStorage
    from gui.server_events.bonuses import WoTPlusBonus

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
 (Features.EXCLUSIVE_VEHICLE, wotp_b.WoTPlusExclusiveVehicle, lambda storage: (storage.getExclusiveVehiclesCount(),)),
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
