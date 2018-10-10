# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/keyword.py
__all__ = ['iskeyword', 'kwlist']
kwlist = ['and',
 'as',
 'assert',
 'break',
 'class',
 'continue',
 'def',
 'del',
 'elif',
 'else',
 'except',
 'exec',
 'finally',
 'for',
 'from',
 'global',
 'if',
 'import',
 'in',
 'is',
 'lambda',
 'not',
 'or',
 'pass',
 'print',
 'raise',
 'return',
 'try',
 'while',
 'with',
 'yield']
iskeyword = frozenset(kwlist).__contains__

def main():
    import sys, re
    args = sys.argv[1:]
    iptfile = args and args[0] or 'Python/graminit.c'
    if len(args) > 1:
        optfile = args[1]
    else:
        optfile = 'Lib/keyword.py'
    fp = open(iptfile)
    strprog = re.compile('"([^"]+)"')
    lines = []
    for line in fp:
        if '{1, "' in line:
            match = strprog.search(line)
            if match:
                lines.append("        '" + match.group(1) + "',\n")

    fp.close()
    lines.sort()
    fp = open(optfile)
    format = fp.readlines()
    fp.close()
    try:
        start = format.index('#--start keywords--\n') + 1
        end = format.index('#--end keywords--\n')
        format[start:end] = lines
    except ValueError:
        sys.stderr.write('target does not contain format markers\n')
        sys.exit(1)

    fp = open(optfile, 'w')
    fp.write(''.join(format))
    fp.close()


if __name__ == '__main__':
    main()
