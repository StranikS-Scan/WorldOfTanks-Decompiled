# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/impl/lobby/common/fun_view_helpers.py
from account_helpers.AccountSettings import AccountSettings, FUN_RANDOM_PROGRESSION, FUN_RANDOM_PROGR_PREV_COUNTER, FUN_RANDOM_INF_PROGR_PREV_COUNTER, FUN_RANDOM_INF_PROGR_PREV_COMPLETE_COUNT
from typing import Any, Dict, List, Optional, Tuple, Union, TYPE_CHECKING
import math_utils
from fun_random.gui.impl.gen.view_models.views.lobby.common.fun_random_progression_stage import FunRandomProgressionStage, Rarity
from fun_random.gui.impl.gen.view_models.views.lobby.common.fun_random_progression_state import FunRandomProgressionStatus
from fun_random.gui.impl.gen.view_models.views.lobby.common.fun_random_quest_card_model import FunRandomQuestCardModel, CardState
from fun_random.gui.impl.lobby.common.lootboxes import FunRandomLootBoxTokenBonusPacker, FunRandomRewardLootBoxTokenBonusPacker, FunRandomLootBoxVehiclesBonusUIPacker, FEP_CATEGORY
from gui.impl import backport
from gui.impl.auxiliary.collections_helper import TmanTemplateBonusPacker
from gui.impl.auxiliary.rewards_helper import BlueprintBonusTypes
from gui.impl.gen import R
from gui.impl.lobby.common.view_helpers import packBonusModelAndTooltipData
from gui.server_events.bonuses import LootBoxTokensBonus, mergeBonuses
from gui.shared.formatters import time_formatters
from gui.shared.formatters.ranges import toRomanRangeString
from gui.shared.missions.packers.bonus import BonusUIPacker, ExtendedBlueprintBonusUIPacker, getDefaultBonusPackersMap, Customization3Dand2DbonusUIPacker, VehiclesBonusUIPacker
from helpers import dependency
from shared_utils import first, findFirst
from skeletons.gui.shared import IItemsCache
if TYPE_CHECKING:
    from frameworks.wulf import Array
    from fun_random.gui.feature.models.progressions import FunProgression
    from fun_random.gui.impl.gen.view_models.views.lobby.common.fun_random_progression_state import FunRandomProgressionState
    from gui.server_events.bonuses import SimpleBonus
    from gui.impl.gen.view_models.common.missions.bonuses.bonus_model import BonusModel
    from gui.impl.gen.view_models.common.missions.bonuses.item_bonus_model import ItemBonusModel
    from fun_random.gui.impl.gen.view_models.views.lobby.common.fun_random_progression_condition import FunRandomProgressionCondition
    from fun_random.gui.impl.gen.view_models.views.lobby.common.fun_random_infinite_progression_condition import FunRandomInfiniteProgressionCondition
    from fun_random.gui.server_events.event_items import FunProgressionTriggerQuest
_PROGRESSION_STATUS_MAP = {(False, False, False): FunRandomProgressionStatus.ACTIVE_RESETTABLE,
 (False, False, True): FunRandomProgressionStatus.ACTIVE_RESETTABLE,
 (True, False, False): FunRandomProgressionStatus.COMPLETED_RESETTABLE,
 (False, True, False): FunRandomProgressionStatus.ACTIVE_FINAL,
 (False, True, True): FunRandomProgressionStatus.ACTIVE_FINAL,
 (True, True, False): FunRandomProgressionStatus.COMPLETED_FINAL,
 (True, False, True): FunRandomProgressionStatus.ACTIVE_INFINITE_RESETTABLE,
 (True, True, True): FunRandomProgressionStatus.ACTIVE_INFINITE_FINAL}
FUN_RANDOM_MAPPING = {'tokens': FunRandomLootBoxTokenBonusPacker,
 'lootBox': FunRandomLootBoxTokenBonusPacker,
 'tmanToken': TmanTemplateBonusPacker,
 'vehicles': VehiclesBonusUIPacker,
 'customizations': Customization3Dand2DbonusUIPacker,
 BlueprintBonusTypes.BLUEPRINTS: ExtendedBlueprintBonusUIPacker,
 BlueprintBonusTypes.BLUEPRINTS_ANY: ExtendedBlueprintBonusUIPacker,
 BlueprintBonusTypes.FINAL_BLUEPRINTS: ExtendedBlueprintBonusUIPacker}
RARITY_ORDER = (Rarity.ORDINARY,
 Rarity.UNUSUAL,
 Rarity.RARE,
 Rarity.EPIC,
 Rarity.LEGENDARY)
LOOTBOX_TYPE = 'fep_{0}'
RARITY_VALUES = tuple((LOOTBOX_TYPE.format(v.value) for v in RARITY_ORDER))
WIN_ICON_KEY = 'win'

def getFormattedTimeLeft(seconds):
    return time_formatters.getTillTimeByResource(seconds, R.strings.fun_random.modeSelector.status.timeLeft, removeLeadingZeros=True)


