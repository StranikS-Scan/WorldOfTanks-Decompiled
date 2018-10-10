# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/quopri.py
__all__ = ['encode',
 'decode',
 'encodestring',
 'decodestring']
ESCAPE = '='
MAXLINESIZE = 76
HEX = '0123456789ABCDEF'
EMPTYSTRING = ''
try:
    from binascii import a2b_qp, b2a_qp
except ImportError:
    a2b_qp = None
    b2a_qp = None

def needsquoting(c, quotetabs, header):
    if c in ' \t':
        return quotetabs
    if c == '_':
        return header
    return c == ESCAPE or not ' ' <= c <= '~'


def quote(c):
    i = ord(c)
    return ESCAPE + HEX[i // 16] + HEX[i % 16]


def encode(input, output, quotetabs, header=0):
    if b2a_qp is not None:
        data = input.read()
        odata = b2a_qp(data, quotetabs=quotetabs, header=header)
        output.write(odata)
        return
    else:

        def write(s, output=output, lineEnd='\n'):
            if s and s[-1:] in ' \t':
                output.write(s[:-1] + quote(s[-1]) + lineEnd)
            elif s == '.':
                output.write(quote(s) + lineEnd)
            else:
                output.write(s + lineEnd)

        prevline = None
        while 1:
            line = input.readline()
            if not line:
                break
            outline = []
            stripped = ''
            if line[-1:] == '\n':
                line = line[:-1]
                stripped = '\n'
            for c in line:
                if needsquoting(c, quotetabs, header):
                    c = quote(c)
                if header and c == ' ':
                    outline.append('_')
                outline.append(c)

            if prevline is not None:
                write(prevline)
            thisline = EMPTYSTRING.join(outline)
            while len(thisline) > MAXLINESIZE:
                write(thisline[:MAXLINESIZE - 1], lineEnd='=\n')
                thisline = thisline[MAXLINESIZE - 1:]

            prevline = thisline

        if prevline is not None:
            write(prevline, lineEnd=stripped)
        return


def encodestring(s, quotetabs=0, header=0):
    if b2a_qp is not None:
        return b2a_qp(s, quotetabs=quotetabs, header=header)
    else:
        from cStringIO import StringIO
        infp = StringIO(s)
        outfp = StringIO()
        encode(infp, outfp, quotetabs, header)
        return outfp.getvalue()


def decode(input, output, header=0):
    if a2b_qp is not None:
        data = input.read()
        odata = a2b_qp(data, header=header)
        output.write(odata)
        return
    else:
        new = ''
        while 1:
            line = input.readline()
            if not line:
                break
            i, n = 0, len(line)
            if n > 0 and line[n - 1] == '\n':
                partial = 0
                n = n - 1
                while n > 0 and line[n - 1] in ' \t\r':
                    n = n - 1

            else:
                partial = 1
            while i < n:
                c = line[i]
                if c == '_' and header:
                    new = new + ' '
                    i = i + 1
                if c != ESCAPE:
                    new = new + c
                    i = i + 1
                if i + 1 == n and not partial:
                    partial = 1
                    break
                if i + 1 < n and line[i + 1] == ESCAPE:
                    new = new + ESCAPE
                    i = i + 2
                if i + 2 < n and ishex(line[i + 1]) and ishex(line[i + 2]):
                    new = new + chr(unhex(line[i + 1:i + 3]))
                    i = i + 3
                new = new + c
                i = i + 1

            if not partial:
                output.write(new + '\n')
                new = ''

        if new:
            output.write(new)
        return


def decodestring(s, header=0):
    if a2b_qp is not None:
        return a2b_qp(s, header=header)
    else:
        from cStringIO import StringIO
        infp = StringIO(s)
        outfp = StringIO()
        decode(infp, outfp, header=header)
        return outfp.getvalue()


def ishex(c):
    return '0' <= c <= '9' or 'a' <= c <= 'f' or 'A' <= c <= 'F'


def unhex(s):
    bits = 0
    for c in s:
        if '0' <= c <= '9':
            i = ord('0')
        elif 'a' <= c <= 'f':
            i = ord('a') - 10
        elif 'A' <= c <= 'F':
            i = ord('A') - 10
        else:
            break
        bits = bits * 16 + (ord(c) - i)

    return bits


def main():
    import sys
    import getopt
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'td')
    except getopt.error as msg:
        sys.stdout = sys.stderr
        print msg
        print 'usage: quopri [-t | -d] [file] ...'
        print '-t: quote tabs'
        print '-d: decode; default encode'
        sys.exit(2)

    deco = 0
    tabs = 0
    for o, a in opts:
        if o == '-t':
            tabs = 1
        if o == '-d':
            deco = 1

    if tabs and deco:
        sys.stdout = sys.stderr
        print '-t and -d are mutually exclusive'
        sys.exit(2)
    if not args:
        args = ['-']
    sts = 0
    for file in args:
        if file == '-':
            fp = sys.stdin
        else:
            try:
                fp = open(file)
            except IOError as msg:
                sys.stderr.write("%s: can't open (%s)\n" % (file, msg))
                sts = 1
                continue

        if deco:
            decode(fp, sys.stdout)
        else:
            encode(fp, sys.stdout, tabs)
        if fp is not sys.stdin:
            fp.close()

    if sts:
        sys.exit(sts)


if __name__ == '__main__':
    main()
