# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/tokenize.py
__author__ = 'Ka-Ping Yee <ping@lfw.org>'
__credits__ = 'GvR, ESR, Tim Peters, Thomas Wouters, Fred Drake, Skip Montanaro, Raymond Hettinger'
from itertools import chain
import string, re
from token import *
import token
__all__ = [ x for x in dir(token) if not x.startswith('_') ]
__all__ += ['COMMENT',
 'tokenize',
 'generate_tokens',
 'NL',
 'untokenize']
del x
del token
COMMENT = N_TOKENS
tok_name[COMMENT] = 'COMMENT'
NL = N_TOKENS + 1
tok_name[NL] = 'NL'
N_TOKENS += 2

def group(*choices):
    return '(' + '|'.join(choices) + ')'


def any(*choices):
    return group(*choices) + '*'


def maybe(*choices):
    return group(*choices) + '?'


Whitespace = '[ \\f\\t]*'
Comment = '#[^\\r\\n]*'
Ignore = Whitespace + any('\\\\\\r?\\n' + Whitespace) + maybe(Comment)
Name = '[a-zA-Z_]\\w*'
Hexnumber = '0[xX][\\da-fA-F]+[lL]?'
Octnumber = '(0[oO][0-7]+)|(0[0-7]*)[lL]?'
Binnumber = '0[bB][01]+[lL]?'
Decnumber = '[1-9]\\d*[lL]?'
Intnumber = group(Hexnumber, Binnumber, Octnumber, Decnumber)
Exponent = '[eE][-+]?\\d+'
Pointfloat = group('\\d+\\.\\d*', '\\.\\d+') + maybe(Exponent)
Expfloat = '\\d+' + Exponent
Floatnumber = group(Pointfloat, Expfloat)
Imagnumber = group('\\d+[jJ]', Floatnumber + '[jJ]')
Number = group(Imagnumber, Floatnumber, Intnumber)
Single = "[^'\\\\]*(?:\\\\.[^'\\\\]*)*'"
Double = '[^"\\\\]*(?:\\\\.[^"\\\\]*)*"'
Single3 = "[^'\\\\]*(?:(?:\\\\.|'(?!''))[^'\\\\]*)*'''"
Double3 = '[^"\\\\]*(?:(?:\\\\.|"(?!""))[^"\\\\]*)*"""'
Triple = group("[uUbB]?[rR]?'''", '[uUbB]?[rR]?"""')
String = group("[uUbB]?[rR]?'[^\\n'\\\\]*(?:\\\\.[^\\n'\\\\]*)*'", '[uUbB]?[rR]?"[^\\n"\\\\]*(?:\\\\.[^\\n"\\\\]*)*"')
Operator = group('\\*\\*=?', '>>=?', '<<=?', '<>', '!=', '//=?', '[+\\-*/%&|^=<>]=?', '~')
Bracket = '[][(){}]'
Special = group('\\r?\\n', '[:;.,`@]')
Funny = group(Operator, Bracket, Special)
PlainToken = group(Number, Funny, String, Name)
Token = Ignore + PlainToken
ContStr = group("[uUbB]?[rR]?'[^\\n'\\\\]*(?:\\\\.[^\\n'\\\\]*)*" + group("'", '\\\\\\r?\\n'), '[uUbB]?[rR]?"[^\\n"\\\\]*(?:\\\\.[^\\n"\\\\]*)*' + group('"', '\\\\\\r?\\n'))
PseudoExtras = group('\\\\\\r?\\n|\\Z', Comment, Triple)
PseudoToken = Whitespace + group(PseudoExtras, Number, Funny, ContStr, Name)
tokenprog, pseudoprog, single3prog, double3prog = map(re.compile, (Token,
 PseudoToken,
 Single3,
 Double3))
endprogs = {"'": re.compile(Single),
 '"': re.compile(Double),
 "'''": single3prog,
 '"""': double3prog,
 "r'''": single3prog,
 'r"""': double3prog,
 "u'''": single3prog,
 'u"""': double3prog,
 "ur'''": single3prog,
 'ur"""': double3prog,
 "R'''": single3prog,
 'R"""': double3prog,
 "U'''": single3prog,
 'U"""': double3prog,
 "uR'''": single3prog,
 'uR"""': double3prog,
 "Ur'''": single3prog,
 'Ur"""': double3prog,
 "UR'''": single3prog,
 'UR"""': double3prog,
 "b'''": single3prog,
 'b"""': double3prog,
 "br'''": single3prog,
 'br"""': double3prog,
 "B'''": single3prog,
 'B"""': double3prog,
 "bR'''": single3prog,
 'bR"""': double3prog,
 "Br'''": single3prog,
 'Br"""': double3prog,
 "BR'''": single3prog,
 'BR"""': double3prog,
 'r': None,
 'R': None,
 'u': None,
 'U': None,
 'b': None,
 'B': None}
