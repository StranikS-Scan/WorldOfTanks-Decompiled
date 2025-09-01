# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/battle_results/packers/white_tiger_packers.py
import logging
import typing
from frameworks.wulf import Array
from gui.Scaleform.genConsts.CURRENCIES_CONSTANTS import CURRENCIES_CONSTANTS
from gui.battle_results.pbs_helpers.additional_bonuses import isAdditionalXpBonusAvailable, getLeftAdditionalBonus
from gui.battle_results.pbs_helpers.economics import getTotalCreditsToShow, getTotalCrystalsToShow, getTotalXPToShow, getTotalFreeXPToShow
from gui.battle_results.presenters.packers.battle_info import BattleInfo
from gui.battle_results.presenters.packers.manageable_xp_multiplier import ManageableXpMultiplier
from gui.battle_results.presenters.packers.personal_efficiency import PersonalEfficiency
from gui.battle_results.presenters.packers.personal_rewards import PersonalRewards
from gui.battle_results.presenters.packers.team.team_stats_packer import TeamStats
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.common.missions.bonuses.bonus_model import BonusModel
from gui.impl.gen.view_models.views.lobby.battle_results.efficiency_param_constants import EfficiencyParamConstants
from gui.impl.gen.view_models.views.lobby.battle_results.player_model import PlayerModel
from gui.impl.gen.view_models.views.lobby.battle_results.team_stats_column_types import TeamStatsColumnTypes
from gui.impl.gen.view_models.views.lobby.battle_results.team_stats_model import SortingOrder
from gui.shared.gui_items.Vehicle import VEHICLE_CLASS_NAME
from gui.shared.missions.packers.conditions import BonusConditionPacker
from gui.shared.missions.packers.conditions import PostBattleConditionPacker
from helpers import dependency
from helpers import time_utils
from skeletons.gui.server_events import IEventsCache
from white_tiger.gui.battle_results.pbs_helpers import getTotalGoldToShow, isCreditsShown, isGoldShown, isXpShown, isFreeXpShown, isCrystalShown, packAchievementTooltipData, isWhiteTigerAddXpBonusStatusAcceptable, getQuestRewards, getWTAchievement
from white_tiger.gui.impl.gen.view_models.views.lobby.widgets.hangar_consumables_panel_view_model import TankTypeEnum
from white_tiger.gui.white_tiger_gui_constants import WT_QUEST_BOSS_GROUP_ID, MAX_VISIBLE_QUESTS, HUNTER_QUEST_CHAINS
from white_tiger.gui.wt_event_helpers import packWTBonus
from white_tiger_common.wt_constants import WT_TEAMS, WT_VEHICLE_TAGS, WhiteTigerEfficiencyParameterCount, WT_PROGRESSION_ACHIEVEMENT
if typing.TYPE_CHECKING:
    from gui.server_events.event_items import Quest
    from gui.battle_results.stats_ctrl import BattleResults
_MAX_VISIBLE_REWARDS = 6
_logger = logging.getLogger(__name__)

class WhiteTigerBattleInfo(BattleInfo):
    __slots__ = ()

    @classmethod
    def packModel(cls, model, battleResults):
        super(WhiteTigerBattleInfo, cls).packModel(model, battleResults)
        model.setModeName(backport.text(R.strings.white_tiger_lobby.headerButtons.battle.types.white_tiger()))


class WhiteTigerPersonalEfficiency(PersonalEfficiency):
    __slots__ = ()
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
        params = super(WhiteTigerPersonalEfficiency, cls)._getParameterList(vehicle, battleResults)
        return params[:WhiteTigerEfficiencyParameterCount.MAX]


class WhiteTigerTeamStats(TeamStats):
    __slots__ = ()
    _SORTING_PRIORITIES = ((TeamStatsColumnTypes.XP, SortingOrder.DESC), (TeamStatsColumnTypes.DAMAGE, SortingOrder.DESC), (TeamStatsColumnTypes.PLAYER, SortingOrder.ASC))

    @classmethod
    def _packTeam(cls, teamModel, teamData, battleResults):
        teamModel.clear()
        for idx, summarizeInfo in enumerate(teamData):
            if WT_VEHICLE_TAGS.BOT in summarizeInfo.vehicle.descriptor.type.tags:
                continue
            playerModel = PlayerModel()
            playerModel.setPlayerIndex(idx)
            cls.packPlayer(playerModel, summarizeInfo, battleResults)
            teamModel.addViewModel(playerModel)

        teamModel.invalidate()


