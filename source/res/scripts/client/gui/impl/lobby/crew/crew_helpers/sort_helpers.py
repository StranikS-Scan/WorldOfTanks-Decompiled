# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/crew_helpers/sort_helpers.py
import heapq
import math
from gui.shared.utils.requesters import REQ_CRITERIA, RequestCriteria

class SortRequestCriteria(RequestCriteria):
    __slots__ = ()
    MAX_MASK = 4294967295L
    MAX_CONDITIONS_NUM = int(round(math.log(MAX_MASK, 2)))

    def __init__(self, other):
        super(SortRequestCriteria, self).__init__(*other.conditions[:self.MAX_CONDITIONS_NUM])

    def __call__(self, item):
        res = 0
        for power, condition in enumerate(self.conditions):
            if condition(item):
                res = 1 << power
                break

        return res & self.MAX_MASK or self.MAX_MASK


class KeySortRequestCriteria(RequestCriteria):
    __slots__ = ()

    def __init__(self, other):
        super(KeySortRequestCriteria, self).__init__(*other.conditions)

    def __call__(self, item):
        res = ()
        for _, c in enumerate(self.conditions):
            res = res + (c(item),)

        return res


class SortHeap(object):
    __slot__ = ('key', 'condition', 'data')

    def __init__(self, items=None, criteria=REQ_CRITERIA.EMPTY, keys=REQ_CRITERIA.CUSTOM(lambda item: tuple())):
        self.condition = SortRequestCriteria(criteria)
        self.key = KeySortRequestCriteria(keys)
        self.data = list(((self.condition(item),) + self.key(item) + (i, item) for i, item in enumerate(items or [])))
        self.rebuild()

    def rebuild(self):
        if self.data:
            heapq.heapify(self.data)

    def push(self, item):
        heapq.heappush(self.data, (self.condition(item),) + self.key(item) + (len(self.data), item))

    def pop(self):
        return heapq.heappop(self.data)[-1] if self.data else None

    def remove(self, item):
        if not self.data:
            return
        for _, row in enumerate(self.data):
            if row[-1] != item:
                continue
            self.data.remove(row)

    def updateRoot(self, item=None, criteria=REQ_CRITERIA.EMPTY, keys=REQ_CRITERIA.CUSTOM(lambda item: tuple())):
        self.condition = SortRequestCriteria(criteria)
        self.key = KeySortRequestCriteria(keys)
        if item is None:
            return
        else:
            if self.data:
                root = heapq.heappop(self.data)[-1]
                if root != item:
                    self.push(root)
            self.remove(item)
            self.push(item)
            return

    def getSortedList(self):
        sortedList = []
        data = self.data[:]
        while data:
            sortedList.append(heapq.heappop(data)[-1])

        return sortedList