triple_quoted = {}
for t in ("'''", '"""', "r'''", 'r"""', "R'''", 'R"""', "u'''", 'u"""', "U'''", 'U"""', "ur'''", 'ur"""', "Ur'''", 'Ur"""', "uR'''", 'uR"""', "UR'''", 'UR"""', "b'''", 'b"""', "B'''", 'B"""', "br'''", 'br"""', "Br'''", 'Br"""', "bR'''", 'bR"""', "BR'''", 'BR"""'):
    triple_quoted[t] = t

single_quoted = {}
for t in ("'", '"', "r'", 'r"', "R'", 'R"', "u'", 'u"', "U'", 'U"', "ur'", 'ur"', "Ur'", 'Ur"', "uR'", 'uR"', "UR'", 'UR"', "b'", 'b"', "B'", 'B"', "br'", 'br"', "Br'", 'Br"', "bR'", 'bR"', "BR'", 'BR"'):
    single_quoted[t] = t

tabsize = 8

class TokenError(Exception):
    pass


class StopTokenizing(Exception):
    pass


def printtoken(type, token, srow_scol, erow_ecol, line):
    srow, scol = srow_scol
    erow, ecol = erow_ecol
    print '%d,%d-%d,%d:\t%s\t%s' % (srow,
     scol,
     erow,
     ecol,
     tok_name[type],
     repr(token))


def tokenize(readline, tokeneater=printtoken):
    try:
        tokenize_loop(readline, tokeneater)
    except StopTokenizing:
        pass


def tokenize_loop(readline, tokeneater):
    for token_info in generate_tokens(readline):
        tokeneater(*token_info)


class Untokenizer:

    def __init__(self):
        self.tokens = []
        self.prev_row = 1
        self.prev_col = 0

    def add_whitespace(self, start):
        row, col = start
        if row < self.prev_row or row == self.prev_row and col < self.prev_col:
            raise ValueError('start ({},{}) precedes previous end ({},{})'.format(row, col, self.prev_row, self.prev_col))
        row_offset = row - self.prev_row
        if row_offset:
            self.tokens.append('\\\n' * row_offset)
            self.prev_col = 0
        col_offset = col - self.prev_col
        if col_offset:
            self.tokens.append(' ' * col_offset)

    def untokenize(self, iterable):
        it = iter(iterable)
        for t in it:
            if len(t) == 2:
                self.compat(t, it)
                break
            tok_type, token, start, end, line = t
            if tok_type == ENDMARKER:
                break
            self.add_whitespace(start)
            self.tokens.append(token)
            self.prev_row, self.prev_col = end
            if tok_type in (NEWLINE, NL):
                self.prev_row += 1
                self.prev_col = 0

        return ''.join(self.tokens)

    def compat(self, token, iterable):
        indents = []
        toks_append = self.tokens.append
        startline = token[0] in (NEWLINE, NL)
        prevstring = False
        for tok in chain([token], iterable):
            toknum, tokval = tok[:2]
            if toknum in (NAME, NUMBER):
                tokval += ' '
            if toknum == STRING:
                if prevstring:
                    tokval = ' ' + tokval
                prevstring = True
            else:
                prevstring = False
            if toknum == INDENT:
                indents.append(tokval)
                continue
            elif toknum == DEDENT:
                indents.pop()
                continue
            elif toknum in (NEWLINE, NL):
                startline = True
            elif startline and indents:
                toks_append(indents[-1])
                startline = False
            toks_append(tokval)


def untokenize(iterable):
    ut = Untokenizer()
    return ut.untokenize(iterable)