def getConditionText(rootStrPath, levels):
    battleCondition = rootStrPath.dyn('battleCondition')
    components = [backport.text(battleCondition()) if battleCondition.exists() else '']
    levelCondition = rootStrPath.dyn('levelCondition')
    levels = toRomanRangeString(levels)
    if levelCondition.exists() and levels:
        components.append(backport.text(levelCondition(), levels=levels))
    return ' '.join(components) if len(components) > 1 else first(components, '')


def getFunRandomBonusPacker():
    mapping = getDefaultBonusPackersMap()
    mapping.update(FUN_RANDOM_MAPPING)
    return BonusUIPacker(mapping)


def getCompensatedFunRandomBonusPacker():
    mapping = getDefaultBonusPackersMap()
    mapping.update(FUN_RANDOM_MAPPING)
    mapping.update({'vehicles': FunRandomLootBoxVehiclesBonusUIPacker})
    return BonusUIPacker(mapping)


def getFunRandomSpecialBonusPacker():
    mapping = getDefaultBonusPackersMap()
    mapping.update(FUN_RANDOM_MAPPING)
    mapping.update({'tokens': FunRandomRewardLootBoxTokenBonusPacker,
     'lootBox': FunRandomRewardLootBoxTokenBonusPacker})
    return BonusUIPacker(mapping)


def defineProgressionStatus(progression):
    return _PROGRESSION_STATUS_MAP[progression.state.isCompleted, progression.state.isLastProgression, progression.hasUnlimitedProgression] if progression is not None else FunRandomProgressionStatus.DISABLED


def packAdditionalRewards(progression, stageIndex, showCount, isSpecial=False):
    if progression.isInUnlimitedProgression:
        bonuses = progression.unlimitedProgression.bonuses
    else:
        stage = findFirst(lambda s: s.stageIndex == stageIndex, progression.stages)
        bonuses = stage.bonuses if stage is not None else []
    return packBonuses(sortFunProgressionBonuses(bonuses), showCount, isSpecial)


def packBonuses(bonuses, showCount, isSpecial):
    result = []
    packer = getFunRandomSpecialBonusPacker() if isSpecial else getFunRandomBonusPacker()
    for bonus in mergeBonuses([ b for b in bonuses if b.isShowInGUI() ]):
        result.extend(packer.pack(bonus))

    return result[showCount:]


def packProgressionActiveStage(progression, stageModel, isSpecial=False, tooltips=None):
    maximumPoints = progression.conditions.maximumCounter
    _packStage(progression.activeStage.bonuses, math_utils.clamp(0, maximumPoints, progression.conditions.counter), maximumPoints, progression.conditions.counter >= progression.conditions.maximumCounter, stageModel, isSpecial, tooltips)


def packInfiniteProgressionStage(progression, stageModel, isSpecial=False, tooltips=None):
    maximumPoints = progression.unlimitedProgression.maximumCounter
    _packStage(progression.unlimitedProgression.bonuses, math_utils.clamp(0, maximumPoints, progression.unlimitedProgression.counter), maximumPoints, progression.unlimitedProgression.unlimitedExecutor.isCompleted(), stageModel, isSpecial, tooltips)


def packFullProgressionConditions(modeUserName, progression, conditionModel):
    packProgressionConditions(progression, conditionModel)
    conditionModel.setTitle(modeUserName)
    maxPoints = progression.conditions.maximumCounter
    currentPoints = math_utils.clamp(0, maxPoints, progression.conditions.counter)
    conditionModel.setCurrentPoints(currentPoints)
    conditionModel.setMaximumPoints(maxPoints)
    progressionsData = AccountSettings.getSettings(FUN_RANDOM_PROGRESSION)
    progressionCounters = progressionsData.get(progression.config.name, {})
    prevPoints = progressionCounters.get(FUN_RANDOM_PROGR_PREV_COUNTER, 0)
    conditionModel.setPrevPoints(prevPoints)


def packProgressionConditions(progression, conditionModel):
    _packConditions(conditionModel, progression.statusTimer, progression.conditions.text, progression.conditions.triggers)


def packFullInfiniteProgressionConditions(modeUserName, progression, conditionModel):
    packInfiniteProgressionConditions(progression, conditionModel)
    conditionModel.setTitle(modeUserName)
    maxPoints = progression.unlimitedProgression.maximumCounter
    currentPoints = math_utils.clamp(0, maxPoints, progression.unlimitedProgression.counter)
    conditionModel.setCurrentPoints(currentPoints)
    conditionModel.setMaximumPoints(maxPoints)
    progressionsData = AccountSettings.getSettings(FUN_RANDOM_PROGRESSION)
    progressionCounters = progressionsData.get(progression.config.name, {})
    prevPoints = progressionCounters.get(FUN_RANDOM_INF_PROGR_PREV_COUNTER, 0)
    conditionModel.setPrevPoints(prevPoints)
    completeCount = progression.unlimitedProgression.unlimitedExecutor.getBonusCount()
    conditionModel.setCompleteCount(completeCount)
    prevCompleteCount = progressionCounters.get(FUN_RANDOM_INF_PROGR_PREV_COMPLETE_COUNT, 0)
    conditionModel.setPrevCompleteCount(prevCompleteCount)


