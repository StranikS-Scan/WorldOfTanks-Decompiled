# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/mhlib.py
from warnings import warnpy3k
warnpy3k('the mhlib module has been removed in Python 3.0; use the mailbox module instead', stacklevel=2)
del warnpy3k
MH_PROFILE = '~/.mh_profile'
PATH = '~/Mail'
MH_SEQUENCES = '.mh_sequences'
FOLDER_PROTECT = 448
import os
import sys
import re
import mimetools
import multifile
import shutil
from bisect import bisect
__all__ = ['MH',
 'Error',
 'Folder',
 'Message']

class Error(Exception):
    pass


class MH():

    def __init__(self, path=None, profile=None):
        if profile is None:
            profile = MH_PROFILE
        self.profile = os.path.expanduser(profile)
        if path is None:
            path = self.getprofile('Path')
        if not path:
            path = PATH
        if not os.path.isabs(path) and path[0] != '~':
            path = os.path.join('~', path)
        path = os.path.expanduser(path)
        if not os.path.isdir(path):
            raise Error, 'MH() path not found'
        self.path = path
        return

    def __repr__(self):
        return 'MH(%r, %r)' % (self.path, self.profile)

    def error(self, msg, *args):
        sys.stderr.write('MH error: %s\n' % (msg % args))

    def getprofile(self, key):
        return pickline(self.profile, key)

    def getpath(self):
        return self.path

    def getcontext(self):
        context = pickline(os.path.join(self.getpath(), 'context'), 'Current-Folder')
        if not context:
            context = 'inbox'
        return context

    def setcontext(self, context):
        fn = os.path.join(self.getpath(), 'context')
        f = open(fn, 'w')
        f.write('Current-Folder: %s\n' % context)
        f.close()

    def listfolders(self):
        folders = []
        path = self.getpath()
        for name in os.listdir(path):
            fullname = os.path.join(path, name)
            if os.path.isdir(fullname):
                folders.append(name)

        folders.sort()
        return folders

    def listsubfolders(self, name):
        fullname = os.path.join(self.path, name)
        nlinks = os.stat(fullname).st_nlink
        if nlinks == 2:
            return []
        subfolders = []
        subnames = os.listdir(fullname)
        for subname in subnames:
            fullsubname = os.path.join(fullname, subname)
            if os.path.isdir(fullsubname):
                name_subname = os.path.join(name, subname)
                subfolders.append(name_subname)
                nlinks = nlinks - 1
                if nlinks == 2:
                    break

        subfolders.sort()
        return subfolders

    def listallfolders(self):
        return self.listallsubfolders('')

    def listallsubfolders(self, name):
        fullname = os.path.join(self.path, name)
        nlinks = os.stat(fullname).st_nlink
        if nlinks == 2:
            return []
        subfolders = []
        subnames = os.listdir(fullname)
        for subname in subnames:
            if subname[0] == ',' or isnumeric(subname):
                continue
            fullsubname = os.path.join(fullname, subname)
            if os.path.isdir(fullsubname):
                name_subname = os.path.join(name, subname)
                subfolders.append(name_subname)
                if not os.path.islink(fullsubname):
                    subsubfolders = self.listallsubfolders(name_subname)
                    subfolders = subfolders + subsubfolders
                nlinks = nlinks - 1
                if nlinks == 2:
                    break

        subfolders.sort()
        return subfolders

    def openfolder(self, name):
        return Folder(self, name)

    def makefolder(self, name):
        protect = pickline(self.profile, 'Folder-Protect')
        if protect and isnumeric(protect):
            mode = int(protect, 8)
        else:
            mode = FOLDER_PROTECT
        os.mkdir(os.path.join(self.getpath(), name), mode)

    def deletefolder(self, name):
        fullname = os.path.join(self.getpath(), name)
        for subname in os.listdir(fullname):
            fullsubname = os.path.join(fullname, subname)
            try:
                os.unlink(fullsubname)
            except os.error:
                self.error('%s not deleted, continuing...' % fullsubname)

        os.rmdir(fullname)


numericprog = re.compile('^[1-9][0-9]*$')

def isnumeric(str):
    return numericprog.match(str) is not None


