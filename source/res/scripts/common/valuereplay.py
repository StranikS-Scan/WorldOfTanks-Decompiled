# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/ValueReplay.py
import struct

class BattleResults(dict):
    pass


class ValueReplayConnector(object):
    __slots__ = ('_battleResultsStruct', '_battleResults')

    def __init__(self, battleResultsStruct, battleResults):
        assert len(battleResultsStruct) <= 1048575
        self._battleResultsStruct = battleResultsStruct
        self._battleResults = battleResults

    @staticmethod
    def makeIndex(idx1, idx2):
        return ((idx1 & 1048575) << 8) + (idx2 & 255)

    @staticmethod
    def parseIndex(idx):
        return (idx >> 8 & 1048575, idx & 255)

    def __contains__(self, item):
        subitems = self.__parseItem(item)
        cont = self._battleResults
        length = len(subitems)
        if length == 2:
            f, s = subitems
            if f not in cont:
                return False
            return len(self.__getSecondValueByName(cont[f], s)) > 0
        return subitems[0] in cont

    def __getitem__(self, item):
        subitems = self.__parseItem(item)
        length = len(subitems)
        cont = self._battleResults
        if length == 2:
            f, s = subitems
            if f not in cont:
                raise KeyError(item)
            return self.__getSecondValueByName(cont[f], s)[0][1][1]
        return cont[subitems[0]]

    def __setitem__(self, item, value):
        subitems = self.__parseItem(item)
        length = len(subitems)
        cont = self._battleResults
        if length == 2:
            f, s = subitems
            if f not in cont:
                raise KeyError(item)
            idx = self.__getSecondValueByName(cont[f], s)[0][0]
            cont[f][idx] = (s, value)
            return
        cont[subitems[0]] = value

    def index(self, item):
        subitems = self.__parseItem(item)
        length = len(subitems)
        if length == 2:
            f, s = subitems
            idx1 = self._battleResultsStruct.indexOf(f)
            idx2 = self.__getSecondValueByName(self._battleResults[f], s)[0][0] + 1
            return ValueReplayConnector.makeIndex(idx1, idx2)
        return ValueReplayConnector.makeIndex(self._battleResultsStruct.indexOf(subitems[0]), 0)

    def name(self, idx):
        idx1, idx2 = ValueReplayConnector.parseIndex(idx)
        subname1 = self._battleResultsStruct[idx1].name
        if idx2 > 0:
            idx2 -= 1
            subname2 = self.__getSecondValueByIndex(self._battleResults[subname1], idx2)[0][1][0]
            return '_'.join([subname1, subname2])
        return subname1

    def __parseItem(self, item):
        pos = item.find('_')
        if pos == -1:
            subitems = [item]
        else:
            subitems = [item[:pos], item[pos + 1:]]
        return subitems

    def __getSecondValueByName(self, cont, name):
        return [ (i, v) for i, v in enumerate(cont) if v[0] == name ]

    def __getSecondValueByIndex(self, cont, idx):
        return [ (i, v) for i, v in enumerate(cont) if i == idx ]


