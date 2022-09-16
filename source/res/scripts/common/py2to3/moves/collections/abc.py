# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/py2to3/moves/collections/abc.py
from __future__ import absolute_import
from future.utils import PY3
if PY3:
    from collections.abc import *
else:
    from collections import Container, Hashable, Iterable, Iterator, Sized, Callable, Sequence, MutableSequence, Set, MutableSet
    from _abcoll import MutableMapping, MappingView, ItemsView, KeysView, Mapping
