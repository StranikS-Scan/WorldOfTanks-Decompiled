# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/user_missions/hangar_widget/utils.py
import typing
from abc import ABCMeta
from gui.Scaleform.genConsts.MISSIONS_STATES import MISSIONS_STATES
from gui.impl.gen.view_models.views.lobby.user_missions.hub.tabs.basic_missions.daily.daily_mission_model import DailyMissionModel
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.user_missions.widget.widget_quest_model import WidgetQuestModel
from gui.server_events.events_helpers import EventInfoModel
from gui.shared.missions.packers.conditions import CONDITION_GROUP_AND
from gui.shared.missions.packers.events import findFirstConditionModel, getEventUIDataPacker
from helpers import dependency
from skeletons.gui.server_events import IEventsCache
if typing.TYPE_CHECKING:
    from typing import Union
    from gui.impl.lobby.user_missions.hangar_widget.providers.user_mission_item import MissionItem
    from gui.server_events.event_items import Quest
    from gui.impl.gen.view_models.views.lobby.user_missions.hub.tabs.basic_missions.weekly.weekly_mission_model import WeeklyMissionModel
    from gui.impl.lobby.user_missions.hangar_widget.providers.user_mission_item import WeeklyQuestMissionItem

class MissionItemPacker(object):
    __metaclass__ = ABCMeta

    def _getFirstConditionModelFromQuestModel(self, dailyQuestModel):
        raise NotImplementedError

    @dependency.replace_none_kwargs(eventsCache=IEventsCache)
    def packMissionItem(self, model, raw, eventsCache=None):

        def setDescription(viewModel, questModel):
            condinionalModel = questModel.postBattleCondition if questModel.postBattleCondition.getItems() else questModel.bonusCondition
            items = condinionalModel.getItems()
            descriptions = [ item.getDescrData() for item in items ]
            separator = ' {} '.format(backport.text(R.strings.quests.dailyQuests.postBattle.conditionTypeAnd()))
            if condinionalModel.getConditionType() == CONDITION_GROUP_AND:
                result = separator.join(descriptions)
            else:
                result = descriptions[0] if descriptions else ''
            viewModel.setDescription(result)

        questUIPacker = getEventUIDataPacker(raw)
        fullQuestModel = questUIPacker.pack()
        isCompleted = fullQuestModel.getStatus().value == MISSIONS_STATES.COMPLETED
        model.setIsCompleted(isCompleted)
        model.setAnimateCompletion(eventsCache.questsProgress.getQuestCompletionChanged(raw.getID()))
        model.setIcon(fullQuestModel.getIcon())
        preFormattedConditionModel = self._getFirstConditionModelFromQuestModel(fullQuestModel)
        if preFormattedConditionModel:
            model.setCurrentProgress(preFormattedConditionModel.getCurrent())
            model.setTotalProgress(preFormattedConditionModel.getTotal())
            model.setEarned(preFormattedConditionModel.getEarned())
            model.setDescription(preFormattedConditionModel.getDescrData())
            setDescription(model, fullQuestModel)
        fullQuestModel.unbind()
        return isCompleted

    def packSpecificMissionItem(self, model, data):
        raise NotImplementedError


def getCountdown(missionItem):
    return EventInfoModel.getDailyProgressResetTimeDelta() if missionItem.itemType == 'bonus' else 0


class DailyMissionItemPacker(MissionItemPacker):

    def _getFirstConditionModelFromQuestModel(self, dailyQuestModel):
        postBattleModel = findFirstConditionModel(dailyQuestModel.postBattleCondition)
        bonusConditionModel = findFirstConditionModel(dailyQuestModel.bonusCondition)
        return postBattleModel if postBattleModel else bonusConditionModel

    def packSpecificMissionItem(self, model, data):
        pass


class WeeklyMissionItemPacker(MissionItemPacker):

    def _getFirstConditionModelFromQuestModel(self, dailyQuestModel):
        return findFirstConditionModel(dailyQuestModel.bonusCondition)

    def packSpecificMissionItem(self, model, data):
        addSpecialConditions(model, data.commonConditionId, data.specialConditionIds)


def addSpecialConditions(model, commonCondition, specialConditionIds):
    model.setCommonConditionId(commonCondition)
    modelSpecialConditions = model.getSpecialConditionIds()
    for conditionId in specialConditionIds:
        modelSpecialConditions.addNumber(conditionId)
