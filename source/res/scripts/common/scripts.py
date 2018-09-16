# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/scripts.py
import weakref
import sys
from functools import partial
from debug_utils import *
from soft_exception import SoftException

class TASK_STATUS():
    RUNNING = 0
    SUCCESS = 1
    FAIL = 2


class SCRIPT_STATUS():
    IDLE = 1
    RUNNING = 2
    DONE = 3


_MAX_TASKS = 50

def _isscript(obj):
    return hasattr(obj, '__iter__')


def _createScriptRoutine(fn, *args, **kwargs):

    def generator():
        routine = fn(*args, **kwargs)
        if not _isscript(routine):
            return
        try:
            value = next(routine)
            while True:
                result = yield value
                value = routine.send(result)

        except StopIteration:
            return

    return generator()


class ScriptInterrupt(SoftException):

    def __init__(self, handler):
        self.handler = handler


class Script(object):

    def __init__(self):
        self.driver = None
        self.status = SCRIPT_STATUS.IDLE
        return

    def destroy(self):
        self.driver = None
        self.status = SCRIPT_STATUS.DONE
        return

    def step(self, result):
        return None

    def completeTask(self, task, cancel):
        pass

    def beginInterrupt(self, interrupt):
        pass

    def endInterrupt(self):
        pass

    def continueAfterInterrupt(self):
        return None

    def callback(self, callback, *args, **kwargs):
        pass


class RemoteScript(Script):

    def __init__(self):
        super(RemoteScript, self).__init__()
        self.__interruptLevel = 0
        self.__requiredInterruptLevel = 0
        self.__pendingTasks = None
        self.__waitTaskIDs = None
        self.__cancelTaskIDs = None
        self.__waitResponseTask = None
        self.__tasks = {}
        return

    def destroy(self):
        self.__tasks = None
        super(RemoteScript, self).destroy()
        return

    def step(self, result):
        if self.__interruptLevel > self.__requiredInterruptLevel:
            self.status = SCRIPT_STATUS.DONE
            return
        elif self.__pendingTasks is not None:
            return self.__executeTasks()
        else:
            self.__interrupt(self.__requestTasks, result)
            return

    def beginInterrupt(self, interrupt):
        self.__interruptLevel += 1
        interrupt.handler()

    def endInterrupt(self):
        self.__interruptLevel -= 1
        self.status = SCRIPT_STATUS.IDLE

    def continueAfterInterrupt(self):
        if self.__interruptLevel == self.__requiredInterruptLevel:
            return self.__executeTasks()
        else:
            return None
            return None

    def callback(self, callback, *args, **kwargs):
        self.__interrupt(self.__invokeCallback, callback, *args, **kwargs)

    def completeTask(self, task, cancel):
        taskID = getattr(task, 'taskID', -1)
        if taskID != -1:
            del self.__tasks[task.taskID]

    def restore(self, backup):
        if self.__waitResponseTask:
            return
        tasks, waitTasksIDs, cancelTasksIDs, interrupt, waiting = self._restore(backup)
        self.__pendingTasks = tasks
        self.__waitTaskIDs = waitTasksIDs
        self.__cancelTaskIDs = cancelTasksIDs
        waitTasks = self.__executeTasks()
        self.driver.waitTasks(waitTasks)
        if interrupt:
            self.__requiredInterruptLevel += 1
            raise ScriptInterrupt(lambda : None)
        if waiting:
            self.__interrupt(self.__waitResponse)

    def _executeTask(self, taskID, typeID, args):
        raise NotImplementedError

    def _invokeCallback(self, taskID, args):
        raise NotImplementedError

    def _requestTasks(self, results):
        raise NotImplementedError

    def _receiveTasks(self, interruptLevel, tasks, waitTasks, cancelTasks):
        self.__pendingTasks = tasks
        self.__waitTaskIDs = waitTasks
        self.__cancelTaskIDs = cancelTasks
        self.__waitResponseTask.complete()
        self.__waitResponseTask = None
        self.__requiredInterruptLevel = interruptLevel
        LOG_DEBUG_DEV('[SCRIPT] received tasks', interruptLevel, self.__interruptLevel, tasks, waitTasks, cancelTasks)
        return

    def _restore(self, backup):
        raise NotImplementedError

    def __interrupt(self, handler, *args, **kwargs):
        raise ScriptInterrupt(partial(handler, *args, **kwargs))

    def __executeTasks(self):
        tasks = self.__tasks
        for taskID in self.__cancelTaskIDs:
            task = tasks.pop(taskID, None)
            if task:
                self.driver.cancelTask(task)

        for taskID, typeID, args in self.__pendingTasks:
            task = self._executeTask(taskID, typeID, args)
            task.taskID = taskID
            tasks[taskID] = task

        waitTasks = []
        if self.__waitTaskIDs:
            for taskID in self.__waitTaskIDs:
                waitTasks.append(tasks[taskID])

        self.__pendingTasks = None
        self.__waitTaskIDs = None
        self.__cancelTaskIDs = None
        return waitTasks

    def __requestTasks(self, results):
        self.__waitResponse()
        self._requestTasks(results)

    def __invokeCallback(self, callbackID, *args, **kwargs):
        self.__waitResponse()
        self._invokeCallback(callbackID, args)

    def __waitResponse(self):
        task = self.__waitResponseTask = self.driver.addTask(_WaitCompletionTask())
        task.taskID = -1
        self.driver.waitTasks((task,))
        return task


