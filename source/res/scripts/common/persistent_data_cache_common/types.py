# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/persistent_data_cache_common/types.py
from __future__ import absolute_import
import typing
TData = typing.TypeVar('TData')
TDataFactory = typing.Callable[[], TData]
TPDCVersion = typing.Tuple[str, ...]
