# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/heapq.py
__about__ = 'Heap queues\n\n[explanation by Fran\xe7ois Pinard]\n\nHeaps are arrays for which a[k] <= a[2*k+1] and a[k] <= a[2*k+2] for\nall k, counting elements from 0.  For the sake of comparison,\nnon-existing elements are considered to be infinite.  The interesting\nproperty of a heap is that a[0] is always its smallest element.\n\nThe strange invariant above is meant to be an efficient memory\nrepresentation for a tournament.  The numbers below are `k\', not a[k]:\n\n                                   0\n\n                  1                                 2\n\n          3               4                5               6\n\n      7       8       9       10      11      12      13      14\n\n    15 16   17 18   19 20   21 22   23 24   25 26   27 28   29 30\n\n\nIn the tree above, each cell `k\' is topping `2*k+1\' and `2*k+2\'.  In\nan usual binary tournament we see in sports, each cell is the winner\nover the two cells it tops, and we can trace the winner down the tree\nto see all opponents s/he had.  However, in many computer applications\nof such tournaments, we do not need to trace the history of a winner.\nTo be more memory efficient, when a winner is promoted, we try to\nreplace it by something else at a lower level, and the rule becomes\nthat a cell and the two cells it tops contain three different items,\nbut the top cell "wins" over the two topped cells.\n\nIf this heap invariant is protected at all time, index 0 is clearly\nthe overall winner.  The simplest algorithmic way to remove it and\nfind the "next" winner is to move some loser (let\'s say cell 30 in the\ndiagram above) into the 0 position, and then percolate this new 0 down\nthe tree, exchanging values, until the invariant is re-established.\nThis is clearly logarithmic on the total number of items in the tree.\nBy iterating over all items, you get an O(n ln n) sort.\n\nA nice feature of this sort is that you can efficiently insert new\nitems while the sort is going on, provided that the inserted items are\nnot "better" than the last 0\'th element you extracted.  This is\nespecially useful in simulation contexts, where the tree holds all\nincoming events, and the "win" condition means the smallest scheduled\ntime.  When an event schedule other events for execution, they are\nscheduled into the future, so they can easily go into the heap.  So, a\nheap is a good structure for implementing schedulers (this is what I\nused for my MIDI sequencer :-).\n\nVarious structures for implementing schedulers have been extensively\nstudied, and heaps are good for this, as they are reasonably speedy,\nthe speed is almost constant, and the worst case is not much different\nthan the average case.  However, there are other representations which\nare more efficient overall, yet the worst cases might be terrible.\n\nHeaps are also very useful in big disk sorts.  You most probably all\nknow that a big sort implies producing "runs" (which are pre-sorted\nsequences, which size is usually related to the amount of CPU memory),\nfollowed by a merging passes for these runs, which merging is often\nvery cleverly organised[1].  It is very important that the initial\nsort produces the longest runs possible.  Tournaments are a good way\nto that.  If, using all the memory available to hold a tournament, you\nreplace and percolate items that happen to fit the current run, you\'ll\nproduce runs which are twice the size of the memory for random input,\nand much better for input fuzzily ordered.\n\nMoreover, if you output the 0\'th item on disk and get an input which\nmay not fit in the current tournament (because the value "wins" over\nthe last output value), it cannot fit in the heap, so the size of the\nheap decreases.  The freed memory could be cleverly reused immediately\nfor progressively building a second heap, which grows at exactly the\nsame rate the first heap is melting.  When the first heap completely\nvanishes, you switch heaps and start a new run.  Clever and quite\neffective!\n\nIn a word, heaps are useful memory structures to know.  I use them in\na few applications, and I think it is good to keep a `heap\' module\naround. :-)\n\n--------------------\n[1] The disk balancing algorithms which are current, nowadays, are\nmore annoying than clever, and this is a consequence of the seeking\ncapabilities of the disks.  On devices which cannot seek, like big\ntape drives, the story was quite different, and one had to be very\nclever to ensure (far in advance) that each tape movement will be the\nmost effective possible (that is, will best participate at\n"progressing" the merge).  Some tapes were even able to read\nbackwards, and this was also used to avoid the rewinding time.\nBelieve me, real good tape sorts were quite spectacular to watch!\nFrom all times, sorting has always been a Great Art! :-)\n'
__all__ = ['heappush',
 'heappop',
 'heapify',
 'heapreplace',
 'merge',
 'nlargest',
 'nsmallest',
 'heappushpop']
from itertools import islice, count, imap, izip, tee, chain
from operator import itemgetter

def cmp_lt(x, y):
    return x < y if hasattr(x, '__lt__') else not y <= x


def heappush(heap, item):
    heap.append(item)
    _siftdown(heap, 0, len(heap) - 1)


def heappop(heap):
    lastelt = heap.pop()
    if heap:
        returnitem = heap[0]
        heap[0] = lastelt
        _siftup(heap, 0)
    else:
        returnitem = lastelt
    return returnitem


def heapreplace(heap, item):
    returnitem = heap[0]
    heap[0] = item
    _siftup(heap, 0)
    return returnitem


def heappushpop(heap, item):
    if heap and cmp_lt(heap[0], item):
        item, heap[0] = heap[0], item
        _siftup(heap, 0)
    return item


