# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/random.py
# Compiled at: 2003-05-14 09:57:53
"""Random variable generators.

    integers
    --------
           uniform within range

    sequences
    ---------
           pick random element
           pick random sample
           generate random permutation

    distributions on the real line:
    ------------------------------
           uniform
           triangular
           normal (Gaussian)
           lognormal
           negative exponential
           gamma
           beta
           pareto
           Weibull

    distributions on the circle (angles 0 to 2pi)
    ---------------------------------------------
           circular uniform
           von Mises

General notes on the underlying Mersenne Twister core generator:

* The period is 2**19937-1.
* It is one of the most extensively tested generators in existence.
* Without a direct way to compute N steps forward, the semantics of
  jumpahead(n) are weakened to simply jump to another distant state and rely
  on the large period to avoid overlapping sequences.
* The random() method is implemented in C, executes in a single Python step,
  and is, therefore, threadsafe.

"""
from __future__ import division
from warnings import warn as _warn
from types import MethodType as _MethodType, BuiltinMethodType as _BuiltinMethodType
from math import log as _log, exp as _exp, pi as _pi, e as _e, ceil as _ceil
from math import sqrt as _sqrt, acos as _acos, cos as _cos, sin as _sin
from os import urandom as _urandom
from binascii import hexlify as _hexlify
import hashlib as _hashlib
__all__ = ['Random',
 'seed',
 'random',
 'uniform',
 'randint',
 'choice',
 'sample',
 'randrange',
 'shuffle',
 'normalvariate',
 'lognormvariate',
 'expovariate',
 'vonmisesvariate',
 'gammavariate',
 'triangular',
 'gauss',
 'betavariate',
 'paretovariate',
 'weibullvariate',
 'getstate',
 'setstate',
 'jumpahead',
 'WichmannHill',
 'getrandbits',
 'SystemRandom']
NV_MAGICCONST = 4 * _exp(-0.5) / _sqrt(2.0)
TWOPI = 2.0 * _pi
LOG4 = _log(4.0)
SG_MAGICCONST = 1.0 + _log(4.5)
BPF = 53
RECIP_BPF = 2 ** (-BPF)
import _random

