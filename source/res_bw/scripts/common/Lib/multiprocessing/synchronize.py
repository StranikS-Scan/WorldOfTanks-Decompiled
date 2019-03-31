# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/multiprocessing/synchronize.py
# Compiled at: 2010-08-25 17:58:21
__all__ = ['Lock',
 'RLock',
 'Semaphore',
 'BoundedSemaphore',
 'Condition',
 'Event']
import threading
import os
import sys
from time import time as _time, sleep as _sleep
import _multiprocessing
from multiprocessing.process import current_process
from multiprocessing.util import Finalize, register_after_fork, debug
from multiprocessing.forking import assert_spawning, Popen
try:
    from _multiprocessing import SemLock
except ImportError:
    raise ImportError('This platform lacks a functioning sem_open' + ' implementation, therefore, the required' + ' synchronization primitives needed will not' + ' function, see issue 3770.')

RECURSIVE_MUTEX, SEMAPHORE = range(2)
SEM_VALUE_MAX = _multiprocessing.SemLock.SEM_VALUE_MAX

class SemLock(object):

    def __init__(self, kind, value, maxvalue):
        sl = self._semlock = _multiprocessing.SemLock(kind, value, maxvalue)
        debug('created semlock with handle %s' % sl.handle)
        self._make_methods()
        if sys.platform != 'win32':

            def _after_fork(obj):
                obj._semlock._after_fork()

            register_after_fork(self, _after_fork)

    def _make_methods(self):
        self.acquire = self._semlock.acquire
        self.release = self._semlock.release
        self.__enter__ = self._semlock.__enter__
        self.__exit__ = self._semlock.__exit__

    def __getstate__(self):
        assert_spawning(self)
        sl = self._semlock
        return (Popen.duplicate_for_child(sl.handle), sl.kind, sl.maxvalue)

    def __setstate__(self, state):
        self._semlock = _multiprocessing.SemLock._rebuild(*state)
        debug('recreated blocker with handle %r' % state[0])
        self._make_methods()


class Semaphore(SemLock):

    def __init__(self, value=1):
        SemLock.__init__(self, SEMAPHORE, value, SEM_VALUE_MAX)

    def get_value(self):
        return self._semlock._get_value()

    def __repr__(self):
        try:
            value = self._semlock._get_value()
        except Exception:
            value = 'unknown'

        return '<Semaphore(value=%s)>' % value


class BoundedSemaphore(Semaphore):

    def __init__(self, value=1):
        SemLock.__init__(self, SEMAPHORE, value, value)

    def __repr__(self):
        try:
            value = self._semlock._get_value()
        except Exception:
            value = 'unknown'

        return '<BoundedSemaphore(value=%s, maxvalue=%s)>' % (value, self._semlock.maxvalue)


class Lock(SemLock):

    def __init__(self):
        SemLock.__init__(self, SEMAPHORE, 1, 1)

    def __repr__(self):
        try:
            if self._semlock._is_mine():
                name = current_process().name
                if threading.current_thread().name != 'MainThread':
                    name += '|' + threading.current_thread().name
            elif self._semlock._get_value() == 1:
                name = 'None'
            elif self._semlock._count() > 0:
                name = 'SomeOtherThread'
            else:
                name = 'SomeOtherProcess'
        except Exception:
            name = 'unknown'

        return '<Lock(owner=%s)>' % name


class RLock(SemLock):

    def __init__(self):
        SemLock.__init__(self, RECURSIVE_MUTEX, 1, 1)

    def __repr__(self):
        try:
            if self._semlock._is_mine():
                name = current_process().name
                if threading.current_thread().name != 'MainThread':
                    name += '|' + threading.current_thread().name
                count = self._semlock._count()
            elif self._semlock._get_value() == 1:
                name, count = ('None', 0)
            elif self._semlock._count() > 0:
                name, count = ('SomeOtherThread', 'nonzero')
            else:
                name, count = ('SomeOtherProcess', 'nonzero')
        except Exception:
            name, count = ('unknown', 'unknown')

        return '<RLock(%s, %s)>' % (name, count)


