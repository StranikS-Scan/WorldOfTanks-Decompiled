# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/DamageModifierAbilityEquipment.py
from AbilityEquipment import AbilityEquipment
from gui.battle_control.controllers.sound_ctrls.common import getGunSoundObject
from items import vehicles
_BOOST_DAMAGE_SOUNDS = {0: 'ability_eisbaer_shot_01',
 1: 'ability_eisbaer_shot_02',
 2: 'ability_eisbaer_shot_03',
 3: 'ability_eisbaer_shot_04'}

class DamageModifierAbilityEquipment(AbilityEquipment):

    def set_currentDamageModifier(self, _):
        currentDamageModifier = self.currentDamageModifier
        equipments = self._sessionProvider.shared.equipments
        equipments.onUpdateDamageModifier(self.compactDescr, currentDamageModifier)

    def playCustomShotSound(self):
        descriptor = vehicles.getItemByCompactDescr(self.compactDescr)
        damageFirstIncrease = descriptor.damageFirstIncrease
        damageIncreasePerShot = descriptor.damageIncreasePerShot
        countPierced = int(round((self.currentDamageModifier - damageFirstIncrease) / damageIncreasePerShot))
        if countPierced in _BOOST_DAMAGE_SOUNDS:
            getGunSoundObject(self.entity).play(_BOOST_DAMAGE_SOUNDS[countPierced])
