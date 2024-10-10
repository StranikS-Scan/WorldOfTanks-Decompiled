# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/battle_control/controllers/sound_ctrl/vehicle_hit_sound_ctrl.py
import random
from shared_utils import first
from gui.battle_control import avatar_getter
from gui.battle_control.controllers.sound_ctrls.vehicle_hit_sound_ctrl import VehicleHitSound
from white_tiger_common import wt_constants

class WTVehicleHitSound(VehicleHitSound):
    _ALTERNATIVE_SOUND_NOTIFICATIONS = {'enemy_hp_damaged_by_projectile_and_gun_damaged_by_player': ['wt23_hunters_vo_shooting_at_wt_shield', 'enemy_no_hp_damage_at_attempt_by_player'],
     'enemy_hp_damaged_by_projectile_and_chassis_damaged_by_player': ['wt23_hunters_vo_shooting_at_wt_shield', 'enemy_no_hp_damage_at_attempt_by_player'],
     'enemy_hp_damaged_by_projectile_by_player': ['wt23_hunters_vo_shooting_at_wt_shield', 'enemy_no_hp_damage_at_attempt_by_player'],
     'enemy_hp_damaged_by_explosion_at_direct_hit_by_player': ['wt23_hunters_vo_shooting_at_wt_shield', 'enemy_no_hp_damage_at_attempt_by_player'],
     'enemy_hp_damaged_by_near_explosion_by_player': ['wt23_hunters_vo_shooting_at_wt_shield', 'enemy_no_hp_damage_at_attempt_by_player'],
     'enemy_ricochet_by_player': ['wt23_hunters_vo_shooting_at_wt_shield', 'enemy_ricochet_by_player']}

    def getSoundStringFromHitFlags(self, enemyVehID, hitFlags, enemiesHitCount):
        sound = super(WTVehicleHitSound, self).getSoundStringFromHitFlags(enemyVehID, hitFlags, enemiesHitCount)
        team = avatar_getter.getPlayerTeam()
        if team != wt_constants.WT_TEAMS.BOSS_TEAM:
            arena = avatar_getter.getArena()
            vehicleInfo = arena.vehicles.get(enemyVehID)
            tags = vehicleInfo['vehicleType'].type.tags
            if wt_constants.WT_TAGS.WT_BOSS in tags:
                publicHealth = arena.arenaInfo.arenaPublicHealth
                soundThresholdPercent = 3
                bossHealthInfo = first([ healthInfo for healthInfo in publicHealth.healthInfoList if healthInfo['vehicleID'] == enemyVehID ])
                if float(bossHealthInfo['health']) / vehicleInfo['maxHealth'] * 100 < soundThresholdPercent:
                    return sound
                wtc = wt_constants
                if wtc.WT_BATTLE_STAGE.getCurrent(arena.arenaInfo) == wtc.WT_BATTLE_STAGE.INVINCIBLE:
                    return self.__getAlternativeSound(sound)
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
