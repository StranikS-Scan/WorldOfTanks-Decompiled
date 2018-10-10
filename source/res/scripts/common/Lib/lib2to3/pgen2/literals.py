# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/lib2to3/pgen2/literals.py
import re
simple_escapes = {'a': '\x07',
 'b': '\x08',
 'f': '\x0c',
 'n': '\n',
 'r': '\r',
 't': '\t',
 'v': '\x0b',
 "'": "'",
 '"': '"',
 '\\': '\\'}

def escape(m):
    all, tail = m.group(0, 1)
    esc = simple_escapes.get(tail)
    if esc is not None:
        return esc
    else:
        if tail.startswith('x'):
            hexes = tail[1:]
            if len(hexes) < 2:
                raise ValueError("invalid hex string escape ('\\%s')" % tail)
            try:
                i = int(hexes, 16)
            except ValueError:
                raise ValueError("invalid hex string escape ('\\%s')" % tail)

        else:
            try:
                i = int(tail, 8)
            except ValueError:
                raise ValueError("invalid octal string escape ('\\%s')" % tail)

        return chr(i)


def evalString(s):
    q = s[0]
    if s[:3] == q * 3:
        q = q * 3
    s = s[len(q):-len(q)]
    return re.sub('\\\\(\\\'|\\"|\\\\|[abfnrtv]|x.{0,2}|[0-7]{1,3})', escape, s)


def test():
    for i in range(256):
        c = chr(i)
        s = repr(c)
        e = evalString(s)
        if e != c:
            print i, c, s, e


if __name__ == '__main__':
    test()
