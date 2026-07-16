# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_light/scripts/client/comp7_light/gui/impl/lobby/battle_results/missions_progress/progress_filters.py
from __future__ import absolute_import
from gui.battle_results.progress.progress_helpers import isQuestCompleted
from helpers import dependency
from comp7_light.skeletons.gui.game_control import IComp7LightProgressionController

@dependency.replace_none_kwargs(progressionCtrl=IComp7LightProgressionController)
def comp7LightProgressionQuestsOnlyFilter(reusable, allCommonQuests, progressionCtrl=None):
    result = []
    if not progressionCtrl.isEnabled:
        return result
    else:
        comp7LightQuestIds = set(progressionCtrl.questContainer.questsIds)
        comp7LightQuests = progressionCtrl.questContainer.getQuests()
        questsProgress = reusable.personal.getQuestsProgress()
        if not questsProgress:
            return result
        for qID, qProgress in questsProgress.items():
            if qID in comp7LightQuestIds:
                quest = comp7LightQuests.get(qID)
                if quest is not None:
                    pGroupBy, pPrev, pCur = qProgress
                    isCompleted = isQuestCompleted(pGroupBy, pPrev, pCur)
                    isProgressReset = not isCompleted and quest.bonusCond.isInRow() and pCur.get('battlesCount', 0) == 0
                    if pPrev or max(pCur.itervalues()) != 0:
                        data = (quest,
                         {pGroupBy: pCur},
                         {pGroupBy: pPrev},
                         isProgressReset,
                         isCompleted)
                        result.append(data)

        return result
