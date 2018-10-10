# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/email/header.py
__all__ = ['Header', 'decode_header', 'make_header']
import re
import binascii
import email.quoprimime
import email.base64mime
from email.errors import HeaderParseError
from email.charset import Charset
NL = '\n'
SPACE = ' '
USPACE = u' '
SPACE8 = ' ' * 8
UEMPTYSTRING = u''
MAXLINELEN = 76
USASCII = Charset('us-ascii')
UTF8 = Charset('utf-8')
ecre = re.compile('\n  =\\?                   # literal =?\n  (?P<charset>[^?]*?)   # non-greedy up to the next ? is the charset\n  \\?                    # literal ?\n  (?P<encoding>[qb])    # either a "q" or a "b", case insensitive\n  \\?                    # literal ?\n  (?P<encoded>.*?)      # non-greedy up to the next ?= is the encoded string\n  \\?=                   # literal ?=\n  (?=[ \\t]|$)           # whitespace or the end of the string\n  ', re.VERBOSE | re.IGNORECASE | re.MULTILINE)
fcre = re.compile('[\\041-\\176]+:$')
_embeded_header = re.compile('\\n[^ \\t]+:')
_max_append = email.quoprimime._max_append

def decode_header(header):
    header = str(header)
    if not ecre.search(header):
        return [(header, None)]
    else:
        decoded = []
        dec = ''
        for line in header.splitlines():
            if not ecre.search(line):
                decoded.append((line, None))
                continue
            parts = ecre.split(line)
            while parts:
                unenc = parts.pop(0).strip()
                if unenc:
                    if decoded and decoded[-1][1] is None:
                        decoded[-1] = (decoded[-1][0] + SPACE + unenc, None)
                    else:
                        decoded.append((unenc, None))
                if parts:
                    charset, encoding = [ s.lower() for s in parts[0:2] ]
                    encoded = parts[2]
                    dec = None
                    if encoding == 'q':
                        dec = email.quoprimime.header_decode(encoded)
                    elif encoding == 'b':
                        paderr = len(encoded) % 4
                        if paderr:
                            encoded += '==='[:4 - paderr]
                        try:
                            dec = email.base64mime.decode(encoded)
                        except binascii.Error:
                            raise HeaderParseError

                    if dec is None:
                        dec = encoded
                    if decoded and decoded[-1][1] == charset:
                        decoded[-1] = (decoded[-1][0] + dec, decoded[-1][1])
                    else:
                        decoded.append((dec, charset))
                del parts[0:3]

        return decoded


def make_header(decoded_seq, maxlinelen=None, header_name=None, continuation_ws=' '):
    h = Header(maxlinelen=maxlinelen, header_name=header_name, continuation_ws=continuation_ws)
    for s, charset in decoded_seq:
        if charset is not None and not isinstance(charset, Charset):
            charset = Charset(charset)
        h.append(s, charset)

    return h


