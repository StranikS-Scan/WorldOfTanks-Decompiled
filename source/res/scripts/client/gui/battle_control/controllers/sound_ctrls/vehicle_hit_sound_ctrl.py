# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/sound_ctrls/vehicle_hit_sound_ctrl.py
import TriggersManager
from constants import VEHICLE_HIT_FLAGS as VHF, WT_TEAMS, WT_BATTLE_STAGE
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from gui.battle_control.controllers.interfaces import IBattleController
from gui.shared.gui_items.Vehicle import VEHICLE_TAGS
from shared_utils import first
from skeletons.gui.sounds import IVehicleHitSound
from gui.battle_control import avatar_getter
import random

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


class EventVehicleHitSound(VehicleHitSound):
    _ALTERNATIVE_SOUND_NOTIFICATIONS = {'enemy_hp_damaged_by_projectile_and_gun_damaged_by_player': ['wt23_hunters_vo_shooting_at_wt_shield', 'enemy_no_hp_damage_at_attempt_by_player'],
     'enemy_hp_damaged_by_projectile_and_chassis_damaged_by_player': ['wt23_hunters_vo_shooting_at_wt_shield', 'enemy_no_hp_damage_at_attempt_by_player'],
     'enemy_hp_damaged_by_projectile_by_player': ['wt23_hunters_vo_shooting_at_wt_shield', 'enemy_no_hp_damage_at_attempt_by_player'],
     'enemy_hp_damaged_by_explosion_at_direct_hit_by_player': ['wt23_hunters_vo_shooting_at_wt_shield', 'enemy_no_hp_damage_at_attempt_by_player'],
     'enemy_hp_damaged_by_near_explosion_by_player': ['wt23_hunters_vo_shooting_at_wt_shield', 'enemy_no_hp_damage_at_attempt_by_player'],
     'enemy_ricochet_by_player': ['wt23_hunters_vo_shooting_at_wt_shield', 'enemy_ricochet_by_player']}
    _INSTANT_STUN_SHOT_SKIP_HIT_NOTIFICATIONS = ('enemy_no_hp_damage_at_attempt_and_gun_damaged_by_player', 'enemy_no_hp_damage_at_no_attempt_and_gun_damaged_by_player', 'enemy_no_hp_damage_at_attempt_and_chassis_damaged_by_player', 'enemy_no_hp_damage_at_no_attempt_and_chassis_damaged_by_player', 'enemy_no_piercing_by_player', 'enemy_no_hp_damage_at_attempt_by_player', 'enemy_no_hp_damage_at_no_attempt_by_player', 'enemy_no_hp_damage_by_near_explosion_by_player', 'enemy_ricochet_by_player')

    def getSoundStringFromHitFlags(self, enemyVehID, hitFlags, enemiesHitCount):
        sound = super(EventVehicleHitSound, self).getSoundStringFromHitFlags(enemyVehID, hitFlags, enemiesHitCount)
        team = avatar_getter.getPlayerTeam()
        if team != WT_TEAMS.BOSS_TEAM:
            arena = avatar_getter.getArena()
            vehicleInfo = arena.vehicles.get(enemyVehID)
            tags = vehicleInfo['vehicleType'].type.tags
            if VEHICLE_TAGS.EVENT_BOSS in tags:
                publicHealth = arena.arenaInfo.arenaPublicHealth
                soundThresholdPercent = 3
                bossHealthInfo = first([ healthInfo for healthInfo in publicHealth.healthInfoList if healthInfo['vehicleID'] == enemyVehID ])
                if float(bossHealthInfo['health']) / vehicleInfo['maxHealth'] * 100 < soundThresholdPercent:
                    return sound
                if WT_BATTLE_STAGE.getCurrent(arena.arenaInfo) == WT_BATTLE_STAGE.INVINCIBLE:
                    return self.__getAlternativeSound(sound)
        elif hitFlags & VHF.STUN_STARTED and sound in self._INSTANT_STUN_SHOT_SKIP_HIT_NOTIFICATIONS:
            return None
        return sound

    def __getAlternativeSound(self, sound):
        altNotification = self._ALTERNATIVE_SOUND_NOTIFICATIONS.get(sound, None)
        if not altNotification:
            return sound
        else:
            if random.randrange(1, 100) > 80:
                altNotification = altNotification[1]
            else:
                altNotification = altNotification[0]
            return altNotification
