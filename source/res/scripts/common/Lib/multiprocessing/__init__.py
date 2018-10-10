# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/multiprocessing/__init__.py
__version__ = '0.70a1'
__all__ = ['Process',
 'current_process',
 'active_children',
 'freeze_support',
 'Manager',
 'Pipe',
 'cpu_count',
 'log_to_stderr',
 'get_logger',
 'allow_connection_pickling',
 'BufferTooShort',
 'TimeoutError',
 'Lock',
 'RLock',
 'Semaphore',
 'BoundedSemaphore',
 'Condition',
 'Event',
 'Queue',
 'JoinableQueue',
 'Pool',
 'Value',
 'Array',
 'RawValue',
 'RawArray',
 'SUBDEBUG',
 'SUBWARNING']
__author__ = 'R. Oudkerk (r.m.oudkerk@gmail.com)'
import os
import sys
from multiprocessing.process import Process, current_process, active_children
from multiprocessing.util import SUBDEBUG, SUBWARNING

class ProcessError(Exception):
    pass


class BufferTooShort(ProcessError):
    pass


class TimeoutError(ProcessError):
    pass


class AuthenticationError(ProcessError):
    pass


import _multiprocessing

def Manager():
    from multiprocessing.managers import SyncManager
    m = SyncManager()
    m.start()
    return m


def Pipe(duplex=True):
    from multiprocessing.connection import Pipe
    return Pipe(duplex)


def cpu_count():
    if sys.platform == 'win32':
        try:
            num = int(os.environ['NUMBER_OF_PROCESSORS'])
        except (ValueError, KeyError):
            num = 0

    elif 'bsd' in sys.platform or sys.platform == 'darwin':
        comm = '/sbin/sysctl -n hw.ncpu'
        if sys.platform == 'darwin':
            comm = '/usr' + comm
        try:
            with os.popen(comm) as p:
                num = int(p.read())
        except ValueError:
            num = 0

    else:
        try:
            num = os.sysconf('SC_NPROCESSORS_ONLN')
        except (ValueError, OSError, AttributeError):
            num = 0

    if num >= 1:
        return num
    raise NotImplementedError('cannot determine number of cpus')


def freeze_support():
    if sys.platform == 'win32' and getattr(sys, 'frozen', False):
        from multiprocessing.forking import freeze_support
        freeze_support()


def get_logger():
    from multiprocessing.util import get_logger
    return get_logger()


def log_to_stderr(level=None):
    from multiprocessing.util import log_to_stderr
    return log_to_stderr(level)


def allow_connection_pickling():
    from multiprocessing import reduction


def Lock():
    from multiprocessing.synchronize import Lock
    return Lock()


def RLock():
    from multiprocessing.synchronize import RLock
    return RLock()


def Condition(lock=None):
    from multiprocessing.synchronize import Condition
    return Condition(lock)


def Semaphore(value=1):
    from multiprocessing.synchronize import Semaphore
    return Semaphore(value)


def BoundedSemaphore(value=1):
    from multiprocessing.synchronize import BoundedSemaphore
    return BoundedSemaphore(value)


def Event():
    from multiprocessing.synchronize import Event
    return Event()


def Queue(maxsize=0):
    from multiprocessing.queues import Queue
    return Queue(maxsize)


def JoinableQueue(maxsize=0):
    from multiprocessing.queues import JoinableQueue
    return JoinableQueue(maxsize)


def Pool(processes=None, initializer=None, initargs=(), maxtasksperchild=None):
    from multiprocessing.pool import Pool
    return Pool(processes, initializer, initargs, maxtasksperchild)


def RawValue(typecode_or_type, *args):
    from multiprocessing.sharedctypes import RawValue
    return RawValue(typecode_or_type, *args)


def RawArray(typecode_or_type, size_or_initializer):
    from multiprocessing.sharedctypes import RawArray
    return RawArray(typecode_or_type, size_or_initializer)


def Value(typecode_or_type, *args, **kwds):
    from multiprocessing.sharedctypes import Value
    return Value(typecode_or_type, *args, **kwds)


def Array(typecode_or_type, size_or_initializer, **kwds):
    from multiprocessing.sharedctypes import Array
    return Array(typecode_or_type, size_or_initializer, **kwds)


if sys.platform == 'win32':

    def set_executable(executable):
        from multiprocessing.forking import set_executable
        set_executable(executable)


    __all__ += ['set_executable']
