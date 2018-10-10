# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/mimify.py
MAXLEN = 200
CHARSET = 'ISO-8859-1'
QUOTE = '> '
import re
import warnings
warnings.warn('the mimify module is deprecated; use the email package instead', DeprecationWarning, 2)
__all__ = ['mimify',
 'unmimify',
 'mime_encode_header',
 'mime_decode_header']
qp = re.compile('^content-transfer-encoding:\\s*quoted-printable', re.I)
base64_re = re.compile('^content-transfer-encoding:\\s*base64', re.I)
mp = re.compile('^content-type:.*multipart/.*boundary="?([^;"\n]*)', re.I | re.S)
chrset = re.compile('^(content-type:.*charset=")(us-ascii|iso-8859-[0-9]+)(".*)', re.I | re.S)
he = re.compile('^-*\n')
mime_code = re.compile('=([0-9a-f][0-9a-f])', re.I)
mime_head = re.compile('=\\?iso-8859-1\\?q\\?([^? \t\n]+)\\?=', re.I)
repl = re.compile('^subject:\\s+re: ', re.I)

class File:

    def __init__(self, file, boundary):
        self.file = file
        self.boundary = boundary
        self.peek = None
        return

    def readline(self):
        if self.peek is not None:
            return ''
        else:
            line = self.file.readline()
            if not line:
                return line
            if self.boundary:
                if line == self.boundary + '\n':
                    self.peek = line
                    return ''
                if line == self.boundary + '--\n':
                    self.peek = line
                    return ''
            return line


class HeaderFile:

    def __init__(self, file):
        self.file = file
        self.peek = None
        return

    def readline(self):
        if self.peek is not None:
            line = self.peek
            self.peek = None
        else:
            line = self.file.readline()
        if not line:
            return line
        elif he.match(line):
            return line
        else:
            while 1:
                self.peek = self.file.readline()
                if len(self.peek) == 0 or self.peek[0] != ' ' and self.peek[0] != '\t':
                    return line
                line = line + self.peek
                self.peek = None

            return


def mime_decode(line):
    newline = ''
    pos = 0
    while 1:
        res = mime_code.search(line, pos)
        if res is None:
            break
        newline = newline + line[pos:res.start(0)] + chr(int(res.group(1), 16))
        pos = res.end(0)

    return newline + line[pos:]


def mime_decode_header(line):
    newline = ''
    pos = 0
    while 1:
        res = mime_head.search(line, pos)
        if res is None:
            break
        match = res.group(1)
        match = ' '.join(match.split('_'))
        newline = newline + line[pos:res.start(0)] + mime_decode(match)
        pos = res.end(0)

    return newline + line[pos:]


def unmimify_part(ifile, ofile, decode_base64=0):
    multipart = None
    quoted_printable = 0
    is_base64 = 0
    is_repl = 0
    if ifile.boundary and ifile.boundary[:2] == QUOTE:
        prefix = QUOTE
    else:
        prefix = ''
    hfile = HeaderFile(ifile)
    while 1:
        line = hfile.readline()
        if not line:
            return
        if prefix and line[:len(prefix)] == prefix:
            line = line[len(prefix):]
            pref = prefix
        else:
            pref = ''
        line = mime_decode_header(line)
        if qp.match(line):
            quoted_printable = 1
            continue
        if decode_base64 and base64_re.match(line):
            is_base64 = 1
            continue
        ofile.write(pref + line)
        if not prefix and repl.match(line):
            is_repl = 1
        mp_res = mp.match(line)
        if mp_res:
            multipart = '--' + mp_res.group(1)
        if he.match(line):
            break

    if is_repl and (quoted_printable or multipart):
        is_repl = 0
    while 1:
        line = ifile.readline()
        if not line:
            return
        line = re.sub(mime_head, '\\1', line)
        if prefix and line[:len(prefix)] == prefix:
            line = line[len(prefix):]
            pref = prefix
        else:
            pref = ''
        while multipart:
            if line == multipart + '--\n':
                ofile.write(pref + line)
                multipart = None
                line = None
                break
            if line == multipart + '\n':
                ofile.write(pref + line)
                nifile = File(ifile, multipart)
                unmimify_part(nifile, ofile, decode_base64)
                line = nifile.peek
                if not line:
                    break
                continue
            break

        if line and quoted_printable:
            while line[-2:] == '=\n':
                line = line[:-2]
                newline = ifile.readline()
                if newline[:len(QUOTE)] == QUOTE:
                    newline = newline[len(QUOTE):]
                line = line + newline

            line = mime_decode(line)
        if line and is_base64 and not pref:
            import base64
            line = base64.decodestring(line)
        if line:
            ofile.write(pref + line)

    return


