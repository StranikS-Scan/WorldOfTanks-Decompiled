# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/whichdb.py
import os
import struct
import sys
try:
    import dbm
    _dbmerror = dbm.error
except ImportError:
    dbm = None
    _dbmerror = IOError

def whichdb(filename):
    try:
        f = open(filename + os.extsep + 'pag', 'rb')
        f.close()
        if not (dbm.library == 'GNU gdbm' and sys.platform == 'os2emx'):
            f = open(filename + os.extsep + 'dir', 'rb')
            f.close()
        return 'dbm'
    except IOError:
        try:
            f = open(filename + os.extsep + 'db', 'rb')
            f.close()
            if dbm is not None:
                d = dbm.open(filename)
                d.close()
                return 'dbm'
        except (IOError, _dbmerror):
            pass

    try:
        os.stat(filename + os.extsep + 'dat')
        size = os.stat(filename + os.extsep + 'dir').st_size
        if size == 0:
            return 'dumbdbm'
        f = open(filename + os.extsep + 'dir', 'rb')
        try:
            if f.read(1) in ("'", '"'):
                return 'dumbdbm'
        finally:
            f.close()

    except (OSError, IOError):
        pass

    try:
        f = open(filename, 'rb')
    except IOError:
        return

    s16 = f.read(16)
    f.close()
    s = s16[0:4]
    if len(s) != 4:
        return ''
    else:
        try:
            magic = struct.unpack('=l', s)
        except struct.error:
            return ''

        if magic in (324508366, 324508365, 324508367):
            return 'gdbm'
        if magic in (398689, 1628767744):
            return 'bsddb185'
        try:
            magic = struct.unpack('=l', s16[-4:])
        except struct.error:
            return ''

        return 'dbhash' if magic in (398689, 1628767744) else ''


if __name__ == '__main__':
    for filename in sys.argv[1:]:
        print whichdb(filename) or 'UNKNOWN', filename
