# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/battle_results/packers/fun_progression_helpers.py
from collections import namedtuple
import math_utils
import typing
from fun_random.gui.feature.fun_constants import FEP_PROGRESSION_BASE_TEMPLATE, FEP_PROGRESSION_TRIGGER_QUEST_ID, FEP_PROGRESSION_ALT_TRIGGER_QUEST_ID, FEP_PROGRESSION_UNLIMITED_TRIGGER_QUEST_ID, FEP_PROGRESSION_UNLIMITED_ALT_TRIGGER_QUEST_ID, FEP_PROGRESSION_EXECUTOR_QUEST_ID, FEP_PROGRESSION_UNLIMITED_EXECUTOR_QUEST_ID, FEP_PROGRESSION_COUNTER_ID, FEP_PROGRESSION_UNLIMITED_COUNTER_ID
from shared_utils import first, findFirst
if typing.TYPE_CHECKING:
    from fun_random.gui.feature.models.progressions import FunProgression
_START_STAGE = 0
_PbsProgress = namedtuple('_PbsProgress', ('description', 'isUnlimitedProgression', 'bonuses', 'previousStage', 'currentStage', 'maximumStage', 'previousPoints', 'currentPoints', 'maximumPoints', 'earnedPoints'))

class _PostbattleProgressionHelper(object):
    __slots__ = ('_triggers', '_altTriggers', '_executors', '_countersProgress')
    _TRIGGER_QUEST_ID = None
    _ALT_TRIGGER_QUEST_ID = None
    _EXECUTOR_QUEST_ID = None
    _COUNTER_ID = None

    def __init__(self):
        self._triggers = {}
        self._altTriggers = {}
        self._executors = {}
        self._countersProgress = {}

    def getProgressionData(self, progression, questsProgress, questsTokens):
        self.__parseProgress(progression, questsProgress, questsTokens)
        return self._collectProgressionData(progression) if self._hasProgress() else None

    def _collectProgressionData(self, progression):
        raise NotImplementedError

    def _getBonuses(self, progression, diffStage=None):
        return []

    def _getPoints(self):
        return (sum([ data.get('diff', 0) for data in self._countersProgress.values() ]), sum([ data.get('total', 0) for data in self._countersProgress.values() ]))

    def _hasProgress(self):
        return bool(self._countersProgress and (self._triggers or self._altTriggers))

    def __parseProgress(self, progression, questsProgress, questsTokens):
        name = progression.config.name
        triggerQuestID = FEP_PROGRESSION_BASE_TEMPLATE.format(self._TRIGGER_QUEST_ID, name)
        altTriggerQuestID = FEP_PROGRESSION_BASE_TEMPLATE.format(self._ALT_TRIGGER_QUEST_ID, name)
        executorQuestID = FEP_PROGRESSION_BASE_TEMPLATE.format(self._EXECUTOR_QUEST_ID, name)
        counterID = FEP_PROGRESSION_BASE_TEMPLATE.format(self._COUNTER_ID, name)
        for qID, pr in questsProgress.items():
            if qID.startswith(triggerQuestID):
                self._triggers[qID] = pr
            if qID.startswith(altTriggerQuestID):
                self._altTriggers[qID] = pr
            if qID.startswith(executorQuestID):
                self._executors[qID] = pr

        self._countersProgress = {tID:progress for tID, progress in questsTokens.items() if tID.startswith(counterID)}


