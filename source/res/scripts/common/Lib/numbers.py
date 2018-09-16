# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/numbers.py
from __future__ import division
from abc import ABCMeta, abstractmethod, abstractproperty
__all__ = ['Number',
 'Complex',
 'Real',
 'Rational',
 'Integral']

class Number(object):
    __metaclass__ = ABCMeta
    __slots__ = ()
    __hash__ = None


class Complex(Number):
    __slots__ = ()

    @abstractmethod
    def __complex__(self):
        pass

    def __nonzero__(self):
        return self != 0

    @abstractproperty
    def real(self):
        raise NotImplementedError

    @abstractproperty
    def imag(self):
        raise NotImplementedError

    @abstractmethod
    def __add__(self, other):
        raise NotImplementedError

    @abstractmethod
    def __radd__(self, other):
        raise NotImplementedError

    @abstractmethod
    def __neg__(self):
        raise NotImplementedError

    @abstractmethod
    def __pos__(self):
        raise NotImplementedError

    def __sub__(self, other):
        return self + -other

    def __rsub__(self, other):
        return -self + other

    @abstractmethod
    def __mul__(self, other):
        raise NotImplementedError

    @abstractmethod
    def __rmul__(self, other):
        raise NotImplementedError

    @abstractmethod
    def __div__(self, other):
        raise NotImplementedError

    @abstractmethod
    def __rdiv__(self, other):
        raise NotImplementedError

    @abstractmethod
    def __truediv__(self, other):
        raise NotImplementedError

    @abstractmethod
    def __rtruediv__(self, other):
        raise NotImplementedError

    @abstractmethod
    def __pow__(self, exponent):
        raise NotImplementedError

    @abstractmethod
    def __rpow__(self, base):
        raise NotImplementedError

    @abstractmethod
    def __abs__(self):
        raise NotImplementedError

    @abstractmethod
    def conjugate(self):
        raise NotImplementedError

    @abstractmethod
    def __eq__(self, other):
        raise NotImplementedError

    def __ne__(self, other):
        return not self == other


Complex.register(complex)

class Real(Complex):
    __slots__ = ()

    @abstractmethod
    def __float__(self):
        raise NotImplementedError

    @abstractmethod
    def __trunc__(self):
        raise NotImplementedError

    def __divmod__(self, other):
        return (self // other, self % other)

    def __rdivmod__(self, other):
        return (other // self, other % self)

    @abstractmethod
    def __floordiv__(self, other):
        raise NotImplementedError

    @abstractmethod
    def __rfloordiv__(self, other):
        raise NotImplementedError

    @abstractmethod
    def __mod__(self, other):
        raise NotImplementedError

    @abstractmethod
    def __rmod__(self, other):
        raise NotImplementedError

    @abstractmethod
    def __lt__(self, other):
        raise NotImplementedError

    @abstractmethod
    def __le__(self, other):
        raise NotImplementedError

    def __complex__(self):
        return complex(float(self))

    @property
    def real(self):
        return +self

    @property
    def imag(self):
        pass

    def conjugate(self):
        return +self


Real.register(float)

class Rational(Real):
    __slots__ = ()

    @abstractproperty
    def numerator(self):
        raise NotImplementedError

    @abstractproperty
    def denominator(self):
        raise NotImplementedError

    def __float__(self):
        return self.numerator / self.denominator


class Integral(Rational):
    __slots__ = ()

    @abstractmethod
    def __long__(self):
        raise NotImplementedError

    def __index__(self):
        return long(self)

    @abstractmethod
    def __pow__(self, exponent, modulus=None):
        raise NotImplementedError

    @abstractmethod
    def __lshift__(self, other):
        raise NotImplementedError

    @abstractmethod
    def __rlshift__(self, other):
        raise NotImplementedError

    @abstractmethod
    def __rshift__(self, other):
        raise NotImplementedError

    @abstractmethod
    def __rrshift__(self, other):
        raise NotImplementedError

    @abstractmethod
    def __and__(self, other):
        raise NotImplementedError

    @abstractmethod
    def __rand__(self, other):
        raise NotImplementedError

    @abstractmethod
    def __xor__(self, other):
        raise NotImplementedError

    @abstractmethod
    def __rxor__(self, other):
        raise NotImplementedError

    @abstractmethod
    def __or__(self, other):
        raise NotImplementedError

    @abstractmethod
    def __ror__(self, other):
        raise NotImplementedError

    @abstractmethod
    def __invert__(self):
        raise NotImplementedError

    def __float__(self):
        return float(long(self))

    @property
    def numerator(self):
        return +self

    @property
    def denominator(self):
        pass


Integral.register(int)
Integral.register(long)