class WhiteTigerPersonalRewards(PersonalRewards):
    __slots__ = ()
    _REWARDS_ORDER = [WT_PROGRESSION_ACHIEVEMENT,
     CURRENCIES_CONSTANTS.XP_COST,
     CURRENCIES_CONSTANTS.FREE_XP,
     CURRENCIES_CONSTANTS.CREDITS,
     CURRENCIES_CONSTANTS.GOLD,
     'stamp',
     'battlePassPoints',
     CURRENCIES_CONSTANTS.CRYSTAL,
     CURRENCIES_CONSTANTS.EQUIP_COIN,
     'wtevent_lootBox',
     'customizations',
     'wtevent_ticket']
    _AVAILABLE_REWARDS = [CURRENCIES_CONSTANTS.XP_COST,
     CURRENCIES_CONSTANTS.FREE_XP,
     CURRENCIES_CONSTANTS.CREDITS,
     CURRENCIES_CONSTANTS.GOLD,
     CURRENCIES_CONSTANTS.CRYSTAL]
    _ITEM_MODEL_CLS = BonusModel
    _REWARD_GETTERS = {CURRENCIES_CONSTANTS.CREDITS: getTotalCreditsToShow,
     CURRENCIES_CONSTANTS.GOLD: getTotalGoldToShow,
     CURRENCIES_CONSTANTS.CRYSTAL: getTotalCrystalsToShow,
     CURRENCIES_CONSTANTS.XP_COST: getTotalXPToShow,
     CURRENCIES_CONSTANTS.FREE_XP: getTotalFreeXPToShow}
    _REWARDS_TO_CONDITION_MAP = {CURRENCIES_CONSTANTS.CREDITS: isCreditsShown,
     CURRENCIES_CONSTANTS.GOLD: isGoldShown,
     CURRENCIES_CONSTANTS.CRYSTAL: isCrystalShown,
     CURRENCIES_CONSTANTS.XP_COST: isXpShown,
     CURRENCIES_CONSTANTS.FREE_XP: isFreeXpShown}

    @classmethod
    def packModel(cls, modelArray, battleResults, tooltipData):
        modelArray.clear()
        cls._addLeftAchievements(battleResults, tooltipData, modelArray)
        ignoredInQuests = cls._AVAILABLE_REWARDS + ['dossier']
        rewards = getQuestRewards(battleResults.reusable, tooltipData, ignoreList=ignoredInQuests)
        cls._getBattleRewards(battleResults, rewards)
        for model in sorted(rewards.itervalues(), key=cls._rewardSortKey)[:_MAX_VISIBLE_REWARDS]:
            modelArray.addViewModel(model)

        modelArray.invalidate()

    @classmethod
    def _addLeftAchievements(cls, battleResults, tooltipData, modelArray):
        achievement = getWTAchievement(battleResults)
        if achievement is None:
            return
        else:
            tooltipIdx = str(len(tooltipData)) if tooltipData else '0'
            rewardModel = cls._ITEM_MODEL_CLS()
            rewardModel.setName(achievement.getName())
            rewardModel.setValue(achievement.getValue())
            rewardModel.setTooltipId(tooltipIdx)
            rewardModel.setTooltipContentId(str(R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent()))
            packAchievementTooltipData(achievement, tooltipData, tooltipIdx)
            modelArray.addViewModel(rewardModel)
            return

    @classmethod
    def _getBattleRewards(cls, battleResults, rewards):
        rewardsData = cls._getShownRewards(battleResults)
        for rewardType, rewardValue in rewardsData:
            rewardModel = cls._ITEM_MODEL_CLS()
            rewardModel.setName(rewardType)
            rewardModel.setValue(str(rewardValue))
            rewardModel.setTooltipContentId(str(R.views.white_tiger.mono.lobby.tooltips.battle_results_economic_tooltip()))
            rewards[rewardType] = rewardModel

    @classmethod
    def _rewardSortKey(cls, reward):
        if reward.getName() in cls._REWARDS_ORDER:
            return cls._REWARDS_ORDER.index(reward.getName())
        _logger.debug('%s reward not in reward order list', reward.getName())
        return len(cls._REWARDS_ORDER)


