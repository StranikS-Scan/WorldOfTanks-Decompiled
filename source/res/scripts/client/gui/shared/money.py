# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/money.py
from collections import namedtuple
from typing import TYPE_CHECKING
from shared_utils import CONST_CONTAINER
from soft_exception import SoftException
if TYPE_CHECKING:
    from typing import Optional, Any, Union, Dict, Tuple, Iterable, Literal, Callable, List
    CURRENCY_TYPE = Literal['credits', 'gold', 'crystal', 'eventCoin', 'bpcoin']
    CURRENCIES_TYPE = Tuple[int, int, int, int, int]
    CURRENCIES_NAMES_TYPE = Tuple[CURRENCY_TYPE, CURRENCY_TYPE, CURRENCY_TYPE, CURRENCY_TYPE, CURRENCY_TYPE]
    OPTIONAL_NUMBER_TYPE = Optional[float]

class Currency(CONST_CONTAINER):
    CREDITS = 'credits'
    GOLD = 'gold'
    CRYSTAL = 'crystal'
    EVENT_COIN = 'eventCoin'
    BPCOIN = 'bpcoin'
    BRCOIN = 'brcoin'
    FREE_XP = 'freeXP'
    EQUIP_COIN = 'equipCoin'
    ALL = (CREDITS,
     GOLD,
     CRYSTAL,
     EVENT_COIN,
     BPCOIN,
     EQUIP_COIN)
    BY_WEIGHT = (GOLD,
     CRYSTAL,
     CREDITS,
     EVENT_COIN,
     BPCOIN,
     EQUIP_COIN)
    GUI_ALL = (CRYSTAL, GOLD, CREDITS)
    _CURRENCY_EXTERNAL_MAP = {CREDITS: 'credits',
     GOLD: 'gold',
     CRYSTAL: 'crystal',
     EVENT_COIN: 'event_coin',
     BPCOIN: 'bpcoin',
     EQUIP_COIN: 'equipCoin'}
    _CURRENCY_INTERNAL_MAP = {external:internal for internal, external in _CURRENCY_EXTERNAL_MAP.iteritems()}

    @classmethod
    def currencyExternalName(cls, currencyName):
        return cls._CURRENCY_EXTERNAL_MAP[currencyName]

    @classmethod
    def currencyInternalName(cls, currencyName):
        return cls._CURRENCY_INTERNAL_MAP[currencyName]

    @classmethod
    def convertExternal(cls, **kwargs):
        return {Currency.currencyInternalName(currency):value for currency, value in kwargs.iteritems()}


__Money = namedtuple('_Money', Currency.ALL)
__Money.__new__.__defaults__ = len(Currency.ALL) * (0,)

class _Money(__Money):

    def get(self, currency):
        return getattr(self, currency)


_CREDITS = Currency.CREDITS
_GOLD = Currency.GOLD
_CRYSTAL = Currency.CRYSTAL
_EVENT_COIN = Currency.EVENT_COIN
_BPCOIN = Currency.BPCOIN
_EQUIP_COIN = Currency.EQUIP_COIN

