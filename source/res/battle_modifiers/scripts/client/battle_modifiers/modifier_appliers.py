# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_modifiers/scripts/client/battle_modifiers/modifier_appliers.py
from battle_modifiers_ext import remappings_cache
from battle_modifiers_ext.constants_ext import ModifiersWithRemapping
from typing import Optional, TYPE_CHECKING
if TYPE_CHECKING:
    from battle_modifiers_common.battle_modifiers import ModifiersContext

def chassisDecalsApplier(value, paramVal, ctx=None):
    from helpers import DecalMap
    overriddenValue = remappings_cache.g_cache.getValue(ModifiersWithRemapping.CHASSIS_DECALS, paramVal, value, ctx)
    return overriddenValue if DecalMap.g_instance.getTextureSet(overriddenValue) else value
