# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/feature/models/progressions.py
import typing
from fun_random.gui.feature.fun_constants import PROGRESSION_COUNTER_TEMPLATE, PROGRESSION_UNLIMITED_COUNTER_TEMPLATE
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.utils.decorators import ReprInjector
from helpers import time_utils
from shared_utils import findFirst
if typing.TYPE_CHECKING:
    from fun_random.helpers.server_settings import FunProgressionConfig
    from gui.server_events.bonuses import SimpleBonus
    from gui.server_events.event_items import Quest
    from fun_random.gui.server_events.event_items import FunProgressionTriggerQuest

@ReprInjector.simple(('text', 'text'), ('conditions', 'conditions'), ('resetTimer', 'resetTimer'), ('counterName', 'counterName'), ('counter', 'counter'), ('maximumCounter', 'maximumCounter'))
class FunProgressionConditions(object):

    def __init__(self, pConfig, counter, triggers):
        self.__counter = counter
        self.__finishTimestamp = triggers[0].getFinishTimeRaw()
        self.__pConfig = pConfig
        self.__triggers = triggers

    @property
    def counter(self):
        return self.__counter

    @property
    def triggers(self):
        return self.__triggers

    @property
    def counterName(self):
        return PROGRESSION_COUNTER_TEMPLATE.format(self.__pConfig.name)

    @property
    def maximumCounter(self):
        return self.__pConfig.executors[-1]

    @property
    def finishTimestamp(self):
        return self.__finishTimestamp

    @property
    def text(self):
        return backport.text(R.strings.fun_random.progression.defaultCondition.text()) if len(self.__triggers) > 1 else self.__triggers[0].getDescription()

    def setCounter(self, counter):
        self.__counter = counter


@ReprInjector.simple(('requiredCounter', 'requiredCounter'), ('bonuses', 'bonuses'))
class FunProgressionStage(object):

    def __init__(self, pConfig, index, executor):
        self.__executorID = executor.getID()
        self.__requiredCounter = pConfig.executors[index]
        self.__prevRequiredCounter = pConfig.executors[index - 1] if index else 0
        self.__bonuses = executor.getBonuses()
        self.__stageIndex = index

    @property
    def bonuses(self):
        return self.__bonuses

    @property
    def executorID(self):
        return self.__executorID

    @property
    def prevRequiredCounter(self):
        return self.__prevRequiredCounter

    @property
    def requiredCounter(self):
        return self.__requiredCounter

    @property
    def stageIndex(self):
        return self.__stageIndex


@ReprInjector.simple(('bonuses', 'bonuses'), ('unlimitedTrigger', 'unlimitedTrigger'), ('counterName', 'counterName'), ('counter', 'counter'), ('maximumCounter', 'maximumCounter'))
class FunProgressionUnlimitedProgress(object):

    def __init__(self, pConfig, trigger, executor, counter):
        self.__unlimitedTrigger = trigger
        self.__unlimitedExecutor = executor
        self.__maximumCounter = pConfig.unlimitedExecutor
        self.__counterName = PROGRESSION_UNLIMITED_COUNTER_TEMPLATE.format(pConfig.name)
        self.__counter = counter

    @property
    def bonuses(self):
        return self.__unlimitedExecutor.getBonuses()

    @property
    def unlimitedTrigger(self):
        return self.__unlimitedTrigger

    @property
    def unlimitedExecutor(self):
        return self.__unlimitedExecutor

    @property
    def counterName(self):
        return self.__counterName

    @property
    def counter(self):
        return self.__counter

    def setCounter(self, counter):
        self.__counter = counter

    @property
    def maximumCounter(self):
        return self.__maximumCounter


@ReprInjector.simple(('isCompleted', 'isCompleted'), ('isLastProgression', 'isLastProgression'), ('currentStageIndex', 'currentStageIndex'), ('maximumStageIndex', 'maximumStageIndex'))
class FunProgressionState(object):

    def __init__(self, pConfig, isFirst, isLast, condition, stages):
        self.__pConfig, self.__isFirst, self.__isLast = pConfig, isFirst, isLast
        self.__isCompleted, self.__currentStageIndex = False, 0
        self.updateState(condition, stages)

    @property
    def isCompleted(self):
        return self.__isCompleted

    @property
    def isFirstProgression(self):
        return self.__isFirst

    @property
    def isLastProgression(self):
        return self.__isLast

    @property
    def currentStageIndex(self):
        return self.__currentStageIndex

    @property
    def maximumStageIndex(self):
        return len(self.__pConfig.executors) - 1

    def updateState(self, condition, stages):
        self.__isCompleted = condition.counter >= condition.maximumCounter
        activeStage = findFirst(lambda s: condition.counter < s.requiredCounter, stages)
        self.__currentStageIndex = activeStage.stageIndex if activeStage else len(stages) - 1


@ReprInjector.simple(('condition', 'condition'), ('state', 'state'), ('stages', 'stages'))
class FunProgression(object):

    def __init__(self, pConfig, isFirst, isLast, counter, triggers, executors, unlimitedProgress):
        self.__conditions = FunProgressionConditions(pConfig, counter, triggers)
        self.__pConfig = pConfig
        self.__stages = tuple((FunProgressionStage(pConfig, idx, exe) for idx, exe in enumerate(executors)))
        self.__state = FunProgressionState(pConfig, isFirst, isLast, self.__conditions, self.__stages)
        self.__unlimitedProgress = FunProgressionUnlimitedProgress(pConfig, *unlimitedProgress) if unlimitedProgress else None
        self.__resetTimestamp = 0
        self.__finishTimestamp = 0
        return

    @property
    def isNotifiable(self):
        return not self.__state.isFirstProgression and self.__conditions.counter == 0

    @property
    def activeStage(self):
        return self.__stages[self.__state.currentStageIndex]

    @property
    def conditions(self):
        return self.__conditions

    @property
    def config(self):
        return self.__pConfig

    @property
    def stages(self):
        return self.__stages

    @property
    def state(self):
        return self.__state

    def getAllBonuses(self):
        return [ bonus for stage in self.__stages for bonus in stage.bonuses ]

    def updateCounter(self, counter):
        self.__condition.setCounter(counter)
        self.__state.updateState(self.__condition, self.__stages)

    @property
    def hasUnlimitedProgression(self):
        return self.__unlimitedProgress is not None

    @property
    def isInUnlimitedProgression(self):
        return self.state.isCompleted and self.hasUnlimitedProgression

    @property
    def unlimitedProgression(self):
        return self.__unlimitedProgress

    @property
    def resetTimestamp(self):
        return self.__resetTimestamp

    def setResetTimestamp(self, timestamp):
        self.__resetTimestamp = timestamp

    @property
    def statusTimer(self):
        return self.resetTimer if self.state.isCompleted and not self.hasUnlimitedProgression and not self.state.isLastProgression else time_utils.getTimeDeltaFromNowInLocal(self.conditions.finishTimestamp)

    @property
    def resetTimer(self):
        return time_utils.getTimeDeltaFromNowInLocal(self.__resetTimestamp)
