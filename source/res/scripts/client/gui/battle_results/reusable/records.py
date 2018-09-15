# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/reusable/records.py
import operator
from ValueReplay import ValueReplay
from debug_utils import LOG_ERROR

class ResultRecord(object):
    """Basic wrapper to store numeric record(s) form the battle statics."""
    __slots__ = ()

    def getRecord(self, *args):
        """Get record or sum of records by specified name(s)."""
        pass

    def findRecord(self, criteria):
        """Find record that stats with specified string.
        :param criteria: name of record must be started by specified string.
        """
        return self.getRecord(criteria)

    def getFactor(self, *args):
        """Gets value of factor if it has or 1.0."""
        pass


class RawRecords(ResultRecord):
    """Wrapper to store numeric records form the battle statics directly."""
    __slots__ = ('_records',)

    def __init__(self, records):
        super(RawRecords, self).__init__()
        self._records = records

    def getRecord(self, *names):
        """Gets sum of records by specified names of records.
        :param names: sequence containing names of records.
        :return: integer containing the sum of values.
        """
        result = 0
        for name in names:
            if name in self._records:
                result += self._records[name]

        return result


def makeReplayValueRound(value):
    """Rounds and converts float value of replay record to int."""
    return int(round(value))


class ReplayRecord(ResultRecord):
    """Basic wrapper to store replay record from some battle replay."""
    __slots__ = ('_name', '_value', '_diff')

    def __init__(self, name, value, diff):
        """Initialization.
        :param name: name of record in the replay
        :param value: actual value of record in the replay.
        :param diff: the difference between the current value of record and
            the previous value of other record in the replay playing process.
        """
        super(ReplayRecord, self).__init__()
        self._name = name
        self._value = value
        self._diff = diff

    def getName(self):
        """Gets name of replay record.
        :return: string containing name of record.
        """
        return self._name

    def getRecord(self):
        """Gets value of replay record.
        :return:
        """
        return self._value

    def _getFactor(self):
        name = self._name.lower()
        if name.endswith('factor100') or name.endswith('factors100'):
            return 100
        return 10 if name.endswith('factor10') or name.endswith('factors10') else 1


class SubReplayRecord(ReplayRecord):
    """Wrapper to store replay record of subtraction operation from some battle replay."""
    __slots__ = ()

    def getRecord(self):
        return -self._value


class FactorReplayRecord(ReplayRecord):
    """Wrapper to store replay record of operation to apply some factor from some battle replay
    and provides value of factor."""
    __slots__ = ()

    def getRecord(self):
        """Gets difference equals (a * k) - a
        :return: integer containing difference.
        """
        return self._diff

    def getFactor(self):
        """Gets value of factor that is calculated like value / factorX,
            where is factorX is got from name of record.
        :return: float containing value of factor.
        """
        return float(self._value) / self._getFactor()


class CoefficientReplayRecord(ReplayRecord):
    """Wrapper to store replay record of operation to apply some coefficient from some battle replay.
    Note: it does provide factor, value of factor always equals 1.0."""
    __slots__ = ()

    def getRecord(self):
        return self._diff


_SUPPORTED_OPS = {ValueReplay.SET: ReplayRecord,
 ValueReplay.ADD: ReplayRecord,
 ValueReplay.SUB: SubReplayRecord,
 ValueReplay.MUL: FactorReplayRecord,
 ValueReplay.FACTOR: FactorReplayRecord,
 ValueReplay.ADDCOEFF: CoefficientReplayRecord,
 ValueReplay.SUBCOEFF: CoefficientReplayRecord}

class ReplayRecords(ResultRecord):
    """Class to play specified replay and store records to internal storage."""
    __slots__ = ('_records',)

    def __init__(self, replay, *last):
        """Initialization.
        :param replay: instance of ValueReplay.
        :param last: tuple containing name of records that are not included to replay, but should be
            added to internal storage.
        """
        super(ReplayRecords, self).__init__()
        self._records = {}
        currentValue = 0
        for op, (appliedName, appliedValue), (_, finalValue) in replay:
            if not isinstance(finalValue, (int, float, long)):
                LOG_ERROR('There is invalid record in the replay', op, appliedName, appliedValue, _, finalValue, replay)
                return
            self._addRecord(op, appliedName, appliedValue, finalValue - currentValue)
            currentValue = finalValue

        for name in last:
            self._addRecord(ValueReplay.SET, name, replay[name], 0)

    def getRecord(self, *names):
        """Get sum of records values by specified names.
        :param names: sequence containing names of records.
        :return: integer containing the sum of values.
        """
        result = 0
        for name in names:
            result += self._getRecord(name)

        return result

    def findRecord(self, criteria):
        """Get sum of records that stats with specified string.
        :param criteria: name of record must be started by specified string.
        """
        result = 0
        for name, record in self._records.iteritems():
            if name.startswith(criteria):
                result += self._getRecord(name)

        return result

    def getFactor(self, name):
        """Gets value of factor if it has or 1.0.
        :param name: string containing name of records.
        :return: float containing value of factor.
        """
        if name in self._records:
            result = self._records[name].getFactor()
        else:
            result = 1.0
        return result

    def _getRecord(self, name):
        return self._records[name].getRecord() if name in self._records else 0

    def _addRecord(self, op, name, value, diff):
        if op in _SUPPORTED_OPS:
            clazz = _SUPPORTED_OPS[op]
            assert clazz is not None
            self._records[name] = clazz(name, value, diff)
        return


class RecordsIterator(ResultRecord):
    """Class to iterate records where is first item is this class.
    That class returns sum of values from all records."""
    __slots__ = ('_seq', '_indexes')

    def __init__(self, seq=None):
        super(RecordsIterator, self).__init__()
        self._seq = seq or []
        self._rebuild()

    def __iter__(self):
        self._rebuild()
        return self

    def next(self):
        while self._indexes:
            idx = self._indexes.pop(0)
            if not idx:
                return self
            return self._seq[idx - 1]

        raise StopIteration()

    def addRecords(self, record):
        """Adds records to iterator.
        :param record: instance of class extends ResultRecord.
        """
        self._seq.append(record)
        self._rebuild()

    def getRecord(self, *names):
        """Get sum of values from all records by specified names.
        :param names: sequence containing names of records.
        :return: integer containing the sum of values.
        """
        return self._sum('getRecord', *names)

    def findRecord(self, criteria):
        """Get sum of records that stats with specified string.
        :param criteria: name of record must be started by specified string.
        """
        return self._sum('findRecord', criteria)

    def getFactor(self, name):
        """Gets max value of factor from all records by specified name.
        :param name: string containing name of records.
        :return: float containing value of factor.
        """
        getter = operator.methodcaller('getFactor', name)
        return max((getter(item) for item in self._seq)) if self._seq else 1

    def _rebuild(self):
        self._indexes = range(len(self._seq) + 1)

    def _sum(self, method, *names):
        getter = operator.methodcaller(method, *names)
        return sum((getter(item) for item in self._seq))
