# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/components/ny_components.py
from collections import namedtuple
from typing import Optional, List, Dict

class SlotDescriptor(object):

    def __init__(self, cfg):
        self.__cfg = cfg

    def __getattr__(self, name):
        try:
            return self.__cfg[name]
        except KeyError:
            raise AttributeError

    def __cmp__(self, other):
        return self.id - other.id


class ToyModelOverride(object):
    _FIELDS_MAP = {'modelOverride': 'modelName'}
    _FLOAT_PARAMS = ('minAlpha', 'maxAlphaDistance')
    __slots__ = ('modelOverride', 'hangingEffectName', 'regularEffectName', 'animationSequence', 'hangingAnimationSequence', 'minAlpha', 'maxAlphaDistance')

    def __init__(self, **kwargs):
        for slotName in self.__slots__:
            setattr(self, slotName, kwargs.get(slotName))

    @classmethod
    def createModel(cls, node):
        modelOverrideDict = {slotName:node.readString(slotName) for slotName in cls.__slots__ if node.has_key(slotName)}
        for floatParam in cls._FLOAT_PARAMS:
            if floatParam in modelOverrideDict:
                modelOverrideDict[floatParam] = float(modelOverrideDict[floatParam])

        return ToyModelOverride(**modelOverrideDict) if modelOverrideDict else None

    def getUpdateDict(self):
        result = {}
        for slotName in self.__slots__:
            slotValue = getattr(self, slotName, None)
            if slotValue is not None:
                result[self._FIELDS_MAP.get(slotName, slotName)] = slotValue

        return result


ToyTransformation = namedtuple('ToyTransformation', 'transform, modelOverride')

class VariadicDiscountDescriptor(object):
    __slots__ = ('_id', '_firstGoodieId', '_lastGoodieId', '_level')

    def __init__(self, discountId, firstGoodieId, lastGoodieId, level):
        self._id = discountId
        self._firstGoodieId = firstGoodieId
        self._lastGoodieId = lastGoodieId
        self._level = level

    @property
    def discountId(self):
        return self._id

    @property
    def goodiesRange(self):
        return (self._firstGoodieId, self._lastGoodieId)

    @property
    def firstGoodieId(self):
        return self._firstGoodieId

    @property
    def lastGoodieId(self):
        return self._lastGoodieId

    @property
    def level(self):
        return self._level
