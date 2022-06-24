# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/battle_modifiers/helpers.py
from typing import TYPE_CHECKING
from gui.impl.lobby.battle_modifiers.constants import MOD_TYPE_MAP, PHYS_TYPE_MAP, USE_TYPE_MAP, GAMEPLAY_IMPACT_MAP
from gui.impl.gen.view_models.views.lobby.battle_modifiers.modifier_model import ModifierModel
if TYPE_CHECKING:
    from battle_modifiers.battle_modifiers import BattleModifier

def packModifierModel(modifier):
    result = ModifierModel()
    result.setValue(modifier.value)
    result.setUseType(USE_TYPE_MAP[modifier.useType])
    result.setModificationType(MOD_TYPE_MAP[modifier.param.id])
    result.setPhysicalType(PHYS_TYPE_MAP[modifier.param.clientData.physicalType])
    result.setGameplayImpact(GAMEPLAY_IMPACT_MAP[modifier.gameplayImpact])
    return result
