# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/fileinput.py
import sys, os
__all__ = ['input',
 'close',
 'nextfile',
 'filename',
 'lineno',
 'filelineno',
 'isfirstline',
 'isstdin',
 'FileInput']
_state = None
DEFAULT_BUFSIZE = 8192

def input(files=None, inplace=0, backup='', bufsize=0, mode='r', openhook=None):
    global _state
    if _state and _state._file:
        raise RuntimeError, 'input() already active'
    _state = FileInput(files, inplace, backup, bufsize, mode, openhook)
    return _state


def close():
    global _state
    state = _state
    _state = None
    if state:
        state.close()
    return


def nextfile():
    if not _state:
        raise RuntimeError, 'no active input()'
    return _state.nextfile()


def filename():
    if not _state:
        raise RuntimeError, 'no active input()'
    return _state.filename()


def lineno():
    if not _state:
        raise RuntimeError, 'no active input()'
    return _state.lineno()


def filelineno():
    if not _state:
        raise RuntimeError, 'no active input()'
    return _state.filelineno()


def fileno():
    if not _state:
        raise RuntimeError, 'no active input()'
    return _state.fileno()


def isfirstline():
    if not _state:
        raise RuntimeError, 'no active input()'
    return _state.isfirstline()


def isstdin():
    if not _state:
        raise RuntimeError, 'no active input()'
    return _state.isstdin()


class FileInput:

    def __init__(self, files=None, inplace=0, backup='', bufsize=0, mode='r', openhook=None):
        if isinstance(files, basestring):
            files = (files,)
        else:
            if files is None:
                files = sys.argv[1:]
            if not files:
                files = ('-',)
            else:
                files = tuple(files)
        self._files = files
        self._inplace = inplace
        self._backup = backup
        self._bufsize = bufsize or DEFAULT_BUFSIZE
        self._savestdout = None
        self._output = None
        self._filename = None
        self._lineno = 0
        self._filelineno = 0
        self._file = None
        self._isstdin = False
        self._backupfilename = None
        self._buffer = []
        self._bufindex = 0
        if mode not in ('r', 'rU', 'U', 'rb'):
            raise ValueError("FileInput opening mode must be one of 'r', 'rU', 'U' and 'rb'")
        self._mode = mode
        if inplace and openhook:
            raise ValueError('FileInput cannot use an opening hook in inplace mode')
        elif openhook and not hasattr(openhook, '__call__'):
            raise ValueError('FileInput openhook must be callable')
        self._openhook = openhook
        return

    def __del__(self):
        self.close()

    def close(self):
        self.nextfile()
        self._files = ()

    def __iter__(self):
        return self

    def next(self):
        try:
            line = self._buffer[self._bufindex]
        except IndexError:
            pass
        else:
            self._bufindex += 1
            self._lineno += 1
            self._filelineno += 1
            return line

        line = self.readline()
        if not line:
            raise StopIteration
        return line

    def __getitem__(self, i):
        if i != self._lineno:
            raise RuntimeError, 'accessing lines out of order'
        try:
            return self.next()
        except StopIteration:
            raise IndexError, 'end of input reached'

    def nextfile(self):
        savestdout = self._savestdout
        self._savestdout = 0
        if savestdout:
            sys.stdout = savestdout
        output = self._output
        self._output = 0
        if output:
            output.close()
        file = self._file
        self._file = 0
        if file and not self._isstdin:
            file.close()
        backupfilename = self._backupfilename
        self._backupfilename = 0
        if backupfilename and not self._backup:
            try:
                os.unlink(backupfilename)
            except OSError:
                pass

        self._isstdin = False
        self._buffer = []
        self._bufindex = 0

    def readline(self):
        try:
            line = self._buffer[self._bufindex]
        except IndexError:
            pass
        else:
            self._bufindex += 1
            self._lineno += 1
            self._filelineno += 1
            return line

        if not self._file:
            if not self._files:
                return ''
            self._filename = self._files[0]
            self._files = self._files[1:]
            self._filelineno = 0
            self._file = None
            self._isstdin = False
            self._backupfilename = 0
            if self._filename == '-':
                self._filename = '<stdin>'
                self._file = sys.stdin
                self._isstdin = True
            elif self._inplace:
                self._backupfilename = self._filename + (self._backup or os.extsep + 'bak')
                try:
                    os.unlink(self._backupfilename)
                except os.error:
                    pass

                os.rename(self._filename, self._backupfilename)
                self._file = open(self._backupfilename, self._mode)
                try:
                    perm = os.fstat(self._file.fileno()).st_mode
                except OSError:
                    self._output = open(self._filename, 'w')
                else:
                    fd = os.open(self._filename, os.O_CREAT | os.O_WRONLY | os.O_TRUNC, perm)
                    self._output = os.fdopen(fd, 'w')
                    try:
                        if hasattr(os, 'chmod'):
                            os.chmod(self._filename, perm)
                    except OSError:
                        pass

                self._savestdout = sys.stdout
                sys.stdout = self._output
            elif self._openhook:
                self._file = self._openhook(self._filename, self._mode)
            else:
                self._file = open(self._filename, self._mode)
        self._buffer = self._file.readlines(self._bufsize)
        self._bufindex = 0
        if not self._buffer:
            self.nextfile()
        return self.readline()

    def filename(self):
        return self._filename

    def lineno(self):
        return self._lineno

    def filelineno(self):
        return self._filelineno

    def fileno(self):
        if self._file:
            try:
                return self._file.fileno()
            except ValueError:
                return -1

        else:
            return -1

    def isfirstline(self):
        return self._filelineno == 1

    def isstdin(self):
        return self._isstdin


def hook_compressed(filename, mode):
    ext = os.path.splitext(filename)[1]
    if ext == '.gz':
        import gzip
        return gzip.open(filename, mode)
    elif ext == '.bz2':
        import bz2
        return bz2.BZ2File(filename, mode)
    else:
        return open(filename, mode)


def hook_encoded(encoding):
    import io

    def openhook(filename, mode):
        mode = mode.replace('U', '').replace('b', '') or 'r'
        return io.open(filename, mode, encoding=encoding, newline='')

    return openhook


def _test():
    import getopt
    inplace = 0
    backup = 0
    opts, args = getopt.getopt(sys.argv[1:], 'ib:')
    for o, a in opts:
        if o == '-i':
            inplace = 1
        if o == '-b':
            backup = a

    for line in input(args, inplace=inplace, backup=backup):
        if line[-1:] == '\n':
            line = line[:-1]
        if line[-1:] == '\r':
            line = line[:-1]
        print '%d: %s[%d]%s %s' % (lineno(),
         filename(),
         filelineno(),
         isfirstline() and '*' or '',
         line)

    print '%d: %s[%d]' % (lineno(), filename(), filelineno())


if __name__ == '__main__':
    _test()