class WhiteTigerPremiumPlus(ManageableXpMultiplier):
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
        return isAdditionalXpBonusAvailable(arenaUniqueID, reusable, hasPremiumPlus, isWhiteTigerAddXpBonusStatusAcceptable)


class QuestsContainer(object):
    eventsCache = dependency.descriptor(IEventsCache)

    def getQuests(self, groupID, allowCompleted=False, reverse=False):

        def filterQuests(quest):
            return quest.getGroupID() == groupID and (quest.accountReqs.isAvailable() or allowCompleted and quest.isCompleted())

        quests = self.eventsCache.getAllQuests(filterQuests).items()
        return sorted(quests, key=lambda item: item[1].getPriority(), reverse=reverse)

    def getQuestCompletionChanged(self, questID):
        return self.eventsCache.questsProgress.getQuestCompletionChanged(questID)

    def markQuestProgressAsViewed(self, seenQuestID):
        self.eventsCache.questsProgress.markQuestProgressAsViewed(seenQuestID)


class WTSimpleQuestUIDataPacker(object):

    def __init__(self):
        self.questContainer = QuestsContainer()

    def fillQuests(self, model, teamID):
        if teamID == WT_TEAMS.BOSS_TEAM:
            availableQuests = self.questContainer.getQuests(WT_QUEST_BOSS_GROUP_ID)
        else:
            availableQuests = []
            for chainID in HUNTER_QUEST_CHAINS:
                harrierQuests = self.questContainer.getQuests(chainID, reverse=True)
                if not harrierQuests:
                    harrierQuests = self.questContainer.getQuests(chainID, allowCompleted=True, reverse=True)
                if not harrierQuests:
                    _logger.error("Can't find quests for group %s", chainID)
                    continue
                availableQuests.append(harrierQuests[0])

        availableQuests = availableQuests[:MAX_VISIBLE_QUESTS]
        quests = Array()
        for _, quest in availableQuests:
            questModel = self.pack(quest)
            if questModel:
                with questModel.transaction() as ts:
                    ts.setDescription(quest.getDescription())
                    ts.setIsCompleted(quest.isCompleted())
                quests.addViewModel(questModel)

        if teamID == WT_TEAMS.BOSS_TEAM:
            model.setTankType(TankTypeEnum.BOSS)
            model.setEngineerQuests(quests)
        else:
            model.setTankType(TankTypeEnum.HUNTER)
            model.setHarrierQuests(quests)

    def pack(self, event):
        newModel = WTBonusConditionPacker().pack(event)
        if not newModel:
            newModel = WTPostBattleConditionPacker().pack(event)
        return newModel


class WTBonusConditionPacker(BonusConditionPacker):

    def _traversCondition(self, ctx):
        preFormattedCondition = self._convertConditionIntoPreFormattedCondition(ctx)
        if not preFormattedCondition:
            _logger.error('Should not be reached: preFormattedConditionTuple was not received.')
            return None
        else:
            if len(preFormattedCondition) > 1:
                _logger.error('Should not be reached: More than one tuple was received.')
            preFmtCond = preFormattedCondition[0]
            return packWTBonus(preFmtCond)

    def pack(self, event):
        bonusConditions = event.bonusCond.getConditions()
        bonusCondsModelList, _ = self._packConditions(bonusConditions, event)
        if not bonusCondsModelList:
            _logger.debug('BonusConditions were not received for event %s.', event.getID())
            return None
        else:
            return bonusCondsModelList[0] if bonusCondsModelList else None


class WTPostBattleConditionPacker(PostBattleConditionPacker):

    def _traversCondition(self, ctx):
        preFormattedCondition = self._convertConditionIntoPreFormattedCondition(ctx)
        if not preFormattedCondition:
            _logger.error('Should not be reached: preFormattedConditionTuple was not received.')
            return None
        else:
            if len(preFormattedCondition) > 1:
                _logger.error('Should not be reached: More than one tuple was received.')
            preFmtCond = preFormattedCondition[0]
            return packWTBonus(preFmtCond)

    def pack(self, event):
        bonusConditions = event.postBattleCond.getConditions()
        bonusCondsModelList, _ = self._packConditions(bonusConditions, event)
        if not bonusCondsModelList:
            _logger.debug('BonusConditions were not received for event %s.', event.getID())
            return None
        else:
            return bonusCondsModelList[0] if bonusCondsModelList else None
