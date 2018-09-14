# Embedded file name: scripts/client/messenger/proto/xmpp/contacts/tasks.py
from collections import defaultdict
import Event
from messenger.m_constants import PROTO_TYPE
from messenger.proto.events import g_messengerEvents
from messenger.proto.xmpp.gloox_constants import IQ_TYPE
from messenger.proto.xmpp.gloox_wrapper import ClientHolder
from messenger.proto.xmpp.log_output import CLIENT_LOG_AREA as _LOG_AREA, g_logOutput
from messenger.storage import storage_getter

class TASK_RESULT(object):
    UNDEFINED = 0
    RUNNING = 1
    CLONE = 2
    REMOVE = 4
    CLEAR = 8
    CREATE_SEQ = 16


class _Task(object):
    __slots__ = ('_result',)

    def __init__(self):
        super(_Task, self).__init__()
        self._result = TASK_RESULT.UNDEFINED

    @storage_getter('users')
    def usersStorage(self):
        return None

    def clear(self):
        self._result = TASK_RESULT.UNDEFINED

    def isRunning(self):
        return self._result & TASK_RESULT.RUNNING > 0

    def isInstantaneous(self):
        return False

    def run(self):
        raise NotImplementedError


class IQTask(_Task, ClientHolder):
    __slots__ = ('_iqID',)

    def __init__(self):
        super(IQTask, self).__init__()
        self._iqID = ''

    def clear(self):
        self._iqID = ''
        super(IQTask, self).clear()

    def getID(self):
        return self._iqID

    def setID(self, iqID):
        self._iqID = iqID

    def run(self):
        client = self.client()
        if client:
            self._doRun(client)
            if self.isInstantaneous():
                self._result = TASK_RESULT.REMOVE
            else:
                self._result = TASK_RESULT.RUNNING
        else:
            self._result = TASK_RESULT.CLEAR
        return self._result

    def handleIQ(self, iqID, iqType, pyGlooxTag):
        if iqID == self._iqID:
            if iqType == IQ_TYPE.RESULT:
                self.result(pyGlooxTag)
            elif iqType == IQ_TYPE.ERROR:
                self.error(pyGlooxTag)
        elif iqType == IQ_TYPE.SET:
            self.set(pyGlooxTag)
        return self._result

    def result(self, pyGlooxTag):
        pass

    def set(self, pyGlooxTag):
        pass

    def error(self, pyGlooxTag):
        error = self._getError(pyGlooxTag)
        if error:
            g_messengerEvents.onErrorReceived(error)
        else:
            g_logOutput.error(_LOG_AREA.PY_WRAPPER, 'Error is not resolved on the client', self.__class__.__name__, pyGlooxTag.getXml())
        self._result = TASK_RESULT.CLEAR

    def _doRun(self, client):
        raise NotImplementedError

    def _getError(self, pyGlooxTag):
        return None


class SeqTask(IQTask):

    def isRequired(self):
        return True

    def sync(self, seq):
        pass


class SeqTaskQueue(object):
    __slots__ = ('__queue', '__wait', '__others', '__multi', '__isSuspend', 'onInited')

    def __init__(self):
        super(SeqTaskQueue, self).__init__()
        self.__queue = []
        self.__wait = []
        self.__others = []
        self.__multi = []
        self.__isSuspend = False
        self.onInited = Event.Event()

    def isInited(self):
        return not self.__wait and self.__queue

    def init(self, *queue):
        self.__queue = list(queue)
        self.__wait = []
        if len(self.__queue):
            for index, task in enumerate(self.__queue):
                if not isinstance(task, SeqTask):
                    raise AssertionError('Task must be SeqTask')
                    task.isRequired() and self.__wait.append(index)
                else:
                    self.__others.append(index)

            self.__queue[0].run()

    def fini(self):
        while self.__queue:
            self.__queue.pop().clear()

        while self.__multi:
            self.__multi.pop().clear()

        self.__wait = []
        self.__others = []
        self.onInited.clear()

    def suspend(self):
        self.__isSuspend = True

    def release(self):
        if not self.__isSuspend:
            return
        self.__isSuspend = False
        if not self.__isSuspend and not self.__wait:
            self.onInited()

    def addMultiRq(self, task):
        raise isinstance(task, SeqTask) or AssertionError('Task must be SeqTask')
        self.__multi.append(task)
        task.run()

    def sync(self, index, seq):
        if index < len(self.__queue):
            task = self.__queue[index]
            task.sync(seq)
            self.__onInited(index)

    def handleIQ(self, iqID, iqType, pyGlooxTag):
        result = False
        for index, task in enumerate(self.__queue):
            if task.getID() == iqID:
                task.handleIQ(iqID, iqType, pyGlooxTag)
                result = True
                if not self.__onInited(index) and self.__others:
                    self.__queue[self.__others.pop()].run()
                break
        else:
            for index, task in enumerate(self.__multi[:]):
                if task.getID() == iqID:
                    task.handleIQ(iqID, iqType, pyGlooxTag)
                    result = True
                    self.__multi.pop(index)
                    break

        return result

    def __onInited(self, index):
        result = False
        if index not in self.__wait:
            return result
        self.__wait.remove(index)
        if not self.__wait:
            if not self.__isSuspend:
                self.onInited()
        else:
            self.__queue[self.__wait[0]].run()
            result = True
        return result