def unmimify(infile, outfile, decode_base64=0):
    if type(infile) == type(''):
        ifile = open(infile)
        if type(outfile) == type('') and infile == outfile:
            import os
            d, f = os.path.split(infile)
            os.rename(infile, os.path.join(d, ',' + f))
    else:
        ifile = infile
    if type(outfile) == type(''):
        ofile = open(outfile, 'w')
    else:
        ofile = outfile
    nifile = File(ifile, None)
    unmimify_part(nifile, ofile, decode_base64)
    ofile.flush()
    return


mime_char = re.compile('[=\x7f-\xff]')
mime_header_char = re.compile('[=?\x7f-\xff]')

def mime_encode(line, header):
    if header:
        reg = mime_header_char
    else:
        reg = mime_char
    newline = ''
    pos = 0
    if len(line) >= 5 and line[:5] == 'From ':
        newline = ('=%02x' % ord('F')).upper()
        pos = 1
    while 1:
        res = reg.search(line, pos)
        if res is None:
            break
        newline = newline + line[pos:res.start(0)] + ('=%02x' % ord(res.group(0))).upper()
        pos = res.end(0)

    line = newline + line[pos:]
    newline = ''
    while len(line) >= 75:
        i = 73
        while line[i] == '=' or line[i - 1] == '=':
            i = i - 1

        i = i + 1
        newline = newline + line[:i] + '=\n'
        line = line[i:]

    return newline + line


mime_header = re.compile('([ \t(]|^)([-a-zA-Z0-9_+]*[\x7f-\xff][-a-zA-Z0-9_+\x7f-\xff]*)(?=[ \t)]|\n)')

def mime_encode_header(line):
    newline = ''
    pos = 0
    while 1:
        res = mime_header.search(line, pos)
        if res is None:
            break
        newline = '%s%s%s=?%s?Q?%s?=' % (newline,
         line[pos:res.start(0)],
         res.group(1),
         CHARSET,
         mime_encode(res.group(2), 1))
        pos = res.end(0)

    return newline + line[pos:]


mv = re.compile('^mime-version:', re.I)
cte = re.compile('^content-transfer-encoding:', re.I)
iso_char = re.compile('[\x7f-\xff]')