class ValueReplay:
    SET = 0
    ADD = 1
    SUB = 2
    MUL = 3
    DIV = 4
    TAG = 5
    FACTOR = 6
    LAST = 15

    def __init__(self, connector, recordName, startRecordName=None, replay=None):
        assert (startRecordName is None) ^ (replay is None)
        assert recordName in connector
        assert connector is not None
        self.__connector = connector
        self.__recordName = recordName
        self.__overiddenValues = {}
        self.__packed = replay
        self.__replay = [] if replay is None else self.unpack()
        self.__appliedValues = set([ self.parseStepCompDescr(step)[1] for step in self.__replay ] if self.__replay else [])
        self.__tags = {}
        if startRecordName is None:
            return
        else:
            self.__setInitial(startRecordName)
            return

    @staticmethod
    def makeStepCompDescr(op, idx):
        return (idx << 4) + (op & 15)

    @staticmethod
    def parseStepCompDescr(packedStep):
        return (packedStep & 15, packedStep >> 4)

    def pack(self):
        size = len(self.__replay)
        self.__packed = struct.pack(('<H%sI' % size), size, *self.__replay)
        return self.__packed

    def unpack(self):
        size = ord(self.__packed[0])
        return struct.unpack('<%sI' % size, self.__packed[2:])

    def __setitem__(self, key, value):
        if self.__connector.index(key) not in self.__appliedValues or key == self.__recordName or key in self.__tags:
            raise Exception('Cannot overload item %s:%s' % (key, value))
        self.__overiddenValues[key] = value

    def __getitem__(self, item):
        if item == self.__recordName:
            finalResult = 0
            for op, (_, _), (_, finalResult) in self:
                pass

            return finalResult
        if item in self.__overiddenValues:
            return self.__overiddenValues[item]
        if item in self.__tags:
            return self.__tags[item]
        raise KeyError

    def __delitem__(self, key):
        if self.__connector.index(key) not in self.__appliedValues or key == self.__recordName or key in self.__tags:
            raise Exception('Unexpected arg %s' % (key,))
        del self.__overiddenValues[key]

    def __add__(self, other):
        idx = self.__validate(other)
        self.__appliedValues.add(idx)
        self.__connector[self.__recordName] = self.__OPERATORS[self.ADD](self, other)
        self.__replay.append(ValueReplay.makeStepCompDescr(self.ADD, idx))
        return self

    def __sub__(self, other):
        idx = self.__validate(other)
        self.__appliedValues.add(idx)
        self.__connector[self.__recordName] = self.__OPERATORS[self.SUB](self, other)
        self.__replay.append(ValueReplay.makeStepCompDescr(self.SUB, idx))
        return self

    def __mul__(self, other):
        idx = self.__validate(other)
        self.__appliedValues.add(idx)
        self.__connector[self.__recordName] = self.__OPERATORS[self.MUL](self, other)
        self.__replay.append(ValueReplay.makeStepCompDescr(self.MUL, idx))
        return self

    def tag(self, other):
        idx = self.__validate(other)
        if self.__tags:
            raise Exception('Just one tag is allowed %s, %s' % (other, self.__tags))
        self.__appliedValues.add(idx)
        self.__connector[other] = self.__tags[other] = self.__OPERATORS[self.TAG](self, other)
        self.__replay.append(ValueReplay.makeStepCompDescr(self.TAG, idx))
        return self

    def applyFactorToTag(self, other):
        idx = self.__validate(other)
        if not self.__tags:
            raise Exception('There is no any tagged values %s' % (other,))
        self.__appliedValues.add(idx)
        self.__connector[self.__recordName] = self.__OPERATORS[self.FACTOR](self, other)
        self.__replay.append(ValueReplay.makeStepCompDescr(self.FACTOR, idx))
        return self

    def __eq__(self, other):
        return False if not isinstance(other, ValueReplay) else self.__replay == other.__replay

    def __iter__(self):
        if not self.__replay:
            raise Exception('Invalid usage of __iter__')
        finalResult = 0
        tags = self.__tags
        connector = self.__connector
        OPERATORS = self.__OPERATORS
        recordName = self.__recordName
        overiddenValues = self.__overiddenValues
        for replay in self.__replay:
            op, idx = ValueReplay.parseStepCompDescr(replay)
            other = connector.name(idx)
            if op == self.TAG:
                tags[other] = OPERATORS[op](self, other, finalResult)
            else:
                finalResult = OPERATORS[op](self, other, finalResult)
            value = overiddenValues.get(other, connector[other])
            yield (op, (other, value), (recordName, finalResult))

    def __validate(self, other, initial=False):
        if other == self.__recordName:
            raise Exception('Invalid usage %s. Cannot apply wrapped value to itself.' % (other,))
        if not initial and not self.__appliedValues:
            raise Exception('Invalid usage %s. Call __setInitial before.' % (other,))
        idx = self.__connector.index(other)
        if idx in self.__appliedValues:
            raise Exception('Unexpected arg %s. Argument has been already applied.' % (other,))
        return idx

    def __setInitial(self, other):
        idx = self.__validate(other, initial=True)
        if self.__appliedValues or self.__replay:
            raise Exception('Invalid usage %s' % (other,))
        self.__appliedValues.add(idx)
        self.__connector[self.__recordName] = self.__OPERATORS[self.SET](self, other)
        self.__replay.append(ValueReplay.makeStepCompDescr(self.SET, idx))

    def __getFactorValue(self, other):
        other = other.lower()
        if 'factor100' in other or 'factors100' in other:
            return 100.0
        elif 'factor10' in other or 'factors10' in other:
            return 10.0
        else:
            return None
            return None

    def __opMul(self, other, x=None):
        if x is None:
            x = self.__connector[self.__recordName]
        value = self.__overiddenValues.get(other, self.__connector[other])
        factor = self.__getFactorValue(other)
        if factor is not None:
            value /= factor
        return int(round(x * value))

    def __opSub(self, other, x=None):
        if x is None:
            x = self.__connector[self.__recordName]
        return x - self.__overiddenValues.get(other, self.__connector[other])

    def __opAdd(self, other, x=None):
        if x is None:
            x = self.__connector[self.__recordName]
        return x + self.__overiddenValues.get(other, self.__connector[other])

    def __opSet(self, other, _=None):
        return self.__overiddenValues.get(other, self.__connector[other])

    def __opTag(self, _1, x=None):
        if x is None:
            x = self.__connector[self.__recordName]
        return x

    def __opFactor(self, other, x=None):
        if x is None:
            x = self.__connector[self.__recordName]
        value = self.__overiddenValues.get(other, self.__connector[other])
        factor = self.__getFactorValue(other)
        if factor is not None:
            value /= factor
        return x + int(round(value * next(self.__tags.itervalues())))

    __OPERATORS = {ADD: __opAdd,
     SUB: __opSub,
     MUL: __opMul,
     SET: __opSet,
     TAG: __opTag,
     FACTOR: __opFactor}
