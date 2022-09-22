# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/sre_compile.py
# Compiled at: 2003-06-23 13:11:11
"""Internal support module for sre"""
import _sre, sys
import sre_parse
from sre_constants import *
assert _sre.MAGIC == MAGIC, 'SRE module mismatch'
if _sre.CODESIZE == 2:
    MAXCODE = 65535
else:
    MAXCODE = 4294967295L
_LITERAL_CODES = set([LITERAL, NOT_LITERAL])
_REPEATING_CODES = set([REPEAT, MIN_REPEAT, MAX_REPEAT])
_SUCCESS_CODES = set([SUCCESS, FAILURE])
_ASSERT_CODES = set([ASSERT, ASSERT_NOT])
_equivalences = ((105, 305),
 (115, 383),
 (181, 956),
 (837, 953, 8126),
 (946, 976),
 (949, 1013),
 (952, 977),
 (954, 1008),
 (960, 982),
 (961, 1009),
 (962, 963),
 (966, 981),
 (7777, 7835))
_ignorecase_fixes = {i:tuple((j for j in t if i != j)) for t in _equivalences for i in t}

def _compile(code, pattern, flags):
    emit = code.append
    _len = len
    LITERAL_CODES = _LITERAL_CODES
    REPEATING_CODES = _REPEATING_CODES
    SUCCESS_CODES = _SUCCESS_CODES
    ASSERT_CODES = _ASSERT_CODES
    if flags & SRE_FLAG_IGNORECASE and not flags & SRE_FLAG_LOCALE and flags & SRE_FLAG_UNICODE:
        fixes = _ignorecase_fixes
    else:
        fixes = None
    for op, av in pattern:
        if op in LITERAL_CODES:
            if flags & SRE_FLAG_IGNORECASE:
                lo = _sre.getlower(av, flags)
                if fixes and lo in fixes:
                    emit(OPCODES[IN_IGNORE])
                    skip = _len(code)
                    emit(0)
                    if op is NOT_LITERAL:
                        emit(OPCODES[NEGATE])
                    for k in (lo,) + fixes[lo]:
                        emit(OPCODES[LITERAL])
                        emit(k)

                    emit(OPCODES[FAILURE])
                    code[skip] = _len(code) - skip
                else:
                    emit(OPCODES[OP_IGNORE[op]])
                    emit(lo)
            else:
                emit(OPCODES[op])
                emit(av)
        if op is IN:
            if flags & SRE_FLAG_IGNORECASE:
                emit(OPCODES[OP_IGNORE[op]])

                def fixup(literal, flags=flags):
                    return _sre.getlower(literal, flags)

            else:
                emit(OPCODES[op])
                fixup = None
            skip = _len(code)
            emit(0)
            _compile_charset(av, flags, code, fixup, fixes)
            code[skip] = _len(code) - skip
        if op is ANY:
            if flags & SRE_FLAG_DOTALL:
                emit(OPCODES[ANY_ALL])
            else:
                emit(OPCODES[ANY])
        if op in REPEATING_CODES:
            if flags & SRE_FLAG_TEMPLATE:
                raise error, 'internal: unsupported template operator'
                emit(OPCODES[REPEAT])
                skip = _len(code)
                emit(0)
                emit(av[0])
                emit(av[1])
                _compile(code, av[2], flags)
                emit(OPCODES[SUCCESS])
                code[skip] = _len(code) - skip
            elif _simple(av) and op is not REPEAT:
                if op is MAX_REPEAT:
                    emit(OPCODES[REPEAT_ONE])
                else:
                    emit(OPCODES[MIN_REPEAT_ONE])
                skip = _len(code)
                emit(0)
                emit(av[0])
                emit(av[1])
                _compile(code, av[2], flags)
                emit(OPCODES[SUCCESS])
                code[skip] = _len(code) - skip
            else:
                emit(OPCODES[REPEAT])
                skip = _len(code)
                emit(0)
                emit(av[0])
                emit(av[1])
                _compile(code, av[2], flags)
                code[skip] = _len(code) - skip
                if op is MAX_REPEAT:
                    emit(OPCODES[MAX_UNTIL])
                else:
                    emit(OPCODES[MIN_UNTIL])
        if op is SUBPATTERN:
            if av[0]:
                emit(OPCODES[MARK])
                emit((av[0] - 1) * 2)
            _compile(code, av[1], flags)
            if av[0]:
                emit(OPCODES[MARK])
                emit((av[0] - 1) * 2 + 1)
        if op in SUCCESS_CODES:
            emit(OPCODES[op])
        if op in ASSERT_CODES:
            emit(OPCODES[op])
            skip = _len(code)
            emit(0)
            if av[0] >= 0:
                emit(0)
            else:
                lo, hi = av[1].getwidth()
                if lo != hi:
                    raise error, 'look-behind requires fixed-width pattern'
                emit(lo)
            _compile(code, av[1], flags)
            emit(OPCODES[SUCCESS])
            code[skip] = _len(code) - skip
        if op is CALL:
            emit(OPCODES[op])
            skip = _len(code)
            emit(0)
            _compile(code, av, flags)
            emit(OPCODES[SUCCESS])
            code[skip] = _len(code) - skip
        if op is AT:
            emit(OPCODES[op])
            if flags & SRE_FLAG_MULTILINE:
                av = AT_MULTILINE.get(av, av)
            if flags & SRE_FLAG_LOCALE:
                av = AT_LOCALE.get(av, av)
            elif flags & SRE_FLAG_UNICODE:
                av = AT_UNICODE.get(av, av)
            emit(ATCODES[av])
        if op is BRANCH:
            emit(OPCODES[op])
            tail = []
            tailappend = tail.append
            for av in av[1]:
                skip = _len(code)
                emit(0)
                _compile(code, av, flags)
                emit(OPCODES[JUMP])
                tailappend(_len(code))
                emit(0)
                code[skip] = _len(code) - skip

            emit(0)
            for tail in tail:
                code[tail] = _len(code) - tail

        if op is CATEGORY:
            emit(OPCODES[op])
            if flags & SRE_FLAG_LOCALE:
                av = CH_LOCALE[av]
            elif flags & SRE_FLAG_UNICODE:
                av = CH_UNICODE[av]
            emit(CHCODES[av])
        if op is GROUPREF:
            if flags & SRE_FLAG_IGNORECASE:
                emit(OPCODES[OP_IGNORE[op]])
            else:
                emit(OPCODES[op])
            emit(av - 1)
        if op is GROUPREF_EXISTS:
            emit(OPCODES[op])
            emit(av[0] - 1)
            skipyes = _len(code)
            emit(0)
            _compile(code, av[1], flags)
            if av[2]:
                emit(OPCODES[JUMP])
                skipno = _len(code)
                emit(0)
                code[skipyes] = _len(code) - skipyes + 1
                _compile(code, av[2], flags)
                code[skipno] = _len(code) - skipno
            else:
                code[skipyes] = _len(code) - skipyes + 1
        raise ValueError, ('unsupported operand type', op)

    return