class Random(_random.Random):
    """Random number generator base class used by bound module functions.
    
    Used to instantiate instances of Random to get generators that don't
    share state.  Especially useful for multi-threaded programs, creating
    a different instance of Random for each thread, and using the jumpahead()
    method to ensure that the generated sequences seen by each thread don't
    overlap.
    
    Class Random can also be subclassed if you want to use a different basic
    generator of your own devising: in that case, override the following
    methods: random(), seed(), getstate(), setstate() and jumpahead().
    Optionally, implement a getrandbits() method so that randrange() can cover
    arbitrarily large ranges.
    
    """
    VERSION = 3

    def __init__(self, x=None):
        """Initialize an instance.
        
        Optional argument x controls seeding, as for Random.seed().
        """
        self.seed(x)
        self.gauss_next = None
        return

    def seed(self, a=None):
        """Initialize internal state of the random number generator.
        
        None or no argument seeds from current time or from an operating
        system specific randomness source if available.
        
        If a is not None or is an int or long, hash(a) is used instead.
        Hash values for some types are nondeterministic when the
        PYTHONHASHSEED environment variable is enabled.
        """
        if a is None:
            try:
                a = long(_hexlify(_urandom(2500)), 16)
            except NotImplementedError:
                import time
                a = long(time.time() * 256)

        super(Random, self).seed(a)
        self.gauss_next = None
        return

    def getstate(self):
        """Return internal state; can be passed to setstate() later."""
        return (self.VERSION, super(Random, self).getstate(), self.gauss_next)

    def setstate(self, state):
        """Restore internal state from object returned by getstate()."""
        version = state[0]
        if version == 3:
            version, internalstate, self.gauss_next = state
            super(Random, self).setstate(internalstate)
        elif version == 2:
            version, internalstate, self.gauss_next = state
            try:
                internalstate = tuple((long(x) % 4294967296L for x in internalstate))
            except ValueError as e:
                raise TypeError, e

            super(Random, self).setstate(internalstate)
        else:
            raise ValueError('state with version %s passed to Random.setstate() of version %s' % (version, self.VERSION))

    def jumpahead(self, n):
        """Change the internal state to one that is likely far away
        from the current state.  This method will not be in Py3.x,
        so it is better to simply reseed.
        """
        s = repr(n) + repr(self.getstate())
        n = int(_hashlib.new('sha512', s).hexdigest(), 16)
        super(Random, self).jumpahead(n)

    def __getstate__(self):
        return self.getstate()

    def __setstate__(self, state):
        self.setstate(state)

    def __reduce__(self):
        return (self.__class__, (), self.getstate())

    def randrange(self, start, stop=None, step=1, _int=int, _maxwidth=1L << BPF):
        """Choose a random item from range(start, stop[, step]).
        
        This fixes the problem with randint() which includes the
        endpoint; in Python this is usually not what you want.
        
        """
        istart = _int(start)
        if istart != start:
            raise ValueError, 'non-integer arg 1 for randrange()'
        if stop is None:
            if istart > 0:
                if istart >= _maxwidth:
                    return self._randbelow(istart)
                return _int(self.random() * istart)
            raise ValueError, 'empty range for randrange()'
        istop = _int(stop)
        if istop != stop:
            raise ValueError, 'non-integer stop for randrange()'
        width = istop - istart
        if step == 1 and width > 0:
            if width >= _maxwidth:
                return _int(istart + self._randbelow(width))
            return _int(istart + _int(self.random() * width))
        else:
            if step == 1:
                raise ValueError, 'empty range for randrange() (%d,%d, %d)' % (istart, istop, width)
            istep = _int(step)
            if istep != step:
                raise ValueError, 'non-integer step for randrange()'
            if istep > 0:
                n = (width + istep - 1) // istep
            elif istep < 0:
                n = (width + istep + 1) // istep
            else:
                raise ValueError, 'zero step for randrange()'
            if n <= 0:
                raise ValueError, 'empty range for randrange()'
            return istart + istep * self._randbelow(n) if n >= _maxwidth else istart + istep * _int(self.random() * n)

    def randint(self, a, b):
        """Return random integer in range [a, b], including both end points.
        """
        return self.randrange(a, b + 1)

    def _randbelow(self, n, _log=_log, _int=int, _maxwidth=1L << BPF, _Method=_MethodType, _BuiltinMethod=_BuiltinMethodType):
        """Return a random int in the range [0,n)
        
        Handles the case where n has more bits than returned
        by a single call to the underlying generator.
        """
        try:
            getrandbits = self.getrandbits
        except AttributeError:
            pass
        else:
            if type(self.random) is _BuiltinMethod or type(getrandbits) is _Method:
                k = _int(1.00001 + _log(n - 1, 2.0))
                r = getrandbits(k)
                while r >= n:
                    r = getrandbits(k)

                return r

        if n >= _maxwidth:
            _warn('Underlying random() generator does not supply \nenough bits to choose from a population range this large')
        return _int(self.random() * n)

    def choice(self, seq):
        """Choose a random element from a non-empty sequence."""
        return seq[int(self.random() * len(seq))]

    def shuffle(self, x, random=None):
        """x, random=random.random -> shuffle list x in place; return None.
        
        Optional arg random is a 0-argument function returning a random
        float in [0.0, 1.0); by default, the standard random.random.
        
        """
        if random is None:
            random = self.random
        _int = int
        for i in reversed(xrange(1, len(x))):
            j = _int(random() * (i + 1))
            x[i], x[j] = x[j], x[i]

        return

    def sample(self, population, k):
        """Chooses k unique random elements from a population sequence.
        
        Returns a new list containing elements from the population while
        leaving the original population unchanged.  The resulting list is
        in selection order so that all sub-slices will also be valid random
        samples.  This allows raffle winners (the sample) to be partitioned
        into grand prize and second place winners (the subslices).
        
        Members of the population need not be hashable or unique.  If the
        population contains repeats, then each occurrence is a possible
        selection in the sample.
        
        To choose a sample in a range of integers, use xrange as an argument.
        This is especially fast and space efficient for sampling from a
        large population:   sample(xrange(10000000), 60)
        """
        n = len(population)
        if not 0 <= k <= n:
            raise ValueError('sample larger than population')
        random = self.random
        _int = int
        result = [None] * k
        setsize = 21
        if k > 5:
            setsize += 4 ** _ceil(_log(k * 3, 4))
        if n <= setsize or hasattr(population, 'keys'):
            pool = list(population)
            for i in xrange(k):
                j = _int(random() * (n - i))
                result[i] = pool[j]
                pool[j] = pool[n - i - 1]

        else:
            try:
                selected = set()
                selected_add = selected.add
                for i in xrange(k):
                    j = _int(random() * n)
                    while j in selected:
                        j = _int(random() * n)

                    selected_add(j)
                    result[i] = population[j]

            except (TypeError, KeyError):
                if isinstance(population, list):
                    raise
                return self.sample(tuple(population), k)

        return result

    def uniform(self, a, b):
        """Get a random number in the range [a, b) or [a, b] depending on rounding."""
        return a + (b - a) * self.random()

    def triangular(self, low=0.0, high=1.0, mode=None):
        """Triangular distribution.
        
        Continuous distribution bounded by given lower and upper limits,
        and having a given mode value in-between.
        
        http://en.wikipedia.org/wiki/Triangular_distribution
        
        """
        u = self.random()
        try:
            c = 0.5 if mode is None else (mode - low) / (high - low)
        except ZeroDivisionError:
            return low

        if u > c:
            u = 1.0 - u
            c = 1.0 - c
            low, high = high, low
        return low + (high - low) * (u * c) ** 0.5

    def normalvariate(self, mu, sigma):
        """Normal distribution.
        
        mu is the mean, and sigma is the standard deviation.
        
        """
        random = self.random
        while 1:
            u1 = random()
            u2 = 1.0 - random()
            z = NV_MAGICCONST * (u1 - 0.5) / u2
            zz = z * z / 4.0
            if zz <= -_log(u2):
                break

        return mu + z * sigma

    def lognormvariate(self, mu, sigma):
        """Log normal distribution.
        
        If you take the natural logarithm of this distribution, you'll get a
        normal distribution with mean mu and standard deviation sigma.
        mu can have any value, and sigma must be greater than zero.
        
        """
        return _exp(self.normalvariate(mu, sigma))

    def expovariate(self, lambd):
        """Exponential distribution.
        
        lambd is 1.0 divided by the desired mean.  It should be
        nonzero.  (The parameter would be called "lambda", but that is
        a reserved word in Python.)  Returned values range from 0 to
        positive infinity if lambd is positive, and from negative
        infinity to 0 if lambd is negative.
        
        """
        return -_log(1.0 - self.random()) / lambd

    def vonmisesvariate(self, mu, kappa):
        """Circular data distribution.
        
        mu is the mean angle, expressed in radians between 0 and 2*pi, and
        kappa is the concentration parameter, which must be greater than or
        equal to zero.  If kappa is equal to zero, this distribution reduces
        to a uniform random angle over the range 0 to 2*pi.
        
        """
        random = self.random
        if kappa <= 1e-06:
            return TWOPI * random()
        s = 0.5 / kappa
        r = s + _sqrt(1.0 + s * s)
        while 1:
            u1 = random()
            z = _cos(_pi * u1)
            d = z / (r + z)
            u2 = random()
            if u2 < 1.0 - d * d or u2 <= (1.0 - d) * _exp(d):
                break

        q = 1.0 / r
        f = (q + z) / (1.0 + q * z)
        u3 = random()
        if u3 > 0.5:
            theta = (mu + _acos(f)) % TWOPI
        else:
            theta = (mu - _acos(f)) % TWOPI
        return theta

    def gammavariate(self, alpha, beta):
        """Gamma distribution.  Not the gamma function!
        
        Conditions on the parameters are alpha > 0 and beta > 0.
        
        The probability distribution function is:
        
                    x ** (alpha - 1) * math.exp(-x / beta)
          pdf(x) =  --------------------------------------
                      math.gamma(alpha) * beta ** alpha
        
        """
        if alpha <= 0.0 or beta <= 0.0:
            raise ValueError, 'gammavariate: alpha and beta must be > 0.0'
        random = self.random
        if alpha > 1.0:
            ainv = _sqrt(2.0 * alpha - 1.0)
            bbb = alpha - LOG4
            ccc = alpha + ainv
            while 1:
                u1 = random()
                if not 1e-07 < u1 < 0.9999999:
                    continue
                u2 = 1.0 - random()
                v = _log(u1 / (1.0 - u1)) / ainv
                x = alpha * _exp(v)
                z = u1 * u1 * u2
                r = bbb + ccc * v - x
                if r + SG_MAGICCONST - 4.5 * z >= 0.0 or r >= _log(z):
                    return x * beta

        else:
            if alpha == 1.0:
                u = random()
                while u <= 1e-07:
                    u = random()

                return -_log(u) * beta
            while 1:
                u = random()
                b = (_e + alpha) / _e
                p = b * u
                if p <= 1.0:
                    x = p ** (1.0 / alpha)
                else:
                    x = -_log((b - p) / alpha)
                u1 = random()
                if p > 1.0:
                    if u1 <= x ** (alpha - 1.0):
                        break
                if u1 <= _exp(-x):
                    break

            return x * beta

    def gauss(self, mu, sigma):
        """Gaussian distribution.
        
        mu is the mean, and sigma is the standard deviation.  This is
        slightly faster than the normalvariate() function.
        
        Not thread-safe without a lock around calls.
        
        """
        random = self.random
        z = self.gauss_next
        self.gauss_next = None
        if z is None:
            x2pi = random() * TWOPI
            g2rad = _sqrt(-2.0 * _log(1.0 - random()))
            z = _cos(x2pi) * g2rad
            self.gauss_next = _sin(x2pi) * g2rad
        return mu + z * sigma

    def betavariate(self, alpha, beta):
        """Beta distribution.
        
        Conditions on the parameters are alpha > 0 and beta > 0.
        Returned values range between 0 and 1.
        
        """
        y = self.gammavariate(alpha, 1.0)
        if y == 0:
            return 0.0
        else:
            return y / (y + self.gammavariate(beta, 1.0))

    def paretovariate(self, alpha):
        """Pareto distribution.  alpha is the shape parameter."""
        u = 1.0 - self.random()
        return 1.0 / pow(u, 1.0 / alpha)

    def weibullvariate(self, alpha, beta):
        """Weibull distribution.
        
        alpha is the scale parameter and beta is the shape parameter.
        
        """
        u = 1.0 - self.random()
        return alpha * pow(-_log(u), 1.0 / beta)


