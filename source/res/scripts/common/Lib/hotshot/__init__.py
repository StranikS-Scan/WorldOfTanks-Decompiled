# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/hotshot/__init__.py
import _hotshot
from _hotshot import ProfilerError
from warnings import warnpy3k as _warnpy3k
_warnpy3k("The 'hotshot' module is not supported in 3.x, use the 'profile' module instead.", stacklevel=2)

class Profile:

    def __init__(self, logfn, lineevents=0, linetimings=1):
        self.lineevents = lineevents and 1 or 0
        self.linetimings = linetimings and lineevents and 1 or 0
        self._prof = p = _hotshot.profiler(logfn, self.lineevents, self.linetimings)
        if self.__class__ is Profile:
            self.close = p.close
            self.start = p.start
            self.stop = p.stop
            self.addinfo = p.addinfo

    def close(self):
        self._prof.close()

    def fileno(self):
        return self._prof.fileno()

    def start(self):
        self._prof.start()

    def stop(self):
        self._prof.stop()

    def addinfo(self, key, value):
        self._prof.addinfo(key, value)

    def run(self, cmd):
        import __main__
        dict = __main__.__dict__
        return self.runctx(cmd, dict, dict)

    def runctx(self, cmd, globals, locals):
        code = compile(cmd, '<string>', 'exec')
        self._prof.runcode(code, globals, locals)
        return self

    def runcall(self, func, *args, **kw):
        return self._prof.runcall(func, args, kw)
