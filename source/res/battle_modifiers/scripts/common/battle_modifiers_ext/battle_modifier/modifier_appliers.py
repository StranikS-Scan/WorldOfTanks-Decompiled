# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_modifiers/scripts/common/battle_modifiers_ext/battle_modifier/modifier_appliers.py
from __future__ import absolute_import
import copy
from future.utils import viewitems
from itertools import chain
from typing import Any, Dict, List, Optional, TYPE_CHECKING, Union
from battle_modifiers_common.battle_modifiers import BattleParams
from battle_modifiers_ext import remappings_cache
from battle_modifiers_ext.battle_modifier.modifier_helpers import makeUseTypeMethods
from battle_modifiers_ext.constants_ext import ModifiersWithRemapping, DataType, UseType
from constants import VEHICLE_HEALTH_DECIMALS
from items.components.sound_components import WWTripleSoundConfig
from items.components.shell_components import Stun
from math_common import ceilTo, round_py2_style_int
if TYPE_CHECKING:
    from battle_modifiers_common.battle_modifiers import ModifiersContext
g_cache = {}
_defaultVal = lambda _, paramVal, __=None: paramVal
_defaultMul = lambda val, paramVal, _=None: val * paramVal
_defaultAdd = lambda val, paramVal, _=None: val + paramVal
_dataTypeAppliers = {DataType.INT: {UseType.VAL: _defaultVal,
                UseType.MUL: lambda val, paramVal, _=None: round_py2_style_int(val * paramVal),
                UseType.ADD: _defaultAdd},
 DataType.FLOAT: {UseType.VAL: _defaultVal,
                  UseType.MUL: _defaultMul,
                  UseType.ADD: _defaultAdd},
 DataType.STRING: _defaultVal,
 DataType.DICT: {UseType.VAL: _defaultVal,
                 UseType.MUL: lambda val, paramVal, _=None: dict(chain(viewitems(paramVal), viewitems(val))),
                 UseType.ADD: lambda val, paramVal, _=None: dict(chain(viewitems(val), viewitems(paramVal)))},
 DataType.HASHABLE_DICT: {UseType.VAL: _defaultVal,
                          UseType.MUL: lambda val, paramVal, _=None: dict(chain(viewitems(paramVal), viewitems(val))),
                          UseType.ADD: lambda val, paramVal, _=None: dict(chain(viewitems(val), viewitems(paramVal)))}}

def _shotEffectsApplier(value, paramVal, ctx=None):
    from items import vehicles
    overridedValue = remappings_cache.g_cache.getValue(ModifiersWithRemapping.SHOT_EFFECTS, paramVal, value, ctx)
    return vehicles.g_cache.shotEffectsIndexes.get(overridedValue, value)


def _gunEffectsApplier(value, paramVal, ctx=None):
    from items import vehicles
    overridedValue = remappings_cache.g_cache.getValue(ModifiersWithRemapping.GUN_EFFECTS, paramVal, value, ctx)
    return vehicles.g_cache.gunEffects.get(overridedValue, value)


def _gunPrefabsApplier(value, paramVal, ctx=None):
    newPrefabPath = remappings_cache.g_cache.getValue(ModifiersWithRemapping.GUN_MAIN_PREFAB, paramVal, value, ctx)
    return newPrefabPath if newPrefabPath is not None else value


def _rootPrefabsMechanicEffectsApplier(value, paramVal, ctx=None):
    newPrefabPath = remappings_cache.g_cache.getValue(ModifiersWithRemapping.ROOT_PREFABS_MECHANIC_EFFECTS, paramVal, value, ctx)
    return newPrefabPath or value


def _engineSoundsApplier(_, paramVal, __=None):
    return WWTripleSoundConfig(wwsound='', wwsoundPC='_'.join((paramVal, 'pc')), wwsoundNPC='_'.join((paramVal, 'npc')))


def _exhaustEffectsApplier(value, paramVal, ctx=None):
    from items import vehicles
    overriddenValue = remappings_cache.g_cache.getValue(ModifiersWithRemapping.EXHAUST_EFFECTS, paramVal, value, ctx)
    return vehicles.g_cache.exhaustEffects.get(overriddenValue) or value


def _soundNotificationsApplier(value, paramVal, ctx=None):
    return remappings_cache.g_cache.getValues(ModifiersWithRemapping.SOUND_NOTIFICATIONS, paramVal, value) if isinstance(value, dict) else remappings_cache.g_cache.getValue(ModifiersWithRemapping.SOUND_NOTIFICATIONS, paramVal, value, ctx)


def _vehicleEffectsApplier(value, paramVal, ctx=None):
    from items import vehicles
    return vehicles.g_cache.getVehicleEffect(paramVal) or value


def _shellStunApplier(value, paramVal, ctx=None):
    if not paramVal or not value:
        return None
    else:
        stun = copy.copy(value)
        for k, v in viewitems(paramVal):
            setattr(stun, k, v)

        return stun


_customAppliers = {BattleParams.VEHICLE_HEALTH: {UseType.MUL: lambda val, paramVal, _=None: int(ceilTo(val * paramVal, VEHICLE_HEALTH_DECIMALS))},
 BattleParams.SHOT_EFFECTS: _shotEffectsApplier,
 BattleParams.GUN_EFFECTS: _gunEffectsApplier,
 BattleParams.GUN_MAIN_PREFAB: _gunPrefabsApplier,
 BattleParams.ROOT_PREFABS_MECHANIC_EFFECTS: _rootPrefabsMechanicEffectsApplier,
 BattleParams.ENGINE_SOUNDS: _engineSoundsApplier,
 BattleParams.EXHAUST_EFFECTS: _exhaustEffectsApplier,
 BattleParams.SOUND_NOTIFICATIONS: _soundNotificationsApplier,
 BattleParams.DESTRUCTION_EFFECT: _vehicleEffectsApplier,
 BattleParams.FULL_DESTRUCTION_EFFECT: _vehicleEffectsApplier,
 BattleParams.SHELL_STUN: _shellStunApplier,
 BattleParams.VSE_MODIFIER: lambda val, paramVal, _=None: paramVal['plan'] if val in paramVal['aspects'] else None}

def registerParamAppliers(paramId, dataType):
    global g_cache
    paramAppliers = makeUseTypeMethods(_dataTypeAppliers[dataType], True)
    if paramId in _customAppliers:
        paramAppliers.update(makeUseTypeMethods(_customAppliers[paramId]))
    g_cache[paramId] = paramAppliers


registerParamAppliers(BattleParams.VSE_MODIFIER, DataType.DICT)
