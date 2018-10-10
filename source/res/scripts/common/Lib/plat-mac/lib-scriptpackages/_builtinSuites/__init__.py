# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/plat-mac/lib-scriptpackages/_builtinSuites/__init__.py
from warnings import warnpy3k
warnpy3k('In 3.x, the _builtinSuites module is removed.', stacklevel=2)
import aetools
import builtin_Suite
_code_to_module = {'reqd': builtin_Suite,
 'core': builtin_Suite}
_code_to_fullname = {'reqd': ('_builtinSuites.builtin_Suite', 'builtin_Suite'),
 'core': ('_builtinSuites.builtin_Suite', 'builtin_Suite')}
from builtin_Suite import *

class _builtinSuites(builtin_Suite_Events, aetools.TalkTo):
    _signature = 'ascr'