def mimify_part(ifile, ofile, is_mime):
    has_cte = is_qp = is_base64 = 0
    multipart = None
    must_quote_body = must_quote_header = has_iso_chars = 0
    header = []
    header_end = ''
    message = []
    message_end = ''
    hfile = HeaderFile(ifile)
    while 1:
        line = hfile.readline()
        if not line:
            break
        if not must_quote_header and iso_char.search(line):
            must_quote_header = 1
        if mv.match(line):
            is_mime = 1
        if cte.match(line):
            has_cte = 1
            if qp.match(line):
                is_qp = 1
            elif base64_re.match(line):
                is_base64 = 1
        mp_res = mp.match(line)
        if mp_res:
            multipart = '--' + mp_res.group(1)
        if he.match(line):
            header_end = line
            break
        header.append(line)

    while 1:
        line = ifile.readline()
        if not line:
            break
        if multipart:
            if line == multipart + '--\n':
                message_end = line
                break
            if line == multipart + '\n':
                message_end = line
                break
        if is_base64:
            message.append(line)
            continue
        if is_qp:
            while line[-2:] == '=\n':
                line = line[:-2]
                newline = ifile.readline()
                if newline[:len(QUOTE)] == QUOTE:
                    newline = newline[len(QUOTE):]
                line = line + newline

            line = mime_decode(line)
        message.append(line)
        if not has_iso_chars:
            if iso_char.search(line):
                has_iso_chars = must_quote_body = 1
        if not must_quote_body:
            if len(line) > MAXLEN:
                must_quote_body = 1

    for line in header:
        if must_quote_header:
            line = mime_encode_header(line)
        chrset_res = chrset.match(line)
        if chrset_res:
            if has_iso_chars:
                if chrset_res.group(2).lower() == 'us-ascii':
                    line = '%s%s%s' % (chrset_res.group(1), CHARSET, chrset_res.group(3))
            else:
                line = '%sus-ascii%s' % chrset_res.group(1, 3)
        if has_cte and cte.match(line):
            line = 'Content-Transfer-Encoding: '
            if is_base64:
                line = line + 'base64\n'
            elif must_quote_body:
                line = line + 'quoted-printable\n'
            else:
                line = line + '7bit\n'
        ofile.write(line)

    if (must_quote_header or must_quote_body) and not is_mime:
        ofile.write('Mime-Version: 1.0\n')
        ofile.write('Content-Type: text/plain; ')
        if has_iso_chars:
            ofile.write('charset="%s"\n' % CHARSET)
        else:
            ofile.write('charset="us-ascii"\n')
    if must_quote_body and not has_cte:
        ofile.write('Content-Transfer-Encoding: quoted-printable\n')
    ofile.write(header_end)
    for line in message:
        if must_quote_body:
            line = mime_encode(line, 0)
        ofile.write(line)

    ofile.write(message_end)
    line = message_end
    while multipart:
        if line == multipart + '--\n':
            while 1:
                line = ifile.readline()
                if not line:
                    return
                if must_quote_body:
                    line = mime_encode(line, 0)
                ofile.write(line)

        if line == multipart + '\n':
            nifile = File(ifile, multipart)
            mimify_part(nifile, ofile, 1)
            line = nifile.peek
            if not line:
                break
            ofile.write(line)
            continue
        while 1:
            line = ifile.readline()
            if not line:
                return
            if must_quote_body:
                line = mime_encode(line, 0)
            ofile.write(line)

    return


def mimify(infile, outfile):
    if type(infile) == type(''):
        ifile = open(infile)
        if type(outfile) == type('') and infile == outfile:
            import os
            d, f = os.path.split(infile)
            os.rename(infile, os.path.join(d, ',' + f))
    else:
        ifile = infile
    if type(outfile) == type(''):
        ofile = open(outfile, 'w')
    else:
        ofile = outfile
    nifile = File(ifile, None)
    mimify_part(nifile, ofile, 0)
    ofile.flush()
    return


import sys
if __name__ == '__main__' or len(sys.argv) > 0 and sys.argv[0] == 'mimify':
    import getopt
    usage = 'Usage: mimify [-l len] -[ed] [infile [outfile]]'
    decode_base64 = 0
    opts, args = getopt.getopt(sys.argv[1:], 'l:edb')
    if len(args) not in (0, 1, 2):
        print usage
        sys.exit(1)
    if (('-e', '') in opts) == (('-d', '') in opts) or ('-b', '') in opts and ('-d', '') not in opts:
        print usage
        sys.exit(1)
    for o, a in opts:
        if o == '-e':
            encode = mimify
        if o == '-d':
            encode = unmimify
        if o == '-l':
            try:
                MAXLEN = int(a)
            except (ValueError, OverflowError):
                print usage
                sys.exit(1)

        if o == '-b':
            decode_base64 = 1

    if len(args) == 0:
        encode_args = (sys.stdin, sys.stdout)
    elif len(args) == 1:
        encode_args = (args[0], sys.stdout)
    else:
        encode_args = (args[0], args[1])
    if decode_base64:
        encode_args = encode_args + (decode_base64,)
    encode(*encode_args)
