# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/sound_ctrls/vehicle_hit_sound_ctrl.py
import TriggersManager
from constants import VEHICLE_HIT_FLAGS as VHF
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from gui.battle_control.controllers.interfaces import IBattleController
from skeletons.gui.sounds import IVehicleHitSound

class VehicleHitSound(IVehicleHitSound, IBattleController):

    def startControl(self, *args):
        pass

    def stopControl(self):
        pass

    def getControllerID(self):
        return BATTLE_CTRL_ID.VEHICLE_HIT_SOUND

    def getSoundStringFromHitFlags(self, enemyVehID, hitFlags, enemiesHitCount):
        sound = None
        if hitFlags & VHF.ATTACK_IS_EXTERNAL_EXPLOSION:
            if hitFlags & VHF.MATERIAL_WITH_POSITIVE_DF_PIERCED_BY_EXPLOSION:
                sound = 'enemy_hp_damaged_by_near_explosion_by_player'
            elif hitFlags & VHF.IS_ANY_PIERCING_MASK:
                sound = 'enemy_no_hp_damage_by_near_explosion_by_player'
        elif hitFlags & VHF.MATERIAL_WITH_POSITIVE_DF_PIERCED_BY_PROJECTILE:
            if hitFlags & (VHF.GUN_DAMAGED_BY_PROJECTILE | VHF.GUN_DAMAGED_BY_EXPLOSION):
                sound = 'enemy_hp_damaged_by_projectile_and_gun_damaged_by_player'
            elif hitFlags & (VHF.CHASSIS_DAMAGED_BY_PROJECTILE | VHF.CHASSIS_DAMAGED_BY_EXPLOSION):
                sound = 'enemy_hp_damaged_by_projectile_and_chassis_damaged_by_player'
            else:
                sound = 'enemy_hp_damaged_by_projectile_by_player'
        elif hitFlags & VHF.MATERIAL_WITH_POSITIVE_DF_PIERCED_BY_EXPLOSION:
            sound = 'enemy_hp_damaged_by_explosion_at_direct_hit_by_player'
        elif hitFlags & VHF.RICOCHET and not hitFlags & VHF.DEVICE_PIERCED_BY_PROJECTILE:
            sound = 'enemy_ricochet_by_player'
            if enemiesHitCount == 1:
                TriggersManager.g_manager.fireTrigger(TriggersManager.TRIGGER_TYPE.PLAYER_SHOT_RICOCHET, targetId=enemyVehID)
        elif hitFlags & VHF.MATERIAL_WITH_POSITIVE_DF_NOT_PIERCED_BY_PROJECTILE:
            if hitFlags & (VHF.GUN_DAMAGED_BY_PROJECTILE | VHF.GUN_DAMAGED_BY_EXPLOSION):
                sound = 'enemy_no_hp_damage_at_attempt_and_gun_damaged_by_player'
            elif hitFlags & (VHF.CHASSIS_DAMAGED_BY_PROJECTILE | VHF.CHASSIS_DAMAGED_BY_EXPLOSION):
                sound = 'enemy_no_hp_damage_at_attempt_and_chassis_damaged_by_player'
            else:
                sound = 'enemy_no_hp_damage_at_attempt_by_player'
                if enemiesHitCount == 1:
                    TriggersManager.g_manager.fireTrigger(TriggersManager.TRIGGER_TYPE.PLAYER_SHOT_NOT_PIERCED, targetId=enemyVehID)
        elif hitFlags & (VHF.GUN_DAMAGED_BY_PROJECTILE | VHF.GUN_DAMAGED_BY_EXPLOSION):
            sound = 'enemy_no_hp_damage_at_no_attempt_and_gun_damaged_by_player'
        elif hitFlags & (VHF.CHASSIS_DAMAGED_BY_PROJECTILE | VHF.CHASSIS_DAMAGED_BY_EXPLOSION):
            sound = 'enemy_no_hp_damage_at_no_attempt_and_chassis_damaged_by_player'
        else:
            if hitFlags & (VHF.ARMOR_WITH_ZERO_DF_NOT_PIERCED_BY_PROJECTILE | VHF.DEVICE_NOT_PIERCED_BY_PROJECTILE) or not hitFlags & VHF.IS_ANY_PIERCING_MASK:
                sound = 'enemy_no_piercing_by_player'
            else:
                sound = 'enemy_no_hp_damage_at_no_attempt_by_player'
            if enemiesHitCount == 1:
                TriggersManager.g_manager.fireTrigger(TriggersManager.TRIGGER_TYPE.PLAYER_SHOT_NOT_PIERCED, targetId=enemyVehID)
        return sound