class Money(object):
    __slots__ = ('_values',)
    ALL = Currency.ALL
    UNDEFINED = None
    WEIGHT = Currency.BY_WEIGHT

    def __init__(self, credits=None, gold=None, crystal=None, eventCoin=None, bpcoin=None, equipCoin=None, *args, **kwargs):
        super(Money, self).__init__()
        values = self._values = {}
        if credits is not None:
            values[_CREDITS] = credits
        if gold is not None:
            values[_GOLD] = gold
        if crystal is not None:
            values[_CRYSTAL] = crystal
        if eventCoin is not None:
            values[_EVENT_COIN] = eventCoin
        if bpcoin is not None:
            values[_BPCOIN] = bpcoin
        if equipCoin is not None:
            values[_EQUIP_COIN] = equipCoin
        return

    def __getitem__(self, index):
        return self.get(self.ALL[index], 0)

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, ', '.join([ '{}'.format(self.get(c)) for c in self.ALL ]))

    def __iter__(self):
        for c in self.__getCurrenciesIterator(byWeight=False):
            yield self._values[c]

    def __contains__(self, currency):
        return currency in self._values

    def __add__(self, other):
        copy = self.copy()
        for c, _ in other.iteritems():
            if c in copy:
                copy._values[c] += other.get(c)
            copy._values[c] = other.get(c)

        return copy

    def __iadd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        copy = self.copy()
        for c, _ in other.iteritems():
            if c in copy:
                copy._values[c] -= other.get(c)
            copy._values[c] = -other.get(c)

        return copy

    def __isub__(self, other):
        return self.__sub__(other)

    def __mul__(self, n):
        return self.__convert(lambda c, v, o: v * o, n)

    def __rmul__(self, n):
        return self.__mul__(n)

    def __div__(self, n):
        return self.__convert(lambda c, v, o: float(v) / o, n)

    def __rdiv__(self, n):
        return self.__div__(n)

    def __lt__(self, other):
        for c, v in self.iteritems():
            if c not in other or v >= other.get(c):
                return False

        return other.isDefined()

    def __le__(self, other):
        for c, v in self.iteritems():
            if c not in other or v > other.get(c):
                return False

        return True

    def __gt__(self, other):
        for c, v in self.iteritems():
            if v <= other.get(c):
                return False

        return self.isDefined()

    def __ge__(self, other):
        if other.isDefined():
            if self.isDefined():
                for c, v in self.iteritems():
                    if v < other.get(c):
                        return False

                return True
            return False
        return True

    def __eq__(self, other):
        for c in self.ALL:
            if self.get(c) != other.get(c):
                return False

        return True

    def __ne__(self, other):
        for c in self.ALL:
            if self.get(c) != other.get(c):
                return True

        return False

    def __nonzero__(self):
        for v in self:
            if v != 0:
                return True

        return False

    def __len__(self):
        return len(self._values)

    @property
    def credits(self):
        try:
            return self._values[_CREDITS]
        except KeyError:
            return None

        return None

    @property
    def gold(self):
        try:
            return self._values[_GOLD]
        except KeyError:
            return None

        return None

    @property
    def crystal(self):
        try:
            return self._values[_CRYSTAL]
        except KeyError:
            return None

        return None

    @property
    def eventCoin(self):
        try:
            return self._values[_EVENT_COIN]
        except KeyError:
            return None

        return None

    @property
    def bpcoin(self):
        try:
            return self._values[_BPCOIN]
        except KeyError:
            return None

        return None

    @property
    def equipCoin(self):
        try:
            return self._values[_EQUIP_COIN]
        except KeyError:
            return None

        return None

    @classmethod
    def makeFrom(cls, currency, value):
        return cls.UNDEFINED.replace(currency, value)

    @classmethod
    def hasMoney(cls, data):
        return any((c in cls.ALL for c in data.iterkeys()))

    @classmethod
    def extractMoneyDict(cls, data):
        return {c:data[c] for c in cls.ALL if c in data}

    @classmethod
    def makeMoney(cls, data):
        if isinstance(data, cls):
            return data
        elif isinstance(data, (tuple, list)):
            return cls.makeFromMoneyTuple(data)
        else:
            return cls(**data) if isinstance(data, dict) else None

    @classmethod
    def makeFromMoneyTuple(cls, moneyTuple):
        setValues = {cls.ALL[index]:v for index, v in enumerate(moneyTuple) if v != 0}
        return cls(**setValues)

    def get(self, currency, default=None):
        return self._values[currency] if currency in self._values else default

    @property
    def currencies(self):
        return self.ALL

    def replace(self, currency, value):
        copy = self._values.copy()
        self._setValue(copy, currency, value)
        return self._copy(**copy)

    def replaceAll(self, values):
        copy = self._values.copy()
        for currency, value in values.iteritems():
            self._setValue(copy, currency, value)

        return self._copy(**copy)

    def copy(self):
        return self._copy(**self._values)

    def exchange(self, currency, toCurrency, rate, default=None):
        if currency == toCurrency:
            raise SoftException('Currencies are same: {}'.format(toCurrency))
        if currency not in self._values:
            raise SoftException('Current is not found: {}'.format(currency))
        value = self.get(toCurrency, 0) + self.get(currency) * rate
        copy = self._values.copy()
        self._setValue(copy, currency, default)
        self._setValue(copy, toCurrency, value)
        return self._copy(**copy)

    def isDefined(self):
        return bool(self._values)

    def isCurrencyDefined(self, currency):
        return currency in self._values

    def isSet(self, currency):
        return currency in self and self.get(currency) != 0

    def isCompound(self):
        return len(self._values) > 1

    def getSetCurrencies(self, byWeight=True):
        return [ c for c in self.__getCurrenciesIterator(byWeight) if self._values[c] != 0 ]

    def getCurrency(self, byWeight=True):
        currency = None
        if self._values:
            for c in self.__getCurrenciesIterator(byWeight):
                if self._values[c] != 0:
                    return c
                if currency is None:
                    currency = c

        return currency or _CREDITS

    def toNonNegative(self):
        return self.apply(lambda v: max(0, v))

    def toAbs(self):
        return self.apply(abs)

    def toDict(self):
        return {c:v for c, v in self._values.iteritems()}

    def toSignDict(self):
        return {c:v for c, v in self._values.iteritems() if v != 0}

    def toDictsList(self):
        return [self.toSignDict()]

    def iteritems(self, byWeight=False):
        for c in self.__getCurrenciesIterator(byWeight=byWeight):
            yield (c, self._values.get(c))

    def apply(self, formatter):
        return self.__convert(lambda c, v, o: formatter(v), None)

    def getShortage(self, price):
        shortage = self.UNDEFINED
        for c in price.__getCurrenciesIterator(byWeight=True):
            delta = price.get(c) - self.get(c, 0)
            if delta > 0:
                shortage = shortage.replace(c, delta)

        return shortage

    def getNegative(self):
        return [ (c, v) for c, v in self.iteritems() if v < 0 ]

    def getPositive(self):
        return [ (c, v) for c, v in self.iteritems() if v > 0 ]

    def toMoneyTuple(self):
        return _Money(**self._values)

    def getSignValue(self, currency):
        return self.get(currency, 0)

    def iterallitems(self, byWeight=False):
        order = self.WEIGHT if byWeight else self.ALL
        for c in order:
            yield (c, self._values.get(c, 0))

    @classmethod
    def _setValue(cls, values, currency, value):
        if value is None:
            if currency in values:
                del values[currency]
        else:
            values[currency] = value
        return

    @classmethod
    def _copy(cls, **values):
        return cls(**values)

    def __convert(self, function, other):
        kwargs = {c:function(c, v, other) for c, v in self._values.iteritems()}
        return self._copy(**kwargs)

    def __getCurrenciesIterator(self, byWeight=True):
        order = self.WEIGHT if byWeight else self.ALL
        for c in order:
            if c in self._values:
                yield c


