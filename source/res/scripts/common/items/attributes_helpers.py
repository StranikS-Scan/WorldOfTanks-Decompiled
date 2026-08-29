# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/attributes_helpers.py
import copy
from operator import add, mul
from math_common import isclose
from soft_exception import SoftException
from items._xml import raiseWrongXml, readFloat, readBool, readString

class MODIFIER_TYPE(object):
    ADD = (0.0, add, add)
    MUL = (1.0, add, mul)


def readModifiers(xmlCtx, section, readers, defaultIndependent=True, prettyMul=True):
    xmlCtx = (xmlCtx, section.name)
    modifiers = []
    for opType, data in section.items():
        name = readString(xmlCtx, data, 'name')
        value = readFloat(xmlCtx, data, 'value')
        independent = readBool(xmlCtx, data, 'independent', defaultIndependent)
        for reader in readers:
            modifier = reader.createModifier(xmlCtx, opType, name, value, independent, prettyMul)
            if modifier:
                modifiers.append(modifier)
                break
        else:
            raiseWrongXml(xmlCtx, opType, 'Exists trash modifiers, name - {}'.format(name))

    return modifiers


def createModifier(opType, name, value, readers):
    for reader in readers:
        modifier = reader.createModifier(None, opType, name, value)
        if modifier:
            return modifier

    return raiseWrongXml(None, opType, 'Unknown modifier - opType({}), name({})'.format(opType, name))


class CommonFactorsHelper(object):
    MODIFIERS = MODIFIER_TYPE
    ALLOWED_ATTRS = None
    PREFIX = None

    def __init__(self):
        if self.ALLOWED_ATTRS is None or self.PREFIX is None:
            raise SoftException('Incorrect ALLOWED_ATTRS({}) or PREFIX({})'.format(self.ALLOWED_ATTRS, self.PREFIX))
        self.ATTRS = attrs = {}
        self.DEFAULTS = defaults = {}
        for aName in self.ALLOWED_ATTRS:
            modifier = None
            if isinstance(aName, tuple):
                aName, modifier = aName
                defaults[aName] = modifier[0]
            attrs[aName] = modifier

        return

    def createModifier(self, xmlCtx, opType, name, value, independent=True, prettyMul=True):
        if not name.startswith(self.PREFIX):
            return
        else:
            attrName = intern(name[len(self.PREFIX):])
            modifier = getattr(self.MODIFIERS, opType.upper(), None)
            if modifier is None:
                return raiseWrongXml(xmlCtx, opType, 'Unknown operation type')
            if prettyMul and modifier is self.MODIFIERS.MUL:
                value -= 1
            if attrName not in self.ATTRS:
                return raiseWrongXml(xmlCtx, opType, 'Unknown attribute attrName - {}'.format(attrName))
            if self.ATTRS[attrName] is None:
                self.ATTRS[attrName] = modifier
                self.DEFAULTS[attrName] = modifier[0]
            elif self.ATTRS[attrName] is not modifier:
                return raiseWrongXml(xmlCtx, opType, 'Different operations types, name - {}'.format(attrName))
            return ((self.PREFIX, attrName), value, independent)

    def collect(self, total, modifiers):
        uniqueAttrs = dict()
        curAttrs = self.ATTRS
        curPrefix = self.PREFIX
        for (attrPrefix, attrName), value, independent in modifiers:
            if attrPrefix != curPrefix:
                continue
            default, merger, applier = curAttrs[attrName]
            if independent:
                value = merger(default, value)
                if isclose(value, default):
                    continue
                total[attrName] = applier(total[attrName], value)
            uniqueAttrs[attrName] = merger(uniqueAttrs.get(attrName, default), value)

        if uniqueAttrs:
            self.apply(total, uniqueAttrs)

    def apply(self, total, mergedModifiers):
        curAttrs = self.ATTRS
        for attrName, value in mergedModifiers.iteritems():
            default, _, applier = curAttrs[attrName]
            if isclose(value, default):
                continue
            total[attrName] = applier(total[attrName], value)

    def defaults(self):
        return copy.copy(self.DEFAULTS)
