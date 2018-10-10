# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/posixfile.py
import warnings
warnings.warn('The posixfile module is deprecated; fcntl.lockf() provides better locking', DeprecationWarning, 2)

class _posixfile_:
    states = ['open', 'closed']

    def __repr__(self):
        file = self._file_
        return "<%s posixfile '%s', mode '%s' at %s>" % (self.states[file.closed],
         file.name,
         file.mode,
         hex(id(self))[2:])

    def open(self, name, mode='r', bufsize=-1):
        import __builtin__
        return self.fileopen(__builtin__.open(name, mode, bufsize))

    def fileopen(self, file):
        import types
        if repr(type(file)) != "<type 'file'>":
            raise TypeError, 'posixfile.fileopen() arg must be file object'
        self._file_ = file
        for maybemethod in dir(file):
            if not maybemethod.startswith('_'):
                attr = getattr(file, maybemethod)
                if isinstance(attr, types.BuiltinMethodType):
                    setattr(self, maybemethod, attr)

        return self

    def file(self):
        return self._file_

    def dup(self):
        import posix
        if not hasattr(posix, 'fdopen'):
            raise AttributeError, 'dup() method unavailable'
        return posix.fdopen(posix.dup(self._file_.fileno()), self._file_.mode)

    def dup2(self, fd):
        import posix
        if not hasattr(posix, 'fdopen'):
            raise AttributeError, 'dup() method unavailable'
        posix.dup2(self._file_.fileno(), fd)
        return posix.fdopen(fd, self._file_.mode)

    def flags(self, *which):
        import fcntl, os
        if which:
            if len(which) > 1:
                raise TypeError, 'Too many arguments'
            which = which[0]
        else:
            which = '?'
        l_flags = 0
        if 'n' in which:
            l_flags = l_flags | os.O_NDELAY
        if 'a' in which:
            l_flags = l_flags | os.O_APPEND
        if 's' in which:
            l_flags = l_flags | os.O_SYNC
        file = self._file_
        if '=' not in which:
            cur_fl = fcntl.fcntl(file.fileno(), fcntl.F_GETFL, 0)
            if '!' in which:
                l_flags = cur_fl & ~l_flags
            else:
                l_flags = cur_fl | l_flags
        l_flags = fcntl.fcntl(file.fileno(), fcntl.F_SETFL, l_flags)
        if 'c' in which:
            arg = '!' not in which
            l_flags = fcntl.fcntl(file.fileno(), fcntl.F_SETFD, arg)
        if '?' in which:
            which = ''
            l_flags = fcntl.fcntl(file.fileno(), fcntl.F_GETFL, 0)
            if os.O_APPEND & l_flags:
                which = which + 'a'
            if fcntl.fcntl(file.fileno(), fcntl.F_GETFD, 0) & 1:
                which = which + 'c'
            if os.O_NDELAY & l_flags:
                which = which + 'n'
            if os.O_SYNC & l_flags:
                which = which + 's'
            return which

    def lock(self, how, *args):
        import struct, fcntl
        if 'w' in how:
            l_type = fcntl.F_WRLCK
        elif 'r' in how:
            l_type = fcntl.F_RDLCK
        elif 'u' in how:
            l_type = fcntl.F_UNLCK
        else:
            raise TypeError, 'no type of lock specified'
        if '|' in how:
            cmd = fcntl.F_SETLKW
        elif '?' in how:
            cmd = fcntl.F_GETLK
        else:
            cmd = fcntl.F_SETLK
        l_whence = 0
        l_start = 0
        l_len = 0
        if len(args) == 1:
            l_len = args[0]
        elif len(args) == 2:
            l_len, l_start = args
        elif len(args) == 3:
            l_len, l_start, l_whence = args
        elif len(args) > 3:
            raise TypeError, 'too many arguments'
        import sys, os
        if sys.platform in ('netbsd1', 'openbsd2', 'freebsd2', 'freebsd3', 'freebsd4', 'freebsd5', 'freebsd6', 'freebsd7', 'freebsd8', 'bsdos2', 'bsdos3', 'bsdos4'):
            flock = struct.pack('lxxxxlxxxxlhh', l_start, l_len, os.getpid(), l_type, l_whence)
        elif sys.platform in ('aix3', 'aix4'):
            flock = struct.pack('hhlllii', l_type, l_whence, l_start, l_len, 0, 0, 0)
        else:
            flock = struct.pack('hhllhh', l_type, l_whence, l_start, l_len, 0, 0)
        flock = fcntl.fcntl(self._file_.fileno(), cmd, flock)
        if '?' in how:
            if sys.platform in ('netbsd1', 'openbsd2', 'freebsd2', 'freebsd3', 'freebsd4', 'freebsd5', 'bsdos2', 'bsdos3', 'bsdos4'):
                l_start, l_len, l_pid, l_type, l_whence = struct.unpack('lxxxxlxxxxlhh', flock)
            elif sys.platform in ('aix3', 'aix4'):
                l_type, l_whence, l_start, l_len, l_sysid, l_pid, l_vfs = struct.unpack('hhlllii', flock)
            elif sys.platform == 'linux2':
                l_type, l_whence, l_start, l_len, l_pid, l_sysid = struct.unpack('hhllhh', flock)
            else:
                l_type, l_whence, l_start, l_len, l_sysid, l_pid = struct.unpack('hhllhh', flock)
            if l_type != fcntl.F_UNLCK:
                if l_type == fcntl.F_RDLCK:
                    return ('r',
                     l_len,
                     l_start,
                     l_whence,
                     l_pid)
                else:
                    return ('w',
                     l_len,
                     l_start,
                     l_whence,
                     l_pid)


def open(name, mode='r', bufsize=-1):
    return _posixfile_().open(name, mode, bufsize)


def fileopen(file):
    return _posixfile_().fileopen(file)


SEEK_SET = 0
SEEK_CUR = 1
SEEK_END = 2
