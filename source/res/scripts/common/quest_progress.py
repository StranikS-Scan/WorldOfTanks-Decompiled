# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/quest_progress.py
from collections import Counter
from constants import QUEST_PROGRESS_STATE
from personal_missions_constants import PROGRESS_TEMPLATE

class IProgress(object):

    def getProgressID(self):
        raise NotImplementedError

    def updateProgress(self, progress):
        raise NotImplementedError

    def getProgress(self):
        raise NotImplementedError

    def isChanged(self):
        raise NotImplementedError

    def markAsVisited(self):
        raise NotImplementedError


class Progress(IProgress):

    def __init__(self, progressID, config):
        self.__progressID = progressID
        self.__isMain = False
        self.__isAward = False
        self.__state = QUEST_PROGRESS_STATE.IN_PROGRESS
        self.__countDown = None
        self.__visibleScope = None
        self.__isChanged = False
        self.__isCumulative = False
        self._setCfg(**config)
        return

    def getProgressID(self):
        return self.__progressID

    def isMain(self):
        return self.__isMain

    def isAward(self):
        return self.__isAward

    def isCumulative(self):
        return self.__isCumulative

    def getParam(self, name):
        return self.__params.get(name)

    def getProgress(self):
        return {'state': self.getState()}

    def updateProgress(self, progress):
        if progress:
            self.setState(progress.get('state'))

    def isChanged(self):
        return self.__isChanged

    def setState(self, state):
        if self.__state != state:
            self.__state = state
            self._markAsChanged()

    def getState(self):
        return self.__state

    def _setCfg(self, isMain=False, countdown=None, visibleScope=(), isCumulative=False, params=None, isAward=False):
        self.__isMain = isMain
        self.__isAward = isAward
        self.__countDown = countdown
        self.__visibleScope = visibleScope
        self.__isCumulative = isCumulative
        self.__params = params or {}

    def getVisibleScope(self):
        return self.__visibleScope

    def getCountDown(self):
        return self.__countDown

    def _markAsChanged(self):
        self.__isChanged = True

    def markAsVisited(self):
        self.__isChanged = False


class BinaryProgress(Progress):

    def __init__(self, progressID, config):
        self.__isDelay = False
        super(BinaryProgress, self).__init__(progressID, config)

    def isDelay(self):
        return self.__isDelay

    def _setCfg(self, isDelay=False, **kwargs):
        super(BinaryProgress, self)._setCfg(**kwargs)
        self.__isDelay = isDelay


class ValueProgress(Progress):

    def __init__(self, progressID, config):
        self.__dynamicGoal = False
        self.__goal = 0
        self.__value = 0
        super(ValueProgress, self).__init__(progressID, config)

    def getProgress(self):
        return {'value': self.getValue(),
         'state': self.getState(),
         'goal': self.getGoal()}

    def updateProgress(self, progress):
        if progress:
            self.setState(progress['state'])
            self.setValue(progress['value'])
            if self.__dynamicGoal:
                self.setGoal(progress['goal'])

    def isDynamicGoal(self):
        return self.__dynamicGoal

    def setGoal(self, goal):
        if self.__goal != goal:
            self.__goal = goal
            self._markAsChanged()

    def getGoal(self):
        return self.__goal

    def setValue(self, value):
        if self.__value != value:
            self.__value = value
            self._markAsChanged()

    def __iadd__(self, value):
        self.setValue(self.__value + value)
        return self

    def getValue(self):
        return self.__value

    def _setCfg(self, goal=0, dynamicGoal=False, **kwargs):
        super(ValueProgress, self)._setCfg(**kwargs)
        self.__goal = goal
        self.__dynamicGoal = dynamicGoal


