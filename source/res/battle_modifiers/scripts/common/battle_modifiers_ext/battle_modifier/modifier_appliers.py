# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_modifiers/scripts/common/battle_modifiers_ext/battle_modifier/modifier_appliers.py
from battle_modifiers_common.battle_modifiers import BattleParams
from battle_modifiers_ext import remappings_cache
from battle_modifiers_ext.battle_modifier.modifier_helpers import makeUseTypeMethods
from battle_modifiers_ext.constants_ext import ModifiersWithRemapping, DataType, UseType
from constants import VEHICLE_HEALTH_DECIMALS
from items.components.sound_components import WWTripleSoundConfig
from math_common import ceilTo
g_cache = {}
_defaultVal = lambda _, paramVal, __=None: paramVal
_defaultMul = lambda val, paramVal, _=None: val * paramVal
_defaultAdd = lambda val, paramVal, _=None: val + paramVal
_dataTypeAppliers = {DataType.INT: {UseType.VAL: _defaultVal,
                UseType.MUL: lambda val, paramVal, __=None: int(round(val * paramVal)),
                UseType.ADD: _defaultAdd},
 DataType.FLOAT: {UseType.VAL: _defaultVal,
                  UseType.MUL: _defaultMul,
                  UseType.ADD: _defaultAdd},
 DataType.STRING: _defaultVal}

def _shotEffectsApplier(value, paramVal, ctx=None):
    from items import vehicles
    overridedValue = remappings_cache.g_cache.getValue(ModifiersWithRemapping.SHOT_EFFECTS, paramVal, value, ctx)
    return vehicles.g_cache.shotEffectsIndexes.get(overridedValue, value)


def _gunEffectsApplier(value, paramVal, ctx=None):
    from items import vehicles
    overridedValue = remappings_cache.g_cache.getValue(ModifiersWithRemapping.GUN_EFFECTS, paramVal, value, ctx)
    return vehicles.g_cache.gunEffects.get(overridedValue, value)


def _engineSoundsApplier(_, paramVal, __=None):
    return WWTripleSoundConfig(wwsound='', wwsoundPC='_'.join((paramVal, 'pc')), wwsoundNPC='_'.join((paramVal, 'npc')))


def _exhaustEffectApplier(_, paramVal, __=None):
    from items import vehicles
    return vehicles.g_cache.exhaustEffect(paramVal)


_customAppliers = {BattleParams.VEHICLE_HEALTH: {UseType.MUL: lambda val, paramVal, _=None: int(ceilTo(val * paramVal, VEHICLE_HEALTH_DECIMALS))},
 BattleParams.SHOT_EFFECTS: _shotEffectsApplier,
 BattleParams.GUN_EFFECTS: _gunEffectsApplier,
 BattleParams.ENGINE_SOUNDS: _engineSoundsApplier,
 BattleParams.EXHAUST_EFFECT: _exhaustEffectApplier}

def registerParamAppliers(paramId, dataType):
    global g_cache
    paramAppliers = makeUseTypeMethods(_dataTypeAppliers[dataType], True)
    if paramId in _customAppliers:
        paramAppliers.update(makeUseTypeMethods(_customAppliers[paramId]))
    g_cache[paramId] = paramAppliers
