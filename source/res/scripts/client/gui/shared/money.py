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
    __INDEXES = {c:i for i, c in enumerate(ALL)}

    @classmethod
    def getCurrencyIndex(cls, currency):
        return cls.__INDEXES.get(currency, None)


__Money = namedtuple('_Money', Currency.ALL)
__Money.__new__.__defaults__ = len(Currency.ALL) * (0,)

class _Money(__Money):
    """
    Money 1.0 concept.
    """

    def get(self, currency):
        return getattr(self, currency)


class Money(object):
    """
    Represents money on the client side. Note that all instances of Money class are immutable objects. Therefore all
    public methods don't change object itself but return a new Money object.
    The following operations are supported by class Money:
    - arithmetical operations: +, -, *, /
    - comparison operations: >, >=, !=, ==, <, <=
    - truth value testing
    - unpacking
    - iterators (simple by value or currency + value pairs)
    - etc.
    Also there are a few helpers method to exchange currencies, to determine shortage and others.
    To see some usage examples please refer to unit tests (test_money.py).
    """
    __slots__ = ('__values',)

    def __init__(self, credits=None, gold=None, crystal=None, *args, **kwargs):
        super(Money, self).__init__()
        self.__values = {}
        self.__initValue(self.__values, Currency.CREDITS, credits)
        self.__initValue(self.__values, Currency.GOLD, gold)
        self.__initValue(self.__values, Currency.CRYSTAL, crystal)

    @property
    def credits(self):
        return self.__values.get(Currency.CREDITS)

    @property
    def gold(self):
        return self.__values.get(Currency.GOLD)

    @property
    def crystal(self):
        return self.__values.get(Currency.CRYSTAL)

    @classmethod
    def makeFrom(cls, currency, value):
        """
        Makes instance of Money class based on the given currency and value. Values for all other
        currencies are undefined (set to None).
        
        :param currency: A currency from the Currency enumeration.
        :param value: A currency value.
        :return: A new instance of Money class.
        """
        return MONEY_UNDEFINED.replace(currency, value)

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
        return {c:data[c] for c in Currency.ALL if c in data}

    def get(self, currency, default=None):
        """
        Gets a value by the given currency. If None, value is not set (not defined).
        
        :param currency: A currency from the Currency enumeration.
        :return: A currency value. Maybe be None if value is not defined for the given currency.
        """
        return self.__values.get(currency, default)

    def replace(self, currency, value):
        """
        Creates a copy of money object and replaces value of the given currency. Values of all
        other currencies are copied without any changes.
        
        :param currency: A currency from the Currency enumeration.
        :param value: A new value for the given currency.
        :return: A copy of original money object with the given value for the given currency.
        """
        copy = self.__values.copy()
        self.__setValue(copy, currency, value)
        return Money(**copy)

    def replaceAll(self, values):
        """
        Creates a copy of money object and replaces values of the given currencies. Values of all
        other currencies are copied without any changes..
        
        :param values: Values that replace current values. Represented by dict, where keys correspond to
                       Currency strings.
        :return: A copy of original money object with updated values.
        """
        copy = self.__values.copy()
        for currency, value in values.iteritems():
            self.__setValue(copy, currency, value)

        return Money(**copy)

    def copy(self):
        """
        Creates a deep copy of money.
        
        :return: A deep copy of original money object.
        """
        return Money(**self.__values)

    def exchange(self, currency, toCurrency, rate, default=None):
        """
        Creates a copy of money object and exchanges value of 'currency' to value of 'toCurrency' by the given rate.
        Note that the currency that is exchanged is set to the given default value.
        
        :param currency: A currency that should be exchanged.
        :param toCurrency: Destination currency.
        :param rate: An exchange rate.
        :param default: A new value of currency to be exchanged.
        :return: A copy of original money object with updated values for the given currencies.
        """
        assert currency != toCurrency
        assert currency in self.__values
        value = self.get(toCurrency, 0) + self.get(currency) * rate
        copy = self.__values.copy()
        self.__setValue(copy, currency, default)
        self.__setValue(copy, toCurrency, value)
        return Money(**copy)

    def isDefined(self):
        """
        Checks whether any value is defined (not None).
        
        :return: False if all values are not defined (None), otherwise True.
        """
        return bool(self.__values)

    def isCurrencyDefined(self, currency):
        """
        Checks whether the given currency is defined (not None).
        
        :param currency: A currency from the Currency enumeration.
        :return: False if the currency is None, otherwise True.
        """
        return currency in self.__values

    def isSet(self, currency):
        """
        Checks whether value of the given currencies is not None and != 0.
        
        :param currency: A currency from the Currency enumeration.
        :return: False if value of the given currency is None or 0, otherwise True.
        """
        return currency in self and self.get(currency) != 0

    def isCompound(self):
        """
        Returns True if the money has several defined currencies (compound money/price), otherwise returns false.
        :return: bool
        """
        return len(self.__values) > 1

    def getSetCurrencies(self, byWeight=True):
        """
        Gets all set currencies sorted by weight. See isSet method and Currency.BY_WEIGHT enumeration.
        
        :param byWeight: If True sort list by Currency.BY_WEIGHT, otherwise the direct order is used.
        :return: List of set currencies from Currency enumeration.
        """
        return [ c for c in self.__getCurrenciesIterator(byWeight) if self.__values[c] != 0 ]

    def getCurrency(self, byWeight=True):
        """
        Gets a currency of money. Since money is made up several currencies, the method takes
        into account the currency weight (Currency.BY_WEIGHT) and returns the first currency
        that is set (if all are unset, that the first one that is defined). If all currencies
        are unset or not defined,returns Currency.CREDITS by default.
        
        :param byWeight: If True Currency.BY_WEIGHT order is used, otherwise the direct
                        order is used.
        
        :return: A currency from the Currency enumeration.
        """
        currency = None
        if self.__values:
            for c in self.__getCurrenciesIterator(byWeight):
                if self.__values[c] != 0:
                    return c
                if currency is None:
                    currency = c

        return currency or Currency.CREDITS

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
        return {c:v for c, v in self.__values.iteritems()}

    def toSignDict(self):
        """
        Converts money to dictionary that includes only set currencies.
        NOTE: As per Money 2.0 concept, if v != 0 is not correct condition!
        """
        return {c:v for c, v in self.__values.iteritems() if v != 0}

    def toMoneySet(self):
        """
        Converts Money to MoneySet.
        
        :return: Returns MoneySet instance including only itself.
        """
        return MoneySet((self,))

    def toDictsList(self):
        """
        Returns money in [{}] format.
        """
        return [self.toSignDict()]

    def iteritems(self, byWeight=False):
        """
        Returns an iterator that allows to iterate money by currency and value simultaneously.
        
        :return: Returns an iterator over the money's (currency, value) pairs.
        """
        for c in self.__getCurrenciesIterator(byWeight=byWeight):
            yield (c, self.__values.get(c))

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
        Returns shortage - subtracts the current money from the given price in Money and returns
        shortage Money where set only those currencies for which delta is more than 0.
        To see examples please refer to test_money_getShortage routine (test_money.py)
        
        :param price: Price in Money.
        :return: Money.
        """
        shortage = MONEY_UNDEFINED
        for c in price.__getCurrenciesIterator(byWeight=True):
            delta = price.get(c) - self.get(c, 0)
            if delta > 0:
                shortage = shortage.replace(c, delta)

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

    @classmethod
    def makeMoney(cls, data):
        """
        Converts the given data to Money. Supported types: tuple, dict, Money. If data has invalid type, returns None.
        For dict object the next stucture is supported: Keys have Currency type (i.e. string), values - float.
        For tuple object - tuple object with values in order: CREDITS, GOLD, CRYSTAL
        
        :param data: data to be converted (tuple, dict or Money).
        :return: A new instance of Money class or None if the data has unsupported type.
        """
        if isinstance(data, Money):
            return data
        elif isinstance(data, (tuple, list)):
            return Money.makeFromMoneyTuple(data)
        else:
            return Money(**data) if isinstance(data, dict) else None

    @classmethod
    def makeFromMoneyTuple(cls, moneyTuple):
        """
        Makes instance of Money class based on the given money tuple (Money 1.0).
        
        NOTE: the method should not be used because it violates Money 2.0 concept and it is implemented only
        to support legacy code (old Client-Server money protocol).
        
        :param moneyTuple: tuple, where undefined or unset values = 0 (in old terms undefined=unset=0).
        :return: A new instance of Money class.
        """
        assert isinstance(moneyTuple, (tuple, list))
        setValues = {Currency.ALL[index]:v for index, v in enumerate(moneyTuple) if v != 0}
        return Money(**setValues)

    def toMoneyTuple(self):
        """
        Returns tuple containing all currencies (Money 1.0). If any currency value is not defined (None), 0 is placed
        into the tuple. Order corresponds to Currency.ALL (default order).
        
        NOTE: this method should not be used because it violates Money 2.0 concept and it is implemented only
        to support legacy code (old Python-AS money protocol). Instead of it use toDictsList.
        """
        return _Money(**self.__values)

    def getSignValue(self, currency):
        """
        Gets a value by the given currency. If undefined returns 0.
        
        NOTE: this method should not be used because it violates Money 2.0 concept and it is implemented only
        to support legacy code (old Python-AS money protocol). Instead of it use toDictsList.
        
        :param currency: A currency from the Currency enumeration.
        :return: A currency value as int (if undefined - 0).
        """
        return self.get(currency, 0)

    def iterallitems(self, byWeight=False):
        """
        Returns an iterator that allows to iterate money by currency and value simultaneously.
        
        NOTE: the method should not be used because it violates Money 2.0 concept and it is implemented only
        to support legacy code (old Python-AS money protocol). Instead of it use the iteritems method.
        
        :param byWeight: If True use Currency.BY_WEIGHT order, otherwise - the direct order.
        :return: Returns an iterator over the money's (currency, value) pairs.
        """
        order = Currency.BY_WEIGHT if byWeight else Currency.ALL
        for c in order:
            yield (c, self.__values.get(c, 0))

    def __getitem__(self, index):
        """
        Operator []. Called to implement evaluation of self[int].
        
        NOTE: operator [] should not be used because it violates Money 2.0 concept and it is implemented only
        to support legacy code (old Client-Server money protocol). Instead of it use the get method or appropriate
        properties.
        
        :param index: index of currency (order corresponds to Currency.ALL)
        :return: float, if value is defined, otherwise - 0.
        """
        return self.get(Currency.ALL[index], 0)

    def __repr__(self):
        return 'Money({})'.format(', '.join([ '{}'.format(self.get(c)) for c in Currency.ALL ]))

    def __iter__(self):
        """
        Returns an iterator object. The object is required to support the iterator protocol.
        Iterable values are represented by currency's value in order determined by Currency
        enumeration.
        """
        for c in self.__getCurrenciesIterator(byWeight=False):
            yield self.__values[c]

    def __contains__(self, currency):
        """
        Checks whether value of the given currencies is defined (not None).
        
        :param currency: A currency from the Currency enumeration.
        :return: True if value of the given currency is defined, otherwise False.
        """
        return currency in self.__values

    def __add__(self, other):
        """
        These methods are called to implement the binary arithmetic operation +. Performs sum of two Money objects.
        To see examples please refer to test_money_operator_add routine (test_money.py)
        
        :param other: Summand represented by Money class.
        :return: A new Money object.
        """
        copy = self.copy()
        for c, v in other.iteritems():
            if c in copy:
                copy.__values[c] += other.get(c)
            copy.__values[c] = other.get(c)

        return copy

    def __iadd__(self, other):
        """
        These methods are called to implement the augmented arithmetic assignment +=. Performs sum of two Money
        objects.
        To see examples please refer to test_money_operator_add routine (test_money.py)
        
        :param other: Summand represented by Money class.
        :return: A new Money object.
        """
        return self.__add__(other)

    def __sub__(self, other):
        """
        These methods are called to implement the binary arithmetic operation -.
        To see examples please refer to test_money_operator_sub routine (test_money.py)
        
        :param other: Deduction represented by Money class.
        :return: A new Money object.
        """
        copy = self.copy()
        for c, v in other.iteritems():
            if c in copy:
                copy.__values[c] -= other.get(c)
            copy.__values[c] = -other.get(c)

        return copy

    def __isub__(self, other):
        """
        These methods are called to implement the augmented arithmetic assignment -=.
        To see examples please refer to test_money_operator_sub routine (test_money.py)
        
        :param other: Deduction represented by Money class.
        :return: A new Money object.
        """
        return self.__sub__(other)

    def __mul__(self, n):
        """
        These methods are called to implement the binary arithmetic operation *.
        To see examples please refer to test_money_operator_mul routine (test_money.py)
        
        :param n: Multiplier represented by a number (not a Money).
        :return: A new Money object.
        """
        return self.__convert(lambda c, v, o: v * o, n)

    def __rmul__(self, n):
        """
        These methods are called to implement the binary arithmetic operation * with reflected
        (swapped) operands. These functions are only called if the left operand does not support
        the corresponding operation and the operands are of different types.
        To see examples please refer to test_money_operator_mul routine (test_money.py)
        
        :param n: Multiplier represented by a number (not a Money).
        :return: A new Money object.
        """
        return self.__mul__(n)

    def __div__(self, n):
        """
        These methods are called to implement the binary arithmetic operation /.
        To see examples please refer to test_money_operator_div routine (test_money.py)
        
        :param n: Denominator represented by a number (not a Money).
        :return: A new Money object.
        """
        return self.__convert(lambda c, v, o: float(v) / o, n)

    def __rdiv__(self, n):
        """
        These methods are called to implement the binary arithmetic operation / with reflected
        (swapped) operands. These functions are only called if the left operand does not support
        the corresponding operation and the operands are of different types.
        To see examples please refer to test_money_operator_div routine (test_money.py)
        
        :param n: Denominator represented by a number (not a Money).
        :return: A new Money object.
        """
        return self.__div__(n)

    def __lt__(self, other):
        """
        These methods are called to implement the comparison operation <.
        To see examples please refer to test_money_comparison_operators routine (test_money.py)
        
        :param other: An instance of Money class
        :return: True if values of ALL DEFINED currencies are less than the appropriate values of the given
        money, otherwise False.
        """
        for c, v in self.iteritems():
            if c not in other or v >= other.get(c):
                return False

        return other.isDefined()

    def __le__(self, other):
        """
        These methods are called to implement the comparison operation <=.
        To see examples please refer to test_money_comparison_operators routine (test_money.py)
        
        :param other: An instance of Money class
        :return: True if values of ALL DEFINED currencies are less or equal to the appropriate values of
        the given money, otherwise False.
        """
        for c, v in self.iteritems():
            if c not in other or v > other.get(c):
                return False

        return True

    def __gt__(self, other):
        """
        These methods are called to implement the comparison operation >.
        To see examples please refer to test_money_comparison_operators routine (test_money.py)
        
        :param other: An instance of Money class
        :return: True if values of ALL DEFINED currencies are more than the appropriate values of the given
        money, otherwise False.
        """
        for c, v in self.iteritems():
            if v <= other.get(c):
                return False

        return self.isDefined()

    def __ge__(self, other):
        """
        These methods are called to implement the comparison operation >=.
        To see examples please refer to test_money_comparison_operators routine (test_money.py)
        
        :param other: An instance of Money class
        :return: True if values of ALL DEFINED currencies are more or equal to the appropriate values of
        the given money, otherwise False.
        """
        if other.isDefined():
            if self.isDefined():
                for c, v in self.iteritems():
                    if v < other.get(c):
                        return False

                return True
            else:
                return False
        else:
            return True

    def __eq__(self, other):
        """
        These methods are called to implement the comparison operation ==.
        To see examples please refer to test_money_comparison_operators routine (test_money.py)
        
        :param other: An instance of Money class
        :return: True if values of ALL currencies (including undefined values!) are equal to the appropriate values of
        the given money, otherwise False.
        """
        for c in Currency.ALL:
            if self.get(c) != other.get(c):
                return False

        return True

    def __ne__(self, other):
        """
        These methods are called to implement the comparison operation !=.
        To see examples please refer to test_money_comparison_operators routine (test_money.py)
        
        :param other: An instance of Money class
        :return: True if at least one value is not equal to the appropriate value of the given
        money, otherwise False.
        """
        for c in Currency.ALL:
            if self.get(c) != other.get(c):
                return True

        return False

    def __nonzero__(self):
        """
        Returns True if there is at least one set currency (!=0); otherwise returns False. Called to implement
        truth value testing and the built-in operation bool().
        
        :return: False if values of all currencies is set to 0 (Zero object), otherwise True.
        """
        for v in self:
            if v != 0:
                return True

        return False

    def __len__(self):
        """
        Returns number of defined currencies (be aware that some of them (or all) might be set to 0). Called to
        implement the built-in function len().
        :return: int >= 0, number of defined currencies.
        """
        return len(self.__values)

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
        kwargs = {c:function(c, v, other) for c, v in self.__values.iteritems()}
        return Money(**kwargs)

    def __getCurrenciesIterator(self, byWeight=True):
        order = Currency.BY_WEIGHT if byWeight else Currency.ALL
        for c in order:
            if c in self.__values:
                yield c

    @classmethod
    def __initValue(cls, values, currency, value):
        if value is not None:
            values[currency] = value
        return

    @classmethod
    def __setValue(cls, values, currency, value):
        if value is None:
            if currency in values:
                del values[currency]
        else:
            values[currency] = value
        return


MONEY_UNDEFINED = Money()
MONEY_ZERO_CREDITS = Money(credits=0)
MONEY_ZERO_GOLD = Money(gold=0)
MONEY_ZERO_CRYSTAL = Money(crystal=0)

class MoneySet(tuple):
    """
    Represents container of moneys. Corresponds to Money 2.0 concept - implements the OR condition.
    """

    def __new__(cls, *moneys):
        return super(MoneySet, cls).__new__(cls, moneys)

    def toDictsList(self):
        """
        Returns money set in [{}, {}, ... ,{}] format.
        """
        return [ money.toSignDict() for money in self ]

    def getSum(self):
        """
        Sum all moneys.
        :return: Money
        """
        money = MONEY_UNDEFINED
        for m in self:
            money += m

        return money

    def toMoneyTuple(self):
        """
        Returns tuple containing all currencies (old format). If any currency value is not defined (None), 0 is placed
        into the tuple. Order corresponds to Currency.ALL (default order).
        
        NOTE: this method should not be used because it violates Money 2.0 concept and it is implemented only
        to support legacy code (old Python-AS money protocol). Instead of it use toDictsList.
        """
        return self.getSum().toMoneyTuple()

    @classmethod
    def makeFromMoneyTuple(cls, moneyTuple):
        """
        Makes instance of MoneySet class based on the given money tuple (Money 1.0).
        Be aware that each item of the given money tuple is treated as separate Money: money set will contain all
        set items in tuple as separate Money instances.
        Also note that all Moneys are sorted by the default order (see Currency.ALL) inside MoneySet.
        
        NOTE: the method should not be used because it violates Money 2.0 concept and it is implemented only
        to support legacy code (old Client-Server money protocol).
        
        :param moneyTuple: tuple, where undefined or unset values = 0 (in old terms undefined=unset=0).
        :return: A new instance of MoneySet class.
        """
        assert isinstance(moneyTuple, (tuple, list))
        return MoneySet([ Money.makeFrom(Currency.ALL[index], v) for index, v in enumerate(moneyTuple) if v != 0 ])


_CurrencyCollection = namedtuple('CurrencyCollection', Currency.ALL)
_CurrencyCollection.__new__.__defaults__ = len(Currency.ALL) * (None,)

class CurrencyCollection(_CurrencyCollection):
    """
    Represents a collection of values associated with currencies (Money-like collection). All currencies by default
    are set to None.
    
    NOTE: All instances of CurrencyCollection are immutable!
    """

    def get(self, currency):
        """
        Gets a value associated with the given currency.
        
        :param currency: A currency from the Currency enumeration.
        :return: A currency value.
        """
        return getattr(self, currency)

    def replace(self, currency, value):
        """
        Creates a copy of money object and replaces value of the given currency. Values of all
        other currencies are copied without any changes.
        
        :param currency: A currency from the Currency enumeration.
        :param value: A new value for the given currency.
        :return: A copy of original CurrencyCollection object with the given value for the given currency.
        """
        return self.replaceAll({currency: value})

    def replaceAll(self, values):
        """
        Creates a copy of money object and replaces values of the given currencies. Values of all
        other currencies are copied without any changes.
        
        :param values: Values that replace current values. Represented by dict, where keys correspond to
                       Currency strings.
        :return: A copy of original CurrencyCollection object with updated values.
        """
        return self._replace(**values)

    def copy(self):
        """
        Creates a deep copy of CurrencyCollection.
        
        :return: A deep copy of original CurrencyCollection object.
        """
        return CurrencyCollection(*self)

    def iteritems(self):
        """
        Returns an iterator that allows to iterate CurrencyCollection by currency and value simultaneously.
        
        :return: Returns an iterator over the CurrencyCollection (currency, value) pairs.
        """
        for c in Currency.ALL:
            yield (c, self.get(c))

    def toDict(self):
        """
        Converts CurrencyCollection to a dictionary. Keys correspond to Currency strings.
        """
        return {c:v for c, v in self.iteritems()}

    def __iter__(self):
        """
        Returns an iterator object. The object is required to support the iterator protocol.
        Iterable values are represented by currency's value in order determined by Currency
        enumeration.
        """
        for c in Currency.ALL:
            yield self.get(c)
