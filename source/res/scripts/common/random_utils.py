# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/random_utils.py
import itertools
import random
from bisect import bisect
from copy import deepcopy
import typing

class wchoices(object):

    def __init__(self, elist, wlist=None):
        if not set(elist):
            raise IndexError
        evtLen = len(elist)
        norm = float(evtLen if wlist is None else sum(wlist[:evtLen]))
        self.welist = tuple((((i + 1 if wlist is None else sum(wlist[:i + 1])) / norm, elist[i]) for i in xrange(evtLen)))
        return

    def nseq(self, count=1):
        return list(itertools.islice(self, count))

    def ncounts(self, count):
        data = sorted(self.nseq(count))
        return dict(((k, len(list(g))) for k, g in itertools.groupby(data)))

    def __iter__(self):
        welist = deepcopy(self.welist)

        def wrapper():
            for r in iter(random.random, -1):
                for w, e in welist:
                    if w > r:
                        yield e
                        break
                else:
                    raise LookupError('At least one option must be selected from %s', welist)

        return wrapper()


def getValueWithDeviationInPercent(value, deviation):
    return value + value * (random.randint(-deviation, deviation) / 100.0)


def weighted_choice(seq, weights):
    total = 0
    cum_weights = []
    for w in weights:
        total += w
        cum_weights.append(total)

    x = random.random() * total
    i = bisect(cum_weights, x)
    if i >= len(seq):
        i = len(seq) - 1
    return seq[i]