class Condition(object):

    def __init__(self, lock=None):
        self._lock = lock or RLock()
        self._sleeping_count = Semaphore(0)
        self._woken_count = Semaphore(0)
        self._wait_semaphore = Semaphore(0)
        self._make_methods()

    def __getstate__(self):
        assert_spawning(self)
        return (self._lock,
         self._sleeping_count,
         self._woken_count,
         self._wait_semaphore)

    def __setstate__(self, state):
        self._lock, self._sleeping_count, self._woken_count, self._wait_semaphore = state
        self._make_methods()

    def _make_methods(self):
        self.acquire = self._lock.acquire
        self.release = self._lock.release
        self.__enter__ = self._lock.__enter__
        self.__exit__ = self._lock.__exit__

    def __repr__(self):
        try:
            num_waiters = self._sleeping_count._semlock._get_value() - self._woken_count._semlock._get_value()
        except Exception:
            num_waiters = 'unkown'

        return '<Condition(%s, %s)>' % (self._lock, num_waiters)

    def wait(self, timeout=None):
        assert self._lock._semlock._is_mine(), 'must acquire() condition before using wait()'
        self._sleeping_count.release()
        count = self._lock._semlock._count()
        for i in xrange(count):
            self._lock.release()

        try:
            self._wait_semaphore.acquire(True, timeout)
        finally:
            self._woken_count.release()
            for i in xrange(count):
                self._lock.acquire()

    def notify(self):
        assert self._lock._semlock._is_mine(), 'lock is not owned'
        assert not self._wait_semaphore.acquire(False)
        while 1:
            res = self._woken_count.acquire(False) and self._sleeping_count.acquire(False)
            assert res

        if self._sleeping_count.acquire(False):
            self._wait_semaphore.release()
            self._woken_count.acquire()
            self._wait_semaphore.acquire(False)

    def notify_all--- This code section failed: ---

 239       0	LOAD_FAST         'self'
           3	LOAD_ATTR         '_lock'
           6	LOAD_ATTR         '_semlock'
           9	LOAD_ATTR         '_is_mine'
          12	CALL_FUNCTION_0   ''
          15	JUMP_IF_TRUE      '27'
          18	LOAD_ASSERT       'AssertionError'
          21	LOAD_CONST        'lock is not owned'
          24	RAISE_VARARGS_2   ''

 240      27	LOAD_FAST         'self'
          30	LOAD_ATTR         '_wait_semaphore'
          33	LOAD_ATTR         'acquire'
          36	LOAD_GLOBAL       'False'
          39	CALL_FUNCTION_1   ''
          42	UNARY_NOT         ''
          43	JUMP_IF_TRUE      '52'
          46	LOAD_ASSERT       'AssertionError'
          49	RAISE_VARARGS_1   ''

 244      52	SETUP_LOOP        '107'
          55	LOAD_FAST         'self'
          58	LOAD_ATTR         '_woken_count'
          61	LOAD_ATTR         'acquire'
          64	LOAD_GLOBAL       'False'
          67	CALL_FUNCTION_1   ''
          70	JUMP_IF_FALSE     '106'

 245      73	LOAD_FAST         'self'
          76	LOAD_ATTR         '_sleeping_count'
          79	LOAD_ATTR         'acquire'
          82	LOAD_GLOBAL       'False'
          85	CALL_FUNCTION_1   ''
          88	STORE_FAST        'res'

 246      91	LOAD_FAST         'res'
          94	JUMP_IF_TRUE      '103'
          97	LOAD_ASSERT       'AssertionError'
         100	RAISE_VARARGS_1   ''
         103	JUMP_BACK         '55'
         106	POP_BLOCK         ''
       107_0	COME_FROM         '52'

 248     107	LOAD_CONST        0
         110	STORE_FAST        'sleepers'

 249     113	SETUP_LOOP        '161'
         116	LOAD_FAST         'self'
         119	LOAD_ATTR         '_sleeping_count'
         122	LOAD_ATTR         'acquire'
         125	LOAD_GLOBAL       'False'
         128	CALL_FUNCTION_1   ''
         131	JUMP_IF_FALSE     '160'

 250     134	LOAD_FAST         'self'
         137	LOAD_ATTR         '_wait_semaphore'
         140	LOAD_ATTR         'release'
         143	CALL_FUNCTION_0   ''
         146	POP_TOP           ''

 251     147	LOAD_FAST         'sleepers'
         150	LOAD_CONST        1
         153	INPLACE_ADD       ''
         154	STORE_FAST        'sleepers'
         157	JUMP_BACK         '116'
         160	POP_BLOCK         ''
       161_0	COME_FROM         '113'

 253     161	LOAD_FAST         'sleepers'
         164	JUMP_IF_FALSE     '231'

 254     167	SETUP_LOOP        '203'
         170	LOAD_GLOBAL       'xrange'
         173	LOAD_FAST         'sleepers'
         176	CALL_FUNCTION_1   ''
         179	GET_ITER          ''
         180	FOR_ITER          '202'
         183	STORE_FAST        'i'

 255     186	LOAD_FAST         'self'
         189	LOAD_ATTR         '_woken_count'
         192	LOAD_ATTR         'acquire'
         195	CALL_FUNCTION_0   ''
         198	POP_TOP           ''
         199	JUMP_BACK         '180'
         202	POP_BLOCK         ''
       203_0	COME_FROM         '167'

 258     203	SETUP_LOOP        '231'
         206	LOAD_FAST         'self'
         209	LOAD_ATTR         '_wait_semaphore'
         212	LOAD_ATTR         'acquire'
         215	LOAD_GLOBAL       'False'
         218	CALL_FUNCTION_1   ''
         221	JUMP_IF_FALSE     '227'

 259     224	JUMP_BACK         '206'
         227	POP_BLOCK         ''
       228_0	COME_FROM         '203'
         228	JUMP_FORWARD      '231'
       231_0	COME_FROM         '228'

Syntax error at or near 'POP_BLOCK' token at offset 227


class Event(object):

    def __init__(self):
        self._cond = Condition(Lock())
        self._flag = Semaphore(0)

    def is_set(self):
        self._cond.acquire()
        try:
            if self._flag.acquire(False):
                self._flag.release()
                return True
            return False
        finally:
            self._cond.release()

    def set(self):
        self._cond.acquire()
        try:
            self._flag.acquire(False)
            self._flag.release()
            self._cond.notify_all()
        finally:
            self._cond.release()

    def clear(self):
        self._cond.acquire()
        try:
            self._flag.acquire(False)
        finally:
            self._cond.release()

    def wait(self, timeout=None):
        self._cond.acquire()
        try:
            if self._flag.acquire(False):
                self._flag.release()
            else:
                self._cond.wait(timeout)
        finally:
            self._cond.release()