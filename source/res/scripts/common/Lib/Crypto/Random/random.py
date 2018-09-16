# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/Crypto/Random/random.py
__revision__ = '$Id$'
__all__ = ['StrongRandom',
 'getrandbits',
 'randrange',
 'randint',
 'choice',
 'shuffle',
 'sample']
from Crypto import Random
import sys
if sys.version_info[0] == 2 and sys.version_info[1] == 1:
    from Crypto.Util.py21compat import *

class StrongRandom(object):

    def __init__(self, rng=None, randfunc=None):
        if randfunc is None and rng is None:
            self._randfunc = None
        elif randfunc is not None and rng is None:
            self._randfunc = randfunc
        elif randfunc is None and rng is not None:
            self._randfunc = rng.read
        else:
            raise ValueError("Cannot specify both 'rng' and 'randfunc'")
        return

    def getrandbits(self, k):
        if self._randfunc is None:
            self._randfunc = Random.new().read
        mask = (1L << k) - 1
        return mask & bytes_to_long(self._randfunc(ceil_div(k, 8)))

    def randrange(self, *args):
        if len(args) == 3:
            start, stop, step = args
        elif len(args) == 2:
            start, stop = args
            step = 1
        elif len(args) == 1:
            stop = args
            start = 0
            step = 1
        else:
            raise TypeError('randrange expected at most 3 arguments, got %d' % (len(args),))
        if not isinstance(start, (int, long)) or not isinstance(stop, (int, long)) or not isinstance(step, (int, long)):
            raise TypeError('randrange requires integer arguments')
        if step == 0:
            raise ValueError('randrange step argument must not be zero')
        num_choices = ceil_div(stop - start, step)
        if num_choices < 0:
            num_choices = 0
        if num_choices < 1:
            raise ValueError('empty range for randrange(%r, %r, %r)' % (start, stop, step))
        r = num_choices
        while r >= num_choices:
            r = self.getrandbits(size(num_choices))

        return start + step * r

    def randint(self, a, b):
        if not isinstance(a, (int, long)) or not isinstance(b, (int, long)):
            raise TypeError('randint requires integer arguments')
        N = self.randrange(a, b + 1)
        return N

    def choice(self, seq):
        if len(seq) == 0:
            raise IndexError('empty sequence')
        return seq[self.randrange(len(seq))]

    def shuffle(self, x):
        for i in xrange(len(x) - 1, 0, -1):
            j = self.randrange(0, i + 1)
            x[i], x[j] = x[j], x[i]

    def sample(self, population, k):
        num_choices = len(population)
        if k > num_choices:
            raise ValueError('sample larger than population')
        retval = []
        selected = {}
        for i in xrange(k):
            r = None
            while r is None or selected.has_key(r):
                r = self.randrange(num_choices)

            retval.append(population[r])
            selected[r] = 1

        return retval


_r = StrongRandom()
getrandbits = _r.getrandbits
randrange = _r.randrange
randint = _r.randint
choice = _r.choice
shuffle = _r.shuffle
sample = _r.sample
from Crypto.Util.number import ceil_div, bytes_to_long, long_to_bytes, size
