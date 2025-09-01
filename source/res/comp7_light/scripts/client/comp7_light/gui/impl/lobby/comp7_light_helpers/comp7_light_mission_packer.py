# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_light/scripts/client/comp7_light/gui/impl/lobby/comp7_light_helpers/comp7_light_mission_packer.py
from gui.Scaleform.genConsts.MISSIONS_STATES import MISSIONS_STATES
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.missions.packers.conditions import CONDITION_GROUP_AND
from gui.shared.missions.packers.events import findFirstConditionModel, getEventUIDataPacker
from helpers import dependency
from skeletons.gui.server_events import IEventsCache

def getFirstConditionModelFromQuestModel(dailyQuestModel):
    postBattleModel = findFirstConditionModel(dailyQuestModel.postBattleCondition)
    bonusConditionModel = findFirstConditionModel(dailyQuestModel.bonusCondition)
    return postBattleModel if postBattleModel else bonusConditionModel


@dependency.replace_none_kwargs(eventsCache=IEventsCache)
def packMissionItem(model, raw, questPacker=None, eventsCache=None):

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

    def setProgress(viewModel, questModel):
        postBattleModel = findFirstConditionModel(questModel.postBattleCondition)
        bonusModel = findFirstConditionModel(questModel.bonusCondition)
        progressModel = postBattleModel if postBattleModel else bonusModel
        if postBattleModel and bonusModel:
            progressModel = postBattleModel if postBattleModel.getTotal() > 0 else bonusModel
        viewModel.setCurrentProgress(progressModel.getCurrent())
        viewModel.setTotalProgress(progressModel.getTotal())
        viewModel.setEarned(progressModel.getEarned())

    questUIPacker = questPacker(raw) if questPacker else getEventUIDataPacker(raw)
    fullQuestModel = questUIPacker.pack()
    isCompleted = fullQuestModel.getStatus().value == MISSIONS_STATES.COMPLETED
    model.setIsCompleted(isCompleted)
    model.setAnimateCompletion(eventsCache.questsProgress.getQuestCompletionChanged(raw.getID()))
    model.setIcon(fullQuestModel.getIcon())
    preFormattedConditionModel = getFirstConditionModelFromQuestModel(fullQuestModel)
    if preFormattedConditionModel:
        setDescription(model, fullQuestModel)
        setProgress(model, fullQuestModel)
    fullQuestModel.unbind()
    return (isCompleted, model.getCurrentProgress())
