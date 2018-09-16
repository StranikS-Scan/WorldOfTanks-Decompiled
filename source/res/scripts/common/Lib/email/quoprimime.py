# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/email/quoprimime.py
__all__ = ['body_decode',
 'body_encode',
 'body_quopri_check',
 'body_quopri_len',
 'decode',
 'decodestring',
 'encode',
 'encodestring',
 'header_decode',
 'header_encode',
 'header_quopri_check',
 'header_quopri_len',
 'quote',
 'unquote']
import re
from string import hexdigits
from email.utils import fix_eols
CRLF = '\r\n'
NL = '\n'
MISC_LEN = 7
hqre = re.compile('[^-a-zA-Z0-9!*+/ ]')
bqre = re.compile('[^ !-<>-~\\t]')

def header_quopri_check(c):
    return bool(hqre.match(c))


def body_quopri_check(c):
    return bool(bqre.match(c))


def header_quopri_len(s):
    count = 0
    for c in s:
        if hqre.match(c):
            count += 3
        count += 1

    return count


def body_quopri_len(str):
    count = 0
    for c in str:
        if bqre.match(c):
            count += 3
        count += 1

    return count


def _max_append(L, s, maxlen, extra=''):
    if not L:
        L.append(s.lstrip())
    elif len(L[-1]) + len(s) <= maxlen:
        L[-1] += extra + s
    else:
        L.append(s.lstrip())


def unquote(s):
    return chr(int(s[1:3], 16))


def quote(c):
    return '=%02X' % ord(c)


def header_encode(header, charset='iso-8859-1', keep_eols=False, maxlinelen=76, eol=NL):
    if not header:
        return header
    else:
        if not keep_eols:
            header = fix_eols(header)
        quoted = []
        if maxlinelen is None:
            max_encoded = 100000
        else:
            max_encoded = maxlinelen - len(charset) - MISC_LEN - 1
        for c in header:
            if c == ' ':
                _max_append(quoted, '_', max_encoded)
            if not hqre.match(c):
                _max_append(quoted, c, max_encoded)
            _max_append(quoted, '=%02X' % ord(c), max_encoded)

        joiner = eol + ' '
        return joiner.join([ '=?%s?q?%s?=' % (charset, line) for line in quoted ])


def encode(body, binary=False, maxlinelen=76, eol=NL):
    if not body:
        return body
    else:
        if not binary:
            body = fix_eols(body)
        encoded_body = ''
        lineno = -1
        lines = body.splitlines(1)
        for line in lines:
            if line.endswith(CRLF):
                line = line[:-2]
            elif line[-1] in CRLF:
                line = line[:-1]
            lineno += 1
            encoded_line = ''
            prev = None
            linelen = len(line)
            for j in range(linelen):
                c = line[j]
                prev = c
                if bqre.match(c):
                    c = quote(c)
                elif j + 1 == linelen:
                    if c not in ' \t':
                        encoded_line += c
                    prev = c
                    continue
                if len(encoded_line) + len(c) >= maxlinelen:
                    encoded_body += encoded_line + '=' + eol
                    encoded_line = ''
                encoded_line += c

            if prev and prev in ' \t':
                if lineno + 1 == len(lines):
                    prev = quote(prev)
                    if len(encoded_line) + len(prev) > maxlinelen:
                        encoded_body += encoded_line + '=' + eol + prev
                    else:
                        encoded_body += encoded_line + prev
                else:
                    encoded_body += encoded_line + prev + '=' + eol
                encoded_line = ''
            if lines[lineno].endswith(CRLF) or lines[lineno][-1] in CRLF:
                encoded_body += encoded_line + eol
            else:
                encoded_body += encoded_line
            encoded_line = ''

        return encoded_body


body_encode = encode
encodestring = encode

def decode(encoded, eol=NL):
    if not encoded:
        return encoded
    decoded = ''
    for line in encoded.splitlines():
        line = line.rstrip()
        if not line:
            decoded += eol
            continue
        i = 0
        n = len(line)
        while i < n:
            c = line[i]
            if c != '=':
                decoded += c
                i += 1
            elif i + 1 == n:
                i += 1
                continue
            elif i + 2 < n and line[i + 1] in hexdigits and line[i + 2] in hexdigits:
                decoded += unquote(line[i:i + 3])
                i += 3
            else:
                decoded += c
                i += 1
            if i == n:
                decoded += eol

    if not encoded.endswith(eol) and decoded.endswith(eol):
        decoded = decoded[:-1]
    return decoded


body_decode = decode
decodestring = decode

def _unquote_match(match):
    s = match.group(0)
    return unquote(s)


def header_decode(s):
    s = s.replace('_', ' ')
    return re.sub('=[a-fA-F0-9]{2}', _unquote_match, s)
