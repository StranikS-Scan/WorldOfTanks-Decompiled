# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/server_events/personal_progress/storage.py
import typing
import quest_progress
from gui.server_events.personal_progress import builders
from gui.server_events.personal_progress import collectors
from gui.server_events.personal_progress import visitors
from personal_missions_constants import VISIBLE_SCOPE, CONTAINER

class ClientProgressStorage(quest_progress.ProgressStorage):

    def __init__(self, generalQuestID, questCfg, savedProgresses):
        super(ClientProgressStorage, self).__init__(questCfg, savedProgresses)
        wrappersVisitors = self._getMetricsVisitors()
        progresses = self.getProgresses()
        for progress in progresses.itervalues():
            progress.markAsVisited()
            progress.postProcess(progresses)
            if progress.getContainerType() == CONTAINER.BODY:
                progress.setGeneralQuestID(generalQuestID)
                progress.acceptWrappersVisitors(wrappersVisitors)

    def _createProgress(self, progressID, configData):
        progress = super(ClientProgressStorage, self)._createProgress(progressID, configData)
        if progress.getContainerType() == CONTAINER.HEADER:
            progress.setCurrentScope(self._getCurrentScope())
        return progress

    def update(self, progressesInfo):
        if progressesInfo is not None:
            super(ClientProgressStorage, self).update(progressesInfo)
        return

    @classmethod
    def _getBuilders(cls):
        return (builders.BinaryProgressBuilder,
         builders.ValueProgressBuilder,
         builders.VehicleTypesProgressBuilder,
         builders.BiathlonProgressBuilder)

    def getHeaderProgresses(self):
        raise NotImplementedError

    def getBodyProgresses(self):
        raise NotImplementedError

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
         visitors.CounterProgressVisitor,
         visitors.TimerProgressVisitor,
         visitors.LimiterProgressVisitor)

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
