# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/server_events/personal_progress/storage.py
import typing
import quest_progress
from gui.server_events.personal_progress import builders
from gui.server_events.personal_progress import collectors
from gui.server_events.personal_progress import visitors
from personal_missions_constants import VISIBLE_SCOPE, CONTAINER

class ClientProgressStorage(quest_progress.ProgressStorage):

    def __init__(self, generalQuestID, questCfg, savedProgresses, hasLockedProgresses):
        self._hasLockedProgresses = hasLockedProgresses
        super(ClientProgressStorage, self).__init__(questCfg, savedProgresses)
        wrappersVisitors = self._getMetricsVisitors()
        progresses = self.getProgresses()
        for progress in progresses.itervalues():
            progress.markAsVisited()
            progress.postProcess(progresses)
            if progress.getContainerType() == CONTAINER.BODY:
                progress.setGeneralQuestID(generalQuestID)
                progress.acceptWrappersVisitors(wrappersVisitors)

        self._updateLocks()

    def update(self, progressesInfo):
        if progressesInfo is not None:
            super(ClientProgressStorage, self).update(progressesInfo)
            self._updateLocks()
        return

    def getHeaderProgresses(self, isMain=None):
        raise NotImplementedError

    def getBodyProgresses(self, isMain=None):
        raise NotImplementedError

    def _createProgress(self, progressID, configData):
        progress = super(ClientProgressStorage, self)._createProgress(progressID, configData)
        if progress.getContainerType() == CONTAINER.HEADER:
            progress.setCurrentScope(self._getCurrentScope())
        return progress

    def _updateLocks(self):
        if self._hasLockedProgresses:
            for addProgress in self.getBodyProgresses(isMain=False).itervalues():
                addProgress.setLocked(not addProgress.isCompleted())

    @classmethod
    def _getBuilders(cls):
        return (builders.BinaryProgressBuilder,
         builders.ValueProgressBuilder,
         builders.VehicleTypesProgressBuilder,
         builders.BiathlonProgressBuilder)

    @classmethod
    def _getMetricsVisitors(cls):
        raise NotImplementedError

    @classmethod
    def _getCurrentScope(cls):
        raise NotImplementedError


class LobbyProgressStorage(ClientProgressStorage):

    def getBodyProgresses(self, isMain=None):
        return self._collectProgressInfo(collectors.LobbyBodyProgressCollector(isMain))

    def getHeaderProgresses(self, isMain=None):
        return self._collectProgressInfo(collectors.LobbyHeaderProgressCollector(isMain))

    def markAsCompleted(self, isCompleted, isFullCompleted):
        for progress in self.getProgresses().itervalues():
            completed = isCompleted if progress.isMain() else isFullCompleted
            if completed:
                progress.markAsCompleted()

        self._updateLocks()

    @classmethod
    def _getMetricsVisitors(cls):
        return (visitors.LobbyValueProgressVisitor, visitors.LimiterProgressVisitor)

    @classmethod
    def _getCurrentScope(cls):
        return VISIBLE_SCOPE.HANGAR


class PostBattleProgressStorage(LobbyProgressStorage):

    @classmethod
    def _getMetricsVisitors(cls):
        pass


class BattleProgressStorage(ClientProgressStorage):

    @classmethod
    def _getMetricsVisitors(cls):
        return (visitors.BinaryProgressVisitor,
         visitors.ValueProgressVisitor,
         visitors.ValueLikeBinaryProgressVisitor,
         visitors.CounterProgressVisitor,
         visitors.TimerProgressVisitor,
         visitors.LimiterProgressVisitor)

    def _updateLocks(self):
        if self._hasLockedProgresses:
            unrelatedProgressCompletion = []
            orRelatedProgressCompletion = []
            for progress in self.getBodyProgresses(isMain=True).itervalues():
                if progress.isInOrGroup():
                    orRelatedProgressCompletion.append(progress.isCompleted())
                unrelatedProgressCompletion.append(progress.isCompleted())

            areAllUnrelatedProgressesCompleted = all(unrelatedProgressCompletion)
            if orRelatedProgressCompletion:
                isAddSecctionUnlocked = areAllUnrelatedProgressesCompleted and any(orRelatedProgressCompletion)
            else:
                isAddSecctionUnlocked = areAllUnrelatedProgressesCompleted
            for addProgress in self.getBodyProgresses(isMain=False).itervalues():
                addProgress.setLocked(not isAddSecctionUnlocked)

    def getHeaderProgresses(self, isMain=None):
        return self._collectProgressInfo(collectors.BattleHeaderProgressCollector(isMain))

    def getBodyProgresses(self, isMain=None):
        return self._collectProgressInfo(collectors.BattleBodyProgressCollector(isMain))

    def getTimerConditions(self):
        return self._collectProgressInfo(collectors.ProgressWithTimerCollector())

    def getChangedConditions(self):
        return self._collectProgressInfo(collectors.ChangedProgressCollector())

    @classmethod
    def _getCurrentScope(cls):
        return VISIBLE_SCOPE.BATTLE