class Folder():

    def __init__(self, mh, name):
        self.mh = mh
        self.name = name
        if not os.path.isdir(self.getfullname()):
            raise Error, 'no folder %s' % name

    def __repr__(self):
        return 'Folder(%r, %r)' % (self.mh, self.name)

    def error(self, *args):
        self.mh.error(*args)

    def getfullname(self):
        return os.path.join(self.mh.path, self.name)

    def getsequencesfilename(self):
        return os.path.join(self.getfullname(), MH_SEQUENCES)

    def getmessagefilename(self, n):
        return os.path.join(self.getfullname(), str(n))

    def listsubfolders(self):
        return self.mh.listsubfolders(self.name)

    def listallsubfolders(self):
        return self.mh.listallsubfolders(self.name)

    def listmessages(self):
        messages = []
        match = numericprog.match
        append = messages.append
        for name in os.listdir(self.getfullname()):
            if match(name):
                append(name)

        messages = map(int, messages)
        messages.sort()
        if messages:
            self.last = messages[-1]
        else:
            self.last = 0
        return messages

    def getsequences(self):
        sequences = {}
        fullname = self.getsequencesfilename()
        try:
            f = open(fullname, 'r')
        except IOError:
            return sequences

        while 1:
            line = f.readline()
            if not line:
                break
            fields = line.split(':')
            if len(fields) != 2:
                self.error('bad sequence in %s: %s' % (fullname, line.strip()))
            key = fields[0].strip()
            value = IntSet(fields[1].strip(), ' ').tolist()
            sequences[key] = value

        return sequences

    def putsequences(self, sequences):
        fullname = self.getsequencesfilename()
        f = None
        for key, seq in sequences.iteritems():
            s = IntSet('', ' ')
            s.fromlist(seq)
            if not f:
                f = open(fullname, 'w')
            f.write('%s: %s\n' % (key, s.tostring()))

        if not f:
            try:
                os.unlink(fullname)
            except os.error:
                pass

        else:
            f.close()
        return

    def getcurrent(self):
        seqs = self.getsequences()
        try:
            return max(seqs['cur'])
        except (ValueError, KeyError):
            raise Error, 'no cur message'

    def setcurrent(self, n):
        updateline(self.getsequencesfilename(), 'cur', str(n), 0)

    def parsesequence(self, seq):
        all = self.listmessages()
        if not all:
            raise Error, 'no messages in %s' % self.name
        if seq == 'all':
            return all
        i = seq.find(':')
        if i >= 0:
            head, dir, tail = seq[:i], '', seq[i + 1:]
            if tail[:1] in '-+':
                dir, tail = tail[:1], tail[1:]
            if not isnumeric(tail):
                raise Error, 'bad message list %s' % seq
            try:
                count = int(tail)
            except (ValueError, OverflowError):
                count = len(all)

            try:
                anchor = self._parseindex(head, all)
            except Error as msg:
                seqs = self.getsequences()
                if head not in seqs:
                    if not msg:
                        msg = 'bad message list %s' % seq
                    raise Error, msg, sys.exc_info()[2]
                msgs = seqs[head]
                if not msgs:
                    raise Error, 'sequence %s empty' % head
                if dir == '-':
                    return msgs[-count:]
                else:
                    return msgs[:count]
            else:
                if not dir:
                    if head in ('prev', 'last'):
                        dir = '-'
                if dir == '-':
                    i = bisect(all, anchor)
                    return all[max(0, i - count):i]
                i = bisect(all, anchor - 1)
                return all[i:i + count]

        i = seq.find('-')
        if i >= 0:
            begin = self._parseindex(seq[:i], all)
            end = self._parseindex(seq[i + 1:], all)
            i = bisect(all, begin - 1)
            j = bisect(all, end)
            r = all[i:j]
            if not r:
                raise Error, 'bad message list %s' % seq
            return r
        try:
            n = self._parseindex(seq, all)
        except Error as msg:
            seqs = self.getsequences()
            if seq not in seqs:
                if not msg:
                    msg = 'bad message list %s' % seq
                raise Error, msg
            return seqs[seq]

        if n not in all:
            if isnumeric(seq):
                raise Error, "message %d doesn't exist" % n
            else:
                raise Error, 'no %s message' % seq
        else:
            return [n]

    def _parseindex(self, seq, all):
        if isnumeric(seq):
            try:
                return int(seq)
            except (OverflowError, ValueError):
                return sys.maxint

        if seq in ('cur', '.'):
            return self.getcurrent()
        elif seq == 'first':
            return all[0]
        elif seq == 'last':
            return all[-1]
        else:
            if seq == 'next':
                n = self.getcurrent()
                i = bisect(all, n)
                try:
                    return all[i]
                except IndexError:
                    raise Error, 'no next message'

            if seq == 'prev':
                n = self.getcurrent()
                i = bisect(all, n - 1)
                if i == 0:
                    raise Error, 'no prev message'
                try:
                    return all[i - 1]
                except IndexError:
                    raise Error, 'no prev message'

            raise Error, None
            return

    def openmessage(self, n):
        return Message(self, n)

    def removemessages(self, list):
        errors = []
        deleted = []
        for n in list:
            path = self.getmessagefilename(n)
            commapath = self.getmessagefilename(',' + str(n))
            try:
                os.unlink(commapath)
            except os.error:
                pass

            try:
                os.rename(path, commapath)
            except os.error as msg:
                errors.append(msg)
            else:
                deleted.append(n)

        if deleted:
            self.removefromallsequences(deleted)
        if errors:
            if len(errors) == 1:
                raise os.error, errors[0]
            else:
                raise os.error, ('multiple errors:', errors)

    def refilemessages(self, list, tofolder, keepsequences=0):
        errors = []
        refiled = {}
        for n in list:
            ton = tofolder.getlast() + 1
            path = self.getmessagefilename(n)
            topath = tofolder.getmessagefilename(ton)
            try:
                os.rename(path, topath)
            except os.error:
                try:
                    shutil.copy2(path, topath)
                    os.unlink(path)
                except (IOError, os.error) as msg:
                    errors.append(msg)
                    try:
                        os.unlink(topath)
                    except os.error:
                        pass

                    continue

            tofolder.setlast(ton)
            refiled[n] = ton

        if refiled:
            if keepsequences:
                tofolder._copysequences(self, refiled.items())
            self.removefromallsequences(refiled.keys())
        if errors:
            if len(errors) == 1:
                raise os.error, errors[0]
            else:
                raise os.error, ('multiple errors:', errors)

    def _copysequences(self, fromfolder, refileditems):
        fromsequences = fromfolder.getsequences()
        tosequences = self.getsequences()
        changed = 0
        for name, seq in fromsequences.items():
            try:
                toseq = tosequences[name]
                new = 0
            except KeyError:
                toseq = []
                new = 1

            for fromn, ton in refileditems:
                if fromn in seq:
                    toseq.append(ton)
                    changed = 1

            if new and toseq:
                tosequences[name] = toseq

        if changed:
            self.putsequences(tosequences)

    def movemessage(self, n, tofolder, ton):
        path = self.getmessagefilename(n)
        f = open(path)
        f.close()
        del f
        topath = tofolder.getmessagefilename(ton)
        backuptopath = tofolder.getmessagefilename(',%d' % ton)
        try:
            os.rename(topath, backuptopath)
        except os.error:
            pass

        try:
            os.rename(path, topath)
        except os.error:
            ok = 0
            try:
                tofolder.setlast(None)
                shutil.copy2(path, topath)
                ok = 1
            finally:
                if not ok:
                    try:
                        os.unlink(topath)
                    except os.error:
                        pass

            os.unlink(path)

        self.removefromallsequences([n])
        return

    def copymessage(self, n, tofolder, ton):
        path = self.getmessagefilename(n)
        f = open(path)
        f.close()
        del f
        topath = tofolder.getmessagefilename(ton)
        backuptopath = tofolder.getmessagefilename(',%d' % ton)
        try:
            os.rename(topath, backuptopath)
        except os.error:
            pass

        ok = 0
        try:
            tofolder.setlast(None)
            shutil.copy2(path, topath)
            ok = 1
        finally:
            if not ok:
                try:
                    os.unlink(topath)
                except os.error:
                    pass

        return

    def createmessage(self, n, txt):
        path = self.getmessagefilename(n)
        backuppath = self.getmessagefilename(',%d' % n)
        try:
            os.rename(path, backuppath)
        except os.error:
            pass

        ok = 0
        BUFSIZE = 16384
        try:
            f = open(path, 'w')
            while 1:
                buf = txt.read(BUFSIZE)
                if not buf:
                    break
                f.write(buf)

            f.close()
            ok = 1
        finally:
            if not ok:
                try:
                    os.unlink(path)
                except os.error:
                    pass

    def removefromallsequences(self, list):
        if hasattr(self, 'last') and self.last in list:
            del self.last
        sequences = self.getsequences()
        changed = 0
        for name, seq in sequences.items():
            if name == 'cur':
                continue
            for n in list:
                if n in seq:
                    seq.remove(n)
                    changed = 1
                    if not seq:
                        del sequences[name]

        if changed:
            self.putsequences(sequences)

    def getlast(self):
        if not hasattr(self, 'last'):
            self.listmessages()
        return self.last

    def setlast(self, last):
        if last is None:
            if hasattr(self, 'last'):
                del self.last
        else:
            self.last = last
        return


