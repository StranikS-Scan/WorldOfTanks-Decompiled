# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/py2to3/backport/inspect.py
from __future__ import absolute_import
import inspect
from future.utils import lmap
from py2to3.utils import PY3

def _joinseq(seq):
    return '(' + seq[0] + ',)' if len(seq) == 1 else '(' + ', '.join(seq) + ')'


def _strseq(obj, convert, join=_joinseq):
    return join(lmap(lambda o, c=convert, j=join: _strseq(o, c, j), obj)) if isinstance(obj, (list, tuple)) else convert(obj)


def getargspec(func):
    return inspect.getfullargspec(func) if PY3 else inspect.getargspec(func)


def formatargspec(args, varargs=None, varkw=None, defaults=None, kwonlyargs=None, kwonlydefaults=None, annotations=None, formatarg=str, formatvarargs=lambda name: '*' + name, formatvarkw=lambda name: '**' + name, formatvalue=lambda value: '=' + repr(value), join=_joinseq):
    specs = []
    if defaults:
        firstdefault = len(args) - len(defaults)
    for i, arg in enumerate(args):
        spec = _strseq(arg, formatarg, join)
        if defaults and i >= firstdefault:
            spec = spec + formatvalue(defaults[i - firstdefault])
        specs.append(spec)

    if varargs is not None:
        specs.append(formatvarargs(varargs))
    if varkw is not None:
        specs.append(formatvarkw(varkw))
    return '(' + ', '.join(specs) + ')'
