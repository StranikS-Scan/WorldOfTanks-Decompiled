# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/shared/missions/packers/events.py
import typing
from comp7.gui.impl.gen.view_models.views.lobby.meta_view.pages.quest_card_model import QuestCardModel, CardState
from comp7.gui.impl.gen.view_models.views.lobby.weekly_quest_model import WeeklyQuestModel
from comp7.gui.impl.lobby.comp7_helpers.account_settings import getLastSeenQuestData
from gui.impl.gen.view_models.common.missions.conditions.condition_group_model import ConditionGroupModel
from gui.impl.gen.view_models.common.missions.conditions.preformatted_condition_model import PreformattedConditionModel
from gui.periodic_battles.models import PeriodType as PT
from gui.shared.missions.packers.conditions import BonusConditionPacker, PostBattleConditionPacker
from gui.shared.missions.packers.events import findFirstConditionModel
from helpers import dependency
from skeletons.gui.game_control import IComp7Controller
if typing.TYPE_CHECKING:
    from typing import Optional, Tuple
    from gui.server_events.event_items import Quest

class Comp7WeeklyQuestPacker(object):
    __comp7Controller = dependency.descriptor(IComp7Controller)
    __slots__ = ('__isUnavailablePeriod', '__isComp7Available', '__hasSuitableVehicles')

    def __init__(self):
        self.__isUnavailablePeriod = self.__comp7Controller.getPeriodInfo().periodType in (PT.BEFORE_SEASON,
         PT.BEFORE_CYCLE,
         PT.BETWEEN_SEASONS,
         PT.AFTER_SEASON,
         PT.AFTER_CYCLE,
         PT.ALL_NOT_AVAILABLE_END,
         PT.NOT_AVAILABLE_END,
         PT.STANDALONE_NOT_AVAILABLE_END)
        self.__isComp7Available = self.__comp7Controller.isAvailable()
        self.__hasSuitableVehicles = self.__comp7Controller.hasSuitableVehicles()

    def pack(self, quest):
        iconKey, currentProgress, totalProgress, description = self.getData(quest)
        state = self.__getQuestState(quest)
        if not currentProgress and state == CardState.COMPLETED:
            currentProgress = totalProgress
        model = QuestCardModel()
        model.setState(state)
        model.setCurrentProgress(currentProgress)
        model.setTotalProgress(totalProgress)
        model.setDescription(description)
        model.setIconKey(iconKey)
        return model

    @staticmethod
    def getData(quest):
        result = (u'', 0, 1, u'')
        if not quest:
            return result
        rootPostBattle = ConditionGroupModel()
        PostBattleConditionPacker().pack(quest, rootPostBattle)
        postBattle = findFirstConditionModel(rootPostBattle)
        rootBonusCond = ConditionGroupModel()
        BonusConditionPacker().pack(quest, rootBonusCond)
        bonusCond = findFirstConditionModel(rootBonusCond)
        bonusCondPriority = bonusCond or postBattle
        if bonusCondPriority:
            postBattlePriority = postBattle or bonusCond
            result = (postBattlePriority.getIconKey(),
             bonusCondPriority.getCurrent(),
             bonusCondPriority.getTotal() or 1,
             quest.getDescription() or bonusCondPriority.getDescrData())
        rootBonusCond.unbind()
        rootPostBattle.unbind()
        return result

    def __getQuestState(self, quest):
        if quest.isCompleted():
            return CardState.COMPLETED
        if self.__isUnavailablePeriod:
            return CardState.LOCKED_BY_INACTIVE_SEASON
        if self.__isComp7Available:
            isQuestAvailable = quest.isAvailable()[0]
            if isQuestAvailable and self.__hasSuitableVehicles:
                return CardState.ACTIVE
            if not isQuestAvailable and not self.__hasSuitableVehicles and quest.getID().endswith('_1_1'):
                return CardState.LOCKED_BY_NO_X_VEHICLES
        return CardState.LOCKED_BY_PREVIOUS_QUEST


class Comp7WeeklyQuestWidgetPacker(Comp7WeeklyQuestPacker):

    def pack(self, quest):
        iconKey, currentProgress, totalProgress, description = self.getData(quest)
        lastSeenProgress, isQuestAnimationSeen = getLastSeenQuestData(quest.getID())
        model = WeeklyQuestModel()
        model.setCurrentProgress(currentProgress)
        model.setTotalProgress(totalProgress)
        model.setDescription(description)
        model.setIcon(iconKey)
        model.setId(quest.getID())
        model.setIsCompleted(quest.isCompleted())
        model.setAnimateCompletion(not isQuestAnimationSeen and quest.isCompleted())
        if not isQuestAnimationSeen:
            model.setEarned(currentProgress - lastSeenProgress)
        return model
