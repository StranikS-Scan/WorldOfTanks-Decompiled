# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/components/supply_slot_categories.py
from typing import Set, Any, Optional, List, Dict, Tuple
from ResMgr import DataSection
from debug_utils import LOG_CODEPOINT_WARNING, LOG_WARNING
from items import _xml
from soft_exception import SoftException

class SlotCategories(object):
    FIREPOWER = 'firepower'
    SURVIVABILITY = 'survivability'
    MOBILITY = 'mobility'
    STEALTH = 'stealth'
    TACTICS = 'tactics'
    FIRESUPPORT = 'firesupport'
    RECONNAISSANCE = 'reconnaissance'
    UNIVERSAL = 'universal'
    ORDER = (FIREPOWER,
     SURVIVABILITY,
     MOBILITY,
     STEALTH,
     TACTICS,
     FIRESUPPORT,
     RECONNAISSANCE)
    ALL = frozenset([FIREPOWER,
     SURVIVABILITY,
     MOBILITY,
     STEALTH,
     TACTICS,
     FIRESUPPORT,
     RECONNAISSANCE,
     UNIVERSAL])


class CategoriesHolder(object):
    __slots__ = ('categories',)

    def __init__(self):
        super(CategoriesHolder, self).__init__()
        self.categories = set()

    def checkIntersection(self, other):
        return bool(self.categories & other.categories)


class SupplySlotFactorLevels(object):
    REGULAR = 0
    IMPROVED = 1
    ALL = (REGULAR, IMPROVED)


class SupplySlotFilter(object):

    @staticmethod
    def defineActiveValuesLevel(slotCategories, supplyCategories):
        return SupplySlotFactorLevels.IMPROVED if slotCategories & supplyCategories else SupplySlotFactorLevels.REGULAR


class AttrsOperation(object):
    MUL = 'mul'
    ADD = 'add'
    ALL = (MUL, ADD)
    _DEFAULT_VALUES = {MUL: 1.0,
     ADD: 0.0}
    _OPERATIONS = {MUL: lambda x, y: x * y,
     ADD: lambda x, y: x + y}

    @staticmethod
    def updateDictWithAttribute(attrsDict, attrName, opType, value):
        operation = AttrsOperation._OPERATIONS[opType]
        prevValue = attrsDict.get(attrName, AttrsOperation._DEFAULT_VALUES[opType])
        newValue = operation(prevValue, value)
        attrsDict[attrName] = newValue


class LevelsFactor(object):
    __slots__ = ('opType', 'values')

    def __init__(self, values, opType=None):
        super(LevelsFactor, self).__init__()
        self.values = values
        self.opType = opType

    def __str__(self):
        return '{}: (opType={}, values={})'.format(self.__class__.__name__, self.opType, self.values)

    def getActiveValue(self, level):
        return self.values[level] if level < len(self.values) else self.values[-1]

    def applyLevelToAttrsDict(self, level, attrsDict, attrName):
        if self.opType is None:
            LOG_CODEPOINT_WARNING('Should not apply factors with no opType!')
            return
        else:
            activeValue = self.getActiveValue(level)
            AttrsOperation.updateDictWithAttribute(attrsDict, attrName, self.opType, activeValue)
            return

    @staticmethod
    def readLevelsFactor(xmlCtx, factorSection):
        attrName = _xml.readString(xmlCtx, factorSection, 'attribute')
        opTypeName = _xml.readString(xmlCtx, factorSection, 'type')
        if opTypeName not in AttrsOperation.ALL:
            raise SoftException('Unknown opTypeName ({}) for LevelsFactor'.format(opTypeName))
        values = LevelsFactor._readFactorValues(xmlCtx, factorSection, 'valueByLevel')
        return (attrName, LevelsFactor(values, opTypeName))

    @staticmethod
    def readTypelessLevelsFactor(xmlCtx, factorSection, factorName):
        values = LevelsFactor._readFactorValues(xmlCtx, factorSection, factorName)
        return LevelsFactor(values)

    @staticmethod
    def _readFactorValues(xmlCtx, section, sectionName):
        values = _xml.readTupleOfFloats(xmlCtx, section, sectionName)
        return values