class Message(mimetools.Message):

    def __init__(self, f, n, fp=None):
        self.folder = f
        self.number = n
        if fp is None:
            path = f.getmessagefilename(n)
            fp = open(path, 'r')
        mimetools.Message.__init__(self, fp)
        return

    def __repr__(self):
        return 'Message(%s, %s)' % (repr(self.folder), self.number)

    def getheadertext(self, pred=None):
        if pred is None:
            return ''.join(self.headers)
        else:
            headers = []
            hit = 0
            for line in self.headers:
                if not line[0].isspace():
                    i = line.find(':')
                    if i > 0:
                        hit = pred(line[:i].lower())
                if hit:
                    headers.append(line)

            return ''.join(headers)

    def getbodytext(self, decode=1):
        self.fp.seek(self.startofbody)
        encoding = self.getencoding()
        if not decode or encoding in ('', '7bit', '8bit', 'binary'):
            return self.fp.read()
        try:
            from cStringIO import StringIO
        except ImportError:
            from StringIO import StringIO

        output = StringIO()
        mimetools.decode(self.fp, output, encoding)
        return output.getvalue()

    def getbodyparts(self):
        if self.getmaintype() != 'multipart':
            raise Error, 'Content-Type is not multipart/*'
        bdry = self.getparam('boundary')
        if not bdry:
            raise Error, 'multipart/* without boundary param'
        self.fp.seek(self.startofbody)
        mf = multifile.MultiFile(self.fp)
        mf.push(bdry)
        parts = []
        while mf.next():
            n = '%s.%r' % (self.number, 1 + len(parts))
            part = SubMessage(self.folder, n, mf)
            parts.append(part)

        mf.pop()
        return parts

    def getbody(self):
        if self.getmaintype() == 'multipart':
            return self.getbodyparts()
        else:
            return self.getbodytext()


