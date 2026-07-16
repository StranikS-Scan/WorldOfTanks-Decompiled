# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/py2to3/patched_future.py
from __future__ import absolute_import
from typing import TYPE_CHECKING
if TYPE_CHECKING:

    def with_metaclass(meta, *bases):
        return meta('temporary_class', bases, {})


else:
    from future.utils import with_metaclass
