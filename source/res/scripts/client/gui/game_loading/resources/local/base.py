# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_loading/resources/local/base.py
import typing
import itertools
from gui.game_loading.resources.base import BaseResources
if typing.TYPE_CHECKING:
    from gui.game_loading.resources.models import BaseResourceModel

class LocalResources(BaseResources):
    __slots__ = ('_source', '_iterator', '_cycle')

    def __init__(self, source, cycle=False):
        super(LocalResources, self).__init__()
        self._source = list(source)
        self._cycle = cycle
        self._iterator = None
        return

    def get(self):
        if self._iterator is None:
            self._iterator = self._createIterator()
        try:
            return self._iterator.next()
        except StopIteration:
            return

        return

    def reset(self):
        if self._iterator is not None:
            self._iterator = None
        super(LocalResources, self).reset()
        return

    def destroy(self):
        super(LocalResources, self).destroy()
        self._iterator = None
        return

    def _createIterator(self):
        return itertools.cycle(self._source) if self._cycle else iter(self._source)
