# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/money.py
from collections import namedtuple
from shared_utils import CONST_CONTAINER

class Currency(CONST_CONTAINER):
    """
    Enumeration of available currencies.
    Note that the order corresponds to the order of money tuple represented on the server
    side and should not be changed.
    Also be aware that enumeration values (currency string representation) are used on UI and
    server sides and should not be changed.
    """
    CREDITS = 'credits'
    GOLD = 'gold'
    CRYSTAL = 'crystal'
    ALL = (CREDITS, GOLD, CRYSTAL)
    BY_WEIGHT = (GOLD, CRYSTAL, CREDITS)


_Money = namedtuple('Money', Currency.ALL)

class Money(_Money):
    """
    Represents money on the client side. Note that all instances of Money class are immutable
    objects. Therefore all public methods don't change object itself but return a new Money object.
    The following operations are supported by class Money:
    - arithmetical operations: +, -, *, /
    - comparison operations: >, >=, !=, ==, <, <=
    - truth value testing
    - unpacking
    - iterators (simple by value or currency + value pairs)
    - etc.
    Also there are a few helpers method to exchange currencies, to determine shortage and others.
    """

    @staticmethod
    def __new__(cls, credits=0, gold=0, crystal=0, *args, **kwargs):
        return _Money.__new__(cls, credits=credits, gold=gold, crystal=crystal)

    @classmethod
    def makeFrom(cls, currency, value):
        """
        Makes instance of Money class based on the given currency and value. Values for all other
        currencies are initialized by 0.
        
        :param currency: A currency from the Currency enumeration.
        :param value: A currency value.
        :return: A new instance of Money class.
        """
        return Money(**{currency: value})

    @classmethod
    def makeMoney(cls, data):
        """
        Converts the given data to Money. Supported types: tuple, dict, Money. If data has invalid type, returns None.
        
        :param data: data to be converted (tuple, dict or Money).
        :return: A new instance of Money class or None if the data has unsupported type.
        """
        if isinstance(data, tuple):
            return Money(*data)
        elif isinstance(data, dict):
            return Money(**data)
        else:
            return data if isinstance(data, Money) else None

    @classmethod
    def hasMoney(cls, data):
        """
        Checks whether the given dictionary has a key equal to an existing currency.
        
        :param data: any dictionary.
        :return: Returns True if the given dictionary has a key equal to an existing currency. Otherwise, false.
        """
        for c in Currency.ALL:
            if c in data:
                return True

        return False

    @classmethod
    def extractMoneyDict(cls, data):
        """
        Copies all existing currencies from the given dict to a new one.
        
        :param data: any dictionary.
        :return: Returns dict with currencies that are present in the given one.
        """
        return dict([ (c, data[c]) for c in Currency.ALL if c in data ])

    def get(self, currency):
        """
        Gets a value by the given currency.
        
        :param currency: A currency from the Currency enumeration.
        :return: A currency value.
        """
        return getattr(self, currency)

    def replace(self, currency, value):
        """
        Creates a copy of money object and replaces value of the given currency. Values of all
        other currencies are copied without any changes..
        
        :param currency: A currency from the Currency enumeration.
        :param value: A new value for the given currency.
        :return: A copy of original money object with the given value for the given currency.
        """
        return self.replaceAll({currency: value})

    def replaceAll(self, values):
        """
        Creates a copy of money object and replaces values of the given currencies. Values of all
        other currencies are copied without any changes..
        
        :param values: Values that replace current values. Represented by dict, where keys correspond to
                       Currency strings.
        :return: A copy of original money object with updated values.
        """
        return self._replace(**values)

    def copy(self):
        """
        Creates a deep copy of money.
        
        :return: A deep copy of original money object.
        """
        return Money(*self)

    def exchange(self, currency, toCurrency, rate):
        """
        Creates a copy of money object and exchanges value of 'currency' to value of 'toCurrency'
        by the given rate.
        Note that the currency that is exchanged is set to 0.
        
        :param currency: A currency that should be exchanged.
        :param toCurrency: Destination currency.
        :param rate: An exchange rate.
        :return: A copy of original money object with updated values for the given currencies.
        """
        assert currency != toCurrency
        value = self.get(toCurrency) + self.get(currency) * rate
        return self._replace(**{currency: 0,
         toCurrency: value})

    def isSet(self, currency):
        """
        Checks whether value of the given currencies is not 0.
        
        :param currency: A currency from the Currency enumeration.
        :return: False if value of the given currency is 0, otherwise True.
        
        """
        return currency in self

    def isAllSet(self):
        """
        Returns True if all currencies are not 0. Otherwise, False.
        """
        for v in self:
            if v == 0:
                return False

        return True

    def getSetCurrencies(self, byWeight=True):
        """
        Gets all set currencies sorted by weight. See isSet method and Currency.BY_WEIGHT
        enumeration.
        
        :param byWeight: If True sort list by Currency.BY_WEIGHT, otherwise the direct
                        order is used.
        
        :return: List of set currencies from Currency enumeration.
        """
        currencies = Currency.BY_WEIGHT if byWeight else Currency.ALL
        return [ c for c in currencies if self.isSet(c) ]

    def getCurrency(self, byWeight=True):
        """
        Gets a currency of money. Since money is made up several currencies, the method takes
        into account the currency weight (Currency.BY_WEIGHT) and returns the first currency
        that is not 0. If all currencies are set to 0, returns Currency.CREDITS by default.
        
        :param byWeight: If True Currency.BY_WEIGHT order is used, otherwise the direct
                        order is used.
        
        :return: A currency from the Currency enumeration.
        """
        currencies = Currency.BY_WEIGHT if byWeight else Currency.ALL
        for c in currencies:
            if self.isSet(c):
                return c

        return Currency.CREDITS

    def toNonNegative(self):
        """
        Replaces all negative currencies to 0.
        :return: Copy of the current money with replaced negative currencies to 0.
        """
        return self.apply(lambda v: max(0, v))

    def toAbs(self):
        """
        Replaces all values to their absolute values.
        
        :return: Copy of the current money with updated values
        """
        return self.apply(lambda v: abs(v))

    def toDict(self):
        """
        Converts money to dictionary. Keys correspond to Currency strings.
        """
        return dict(((c, v) for c, v in self.iteritems()))

    def toSignDict(self):
        """
        Converts money to dictionary that includes only set currencies.
        NOTE: As per Money 2.0 concept, if v != 0 is not correct condition!
        """
        return dict(((c, v) for c, v in self.iteritems() if v != 0))

    def toMoneySet(self):
        """
        Converts Money to MoneySet.
        
        :return: Returns MoneySet instance including self.
        """
        return MoneySet((self,))

    def toDictsList(self):
        """
        Returns money in [{}] format.
        """
        return [self.toSignDict()]

    def iteritems(self):
        """
        Returns an iterator that allows to iterate money by currency and value simultaneously.
        
        :return: Returns an iterator over the money's (currency, value) pairs.
        """
        for c in Currency.ALL:
            yield (c, self.get(c))

    def apply(self, formatter):
        """
        Applies the given formatter to all currencies values.
        
        :param formatter: An callable object that gives one parameter (currency value) and
        returns a new formatted value.
        :return: A new formatted money object.
        """
        return self.__convert(lambda c, v, o: formatter(v), None)

    def getShortage(self, price):
        """
        Returns shortage - subtracts the current money from the given price in money and returns
        list of (currency, delta) tuples sorted by currency weight for which delta is more than 0.
        
        :param price: Price in Money
        :return: List of (currency, delta) tuples sorted by currency weight
        """
        shortage = list()
        for c in Currency.BY_WEIGHT:
            delta = price.get(c) - self.get(c)
            if delta > 0:
                shortage.append((c, delta))

        return shortage

    def getNegative(self):
        """
        Returns list of (currency, delta) tuples of currencies for which value < 0
        """
        return [ (c, v) for c, v in self.iteritems() if v < 0 ]

    def getPositive(self):
        """
        Returns list of (currency, delta) tuples of currencies for which value > 0
        """
        return [ (c, v) for c, v in self.iteritems() if v > 0 ]

    def __iter__(self):
        """
        Returns an iterator object. The object is required to support the iterator protocol.
        Iterable values are represented by currency's value in order determined by Currency
        enumeration.
        """
        for c in Currency.ALL:
            yield self.get(c)

    def __contains__(self, currency):
        """
        Checks whether value of the given currencies is set (not 0).
        
        :param currency: A currency from the Currency enumeration.
        :return: True if value of the given currency is set, otherwise False.
        """
        return self.get(currency) != 0

    def __add__(self, other):
        """
        These methods are called to implement the binary arithmetic operation +.
        Performs sum of two Money objects.
        
        :param other: Summand represented by Money class.
        :return: A new Money object.
        """
        return self.__convert(lambda c, v, o: v + o.get(c), other)

    def __iadd__(self, other):
        """
        These methods are called to implement the augmented arithmetic assignment +=.
        Performs sum of two Money objects.
        
        :param other: Summand represented by Money class.
        :return: A new Money object.
        """
        return self.__add__(other)

    def __sub__(self, other):
        """
        These methods are called to implement the binary arithmetic operation -.
        
        :param other: Deduction represented by Money class.
        :return: A new Money object.
        """
        return self.__convert(lambda c, v, o: v - o.get(c), other)

    def __isub__(self, other):
        """
        These methods are called to implement the augmented arithmetic assignment -=.
        
        :param other: Deduction represented by Money class.
        :return: A new Money object.
        """
        return self.__sub__(other)

    def __mul__(self, n):
        """
        These methods are called to implement the binary arithmetic operation *.
        
        :param n: Multiplier represented by a number (not a Money).
        :return: A new Money object.
        """
        return self.__convert(lambda c, v, o: v * o, n)

    def __rmul__(self, n):
        """
        These methods are called to implement the binary arithmetic operation * with reflected
        (swapped) operands. These functions are only called if the left operand does not support
        the corresponding operation and the operands are of different types.
        
        :param n: Multiplier represented by a number (not a Money).
        :return: A new Money object.
        """
        return self.__mul__(n)

    def __div__(self, n):
        """
        These methods are called to implement the binary arithmetic operation /.
        
        :param n: Denominator represented by a number (not a Money).
        :return: A new Money object.
        """
        return self.__convert(lambda c, v, o: v / o, n)

    def __rdiv__(self, n):
        """
        These methods are called to implement the binary arithmetic operation / with reflected
        (swapped) operands. These functions are only called if the left operand does not support
        the corresponding operation and the operands are of different types.
        
        :param n: Denominator represented by a number (not a Money).
        :return: A new Money object.
        """
        return self.__mul__(n)

    def __lt__(self, other):
        """
        These methods are called to implement the comparison operation <.
        
        :param other: An instance of Money class
        :return: True if values of ALL currencies are less than the appropriate values of the given
        money, otherwise False.
        """
        for c, v in self.iteritems():
            if v >= other.get(c):
                return False

        return True

    def __le__(self, other):
        """
        These methods are called to implement the comparison operation <=.
        
        :param other: An instance of Money class
        :return: True if values of ALL currencies are less or equal to the appropriate values of
        the given money, otherwise False.
        """
        for c, v in self.iteritems():
            if v > other.get(c):
                return False

        return True

    def __gt__(self, other):
        """
        These methods are called to implement the comparison operation >.
        
        :param other: An instance of Money class
        :return: True if values of ALL currencies are more than the appropriate values of the given
        money, otherwise False.
        """
        for c, v in self.iteritems():
            if other.get(c) >= v:
                return False

        return True

    def __ge__(self, other):
        """
        These methods are called to implement the comparison operation >=.
        
        :param other: An instance of Money class
        :return: True if values of ALL currencies are more or equal to the appropriate values of
        the given money, otherwise False.
        """
        for c, v in self.iteritems():
            if other.get(c) > v:
                return False

        return True

    def __eq__(self, other):
        """
        These methods are called to implement the comparison operation ==.
        
        :param other: An instance of Money class
        :return: True if values of ALL currencies are equal to the appropriate values of
        the given money, otherwise False.
        """
        for c, v in self.iteritems():
            if other.get(c) != v:
                return False

        return True

    def __ne__(self, other):
        """
        These methods are called to implement the comparison operation !=.
        
        :param other: An instance of Money class
        :return: True if at least one value is not equal to the appropriate value of the given
        money, otherwise False.
        """
        return not self.__eq__(other)

    def __nonzero__(self):
        """
        Called to implement truth value testing and the built-in operation bool().
        
        :return: False if values of all currencies is set to 0 (Zero object), otherwise True.
        """
        for v in self:
            if v != 0:
                return True

        return False

    def __convert(self, function, other):
        """
        Applies the given function to each currency and returns a new Money object.
        Note that the function takes three arguments:
        - formatted currency ('c')
        - original value ('v')
        - the given object ('other').
        
        :param other: Object to be passed to the the given function as the last argument.
        :param function: A callable object that takes tree arguments described above.
        :return: A new Money object.
        """
        kwargs = dict(((c, function(c, v, other)) for c, v in self.iteritems()))
        return Money(**kwargs)


ZERO_MONEY = Money()

class MoneySet(tuple):
    """
    Represents container of moneys. Corresponds to Money 2.0 concept - implements the OR condition.
    """

    def __init__(self, prices=()):
        super(MoneySet, self).__init__(prices)

    def toDictsList(self):
        """
        Returns money set in [{}, {}, ... ,{}] format.
        """
        return [ money.toSignDict() for money in self ]
