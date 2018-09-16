# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/queues/LimitedThroughputQueue.py
import BigWorld

class LimitedThroughputQueue:

    def __init__(self, actionsPerSecond, maxActionsPerBatch=1):
        self.__queue = []
        self.__actionsPerSecond = actionsPerSecond
        self.__maxActionsPerBatch = maxActionsPerBatch
        self.__timerID = 0

    def scheduleAction(self, action):
        self.__queue.append(action)
        self._startJob()

    def _startJob(self):
        if self.__timerID != 0:
            return
        self.__timerID = BigWorld.addTimer(self._job, 0, 1.0 / self.__maxActionsPerBatch)

    def _stopJob(self):
        if self.__timerID == 0:
            return
        BigWorld.delTimer(self.__timerID)
        self.__timerID = 0

    def _job(self, timerID, _=0):
        for i in xrange(0, self.__actionsPerSecond / self.__maxActionsPerBatch):
            action = self.__queue.pop()
            action()
            if len(self.__queue) == 0:
                self._stopJob()
                break

    @property
    def actionsPerSecond(self):
        return self.__actionsPerSecond
