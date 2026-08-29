# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/wot_plus/utils.py
from __future__ import absolute_import
from collections import defaultdict
import typing
from future.utils import viewitems
from arena_bonus_type_caps import ARENA_BONUS_TYPE_CAPS as BONUS_CAPS
from constants import ARENA_BONUS_TYPE
from constants import QUEUE_TYPE, ARENA_BONUS_TYPE_TO_QUEUE_TYPE
from gui.impl.gen.view_models.views.lobby.battle_results.additional_bonus_model import WotPlusTypeEnum
from gui.prb_control.settings import PREBATTLE_TYPE_TO_QUEUE_TYPE
from helpers import dependency
from renewable_subscription_common.settings_constants import WotPlusTier
from skeletons.gui.game_control import IWotPlusController, IHangarGuiController, ISteamCompletionController
if typing.TYPE_CHECKING:
    from constants import PREBATTLE_TYPE
    from renewable_subscription_common.settings_helpers import SubscriptionSettingsStorage
    from typing import Optional
WOT_PLUS_TIER_MAP = {WotPlusTier.NONE: WotPlusTypeEnum.NONE,
 WotPlusTier.CORE: WotPlusTypeEnum.CORE,
 WotPlusTier.PRO: WotPlusTypeEnum.PRO}

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
def hasAdditionalXPPromoData(wotPlusController=None):
    storage = wotPlusController.getSettingsStorage()
    if storage.isAdditionalXPBonusEnabled():
        for _, tierSettings in storage.reverseIterTiers():
            additionalXPFeature = tierSettings.additionalXPBonusFeature
            if additionalXPFeature.available and additionalXPFeature.applyCount > 0:
                return True

    return False


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


@dependency.replace_none_kwargs(wotPlusController=IWotPlusController)
def getMaxGoldReserveCapacityFromAllTiers(wotPlusController=None):
    storage = wotPlusController.getSettingsStorage()
    if not storage.isGoldReserveFeatureEnabled():
        return 0
    if storage.isGoldReserveFeatureAvailable():
        return storage.getMaxGoldReserveCapacity()
    maxCapacity = 0
    for _, tierSettings in storage.iterTier():
        if tierSettings.goldReserveFeature.available:
            maxCapacity = max(maxCapacity, tierSettings.goldReserveFeature.maxCapacity)

    return maxCapacity


@dependency.replace_none_kwargs(wotPlusController=IWotPlusController, steamCompletionCtrl=ISteamCompletionController)
def shouldRedirectToSteamInfoPage(wotPlusController=None, steamCompletionCtrl=None):
    return steamCompletionCtrl.isSteamAccount and wotPlusController.getTier() != WotPlusTier.PRO


@dependency.replace_none_kwargs(wotPlusController=IWotPlusController)
def getPassiveCrewXPPerMinuteFromAllTiers(wotPlusController=None):
    storage = wotPlusController.getSettingsStorage()
    return 0.0 if not storage.isPassiveCrewXPEnabled() else storage.getDefCrewXPPerMinute()


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
            for abt, qbt in viewitems(ARENA_BONUS_TYPE_TO_QUEUE_TYPE):
                cls._QUEUE_TYPE_TO_ARENA_BONUS_TYPES[qbt].add(abt)

        for queueType in queueTypes:
            arenaBonusTypes = cls._QUEUE_TYPE_TO_ARENA_BONUS_TYPES.get(queueType)
            if not arenaBonusTypes:
                continue
            for abType in arenaBonusTypes:
                if BONUS_CAPS.checkAny(abType, BONUS_CAPS.WOT_PLUS_PRO_BOOST):
                    return True

        return False
