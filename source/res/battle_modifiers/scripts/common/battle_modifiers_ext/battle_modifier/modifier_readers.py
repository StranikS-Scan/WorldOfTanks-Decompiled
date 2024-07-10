# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_modifiers/scripts/common/battle_modifiers_ext/battle_modifier/modifier_readers.py
from battle_modifiers_common.battle_modifiers import BattleParams
from battle_modifiers_ext.constants_ext import DataType, UseType
from bonus_caps_overrides import readBonusCapsOverrides
from constants import DamageAbsorptionLabelToType
from crystal_rewards_common import readCrystalRewards
from items.components.component_constants import KMH_TO_MS, MS_TO_KMH
from modifier_helpers import makeUseTypeMethods
from math import radians, degrees
from renewable_subscription_common.config import readGoldReserveGains
g_cache = {}
_readInt = lambda dataSection: dataSection.asInt
_readFloat = lambda dataSection: dataSection.asFloat
_readString = lambda dataSection: dataSection.asString
_readDict = lambda dataSection: {k:v.asString for k, v in dataSection.items()}
_dataTypeReaders = {DataType.INT: {UseType.VAL: _readInt,
                UseType.MUL: _readFloat,
                UseType.ADD: _readInt},
 DataType.FLOAT: _readFloat,
 DataType.STRING: _readString,
 DataType.DICT: _readDict}
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
_damageAbsorptionReader = lambda dataSection: DamageAbsorptionLabelToType[dataSection.asString]

def _readVisualScriptPlan(dataSection):
    from visual_script.misc import readVisualScriptPlan
    return {'aspects': dataSection.readString('aspects', '').split(),
     'plan': readVisualScriptPlan(dataSection['plan'])}


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
 BattleParams.ROTATION_SPEED_ON_MOVE: _radiansType,
 BattleParams.ARMOR_SPALLS_CONE_ANGLE: _radiansType,
 BattleParams.ARMOR_SPALLS_DAMAGE_ABSORPTION: _damageAbsorptionReader,
 BattleParams.VSE_MODIFIER: _readVisualScriptPlan,
 BattleParams.BONUS_CAPS_OVERRIDES: readBonusCapsOverrides,
 BattleParams.CRYSTAL_REWARDS: readCrystalRewards,
 BattleParams.GOLD_RESERVE_GAINS: readGoldReserveGains}

def registerParamReaders(paramId, dataType):
    global g_cache
    paramReaders = makeUseTypeMethods(_dataTypeReaders[dataType], True)
    if paramId in _customReaders:
        paramReaders.update(makeUseTypeMethods(_customReaders[paramId]))
    g_cache[paramId] = paramReaders


registerParamReaders(BattleParams.VSE_MODIFIER, DataType.DICT)