class RemoteScriptController(object):

    def __init__(self, script):
        self.__script = script
        self.__interruptLevel = 0
        self.__tasks = []
        self.__cancelledTasks = []
        self.__callbacks = {}
        self.__taskID = 0

    def destroy(self):
        self.__script.destroy()
        self.__callbacks = None
        self.__script = None
        return

    def addTask(self, typeID, *args, **kwargs):
        self.__taskID += 1
        taskID = self.__taskID
        callback = kwargs.get('callback')
        if callback:
            self.__registerCallback(taskID, callback)
            args += (taskID,)
        task = [taskID, typeID, args]
        self.__tasks.append(task)
        return task

    def cancelTask(self, task):
        taskID = task[0]
        self.__cancelledTasks.append(taskID)

    def _step(self, results):
        waitTasks = self.__script.step(results)
        if self.__script.status == SCRIPT_STATUS.DONE:
            self.__script.endInterrupt()
            self.__interruptLevel -= 1
            waitTasks = self.__script.continueAfterInterrupt()
        self.__sendTasks(self.__interruptLevel, waitTasks)

    def _sendTasks(self, interruptLevel, tasks, waitTasks, cancelTasks):
        raise NotImplementedError

    def _callback(self, taskID, args):
        callback = self.__callbacks[taskID]
        waitTasks = None
        try:
            self.__script.callback(callback, *args)
        except ScriptInterrupt as e:
            self.__script.beginInterrupt(e)
            self.__interruptLevel += 1
            waitTasks = self.__script.step(None)

        if self.__tasks:
            self.__sendTasks(self.__interruptLevel, waitTasks)
        return

    def __sendTasks(self, interruptLevel, waitTasks):
        tasks = []
        for task in self.__tasks:
            taskID, typeID, args = task
            tasks.append((taskID, typeID, args))

        waitTasks = map(lambda task: task[0], waitTasks) if waitTasks is not None else []
        self._sendTasks(interruptLevel, tasks, waitTasks, self.__cancelledTasks)
        self.__tasks = []
        self.__cancelledTasks = []
        return

    def __registerCallback(self, taskID, callback):
        self.__callbacks[taskID] = callback
        return taskID


def _isExceptionInfo(value):
    try:
        return isinstance(value, tuple) and len(value) == 3 and issubclass(value[0], BaseException) and isinstance(value[1], BaseException) and isinstance(value[1], value[0])
    except TypeError:
        return False


class LocalScript(Script):

    def __init__(self, entryPoint, *args, **kwargs):
        super(LocalScript, self).__init__()
        if kwargs.pop('isScriptRoutine', False):
            self.__routine = entryPoint(*args, **kwargs)
        else:
            self.__routine = _createScriptRoutine(entryPoint, *args, **kwargs)
        self.__interruptedRoutines = []

    def destroy(self):
        self.__interruptedRoutines = None
        self.__routine = None
        super(LocalScript, self).destroy()
        return

    def step(self, results):
        waitingTasks = None
        try:
            if results:
                results = results[0] if len(results) == 1 else tuple(results)
                if _isExceptionInfo(results):
                    waitingTasks = self.__routine.throw(*results)
                else:
                    waitingTasks = self.__routine.send(results)
            else:
                waitingTasks = next(self.__routine)
            if waitingTasks is not None and not isinstance(waitingTasks, tuple):
                waitingTasks = (waitingTasks,)
        except StopIteration:
            self.status = SCRIPT_STATUS.DONE

        return waitingTasks

    def beginInterrupt(self, interrupt):
        self.__interruptedRoutines.append(self.__routine)
        self.__routine = interrupt.handler

    def endInterrupt(self):
        self.__routine = self.__interruptedRoutines.pop()
        self.status = SCRIPT_STATUS.IDLE

    def callback(self, callback, *args, **kwargs):
        routine = callback(*args, **kwargs)
        if _isscript(routine):
            raise ScriptInterrupt(routine)


