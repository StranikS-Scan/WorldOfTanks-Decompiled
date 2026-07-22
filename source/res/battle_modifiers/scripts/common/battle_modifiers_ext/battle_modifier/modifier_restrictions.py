# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_modifiers/scripts/common/battle_modifiers_ext/battle_modifier/modifier_restrictions.py
from soft_exception import SoftException
from battle_modifiers_ext.battle_modifier import modifier_readers
from battle_modifiers_ext.constants_ext import UseType, ModifierRestriction
from typing import TYPE_CHECKING, Any, Set, Dict, Type, Optional, Tuple
if TYPE_CHECKING:
    from battle_modifiers_ext.battle_modifier.modifier_filters import ModificationNode
    from ResMgr import DataSection

class IModifierValidator(object):
    __slots__ = ('arg',)

    def __init__(self, config, paramId):
        self.arg = self._readConfig(config, paramId)

    def __call__(self, modificationNode):
        if not self._validate(modificationNode):
            paramName = modificationNode.param.name
            errorMsg = self._errorMessage(modificationNode)
            raise SoftException("[BattleModifier] Validation error for param '{}': {}".format(paramName, errorMsg))

    def _readConfig(self, config, paramId):
        return None

    def _validate(self, modificationNode):
        raise NotImplementedError

    def _errorMessage(self, modificationNode):
        pass


class UseTypeValidator(IModifierValidator):

    def _readConfig(self, config, _):
        useTypes = []
        for useTypeName in config.asString.split():
            if useTypeName not in UseType.NAMES:
                raise SoftException("[BattleParams] Unknown use type '{}'".format(useTypeName))
            useTypes.append(UseType.NAME_TO_ID[useTypeName])

        return set(useTypes)

    def _validate(self, modificationNode):
        return modificationNode.useType in self.arg

    def _errorMessage(self, modificationNode):
        return "use type '{}' is not allowed".format(UseType.ID_TO_NAME[modificationNode.useType])


class IValueValidator(IModifierValidator):

    def _readConfig(self, config, paramId):
        return modifier_readers.g_cache[paramId][UseType.VAL](config)

    def _validate(self, modificationNode):
        return True if modificationNode.useType != UseType.VAL else self._validateValue(modificationNode.value)

    def _validateValue(self, value):
        raise NotImplementedError


class MinValidator(IValueValidator):

    def _validateValue(self, value):
        return value >= self.arg

    def _errorMessage(self, modificationNode):
        return 'value should be at least {}, given value - {}'.format(self.arg, modificationNode.value)


class MaxValidator(IValueValidator):

    def _validateValue(self, value):
        return value <= self.arg

    def _errorMessage(self, modificationNode):
        return 'value should be no more than {}, given value - {}'.format(self.arg, modificationNode.value)


class IValueLimiter(object):

    def __call__(self, value):
        raise NotImplementedError


class MinLimiter(IValueLimiter):
    __slots__ = ('__min',)

    def __init__(self, value):
        self.__min = value

    def __call__(self, value):
        return self.__min if value < self.__min else value


class MaxLimiter(IValueLimiter):
    __slots__ = ('__max',)

    def __init__(self, value):
        self.__max = value

    def __call__(self, value):
        return self.__max if value > self.__max else value


class MinMaxLimiter(IValueLimiter):
    __slots__ = ('__min', '__max')

    def __init__(self, minValue, maxValue):
        self.__min = minValue
        self.__max = maxValue

    def __call__(self, value):
        if value < self.__min:
            return self.__min
        return self.__max if value > self.__max else value


g_modifierValidators = {ModifierRestriction.MIN: MinValidator,
 ModifierRestriction.MAX: MaxValidator,
 ModifierRestriction.USE_TYPES: UseTypeValidator}

def readRestrictions(config, paramId, allowedRestrictions=None):
    if not config.has_key('restrictions'):
        return ({}, None, None)
    else:
        if allowedRestrictions is None:
            allowedRestrictions = ModifierRestriction.ALL
        validators = {}
        minValue = None
        maxValue = None
        for restrictionName, restrictionSection in config['restrictions'].items():
            if restrictionName not in ModifierRestriction.NAMES:
                raise SoftException("[BattleParams] Unknown restriction '{}'".format(restrictionName))
            restrictionId = ModifierRestriction.NAME_TO_ID[restrictionName]
            if restrictionId not in allowedRestrictions:
                raise SoftException("[BattleParams] Restriction '{}' isn't allowed".format(restrictionName))
            if restrictionId in validators:
                raise SoftException("[BattleParams] Duplicate restriction '{}'".format(restrictionName))
            validators[restrictionId] = g_modifierValidators[restrictionId](restrictionSection, paramId)

        if ModifierRestriction.MIN in validators:
            minValue = validators[ModifierRestriction.MIN].arg
        if ModifierRestriction.MAX in validators:
            maxValue = validators[ModifierRestriction.MAX].arg
        if minValue is not None and maxValue is not None and minValue > maxValue:
            raise SoftException('[BattleParams] Incorrect limits: min - {}, max - {}'.format(minValue, maxValue))
        return (validators, minValue, maxValue)


def getValueLimiter(minValue, maxValue):
    if minValue is not None and maxValue is not None:
        return MinMaxLimiter(minValue, maxValue)
    elif minValue is not None:
        return MinLimiter(minValue)
    else:
        return MaxLimiter(maxValue) if maxValue is not None else None
