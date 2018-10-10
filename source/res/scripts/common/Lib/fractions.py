# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/fractions.py
from __future__ import division
from decimal import Decimal
import math
import numbers
import operator
import re
__all__ = ['Fraction', 'gcd']
Rational = numbers.Rational

def gcd(a, b):
    while b:
        a, b = b, a % b

    return a


_RATIONAL_FORMAT = re.compile('\n    \\A\\s*                      # optional whitespace at the start, then\n    (?P<sign>[-+]?)            # an optional sign, then\n    (?=\\d|\\.\\d)                # lookahead for digit or .digit\n    (?P<num>\\d*)               # numerator (possibly empty)\n    (?:                        # followed by\n       (?:/(?P<denom>\\d+))?    # an optional denominator\n    |                          # or\n       (?:\\.(?P<decimal>\\d*))? # an optional fractional part\n       (?:E(?P<exp>[-+]?\\d+))? # and optional exponent\n    )\n    \\s*\\Z                      # and optional whitespace to finish\n', re.VERBOSE | re.IGNORECASE)

class Fraction(Rational):
    __slots__ = ('_numerator', '_denominator')

    def __new__(cls, numerator=0, denominator=None):
        self = super(Fraction, cls).__new__(cls)
        if denominator is None:
            if isinstance(numerator, Rational):
                self._numerator = numerator.numerator
                self._denominator = numerator.denominator
                return self
            if isinstance(numerator, float):
                value = Fraction.from_float(numerator)
                self._numerator = value._numerator
                self._denominator = value._denominator
                return self
            if isinstance(numerator, Decimal):
                value = Fraction.from_decimal(numerator)
                self._numerator = value._numerator
                self._denominator = value._denominator
                return self
            if isinstance(numerator, basestring):
                m = _RATIONAL_FORMAT.match(numerator)
                if m is None:
                    raise ValueError('Invalid literal for Fraction: %r' % numerator)
                numerator = int(m.group('num') or '0')
                denom = m.group('denom')
                if denom:
                    denominator = int(denom)
                else:
                    denominator = 1
                    decimal = m.group('decimal')
                    if decimal:
                        scale = 10 ** len(decimal)
                        numerator = numerator * scale + int(decimal)
                        denominator *= scale
                    exp = m.group('exp')
                    if exp:
                        exp = int(exp)
                        if exp >= 0:
                            numerator *= 10 ** exp
                        else:
                            denominator *= 10 ** (-exp)
                if m.group('sign') == '-':
                    numerator = -numerator
            else:
                raise TypeError('argument should be a string or a Rational instance')
        elif isinstance(numerator, Rational) and isinstance(denominator, Rational):
            numerator, denominator = numerator.numerator * denominator.denominator, denominator.numerator * numerator.denominator
        else:
            raise TypeError('both arguments should be Rational instances')
        if denominator == 0:
            raise ZeroDivisionError('Fraction(%s, 0)' % numerator)
        g = gcd(numerator, denominator)
        self._numerator = numerator // g
        self._denominator = denominator // g
        return self

    @classmethod
    def from_float(cls, f):
        if isinstance(f, numbers.Integral):
            return cls(f)
        if not isinstance(f, float):
            raise TypeError('%s.from_float() only takes floats, not %r (%s)' % (cls.__name__, f, type(f).__name__))
        if math.isnan(f) or math.isinf(f):
            raise TypeError('Cannot convert %r to %s.' % (f, cls.__name__))
        return cls(*f.as_integer_ratio())

    @classmethod
    def from_decimal(cls, dec):
        from decimal import Decimal
        if isinstance(dec, numbers.Integral):
            dec = Decimal(int(dec))
        elif not isinstance(dec, Decimal):
            raise TypeError('%s.from_decimal() only takes Decimals, not %r (%s)' % (cls.__name__, dec, type(dec).__name__))
        if not dec.is_finite():
            raise TypeError('Cannot convert %s to %s.' % (dec, cls.__name__))
        sign, digits, exp = dec.as_tuple()
        digits = int(''.join(map(str, digits)))
        if sign:
            digits = -digits
        if exp >= 0:
            return cls(digits * 10 ** exp)
        else:
            return cls(digits, 10 ** (-exp))

    def limit_denominator(self, max_denominator=1000000):
        if max_denominator < 1:
            raise ValueError('max_denominator should be at least 1')
        if self._denominator <= max_denominator:
            return Fraction(self)
        p0, q0, p1, q1 = (0, 1, 1, 0)
        n, d = self._numerator, self._denominator
        while True:
            a = n // d
            q2 = q0 + a * q1
            if q2 > max_denominator:
                break
            p0, q0, p1, q1 = (p1,
             q1,
             p0 + a * p1,
             q2)
            n, d = d, n - a * d

        k = (max_denominator - q0) // q1
        bound1 = Fraction(p0 + k * p1, q0 + k * q1)
        bound2 = Fraction(p1, q1)
        if abs(bound2 - self) <= abs(bound1 - self):
            return bound2
        else:
            return bound1

    @property
    def numerator(a):
        return a._numerator

    @property
    def denominator(a):
        return a._denominator

    def __repr__(self):
        return 'Fraction(%s, %s)' % (self._numerator, self._denominator)

    def __str__(self):
        if self._denominator == 1:
            return str(self._numerator)
        else:
            return '%s/%s' % (self._numerator, self._denominator)

    def _operator_fallbacks(monomorphic_operator, fallback_operator):

        def forward(a, b):
            if isinstance(b, (int, long, Fraction)):
                return monomorphic_operator(a, b)
            elif isinstance(b, float):
                return fallback_operator(float(a), b)
            elif isinstance(b, complex):
                return fallback_operator(complex(a), b)
            else:
                return NotImplemented

        forward.__name__ = '__' + fallback_operator.__name__ + '__'
        forward.__doc__ = monomorphic_operator.__doc__

        def reverse(b, a):
            if isinstance(a, Rational):
                return monomorphic_operator(a, b)
            elif isinstance(a, numbers.Real):
                return fallback_operator(float(a), float(b))
            elif isinstance(a, numbers.Complex):
                return fallback_operator(complex(a), complex(b))
            else:
                return NotImplemented

        reverse.__name__ = '__r' + fallback_operator.__name__ + '__'
        reverse.__doc__ = monomorphic_operator.__doc__
        return (forward, reverse)

    def _add(a, b):
        return Fraction(a.numerator * b.denominator + b.numerator * a.denominator, a.denominator * b.denominator)

    __add__, __radd__ = _operator_fallbacks(_add, operator.add)

    def _sub(a, b):
        return Fraction(a.numerator * b.denominator - b.numerator * a.denominator, a.denominator * b.denominator)

    __sub__, __rsub__ = _operator_fallbacks(_sub, operator.sub)

    def _mul(a, b):
        return Fraction(a.numerator * b.numerator, a.denominator * b.denominator)

    __mul__, __rmul__ = _operator_fallbacks(_mul, operator.mul)

    def _div(a, b):
        return Fraction(a.numerator * b.denominator, a.denominator * b.numerator)

    __truediv__, __rtruediv__ = _operator_fallbacks(_div, operator.truediv)
    __div__, __rdiv__ = _operator_fallbacks(_div, operator.div)

    def __floordiv__(a, b):
        div = a / b
        if isinstance(div, Rational):
            return div.numerator // div.denominator
        else:
            return math.floor(div)

    def __rfloordiv__(b, a):
        div = a / b
        if isinstance(div, Rational):
            return div.numerator // div.denominator
        else:
            return math.floor(div)

    def __mod__(a, b):
        div = a // b
        return a - b * div

    def __rmod__(b, a):
        div = a // b
        return a - b * div

    def __pow__(a, b):
        if isinstance(b, Rational):
            if b.denominator == 1:
                power = b.numerator
                if power >= 0:
                    return Fraction(a._numerator ** power, a._denominator ** power)
                else:
                    return Fraction(a._denominator ** (-power), a._numerator ** (-power))
            else:
                return float(a) ** float(b)
        else:
            return float(a) ** b

    def __rpow__(b, a):
        if b._denominator == 1 and b._numerator >= 0:
            return a ** b._numerator
        if isinstance(a, Rational):
            return Fraction(a.numerator, a.denominator) ** b
        return a ** b._numerator if b._denominator == 1 else a ** float(b)

    def __pos__(a):
        return Fraction(a._numerator, a._denominator)

    def __neg__(a):
        return Fraction(-a._numerator, a._denominator)

    def __abs__(a):
        return Fraction(abs(a._numerator), a._denominator)

    def __trunc__(a):
        if a._numerator < 0:
            return -(-a._numerator // a._denominator)
        else:
            return a._numerator // a._denominator

    def __hash__(self):
        if self._denominator == 1:
            return hash(self._numerator)
        elif self == float(self):
            return hash(float(self))
        else:
            return hash((self._numerator, self._denominator))

    def __eq__(a, b):
        if isinstance(b, Rational):
            return a._numerator == b.numerator and a._denominator == b.denominator
        if isinstance(b, numbers.Complex) and b.imag == 0:
            b = b.real
        if isinstance(b, float):
            if math.isnan(b) or math.isinf(b):
                return 0.0 == b
            else:
                return a == a.from_float(b)
        else:
            return NotImplemented

    def _richcmp(self, other, op):
        if isinstance(other, Rational):
            return op(self._numerator * other.denominator, self._denominator * other.numerator)
        if isinstance(other, complex):
            raise TypeError('no ordering relation is defined for complex numbers')
        if isinstance(other, float):
            if math.isnan(other) or math.isinf(other):
                return op(0.0, other)
            else:
                return op(self, self.from_float(other))
        else:
            return NotImplemented

    def __lt__(a, b):
        return a._richcmp(b, operator.lt)

    def __gt__(a, b):
        return a._richcmp(b, operator.gt)

    def __le__(a, b):
        return a._richcmp(b, operator.le)

    def __ge__(a, b):
        return a._richcmp(b, operator.ge)

    def __nonzero__(a):
        return a._numerator != 0

    def __reduce__(self):
        return (self.__class__, (str(self),))

    def __copy__(self):
        return self if type(self) == Fraction else self.__class__(self._numerator, self._denominator)

    def __deepcopy__(self, memo):
        return self if type(self) == Fraction else self.__class__(self._numerator, self._denominator)