class SubMessage(Message):

    def __init__(self, f, n, fp):
        Message.__init__(self, f, n, fp)
        if self.getmaintype() == 'multipart':
            self.body = Message.getbodyparts(self)
        else:
            self.body = Message.getbodytext(self)
        self.bodyencoded = Message.getbodytext(self, decode=0)

    def __repr__(self):
        f, n, fp = self.folder, self.number, self.fp
        return 'SubMessage(%s, %s, %s)' % (f, n, fp)

    def getbodytext(self, decode=1):
        if not decode:
            return self.bodyencoded
        return self.body if type(self.body) == type('') else None

    def getbodyparts(self):
        return self.body if type(self.body) == type([]) else None

    def getbody(self):
        return self.body


class IntSet():

    def __init__(self, data=None, sep=',', rng='-'):
        self.pairs = []
        self.sep = sep
        self.rng = rng
        if data:
            self.fromstring(data)

    def reset(self):
        self.pairs = []

    def __cmp__(self, other):
        return cmp(self.pairs, other.pairs)

    def __hash__(self):
        return hash(self.pairs)

    def __repr__(self):
        return 'IntSet(%r, %r, %r)' % (self.tostring(), self.sep, self.rng)

    def normalize(self):
        self.pairs.sort()
        i = 1
        while i < len(self.pairs):
            alo, ahi = self.pairs[i - 1]
            blo, bhi = self.pairs[i]
            if ahi >= blo - 1:
                self.pairs[i - 1:i + 1] = [(alo, max(ahi, bhi))]
            i = i + 1

    def tostring(self):
        s = ''
        for lo, hi in self.pairs:
            if lo == hi:
                t = repr(lo)
            else:
                t = repr(lo) + self.rng + repr(hi)
            if s:
                s = s + (self.sep + t)
            s = t

        return s

    def tolist(self):
        l = []
        for lo, hi in self.pairs:
            m = range(lo, hi + 1)
            l = l + m

        return l

    def fromlist(self, list):
        for i in list:
            self.append(i)

    def clone(self):
        new = IntSet()
        new.pairs = self.pairs[:]
        return new

    def min(self):
        return self.pairs[0][0]

    def max(self):
        return self.pairs[-1][-1]

    def contains(self, x):
        for lo, hi in self.pairs:
            if lo <= x <= hi:
                return True

        return False

    def append(self, x):
        for i in range(len(self.pairs)):
            lo, hi = self.pairs[i]
            if x < lo:
                if x + 1 == lo:
                    self.pairs[i] = (x, hi)
                else:
                    self.pairs.insert(i, (x, x))
                if i > 0 and x - 1 == self.pairs[i - 1][1]:
                    self.pairs[i - 1:i + 1] = [(self.pairs[i - 1][0], self.pairs[i][1])]
                return
            if x <= hi:
                return

        i = len(self.pairs) - 1
        if i >= 0:
            lo, hi = self.pairs[i]
            if x - 1 == hi:
                self.pairs[i] = (lo, x)
                return
        self.pairs.append((x, x))

    def addpair(self, xlo, xhi):
        if xlo > xhi:
            return
        self.pairs.append((xlo, xhi))
        self.normalize()

    def fromstring(self, data):
        new = []
        for part in data.split(self.sep):
            list = []
            for subp in part.split(self.rng):
                s = subp.strip()
                list.append(int(s))

            if len(list) == 1:
                new.append((list[0], list[0]))
            if len(list) == 2 and list[0] <= list[1]:
                new.append((list[0], list[1]))
            raise ValueError, 'bad data passed to IntSet'

        self.pairs = self.pairs + new
        self.normalize()