def packInfiniteProgressionConditions(progression, conditionModel):
    text = progression.unlimitedProgression.unlimitedTrigger.getDescription()
    triggers = (progression.unlimitedProgression.unlimitedTrigger,)
    statusTimer = progression.statusTimer
    _packConditions(conditionModel, statusTimer, text, triggers)


def packProgressionStages(progression, stagesModel, tooltips=None):
    stagesModel.clear()
    for stage in progression.stages:
        stageModel = FunRandomProgressionStage()
        _packStage(stage.bonuses, progression.conditions.counter, stage.requiredCounter, progression.conditions.counter >= stage.requiredCounter, stageModel, tooltips=tooltips)
        stagesModel.addViewModel(stageModel)

    stagesModel.invalidate()


def packProgressionState(progression, stateModel):
    stateModel.setStatus(defineProgressionStatus(progression))
    stateModel.setCurrentStage(progression.state.currentStageIndex + 1)
    stateModel.setMaximumStage(progression.state.maximumStageIndex + 1)
    stateModel.setStatusTimer(progression.statusTimer)


def packInfiniteProgressionState(progression, stateModel):
    stateModel.setStatus(defineProgressionStatus(progression))
    unlimitedExecutor = progression.unlimitedProgression.unlimitedExecutor
    stateModel.setCurrentStage(unlimitedExecutor.getBonusCount())
    stateModel.setMaximumStage(unlimitedExecutor.bonusCond.getBonusLimit())
    stateModel.setStatusTimer(progression.statusTimer)


def packStageRewards(bonuses, rewardsModel, isSpecial=False, tooltips=None):
    packer = getFunRandomSpecialBonusPacker() if isSpecial else getFunRandomBonusPacker()
    rewardsModel.clear()
    packBonusModelAndTooltipData(sortFunProgressionBonuses(mergeBonuses(bonuses)), rewardsModel, tooltipData=tooltips, packer=packer)
    rewardsModel.invalidate()


def sortFunProgressionBonuses(bonuses):
    lootboxes, other = [], []
    for bonus in bonuses:
        if isinstance(bonus, LootBoxTokensBonus):
            lootboxes.append(bonus)
        other.append(bonus)

    return sorted(lootboxes) + sorted(other)


def _packConditions(conditionModel, statusTimer, text, triggers):
    conditionModel.setText(text)
    conditionModel.setStatusTimer(statusTimer)
    _packTriggers(triggers, conditionModel.getConditions())
    conditionsList = conditionModel.getConditions()
    conditionModel.setConditionIcon(conditionsList[0].getIconKey() if len(conditionsList) == 1 else WIN_ICON_KEY)


def _packTriggers(triggers, cardsModel):
    cardsModel.clear()
    for trigger in sorted(triggers, key=lambda q: q.isCompleted()):
        cardModel = FunRandomQuestCardModel()
        _packTrigger(cardModel, trigger)
        cardsModel.addViewModel(cardModel)

    cardsModel.invalidate()


def _packTrigger(cardModel, trigger):
    cardModel.setState(CardState.COMPLETED if trigger.isCompleted() else CardState.ACTIVE)
    cardModel.setDescription(trigger.getDescription())
    cardModel.setIconKey(trigger.getIconKey())
    cardModel.setCurrentProgress(trigger.getCurrentProgress())
    cardModel.setTotalProgress(trigger.getTotalProgress())
    cardModel.setTotalPoints(trigger.getEarnedPoints())
    altQuest = trigger.getAltQuest()
    cardModel.setMainBonusCount(trigger.getBonusCounterNumber())
    cardModel.setAltBonusCount(altQuest.getBonusCounterNumber() if altQuest else 0)


def _packStage(bonuses, currentPoints, maximumPoints, isCompleted, stageModel, isSpecial=False, tooltips=None):
    stageModel.setCurrentPoints(currentPoints)
    stageModel.setMaximumPoints(maximumPoints)
    stageModel.setRarity(_getStageRarity(bonuses))
    stageModel.setIsCompleted(isCompleted)
    packStageRewards(bonuses, stageModel.getRewards(), isSpecial, tooltips)


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def _getStageRarity(bonuses, itemsCache=None):
    rarityIdx = RARITY_ORDER.index(Rarity.ORDINARY)
    for bonus in (b for b in bonuses if isinstance(b, LootBoxTokensBonus)):
        for tID in bonus.getTokens():
            lb = itemsCache.items.tokens.getLootBoxByTokenID(tID)
            if lb and lb.getCategory() == FEP_CATEGORY and lb.getType() in RARITY_VALUES:
                lbRarityIdx = RARITY_VALUES.index(lb.getType())
                if lbRarityIdx > rarityIdx:
                    rarityIdx = lbRarityIdx

    return RARITY_ORDER[rarityIdx]