Money.UNDEFINED = MONEY_UNDEFINED = Money()
MONEY_ZERO_CREDITS = Money(credits=0)
MONEY_ZERO_GOLD = Money(gold=0)
MONEY_ZERO_CRYSTAL = Money(crystal=0)
MONEY_ZERO_EVENT_COIN = Money(eventCoin=0)
MONEY_ZERO_BPCOIN = Money(bpcoin=0)
ZERO_MONEY = Money(**{c:0 for c in Currency.ALL})
_CurrencyCollection = namedtuple('CurrencyCollection', Currency.ALL)
_CurrencyCollection.__new__.__defaults__ = len(Currency.ALL) * (None,)

class DynamicMoney(Money):

    def __init__(self, *args, **kwargs):
        super(DynamicMoney, self).__init__(*args, **kwargs)
        if kwargs:
            extended = {key:value for key, value in kwargs.iteritems() if key not in self._values}
            self._values.update(extended)
            currencies = tuple(extended.keys())
            self.ALL = Currency.ALL + currencies
            self.WEIGHT = Currency.BY_WEIGHT + currencies

    def isCompound(self):
        return self.isCompound() and self.isDynCompound()

    def isDynCompound(self):
        consist = [ currency for currency in self._values if currency not in Currency.ALL and self.get(currency, 0) != 0 ]
        return len(consist) > 1

    def isSpecCompound(self, currencies):
        consist = [ currency for currency in currencies if self.isSet(currency) ]
        return len(consist) > 1

    def toMoneyTuple(self):
        raise SoftException('Conversion of ExtendedMoney to old style _Money is not supported')


DynamicMoney.UNDEFINED = DynamicMoney()
DYNAMIC_MONEY_ZERO_CREDITS = DynamicMoney(credits=0)
DYNAMIC_MONEY_ZERO_GOLD = DynamicMoney(gold=0)
DYNAMIC_MONEY_ZERO_CRYSTAL = DynamicMoney(crystal=0)
DYNAMIC_MONEY_ZERO_EVENT_COIN = DynamicMoney(eventCoin=0)
DYNAMIC_MONEY_ZERO_BPCOIN = DynamicMoney(bpcoin=0)

class CurrencyCollection(_CurrencyCollection):

    def get(self, currency):
        return getattr(self, currency)

    def replace(self, currency, value):
        return self.replaceAll({currency: value})

    def replaceAll(self, values):
        return self._replace(**values)

    def copy(self):
        return CurrencyCollection(*self)

    def iteritems(self):
        for c in Currency.ALL:
            yield (c, self.get(c))

    def toDict(self):
        return {c:v for c, v in self.iteritems()}

    def __iter__(self):
        for c in Currency.ALL:
            yield self.get(c)
