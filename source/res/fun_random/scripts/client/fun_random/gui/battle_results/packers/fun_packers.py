# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/battle_results/packers/fun_packers.py
from fun_random_common.fun_constants import FunEfficiencyParameterCount
from fun_random.gui.battle_results.packers.fun_progression_helpers import FunPbsProgressionHelper, FunPbsUnlimitedProgressionHelper
from fun_random.gui.battle_results.pbs_helpers import getTotalTMenXPToShow, getTotalGoldToShow, getEventID, isCreditsShown, isGoldShown, isXpShown, isFreeXpShown, isTmenXpShown, isCrystalShown, isFunAddXpBonusStatusAcceptable
from fun_random.gui.feature.util.fun_helpers import isFunProgressionUnlimitedTrigger
from fun_random.gui.feature.util.fun_mixins import FunAssetPacksMixin, FunSubModesWatcher, FunProgressionWatcher
from fun_random.gui.impl.gen.view_models.views.lobby.feature.battle_results.fun_random_reward_item_model import FunRandomRewardItemModel, FunRewardTypes
from fun_random.gui.impl.lobby.common.fun_view_helpers import packStageRewards, sortFunProgressionBonuses
from gui.battle_results.pbs_helpers.additional_bonuses import isAdditionalXpBonusAvailable, getLeftAdditionalBonus
from gui.battle_results.pbs_helpers.economics import getTotalCreditsToShow, getTotalCrystalsToShow, getTotalXPToShow, getTotalFreeXPToShow
from gui.battle_results.presenters.packers.battle_info import BattleInfo
from gui.battle_results.presenters.packers.personal_efficiency import PersonalEfficiency
from gui.battle_results.presenters.packers.personal_rewards import PersonalRewards
from gui.battle_results.presenters.packers.premium_plus import PremiumPlus
from gui.battle_results.presenters.packers.team.team_stats_packer import TeamStats
from gui.impl.gen.view_models.views.lobby.battle_results.personal_efficiency_model import EfficiencyParameter
from gui.impl.gen.view_models.views.lobby.battle_results.team_stats_model import ColumnType, SortingOrder
from gui.shared.gui_items.Vehicle import VEHICLE_CLASS_NAME
from helpers import time_utils

class FunRandomBattleInfo(BattleInfo, FunAssetPacksMixin):
    __slots__ = ()

    @classmethod
    def packModel(cls, model, battleResults):
        super(FunRandomBattleInfo, cls).packModel(model, battleResults)
        model.setModeName(cls.getModeUserName())
        model.setAssetsPointer(FunAssetPacksMixin.getModeAssetsPointer())


class FunRandomPersonalEfficiency(PersonalEfficiency, FunSubModesWatcher):
    __slots__ = ()
    _PARAMETERS = {VEHICLE_CLASS_NAME.SPG: (EfficiencyParameter.KILLS,
                              EfficiencyParameter.DAMAGEDEALT,
                              EfficiencyParameter.DAMAGEASSISTED,
                              EfficiencyParameter.STUN)}
    _DEFAULT_PARAMS = (EfficiencyParameter.KILLS,
     EfficiencyParameter.DAMAGEDEALT,
     EfficiencyParameter.DAMAGEASSISTED,
     EfficiencyParameter.DAMAGEBLOCKEDBYARMOR)

    @classmethod
    def _getParameterList(cls, vehicle, battleResults):
        subMode = cls.getSubMode(getEventID(battleResults.reusable))
        allParameters = subMode.getEfficiencyParameters() if subMode is not None else {}
        params = [ EfficiencyParameter(param) for param in allParameters.get(vehicle.type, ()) ]
        params = params or super(FunRandomPersonalEfficiency, cls)._getParameterList(vehicle, battleResults)
        return params[:FunEfficiencyParameterCount.MAX]


class FunRandomTeamStats(TeamStats):
    __slots__ = ()
    _SORTING_PRIORITIES = ((ColumnType.XP.value, SortingOrder.DESC), (ColumnType.DAMAGE.value, SortingOrder.DESC), (ColumnType.PLAYER.value, SortingOrder.ASC))


class FunRandomPersonalRewards(PersonalRewards):
    __slots__ = ()
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


class FunRandomPremiumPlus(PremiumPlus):
    __slots__ = ()

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


class FunRandomProgress(FunProgressionWatcher, FunAssetPacksMixin):
    __slots__ = ()

    @classmethod
    def packModel(cls, model, battleResults, *args, **kwargs):
        progression = FunProgressionWatcher.getActiveProgression()
        if progression is None:
            model.setHasProgress(False)
            return
        else:
            personalInfo = battleResults.reusable.personal
            questsProgress = personalInfo.getQuestsProgress()
            questsTokens = personalInfo.getQuestTokensCount()
            helper = cls.__createProgressionHelper(questsProgress)
            progressionData = helper.getProgressionData(progression, questsProgress, questsTokens)
            if progressionData is None:
                model.setHasProgress(False)
                return
            model.setHasProgress(True)
            model.setAssetsPointer(FunAssetPacksMixin.getModeAssetsPointer())
            model.setIsInUnlimitedProgression(progressionData.isUnlimitedProgression)
            model.setDescription(progressionData.description)
            model.setPreviousPoints(progressionData.previousPoints)
            model.setCurrentPoints(progressionData.currentPoints)
            model.setMaximumPoints(progressionData.maximumPoints)
            model.setEarnedPoints(progressionData.earnedPoints)
            model.setPreviousStage(progressionData.previousStage)
            model.setCurrentStage(progressionData.currentStage)
            model.setMaximumStage(progressionData.maximumStage)
            bonuses = progressionData.bonuses
            rewardsData = kwargs.get('rewardsData')
            if bonuses and rewardsData is not None:
                bonuses = sortFunProgressionBonuses(bonuses)
                packStageRewards(bonuses, model.getRewards(), isSpecial=True, tooltips=rewardsData.tooltips)
                rewardsData.bonuses.extend(bonuses)
            return

    @staticmethod
    def __createProgressionHelper(questsProgress):
        unlimitedTriggers = {qID:p for qID, p in questsProgress.items() if isFunProgressionUnlimitedTrigger(qID)}
        helperCls = FunPbsUnlimitedProgressionHelper if unlimitedTriggers else FunPbsProgressionHelper
        return helperCls()
