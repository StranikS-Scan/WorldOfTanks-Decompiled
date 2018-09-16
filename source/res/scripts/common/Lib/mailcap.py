# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/mailcap.py
import os
__all__ = ['getcaps', 'findmatch']

def getcaps():
    caps = {}
    for mailcap in listmailcapfiles():
        try:
            fp = open(mailcap, 'r')
        except IOError:
            continue

        with fp:
            morecaps = readmailcapfile(fp)
        for key, value in morecaps.iteritems():
            if key not in caps:
                caps[key] = value
            caps[key] = caps[key] + value

    return caps


def listmailcapfiles():
    if 'MAILCAPS' in os.environ:
        str = os.environ['MAILCAPS']
        mailcaps = str.split(':')
    else:
        if 'HOME' in os.environ:
            home = os.environ['HOME']
        else:
            home = '.'
        mailcaps = [home + '/.mailcap',
         '/etc/mailcap',
         '/usr/etc/mailcap',
         '/usr/local/etc/mailcap']
    return mailcaps


def readmailcapfile(fp):
    caps = {}
    while 1:
        line = fp.readline()
        if not line:
            break
        if line[0] == '#' or line.strip() == '':
            continue
        nextline = line
        while nextline[-2:] == '\\\n':
            nextline = fp.readline()
            if not nextline:
                nextline = '\n'
            line = line[:-2] + nextline

        key, fields = parseline(line)
        if not (key and fields):
            continue
        types = key.split('/')
        for j in range(len(types)):
            types[j] = types[j].strip()

        key = '/'.join(types).lower()
        if key in caps:
            caps[key].append(fields)
        caps[key] = [fields]

    return caps


def parseline(line):
    fields = []
    i, n = 0, len(line)
    while i < n:
        field, i = parsefield(line, i, n)
        fields.append(field)
        i = i + 1

    if len(fields) < 2:
        return (None, None)
    else:
        key, view, rest = fields[0], fields[1], fields[2:]
        fields = {'view': view}
        for field in rest:
            i = field.find('=')
            if i < 0:
                fkey = field
                fvalue = ''
            else:
                fkey = field[:i].strip()
                fvalue = field[i + 1:].strip()
            if fkey in fields:
                pass
            fields[fkey] = fvalue

        return (key, fields)


def parsefield(line, i, n):
    start = i
    while i < n:
        c = line[i]
        if c == ';':
            break
        if c == '\\':
            i = i + 2
        i = i + 1

    return (line[start:i].strip(), i)


def findmatch(caps, MIMEtype, key='view', filename='/dev/null', plist=[]):
    entries = lookup(caps, MIMEtype, key)
    for e in entries:
        if 'test' in e:
            test = subst(e['test'], filename, plist)
            if test and os.system(test) != 0:
                continue
        command = subst(e[key], MIMEtype, filename, plist)
        return (command, e)

    return (None, None)


def lookup(caps, MIMEtype, key=None):
    entries = []
    if MIMEtype in caps:
        entries = entries + caps[MIMEtype]
    MIMEtypes = MIMEtype.split('/')
    MIMEtype = MIMEtypes[0] + '/*'
    if MIMEtype in caps:
        entries = entries + caps[MIMEtype]
    if key is not None:
        entries = filter(lambda e, key=key: key in e, entries)
    return entries


def subst(field, MIMEtype, filename, plist=[]):
    res = ''
    i, n = 0, len(field)
    while i < n:
        c = field[i]
        i = i + 1
        if c != '%':
            if c == '\\':
                c = field[i:i + 1]
                i = i + 1
            res = res + c
        c = field[i]
        i = i + 1
        if c == '%':
            res = res + c
        if c == 's':
            res = res + filename
        if c == 't':
            res = res + MIMEtype
        if c == '{':
            start = i
            while i < n and field[i] != '}':
                i = i + 1

            name = field[start:i]
            i = i + 1
            res = res + findparam(name, plist)
        res = res + '%' + c

    return res


def findparam(name, plist):
    name = name.lower() + '='
    n = len(name)
    for p in plist:
        if p[:n].lower() == name:
            return p[n:]


def test():
    import sys
    caps = getcaps()
    if not sys.argv[1:]:
        show(caps)
        return
    for i in range(1, len(sys.argv), 2):
        args = sys.argv[i:i + 2]
        if len(args) < 2:
            print 'usage: mailcap [MIMEtype file] ...'
            return
        MIMEtype = args[0]
        file = args[1]
        command, e = findmatch(caps, MIMEtype, 'view', file)
        if not command:
            print 'No viewer found for', type
        print 'Executing:', command
        sts = os.system(command)
        if sts:
            print 'Exit status:', sts


def show(caps):
    print 'Mailcap files:'
    for fn in listmailcapfiles():
        print '\t' + fn

    print
    if not caps:
        caps = getcaps()
    print 'Mailcap entries:'
    print
    ckeys = caps.keys()
    ckeys.sort()
    for type in ckeys:
        print type
        entries = caps[type]
        for e in entries:
            keys = e.keys()
            keys.sort()
            for k in keys:
                print '  %-15s' % k, e[k]

            print


if __name__ == '__main__':
    test()
