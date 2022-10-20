# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/common/buffs_helpers.py
from enum import Enum
from itertools import izip_longest, izip

def makeBuffName(buffName, typeDescriptor):
    return buffName.format(**{'lvl': typeDescriptor.level,
     'class': typeDescriptor.type.getVehicleClass()})


def extractBuffNamePrefix(name):
    return name.split('_')[0]


class ModifierOpType(Enum):
    ADD_FACTOR = 'addFactor'
    ADD_VALUE = 'addValue'
    SET_VALUE = 'setValue'


class ModifiersDict(object):

    def __init__(self):
        super(ModifiersDict, self).__init__()
        self.__dict = {}

    def __add__(self, other):
        result = ModifiersDict()
        for k in self.__dict.viewkeys() | other.__dict.viewkeys():
            result.__dict[k] = self.__combineModifiers(self.__dict.get(k, 0.0), other.__dict.get(k, 0.0))

        return result

    def __len__(self):
        return len(self.__dict)

    def getModifiers(self, name):
        return {op:self.__dict[op.value, name] for op in ModifierOpType if (op.value, name) in self.__dict}

    def readXml(self, section):
        for opType, factorsSection in section.items():
            for modifierName, modifierValue in factorsSection.items():
                key = (opType, modifierName)
                self.__dict[key] = self.__combineModifiers(self.__readXmlModifierValue(modifierValue.asString), self.__dict.get(key, 0.0))

    @staticmethod
    def __combineModifiers(modifiersA, modifiersB):
        isTupleA = isinstance(modifiersA, tuple)
        isTupleB = isinstance(modifiersB, tuple)
        if isTupleA or isTupleB:
            modifiersA = (modifiersA,) if not isTupleA else modifiersA
            modifiersB = (modifiersB,) if not isTupleB else modifiersB
            return tuple((f1 + f2 for f1, f2 in izip_longest(modifiersA, modifiersB, fillvalue=0.0)))
        return modifiersA + modifiersB

    @staticmethod
    def __readXmlModifierValue(modifierValueString):
        value = modifierValueString.split()
        return float(value[0]) if len(value) == 1 else tuple((float(v) for v in value))


class ValueSimpleModifier(object):
    DEFAULT_FACTOR = 1.0
    OPERATIONS_ORDERED = ((ModifierOpType.ADD_FACTOR, lambda a, b: a * (ValueSimpleModifier.DEFAULT_FACTOR + b)), (ModifierOpType.ADD_VALUE, lambda a, b: a + b), (ModifierOpType.SET_VALUE, lambda a, b: b))
    VALUE_FAIL_CHECKS = (lambda a, b: isinstance(a, tuple) and isinstance(b, tuple) and len(a) != len(b), lambda a, b: isinstance(a, list) and isinstance(b, tuple) and len(a) != len(b), lambda a, b: isinstance(a, (int, float)) and isinstance(b, tuple))
    TYPE_RESOLVERS = {(int, int): lambda opFn, f1, f2: opFn(f1, f2),
     (float, float): lambda opFn, f1, f2: opFn(f1, f2),
     (int, float): lambda opFn, f1, f2: opFn(f1, f2),
     (float, int): lambda opFn, f1, f2: opFn(f1, f2),
     (bool, bool): lambda opFn, f1, f2: opFn(f1, f2),
     (tuple, float): lambda opFn, t, f: tuple((opFn(a, f) for a in t)),
     (tuple, tuple): lambda opFn, t1, t2: tuple((opFn(a, b) for a, b in izip(t1, t2))),
     (tuple, list): lambda opFn, t1, t2: tuple((opFn(a, b) for a, b in izip(t1, t2))),
     (list, float): lambda opFn, t, f: list((opFn(a, f) for a in t)),
     (list, tuple): lambda opFn, t1, t2: list((opFn(a, b) for a, b in izip(t1, t2))),
     (list, list): lambda opFn, t1, t2: list((opFn(a, b) for a, b in izip(t1, t2)))}

    def __init__(self, modifiers):
        super(ValueSimpleModifier, self).__init__()
        self.modifiers = modifiers

    def apply(self, value):
        result = value
        for opType, opFn in self.OPERATIONS_ORDERED:
            if opType in self.modifiers:
                modifier = self.modifiers[opType]
                if any((check(result, modifier) for check in self.VALUE_FAIL_CHECKS)):
                    return (None, 'VALUE_FAIL_CHECK')
                resolver = self.TYPE_RESOLVERS.get((type(result), type(modifier)), None)
                if resolver is None:
                    return (None, 'TYPES_RESOLVER_MISSING for types({}, {})'.format(type(result), type(modifier)))
                result = resolver(opFn, result, modifier)

        return (result, None)