class FunPbsProgressionHelper(_PostbattleProgressionHelper):
    __slots__ = ()
    _TRIGGER_QUEST_ID = FEP_PROGRESSION_TRIGGER_QUEST_ID
    _ALT_TRIGGER_QUEST_ID = FEP_PROGRESSION_ALT_TRIGGER_QUEST_ID
    _EXECUTOR_QUEST_ID = FEP_PROGRESSION_EXECUTOR_QUEST_ID
    _COUNTER_ID = FEP_PROGRESSION_COUNTER_ID

    def _collectProgressionData(self, progression):
        conditions = progression.conditions
        activeTriggers = self.__getActiveQuests(progression.conditions.triggers)
        maximumPoints = conditions.maximumCounter
        earnedPoints, fullCurrentPoints = self._getPoints()
        previousPoints = max(0, fullCurrentPoints - earnedPoints)
        currentPoints = math_utils.clamp(0, maximumPoints, fullCurrentPoints)
        if fullCurrentPoints > maximumPoints:
            earnedPoints = currentPoints - previousPoints
        currentStage = findFirst(lambda s: currentPoints < s.requiredCounter, progression.stages, progression.stages[-1])
        currentStageIdx = math_utils.clamp(0, len(progression.stages), currentStage.stageIndex + 1)
        previousStageIdx = findFirst(lambda s: previousPoints < s.requiredCounter, progression.stages, progression.stages[0]).stageIndex
        previousStage = progression.stages[previousStageIdx]
        descr = first(activeTriggers.values()).getDescription() if len(activeTriggers) == 1 else conditions.text
        return _PbsProgress(isUnlimitedProgression=False, description=descr, previousStage=previousStageIdx + 1, currentStage=currentStageIdx, maximumStage=progression.state.maximumStageIndex + 1, previousPoints=previousPoints - previousStage.prevRequiredCounter, currentPoints=currentPoints - currentStage.prevRequiredCounter, earnedPoints=earnedPoints, maximumPoints=currentStage.requiredCounter - currentStage.prevRequiredCounter, bonuses=self._getBonuses(progression))

    def _getBonuses(self, progression):
        completedStages = sorted([ stage for stage in progression.stages if stage.executorID in self._executors ])
        return [ bonus for stage in completedStages for bonus in stage.bonuses ]

    def __getActiveQuests(self, triggers):
        activeQuests = {}
        for q in triggers:
            if q.getID() in self._triggers:
                activeQuests[q.getID()] = q
            altQuest = q.getAltQuest()
            if altQuest:
                qID = altQuest.getID()
                if qID in self._altTriggers:
                    activeQuests[qID] = altQuest

        return activeQuests


class FunPbsUnlimitedProgressionHelper(_PostbattleProgressionHelper):
    __slots__ = ()
    _TRIGGER_QUEST_ID = FEP_PROGRESSION_UNLIMITED_TRIGGER_QUEST_ID
    _ALT_TRIGGER_QUEST_ID = FEP_PROGRESSION_UNLIMITED_ALT_TRIGGER_QUEST_ID
    _EXECUTOR_QUEST_ID = FEP_PROGRESSION_UNLIMITED_EXECUTOR_QUEST_ID
    _COUNTER_ID = FEP_PROGRESSION_UNLIMITED_COUNTER_ID

    def _collectProgressionData(self, progression):
        unlimitedProgression = progression.unlimitedProgression
        if unlimitedProgression is None:
            return
        else:
            pointsPerStage = unlimitedProgression.maximumCounter
            earnedPoints, totalPoints = self._getPoints()
            if totalPoints > pointsPerStage:
                diffStage = earnedPoints // pointsPerStage
                currentPoints = totalPoints % pointsPerStage
                previousPoints = (totalPoints - earnedPoints) % pointsPerStage
            else:
                diffStage, previousPoints = divmod(totalPoints - earnedPoints, pointsPerStage)
                currentPoints = totalPoints
            return _PbsProgress(isUnlimitedProgression=True, description=unlimitedProgression.unlimitedTrigger.getDescription(), previousStage=_START_STAGE, currentStage=_START_STAGE + abs(diffStage), maximumStage=unlimitedProgression.unlimitedExecutor.bonusCond.getBonusLimit(), previousPoints=previousPoints, currentPoints=currentPoints, earnedPoints=earnedPoints, maximumPoints=pointsPerStage, bonuses=self._getBonuses(progression, abs(diffStage)))

    def _getBonuses(self, progression, diffStage=None):
        diffStage = diffStage if diffStage is not None and diffStage > 1 else 1
        return progression.unlimitedProgression.bonuses * diffStage if self._executors else []
