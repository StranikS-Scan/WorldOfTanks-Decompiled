# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/battle_results/packers/fun_packers.py
from __future__ import absolute_import
from fun_random_common.fun_constants import FunEfficiencyParameterCount
from fun_random.gui.battle_results.pbs_helpers import getTotalTMenXPToShow, getTotalGoldToShow, getEventID, isCreditsShown, isGoldShown, isXpShown, isFreeXpShown, isTmenXpShown, isCrystalShown, isFunAddXpBonusStatusAcceptable
from fun_random.gui.feature.util.fun_mixins import FunAssetPacksMixin, FunSubModesWatcher
from fun_random.gui.impl.gen.view_models.views.lobby.feature.battle_results.fun_player_model import FunPlayerModel
from fun_random.gui.impl.gen.view_models.views.lobby.feature.battle_results.fun_random_reward_item_model import FunRandomRewardItemModel, FunRewardTypes
from gui.battle_results.pbs_helpers.additional_bonuses import isAdditionalXpBonusAvailable, getLeftAdditionalBonus
from gui.battle_results.pbs_helpers.economics import getTotalCreditsToShow, getTotalCrystalsToShow, getTotalXPToShow, getTotalFreeXPToShow
from gui.battle_results.presenters.packers.battle_info import BattleInfo
from gui.battle_results.presenters.packers.personal_efficiency import PersonalEfficiency
from gui.battle_results.presenters.packers.personal_rewards import PersonalRewards
from gui.battle_results.presenters.packers.manageable_xp_multiplier import ManageableXpMultiplier
from gui.battle_results.presenters.packers.team.team_stats_packer import TeamStats
from gui.impl.gen.view_models.views.lobby.battle_results.efficiency_param_constants import EfficiencyParamConstants
from gui.impl.gen.view_models.views.lobby.battle_results.team_stats_model import SortingOrder
from gui.impl.gen.view_models.views.lobby.battle_results.team_stats_column_types import TeamStatsColumnTypes
from gui.shared.gui_items.Vehicle import VEHICLE_CLASS_NAME
from helpers import time_utils

class FunRandomBattleInfo(BattleInfo, FunAssetPacksMixin, FunSubModesWatcher):

    @classmethod
    def packModel(cls, model, battleResults):
        super(FunRandomBattleInfo, cls).packModel(model, battleResults)
        model.setModeName(cls.getModeUserName())
        model.setAssetsPointer(cls.getModeAssetsPointer())
        subMode = cls.getSubMode(getEventID(battleResults.reusable))
        model.setSubModeAssetsPointer(subMode.getAssetsPointer())


class FunRandomPersonalEfficiency(PersonalEfficiency, FunSubModesWatcher):
    _PARAMETERS = {VEHICLE_CLASS_NAME.SPG: (EfficiencyParamConstants.KILLS,
                              EfficiencyParamConstants.DAMAGE_DEALT,
                              EfficiencyParamConstants.DAMAGE_ASSISTED,
                              EfficiencyParamConstants.STUN)}
    _DEFAULT_PARAMS = (EfficiencyParamConstants.KILLS,
     EfficiencyParamConstants.DAMAGE_DEALT,
     EfficiencyParamConstants.DAMAGE_ASSISTED,
     EfficiencyParamConstants.DAMAGE_BLOCKED_BY_ARMOR)

    @classmethod
    def _getParameterList(cls, vehicle, battleResults):
        subMode = cls.getSubMode(getEventID(battleResults.reusable))
        allParameters = subMode.getEfficiencyParameters() if subMode is not None else {}
        params = list(allParameters.get(vehicle.type, ()))
        params = params or super(FunRandomPersonalEfficiency, cls)._getParameterList(vehicle, battleResults)
        return params[:FunEfficiencyParameterCount.MAX]


class FunRandomTeamStats(TeamStats):
    _PLAYER_MODEL_CLS = FunPlayerModel
    _SORTING_PRIORITIES = ((TeamStatsColumnTypes.XP, SortingOrder.DESC), (TeamStatsColumnTypes.DAMAGE, SortingOrder.DESC), (TeamStatsColumnTypes.PLAYER, SortingOrder.ASC))


class FunRandomPersonalRewards(PersonalRewards):
    _AVAILABLE_REWARDS = [FunRewardTypes.XP,
     FunRewardTypes.CREDITS,
     FunRewardTypes.GOLD,
     FunRewardTypes.CRYSTALS,
     FunRewardTypes.FREE_XP,
     FunRewardTypes.TANKMEN_XP]
    _ITEM_MODEL_CLS = FunRandomRewardItemModel
    _REWARD_GETTERS = {FunRewardTypes.CREDITS: getTotalCreditsToShow,
     FunRewardTypes.GOLD: getTotalGoldToShow,
     FunRewardTypes.CRYSTALS: getTotalCrystalsToShow,
     FunRewardTypes.XP: getTotalXPToShow,
     FunRewardTypes.FREE_XP: getTotalFreeXPToShow,
     FunRewardTypes.TANKMEN_XP: getTotalTMenXPToShow}
    _REWARDS_TO_CONDITION_MAP = {FunRewardTypes.CREDITS: isCreditsShown,
     FunRewardTypes.GOLD: isGoldShown,
     FunRewardTypes.CRYSTALS: isCrystalShown,
     FunRewardTypes.XP: isXpShown,
     FunRewardTypes.FREE_XP: isFreeXpShown,
     FunRewardTypes.TANKMEN_XP: isTmenXpShown}


class FunRandomPremiumPlus(ManageableXpMultiplier):

    @classmethod
    def _updateLeftCount(cls, model, wasPremiumPlusInBattle, hasPremiumPlus, hasWotPlus):
        hasAccessToAdditionalBonus, leftCount, wotPremLeftCount = getLeftAdditionalBonus(hasWotPlus, hasPremiumPlus, wasPremiumPlusInBattle)
        isAllAddBonusesApplied = hasAccessToAdditionalBonus and leftCount == 0 and wotPremLeftCount == 0
        timeLeft = time_utils.getDayTimeLeft() if isAllAddBonusesApplied else -1
        model.setNextBonusTime(timeLeft)
        model.setLeftBonusCount(leftCount)
        model.setIsUndefinedLeftBonusCount(hasAccessToAdditionalBonus and leftCount == 0 and wotPremLeftCount > 0)

    @classmethod
    def _getXpAdditionalBonusStatus(cls, arenaUniqueID, reusable, hasPremiumPlus):
        return isAdditionalXpBonusAvailable(arenaUniqueID, reusable, hasPremiumPlus, isFunAddXpBonusStatusAcceptable)
