# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/DamageModifierAbilityEquipment.py
from AbilityEquipment import AbilityEquipment

class DamageModifierAbilityEquipment(AbilityEquipment):

    def set_currentDamageModifier(self, _):
        currentDamageModifier = self.currentDamageModifier
        equipments = self._sessionProvider.shared.equipments
        equipments.onUpdateDamageModifier(self.compactDescr, currentDamageModifier)