def pickline(file, key, casefold=1):
    try:
        f = open(file, 'r')
    except IOError:
        return None

    pat = re.escape(key) + ':'
    prog = re.compile(pat, casefold and re.IGNORECASE)
    while 1:
        line = f.readline()
        if not line:
            break
        if prog.match(line):
            text = line[len(key) + 1:]
            while 1:
                line = f.readline()
                if not line or not line[0].isspace():
                    break
                text = text + line

            return text.strip()

    return None


def updateline(file, key, value, casefold=1):
    try:
        f = open(file, 'r')
        lines = f.readlines()
        f.close()
    except IOError:
        lines = []

    pat = re.escape(key) + ':(.*)\n'
    prog = re.compile(pat, casefold and re.IGNORECASE)
    if value is None:
        newline = None
    else:
        newline = '%s: %s\n' % (key, value)
    for i in range(len(lines)):
        line = lines[i]
        if prog.match(line):
            if newline is None:
                del lines[i]
            else:
                lines[i] = newline
            break
    else:
        if newline is not None:
            lines.append(newline)

    tempfile = file + '~'
    f = open(tempfile, 'w')
    for line in lines:
        f.write(line)

    f.close()
    os.rename(tempfile, file)
    return


def test():
    global mh
    global f
    os.system('rm -rf $HOME/Mail/@test')
    mh = MH()

    def do(s):
        print s
        print eval(s)

    do('mh.listfolders()')
    do('mh.listallfolders()')
    testfolders = ['@test',
     '@test/test1',
     '@test/test2',
     '@test/test1/test11',
     '@test/test1/test12',
     '@test/test1/test11/test111']
    for t in testfolders:
        do('mh.makefolder(%r)' % (t,))

    do("mh.listsubfolders('@test')")
    do("mh.listallsubfolders('@test')")
    f = mh.openfolder('@test')
    do('f.listsubfolders()')
    do('f.listallsubfolders()')
    do('f.getsequences()')
    seqs = f.getsequences()
    seqs['foo'] = IntSet('1-10 12-20', ' ').tolist()
    print seqs
    f.putsequences(seqs)
    do('f.getsequences()')
    for t in reversed(testfolders):
        do('mh.deletefolder(%r)' % (t,))

    do('mh.getcontext()')
    context = mh.getcontext()
    f = mh.openfolder(context)
    do('f.getcurrent()')
    for seq in ('first', 'last', 'cur', '.', 'prev', 'next', 'first:3', 'last:3', 'cur:3', 'cur:-3', 'prev:3', 'next:3', '1:3', '1:-3', '100:3', '100:-3', '10000:3', '10000:-3', 'all'):
        try:
            do('f.parsesequence(%r)' % (seq,))
        except Error as msg:
            print 'Error:', msg

        stuff = os.popen('pick %r 2>/dev/null' % (seq,)).read()
        list = map(int, stuff.split())
        print list, '<-- pick'

    do('f.listmessages()')


if __name__ == '__main__':
    test()
