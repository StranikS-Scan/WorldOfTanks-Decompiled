# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/ValueReplay.py
from bit_coder import BitCoder
import struct

def makeFactor10(factor):
    return int(round(factor * 10))


def makeFactor100(factor):
    return int(round(factor * 100))


class BattleResults(dict):
    pass


class ValueReplayConnector(object):
    __slots__ = ('_battleResultsStruct', '_battleResults')
    _bitCoder = BitCoder(10, 8, 10)

    def __init__(self, battleResultsStruct, battleResults):
        self._battleResultsStruct = battleResultsStruct
        self._battleResults = battleResults

    @staticmethod
    def makeIndex(paramIndex, paramSubIndex, secondParamIndex):
        coder = ValueReplayConnector._bitCoder
        return coder.emplace(paramIndex, paramSubIndex, secondParamIndex)

    @staticmethod
    def parseIndex(idx):
        return ValueReplayConnector._bitCoder.extract(idx)

    def __contains__(self, item):
        subitems = self.__splitName(item)
        cont = self._battleResults
        length = len(subitems)
        if length == 2:
            f, s = subitems
            if f not in cont:
                return False
            return len(self.__getSecondValueByName(cont[f], s)) > 0
        return subitems[0] in cont

    def __getitem__(self, item):
        subitems = self.__splitName(item)
        length = len(subitems)
        cont = self._battleResults
        if length == 2:
            f, s = subitems
            if f not in cont:
                raise KeyError(item)
            return self.__getSecondValueByName(cont[f], s)[0][1][1]
        return cont[subitems[0]]

    def __setitem__(self, item, value):
        subitems = self.__splitName(item)
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

    def index(self, item, item2=None):
        subitems = self.__splitName(item)
        length = len(subitems)
        secondIndex = 0 if item2 is None else self._battleResultsStruct.indexOf(item2)
        if length == 2:
            f, s = subitems
            index = self._battleResultsStruct.indexOf(f)
            subIndex = self.__getSecondValueByName(self._battleResults[f], s)[0][0] + 1
            return ValueReplayConnector.makeIndex(index, subIndex, secondIndex)
        else:
            return ValueReplayConnector.makeIndex(self._battleResultsStruct.indexOf(subitems[0]), 0, secondIndex)

    def indexToNames(self, idx):
        index, subIndex, secondIndex = ValueReplayConnector.parseIndex(idx)
        subname1 = self._battleResultsStruct[index].name
        secondName = self._battleResultsStruct[secondIndex].name
        if subIndex > 0:
            subIndex -= 1
            subname2 = self.__getSecondValueByIndex(self._battleResults[subname1], subIndex)[0][1][0]
            return ('_'.join([subname1, subname2]), secondName)
        return (subname1, secondName)

    def __splitName(self, item):
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
    ADDCOEFF = 7
    SUBCOEFF = 8
    LAST = 15

    def __init__(self, connector, recordName, startRecordName=None, replay=None):
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
        size = struct.unpack('<H', self.__packed[:2])[0]
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
        self.__connector[self.__recordName] = self.__OPERATORS[self.ADD](self, other, None)
        self.__replay.append(ValueReplay.makeStepCompDescr(self.ADD, idx))
        return self

    def __sub__(self, other):
        idx = self.__validate(other)
        self.__appliedValues.add(idx)
        self.__connector[self.__recordName] = self.__OPERATORS[self.SUB](self, other, None)
        self.__replay.append(ValueReplay.makeStepCompDescr(self.SUB, idx))
        return self

    def __mul__(self, other):
        idx = self.__validate(other)
        self.__appliedValues.add(idx)
        self.__connector[self.__recordName] = self.__OPERATORS[self.MUL](self, other, None)
        self.__replay.append(ValueReplay.makeStepCompDescr(self.MUL, idx))
        return self

    def tag(self, other):
        idx = self.__validate(other)
        if self.__tags:
            raise Exception('Just one tag is allowed %s, %s' % (other, self.__tags))
        self.__appliedValues.add(idx)
        self.__connector[other] = self.__tags[other] = self.__OPERATORS[self.TAG](self, other, None)
        self.__replay.append(ValueReplay.makeStepCompDescr(self.TAG, idx))
        return self

    def applyFactorToTag(self, other):
        idx = self.__validate(other)
        if not self.__tags:
            raise Exception('There is no any tagged values %s' % (other,))
        self.__appliedValues.add(idx)
        self.__connector[self.__recordName] = self.__OPERATORS[self.FACTOR](self, other, None)
        self.__replay.append(ValueReplay.makeStepCompDescr(self.FACTOR, idx))
        return self

    def addMultipliedValue(self, other, coeff):
        idx = self.__validate(other, coeff)
        self.__appliedValues.add(idx)
        self.__connector[self.__recordName] = self.__OPERATORS[self.ADDCOEFF](self, other, coeff)
        self.__replay.append(ValueReplay.makeStepCompDescr(self.ADDCOEFF, idx))
        return self

    def subMultipliedValue(self, other, coeff):
        idx = self.__validate(other, coeff)
        self.__appliedValues.add(idx)
        self.__connector[self.__recordName] = self.__OPERATORS[self.SUBCOEFF](self, other, coeff)
        self.__replay.append(ValueReplay.makeStepCompDescr(self.SUBCOEFF, idx))
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
            param1, param2 = connector.indexToNames(idx)
            if op == self.TAG:
                tags[param1] = OPERATORS[op](self, param1, None, finalResult)
            else:
                finalResult = OPERATORS[op](self, param1, param2, finalResult)
            value = overiddenValues.get(param1, connector[param1])
            yield (op, (param1, value), (recordName, finalResult))

        return

    def __contains__(self, item):
        if not self.__replay:
            raise Exception('Invalid usage of __contains__')
        connector = self.__connector
        for replay in self.__replay:
            _, idx = ValueReplay.parseStepCompDescr(replay)
            param1, _ = connector.indexToNames(idx)
            if param1 == item:
                return True

        return False

    def __checkParam(self, param):
        if param == self.__recordName:
            raise Exception('Invalid usage %s. Cannot apply wrapped value to itself.' % (param,))

    def __validate(self, param1, param2=None, initial=False):
        self.__checkParam(param1)
        self.__checkParam(param2)
        if not initial and not self.__appliedValues:
            raise Exception('Invalid usage %s. Call __setInitial before.' % (param1,))
        idx = self.__connector.index(param1, param2)
        if idx in self.__appliedValues:
            raise Exception('Unexpected arg (%s,%s). Argument has been already applied.' % (param1, param2))
        return idx

    def __setInitial(self, other):
        idx = self.__validate(other, initial=True)
        if self.__appliedValues or self.__replay:
            raise Exception('Invalid usage %s' % (other,))
        self.__appliedValues.add(idx)
        self.__connector[self.__recordName] = self.__OPERATORS[self.SET](self, other, None)
        self.__replay.append(ValueReplay.makeStepCompDescr(self.SET, idx))
        return

    def __getFactorValue(self, other):
        other = other.lower()
        if 'factor100' in other or 'factors100' in other:
            return 100.0
        elif 'factor10' in other or 'factors10' in other:
            return 10.0
        else:
            return None
            return None

    def __opMul(self, other, _, x=None):
        if x is None:
            x = self.__connector[self.__recordName]
        value = self.__overiddenValues.get(other, self.__connector[other])
        factor = self.__getFactorValue(other)
        if factor is not None:
            value /= factor
        return int(round(x * value))

    def __opSub(self, other, _, x=None):
        if x is None:
            x = self.__connector[self.__recordName]
        return x - self.__overiddenValues.get(other, self.__connector[other])

    def __opAdd(self, other, _, x=None):
        if x is None:
            x = self.__connector[self.__recordName]
        return x + self.__overiddenValues.get(other, self.__connector[other])

    def __opSet(self, other, _, _1=None):
        return self.__overiddenValues.get(other, self.__connector[other])

    def __opTag(self, _1, _2, x=None):
        if x is None:
            x = self.__connector[self.__recordName]
        return x

    def __opFactor(self, other, _, x=None):
        if x is None:
            x = self.__connector[self.__recordName]
        value = self.__overiddenValues.get(other, self.__connector[other])
        factor = self.__getFactorValue(other)
        if factor is not None:
            value /= factor
        return x + int(round(value * next(self.__tags.itervalues())))

    def __addCoeffImpl(self, initial, value, coeff, op):
        if initial is None:
            initial = self.__connector[self.__recordName]
        value = self.__overiddenValues.get(value, self.__connector[value])
        coeff = self.__overiddenValues.get(coeff, self.__connector[coeff]) / self.__getFactorValue(coeff)
        return op(initial, int(round(value * coeff)))

    def __opAddCoeff(self, other, coeff, x=None):
        return self.__addCoeffImpl(x, other, coeff, lambda a, b: a + b)

    def __opSubCoeff(self, other, coeff, x=None):
        return self.__addCoeffImpl(x, other, coeff, lambda a, b: a - b)

    __OPERATORS = {ADD: __opAdd,
     SUB: __opSub,
     MUL: __opMul,
     SET: __opSet,
     TAG: __opTag,
     FACTOR: __opFactor,
     ADDCOEFF: __opAddCoeff,
     SUBCOEFF: __opSubCoeff}
