# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/helpers/threads.py
import time
import weakref
import threading
from Queue import Queue, Empty as QueueEmptyError
from debug_utils import LOG_ERROR, LOG_DEBUG, LOG_CURRENT_EXCEPTION

class Job(object):

    def doWork(self, worker):
        raise NotImplementedError


class TerminateJob(Job):

    def doWork(self, worker):
        worker.terminate()


class Worker(threading.Thread):

    def __init__(self, jobsQueue, name=None):
        super(Worker, self).__init__(name=name)
        self.__queueRef = weakref.ref(jobsQueue)
        self._terminated = False

    def __del__(self):
        LOG_DEBUG('Worker has been deleted', self)

    def terminate(self):
        self._terminated = True

    def run(self):
        while not self._terminated:
            try:
                queue = self.__queueRef()
                if queue is not None:
                    job = queue.get()
                    job.doWork(self)
                    queue.task_done()
                else:
                    self.terminate()
                    break
                time.sleep(0.001)
            except Exception:
                LOG_CURRENT_EXCEPTION()

        return

    def __repr__(self):
        return '%s(name = %s)' % (self.__class__.__name__, self.name) if not self._terminated else '%s(terminated)' % self.__class__.__name__


class ThreadPool(object):

    def __init__(self, workersLimit, queueLimit=-1):
        self._jobs = Queue(queueLimit)
        self._running = False
        self._workers = []
        self._workersLimit = workersLimit

    def start(self):
        for _ in xrange(self._workersLimit):
            worker = self._createNewWorker()
            try:
                worker.start()
            except Exception:
                LOG_ERROR('Worker has not been started properly', worker)
            else:
                self._workers.append(worker)

        self._running = True

    def stop(self):
        self._running = False
        try:
            while True:
                self._jobs.get_nowait()

        except QueueEmptyError:
            pass

        for _ in self._workers:
            self._jobs.put_nowait(TerminateJob())

        self._workers = []

    def _createNewWorker(self):
        return Worker(self._jobs)

    def putJob(self, job):
        if not self._running:
            LOG_ERROR('Thread pool is not running. Trying to put new job', job)
            return
        self._jobs.put_nowait(job)

    def __repr__(self):
        return '%s(workers = %d; jobs = %d)' % (self.__class__.__name__, len(self._workers), self._jobs.qsize())