def _compile_charset(charset, flags, code, fixup=None, fixes=None):
    emit = code.append
    for op, av in _optimize_charset(charset, fixup, fixes, flags & SRE_FLAG_UNICODE):
        emit(OPCODES[op])
        if op is NEGATE:
            pass
        if op is LITERAL:
            emit(av)
        if op is RANGE:
            emit(av[0])
            emit(av[1])
        if op is CHARSET:
            code.extend(av)
        if op is BIGCHARSET:
            code.extend(av)
        if op is CATEGORY:
            if flags & SRE_FLAG_LOCALE:
                emit(CHCODES[CH_LOCALE[av]])
            elif flags & SRE_FLAG_UNICODE:
                emit(CHCODES[CH_UNICODE[av]])
            else:
                emit(CHCODES[av])
        raise error, 'internal: unsupported set operator'

    emit(OPCODES[FAILURE])


def _optimize_charset(charset, fixup, fixes, isunicode):
    out = []
    tail = []
    charmap = bytearray(256)
    for op, av in charset:
        while True:
            try:
                if op is LITERAL:
                    if fixup:
                        i = fixup(av)
                        charmap[i] = 1
                        if fixes and i in fixes:
                            for k in fixes[i]:
                                charmap[k] = 1

                    else:
                        charmap[av] = 1
                elif op is RANGE:
                    r = range(av[0], av[1] + 1)
                    if fixup:
                        r = map(fixup, r)
                    if fixup and fixes:
                        for i in r:
                            charmap[i] = 1
                            if i in fixes:
                                for k in fixes[i]:
                                    charmap[k] = 1

                    else:
                        for i in r:
                            charmap[i] = 1

                elif op is NEGATE:
                    out.append((op, av))
                else:
                    tail.append((op, av))
            except IndexError:
                if len(charmap) == 256:
                    charmap += '\x00' * 65280
                    continue
                if fixup and isunicode and op is RANGE:
                    lo, hi = av
                    ranges = [av]
                    _fixup_range(max(65536, lo), min(73727, hi), ranges, fixup)
                    for lo, hi in ranges:
                        if lo == hi:
                            tail.append((LITERAL, hi))
                        tail.append((RANGE, (lo, hi)))

                else:
                    tail.append((op, av))

            break

    runs = []
    q = 0
    while True:
        p = charmap.find('\x01', q)
        if p < 0:
            break
        if len(runs) >= 2:
            runs = None
            break
        q = charmap.find('\x00', p)
        if q < 0:
            runs.append((p, len(charmap)))
            break
        runs.append((p, q))

    if runs is not None:
        for p, q in runs:
            if q - p == 1:
                out.append((LITERAL, p))
            out.append((RANGE, (p, q - 1)))

        out += tail
        if fixup or len(out) < len(charset):
            return out
        return charset
    elif len(charmap) == 256:
        data = _mk_bitmap(charmap)
        out.append((CHARSET, data))
        out += tail
        return out
    else:
        charmap = bytes(charmap)
        comps = {}
        mapping = bytearray(256)
        block = 0
        data = bytearray()
        for i in range(0, 65536, 256):
            chunk = charmap[i:i + 256]
            if chunk in comps:
                mapping[i // 256] = comps[chunk]
            mapping[i // 256] = comps[chunk] = block
            block += 1
            data += chunk

        data = _mk_bitmap(data)
        data[0:0] = [block] + _bytes_to_codes(mapping)
        out.append((BIGCHARSET, data))
        out += tail
        return out


def _fixup_range(lo, hi, ranges, fixup):
    for i in map(fixup, range(lo, hi + 1)):
        for k, (lo, hi) in enumerate(ranges):
            if i < lo:
                if l == lo - 1:
                    ranges[k] = (i, hi)
                else:
                    ranges.insert(k, (i, i))
                break
            if i > hi:
                if i == hi + 1:
                    ranges[k] = (lo, i)
                    break
            break
        else:
            ranges.append((i, i))


_CODEBITS = _sre.CODESIZE * 8
_BITS_TRANS = '0' + '1' * 255

def _mk_bitmap(bits, _CODEBITS=_CODEBITS, _int=int):
    s = bytes(bits).translate(_BITS_TRANS)[::-1]
    return [ _int(s[i - _CODEBITS:i], 2) for i in range(len(s), 0, -_CODEBITS) ]


def _bytes_to_codes(b):
    import array
    if _sre.CODESIZE == 2:
        code = 'H'
    else:
        code = 'I'
    a = array.array(code, bytes(b))
    assert a.itemsize == _sre.CODESIZE
    assert len(a) * a.itemsize == len(b)
    return a.tolist()


def _simple(av):
    lo, hi = av[2].getwidth()
    return lo == hi == 1 and av[2][0][0] != SUBPATTERN


def _compile_info(code, pattern, flags):
    lo, hi = pattern.getwidth()
    if not lo and hi:
        return
    prefix = []
    prefixappend = prefix.append
    prefix_skip = 0
    charset = []
    charsetappend = charset.append
    if not flags & SRE_FLAG_IGNORECASE:
        for op, av in pattern.data:
            if op is LITERAL:
                if len(prefix) == prefix_skip:
                    prefix_skip = prefix_skip + 1
                prefixappend(av)
            if op is SUBPATTERN and len(av[1]) == 1:
                op, av = av[1][0]
                if op is LITERAL:
                    prefixappend(av)
                else:
                    break
            break

        if not prefix and pattern.data:
            op, av = pattern.data[0]
            if op is SUBPATTERN and av[1]:
                op, av = av[1][0]
                if op is LITERAL:
                    charsetappend((op, av))
                elif op is BRANCH:
                    c = []
                    cappend = c.append
                    for p in av[1]:
                        if not p:
                            break
                        op, av = p[0]
                        if op is LITERAL:
                            cappend((op, av))
                        break
                    else:
                        charset = c

            elif op is BRANCH:
                c = []
                cappend = c.append
                for p in av[1]:
                    if not p:
                        break
                    op, av = p[0]
                    if op is LITERAL:
                        cappend((op, av))
                    break
                else:
                    charset = c

            elif op is IN:
                charset = av
    emit = code.append
    emit(OPCODES[INFO])
    skip = len(code)
    emit(0)
    mask = 0
    if prefix:
        mask = SRE_INFO_PREFIX
        if len(prefix) == prefix_skip == len(pattern.data):
            mask = mask + SRE_INFO_LITERAL
    elif charset:
        mask = mask + SRE_INFO_CHARSET
    emit(mask)
    if lo < MAXCODE:
        emit(lo)
    else:
        emit(MAXCODE)
        prefix = prefix[:MAXCODE]
    if hi < MAXCODE:
        emit(hi)
    else:
        emit(0)
    if prefix:
        emit(len(prefix))
        emit(prefix_skip)
        code.extend(prefix)
        table = [-1] + [0] * len(prefix)
        for i in xrange(len(prefix)):
            table[i + 1] = table[i] + 1
            while table[i + 1] > 0 and prefix[i] != prefix[table[i + 1] - 1]:
                table[i + 1] = table[table[i + 1] - 1] + 1

        code.extend(table[1:])
    elif charset:
        _compile_charset(charset, flags, code)
    code[skip] = len(code) - skip


try:
    unicode
except NameError:
    STRING_TYPES = (type(''),)
else:
    STRING_TYPES = (type(''), type(unicode('')))

def isstring(obj):
    for tp in STRING_TYPES:
        if isinstance(obj, tp):
            return 1


def _code(p, flags):
    flags = p.pattern.flags | flags
    code = []
    _compile_info(code, p, flags)
    _compile(code, p.data, flags)
    code.append(OPCODES[SUCCESS])
    return code


def compile(p, flags=0):
    if isstring(p):
        pattern = p
        p = sre_parse.parse(p, flags)
    else:
        pattern = None
    code = _code(p, flags)
    if p.pattern.groups > 100:
        raise AssertionError('sorry, but this version only supports 100 named groups')
    groupindex = p.pattern.groupdict
    indexgroup = [None] * p.pattern.groups
    for k, i in groupindex.items():
        indexgroup[i] = k

    return _sre.compile(pattern, flags | p.pattern.flags, code, p.pattern.groups - 1, groupindex, indexgroup)