def generate_tokens(readline):
    lnum = parenlev = continued = 0
    namechars, numchars = string.ascii_letters + '_', '0123456789'
    contstr, needcont = ('', 0)
    contline = None
    indents = [0]
    while 1:
        try:
            line = readline()
        except StopIteration:
            line = ''

        lnum += 1
        pos, max = 0, len(line)
        if contstr:
            if not line:
                raise TokenError, ('EOF in multi-line string', strstart)
            endmatch = endprog.match(line)
            if endmatch:
                pos = end = endmatch.end(0)
                yield (STRING,
                 contstr + line[:end],
                 strstart,
                 (lnum, end),
                 contline + line)
                contstr, needcont = ('', 0)
                contline = None
            elif needcont and line[-2:] != '\\\n' and line[-3:] != '\\\r\n':
                yield (ERRORTOKEN,
                 contstr + line,
                 strstart,
                 (lnum, len(line)),
                 contline)
                contstr = ''
                contline = None
                continue
            else:
                contstr = contstr + line
                contline = contline + line
                continue
        elif parenlev == 0 and not continued:
            if not line:
                break
            column = 0
            while pos < max:
                if line[pos] == ' ':
                    column += 1
                elif line[pos] == '\t':
                    column = (column // tabsize + 1) * tabsize
                elif line[pos] == '\x0c':
                    column = 0
                else:
                    break
                pos += 1

            if pos == max:
                break
            if line[pos] in '#\r\n':
                if line[pos] == '#':
                    comment_token = line[pos:].rstrip('\r\n')
                    nl_pos = pos + len(comment_token)
                    yield (COMMENT,
                     comment_token,
                     (lnum, pos),
                     (lnum, pos + len(comment_token)),
                     line)
                    yield (NL,
                     line[nl_pos:],
                     (lnum, nl_pos),
                     (lnum, len(line)),
                     line)
                yield ((NL, COMMENT)[line[pos] == '#'],
                 line[pos:],
                 (lnum, pos),
                 (lnum, len(line)),
                 line)
                continue
            if column > indents[-1]:
                indents.append(column)
                yield (INDENT,
                 line[:pos],
                 (lnum, 0),
                 (lnum, pos),
                 line)
            while column < indents[-1]:
                if column not in indents:
                    raise IndentationError('unindent does not match any outer indentation level', ('<tokenize>',
                     lnum,
                     pos,
                     line))
                indents = indents[:-1]
                yield (DEDENT,
                 '',
                 (lnum, pos),
                 (lnum, pos),
                 line)

        else:
            if not line:
                raise TokenError, ('EOF in multi-line statement', (lnum, 0))
            continued = 0
        while pos < max:
            pseudomatch = pseudoprog.match(line, pos)
            if pseudomatch:
                start, end = pseudomatch.span(1)
                spos, epos, pos = (lnum, start), (lnum, end), end
                if start == end:
                    continue
                token, initial = line[start:end], line[start]
                if initial in numchars or initial == '.' and token != '.':
                    yield (NUMBER,
                     token,
                     spos,
                     epos,
                     line)
                elif initial in '\r\n':
                    yield (NL if parenlev > 0 else NEWLINE,
                     token,
                     spos,
                     epos,
                     line)
                elif initial == '#':
                    yield (COMMENT,
                     token,
                     spos,
                     epos,
                     line)
                elif token in triple_quoted:
                    endprog = endprogs[token]
                    endmatch = endprog.match(line, pos)
                    if endmatch:
                        pos = endmatch.end(0)
                        token = line[start:pos]
                        yield (STRING,
                         token,
                         spos,
                         (lnum, pos),
                         line)
                    else:
                        strstart = (lnum, start)
                        contstr = line[start:]
                        contline = line
                        break
                elif initial in single_quoted or token[:2] in single_quoted or token[:3] in single_quoted:
                    if token[-1] == '\n':
                        strstart = (lnum, start)
                        endprog = endprogs[initial] or endprogs[token[1]] or endprogs[token[2]]
                        contstr, needcont = line[start:], 1
                        contline = line
                        break
                    else:
                        yield (STRING,
                         token,
                         spos,
                         epos,
                         line)
                elif initial in namechars:
                    yield (NAME,
                     token,
                     spos,
                     epos,
                     line)
                elif initial == '\\':
                    continued = 1
                else:
                    if initial in '([{':
                        parenlev += 1
                    elif initial in ')]}':
                        parenlev -= 1
                    yield (OP,
                     token,
                     spos,
                     epos,
                     line)
            yield (ERRORTOKEN,
             line[pos],
             (lnum, pos),
             (lnum, pos + 1),
             line)
            pos += 1

    for indent in indents[1:]:
        yield (DEDENT,
         '',
         (lnum, 0),
         (lnum, 0),
         '')

    yield (ENDMARKER,
     '',
     (lnum, 0),
     (lnum, 0),
     '')
    return


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        tokenize(open(sys.argv[1]).readline)
    else:
        tokenize(sys.stdin.readline)
