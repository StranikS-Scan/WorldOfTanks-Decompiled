# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/veh_post_porgression/models/iterators.py
import typing
from collections import deque
if typing.TYPE_CHECKING:
    from gui.veh_post_porgression.models.progression import PostProgressionItem

class UnorederdStepsIterator(object):
    __slots__ = ('_postProgression', '_tree')

    def __init__(self, postProgression):
        self._postProgression = postProgression
        self._tree = postProgression.getRawTree()

    def __iter__(self):
        return (self._postProgression.getStep(stepID) for stepID in self._tree.steps.keys())


class OrderedStepsIterator(UnorederdStepsIterator):
    __slots__ = ('__fifo',)

    def __init__(self, postProgression):
        super(OrderedStepsIterator, self).__init__(postProgression)
        self.__fifo = deque((self._tree.rootStep,))

    def __iter__(self):
        return self

    def next(self):
        if not self.__fifo:
            raise StopIteration
        step = self._postProgression.getStep(self.__fifo.popleft())
        self.__fifo.extend(self._getOrderedUnlocks(step.getNextStepIDs()))
        return step

    def _getOrderedUnlocks(self, unlocks):
        return unlocks