class Header():

    def __init__(self, s=None, charset=None, maxlinelen=None, header_name=None, continuation_ws=' ', errors='strict'):
        if charset is None:
            charset = USASCII
        if not isinstance(charset, Charset):
            charset = Charset(charset)
        self._charset = charset
        self._continuation_ws = continuation_ws
        cws_expanded_len = len(continuation_ws.replace('\t', SPACE8))
        self._chunks = []
        if s is not None:
            self.append(s, charset, errors)
        if maxlinelen is None:
            maxlinelen = MAXLINELEN
        if header_name is None:
            self._firstlinelen = maxlinelen
        else:
            self._firstlinelen = maxlinelen - len(header_name) - 2
        self._maxlinelen = maxlinelen - cws_expanded_len
        return

    def __str__(self):
        return self.encode()

    def __unicode__(self):
        uchunks = []
        lastcs = None
        for s, charset in self._chunks:
            nextcs = charset
            if uchunks:
                if lastcs not in (None, 'us-ascii'):
                    if nextcs in (None, 'us-ascii'):
                        uchunks.append(USPACE)
                        nextcs = None
                elif nextcs not in (None, 'us-ascii'):
                    uchunks.append(USPACE)
            lastcs = nextcs
            uchunks.append(unicode(s, str(charset)))

        return UEMPTYSTRING.join(uchunks)

    def __eq__(self, other):
        return other == self.encode()

    def __ne__(self, other):
        return not self == other

    def append(self, s, charset=None, errors='strict'):
        if charset is None:
            charset = self._charset
        elif not isinstance(charset, Charset):
            charset = Charset(charset)
        if charset != '8bit':
            if isinstance(s, str):
                incodec = charset.input_codec or 'us-ascii'
                ustr = unicode(s, incodec, errors)
                outcodec = charset.output_codec or 'us-ascii'
                ustr.encode(outcodec, errors)
            elif isinstance(s, unicode):
                for charset in (USASCII, charset, UTF8):
                    try:
                        outcodec = charset.output_codec or 'us-ascii'
                        s = s.encode(outcodec, errors)
                        break
                    except UnicodeError:
                        pass

        self._chunks.append((s, charset))
        return

    def _split(self, s, charset, maxlinelen, splitchars):
        splittable = charset.to_splittable(s)
        encoded = charset.from_splittable(splittable, True)
        elen = charset.encoded_header_len(encoded)
        if elen <= maxlinelen:
            return [(encoded, charset)]
        if charset == '8bit':
            return [(s, charset)]
        if charset == 'us-ascii':
            return self._split_ascii(s, charset, maxlinelen, splitchars)
        if elen == len(s):
            splitpnt = maxlinelen
            first = charset.from_splittable(splittable[:splitpnt], False)
            last = charset.from_splittable(splittable[splitpnt:], False)
        else:
            first, last = _binsplit(splittable, charset, maxlinelen)
        fsplittable = charset.to_splittable(first)
        fencoded = charset.from_splittable(fsplittable, True)
        chunk = [(fencoded, charset)]
        return chunk + self._split(last, charset, self._maxlinelen, splitchars)

    def _split_ascii(self, s, charset, firstlen, splitchars):
        chunks = _split_ascii(s, firstlen, self._maxlinelen, self._continuation_ws, splitchars)
        return zip(chunks, [charset] * len(chunks))

    def _encode_chunks(self, newchunks, maxlinelen):
        chunks = []
        for header, charset in newchunks:
            if not header:
                continue
            if charset is None or charset.header_encoding is None:
                s = header
            else:
                s = charset.header_encode(header)
            if chunks and chunks[-1].endswith(' '):
                extra = ''
            else:
                extra = ' '
            _max_append(chunks, s, maxlinelen, extra)

        joiner = NL + self._continuation_ws
        return joiner.join(chunks)

    def encode(self, splitchars=';, '):
        newchunks = []
        maxlinelen = self._firstlinelen
        lastlen = 0
        for s, charset in self._chunks:
            targetlen = maxlinelen - lastlen - 1
            if targetlen < charset.encoded_header_len(''):
                targetlen = maxlinelen
            newchunks += self._split(s, charset, targetlen, splitchars)
            lastchunk, lastcharset = newchunks[-1]
            lastlen = lastcharset.encoded_header_len(lastchunk)

        value = self._encode_chunks(newchunks, maxlinelen)
        if _embeded_header.search(value):
            raise HeaderParseError('header value appears to contain an embedded header: {!r}'.format(value))
        return value


def _split_ascii(s, firstlen, restlen, continuation_ws, splitchars):
    lines = []
    maxlen = firstlen
    for line in s.splitlines():
        line = line.lstrip()
        if len(line) < maxlen:
            lines.append(line)
            maxlen = restlen
            continue
        for ch in splitchars:
            if ch in line:
                break
        else:
            lines.append(line)
            maxlen = restlen
            continue

        cre = re.compile('%s\\s*' % ch)
        if ch in ';,':
            eol = ch
        else:
            eol = ''
        joiner = eol + ' '
        joinlen = len(joiner)
        wslen = len(continuation_ws.replace('\t', SPACE8))
        this = []
        linelen = 0
        for part in cre.split(line):
            curlen = linelen + max(0, len(this) - 1) * joinlen
            partlen = len(part)
            onfirstline = not lines
            if ch == ' ' and onfirstline and len(this) == 1 and fcre.match(this[0]):
                this.append(part)
                linelen += partlen
            if curlen + partlen > maxlen:
                if this:
                    lines.append(joiner.join(this) + eol)
                if partlen > maxlen and ch != ' ':
                    subl = _split_ascii(part, maxlen, restlen, continuation_ws, ' ')
                    lines.extend(subl[:-1])
                    this = [subl[-1]]
                else:
                    this = [part]
                linelen = wslen + len(this[-1])
                maxlen = restlen
            this.append(part)
            linelen += partlen

        if this:
            lines.append(joiner.join(this))

    return lines


def _binsplit(splittable, charset, maxlinelen):
    i = 0
    j = len(splittable)
    while i < j:
        m = i + j + 1 >> 1
        chunk = charset.from_splittable(splittable[:m], True)
        chunklen = charset.encoded_header_len(chunk)
        if chunklen <= maxlinelen:
            i = m
        j = m - 1

    first = charset.from_splittable(splittable[:i], False)
    last = charset.from_splittable(splittable[i:], False)
    return (first, last)
