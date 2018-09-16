# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/Queue.py
from time import time as _time
try:
    import threading as _threading
except ImportError:
    import dummy_threading as _threading

from collections import deque
import heapq
__all__ = ['Empty',
 'Full',
 'Queue',
 'PriorityQueue',
 'LifoQueue']

class Empty(Exception):
    pass


class Full(Exception):
    pass


class Queue:

    def __init__(self, maxsize=0):
        self.maxsize = maxsize
        self._init(maxsize)
        self.mutex = _threading.Lock()
        self.not_empty = _threading.Condition(self.mutex)
        self.not_full = _threading.Condition(self.mutex)
        self.all_tasks_done = _threading.Condition(self.mutex)
        self.unfinished_tasks = 0

    def task_done(self):
        self.all_tasks_done.acquire()
        try:
            unfinished = self.unfinished_tasks - 1
            if unfinished <= 0:
                if unfinished < 0:
                    raise ValueError('task_done() called too many times')
                self.all_tasks_done.notify_all()
            self.unfinished_tasks = unfinished
        finally:
            self.all_tasks_done.release()

    def join(self):
        self.all_tasks_done.acquire()
        try:
            while self.unfinished_tasks:
                self.all_tasks_done.wait()

        finally:
            self.all_tasks_done.release()

    def qsize(self):
        self.mutex.acquire()
        n = self._qsize()
        self.mutex.release()
        return n

    def empty(self):
        self.mutex.acquire()
        n = not self._qsize()
        self.mutex.release()
        return n

    def full(self):
        self.mutex.acquire()
        n = 0 < self.maxsize == self._qsize()
        self.mutex.release()
        return n

    def put(self, item, block=True, timeout=None):
        self.not_full.acquire()
        try:
            if self.maxsize > 0:
                if not block:
                    if self._qsize() == self.maxsize:
                        raise Full
                elif timeout is None:
                    while self._qsize() == self.maxsize:
                        self.not_full.wait()

                elif timeout < 0:
                    raise ValueError("'timeout' must be a non-negative number")
                else:
                    endtime = _time() + timeout
                    while self._qsize() == self.maxsize:
                        remaining = endtime - _time()
                        if remaining <= 0.0:
                            raise Full
                        self.not_full.wait(remaining)

            self._put(item)
            self.unfinished_tasks += 1
            self.not_empty.notify()
        finally:
            self.not_full.release()

        return

    def put_nowait(self, item):
        return self.put(item, False)

    def get(self, block=True, timeout=None):
        self.not_empty.acquire()
        try:
            if not block:
                if not self._qsize():
                    raise Empty
            elif timeout is None:
                while not self._qsize():
                    self.not_empty.wait()

            elif timeout < 0:
                raise ValueError("'timeout' must be a non-negative number")
            else:
                endtime = _time() + timeout
                while not self._qsize():
                    remaining = endtime - _time()
                    if remaining <= 0.0:
                        raise Empty
                    self.not_empty.wait(remaining)

            item = self._get()
            self.not_full.notify()
            return item
        finally:
            self.not_empty.release()

        return

    def get_nowait(self):
        return self.get(False)

    def _init(self, maxsize):
        self.queue = deque()

    def _qsize(self, len=len):
        return len(self.queue)

    def _put(self, item):
        self.queue.append(item)

    def _get(self):
        return self.queue.popleft()


class PriorityQueue(Queue):

    def _init(self, maxsize):
        self.queue = []

    def _qsize(self, len=len):
        return len(self.queue)

    def _put(self, item, heappush=heapq.heappush):
        heappush(self.queue, item)

    def _get(self, heappop=heapq.heappop):
        return heappop(self.queue)


class LifoQueue(Queue):

    def _init(self, maxsize):
        self.queue = []

    def _qsize(self, len=len):
        return len(self.queue)

    def _put(self, item):
        self.queue.append(item)

    def _get(self):
        return self.queue.pop()
