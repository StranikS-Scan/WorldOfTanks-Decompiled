# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/py2to3/patched_typing.py
from __future__ import absolute_import
import abc
import typing
from future.utils import PY2
if not typing.TYPE_CHECKING and PY2:

    class _RuntimeGenericMeta(abc.ABCMeta):

        def __getitem__(cls, item):
            return cls


    class Generic(object):
        __metaclass__ = _RuntimeGenericMeta
        __slots__ = ()


else:
    from typing import Generic
__all__ = ('Generic',)
