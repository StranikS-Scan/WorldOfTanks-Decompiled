# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/server_events/battle_quests/quest_model_helpers.py
import typing
from constants import DailyQuestDecorationMap, DailyQuestsDecorations
from gui.impl.gen.view_models.common.missions.event_model import EventStatus
from gui.shared.missions.packers.events import findFirstConditionModel
from historical_battles.gui.impl.gen.view_models.views.lobby.quest_model import QuestModel, QuestType
from historical_battles.gui.impl.gen.view_models.views.lobby.hb_meta_view.bonus_model import BonusModel
from historical_battles.gui.server_events.hb_awards_formatter import HBQuestUIDataPacker
if typing.TYPE_CHECKING:
    from typing import Tuple, Optional
    from gui.server_events.event_items import Quest
    from gui.impl.gen.view_models.common.missions.daily_quest_model import DailyQuestModel
__QUEST_DECORATION_TO_TYPE = {DailyQuestsDecorations.WIN: QuestType.WIN,
 DailyQuestsDecorations.FINISH_TOP1: QuestType.TAKEPLACE,
 DailyQuestsDecorations.DESTROY_TANK: QuestType.DESTROYVEHICLES,
 DailyQuestsDecorations.DAMAGE_TANK: QuestType.MAKEDAMAGE}

def makeQuestModel(quest, isDaily=False, questPacker=None):
    questModel = QuestModel()
    fillQuestModel(quest, questModel, isDaily, questPacker)
    return questModel


def fillQuestModel(quest, questModel, isDaily=False, questPacker=None):
    questPacker = questPacker or HBQuestUIDataPacker(quest)
    fullQuestModel = questPacker.pack()
    questModel.setId(fullQuestModel.getId())
    questModel.setDesc(fullQuestModel.getDescription())
    questModel.setType(getQuestType(quest))
    currentProgress, totalProgress = __getProgressData(fullQuestModel)
    questModel.setProgressCount(currentProgress)
    questModel.setProgressTotal(totalProgress)
    questModel.setIsCompleted(fullQuestModel.getStatus() == EventStatus.DONE)
    bonuses = questModel.getBonuses()
    for fullBonusModel in fullQuestModel.getBonuses():
        bonusModel = BonusModel()
        bonusModel.setName(fullBonusModel.getName())
        bonusModel.setIcon(fullBonusModel.getIcon())
        value = fullBonusModel.getValue()
        bonusModel.setAmount(int(value) or 1 if value else 1)
        bonusModel.setTooltipId(fullBonusModel.getTooltipId())
        bonusModel.setTooltipContentId(fullBonusModel.getTooltipContentId())
        bonuses.addViewModel(bonusModel)

    if isDaily:
        questModel.setUpdateTime(quest.getFinishTimeLeft())
    fullQuestModel.unbind()


def getQuestType(quest):
    iconID = quest.getIconID()
    questDecoration = DailyQuestDecorationMap.get(iconID)
    return __QUEST_DECORATION_TO_TYPE.get(questDecoration)


def __getProgressData(dailyQuestModel):
    for conditionModel in [dailyQuestModel.bonusCondition, dailyQuestModel.postBattleCondition]:
        conditionModel = findFirstConditionModel(conditionModel)
        total = conditionModel.getTotal() if conditionModel else None
        if total:
            return (conditionModel.getCurrent(), total)

    return (0, 0)