class CounterProgress(Progress):

    def __init__(self, progressID, config):
        self.__uniqueGoal = 0
        self.__totalGoal = 0
        self.__counter = Counter()
        super(CounterProgress, self).__init__(progressID, config)

    def _setCfg(self, uniqueGoal=0, totalGoal=False, **kwargs):
        super(CounterProgress, self)._setCfg(**kwargs)
        self.__uniqueGoal = uniqueGoal
        self.__totalGoal = totalGoal

    def getCounter(self):
        return self.__counter

    def addValue(self, key, value):
        self.__counter[key] += value
        self._markAsChanged()

    def getUniqueGoal(self):
        return self.__uniqueGoal

    def getUniqueCount(self):
        return len(self.__counter)

    def getTotalGoal(self):
        return self.__totalGoal

    def getTotalCount(self):
        return sum(self.__counter.itervalues())

    def getUniqueKeys(self):
        return self.__counter.keys()

    def setCounter(self, counter):
        if self.__counter != counter:
            self.__counter = counter
            self._markAsChanged()

    def getProgress(self):
        return {'counter': self.getCounter(),
         'state': self.getState()}

    def updateProgress(self, progress):
        if progress:
            self.setState(progress['state'])
            self.setCounter(progress['counter'])


class BattlesSeries(Progress):

    def __init__(self, progressID, config):
        self.__goal = 0
        self.__battlesLimit = 0
        self.__battles = []
        super(BattlesSeries, self).__init__(progressID, config)

    def addBattle(self, result):
        self.__battles.append(result)

    def getSuccessfullBattles(self):
        return self.__battles.count(True)

    def getFailedBattles(self):
        return self.__battles.count(False)

    def setGoal(self, goal):
        if self.__goal != goal:
            self.__goal = goal
            self._markAsChanged()

    def getGoal(self):
        return self.__goal

    def getBattlesLimit(self):
        return self.__battlesLimit

    def getBattles(self):
        return self.__battles

    def setBattles(self, battles):
        if self.__battles != battles:
            self.__battles = battles
            self._markAsChanged()

    def getProgress(self):
        return {'battles': self.getBattles(),
         'state': self.getState(),
         'goal': self.getGoal()}

    def updateProgress(self, progress):
        if progress:
            self.setState(progress['state'])
            self.setBattles(progress['battles'])

    def setZero(self):
        self.setState(QUEST_PROGRESS_STATE.IN_PROGRESS)
        self.setBattles([])

    def isZero(self):
        return self.getState() in (QUEST_PROGRESS_STATE.IN_PROGRESS, QUEST_PROGRESS_STATE.NOT_STARTED) and len(self.getBattles()) == 0

    def _setCfg(self, goal=0, battlesLimit=0, **kwargs):
        super(BattlesSeries, self)._setCfg(**kwargs)
        self.__goal = goal
        self.__battlesLimit = battlesLimit


class IProgressBuilder(object):

    @classmethod
    def build(cls, progressID, progressData):
        raise NotImplementedError

    @classmethod
    def getTemplateID(cls):
        raise NotImplementedError


class BinaryProgressBuilder(IProgressBuilder):

    @classmethod
    def build(cls, progressID, progressData):
        return BinaryProgress(progressID, progressData['config'])

    @classmethod
    def getTemplateID(cls):
        return PROGRESS_TEMPLATE.BINARY


class ValueProgressBuilder(IProgressBuilder):

    @classmethod
    def build(cls, progressID, progressData):
        return ValueProgress(progressID, progressData['config'])

    @classmethod
    def getTemplateID(cls):
        return PROGRESS_TEMPLATE.VALUE


class CounterProgressBuilder(IProgressBuilder):

    @classmethod
    def build(cls, progressID, progressData):
        return CounterProgress(progressID, progressData['config'])

    @classmethod
    def getTemplateID(cls):
        return PROGRESS_TEMPLATE.COUNTER


class BattlesSeriesProgressBuilder(IProgressBuilder):

    @classmethod
    def build(cls, progressID, progressData):
        return BattlesSeries(progressID, progressData['config'])

    @classmethod
    def getTemplateID(cls):
        return PROGRESS_TEMPLATE.BIATHLON


class IDataCollector(object):

    @classmethod
    def validate(cls, progress):
        raise NotImplementedError

    @classmethod
    def collect(cls, progress):
        raise NotImplementedError


class AllProgressCollector(IDataCollector):

    @classmethod
    def validate(cls, progress):
        if progress.isChanged():
            progress.markAsVisited()
        return True

    @classmethod
    def collect(cls, progress):
        return progress.getProgress()


