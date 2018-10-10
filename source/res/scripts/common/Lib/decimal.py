# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/decimal.py
__all__ = ['Decimal',
 'Context',
 'DefaultContext',
 'BasicContext',
 'ExtendedContext',
 'DecimalException',
 'Clamped',
 'InvalidOperation',
 'DivisionByZero',
 'Inexact',
 'Rounded',
 'Subnormal',
 'Overflow',
 'Underflow',
 'ROUND_DOWN',
 'ROUND_HALF_UP',
 'ROUND_HALF_EVEN',
 'ROUND_CEILING',
 'ROUND_FLOOR',
 'ROUND_UP',
 'ROUND_HALF_DOWN',
 'ROUND_05UP',
 'setcontext',
 'getcontext',
 'localcontext']
__version__ = '1.70'
import copy as _copy
import math as _math
import numbers as _numbers
try:
    from collections import namedtuple as _namedtuple
    DecimalTuple = _namedtuple('DecimalTuple', 'sign digits exponent')
except ImportError:
    DecimalTuple = lambda *args: args

ROUND_DOWN = 'ROUND_DOWN'
ROUND_HALF_UP = 'ROUND_HALF_UP'
ROUND_HALF_EVEN = 'ROUND_HALF_EVEN'
ROUND_CEILING = 'ROUND_CEILING'
ROUND_FLOOR = 'ROUND_FLOOR'
ROUND_UP = 'ROUND_UP'
ROUND_HALF_DOWN = 'ROUND_HALF_DOWN'
ROUND_05UP = 'ROUND_05UP'

class DecimalException(ArithmeticError):

    def handle(self, context, *args):
        pass


class Clamped(DecimalException):
    pass


class InvalidOperation(DecimalException):

    def handle(self, context, *args):
        if args:
            ans = _dec_from_triple(args[0]._sign, args[0]._int, 'n', True)
            return ans._fix_nan(context)
        return _NaN


class ConversionSyntax(InvalidOperation):

    def handle(self, context, *args):
        return _NaN


class DivisionByZero(DecimalException, ZeroDivisionError):

    def handle(self, context, sign, *args):
        return _SignedInfinity[sign]


class DivisionImpossible(InvalidOperation):

    def handle(self, context, *args):
        return _NaN


class DivisionUndefined(InvalidOperation, ZeroDivisionError):

    def handle(self, context, *args):
        return _NaN


class Inexact(DecimalException):
    pass


class InvalidContext(InvalidOperation):

    def handle(self, context, *args):
        return _NaN


class Rounded(DecimalException):
    pass


class Subnormal(DecimalException):
    pass


class Overflow(Inexact, Rounded):

    def handle(self, context, sign, *args):
        if context.rounding in (ROUND_HALF_UP,
         ROUND_HALF_EVEN,
         ROUND_HALF_DOWN,
         ROUND_UP):
            return _SignedInfinity[sign]
        if sign == 0:
            if context.rounding == ROUND_CEILING:
                return _SignedInfinity[sign]
            return _dec_from_triple(sign, '9' * context.prec, context.Emax - context.prec + 1)
        if sign == 1:
            if context.rounding == ROUND_FLOOR:
                return _SignedInfinity[sign]
            return _dec_from_triple(sign, '9' * context.prec, context.Emax - context.prec + 1)


class Underflow(Inexact, Rounded, Subnormal):
    pass


_signals = [Clamped,
 DivisionByZero,
 Inexact,
 Overflow,
 Rounded,
 Underflow,
 InvalidOperation,
 Subnormal]
_condition_map = {ConversionSyntax: InvalidOperation,
 DivisionImpossible: InvalidOperation,
 DivisionUndefined: InvalidOperation,
 InvalidContext: InvalidOperation}
try:
    import threading
except ImportError:
    import sys

    class MockThreading(object):

        def local(self, sys=sys):
            return sys.modules[__name__]


    threading = MockThreading()
    del sys
    del MockThreading

try:
    threading.local
except AttributeError:
    if hasattr(threading.currentThread(), '__decimal_context__'):
        del threading.currentThread().__decimal_context__

    def setcontext(context):
        if context in (DefaultContext, BasicContext, ExtendedContext):
            context = context.copy()
            context.clear_flags()
        threading.currentThread().__decimal_context__ = context


    def getcontext():
        try:
            return threading.currentThread().__decimal_context__
        except AttributeError:
            context = Context()
            threading.currentThread().__decimal_context__ = context
            return context


else:
    local = threading.local()
    if hasattr(local, '__decimal_context__'):
        del local.__decimal_context__

    def getcontext(_local=local):
        try:
            return _local.__decimal_context__
        except AttributeError:
            context = Context()
            _local.__decimal_context__ = context
            return context


    def setcontext(context, _local=local):
        if context in (DefaultContext, BasicContext, ExtendedContext):
            context = context.copy()
            context.clear_flags()
        _local.__decimal_context__ = context


    del threading
    del local

def localcontext(ctx=None):
    if ctx is None:
        ctx = getcontext()
    return _ContextManager(ctx)