def heapify(x):
    n = len(x)
    for i in reversed(xrange(n // 2)):
        _siftup(x, i)


def _heappushpop_max(heap, item):
    if heap and cmp_lt(item, heap[0]):
        item, heap[0] = heap[0], item
        _siftup_max(heap, 0)
    return item


def _heapify_max(x):
    n = len(x)
    for i in reversed(range(n // 2)):
        _siftup_max(x, i)


def nlargest(n, iterable):
    if n < 0:
        return []
    it = iter(iterable)
    result = list(islice(it, n))
    if not result:
        return result
    heapify(result)
    _heappushpop = heappushpop
    for elem in it:
        _heappushpop(result, elem)

    result.sort(reverse=True)
    return result


def nsmallest(n, iterable):
    if n < 0:
        return []
    it = iter(iterable)
    result = list(islice(it, n))
    if not result:
        return result
    _heapify_max(result)
    _heappushpop = _heappushpop_max
    for elem in it:
        _heappushpop(result, elem)

    result.sort()
    return result


def _siftdown(heap, startpos, pos):
    newitem = heap[pos]
    while pos > startpos:
        parentpos = pos - 1 >> 1
        parent = heap[parentpos]
        if cmp_lt(newitem, parent):
            heap[pos] = parent
            pos = parentpos
            continue
        break

    heap[pos] = newitem


def _siftup(heap, pos):
    endpos = len(heap)
    startpos = pos
    newitem = heap[pos]
    childpos = 2 * pos + 1
    while childpos < endpos:
        rightpos = childpos + 1
        if rightpos < endpos and not cmp_lt(heap[childpos], heap[rightpos]):
            childpos = rightpos
        heap[pos] = heap[childpos]
        pos = childpos
        childpos = 2 * pos + 1

    heap[pos] = newitem
    _siftdown(heap, startpos, pos)


def _siftdown_max(heap, startpos, pos):
    newitem = heap[pos]
    while pos > startpos:
        parentpos = pos - 1 >> 1
        parent = heap[parentpos]
        if cmp_lt(parent, newitem):
            heap[pos] = parent
            pos = parentpos
            continue
        break

    heap[pos] = newitem


def _siftup_max(heap, pos):
    endpos = len(heap)
    startpos = pos
    newitem = heap[pos]
    childpos = 2 * pos + 1
    while childpos < endpos:
        rightpos = childpos + 1
        if rightpos < endpos and not cmp_lt(heap[rightpos], heap[childpos]):
            childpos = rightpos
        heap[pos] = heap[childpos]
        pos = childpos
        childpos = 2 * pos + 1

    heap[pos] = newitem
    _siftdown_max(heap, startpos, pos)


try:
    from _heapq import *
except ImportError:
    pass

def merge(*iterables):
    _heappop, _heapreplace, _StopIteration = heappop, heapreplace, StopIteration
    _len = len
    h = []
    h_append = h.append
    for itnum, it in enumerate(map(iter, iterables)):
        try:
            next = it.next
            h_append([next(), itnum, next])
        except _StopIteration:
            pass

    heapify(h)
    while _len(h) > 1:
        try:
            while 1:
                v, itnum, next = s = h[0]
                yield v
                s[0] = next()
                _heapreplace(h, s)

        except _StopIteration:
            _heappop(h)

    if h:
        v, itnum, next = h[0]
        yield v
        for v in next.__self__:
            yield v


_nsmallest = nsmallest

def nsmallest(n, iterable, key=None):
    if n == 1:
        it = iter(iterable)
        head = list(islice(it, 1))
        if not head:
            return []
        if key is None:
            return [min(chain(head, it))]
        return [min(chain(head, it), key=key)]
    else:
        try:
            size = len(iterable)
        except (TypeError, AttributeError):
            pass
        else:
            if n >= size:
                return sorted(iterable, key=key)[:n]

        if key is None:
            it = izip(iterable, count())
            result = _nsmallest(n, it)
            return map(itemgetter(0), result)
        in1, in2 = tee(iterable)
        it = izip(imap(key, in1), count(), in2)
        result = _nsmallest(n, it)
        return map(itemgetter(2), result)


_nlargest = nlargest

def nlargest(n, iterable, key=None):
    if n == 1:
        it = iter(iterable)
        head = list(islice(it, 1))
        if not head:
            return []
        if key is None:
            return [max(chain(head, it))]
        return [max(chain(head, it), key=key)]
    else:
        try:
            size = len(iterable)
        except (TypeError, AttributeError):
            pass
        else:
            if n >= size:
                return sorted(iterable, key=key, reverse=True)[:n]

        if key is None:
            it = izip(iterable, count(0, -1))
            result = _nlargest(n, it)
            return map(itemgetter(0), result)
        in1, in2 = tee(iterable)
        it = izip(imap(key, in1), count(0, -1), in2)
        result = _nlargest(n, it)
        return map(itemgetter(2), result)


if __name__ == '__main__':
    heap = []
    data = [1,
     3,
     5,
     7,
     9,
     2,
     4,
     6,
     8,
     0]
    for item in data:
        heappush(heap, item)

    sort = []
    while heap:
        sort.append(heappop(heap))

    print sort
    import doctest
    doctest.testmod()
