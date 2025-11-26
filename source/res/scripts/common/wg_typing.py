# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/wg_typing.py
import typing
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import *
    __all__ = locals().keys()
else:
    __all__ = ('typing', 'TYPE_CHECKING')