class ChangedProgressCollector(IDataCollector):

    @classmethod
    def validate(cls, progress):
        if progress.isChanged():
            progress.markAsVisited()
            return True
        return False

    @classmethod
    def collect(cls, progress):
        return progress.getProgress()


class CumulativeOnlyProgressCollector(IDataCollector):

    @classmethod
    def validate(cls, progress):
        return progress.isCumulative()

    @classmethod
    def collect(cls, progress):
        return progress.getProgress()


class ProgressStorage(object):
    __slots__ = ('__progresses', '_buildrers', '_wasMultiplied')

    def __init__(self, questCfg, savedProgresses=None):
        self.__progresses = {}
        self._buildrers = {}
        self._wasMultiplied = None
        for builder in self._getBuilders():
            self.__addBuilder(builder)

        for progressID, configData in questCfg.iteritems():
            self.__progresses[progressID] = self._createProgress(progressID, configData)

        if savedProgresses:
            self.update(savedProgresses)
        return

    def update(self, progressesInfo):
        for progressID, progressInfo in progressesInfo.iteritems():
            progress = self.__progresses.get(progressID)
            if progress:
                progress.updateProgress(progressInfo)

    def getProgresses(self):
        return self.__progresses

    def getProgress(self, progressID):
        return self.__progresses.get(progressID)

    def getMainProgress(self):
        return [ value for value in self.__progresses.itervalues() if value.isMain() and value.isAward() ]

    def save(self):
        return self._collectProgressInfo(CumulativeOnlyProgressCollector())

    def _createProgress(self, progressID, configData):
        builder = self._buildrers[configData['type']]
        return builder.build(progressID, configData)

    def _collectProgressInfo(self, dataCollector):
        result = {}
        for progressID, progress in self.__progresses.iteritems():
            if dataCollector.validate(progress):
                result[progressID] = dataCollector.collect(progress)

        return result

    @classmethod
    def _getBuilders(cls):
        return (BinaryProgressBuilder,
         ValueProgressBuilder,
         CounterProgressBuilder,
         BattlesSeriesProgressBuilder)

    def __addBuilder(self, builder):
        self._buildrers[builder.getTemplateID()] = builder