class Decimal(object):
    __slots__ = ('_exp', '_int', '_sign', '_is_special')

    def __new__(cls, value='0', context=None):
        self = object.__new__(cls)
        if isinstance(value, basestring):
            m = _parser(value.strip())
            if m is None:
                if context is None:
                    context = getcontext()
                return context._raise_error(ConversionSyntax, 'Invalid literal for Decimal: %r' % value)
            if m.group('sign') == '-':
                self._sign = 1
            else:
                self._sign = 0
            intpart = m.group('int')
            if intpart is not None:
                fracpart = m.group('frac') or ''
                exp = int(m.group('exp') or '0')
                self._int = str(int(intpart + fracpart))
                self._exp = exp - len(fracpart)
                self._is_special = False
            else:
                diag = m.group('diag')
                if diag is not None:
                    self._int = str(int(diag or '0')).lstrip('0')
                    if m.group('signal'):
                        self._exp = 'N'
                    else:
                        self._exp = 'n'
                else:
                    self._int = '0'
                    self._exp = 'F'
                self._is_special = True
            return self
        elif isinstance(value, (int, long)):
            if value >= 0:
                self._sign = 0
            else:
                self._sign = 1
            self._exp = 0
            self._int = str(abs(value))
            self._is_special = False
            return self
        elif isinstance(value, Decimal):
            self._exp = value._exp
            self._sign = value._sign
            self._int = value._int
            self._is_special = value._is_special
            return self
        elif isinstance(value, _WorkRep):
            self._sign = value.sign
            self._int = str(value.int)
            self._exp = int(value.exp)
            self._is_special = False
            return self
        elif isinstance(value, (list, tuple)):
            if len(value) != 3:
                raise ValueError('Invalid tuple size in creation of Decimal from list or tuple.  The list or tuple should have exactly three elements.')
            if not (isinstance(value[0], (int, long)) and value[0] in (0, 1)):
                raise ValueError('Invalid sign.  The first value in the tuple should be an integer; either 0 for a positive number or 1 for a negative number.')
            self._sign = value[0]
            if value[2] == 'F':
                self._int = '0'
                self._exp = value[2]
                self._is_special = True
            else:
                digits = []
                for digit in value[1]:
                    if isinstance(digit, (int, long)):
                        if 0 <= digit <= 9:
                            (digits or digit != 0) and digits.append(digit)
                    raise ValueError('The second value in the tuple must be composed of integers in the range 0 through 9.')

                if value[2] in ('n', 'N'):
                    self._int = ''.join(map(str, digits))
                    self._exp = value[2]
                    self._is_special = True
                elif isinstance(value[2], (int, long)):
                    self._int = ''.join(map(str, digits or [0]))
                    self._exp = value[2]
                    self._is_special = False
                else:
                    raise ValueError("The third value in the tuple must be an integer, or one of the strings 'F', 'n', 'N'.")
            return self
        elif isinstance(value, float):
            value = Decimal.from_float(value)
            self._exp = value._exp
            self._sign = value._sign
            self._int = value._int
            self._is_special = value._is_special
            return self
        else:
            raise TypeError('Cannot convert %r to Decimal' % value)
            return

    def from_float(cls, f):
        if isinstance(f, (int, long)):
            return cls(f)
        elif _math.isinf(f) or _math.isnan(f):
            return cls(repr(f))
        if _math.copysign(1.0, f) == 1.0:
            sign = 0
        else:
            sign = 1
        n, d = abs(f).as_integer_ratio()
        k = d.bit_length() - 1
        result = _dec_from_triple(sign, str(n * 5 ** k), -k)
        if cls is Decimal:
            return result
        else:
            return cls(result)

    from_float = classmethod(from_float)

    def _isnan(self):
        if self._is_special:
            exp = self._exp
            if exp == 'n':
                return 1
            if exp == 'N':
                return 2

    def _isinfinity(self):
        if self._exp == 'F':
            if self._sign:
                return -1
            return 1

    def _check_nans(self, other=None, context=None):
        self_is_nan = self._isnan()
        if other is None:
            other_is_nan = False
        else:
            other_is_nan = other._isnan()
        if self_is_nan or other_is_nan:
            if context is None:
                context = getcontext()
            if self_is_nan == 2:
                return context._raise_error(InvalidOperation, 'sNaN', self)
            if other_is_nan == 2:
                return context._raise_error(InvalidOperation, 'sNaN', other)
            if self_is_nan:
                return self._fix_nan(context)
            return other._fix_nan(context)
        else:
            return 0

    def _compare_check_nans(self, other, context):
        if context is None:
            context = getcontext()
        if self._is_special or other._is_special:
            if self.is_snan():
                return context._raise_error(InvalidOperation, 'comparison involving sNaN', self)
            if other.is_snan():
                return context._raise_error(InvalidOperation, 'comparison involving sNaN', other)
            if self.is_qnan():
                return context._raise_error(InvalidOperation, 'comparison involving NaN', self)
            if other.is_qnan():
                return context._raise_error(InvalidOperation, 'comparison involving NaN', other)
        return 0

    def __nonzero__(self):
        return self._is_special or self._int != '0'

    def _cmp(self, other):
        if self._is_special or other._is_special:
            self_inf = self._isinfinity()
            other_inf = other._isinfinity()
            if self_inf == other_inf:
                return 0
            elif self_inf < other_inf:
                return -1
            else:
                return 1
        if not self:
            if not other:
                return 0
            else:
                return -(-1) ** other._sign
        if not other:
            return (-1) ** self._sign
        if other._sign < self._sign:
            return -1
        if self._sign < other._sign:
            return 1
        self_adjusted = self.adjusted()
        other_adjusted = other.adjusted()
        if self_adjusted == other_adjusted:
            self_padded = self._int + '0' * (self._exp - other._exp)
            other_padded = other._int + '0' * (other._exp - self._exp)
            if self_padded == other_padded:
                return 0
            elif self_padded < other_padded:
                return -(-1) ** self._sign
            else:
                return (-1) ** self._sign
        else:
            if self_adjusted > other_adjusted:
                return (-1) ** self._sign
            return -(-1) ** self._sign

    def __eq__(self, other, context=None):
        other = _convert_other(other, allow_float=True)
        if other is NotImplemented:
            return other
        return False if self._check_nans(other, context) else self._cmp(other) == 0

    def __ne__(self, other, context=None):
        other = _convert_other(other, allow_float=True)
        if other is NotImplemented:
            return other
        return True if self._check_nans(other, context) else self._cmp(other) != 0

    def __lt__(self, other, context=None):
        other = _convert_other(other, allow_float=True)
        if other is NotImplemented:
            return other
        ans = self._compare_check_nans(other, context)
        return False if ans else self._cmp(other) < 0

    def __le__(self, other, context=None):
        other = _convert_other(other, allow_float=True)
        if other is NotImplemented:
            return other
        ans = self._compare_check_nans(other, context)
        return False if ans else self._cmp(other) <= 0

    def __gt__(self, other, context=None):
        other = _convert_other(other, allow_float=True)
        if other is NotImplemented:
            return other
        ans = self._compare_check_nans(other, context)
        return False if ans else self._cmp(other) > 0

    def __ge__(self, other, context=None):
        other = _convert_other(other, allow_float=True)
        if other is NotImplemented:
            return other
        ans = self._compare_check_nans(other, context)
        return False if ans else self._cmp(other) >= 0

    def compare(self, other, context=None):
        other = _convert_other(other, raiseit=True)
        if self._is_special or other and other._is_special:
            ans = self._check_nans(other, context)
            if ans:
                return ans
        return Decimal(self._cmp(other))

    def __hash__(self):
        if self._is_special:
            if self.is_snan():
                raise TypeError('Cannot hash a signaling NaN value.')
            elif self.is_nan():
                return 0
            elif self._sign:
                return -271828
            else:
                return 314159
        self_as_float = float(self)
        if Decimal.from_float(self_as_float) == self:
            return hash(self_as_float)
        if self._isinteger():
            op = _WorkRep(self.to_integral_value())
            return hash((-1) ** op.sign * op.int * pow(10, op.exp, 18446744073709551615L))
        return hash((self._sign, self._exp + len(self._int), self._int.rstrip('0')))

    def as_tuple(self):
        return DecimalTuple(self._sign, tuple(map(int, self._int)), self._exp)

    def __repr__(self):
        return "Decimal('%s')" % str(self)

    def __str__(self, eng=False, context=None):
        sign = ['', '-'][self._sign]
        if self._is_special:
            if self._exp == 'F':
                return sign + 'Infinity'
            elif self._exp == 'n':
                return sign + 'NaN' + self._int
            else:
                return sign + 'sNaN' + self._int
        leftdigits = self._exp + len(self._int)
        if self._exp <= 0 and leftdigits > -6:
            dotplace = leftdigits
        elif not eng:
            dotplace = 1
        elif self._int == '0':
            dotplace = (leftdigits + 1) % 3 - 1
        else:
            dotplace = (leftdigits - 1) % 3 + 1
        if dotplace <= 0:
            intpart = '0'
            fracpart = '.' + '0' * -dotplace + self._int
        elif dotplace >= len(self._int):
            intpart = self._int + '0' * (dotplace - len(self._int))
            fracpart = ''
        else:
            intpart = self._int[:dotplace]
            fracpart = '.' + self._int[dotplace:]
        if leftdigits == dotplace:
            exp = ''
        else:
            if context is None:
                context = getcontext()
            exp = ['e', 'E'][context.capitals] + '%+d' % (leftdigits - dotplace)
        return sign + intpart + fracpart + exp

    def to_eng_string(self, context=None):
        return self.__str__(eng=True, context=context)

    def __neg__(self, context=None):
        if self._is_special:
            ans = self._check_nans(context=context)
            if ans:
                return ans
        if context is None:
            context = getcontext()
        if not self and context.rounding != ROUND_FLOOR:
            ans = self.copy_abs()
        else:
            ans = self.copy_negate()
        return ans._fix(context)

    def __pos__(self, context=None):
        if self._is_special:
            ans = self._check_nans(context=context)
            if ans:
                return ans
        if context is None:
            context = getcontext()
        if not self and context.rounding != ROUND_FLOOR:
            ans = self.copy_abs()
        else:
            ans = Decimal(self)
        return ans._fix(context)

    def __abs__(self, round=True, context=None):
        if not round:
            return self.copy_abs()
        if self._is_special:
            ans = self._check_nans(context=context)
            if ans:
                return ans
        if self._sign:
            ans = self.__neg__(context=context)
        else:
            ans = self.__pos__(context=context)
        return ans

    def __add__(self, other, context=None):
        other = _convert_other(other)
        if other is NotImplemented:
            return other
        else:
            if context is None:
                context = getcontext()
            if self._is_special or other._is_special:
                ans = self._check_nans(other, context)
                if ans:
                    return ans
                if self._isinfinity():
                    if self._sign != other._sign and other._isinfinity():
                        return context._raise_error(InvalidOperation, '-INF + INF')
                    return Decimal(self)
                if other._isinfinity():
                    return Decimal(other)
            exp = min(self._exp, other._exp)
            negativezero = 0
            if context.rounding == ROUND_FLOOR and self._sign != other._sign:
                negativezero = 1
            if not self and not other:
                sign = min(self._sign, other._sign)
                if negativezero:
                    sign = 1
                ans = _dec_from_triple(sign, '0', exp)
                ans = ans._fix(context)
                return ans
            if not self:
                exp = max(exp, other._exp - context.prec - 1)
                ans = other._rescale(exp, context.rounding)
                ans = ans._fix(context)
                return ans
            if not other:
                exp = max(exp, self._exp - context.prec - 1)
                ans = self._rescale(exp, context.rounding)
                ans = ans._fix(context)
                return ans
            op1 = _WorkRep(self)
            op2 = _WorkRep(other)
            op1, op2 = _normalize(op1, op2, context.prec)
            result = _WorkRep()
            if op1.sign != op2.sign:
                if op1.int == op2.int:
                    ans = _dec_from_triple(negativezero, '0', exp)
                    ans = ans._fix(context)
                    return ans
                if op1.int < op2.int:
                    op1, op2 = op2, op1
                if op1.sign == 1:
                    result.sign = 1
                    op1.sign, op2.sign = op2.sign, op1.sign
                else:
                    result.sign = 0
            elif op1.sign == 1:
                result.sign = 1
                op1.sign, op2.sign = (0, 0)
            else:
                result.sign = 0
            if op2.sign == 0:
                result.int = op1.int + op2.int
            else:
                result.int = op1.int - op2.int
            result.exp = op1.exp
            ans = Decimal(result)
            ans = ans._fix(context)
            return ans

    __radd__ = __add__

    def __sub__(self, other, context=None):
        other = _convert_other(other)
        if other is NotImplemented:
            return other
        if self._is_special or other._is_special:
            ans = self._check_nans(other, context=context)
            if ans:
                return ans
        return self.__add__(other.copy_negate(), context=context)

    def __rsub__(self, other, context=None):
        other = _convert_other(other)
        return other if other is NotImplemented else other.__sub__(self, context=context)

    def __mul__(self, other, context=None):
        other = _convert_other(other)
        if other is NotImplemented:
            return other
        else:
            if context is None:
                context = getcontext()
            resultsign = self._sign ^ other._sign
            if self._is_special or other._is_special:
                ans = self._check_nans(other, context)
                if ans:
                    return ans
                if self._isinfinity():
                    if not other:
                        return context._raise_error(InvalidOperation, '(+-)INF * 0')
                    return _SignedInfinity[resultsign]
                if other._isinfinity():
                    if not self:
                        return context._raise_error(InvalidOperation, '0 * (+-)INF')
                    return _SignedInfinity[resultsign]
            resultexp = self._exp + other._exp
            if not self or not other:
                ans = _dec_from_triple(resultsign, '0', resultexp)
                ans = ans._fix(context)
                return ans
            if self._int == '1':
                ans = _dec_from_triple(resultsign, other._int, resultexp)
                ans = ans._fix(context)
                return ans
            if other._int == '1':
                ans = _dec_from_triple(resultsign, self._int, resultexp)
                ans = ans._fix(context)
                return ans
            op1 = _WorkRep(self)
            op2 = _WorkRep(other)
            ans = _dec_from_triple(resultsign, str(op1.int * op2.int), resultexp)
            ans = ans._fix(context)
            return ans

    __rmul__ = __mul__

    def __truediv__(self, other, context=None):
        other = _convert_other(other)
        if other is NotImplemented:
            return NotImplemented
        else:
            if context is None:
                context = getcontext()
            sign = self._sign ^ other._sign
            if self._is_special or other._is_special:
                ans = self._check_nans(other, context)
                if ans:
                    return ans
                if self._isinfinity() and other._isinfinity():
                    return context._raise_error(InvalidOperation, '(+-)INF/(+-)INF')
                if self._isinfinity():
                    return _SignedInfinity[sign]
                if other._isinfinity():
                    context._raise_error(Clamped, 'Division by infinity')
                    return _dec_from_triple(sign, '0', context.Etiny())
            if not other:
                if not self:
                    return context._raise_error(DivisionUndefined, '0 / 0')
                return context._raise_error(DivisionByZero, 'x / 0', sign)
            if not self:
                exp = self._exp - other._exp
                coeff = 0
            else:
                shift = len(other._int) - len(self._int) + context.prec + 1
                exp = self._exp - other._exp - shift
                op1 = _WorkRep(self)
                op2 = _WorkRep(other)
                if shift >= 0:
                    coeff, remainder = divmod(op1.int * 10 ** shift, op2.int)
                else:
                    coeff, remainder = divmod(op1.int, op2.int * 10 ** (-shift))
                if remainder:
                    if coeff % 5 == 0:
                        coeff += 1
                else:
                    ideal_exp = self._exp - other._exp
                    while exp < ideal_exp and coeff % 10 == 0:
                        coeff //= 10
                        exp += 1

            ans = _dec_from_triple(sign, str(coeff), exp)
            return ans._fix(context)

    def _divide(self, other, context):
        sign = self._sign ^ other._sign
        if other._isinfinity():
            ideal_exp = self._exp
        else:
            ideal_exp = min(self._exp, other._exp)
        expdiff = self.adjusted() - other.adjusted()
        if not self or other._isinfinity() or expdiff <= -2:
            return (_dec_from_triple(sign, '0', 0), self._rescale(ideal_exp, context.rounding))
        if expdiff <= context.prec:
            op1 = _WorkRep(self)
            op2 = _WorkRep(other)
            if op1.exp >= op2.exp:
                op1.int *= 10 ** (op1.exp - op2.exp)
            else:
                op2.int *= 10 ** (op2.exp - op1.exp)
            q, r = divmod(op1.int, op2.int)
            if q < 10 ** context.prec:
                return (_dec_from_triple(sign, str(q), 0), _dec_from_triple(self._sign, str(r), ideal_exp))
        ans = context._raise_error(DivisionImpossible, 'quotient too large in //, % or divmod')
        return (ans, ans)

    def __rtruediv__(self, other, context=None):
        other = _convert_other(other)
        return other if other is NotImplemented else other.__truediv__(self, context=context)

    __div__ = __truediv__
    __rdiv__ = __rtruediv__

    def __divmod__(self, other, context=None):
        other = _convert_other(other)
        if other is NotImplemented:
            return other
        else:
            if context is None:
                context = getcontext()
            ans = self._check_nans(other, context)
            if ans:
                return (ans, ans)
            sign = self._sign ^ other._sign
            if self._isinfinity():
                if other._isinfinity():
                    ans = context._raise_error(InvalidOperation, 'divmod(INF, INF)')
                    return (ans, ans)
                else:
                    return (_SignedInfinity[sign], context._raise_error(InvalidOperation, 'INF % x'))
            if not other:
                if not self:
                    ans = context._raise_error(DivisionUndefined, 'divmod(0, 0)')
                    return (ans, ans)
                else:
                    return (context._raise_error(DivisionByZero, 'x // 0', sign), context._raise_error(InvalidOperation, 'x % 0'))
            quotient, remainder = self._divide(other, context)
            remainder = remainder._fix(context)
            return (quotient, remainder)

    def __rdivmod__(self, other, context=None):
        other = _convert_other(other)
        return other if other is NotImplemented else other.__divmod__(self, context=context)

    def __mod__(self, other, context=None):
        other = _convert_other(other)
        if other is NotImplemented:
            return other
        else:
            if context is None:
                context = getcontext()
            ans = self._check_nans(other, context)
            if ans:
                return ans
            if self._isinfinity():
                return context._raise_error(InvalidOperation, 'INF % x')
            if not other:
                if self:
                    return context._raise_error(InvalidOperation, 'x % 0')
                else:
                    return context._raise_error(DivisionUndefined, '0 % 0')
            remainder = self._divide(other, context)[1]
            remainder = remainder._fix(context)
            return remainder

    def __rmod__(self, other, context=None):
        other = _convert_other(other)
        return other if other is NotImplemented else other.__mod__(self, context=context)

    def remainder_near(self, other, context=None):
        if context is None:
            context = getcontext()
        other = _convert_other(other, raiseit=True)
        ans = self._check_nans(other, context)
        if ans:
            return ans
        elif self._isinfinity():
            return context._raise_error(InvalidOperation, 'remainder_near(infinity, x)')
        else:
            if not other:
                if self:
                    return context._raise_error(InvalidOperation, 'remainder_near(x, 0)')
                else:
                    return context._raise_error(DivisionUndefined, 'remainder_near(0, 0)')
            if other._isinfinity():
                ans = Decimal(self)
                return ans._fix(context)
            ideal_exponent = min(self._exp, other._exp)
            if not self:
                ans = _dec_from_triple(self._sign, '0', ideal_exponent)
                return ans._fix(context)
            expdiff = self.adjusted() - other.adjusted()
            if expdiff >= context.prec + 1:
                return context._raise_error(DivisionImpossible)
            elif expdiff <= -2:
                ans = self._rescale(ideal_exponent, context.rounding)
                return ans._fix(context)
            op1 = _WorkRep(self)
            op2 = _WorkRep(other)
            if op1.exp >= op2.exp:
                op1.int *= 10 ** (op1.exp - op2.exp)
            else:
                op2.int *= 10 ** (op2.exp - op1.exp)
            q, r = divmod(op1.int, op2.int)
            if 2 * r + (q & 1) > op2.int:
                r -= op2.int
                q += 1
            if q >= 10 ** context.prec:
                return context._raise_error(DivisionImpossible)
            sign = self._sign
            if r < 0:
                sign = 1 - sign
                r = -r
            ans = _dec_from_triple(sign, str(r), ideal_exponent)
            return ans._fix(context)

    def __floordiv__(self, other, context=None):
        other = _convert_other(other)
        if other is NotImplemented:
            return other
        else:
            if context is None:
                context = getcontext()
            ans = self._check_nans(other, context)
            if ans:
                return ans
            if self._isinfinity():
                if other._isinfinity():
                    return context._raise_error(InvalidOperation, 'INF // INF')
                else:
                    return _SignedInfinity[self._sign ^ other._sign]
            if not other:
                if self:
                    return context._raise_error(DivisionByZero, 'x // 0', self._sign ^ other._sign)
                else:
                    return context._raise_error(DivisionUndefined, '0 // 0')
            return self._divide(other, context)[0]

    def __rfloordiv__(self, other, context=None):
        other = _convert_other(other)
        return other if other is NotImplemented else other.__floordiv__(self, context=context)

    def __float__(self):
        if self._isnan():
            if self.is_snan():
                raise ValueError('Cannot convert signaling NaN to float')
            s = '-nan' if self._sign else 'nan'
        else:
            s = str(self)
        return float(s)

    def __int__(self):
        if self._is_special:
            if self._isnan():
                raise ValueError('Cannot convert NaN to integer')
            elif self._isinfinity():
                raise OverflowError('Cannot convert infinity to integer')
        s = (-1) ** self._sign
        if self._exp >= 0:
            return s * int(self._int) * 10 ** self._exp
        else:
            return s * int(self._int[:self._exp] or '0')

    __trunc__ = __int__

    def real(self):
        return self

    real = property(real)

    def imag(self):
        return Decimal(0)

    imag = property(imag)

    def conjugate(self):
        return self

    def __complex__(self):
        return complex(float(self))

    def __long__(self):
        return long(self.__int__())

    def _fix_nan(self, context):
        payload = self._int
        max_payload_len = context.prec - context._clamp
        if len(payload) > max_payload_len:
            payload = payload[len(payload) - max_payload_len:].lstrip('0')
            return _dec_from_triple(self._sign, payload, self._exp, True)
        return Decimal(self)

    def _fix(self, context):
        if self._is_special:
            if self._isnan():
                return self._fix_nan(context)
            else:
                return Decimal(self)
        Etiny = context.Etiny()
        Etop = context.Etop()
        if not self:
            exp_max = [context.Emax, Etop][context._clamp]
            new_exp = min(max(self._exp, Etiny), exp_max)
            if new_exp != self._exp:
                context._raise_error(Clamped)
                return _dec_from_triple(self._sign, '0', new_exp)
            else:
                return Decimal(self)
        exp_min = len(self._int) + self._exp - context.prec
        if exp_min > Etop:
            ans = context._raise_error(Overflow, 'above Emax', self._sign)
            context._raise_error(Inexact)
            context._raise_error(Rounded)
            return ans
        self_is_subnormal = exp_min < Etiny
        if self_is_subnormal:
            exp_min = Etiny
        if self._exp < exp_min:
            digits = len(self._int) + self._exp - exp_min
            if digits < 0:
                self = _dec_from_triple(self._sign, '1', exp_min - 1)
                digits = 0
            rounding_method = self._pick_rounding_function[context.rounding]
            changed = rounding_method(self, digits)
            coeff = self._int[:digits] or '0'
            if changed > 0:
                coeff = str(int(coeff) + 1)
                if len(coeff) > context.prec:
                    coeff = coeff[:-1]
                    exp_min += 1
            if exp_min > Etop:
                ans = context._raise_error(Overflow, 'above Emax', self._sign)
            else:
                ans = _dec_from_triple(self._sign, coeff, exp_min)
            if changed and self_is_subnormal:
                context._raise_error(Underflow)
            if self_is_subnormal:
                context._raise_error(Subnormal)
            if changed:
                context._raise_error(Inexact)
            context._raise_error(Rounded)
            if not ans:
                context._raise_error(Clamped)
            return ans
        if self_is_subnormal:
            context._raise_error(Subnormal)
        if context._clamp == 1 and self._exp > Etop:
            context._raise_error(Clamped)
            self_padded = self._int + '0' * (self._exp - Etop)
            return _dec_from_triple(self._sign, self_padded, Etop)
        return Decimal(self)

    def _round_down(self, prec):
        if _all_zeros(self._int, prec):
            return 0
        else:
            return -1

    def _round_up(self, prec):
        return -self._round_down(prec)

    def _round_half_up(self, prec):
        if self._int[prec] in '56789':
            return 1
        elif _all_zeros(self._int, prec):
            return 0
        else:
            return -1

    def _round_half_down(self, prec):
        if _exact_half(self._int, prec):
            return -1
        else:
            return self._round_half_up(prec)

    def _round_half_even(self, prec):
        if _exact_half(self._int, prec) and (prec == 0 or self._int[prec - 1] in '02468'):
            return -1
        else:
            return self._round_half_up(prec)

    def _round_ceiling(self, prec):
        if self._sign:
            return self._round_down(prec)
        else:
            return -self._round_down(prec)

    def _round_floor(self, prec):
        if not self._sign:
            return self._round_down(prec)
        else:
            return -self._round_down(prec)

    def _round_05up(self, prec):
        if prec and self._int[prec - 1] not in '05':
            return self._round_down(prec)
        else:
            return -self._round_down(prec)

    _pick_rounding_function = dict(ROUND_DOWN=_round_down, ROUND_UP=_round_up, ROUND_HALF_UP=_round_half_up, ROUND_HALF_DOWN=_round_half_down, ROUND_HALF_EVEN=_round_half_even, ROUND_CEILING=_round_ceiling, ROUND_FLOOR=_round_floor, ROUND_05UP=_round_05up)

    def fma(self, other, third, context=None):
        other = _convert_other(other, raiseit=True)
        if self._is_special or other._is_special:
            if context is None:
                context = getcontext()
            if self._exp == 'N':
                return context._raise_error(InvalidOperation, 'sNaN', self)
            if other._exp == 'N':
                return context._raise_error(InvalidOperation, 'sNaN', other)
            if self._exp == 'n':
                product = self
            elif other._exp == 'n':
                product = other
            elif self._exp == 'F':
                if not other:
                    return context._raise_error(InvalidOperation, 'INF * 0 in fma')
                product = _SignedInfinity[self._sign ^ other._sign]
            elif other._exp == 'F':
                if not self:
                    return context._raise_error(InvalidOperation, '0 * INF in fma')
                product = _SignedInfinity[self._sign ^ other._sign]
        else:
            product = _dec_from_triple(self._sign ^ other._sign, str(int(self._int) * int(other._int)), self._exp + other._exp)
        third = _convert_other(third, raiseit=True)
        return product.__add__(third, context)

    def _power_modulo(self, other, modulo, context=None):
        other = _convert_other(other, raiseit=True)
        modulo = _convert_other(modulo, raiseit=True)
        if context is None:
            context = getcontext()
        self_is_nan = self._isnan()
        other_is_nan = other._isnan()
        modulo_is_nan = modulo._isnan()
        if self_is_nan or other_is_nan or modulo_is_nan:
            if self_is_nan == 2:
                return context._raise_error(InvalidOperation, 'sNaN', self)
            if other_is_nan == 2:
                return context._raise_error(InvalidOperation, 'sNaN', other)
            if modulo_is_nan == 2:
                return context._raise_error(InvalidOperation, 'sNaN', modulo)
            if self_is_nan:
                return self._fix_nan(context)
            if other_is_nan:
                return other._fix_nan(context)
            return modulo._fix_nan(context)
        elif not (self._isinteger() and other._isinteger() and modulo._isinteger()):
            return context._raise_error(InvalidOperation, 'pow() 3rd argument not allowed unless all arguments are integers')
        elif other < 0:
            return context._raise_error(InvalidOperation, 'pow() 2nd argument cannot be negative when 3rd argument specified')
        elif not modulo:
            return context._raise_error(InvalidOperation, 'pow() 3rd argument cannot be 0')
        elif modulo.adjusted() >= context.prec:
            return context._raise_error(InvalidOperation, 'insufficient precision: pow() 3rd argument must not have more than precision digits')
        elif not other and not self:
            return context._raise_error(InvalidOperation, 'at least one of pow() 1st argument and 2nd argument must be nonzero ;0**0 is not defined')
        else:
            if other._iseven():
                sign = 0
            else:
                sign = self._sign
            modulo = abs(int(modulo))
            base = _WorkRep(self.to_integral_value())
            exponent = _WorkRep(other.to_integral_value())
            base = base.int % modulo * pow(10, base.exp, modulo) % modulo
            for i in xrange(exponent.exp):
                base = pow(base, 10, modulo)

            base = pow(base, exponent.int, modulo)
            return _dec_from_triple(sign, str(base), 0)

    def _power_exact(self, other, p):
        x = _WorkRep(self)
        xc, xe = x.int, x.exp
        while xc % 10 == 0:
            xc //= 10
            xe += 1

        y = _WorkRep(other)
        yc, ye = y.int, y.exp
        while yc % 10 == 0:
            yc //= 10
            ye += 1

        if xc == 1:
            xe *= yc
            while xe % 10 == 0:
                xe //= 10
                ye += 1

            if ye < 0:
                return
            exponent = xe * 10 ** ye
            if y.sign == 1:
                exponent = -exponent
            if other._isinteger() and other._sign == 0:
                ideal_exponent = self._exp * int(other)
                zeros = min(exponent - ideal_exponent, p - 1)
            else:
                zeros = 0
            return _dec_from_triple(0, '1' + '0' * zeros, exponent - zeros)
        elif y.sign == 1:
            last_digit = xc % 10
            if last_digit in (2, 4, 6, 8):
                if xc & -xc != xc:
                    return
                e = _nbits(xc) - 1
                emax = p * 93 // 65
                if ye >= len(str(emax)):
                    return
                e = _decimal_lshift_exact(e * yc, ye)
                xe = _decimal_lshift_exact(xe * yc, ye)
                if e is None or xe is None:
                    return
                if e > emax:
                    return
                xc = 5 ** e
            elif last_digit == 5:
                e = _nbits(xc) * 28 // 65
                xc, remainder = divmod(5 ** e, xc)
                if remainder:
                    return
                while xc % 5 == 0:
                    xc //= 5
                    e -= 1

                emax = p * 10 // 3
                if ye >= len(str(emax)):
                    return
                e = _decimal_lshift_exact(e * yc, ye)
                xe = _decimal_lshift_exact(xe * yc, ye)
                if e is None or xe is None:
                    return
                if e > emax:
                    return
                xc = 2 ** e
            else:
                return
            if xc >= 10 ** p:
                return
            xe = -e - xe
            return _dec_from_triple(0, str(xc), xe)
        else:
            if ye >= 0:
                m, n = yc * 10 ** ye, 1
            else:
                if xe != 0 and len(str(abs(yc * xe))) <= -ye:
                    return
                xc_bits = _nbits(xc)
                if xc != 1 and len(str(abs(yc) * xc_bits)) <= -ye:
                    return
                m, n = yc, 10 ** (-ye)
                while m % 2 == n % 2 == 0:
                    m //= 2
                    n //= 2

            while m % 5 == n % 5 == 0:
                m //= 5
                n //= 5

            if n > 1:
                if xc != 1 and xc_bits <= n:
                    return
                xe, rem = divmod(xe, n)
                if rem != 0:
                    return
                a = 1L << -(-_nbits(xc) // n)
                while True:
                    q, r = divmod(xc, a ** (n - 1))
                    if a <= q:
                        break
                    a = (a * (n - 1) + q) // n

                if not (a == q and r == 0):
                    return
                xc = a
            if xc > 1 and m > p * 100 // _log10_lb(xc):
                return
            xc = xc ** m
            xe *= m
            if xc > 10 ** p:
                return
            str_xc = str(xc)
            if other._isinteger() and other._sign == 0:
                ideal_exponent = self._exp * int(other)
                zeros = min(xe - ideal_exponent, p - len(str_xc))
            else:
                zeros = 0
            return _dec_from_triple(0, str_xc + '0' * zeros, xe - zeros)

    def __pow__(self, other, modulo=None, context=None):
        if modulo is not None:
            return self._power_modulo(other, modulo, context)
        else:
            other = _convert_other(other)
            if other is NotImplemented:
                return other
            if context is None:
                context = getcontext()
            ans = self._check_nans(other, context)
            if ans:
                return ans
            if not other:
                if not self:
                    return context._raise_error(InvalidOperation, '0 ** 0')
                else:
                    return _One
            result_sign = 0
            if self._sign == 1:
                if other._isinteger():
                    if not other._iseven():
                        result_sign = 1
                elif self:
                    return context._raise_error(InvalidOperation, 'x ** y with x negative and y not an integer')
                self = self.copy_negate()
            if not self:
                if other._sign == 0:
                    return _dec_from_triple(result_sign, '0', 0)
                else:
                    return _SignedInfinity[result_sign]
            if self._isinfinity():
                if other._sign == 0:
                    return _SignedInfinity[result_sign]
                else:
                    return _dec_from_triple(result_sign, '0', 0)
            if self == _One:
                if other._isinteger():
                    if other._sign == 1:
                        multiplier = 0
                    elif other > context.prec:
                        multiplier = context.prec
                    else:
                        multiplier = int(other)
                    exp = self._exp * multiplier
                    if exp < 1 - context.prec:
                        exp = 1 - context.prec
                        context._raise_error(Rounded)
                else:
                    context._raise_error(Inexact)
                    context._raise_error(Rounded)
                    exp = 1 - context.prec
                return _dec_from_triple(result_sign, '1' + '0' * -exp, exp)
            self_adj = self.adjusted()
            if other._isinfinity():
                if (other._sign == 0) == (self_adj < 0):
                    return _dec_from_triple(result_sign, '0', 0)
                else:
                    return _SignedInfinity[result_sign]
            ans = None
            exact = False
            bound = self._log10_exp_bound() + other.adjusted()
            if (self_adj >= 0) == (other._sign == 0):
                if bound >= len(str(context.Emax)):
                    ans = _dec_from_triple(result_sign, '1', context.Emax + 1)
            else:
                Etiny = context.Etiny()
                if bound >= len(str(-Etiny)):
                    ans = _dec_from_triple(result_sign, '1', Etiny - 1)
            if ans is None:
                ans = self._power_exact(other, context.prec + 1)
                if ans is not None:
                    if result_sign == 1:
                        ans = _dec_from_triple(1, ans._int, ans._exp)
                    exact = True
            if ans is None:
                p = context.prec
                x = _WorkRep(self)
                xc, xe = x.int, x.exp
                y = _WorkRep(other)
                yc, ye = y.int, y.exp
                if y.sign == 1:
                    yc = -yc
                extra = 3
                while True:
                    coeff, exp = _dpower(xc, xe, yc, ye, p + extra)
                    if coeff % (5 * 10 ** (len(str(coeff)) - p - 1)):
                        break
                    extra += 3

                ans = _dec_from_triple(result_sign, str(coeff), exp)
            if exact and not other._isinteger():
                if len(ans._int) <= context.prec:
                    expdiff = context.prec + 1 - len(ans._int)
                    ans = _dec_from_triple(ans._sign, ans._int + '0' * expdiff, ans._exp - expdiff)
                newcontext = context.copy()
                newcontext.clear_flags()
                for exception in _signals:
                    newcontext.traps[exception] = 0

                ans = ans._fix(newcontext)
                newcontext._raise_error(Inexact)
                if newcontext.flags[Subnormal]:
                    newcontext._raise_error(Underflow)
                if newcontext.flags[Overflow]:
                    context._raise_error(Overflow, 'above Emax', ans._sign)
                for exception in (Underflow,
                 Subnormal,
                 Inexact,
                 Rounded,
                 Clamped):
                    if newcontext.flags[exception]:
                        context._raise_error(exception)

            else:
                ans = ans._fix(context)
            return ans

    def __rpow__(self, other, context=None):
        other = _convert_other(other)
        return other if other is NotImplemented else other.__pow__(self, context=context)

    def normalize(self, context=None):
        if context is None:
            context = getcontext()
        if self._is_special:
            ans = self._check_nans(context=context)
            if ans:
                return ans
        dup = self._fix(context)
        if dup._isinfinity():
            return dup
        elif not dup:
            return _dec_from_triple(dup._sign, '0', 0)
        else:
            exp_max = [context.Emax, context.Etop()][context._clamp]
            end = len(dup._int)
            exp = dup._exp
            while dup._int[end - 1] == '0' and exp < exp_max:
                exp += 1
                end -= 1

            return _dec_from_triple(dup._sign, dup._int[:end], exp)

    def quantize(self, exp, rounding=None, context=None, watchexp=True):
        exp = _convert_other(exp, raiseit=True)
        if context is None:
            context = getcontext()
        if rounding is None:
            rounding = context.rounding
        if self._is_special or exp._is_special:
            ans = self._check_nans(exp, context)
            if ans:
                return ans
            if exp._isinfinity() or self._isinfinity():
                if exp._isinfinity() and self._isinfinity():
                    return Decimal(self)
                return context._raise_error(InvalidOperation, 'quantize with one INF')
        if not watchexp:
            ans = self._rescale(exp._exp, rounding)
            if ans._exp > self._exp:
                context._raise_error(Rounded)
                if ans != self:
                    context._raise_error(Inexact)
            return ans
        elif not context.Etiny() <= exp._exp <= context.Emax:
            return context._raise_error(InvalidOperation, 'target exponent out of bounds in quantize')
        elif not self:
            ans = _dec_from_triple(self._sign, '0', exp._exp)
            return ans._fix(context)
        else:
            self_adjusted = self.adjusted()
            if self_adjusted > context.Emax:
                return context._raise_error(InvalidOperation, 'exponent of quantize result too large for current context')
            elif self_adjusted - exp._exp + 1 > context.prec:
                return context._raise_error(InvalidOperation, 'quantize result has too many digits for current context')
            ans = self._rescale(exp._exp, rounding)
            if ans.adjusted() > context.Emax:
                return context._raise_error(InvalidOperation, 'exponent of quantize result too large for current context')
            elif len(ans._int) > context.prec:
                return context._raise_error(InvalidOperation, 'quantize result has too many digits for current context')
            if ans and ans.adjusted() < context.Emin:
                context._raise_error(Subnormal)
            if ans._exp > self._exp:
                if ans != self:
                    context._raise_error(Inexact)
                context._raise_error(Rounded)
            ans = ans._fix(context)
            return ans

    def same_quantum(self, other):
        other = _convert_other(other, raiseit=True)
        return self.is_nan() and other.is_nan() or self.is_infinite() and other.is_infinite() if self._is_special or other._is_special else self._exp == other._exp

    def _rescale(self, exp, rounding):
        if self._is_special:
            return Decimal(self)
        if not self:
            return _dec_from_triple(self._sign, '0', exp)
        if self._exp >= exp:
            return _dec_from_triple(self._sign, self._int + '0' * (self._exp - exp), exp)
        digits = len(self._int) + self._exp - exp
        if digits < 0:
            self = _dec_from_triple(self._sign, '1', exp - 1)
            digits = 0
        this_function = self._pick_rounding_function[rounding]
        changed = this_function(self, digits)
        coeff = self._int[:digits] or '0'
        if changed == 1:
            coeff = str(int(coeff) + 1)
        return _dec_from_triple(self._sign, coeff, exp)

    def _round(self, places, rounding):
        if places <= 0:
            raise ValueError('argument should be at least 1 in _round')
        if self._is_special or not self:
            return Decimal(self)
        ans = self._rescale(self.adjusted() + 1 - places, rounding)
        if ans.adjusted() != self.adjusted():
            ans = ans._rescale(ans.adjusted() + 1 - places, rounding)
        return ans

    def to_integral_exact(self, rounding=None, context=None):
        if self._is_special:
            ans = self._check_nans(context=context)
            if ans:
                return ans
            return Decimal(self)
        elif self._exp >= 0:
            return Decimal(self)
        elif not self:
            return _dec_from_triple(self._sign, '0', 0)
        else:
            if context is None:
                context = getcontext()
            if rounding is None:
                rounding = context.rounding
            ans = self._rescale(0, rounding)
            if ans != self:
                context._raise_error(Inexact)
            context._raise_error(Rounded)
            return ans

    def to_integral_value(self, rounding=None, context=None):
        if context is None:
            context = getcontext()
        if rounding is None:
            rounding = context.rounding
        if self._is_special:
            ans = self._check_nans(context=context)
            if ans:
                return ans
            return Decimal(self)
        elif self._exp >= 0:
            return Decimal(self)
        else:
            return self._rescale(0, rounding)
            return

    to_integral = to_integral_value

    def sqrt(self, context=None):
        if context is None:
            context = getcontext()
        if self._is_special:
            ans = self._check_nans(context=context)
            if ans:
                return ans
            if self._isinfinity() and self._sign == 0:
                return Decimal(self)
        if not self:
            ans = _dec_from_triple(self._sign, '0', self._exp // 2)
            return ans._fix(context)
        elif self._sign == 1:
            return context._raise_error(InvalidOperation, 'sqrt(-x), x > 0')
        else:
            prec = context.prec + 1
            op = _WorkRep(self)
            e = op.exp >> 1
            if op.exp & 1:
                c = op.int * 10
                l = (len(self._int) >> 1) + 1
            else:
                c = op.int
                l = len(self._int) + 1 >> 1
            shift = prec - l
            if shift >= 0:
                c *= 100 ** shift
                exact = True
            else:
                c, remainder = divmod(c, 100 ** (-shift))
                exact = not remainder
            e -= shift
            n = 10 ** prec
            while True:
                q = c // n
                if n <= q:
                    break
                n = n + q >> 1

            exact = exact and n * n == c
            if exact:
                if shift >= 0:
                    n //= 10 ** shift
                else:
                    n *= 10 ** (-shift)
                e += shift
            elif n % 5 == 0:
                n += 1
            ans = _dec_from_triple(0, str(n), e)
            context = context._shallow_copy()
            rounding = context._set_rounding(ROUND_HALF_EVEN)
            ans = ans._fix(context)
            context.rounding = rounding
            return ans

    def max(self, other, context=None):
        other = _convert_other(other, raiseit=True)
        if context is None:
            context = getcontext()
        if self._is_special or other._is_special:
            sn = self._isnan()
            on = other._isnan()
            if sn or on:
                if on == 1 and sn == 0:
                    return self._fix(context)
                if sn == 1 and on == 0:
                    return other._fix(context)
                return self._check_nans(other, context)
        c = self._cmp(other)
        if c == 0:
            c = self.compare_total(other)
        if c == -1:
            ans = other
        else:
            ans = self
        return ans._fix(context)

    def min(self, other, context=None):
        other = _convert_other(other, raiseit=True)
        if context is None:
            context = getcontext()
        if self._is_special or other._is_special:
            sn = self._isnan()
            on = other._isnan()
            if sn or on:
                if on == 1 and sn == 0:
                    return self._fix(context)
                if sn == 1 and on == 0:
                    return other._fix(context)
                return self._check_nans(other, context)
        c = self._cmp(other)
        if c == 0:
            c = self.compare_total(other)
        if c == -1:
            ans = self
        else:
            ans = other
        return ans._fix(context)

    def _isinteger(self):
        if self._is_special:
            return False
        if self._exp >= 0:
            return True
        rest = self._int[self._exp:]
        return rest == '0' * len(rest)

    def _iseven(self):
        return True if not self or self._exp > 0 else self._int[-1 + self._exp] in '02468'

    def adjusted(self):
        try:
            return self._exp + len(self._int) - 1
        except TypeError:
            return 0

    def canonical(self, context=None):
        return self

    def compare_signal(self, other, context=None):
        other = _convert_other(other, raiseit=True)
        ans = self._compare_check_nans(other, context)
        return ans if ans else self.compare(other, context=context)

    def compare_total(self, other):
        other = _convert_other(other, raiseit=True)
        if self._sign and not other._sign:
            return _NegativeOne
        if not self._sign and other._sign:
            return _One
        sign = self._sign
        self_nan = self._isnan()
        other_nan = other._isnan()
        if self_nan or other_nan:
            if self_nan == other_nan:
                self_key = (len(self._int), self._int)
                other_key = (len(other._int), other._int)
                if self_key < other_key:
                    if sign:
                        return _One
                    else:
                        return _NegativeOne
                if self_key > other_key:
                    if sign:
                        return _NegativeOne
                    else:
                        return _One
                return _Zero
            if sign:
                if self_nan == 1:
                    return _NegativeOne
                if other_nan == 1:
                    return _One
                if self_nan == 2:
                    return _NegativeOne
                if other_nan == 2:
                    return _One
            else:
                if self_nan == 1:
                    return _One
                if other_nan == 1:
                    return _NegativeOne
                if self_nan == 2:
                    return _One
                if other_nan == 2:
                    return _NegativeOne
        if self < other:
            return _NegativeOne
        if self > other:
            return _One
        if self._exp < other._exp:
            if sign:
                return _One
            else:
                return _NegativeOne
        if self._exp > other._exp:
            if sign:
                return _NegativeOne
            else:
                return _One
        return _Zero

    def compare_total_mag(self, other):
        other = _convert_other(other, raiseit=True)
        s = self.copy_abs()
        o = other.copy_abs()
        return s.compare_total(o)

    def copy_abs(self):
        return _dec_from_triple(0, self._int, self._exp, self._is_special)

    def copy_negate(self):
        if self._sign:
            return _dec_from_triple(0, self._int, self._exp, self._is_special)
        else:
            return _dec_from_triple(1, self._int, self._exp, self._is_special)

    def copy_sign(self, other):
        other = _convert_other(other, raiseit=True)
        return _dec_from_triple(other._sign, self._int, self._exp, self._is_special)

    def exp(self, context=None):
        if context is None:
            context = getcontext()
        ans = self._check_nans(context=context)
        if ans:
            return ans
        elif self._isinfinity() == -1:
            return _Zero
        elif not self:
            return _One
        elif self._isinfinity() == 1:
            return Decimal(self)
        else:
            p = context.prec
            adj = self.adjusted()
            if self._sign == 0 and adj > len(str((context.Emax + 1) * 3)):
                ans = _dec_from_triple(0, '1', context.Emax + 1)
            elif self._sign == 1 and adj > len(str((-context.Etiny() + 1) * 3)):
                ans = _dec_from_triple(0, '1', context.Etiny() - 1)
            elif self._sign == 0 and adj < -p:
                ans = _dec_from_triple(0, '1' + '0' * (p - 1) + '1', -p)
            elif self._sign == 1 and adj < -p - 1:
                ans = _dec_from_triple(0, '9' * (p + 1), -p - 1)
            else:
                op = _WorkRep(self)
                c, e = op.int, op.exp
                if op.sign == 1:
                    c = -c
                extra = 3
                while True:
                    coeff, exp = _dexp(c, e, p + extra)
                    if coeff % (5 * 10 ** (len(str(coeff)) - p - 1)):
                        break
                    extra += 3

                ans = _dec_from_triple(0, str(coeff), exp)
            context = context._shallow_copy()
            rounding = context._set_rounding(ROUND_HALF_EVEN)
            ans = ans._fix(context)
            context.rounding = rounding
            return ans

    def is_canonical(self):
        return True

    def is_finite(self):
        return not self._is_special

    def is_infinite(self):
        return self._exp == 'F'

    def is_nan(self):
        return self._exp in ('n', 'N')

    def is_normal(self, context=None):
        if self._is_special or not self:
            return False
        else:
            if context is None:
                context = getcontext()
            return context.Emin <= self.adjusted()

    def is_qnan(self):
        return self._exp == 'n'

    def is_signed(self):
        return self._sign == 1

    def is_snan(self):
        return self._exp == 'N'

    def is_subnormal(self, context=None):
        if self._is_special or not self:
            return False
        else:
            if context is None:
                context = getcontext()
            return self.adjusted() < context.Emin

    def is_zero(self):
        return not self._is_special and self._int == '0'

    def _ln_exp_bound(self):
        adj = self._exp + len(self._int) - 1
        if adj >= 1:
            return len(str(adj * 23 // 10)) - 1
        if adj <= -2:
            return len(str((-1 - adj) * 23 // 10)) - 1
        op = _WorkRep(self)
        c, e = op.int, op.exp
        if adj == 0:
            num = str(c - 10 ** (-e))
            den = str(c)
            return len(num) - len(den) - (num < den)
        return e + len(str(10 ** (-e) - c)) - 1

    def ln(self, context=None):
        if context is None:
            context = getcontext()
        ans = self._check_nans(context=context)
        if ans:
            return ans
        elif not self:
            return _NegativeInfinity
        elif self._isinfinity() == 1:
            return _Infinity
        elif self == _One:
            return _Zero
        elif self._sign == 1:
            return context._raise_error(InvalidOperation, 'ln of a negative value')
        else:
            op = _WorkRep(self)
            c, e = op.int, op.exp
            p = context.prec
            places = p - self._ln_exp_bound() + 2
            while True:
                coeff = _dlog(c, e, places)
                if coeff % (5 * 10 ** (len(str(abs(coeff))) - p - 1)):
                    break
                places += 3

            ans = _dec_from_triple(int(coeff < 0), str(abs(coeff)), -places)
            context = context._shallow_copy()
            rounding = context._set_rounding(ROUND_HALF_EVEN)
            ans = ans._fix(context)
            context.rounding = rounding
            return ans

    def _log10_exp_bound(self):
        adj = self._exp + len(self._int) - 1
        if adj >= 1:
            return len(str(adj)) - 1
        if adj <= -2:
            return len(str(-1 - adj)) - 1
        op = _WorkRep(self)
        c, e = op.int, op.exp
        if adj == 0:
            num = str(c - 10 ** (-e))
            den = str(231 * c)
            return len(num) - len(den) - (num < den) + 2
        num = str(10 ** (-e) - c)
        return len(num) + e - (num < '231') - 1

    def log10(self, context=None):
        if context is None:
            context = getcontext()
        ans = self._check_nans(context=context)
        if ans:
            return ans
        elif not self:
            return _NegativeInfinity
        elif self._isinfinity() == 1:
            return _Infinity
        elif self._sign == 1:
            return context._raise_error(InvalidOperation, 'log10 of a negative value')
        else:
            if self._int[0] == '1' and self._int[1:] == '0' * (len(self._int) - 1):
                ans = Decimal(self._exp + len(self._int) - 1)
            else:
                op = _WorkRep(self)
                c, e = op.int, op.exp
                p = context.prec
                places = p - self._log10_exp_bound() + 2
                while True:
                    coeff = _dlog10(c, e, places)
                    if coeff % (5 * 10 ** (len(str(abs(coeff))) - p - 1)):
                        break
                    places += 3

                ans = _dec_from_triple(int(coeff < 0), str(abs(coeff)), -places)
            context = context._shallow_copy()
            rounding = context._set_rounding(ROUND_HALF_EVEN)
            ans = ans._fix(context)
            context.rounding = rounding
            return ans

    def logb(self, context=None):
        ans = self._check_nans(context=context)
        if ans:
            return ans
        else:
            if context is None:
                context = getcontext()
            if self._isinfinity():
                return _Infinity
            if not self:
                return context._raise_error(DivisionByZero, 'logb(0)', 1)
            ans = Decimal(self.adjusted())
            return ans._fix(context)

    def _islogical(self):
        if self._sign != 0 or self._exp != 0:
            return False
        for dig in self._int:
            if dig not in '01':
                return False

        return True

    def _fill_logical(self, context, opa, opb):
        dif = context.prec - len(opa)
        if dif > 0:
            opa = '0' * dif + opa
        elif dif < 0:
            opa = opa[-context.prec:]
        dif = context.prec - len(opb)
        if dif > 0:
            opb = '0' * dif + opb
        elif dif < 0:
            opb = opb[-context.prec:]
        return (opa, opb)

    def logical_and(self, other, context=None):
        if context is None:
            context = getcontext()
        other = _convert_other(other, raiseit=True)
        if not self._islogical() or not other._islogical():
            return context._raise_error(InvalidOperation)
        else:
            opa, opb = self._fill_logical(context, self._int, other._int)
            result = ''.join([ str(int(a) & int(b)) for a, b in zip(opa, opb) ])
            return _dec_from_triple(0, result.lstrip('0') or '0', 0)

    def logical_invert(self, context=None):
        if context is None:
            context = getcontext()
        return self.logical_xor(_dec_from_triple(0, '1' * context.prec, 0), context)

    def logical_or(self, other, context=None):
        if context is None:
            context = getcontext()
        other = _convert_other(other, raiseit=True)
        if not self._islogical() or not other._islogical():
            return context._raise_error(InvalidOperation)
        else:
            opa, opb = self._fill_logical(context, self._int, other._int)
            result = ''.join([ str(int(a) | int(b)) for a, b in zip(opa, opb) ])
            return _dec_from_triple(0, result.lstrip('0') or '0', 0)

    def logical_xor(self, other, context=None):
        if context is None:
            context = getcontext()
        other = _convert_other(other, raiseit=True)
        if not self._islogical() or not other._islogical():
            return context._raise_error(InvalidOperation)
        else:
            opa, opb = self._fill_logical(context, self._int, other._int)
            result = ''.join([ str(int(a) ^ int(b)) for a, b in zip(opa, opb) ])
            return _dec_from_triple(0, result.lstrip('0') or '0', 0)

    def max_mag(self, other, context=None):
        other = _convert_other(other, raiseit=True)
        if context is None:
            context = getcontext()
        if self._is_special or other._is_special:
            sn = self._isnan()
            on = other._isnan()
            if sn or on:
                if on == 1 and sn == 0:
                    return self._fix(context)
                if sn == 1 and on == 0:
                    return other._fix(context)
                return self._check_nans(other, context)
        c = self.copy_abs()._cmp(other.copy_abs())
        if c == 0:
            c = self.compare_total(other)
        if c == -1:
            ans = other
        else:
            ans = self
        return ans._fix(context)

    def min_mag(self, other, context=None):
        other = _convert_other(other, raiseit=True)
        if context is None:
            context = getcontext()
        if self._is_special or other._is_special:
            sn = self._isnan()
            on = other._isnan()
            if sn or on:
                if on == 1 and sn == 0:
                    return self._fix(context)
                if sn == 1 and on == 0:
                    return other._fix(context)
                return self._check_nans(other, context)
        c = self.copy_abs()._cmp(other.copy_abs())
        if c == 0:
            c = self.compare_total(other)
        if c == -1:
            ans = self
        else:
            ans = other
        return ans._fix(context)

    def next_minus(self, context=None):
        if context is None:
            context = getcontext()
        ans = self._check_nans(context=context)
        if ans:
            return ans
        elif self._isinfinity() == -1:
            return _NegativeInfinity
        elif self._isinfinity() == 1:
            return _dec_from_triple(0, '9' * context.prec, context.Etop())
        else:
            context = context.copy()
            context._set_rounding(ROUND_FLOOR)
            context._ignore_all_flags()
            new_self = self._fix(context)
            return new_self if new_self != self else self.__sub__(_dec_from_triple(0, '1', context.Etiny() - 1), context)

    def next_plus(self, context=None):
        if context is None:
            context = getcontext()
        ans = self._check_nans(context=context)
        if ans:
            return ans
        elif self._isinfinity() == 1:
            return _Infinity
        elif self._isinfinity() == -1:
            return _dec_from_triple(1, '9' * context.prec, context.Etop())
        else:
            context = context.copy()
            context._set_rounding(ROUND_CEILING)
            context._ignore_all_flags()
            new_self = self._fix(context)
            return new_self if new_self != self else self.__add__(_dec_from_triple(0, '1', context.Etiny() - 1), context)

    def next_toward(self, other, context=None):
        other = _convert_other(other, raiseit=True)
        if context is None:
            context = getcontext()
        ans = self._check_nans(other, context)
        if ans:
            return ans
        else:
            comparison = self._cmp(other)
            if comparison == 0:
                return self.copy_sign(other)
            if comparison == -1:
                ans = self.next_plus(context)
            else:
                ans = self.next_minus(context)
            if ans._isinfinity():
                context._raise_error(Overflow, 'Infinite result from next_toward', ans._sign)
                context._raise_error(Inexact)
                context._raise_error(Rounded)
            elif ans.adjusted() < context.Emin:
                context._raise_error(Underflow)
                context._raise_error(Subnormal)
                context._raise_error(Inexact)
                context._raise_error(Rounded)
                if not ans:
                    context._raise_error(Clamped)
            return ans

    def number_class(self, context=None):
        if self.is_snan():
            return 'sNaN'
        elif self.is_qnan():
            return 'NaN'
        else:
            inf = self._isinfinity()
            if inf == 1:
                return '+Infinity'
            elif inf == -1:
                return '-Infinity'
            if self.is_zero():
                if self._sign:
                    return '-Zero'
                else:
                    return '+Zero'
            if context is None:
                context = getcontext()
            if self.is_subnormal(context=context):
                if self._sign:
                    return '-Subnormal'
                else:
                    return '+Subnormal'
            if self._sign:
                return '-Normal'
            return '+Normal'
            return

    def radix(self):
        return Decimal(10)

    def rotate(self, other, context=None):
        if context is None:
            context = getcontext()
        other = _convert_other(other, raiseit=True)
        ans = self._check_nans(other, context)
        if ans:
            return ans
        elif other._exp != 0:
            return context._raise_error(InvalidOperation)
        elif not -context.prec <= int(other) <= context.prec:
            return context._raise_error(InvalidOperation)
        elif self._isinfinity():
            return Decimal(self)
        else:
            torot = int(other)
            rotdig = self._int
            topad = context.prec - len(rotdig)
            if topad > 0:
                rotdig = '0' * topad + rotdig
            elif topad < 0:
                rotdig = rotdig[-topad:]
            rotated = rotdig[torot:] + rotdig[:torot]
            return _dec_from_triple(self._sign, rotated.lstrip('0') or '0', self._exp)

    def scaleb(self, other, context=None):
        if context is None:
            context = getcontext()
        other = _convert_other(other, raiseit=True)
        ans = self._check_nans(other, context)
        if ans:
            return ans
        elif other._exp != 0:
            return context._raise_error(InvalidOperation)
        else:
            liminf = -2 * (context.Emax + context.prec)
            limsup = 2 * (context.Emax + context.prec)
            if not liminf <= int(other) <= limsup:
                return context._raise_error(InvalidOperation)
            elif self._isinfinity():
                return Decimal(self)
            d = _dec_from_triple(self._sign, self._int, self._exp + int(other))
            d = d._fix(context)
            return d

    def shift(self, other, context=None):
        if context is None:
            context = getcontext()
        other = _convert_other(other, raiseit=True)
        ans = self._check_nans(other, context)
        if ans:
            return ans
        elif other._exp != 0:
            return context._raise_error(InvalidOperation)
        elif not -context.prec <= int(other) <= context.prec:
            return context._raise_error(InvalidOperation)
        elif self._isinfinity():
            return Decimal(self)
        else:
            torot = int(other)
            rotdig = self._int
            topad = context.prec - len(rotdig)
            if topad > 0:
                rotdig = '0' * topad + rotdig
            elif topad < 0:
                rotdig = rotdig[-topad:]
            if torot < 0:
                shifted = rotdig[:torot]
            else:
                shifted = rotdig + '0' * torot
                shifted = shifted[-context.prec:]
            return _dec_from_triple(self._sign, shifted.lstrip('0') or '0', self._exp)

    def __reduce__(self):
        return (self.__class__, (str(self),))

    def __copy__(self):
        return self if type(self) is Decimal else self.__class__(str(self))

    def __deepcopy__(self, memo):
        return self if type(self) is Decimal else self.__class__(str(self))

    def __format__(self, specifier, context=None, _localeconv=None):
        if context is None:
            context = getcontext()
        spec = _parse_format_specifier(specifier, _localeconv=_localeconv)
        if self._is_special:
            sign = _format_sign(self._sign, spec)
            body = str(self.copy_abs())
            return _format_align(sign, body, spec)
        else:
            if spec['type'] is None:
                spec['type'] = ['g', 'G'][context.capitals]
            if spec['type'] == '%':
                self = _dec_from_triple(self._sign, self._int, self._exp + 2)
            rounding = context.rounding
            precision = spec['precision']
            if precision is not None:
                if spec['type'] in 'eE':
                    self = self._round(precision + 1, rounding)
                elif spec['type'] in 'fF%':
                    self = self._rescale(-precision, rounding)
                elif spec['type'] in 'gG' and len(self._int) > precision:
                    self = self._round(precision, rounding)
            if not self and self._exp > 0 and spec['type'] in 'fF%':
                self = self._rescale(0, rounding)
            leftdigits = self._exp + len(self._int)
            if spec['type'] in 'eE':
                if not self and precision is not None:
                    dotplace = 1 - precision
                else:
                    dotplace = 1
            elif spec['type'] in 'fF%':
                dotplace = leftdigits
            elif spec['type'] in 'gG':
                if self._exp <= 0 and leftdigits > -6:
                    dotplace = leftdigits
                else:
                    dotplace = 1
            if dotplace < 0:
                intpart = '0'
                fracpart = '0' * -dotplace + self._int
            elif dotplace > len(self._int):
                intpart = self._int + '0' * (dotplace - len(self._int))
                fracpart = ''
            else:
                intpart = self._int[:dotplace] or '0'
                fracpart = self._int[dotplace:]
            exp = leftdigits - dotplace
            return _format_number(self._sign, intpart, fracpart, exp, spec)


def _dec_from_triple(sign, coefficient, exponent, special=False):
    self = object.__new__(Decimal)
    self._sign = sign
    self._int = coefficient
    self._exp = exponent
    self._is_special = special
    return self


_numbers.Number.register(Decimal)

class _ContextManager(object):

    def __init__(self, new_context):
        self.new_context = new_context.copy()

    def __enter__(self):
        self.saved_context = getcontext()
        setcontext(self.new_context)
        return self.new_context

    def __exit__(self, t, v, tb):
        setcontext(self.saved_context)


class Context(object):

    def __init__(self, prec=None, rounding=None, traps=None, flags=None, Emin=None, Emax=None, capitals=None, _clamp=0, _ignored_flags=None):
        try:
            dc = DefaultContext
        except NameError:
            pass

        self.prec = prec if prec is not None else dc.prec
        self.rounding = rounding if rounding is not None else dc.rounding
        self.Emin = Emin if Emin is not None else dc.Emin
        self.Emax = Emax if Emax is not None else dc.Emax
        self.capitals = capitals if capitals is not None else dc.capitals
        self._clamp = _clamp if _clamp is not None else dc._clamp
        if _ignored_flags is None:
            self._ignored_flags = []
        else:
            self._ignored_flags = _ignored_flags
        if traps is None:
            self.traps = dc.traps.copy()
        elif not isinstance(traps, dict):
            self.traps = dict(((s, int(s in traps)) for s in _signals))
        else:
            self.traps = traps
        if flags is None:
            self.flags = dict.fromkeys(_signals, 0)
        elif not isinstance(flags, dict):
            self.flags = dict(((s, int(s in flags)) for s in _signals))
        else:
            self.flags = flags
        return

    def __repr__(self):
        s = []
        s.append('Context(prec=%(prec)d, rounding=%(rounding)s, Emin=%(Emin)d, Emax=%(Emax)d, capitals=%(capitals)d' % vars(self))
        names = [ f.__name__ for f, v in self.flags.items() if v ]
        s.append('flags=[' + ', '.join(names) + ']')
        names = [ t.__name__ for t, v in self.traps.items() if v ]
        s.append('traps=[' + ', '.join(names) + ']')
        return ', '.join(s) + ')'

    def clear_flags(self):
        for flag in self.flags:
            self.flags[flag] = 0

    def _shallow_copy(self):
        nc = Context(self.prec, self.rounding, self.traps, self.flags, self.Emin, self.Emax, self.capitals, self._clamp, self._ignored_flags)
        return nc

    def copy(self):
        nc = Context(self.prec, self.rounding, self.traps.copy(), self.flags.copy(), self.Emin, self.Emax, self.capitals, self._clamp, self._ignored_flags)
        return nc

    __copy__ = copy

    def _raise_error(self, condition, explanation=None, *args):
        error = _condition_map.get(condition, condition)
        if error in self._ignored_flags:
            return error().handle(self, *args)
        self.flags[error] = 1
        if not self.traps[error]:
            return condition().handle(self, *args)
        raise error(explanation)

    def _ignore_all_flags(self):
        return self._ignore_flags(*_signals)

    def _ignore_flags(self, *flags):
        self._ignored_flags = self._ignored_flags + list(flags)
        return list(flags)

    def _regard_flags(self, *flags):
        if flags and isinstance(flags[0], (tuple, list)):
            flags = flags[0]
        for flag in flags:
            self._ignored_flags.remove(flag)

    __hash__ = None

    def Etiny(self):
        return int(self.Emin - self.prec + 1)

    def Etop(self):
        return int(self.Emax - self.prec + 1)

    def _set_rounding(self, type):
        rounding = self.rounding
        self.rounding = type
        return rounding

    def create_decimal(self, num='0'):
        if isinstance(num, basestring) and num != num.strip():
            return self._raise_error(ConversionSyntax, 'no trailing or leading whitespace is permitted.')
        d = Decimal(num, context=self)
        return self._raise_error(ConversionSyntax, 'diagnostic info too long in NaN') if d._isnan() and len(d._int) > self.prec - self._clamp else d._fix(self)

    def create_decimal_from_float(self, f):
        d = Decimal.from_float(f)
        return d._fix(self)

    def abs(self, a):
        a = _convert_other(a, raiseit=True)
        return a.__abs__(context=self)

    def add(self, a, b):
        a = _convert_other(a, raiseit=True)
        r = a.__add__(b, context=self)
        if r is NotImplemented:
            raise TypeError('Unable to convert %s to Decimal' % b)
        else:
            return r

    def _apply(self, a):
        return str(a._fix(self))

    def canonical(self, a):
        return a.canonical(context=self)

    def compare(self, a, b):
        a = _convert_other(a, raiseit=True)
        return a.compare(b, context=self)

    def compare_signal(self, a, b):
        a = _convert_other(a, raiseit=True)
        return a.compare_signal(b, context=self)

    def compare_total(self, a, b):
        a = _convert_other(a, raiseit=True)
        return a.compare_total(b)

    def compare_total_mag(self, a, b):
        a = _convert_other(a, raiseit=True)
        return a.compare_total_mag(b)

    def copy_abs(self, a):
        a = _convert_other(a, raiseit=True)
        return a.copy_abs()

    def copy_decimal(self, a):
        a = _convert_other(a, raiseit=True)
        return Decimal(a)

    def copy_negate(self, a):
        a = _convert_other(a, raiseit=True)
        return a.copy_negate()

    def copy_sign(self, a, b):
        a = _convert_other(a, raiseit=True)
        return a.copy_sign(b)

    def divide(self, a, b):
        a = _convert_other(a, raiseit=True)
        r = a.__div__(b, context=self)
        if r is NotImplemented:
            raise TypeError('Unable to convert %s to Decimal' % b)
        else:
            return r

    def divide_int(self, a, b):
        a = _convert_other(a, raiseit=True)
        r = a.__floordiv__(b, context=self)
        if r is NotImplemented:
            raise TypeError('Unable to convert %s to Decimal' % b)
        else:
            return r

    def divmod(self, a, b):
        a = _convert_other(a, raiseit=True)
        r = a.__divmod__(b, context=self)
        if r is NotImplemented:
            raise TypeError('Unable to convert %s to Decimal' % b)
        else:
            return r

    def exp(self, a):
        a = _convert_other(a, raiseit=True)
        return a.exp(context=self)

    def fma(self, a, b, c):
        a = _convert_other(a, raiseit=True)
        return a.fma(b, c, context=self)

    def is_canonical(self, a):
        return a.is_canonical()

    def is_finite(self, a):
        a = _convert_other(a, raiseit=True)
        return a.is_finite()

    def is_infinite(self, a):
        a = _convert_other(a, raiseit=True)
        return a.is_infinite()

    def is_nan(self, a):
        a = _convert_other(a, raiseit=True)
        return a.is_nan()

    def is_normal(self, a):
        a = _convert_other(a, raiseit=True)
        return a.is_normal(context=self)

    def is_qnan(self, a):
        a = _convert_other(a, raiseit=True)
        return a.is_qnan()

    def is_signed(self, a):
        a = _convert_other(a, raiseit=True)
        return a.is_signed()

    def is_snan(self, a):
        a = _convert_other(a, raiseit=True)
        return a.is_snan()

    def is_subnormal(self, a):
        a = _convert_other(a, raiseit=True)
        return a.is_subnormal(context=self)

    def is_zero(self, a):
        a = _convert_other(a, raiseit=True)
        return a.is_zero()

    def ln(self, a):
        a = _convert_other(a, raiseit=True)
        return a.ln(context=self)

    def log10(self, a):
        a = _convert_other(a, raiseit=True)
        return a.log10(context=self)

    def logb(self, a):
        a = _convert_other(a, raiseit=True)
        return a.logb(context=self)

    def logical_and(self, a, b):
        a = _convert_other(a, raiseit=True)
        return a.logical_and(b, context=self)

    def logical_invert(self, a):
        a = _convert_other(a, raiseit=True)
        return a.logical_invert(context=self)

    def logical_or(self, a, b):
        a = _convert_other(a, raiseit=True)
        return a.logical_or(b, context=self)

    def logical_xor(self, a, b):
        a = _convert_other(a, raiseit=True)
        return a.logical_xor(b, context=self)

    def max(self, a, b):
        a = _convert_other(a, raiseit=True)
        return a.max(b, context=self)

    def max_mag(self, a, b):
        a = _convert_other(a, raiseit=True)
        return a.max_mag(b, context=self)

    def min(self, a, b):
        a = _convert_other(a, raiseit=True)
        return a.min(b, context=self)

    def min_mag(self, a, b):
        a = _convert_other(a, raiseit=True)
        return a.min_mag(b, context=self)

    def minus(self, a):
        a = _convert_other(a, raiseit=True)
        return a.__neg__(context=self)

    def multiply(self, a, b):
        a = _convert_other(a, raiseit=True)
        r = a.__mul__(b, context=self)
        if r is NotImplemented:
            raise TypeError('Unable to convert %s to Decimal' % b)
        else:
            return r

    def next_minus(self, a):
        a = _convert_other(a, raiseit=True)
        return a.next_minus(context=self)

    def next_plus(self, a):
        a = _convert_other(a, raiseit=True)
        return a.next_plus(context=self)

    def next_toward(self, a, b):
        a = _convert_other(a, raiseit=True)
        return a.next_toward(b, context=self)

    def normalize(self, a):
        a = _convert_other(a, raiseit=True)
        return a.normalize(context=self)

    def number_class(self, a):
        a = _convert_other(a, raiseit=True)
        return a.number_class(context=self)

    def plus(self, a):
        a = _convert_other(a, raiseit=True)
        return a.__pos__(context=self)

    def power(self, a, b, modulo=None):
        a = _convert_other(a, raiseit=True)
        r = a.__pow__(b, modulo, context=self)
        if r is NotImplemented:
            raise TypeError('Unable to convert %s to Decimal' % b)
        else:
            return r

    def quantize(self, a, b):
        a = _convert_other(a, raiseit=True)
        return a.quantize(b, context=self)

    def radix(self):
        return Decimal(10)

    def remainder(self, a, b):
        a = _convert_other(a, raiseit=True)
        r = a.__mod__(b, context=self)
        if r is NotImplemented:
            raise TypeError('Unable to convert %s to Decimal' % b)
        else:
            return r

    def remainder_near(self, a, b):
        a = _convert_other(a, raiseit=True)
        return a.remainder_near(b, context=self)

    def rotate(self, a, b):
        a = _convert_other(a, raiseit=True)
        return a.rotate(b, context=self)

    def same_quantum(self, a, b):
        a = _convert_other(a, raiseit=True)
        return a.same_quantum(b)

    def scaleb(self, a, b):
        a = _convert_other(a, raiseit=True)
        return a.scaleb(b, context=self)

    def shift(self, a, b):
        a = _convert_other(a, raiseit=True)
        return a.shift(b, context=self)

    def sqrt(self, a):
        a = _convert_other(a, raiseit=True)
        return a.sqrt(context=self)

    def subtract(self, a, b):
        a = _convert_other(a, raiseit=True)
        r = a.__sub__(b, context=self)
        if r is NotImplemented:
            raise TypeError('Unable to convert %s to Decimal' % b)
        else:
            return r

    def to_eng_string(self, a):
        a = _convert_other(a, raiseit=True)
        return a.to_eng_string(context=self)

    def to_sci_string(self, a):
        a = _convert_other(a, raiseit=True)
        return a.__str__(context=self)

    def to_integral_exact(self, a):
        a = _convert_other(a, raiseit=True)
        return a.to_integral_exact(context=self)

    def to_integral_value(self, a):
        a = _convert_other(a, raiseit=True)
        return a.to_integral_value(context=self)

    to_integral = to_integral_value


class _WorkRep(object):
    __slots__ = ('sign', 'int', 'exp')

    def __init__(self, value=None):
        if value is None:
            self.sign = None
            self.int = 0
            self.exp = None
        elif isinstance(value, Decimal):
            self.sign = value._sign
            self.int = int(value._int)
            self.exp = value._exp
        else:
            self.sign = value[0]
            self.int = value[1]
            self.exp = value[2]
        return

    def __repr__(self):
        return '(%r, %r, %r)' % (self.sign, self.int, self.exp)

    __str__ = __repr__


def _normalize(op1, op2, prec=0):
    if op1.exp < op2.exp:
        tmp = op2
        other = op1
    else:
        tmp = op1
        other = op2
    tmp_len = len(str(tmp.int))
    other_len = len(str(other.int))
    exp = tmp.exp + min(-1, tmp_len - prec - 2)
    if other_len + other.exp - 1 < exp:
        other.int = 1
        other.exp = exp
    tmp.int *= 10 ** (tmp.exp - other.exp)
    tmp.exp = other.exp
    return (op1, op2)


def _nbits(n, correction={'0': 4,
 '1': 3,
 '2': 2,
 '3': 2,
 '4': 1,
 '5': 1,
 '6': 1,
 '7': 1,
 '8': 0,
 '9': 0,
 'a': 0,
 'b': 0,
 'c': 0,
 'd': 0,
 'e': 0,
 'f': 0}):
    if n < 0:
        raise ValueError('The argument to _nbits should be nonnegative.')
    hex_n = '%x' % n
    return 4 * len(hex_n) - correction[hex_n[0]]


def _decimal_lshift_exact(n, e):
    if n == 0:
        return 0
    elif e >= 0:
        return n * 10 ** e
    else:
        str_n = str(abs(n))
        val_n = len(str_n) - len(str_n.rstrip('0'))
        if val_n < -e:
            return None
        return n // 10 ** (-e)
        return None


def _sqrt_nearest(n, a):
    if n <= 0 or a <= 0:
        raise ValueError('Both arguments to _sqrt_nearest should be positive.')
    b = 0
    while a != b:
        b, a = a, a - -n // a >> 1

    return a


def _rshift_nearest(x, shift):
    b, q = 1L << shift, x >> shift
    return q + (2 * (x & b - 1) + (q & 1) > b)


def _div_nearest(a, b):
    q, r = divmod(a, b)
    return q + (2 * r + (q & 1) > b)


def _ilog(x, M, L=8):
    y = x - M
    R = 0
    while 1:
        y = (R <= L and long(abs(y)) << L - R >= M or R > L and abs(y) >> R - L >= M) and _div_nearest(long(M * y) << 1, M + _sqrt_nearest(M * (M + _rshift_nearest(y, R)), M))
        R += 1

    T = -int(-10 * len(str(M)) // (3 * L))
    yshift = _rshift_nearest(y, R)
    w = _div_nearest(M, T)
    for k in xrange(T - 1, 0, -1):
        w = _div_nearest(M, k) - _div_nearest(yshift * w, M)

    return _div_nearest(w * y, M)


def _dlog10(c, e, p):
    p += 2
    l = len(str(c))
    f = e + l - (e + l >= 1)
    if p > 0:
        M = 10 ** p
        k = e + p - f
        if k >= 0:
            c *= 10 ** k
        else:
            c = _div_nearest(c, 10 ** (-k))
        log_d = _ilog(c, M)
        log_10 = _log10_digits(p)
        log_d = _div_nearest(log_d * M, log_10)
        log_tenpower = f * M
    else:
        log_d = 0
        log_tenpower = _div_nearest(f, 10 ** (-p))
    return _div_nearest(log_tenpower + log_d, 100)


def _dlog(c, e, p):
    p += 2
    l = len(str(c))
    f = e + l - (e + l >= 1)
    if p > 0:
        k = e + p - f
        if k >= 0:
            c *= 10 ** k
        else:
            c = _div_nearest(c, 10 ** (-k))
        log_d = _ilog(c, 10 ** p)
    else:
        log_d = 0
    if f:
        extra = len(str(abs(f))) - 1
        if p + extra >= 0:
            f_log_ten = _div_nearest(f * _log10_digits(p + extra), 10 ** extra)
        else:
            f_log_ten = 0
    else:
        f_log_ten = 0
    return _div_nearest(f_log_ten + log_d, 100)


class _Log10Memoize(object):

    def __init__(self):
        self.digits = '23025850929940456840179914546843642076011014886'

    def getdigits(self, p):
        if p < 0:
            raise ValueError('p should be nonnegative')
        if p >= len(self.digits):
            extra = 3
            while True:
                M = 10 ** (p + extra + 2)
                digits = str(_div_nearest(_ilog(10 * M, M), 100))
                if digits[-extra:] != '0' * extra:
                    break
                extra += 3

            self.digits = digits.rstrip('0')[:-1]
        return int(self.digits[:p + 1])


_log10_digits = _Log10Memoize().getdigits

def _iexp(x, M, L=8):
    R = _nbits((long(x) << L) // M)
    T = -int(-10 * len(str(M)) // (3 * L))
    y = _div_nearest(x, T)
    Mshift = long(M) << R
    for i in xrange(T - 1, 0, -1):
        y = _div_nearest(x * (Mshift + y), Mshift * i)

    for k in xrange(R - 1, -1, -1):
        Mshift = long(M) << k + 2
        y = _div_nearest(y * (y + Mshift), Mshift)

    return M + y


def _dexp(c, e, p):
    p += 2
    extra = max(0, e + len(str(c)) - 1)
    q = p + extra
    shift = e + q
    if shift >= 0:
        cshift = c * 10 ** shift
    else:
        cshift = c // 10 ** (-shift)
    quot, rem = divmod(cshift, _log10_digits(q))
    rem = _div_nearest(rem, 10 ** extra)
    return (_div_nearest(_iexp(rem, 10 ** p), 1000), quot - p + 3)


def _dpower(xc, xe, yc, ye, p):
    b = len(str(abs(yc))) + ye
    lxc = _dlog(xc, xe, p + b + 1)
    shift = ye - b
    if shift >= 0:
        pc = lxc * yc * 10 ** shift
    else:
        pc = _div_nearest(lxc * yc, 10 ** (-shift))
    if pc == 0:
        if (len(str(xc)) + xe >= 1) == (yc > 0):
            coeff, exp = 10 ** (p - 1) + 1, 1 - p
        else:
            coeff, exp = 10 ** p - 1, -p
    else:
        coeff, exp = _dexp(pc, -(p + 1), p + 1)
        coeff = _div_nearest(coeff, 10)
        exp += 1
    return (coeff, exp)


def _log10_lb(c, correction={'1': 100,
 '2': 70,
 '3': 53,
 '4': 40,
 '5': 31,
 '6': 23,
 '7': 16,
 '8': 10,
 '9': 5}):
    if c <= 0:
        raise ValueError('The argument to _log10_lb should be nonnegative.')
    str_c = str(c)
    return 100 * len(str_c) - correction[str_c[0]]


def _convert_other(other, raiseit=False, allow_float=False):
    if isinstance(other, Decimal):
        return other
    if isinstance(other, (int, long)):
        return Decimal(other)
    if allow_float and isinstance(other, float):
        return Decimal.from_float(other)
    if raiseit:
        raise TypeError('Unable to convert %s to Decimal' % other)
    return NotImplemented


DefaultContext = Context(prec=28, rounding=ROUND_HALF_EVEN, traps=[DivisionByZero, Overflow, InvalidOperation], flags=[], Emax=999999999, Emin=-999999999, capitals=1)
BasicContext = Context(prec=9, rounding=ROUND_HALF_UP, traps=[DivisionByZero,
 Overflow,
 InvalidOperation,
 Clamped,
 Underflow], flags=[])
ExtendedContext = Context(prec=9, rounding=ROUND_HALF_EVEN, traps=[], flags=[])
import re
_parser = re.compile('        # A numeric string consists of:\n#    \\s*\n    (?P<sign>[-+])?              # an optional sign, followed by either...\n    (\n        (?=\\d|\\.\\d)              # ...a number (with at least one digit)\n        (?P<int>\\d*)             # having a (possibly empty) integer part\n        (\\.(?P<frac>\\d*))?       # followed by an optional fractional part\n        (E(?P<exp>[-+]?\\d+))?    # followed by an optional exponent, or...\n    |\n        Inf(inity)?              # ...an infinity, or...\n    |\n        (?P<signal>s)?           # ...an (optionally signaling)\n        NaN                      # NaN\n        (?P<diag>\\d*)            # with (possibly empty) diagnostic info.\n    )\n#    \\s*\n    \\Z\n', re.VERBOSE | re.IGNORECASE | re.UNICODE).match
_all_zeros = re.compile('0*$').match
_exact_half = re.compile('50*$').match
_parse_format_specifier_regex = re.compile('\\A\n(?:\n   (?P<fill>.)?\n   (?P<align>[<>=^])\n)?\n(?P<sign>[-+ ])?\n(?P<zeropad>0)?\n(?P<minimumwidth>(?!0)\\d+)?\n(?P<thousands_sep>,)?\n(?:\\.(?P<precision>0|(?!0)\\d+))?\n(?P<type>[eEfFgGn%])?\n\\Z\n', re.VERBOSE)
del re
try:
    import locale as _locale
except ImportError:
    pass

def _parse_format_specifier(format_spec, _localeconv=None):
    m = _parse_format_specifier_regex.match(format_spec)
    if m is None:
        raise ValueError('Invalid format specifier: ' + format_spec)
    format_dict = m.groupdict()
    fill = format_dict['fill']
    align = format_dict['align']
    format_dict['zeropad'] = format_dict['zeropad'] is not None
    if format_dict['zeropad']:
        if fill is not None:
            raise ValueError("Fill character conflicts with '0' in format specifier: " + format_spec)
        if align is not None:
            raise ValueError("Alignment conflicts with '0' in format specifier: " + format_spec)
    format_dict['fill'] = fill or ' '
    format_dict['align'] = align or '>'
    if format_dict['sign'] is None:
        format_dict['sign'] = '-'
    format_dict['minimumwidth'] = int(format_dict['minimumwidth'] or '0')
    if format_dict['precision'] is not None:
        format_dict['precision'] = int(format_dict['precision'])
    if format_dict['precision'] == 0:
        if format_dict['type'] is None or format_dict['type'] in 'gG':
            format_dict['precision'] = 1
    if format_dict['type'] == 'n':
        format_dict['type'] = 'g'
        if _localeconv is None:
            _localeconv = _locale.localeconv()
        if format_dict['thousands_sep'] is not None:
            raise ValueError("Explicit thousands separator conflicts with 'n' type in format specifier: " + format_spec)
        format_dict['thousands_sep'] = _localeconv['thousands_sep']
        format_dict['grouping'] = _localeconv['grouping']
        format_dict['decimal_point'] = _localeconv['decimal_point']
    else:
        if format_dict['thousands_sep'] is None:
            format_dict['thousands_sep'] = ''
        format_dict['grouping'] = [3, 0]
        format_dict['decimal_point'] = '.'
    format_dict['unicode'] = isinstance(format_spec, unicode)
    return format_dict


def _format_align(sign, body, spec):
    minimumwidth = spec['minimumwidth']
    fill = spec['fill']
    padding = fill * (minimumwidth - len(sign) - len(body))
    align = spec['align']
    if align == '<':
        result = sign + body + padding
    elif align == '>':
        result = padding + sign + body
    elif align == '=':
        result = sign + padding + body
    elif align == '^':
        half = len(padding) // 2
        result = padding[:half] + sign + body + padding[half:]
    else:
        raise ValueError('Unrecognised alignment field')
    if spec['unicode']:
        result = unicode(result)
    return result


def _group_lengths(grouping):
    from itertools import chain, repeat
    if not grouping:
        return []
    if grouping[-1] == 0 and len(grouping) >= 2:
        return chain(grouping[:-1], repeat(grouping[-2]))
    if grouping[-1] == _locale.CHAR_MAX:
        return grouping[:-1]
    raise ValueError('unrecognised format for grouping')


def _insert_thousands_sep(digits, spec, min_width=1):
    sep = spec['thousands_sep']
    grouping = spec['grouping']
    groups = []
    for l in _group_lengths(grouping):
        if l <= 0:
            raise ValueError('group length should be positive')
        l = min(max(len(digits), min_width, 1), l)
        groups.append('0' * (l - len(digits)) + digits[-l:])
        digits = digits[:-l]
        min_width -= l
        if not digits and min_width <= 0:
            break
        min_width -= len(sep)
    else:
        l = max(len(digits), min_width, 1)
        groups.append('0' * (l - len(digits)) + digits[-l:])

    return sep.join(reversed(groups))


def _format_sign(is_negative, spec):
    if is_negative:
        return '-'
    elif spec['sign'] in ' +':
        return spec['sign']
    else:
        return ''


def _format_number(is_negative, intpart, fracpart, exp, spec):
    sign = _format_sign(is_negative, spec)
    if fracpart:
        fracpart = spec['decimal_point'] + fracpart
    if exp != 0 or spec['type'] in 'eE':
        echar = {'E': 'E',
         'e': 'e',
         'G': 'E',
         'g': 'e'}[spec['type']]
        fracpart += '{0}{1:+}'.format(echar, exp)
    if spec['type'] == '%':
        fracpart += '%'
    if spec['zeropad']:
        min_width = spec['minimumwidth'] - len(fracpart) - len(sign)
    else:
        min_width = 0
    intpart = _insert_thousands_sep(intpart, spec, min_width)
    return _format_align(sign, intpart + fracpart, spec)


_Infinity = Decimal('Inf')
_NegativeInfinity = Decimal('-Inf')
_NaN = Decimal('NaN')
_Zero = Decimal(0)
_One = Decimal(1)
_NegativeOne = Decimal(-1)
_SignedInfinity = (_Infinity, _NegativeInfinity)
if __name__ == '__main__':
    import doctest, sys
    doctest.testmod(sys.modules[__name__])