class WichmannHill(Random):
    VERSION = 1

    def seed(self, a=None):
        """Initialize internal state from hashable object.
        
        None or no argument seeds from current time or from an operating
        system specific randomness source if available.
        
        If a is not None or an int or long, hash(a) is used instead.
        
        If a is an int or long, a is used directly.  Distinct values between
        0 and 27814431486575L inclusive are guaranteed to yield distinct
        internal states (this guarantee is specific to the default
        Wichmann-Hill generator).
        """
        if a is None:
            try:
                a = long(_hexlify(_urandom(16)), 16)
            except NotImplementedError:
                import time
                a = long(time.time() * 256)

        if not isinstance(a, (int, long)):
            a = hash(a)
        a, x = divmod(a, 30268)
        a, y = divmod(a, 30306)
        a, z = divmod(a, 30322)
        self._seed = (int(x) + 1, int(y) + 1, int(z) + 1)
        self.gauss_next = None
        return

    def random(self):
        """Get the next random number in the range [0.0, 1.0)."""
        x, y, z = self._seed
        x = 171 * x % 30269
        y = 172 * y % 30307
        z = 170 * z % 30323
        self._seed = (x, y, z)
        return (x / 30269.0 + y / 30307.0 + z / 30323.0) % 1.0

    def getstate(self):
        """Return internal state; can be passed to setstate() later."""
        return (self.VERSION, self._seed, self.gauss_next)

    def setstate(self, state):
        """Restore internal state from object returned by getstate()."""
        version = state[0]
        if version == 1:
            version, self._seed, self.gauss_next = state
        else:
            raise ValueError('state with version %s passed to Random.setstate() of version %s' % (version, self.VERSION))

    def jumpahead(self, n):
        """Act as if n calls to random() were made, but quickly.
        
        n is an int, greater than or equal to 0.
        
        Example use:  If you have 2 threads and know that each will
        consume no more than a million random numbers, create two Random
        objects r1 and r2, then do
            r2.setstate(r1.getstate())
            r2.jumpahead(1000000)
        Then r1 and r2 will use guaranteed-disjoint segments of the full
        period.
        """
        if not n >= 0:
            raise ValueError('n must be >= 0')
        x, y, z = self._seed
        x = int(x * pow(171, n, 30269)) % 30269
        y = int(y * pow(172, n, 30307)) % 30307
        z = int(z * pow(170, n, 30323)) % 30323
        self._seed = (x, y, z)

    def __whseed(self, x=0, y=0, z=0):
        """Set the Wichmann-Hill seed from (x, y, z).
        
        These must be integers in the range [0, 256).
        """
        if not type(x) == type(y) == type(z) == int:
            raise TypeError('seeds must be integers')
        if not (0 <= x < 256 and 0 <= y < 256 and 0 <= z < 256):
            raise ValueError('seeds must be in range(0, 256)')
        if 0 == x == y == z:
            import time
            t = long(time.time() * 256)
            t = int(t & 16777215 ^ t >> 24)
            t, x = divmod(t, 256)
            t, y = divmod(t, 256)
            t, z = divmod(t, 256)
        self._seed = (x or 1, y or 1, z or 1)
        self.gauss_next = None
        return

    def whseed(self, a=None):
        """Seed from hashable object's hash code.
        
        None or no argument seeds from current time.  It is not guaranteed
        that objects with distinct hash codes lead to distinct internal
        states.
        
        This is obsolete, provided for compatibility with the seed routine
        used prior to Python 2.1.  Use the .seed() method instead.
        """
        if a is None:
            self.__whseed()
            return
        else:
            a = hash(a)
            a, x = divmod(a, 256)
            a, y = divmod(a, 256)
            a, z = divmod(a, 256)
            x = (x + a) % 256 or 1
            y = (y + a) % 256 or 1
            z = (z + a) % 256 or 1
            self.__whseed(x, y, z)
            return


