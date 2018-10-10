# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/plat-mac/applesingle.py
from warnings import warnpy3k
warnpy3k('In 3.x, the applesingle module is removed.', stacklevel=2)
import struct
import sys
try:
    import MacOS
    import Carbon.File
except:

    class MacOS:

        def openrf(path, mode):
            return open(path + '.rsrc', mode)

        openrf = classmethod(openrf)


    class Carbon:

        class File:

            class FSSpec:
                pass

            class FSRef:
                pass

            class Alias:
                pass


class Error(ValueError):
    pass


AS_HEADER_FORMAT = '>LL16sh'
AS_HEADER_LENGTH = 26
AS_MAGIC = 333312
AS_VERSION = 131072
AS_ENTRY_FORMAT = '>lll'
AS_ENTRY_LENGTH = 12
AS_DATAFORK = 1
AS_RESOURCEFORK = 2
AS_IGNORE = (3, 4, 5, 6, 8, 9, 10, 11, 12, 13, 14, 15)

class AppleSingle(object):
    datafork = None
    resourcefork = None

    def __init__(self, fileobj, verbose=False):
        header = fileobj.read(AS_HEADER_LENGTH)
        try:
            magic, version, ig, nentry = struct.unpack(AS_HEADER_FORMAT, header)
        except ValueError as arg:
            raise Error, 'Unpack header error: %s' % (arg,)

        if verbose:
            print 'Magic:   0x%8.8x' % (magic,)
            print 'Version: 0x%8.8x' % (version,)
            print 'Entries: %d' % (nentry,)
        if magic != AS_MAGIC:
            raise Error, 'Unknown AppleSingle magic number 0x%8.8x' % (magic,)
        if version != AS_VERSION:
            raise Error, 'Unknown AppleSingle version number 0x%8.8x' % (version,)
        if nentry <= 0:
            raise Error, 'AppleSingle file contains no forks'
        headers = [ fileobj.read(AS_ENTRY_LENGTH) for i in xrange(nentry) ]
        self.forks = []
        for hdr in headers:
            try:
                restype, offset, length = struct.unpack(AS_ENTRY_FORMAT, hdr)
            except ValueError as arg:
                raise Error, 'Unpack entry error: %s' % (arg,)

            if verbose:
                print 'Fork %d, offset %d, length %d' % (restype, offset, length)
            fileobj.seek(offset)
            data = fileobj.read(length)
            if len(data) != length:
                raise Error, 'Short read: expected %d bytes got %d' % (length, len(data))
            self.forks.append((restype, data))
            if restype == AS_DATAFORK:
                self.datafork = data
            if restype == AS_RESOURCEFORK:
                self.resourcefork = data

    def tofile(self, path, resonly=False):
        outfile = open(path, 'wb')
        data = False
        if resonly:
            if self.resourcefork is None:
                raise Error, 'No resource fork found'
            fp = open(path, 'wb')
            fp.write(self.resourcefork)
            fp.close()
        elif self.resourcefork is None and self.datafork is None:
            raise Error, 'No useful forks found'
        else:
            if self.datafork is not None:
                fp = open(path, 'wb')
                fp.write(self.datafork)
                fp.close()
            if self.resourcefork is not None:
                fp = MacOS.openrf(path, '*wb')
                fp.write(self.resourcefork)
                fp.close()
        return


def decode(infile, outpath, resonly=False, verbose=False):
    if not hasattr(infile, 'read'):
        if isinstance(infile, Carbon.File.Alias):
            infile = infile.ResolveAlias()[0]
        if hasattr(Carbon.File, 'FSSpec'):
            if isinstance(infile, (Carbon.File.FSSpec, Carbon.File.FSRef)):
                infile = infile.as_pathname()
        elif isinstance(infile, Carbon.File.FSRef):
            infile = infile.as_pathname()
        infile = open(infile, 'rb')
    asfile = AppleSingle(infile, verbose=verbose)
    asfile.tofile(outpath, resonly=resonly)


def _test():
    if len(sys.argv) < 3 or sys.argv[1] == '-r' and len(sys.argv) != 4:
        print 'Usage: applesingle.py [-r] applesinglefile decodedfile'
        sys.exit(1)
    if sys.argv[1] == '-r':
        resonly = True
        del sys.argv[1]
    else:
        resonly = False
    decode(sys.argv[1], sys.argv[2], resonly=resonly)


if __name__ == '__main__':
    _test()