class ContactTask(IQTask):
    __slots__ = ('_jid', '_name')

    def __init__(self, jid, name = ''):
        super(ContactTask, self).__init__()
        self._jid = jid
        self._name = name

    def getJID(self):
        return self._jid

    def getContext(self):
        return -1

    def clone(self):
        return []

    def createSeqTask(self):
        return None

    def clear(self):
        self._jid = None
        self._name = ''
        super(ContactTask, self).clear()
        return

    def sync(self, name, groups, sub = None, clanInfo = None):
        self._doSync(name, groups, sub, clanInfo)
        self._result = TASK_RESULT.REMOVE
        return self._result

    def _doSync(self, name, groups = None, sub = None, clanInfo = None):
        raise NotImplementedError

    def _getUser(self, protoType = PROTO_TYPE.XMPP):
        return self.usersStorage.getUser(self._jid.getDatabaseID(), protoType)

    def _doNotify(self, actionID, user, nextRev = True):
        g_messengerEvents.users.onUserActionReceived(actionID, user)
        if nextRev:
            self.usersStorage.nextRev()


class ContactTaskQueue(object):
    __slots__ = ('__queue', '__isSuspend', '__pending', '__syncByIQ', 'onSeqTaskRequested')

    def __init__(self, syncByIQ = None):
        super(ContactTaskQueue, self).__init__()
        self.__queue = defaultdict(list)
        self.__isSuspend = False
        self.__pending = []
        self.__syncByIQ = syncByIQ or []
        self.onSeqTaskRequested = Event.Event()

    def clear(self):
        self.__isSuspend = True
        self.__pending = []
        self.onSeqTaskRequested.clear()
        while self.__queue:
            _, tasks = self.__queue.popitem()
            while tasks:
                tasks.pop().clear()

    def suspend(self):
        self.__isSuspend = True

    def release(self):
        self.__isSuspend = False
        while self.__pending:
            self.runFirstTask(self.__pending.pop())

    def addTasks(self, jid, *args):
        tasks = self.__queue[jid]
        if tasks:
            return False
        for task in args:
            raise jid == task.getJID() or AssertionError
            raise isinstance(task, ContactTask) or AssertionError('Task must be ContactTask')
            tasks.append(task)

        return True

    def removeTasks(self, jid):
        tasks = self.__queue.pop(jid, [])
        while tasks:
            tasks.pop().clear()

    def runFirstTask(self, jid):
        if self.__isSuspend:
            self.__pending.insert(0, jid)
        else:
            self._doRunFirstTask(jid)

    def sync(self, jid, name = '', groups = None, sub = None, clanInfo = None, defaultTask = None):
        if not jid.getDatabaseID():
            g_logOutput.error(_LOG_AREA.SYNC, 'JID "{0}" is invalid'.format(jid))
            return
        generator = self._getSyncGenerator(jid, name, groups, sub, clanInfo)
        if not self._handleTasksResult(jid, generator) and defaultTask:
            task = defaultTask(jid)
            task.sync(name, groups, sub, clanInfo)
            task.clear()

    def setIQ(self, iqID, jid, context):
        for task in self.__queue[jid]:
            if context == task.getContext():
                task.setID(iqID)
                break

    def handleIQ(self, iqID, iqType, pyGlooxTag):
        isHandled = False
        for jid in self.__queue.keys():
            isHandled |= self._handleTasksResult(jid, self._getIQGenerator(jid, iqID, iqType, pyGlooxTag))

        if not isHandled and iqType == IQ_TYPE.SET:
            for task in self.__syncByIQ:
                result = task.handleIQ(iqID, iqType, pyGlooxTag)
                if result in (TASK_RESULT.CLEAR, TASK_RESULT.REMOVE):
                    break
            else:
                isHandled = True

        return isHandled

    def _getIQGenerator(self, jid, iqID, iqType, pyGlooxTag):
        for task in self.__queue[jid][:]:
            yield (task.handleIQ(iqID, iqType, pyGlooxTag), task)

    def _getSyncGenerator(self, jid, name, groups, sub, clanInfo):
        for task in self.__queue[jid][:]:
            yield (task.sync(name, groups, sub, clanInfo), task)

    def _doRunFirstTask(self, jid):
        tasks = self.__queue[jid]
        newTasks = []
        for task in tasks:
            if task.isRunning():
                return
            result = task.run()
            if result & TASK_RESULT.CLEAR > 0:
                self.removeTasks(jid)
                return
            if result & TASK_RESULT.CLONE > 0:
                newTasks.extend(task.clone())
            if result & TASK_RESULT.REMOVE > 0:
                task.clear()
                tasks.remove(task)
                continue
            if task.isRunning():
                break

        if newTasks:
            toRun = set()
            for task in newTasks:
                jid = task.getJID()
                toRun.add(jid)
                self.__queue[jid].append(task)

            for jid in toRun:
                self._doRunFirstTask(jid)

    def _handleTasksResult(self, jid, generator):
        tasks = self.__queue[jid]
        toRun = set()
        isHandled = False
        for result, task in generator:
            isHandled = True
            if result == TASK_RESULT.UNDEFINED:
                if not task.isRunning():
                    toRun.add(task.getJID())
                continue
            if result & TASK_RESULT.CREATE_SEQ > 0:
                seqTask = task.createSeqTask()
                if seqTask:
                    self.onSeqTaskRequested(seqTask)
            if result & TASK_RESULT.CLONE > 0:
                for newTask in task.clone():
                    nextJID = newTask.getJID()
                    toRun.add(nextJID)
                    self.__queue[nextJID].append(newTask)

            if result & TASK_RESULT.REMOVE > 0:
                task.clear()
                tasks.remove(task)
            if result & TASK_RESULT.CLEAR > 0:
                toRun.discard(jid)
                self.removeTasks(jid)
                break

        for jid in toRun:
            self._doRunFirstTask(jid)

        return isHandled