class SystemRandom(Random):
    """Alternate random number generator using sources provided
    by the operating system (such as /dev/urandom on Unix or
    CryptGenRandom on Windows).
    
     Not available on all systems (see os.urandom() for details).
    """

    def random(self):
        """Get the next random number in the range [0.0, 1.0)."""
        return (long(_hexlify(_urandom(7)), 16) >> 3) * RECIP_BPF

    def getrandbits(self, k):
        """getrandbits(k) -> x.  Generates a long int with k random bits."""
        if k <= 0:
            raise ValueError('number of bits must be greater than zero')
        if k != int(k):
            raise TypeError('number of bits should be an integer')
        bytes = (k + 7) // 8
        x = long(_hexlify(_urandom(bytes)), 16)
        return x >> bytes * 8 - k

    def _stub(self, *args, **kwds):
        """Stub method.  Not used for a system random number generator."""
        return None

    seed = jumpahead = _stub

    def _notimplemented(self, *args, **kwds):
        """Method should not be called for a system random number generator."""
        raise NotImplementedError('System entropy source does not have state.')

    getstate = setstate = _notimplemented


def _test_generator(n, func, args):
    import time
    print n, 'times', func.__name__
    total = 0.0
    sqsum = 0.0
    smallest = 10000000000.0
    largest = -10000000000.0
    t0 = time.time()
    for i in range(n):
        x = func(*args)
        total += x
        sqsum = sqsum + x * x
        smallest = min(x, smallest)
        largest = max(x, largest)

    t1 = time.time()
    print round(t1 - t0, 3), 'sec,',
    avg = total / n
    stddev = _sqrt(sqsum / n - avg * avg)
    print 'avg %g, stddev %g, min %g, max %g' % (avg,
     stddev,
     smallest,
     largest)


