# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/codeop.py
import __future__
_features = [ getattr(__future__, fname) for fname in __future__.all_feature_names ]
__all__ = ['compile_command', 'Compile', 'CommandCompiler']
PyCF_DONT_IMPLY_DEDENT = 512

def _maybe_compile(compiler, source, filename, symbol):
    for line in source.split('\n'):
        line = line.strip()
        if line and line[0] != '#':
            break
    else:
        if symbol != 'eval':
            source = 'pass'

    err = err1 = err2 = None
    code = code1 = code2 = None
    try:
        code = compiler(source, filename, symbol)
    except SyntaxError as err:
        pass

    try:
        code1 = compiler(source + '\n', filename, symbol)
    except SyntaxError as err1:
        pass

    try:
        code2 = compiler(source + '\n\n', filename, symbol)
    except SyntaxError as err2:
        pass

    if code:
        return code
    else:
        if not code1 and repr(err1) == repr(err2):
            raise SyntaxError, err1
        return


def _compile(source, filename, symbol):
    return compile(source, filename, symbol, PyCF_DONT_IMPLY_DEDENT)


def compile_command(source, filename='<input>', symbol='single'):
    return _maybe_compile(_compile, source, filename, symbol)


class Compile:

    def __init__(self):
        self.flags = PyCF_DONT_IMPLY_DEDENT

    def __call__(self, source, filename, symbol):
        codeob = compile(source, filename, symbol, self.flags, 1)
        for feature in _features:
            if codeob.co_flags & feature.compiler_flag:
                self.flags |= feature.compiler_flag

        return codeob


class CommandCompiler:

    def __init__(self):
        self.compiler = Compile()

    def __call__(self, source, filename='<input>', symbol='single'):
        return _maybe_compile(self.compiler, source, filename, symbol)
