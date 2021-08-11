# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/helpers/threads.py
import logging
import time
import weakref
import threading
from Queue import PriorityQueue, Empty as QueueEmptyError
_logger = logging.getLogger(__name__)
INFINITE_QUEUE_SIZE = 0
_LOW_PRIORITY = 10
_DEFAULT_PRIORITY = 1

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
        _logger.debug('Worker has been deleted: %s', self)

    def terminate(self):
        self._terminated = True

    def run(self):
        while not self._terminated:
            try:
                queue = self.__queueRef()
                if queue is not None:
                    _, job = queue.get()
                    job.doWork(self)
                    queue.task_done()
                else:
                    self.terminate()
                    break
                time.sleep(0.001)
            except Exception:
                _logger.exception('Exception raises in Worker: %r', self)

        return

    def __repr__(self):
        return '%s(name = %s)' % (self.__class__.__name__, self.name) if not self._terminated else '%s(terminated)' % self.__class__.__name__


class ThreadPool(object):

    def __init__(self, workersLimit, queueLimit=-1):
        self._jobs = PriorityQueue(queueLimit)
        self._running = False
        self._workers = []
        self._workersLimit = workersLimit

    def start(self):
        for _ in xrange(self._workersLimit):
            worker = self._createNewWorker()
            try:
                worker.start()
            except Exception:
                _logger.error('Worker has not been started properly: %r', worker)
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
            self._jobs.put_nowait((_LOW_PRIORITY, TerminateJob()))

        self._workers = []

    def _createNewWorker(self):
        return Worker(self._jobs)

    def putLowPriorityJob(self, job):
        if not self._running:
            _logger.error('Thread pool is not running. Trying to put new job: %r', job)
            return
        self._jobs.put_nowait((_LOW_PRIORITY, job))

    def putJob(self, job):
        if not self._running:
            _logger.error('Thread pool is not running. Trying to put new job: %r', job)
            return
        self._jobs.put_nowait((_DEFAULT_PRIORITY, job))

    def __repr__(self):
        return '%s(workers = %d; jobs = %d)' % (self.__class__.__name__, len(self._workers), self._jobs.qsize())