def _test(N=2000):
    _test_generator(N, random, ())
    _test_generator(N, normalvariate, (0.0, 1.0))
    _test_generator(N, lognormvariate, (0.0, 1.0))
    _test_generator(N, vonmisesvariate, (0.0, 1.0))
    _test_generator(N, gammavariate, (0.01, 1.0))
    _test_generator(N, gammavariate, (0.1, 1.0))
    _test_generator(N, gammavariate, (0.1, 2.0))
    _test_generator(N, gammavariate, (0.5, 1.0))
    _test_generator(N, gammavariate, (0.9, 1.0))
    _test_generator(N, gammavariate, (1.0, 1.0))
    _test_generator(N, gammavariate, (2.0, 1.0))
    _test_generator(N, gammavariate, (20.0, 1.0))
    _test_generator(N, gammavariate, (200.0, 1.0))
    _test_generator(N, gauss, (0.0, 1.0))
    _test_generator(N, betavariate, (3.0, 3.0))
    _test_generator(N, triangular, (0.0, 1.0, 0.3333333333333333))


_inst = Random()
seed = _inst.seed
random = _inst.random
uniform = _inst.uniform
triangular = _inst.triangular
randint = _inst.randint
choice = _inst.choice
randrange = _inst.randrange
sample = _inst.sample
shuffle = _inst.shuffle
normalvariate = _inst.normalvariate
lognormvariate = _inst.lognormvariate
expovariate = _inst.expovariate
vonmisesvariate = _inst.vonmisesvariate
gammavariate = _inst.gammavariate
gauss = _inst.gauss
betavariate = _inst.betavariate
paretovariate = _inst.paretovariate
weibullvariate = _inst.weibullvariate
getstate = _inst.getstate
setstate = _inst.setstate
jumpahead = _inst.jumpahead
getrandbits = _inst.getrandbits
if __name__ == '__main__':
    _test()