class ScriptDriver(object):

    def __init__(self, script):
        self.__suspended = False
        self.__script = script
        self.__tasks = []
        self.__waitingTasks = set()
        self.__waitResults = []
        self.__namedTasks = {}
        self.__taggedTasks = {}
        self.__cancelledTasks = set()
        self.__blockedTasks = {}
        self.__interruptDriver = None
        script.driver = self
        return

    def destroy(self):
        if self.__interruptDriver:
            self.__interruptDriver.destroy()
            self.__interruptDriver = None
        self.__suspended = True
        for task in self.__tasks:
            task.destroy()

        self.__blockedTasks = None
        self.__cancelledTasks = None
        self.__taggedTasks = None
        self.__namedTasks = None
        self.__waitingTasks = None
        self.__tasks = None
        if self.__script:
            self.__script.destroy()
            self.__script = None
        return

    def detachScript(self):
        self.__script.driver = None
        self.__script = None
        return

    def __processTasks(self):
        tasks = self.__tasks
        cancelledTasks = self.__cancelledTasks
        cancelledTasks.clear()
        exc_info = None
        for task in list(tasks):
            if task.predecessors or task in cancelledTasks:
                continue
            process = task.process
            try:
                status = process()
            except ScriptInterrupt:
                raise
            except BaseException:
                status = TASK_STATUS.RUNNING
                exc_info = sys.exc_info()

            if status == TASK_STATUS.SUCCESS:
                self.__removeTask(task, False)

        if exc_info:
            for task in list(tasks):
                self.__removeTask(task, True)

            self.__waitResults = exc_info
        cancelledTasks.clear()
        return

    def beginInterrupt(self, interrupt):
        self.__beginInterrupt(interrupt)

    def __beginInterrupt(self, interrupt):
        self.suspend()
        self.__interruptDriver = ScriptDriver(self.__script)
        self.__script.beginInterrupt(interrupt)

    def __endInterrupt(self):
        script = self.__script
        interruptDriver = self.__interruptDriver
        script.endInterrupt()
        interruptDriver.detachScript()
        interruptDriver.destroy()
        self.__interruptDriver = None
        script.driver = self
        self.resume()
        waitTasks = script.continueAfterInterrupt()
        if waitTasks:
            self.waitTasks(waitTasks)
        return

    def run(self):
        while True:
            if self.__interruptDriver is not None:
                done = self.__interruptDriver.run()
                if not done:
                    return False
                self.__endInterrupt()
            scriptStatus = self.__script.status
            if scriptStatus == SCRIPT_STATUS.RUNNING:
                return False
            if scriptStatus == SCRIPT_STATUS.DONE:
                return True
            try:
                self.__processTasks()
                if not self.__waitingTasks:
                    waitResults = self.__waitResults
                    self.__waitResults = None
                    waitingTasks = self.__script.step(waitResults)
                    if waitingTasks is None:
                        waitingTasks = self.__tasks
                    if waitingTasks:
                        self.waitTasks(waitingTasks)
                    scriptStatus = self.__script.status
                return scriptStatus == SCRIPT_STATUS.DONE
            except ScriptInterrupt as e:
                self.__beginInterrupt(e)

        return

    def restore(self, backup):
        try:
            self.__script.restore(backup)
        except ScriptInterrupt as e:
            self.__beginInterrupt(e)
            self.__interruptDriver.restore(backup)

    def addTask(self, task, name=None, parent=None, predecessors=None):
        if self.__interruptDriver:
            return self.__interruptDriver.addTask(task, name=name, parent=parent, predecessors=predecessors)
        else:
            tasks = self.__tasks
            task.name = name
            task.waitOrder = None
            if parent is not None:
                parent.addSubtask(task)
            taskPredecessors = set()
            task.predecessors = taskPredecessors
            if predecessors:
                for predecessor in predecessors:
                    if predecessor in tasks:
                        taskPredecessors.add(predecessor)

            if len(tasks) >= _MAX_TASKS:
                LOG_WARNING('[SCRIPT] task dropped because of exceeded limit', task, tasks)
                return
            if taskPredecessors:
                blockedTasks = self.__blockedTasks
                for predecessor in taskPredecessors:
                    blockedTasks.setdefault(predecessor, []).append(task)

            tasks.append(task)
            if not taskPredecessors:
                self.__registerActiveTask(task)
            return task

    def waitTasks(self, tasks):
        if self.__interruptDriver:
            self.__interruptDriver.waitTasks(tasks)
            return
        else:
            waitingTasks = self.__waitingTasks
            for waitOrder, task in enumerate(tasks):
                if task is not None:
                    task.waitOrder = waitOrder
                    waitingTasks.add(task)

            self.__waitResults = [None] * len(tasks)
            return

    def lookupTask(self, name):
        return self.__interruptDriver.lookupTask(name) if self.__interruptDriver else self.__namedTasks.get(name, None)

    def __registerActiveTask(self, task):
        name = task.name
        tags = task.tags
        retry = True
        while retry:
            retry = False
            if name is not None:
                prevTask = self.__namedTasks.get(name, None)
                if prevTask is not None:
                    LOG_DEBUG_DEV('[SCRIPT] detected conflicting tasks by name', task, prevTask, name)
                    self.cancelTask(prevTask)
                    retry = True
            if tags:
                for tag in tags:
                    prevTask = self.__taggedTasks.get(tag, None)
                    if prevTask:
                        LOG_DEBUG_DEV('[SCRIPT] detected conflicting tasks by tag', task, prevTask, tag)
                        self.cancelTask(prevTask)
                        retry = True

        if name is not None:
            self.__namedTasks[name] = task
        if tags:
            for tag in tags:
                self.__taggedTasks[tag] = task

        return

    def __removeTask(self, task, cancel):
        if task not in self.__tasks:
            return False
        else:
            while task.subtasks:
                subtask = task.subtasks[0]
                self.cancelTask(subtask)

            if task.parent:
                task.parent.removeSubtask(task)
                task.parent = None
            waitOrder = task.waitOrder
            if waitOrder is not None:
                self.__waitResults[waitOrder] = task.result
            self.__script.completeTask(task, cancel)
            self.__tasks.remove(task)
            self.__waitingTasks.discard(task)
            blockedTasks = self.__blockedTasks
            if not task.predecessors:
                if task.name is not None:
                    del self.__namedTasks[task.name]
                if task.tags:
                    taggedTasks = self.__taggedTasks
                    for tag in task.tags:
                        taggedTasks.pop(tag, None)

            else:
                for predecessor in task.predecessors:
                    blockedTasks[predecessor].remove(task)

            if task in blockedTasks:
                for blockedTask in blockedTasks[task]:
                    predecessors = blockedTask.predecessors
                    predecessors.remove(task)
                    if not predecessors:
                        self.__registerActiveTask(blockedTask)

                del blockedTasks[task]
            task.suspend(cancel)
            task.destroy()
            return True

    def cancelTask(self, task):
        if self.__interruptDriver:
            self.__interruptDriver.cancelTask(task)
            return
        if self.__removeTask(task, True):
            self.__cancelledTasks.add(task)

    def suspend(self):
        if self.__interruptDriver:
            self.__interruptDriver.suspend()
            return
        for task in self.__tasks:
            task.suspend(False)

        self.__suspended = True

    def resume(self):
        if self.__interruptDriver:
            self.__interruptDriver.resume()
            return
        for task in self.__tasks:
            task.resume()

        self.__suspended = False


class ScriptTask(object):

    def __init__(self, tags=None):
        self.result = None
        self.tags = tags
        self.subtasks = []
        self.parent = None
        return

    def destroy(self):
        self.parent = None
        self.subtasks = None
        return

    def addSubtask(self, task):
        task.parent = weakref.proxy(self)
        self.subtasks.append(task)

    def removeSubtask(self, task):
        self.subtasks.remove(task)

    def process(self):
        raise SoftException('Task must implement process method')

    def suspend(self, cancel):
        pass

    def resume(self):
        pass


class SimpleScriptTask(ScriptTask):

    def __init__(self, routine, tags=None):
        ScriptTask.__init__(self, tags)
        self.__routine = routine

    def process(self):
        self.result = self.__routine()
        return TASK_STATUS.SUCCESS


class _WaitCompletionTask(ScriptTask):

    def __init__(self):
        ScriptTask.__init__(self)
        self.__waiting = True

    def process(self):
        return TASK_STATUS.RUNNING if self.__waiting else TASK_STATUS.SUCCESS

    def complete(self):
        self.__waiting = False