class BaseQuestProgress(object):

    def __init__(self, questCfg, savedProgresses):
        self._progressStorage = ProgressStorage(questCfg, savedProgresses)
        self._timeProvider = lambda : 0
        self._wasFailed = False
        self._wasCompleted = False
        self._progressBeforeFailed = ''

    def save(self):
        return self._progressStorage.save()

    def getProgresses(self):
        return self._progressStorage.getProgresses()

    def getProgress(self, progressID):
        return self._progressStorage.getProgress(progressID)

    def getMainProgress(self):
        return self._progressStorage.getMainProgress()

    def setCompleted(self, progressID, isMainProgressCompleted=True):
        progress = self._progressStorage.getProgress(progressID)
        if isMainProgressCompleted:
            self.setWasCompleted(progressID, True)
            progress.setState(QUEST_PROGRESS_STATE.COMPLETED)
        else:
            progress.setState(QUEST_PROGRESS_STATE.PRELIMINARY_COMPLETED)

    def isCompleted(self, progressID):
        progress = self._progressStorage.getProgress(progressID)
        return progress.getState() == QUEST_PROGRESS_STATE.COMPLETED

    def isFailed(self, progressID):
        progress = self._progressStorage.getProgress(progressID)
        return progress.getState() == QUEST_PROGRESS_STATE.FAILED

    def isAward(self, progressID):
        progress = self._progressStorage.getProgress(progressID)
        return progress.isAward()

    def isPreliminaryCompleted(self, progressID):
        progress = self._progressStorage.getProgress(progressID)
        return progress.getState() == QUEST_PROGRESS_STATE.PRELIMINARY_COMPLETED

    def isFinished(self, progressID):
        progress = self._progressStorage.getProgress(progressID)
        return progress.getState() in QUEST_PROGRESS_STATE.FINISHED_STATES

    def setFailed(self, progressID):
        progress = self._progressStorage.getProgress(progressID)
        progress.setState(QUEST_PROGRESS_STATE.FAILED)

    def setZero(self, progressID):
        progress = self._progressStorage.getProgress(progressID)
        progress.setState(QUEST_PROGRESS_STATE.IN_PROGRESS)
        if isinstance(progress, ValueProgress):
            progress.setValue(0)
        elif isinstance(progress, BattlesSeries):
            progress.setBattles([])
        else:
            progress.setCounter(Counter())

    def isZero(self, progressID):
        progress = self._progressStorage.getProgress(progressID)
        if isinstance(progress, ValueProgress):
            return bool(progress.getState() is QUEST_PROGRESS_STATE.IN_PROGRESS and progress.getValue() == 0)
        elif isinstance(progress, BattlesSeries):
            return bool(progress.getState() is QUEST_PROGRESS_STATE.IN_PROGRESS and progress.getBattles() == [])
        else:
            return bool(progress.getState() is QUEST_PROGRESS_STATE.IN_PROGRESS and progress.getCounter() == Counter())

    def setFailedIfNotCompleted(self, progressID):
        progress = self._progressStorage.getProgress(progressID)
        if progress.getState() not in QUEST_PROGRESS_STATE.COMPLETED_STATES:
            progress.setState(QUEST_PROGRESS_STATE.FAILED)

    def getInitialValueForUpdate(self, progressID):
        progress = self._progressStorage.getProgress(progressID)
        return progress.getValue()

    def updateUntilComplete(self, progressID, value, isMainProgressCompleted=True):
        progress = self._progressStorage.getProgress(progressID)
        if progress.getState() not in QUEST_PROGRESS_STATE.COMPLETED_STATES:
            progress.setValue(value)
            if progress.getValue() >= progress.getGoal():
                self.setCompleted(progressID, isMainProgressCompleted)
        return self.isCompleted(progressID)

    def increaseUntilComplete(self, progressID, value, isMainProgressCompleted=True):
        progress = self._progressStorage.getProgress(progressID)
        countdown = progress.getCountDown()
        if not countdown or self._timeProvider() <= countdown:
            if progress.getState() not in QUEST_PROGRESS_STATE.COMPLETED_STATES:
                mulCfg = progress.getParam('multiplier')
                if mulCfg:
                    task = mulCfg.get('task')
                    if task:
                        task_id, multiplier = next(task.iteritems())
                        needMultiply = self.isCompleted(task_id)
                        if needMultiply:
                            value *= multiplier
                        self._progressStorage._wasMultiplied = needMultiply
                progress += value
                if progress.getValue() >= progress.getGoal():
                    self.setCompleted(progressID, isMainProgressCompleted)
        return self.isCompleted(progressID)

    def increaseSeriesUntilComplete(self, seriesProgressID, inBattleProgressID, inBattleValue, isMainProgressCompleted=True):
        wasNotCompleted = not self.isCompleted(inBattleProgressID)
        if wasNotCompleted and self.increaseUntilComplete(inBattleProgressID, inBattleValue):
            self.increaseUntilComplete(seriesProgressID, 1, isMainProgressCompleted)
        return self.isCompleted(seriesProgressID)

    def increaseCounterUntilComplete(self, progressID, key, value, isMainProgressCompleted=True):
        progress = self._progressStorage.getProgress(progressID)
        countdown = progress.getCountDown()
        if not countdown or self._timeProvider() <= countdown:
            if progress.getState() not in QUEST_PROGRESS_STATE.COMPLETED_STATES:
                progress.addValue(key, value)
                if progress.getUniqueCount() >= progress.getUniqueGoal() and progress.getTotalCount() >= progress.getTotalGoal():
                    self.setCompleted(progressID, isMainProgressCompleted)
        return self.isCompleted(progressID)

    def increaseCounterSeriesUntilComplete(self, seriesProgressID, inBattleProgressID, inBattleKey, inBattleValue, isMainProgressCompleted=True):
        wasNotCompleted = not self.isCompleted(inBattleProgressID)
        if wasNotCompleted and self.increaseCounterUntilComplete(inBattleProgressID, inBattleKey, inBattleValue):
            self.increaseUntilComplete(seriesProgressID, 1, isMainProgressCompleted)
        return self.isCompleted(seriesProgressID)

    def checkProgressForCountdown(self):
        updated = False
        for progressID, progress in self._progressStorage.getProgresses().iteritems():
            if progress.isCumulative():
                continue
            if progress.getState() in QUEST_PROGRESS_STATE.COMPLETED_STATES + (QUEST_PROGRESS_STATE.FAILED,):
                continue
            countdown = progress.getCountDown()
            if countdown and self._timeProvider() > countdown:
                self.setFailed(progressID)
                self.setWasFailed(progressID, True)
                updated = True

        return updated

    def increaseBattleSeriesUntilCompleteOrFail(self, progressID, result, mainID=None):
        progress = self._progressStorage.getProgress(progressID)
        if mainID:
            if self.isZero(mainID):
                self.setZero(progressID)
            elif progress.getState() not in QUEST_PROGRESS_STATE.COMPLETED_STATES:
                if progress.getBattlesLimit() > len(progress.getBattles()):
                    progress.addBattle(result)
                    if progress.getSuccessfullBattles() >= progress.getGoal():
                        self.setCompleted(progressID, self.isCompleted(mainID))
                if progress.getBattlesLimit() < progress.getFailedBattles() + progress.getGoal():
                    if self.isCompleted(mainID):
                        self.setZero(progressID)
                    else:
                        self.setFailed(progressID)
        elif progress.getState() not in QUEST_PROGRESS_STATE.COMPLETED_STATES:
            if progress.getBattlesLimit() > len(progress.getBattles()):
                progress.addBattle(result)
                if progress.getSuccessfullBattles() >= progress.getGoal():
                    self.setCompleted(progressID)
            if progress.getBattlesLimit() < progress.getFailedBattles() + progress.getGoal():
                self.setWasFailed(progressID, True)
                self.setZero(progressID)
        return self.isCompleted(progressID)

    def increaseSumProgress(self, progressID, attemptsID, value, mainProgressID=None):
        progressCompleted = self.increaseUntilComplete(progressID, value)
        isMainOrMainCompleted = True if not mainProgressID else (True if self.isCompleted(mainProgressID) else False)
        if progressCompleted and not self.isFinished(attemptsID) and isMainOrMainCompleted:
            self.setCompleted(progressID)
            self.setCompleted(attemptsID)
        elif self.increaseUntilComplete(attemptsID, 1) and not self.isCompleted(progressID):
            self.setWasFailed(progressID, True)
            self.setWasFailed(attemptsID, True)
            self.setZero(progressID)
            self.setZero(attemptsID)

    def increaseEveryProgress(self, attemptsID, value, mainProgressID=None):
        if mainProgressID:
            if self.isZero(mainProgressID) or self.isCompleted(mainProgressID) and self.isFailed(attemptsID):
                self.setZero(attemptsID)
            else:
                if self.isFinished(attemptsID):
                    return
                if value:
                    self.increaseUntilComplete(attemptsID, 1)
                else:
                    self.setFailed(attemptsID)
                    if self.isCompleted(mainProgressID):
                        self.setZero(attemptsID)
        elif not self.isCompleted(attemptsID):
            if value:
                self.increaseUntilComplete(attemptsID, 1)
            else:
                self.setWasFailed(attemptsID, True)
                self.setZero(attemptsID)

    def isMultiplied(self):
        return self._progressStorage._wasMultiplied

    def setWasFailed(self, progressID, value):
        progress = self._progressStorage.getProgress(progressID)
        if progress.isAward() and progress.isMain():
            self._progressBeforeFailed = str(self._progressStorage.save())
            self._wasFailed = value

    def wasFailed(self, progressID):
        progress = self._progressStorage.getProgress(progressID)
        if progress.isAward() and progress.isMain():
            return self._wasFailed
        else:
            return False

    def getProgressBeforeFailed(self):
        return self._progressBeforeFailed

    def setWasCompleted(self, progressID, value):
        progress = self._progressStorage.getProgress(progressID)
        if progress.isAward() and progress.isMain():
            self._wasCompleted = value

    def wasCompleted(self, progressID):
        progress = self._progressStorage.getProgress(progressID)
        if progress.isAward() and progress.isMain():
            return self._wasCompleted
        else:
            return False
