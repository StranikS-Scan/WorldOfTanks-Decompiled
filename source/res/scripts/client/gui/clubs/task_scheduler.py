# Embedded file name: scripts/client/gui/clubs/task_scheduler.py
import BigWorld
from helpers import time_utils

class TaskScheduler(object):

    def __init__(self, *args, **kwargs):
        super(TaskScheduler, self).__init__()
        self.__tasks = {}
        self.__queue = []
        self.__bwCbId = None
        self.__isStarted = False
        return

    def __del__(self):
        self.cancelAllTasks()

    def scheduleTask(self, task):
        if TaskScheduler.isTaskValid(task) and time_utils.isFuture(task.getTime()):
            if self.__bwCbId is not None:
                schTask = self.__queue[0]
                if task.getId() == schTask.getId() or task.getTime() < schTask.getTime():
                    self._cancelBigWorldCb()
            self._addTask(task)
            self._processQueue()
        return

    def cancelTask(self, taskId):
        if taskId is not None and taskId in self.__tasks:
            schTask = self.__queue[0]
            if self.__bwCbId is not None and taskId == schTask.getId():
                self._cancelBigWorldCb()
            self._removeTask(taskId)
            self._processQueue()
        return

    def cancelAllTasks(self):
        if self.__bwCbId is not None:
            self._cancelBigWorldCb()
        self.__tasks = {}
        self.__queue = []
        return

    def getTask(self, taskId):
        return self.__tasks.get(taskId, None)

    def isStarted(self):
        return self.__isStarted

    def start(self):
        if self.__isStarted is False:
            self.__isStarted = True
            self._processQueue()

    def stop(self):
        if self.__isStarted is True:
            self._cancelBigWorldCb()
            self.__isStarted = False

    def _processQueue(self):
        if self.__isStarted is False:
            return
        else:
            if self.__bwCbId is None:
                while len(self.__queue):
                    task = self.__queue[0]
                    delta = time_utils.getTimeDeltaFromNow(task.getTime())
                    if delta > 0:
                        self._registerBigWorldCb(delta)
                        break
                    else:
                        self._removeTask(task.getId())
                        task.execute()

            return

    def _addTask(self, task):
        storedTask = self.getTask(task.getId())
        if storedTask is not None:
            self.__queue.remove(storedTask)
        self.__tasks[task.getId()] = task
        self.__queue.append(task)
        self.__queue.sort(key=lambda tsk: tsk.getTime())
        return

    def _removeTask(self, taskId):
        task = self.__tasks.pop(taskId, None)
        if task is not None:
            self.__queue.remove(task)
        return

    def _cancelBigWorldCb(self):
        BigWorld.cancelCallback(self.__bwCbId)
        self.__bwCbId = None
        return

    def _registerBigWorldCb(self, delta):
        self.__bwCbId = BigWorld.callback(delta, self._onBigWorldCb)

    def _onBigWorldCb(self):
        schTask = self.__queue[0]
        self.__bwCbId = None
        self._removeTask(schTask.getId())
        schTask.execute()
        self._processQueue()
        return

    @classmethod
    def isTaskValid(cls, task):
        return task is not None and task.getId() is not None and task.getTime() is not None and task.getCallback() is not None


class Task(object):

    def __init__(self, taskId, time, cb, extraData):
        super(Task, self).__init__()
        self._id = taskId
        self._cb = cb
        self._time = time
        self._extraData = extraData

    def getId(self):
        return self._id

    def getTime(self):
        return self._time

    def getCallback(self):
        return self._cb

    def getExtraData(self):
        return self._extraData

    def execute(self):
        self._cb(self._id, self._extraData)
