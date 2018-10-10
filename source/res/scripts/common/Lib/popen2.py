# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/popen2.py
import os
import sys
import warnings
warnings.warn('The popen2 module is deprecated.  Use the subprocess module.', DeprecationWarning, stacklevel=2)
__all__ = ['popen2', 'popen3', 'popen4']
try:
    MAXFD = os.sysconf('SC_OPEN_MAX')
except (AttributeError, ValueError):
    MAXFD = 256

_active = []

def _cleanup():
    for inst in _active[:]:
        if inst.poll(_deadstate=sys.maxint) >= 0:
            try:
                _active.remove(inst)
            except ValueError:
                pass


class Popen3:
    sts = -1

    def __init__(self, cmd, capturestderr=False, bufsize=-1):
        _cleanup()
        self.cmd = cmd
        p2cread, p2cwrite = os.pipe()
        c2pread, c2pwrite = os.pipe()
        if capturestderr:
            errout, errin = os.pipe()
        self.pid = os.fork()
        if self.pid == 0:
            os.dup2(p2cread, 0)
            os.dup2(c2pwrite, 1)
            if capturestderr:
                os.dup2(errin, 2)
            self._run_child(cmd)
        os.close(p2cread)
        self.tochild = os.fdopen(p2cwrite, 'w', bufsize)
        os.close(c2pwrite)
        self.fromchild = os.fdopen(c2pread, 'r', bufsize)
        if capturestderr:
            os.close(errin)
            self.childerr = os.fdopen(errout, 'r', bufsize)
        else:
            self.childerr = None
        return

    def __del__(self):
        self.poll(_deadstate=sys.maxint)
        if self.sts < 0:
            if _active is not None:
                _active.append(self)
        return

    def _run_child(self, cmd):
        if isinstance(cmd, basestring):
            cmd = ['/bin/sh', '-c', cmd]
        os.closerange(3, MAXFD)
        try:
            os.execvp(cmd[0], cmd)
        finally:
            os._exit(1)

    def poll(self, _deadstate=None):
        if self.sts < 0:
            try:
                pid, sts = os.waitpid(self.pid, os.WNOHANG)
                if pid == self.pid:
                    self.sts = sts
            except os.error:
                if _deadstate is not None:
                    self.sts = _deadstate

        return self.sts

    def wait(self):
        if self.sts < 0:
            pid, sts = os.waitpid(self.pid, 0)
            self.sts = sts
        return self.sts


class Popen4(Popen3):
    childerr = None

    def __init__(self, cmd, bufsize=-1):
        _cleanup()
        self.cmd = cmd
        p2cread, p2cwrite = os.pipe()
        c2pread, c2pwrite = os.pipe()
        self.pid = os.fork()
        if self.pid == 0:
            os.dup2(p2cread, 0)
            os.dup2(c2pwrite, 1)
            os.dup2(c2pwrite, 2)
            self._run_child(cmd)
        os.close(p2cread)
        self.tochild = os.fdopen(p2cwrite, 'w', bufsize)
        os.close(c2pwrite)
        self.fromchild = os.fdopen(c2pread, 'r', bufsize)


if sys.platform[:3] == 'win' or sys.platform == 'os2emx':
    del Popen3
    del Popen4

    def popen2(cmd, bufsize=-1, mode='t'):
        w, r = os.popen2(cmd, mode, bufsize)
        return (r, w)


    def popen3(cmd, bufsize=-1, mode='t'):
        w, r, e = os.popen3(cmd, mode, bufsize)
        return (r, w, e)


    def popen4(cmd, bufsize=-1, mode='t'):
        w, r = os.popen4(cmd, mode, bufsize)
        return (r, w)


else:

    def popen2(cmd, bufsize=-1, mode='t'):
        inst = Popen3(cmd, False, bufsize)
        return (inst.fromchild, inst.tochild)


    def popen3(cmd, bufsize=-1, mode='t'):
        inst = Popen3(cmd, True, bufsize)
        return (inst.fromchild, inst.tochild, inst.childerr)


    def popen4(cmd, bufsize=-1, mode='t'):
        inst = Popen4(cmd, bufsize)
        return (inst.fromchild, inst.tochild)


    __all__.extend(['Popen3', 'Popen4'])
