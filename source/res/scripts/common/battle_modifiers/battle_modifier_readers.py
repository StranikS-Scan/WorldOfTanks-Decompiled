# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/battle_modifiers/battle_modifier_readers.py
from battle_modifier_constants import DataType, UseType, BattleParams
from battle_modifier_helpers import makeUseTypeMethods
from math import radians, degrees
from items.components.component_constants import KMH_TO_MS, MS_TO_KMH
g_cache = {}
_readInt = lambda dataSection: dataSection.asInt
_readFloat = lambda dataSection: dataSection.asFloat
_readFloatTuple = lambda dataSection: tuple(map(float, dataSection.asString.split()))
_readToDegrees = lambda dataSection: degrees(dataSection.asFloat)
_readToRadians = lambda dataSection: radians(dataSection.asFloat)
_radiansType = {UseType.VAL: _readToRadians,
 UseType.MUL: _readFloat,
 UseType.ADD: _readToRadians}
_readToKMH = lambda dataSection: dataSection.asFloat * MS_TO_KMH
_readToMS = lambda dataSection: dataSection.asFloat * KMH_TO_MS
_speedType = {UseType.VAL: _readToMS,
 UseType.MUL: _readFloat,
 UseType.ADD: _readToMS}
_dataTypeReaders = {DataType.INT: {UseType.VAL: _readInt,
                UseType.MUL: _readFloat,
                UseType.ADD: _readInt},
 DataType.FLOAT: _readFloat}
_customReaders = {BattleParams.TURRET_ROTATION_SPEED: _radiansType,
 BattleParams.GUN_ROTATION_SPEED: _radiansType,
 BattleParams.DISP_FACTOR_CHASSIS_MOVEMENT: {UseType.VAL: _readToKMH,
                                             UseType.ADD: _readToKMH},
 BattleParams.DISP_FACTOR_CHASSIS_ROTATION: {UseType.VAL: _readToDegrees,
                                             UseType.ADD: _readToDegrees},
 BattleParams.DISP_FACTOR_TURRET_ROTATION: {UseType.VAL: _readToDegrees,
                                            UseType.ADD: _readToDegrees},
 BattleParams.NORMALIZATION_ANGLE: _radiansType,
 BattleParams.RICOCHET_ANGLE: _radiansType,
 BattleParams.FW_MAX_SPEED: _speedType,
 BattleParams.BK_MAX_SPEED: _speedType,
 BattleParams.ROTATION_SPEED_ON_STILL: _radiansType,
 BattleParams.ROTATION_SPEED_ON_MOVE: _radiansType}

def registerParamReaders(paramId, dataType):
    global g_cache
    paramReaders = makeUseTypeMethods(_dataTypeReaders[dataType], True)
    if paramId in _customReaders:
        paramReaders.update(makeUseTypeMethods(_customReaders[paramId]))
    g_cache[paramId] = paramReaders
