# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_modifiers/scripts/client/battle_modifiers/__init__.py
from battle_modifiers.modifier_appliers import chassisDecalsApplier
from battle_modifiers_common.battle_modifiers import BattleParams
from battle_modifiers_ext.battle_modifier.modifier_appliers import registerParamAppliers
from battle_modifiers_ext.constants_ext import DataType

def preInit():
    registerParamAppliers(BattleParams.CHASSIS_DECALS, DataType.STRING, customFunc=chassisDecalsApplier)
