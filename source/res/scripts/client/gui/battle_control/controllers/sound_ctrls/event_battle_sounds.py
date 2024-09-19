# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/sound_ctrls/event_battle_sounds.py
from gui.battle_control.controllers.sound_ctrls.common import ShotsResultSoundController
from gui.battle_control import avatar_getter
from gui.shared.gui_items.Vehicle import VEHICLE_TAGS
from shared_utils import first
from constants import VEHICLE_HIT_FLAGS as VHF, WT_TEAMS, WT_BATTLE_STAGE

class EventBattleSoundController(ShotsResultSoundController):
    _SHOOTING_AT_SHIELD_NOTIFICATION = 'wt23_hunters_vo_shooting_at_wt_shield'
    _SHOOTING_AT_SHIELD_NOTIFICATION_RICOCHET = 'wt23_hunters_vo_shooting_at_wt_shield_ricochet'
    _DEFAULT_THRESHOLD_PERCENT = 3
    _INSTANT_STUN_SHOT_SKIP_HIT_NOTIFICATIONS = ('enemy_no_hp_damage_at_attempt_and_gun_damaged_by_player', 'enemy_no_hp_damage_at_no_attempt_and_gun_damaged_by_player', 'enemy_no_hp_damage_at_attempt_and_chassis_damaged_by_player', 'enemy_no_hp_damage_at_no_attempt_and_chassis_damaged_by_player', 'enemy_no_piercing_by_player', 'enemy_no_hp_damage_at_attempt_by_player', 'enemy_no_hp_damage_at_no_attempt_by_player', 'enemy_no_hp_damage_by_near_explosion_by_player', 'enemy_ricochet_by_player')
    _ALTERNATIVE_SOUND_NOTIFICATIONS = {'enemy_no_hp_damage_at_attempt_by_player': 'wt23_hunters_vo_shooting_at_wt_shield',
     'enemy_no_hp_damage_at_no_attempt_by_player': 'wt23_hunters_vo_shooting_at_wt_shield',
     'enemy_hp_damaged_by_projectile_and_gun_damaged_by_player': 'wt23_hunters_vo_shooting_at_wt_shield',
     'enemy_hp_damaged_by_projectile_and_chassis_damaged_by_player': 'wt23_hunters_vo_shooting_at_wt_shield',
     'enemy_hp_damaged_by_projectile_by_player': 'wt23_hunters_vo_shooting_at_wt_shield',
     'enemy_hp_damaged_by_explosion_at_direct_hit_by_player': 'wt23_hunters_vo_shooting_at_wt_shield',
     'enemy_hp_damaged_by_near_explosion_by_player': 'wt23_hunters_vo_shooting_at_wt_shield',
     'enemy_ricochet_by_player': 'wt23_hunters_vo_shooting_at_wt_shield_ricochet'}

    def __init__(self):
        super(EventBattleSoundController, self).__init__()
        self._SHOT_RESULT_SOUND_PRIORITIES[self._SHOOTING_AT_SHIELD_NOTIFICATION] = 15
        self._SHOT_RESULT_SOUND_PRIORITIES[self._SHOOTING_AT_SHIELD_NOTIFICATION_RICOCHET] = 14

    def getVehicleHitResultSound(self, enemyVehID, hitFlags, enemiesHitCount):
        sound = super(EventBattleSoundController, self).getVehicleHitResultSound(enemyVehID, hitFlags, enemiesHitCount)
        team = avatar_getter.getPlayerTeam()
        arena = avatar_getter.getArena()
        vehicleInfo = arena.vehicles.get(enemyVehID)
        tags = vehicleInfo['vehicleType'].type.tags
        if team != WT_TEAMS.BOSS_TEAM:
            if VEHICLE_TAGS.EVENT_BOSS in tags:
                publicHealth = arena.arenaInfo.arenaPublicHealth
                bossHealthInfo = first([ healthInfo for healthInfo in publicHealth.healthInfoList if healthInfo['vehicleID'] == enemyVehID ])
                triggerThreshold = self.__getTriggerThreshold(self._SHOOTING_AT_SHIELD_NOTIFICATION)
                if float(bossHealthInfo['health']) / vehicleInfo['maxHealth'] * 100 < triggerThreshold:
                    return sound
                if WT_BATTLE_STAGE.getCurrent(arena.arenaInfo) == WT_BATTLE_STAGE.INVINCIBLE:
                    return self.__getAlternativeSound(sound)
            elif hitFlags & VHF.STUN_STARTED and sound in self._INSTANT_STUN_SHOT_SKIP_HIT_NOTIFICATIONS:
                return None
        return sound

    def __getAlternativeSound(self, sound):
        altNotification = self._ALTERNATIVE_SOUND_NOTIFICATIONS.get(sound, None)
        return sound if not altNotification else altNotification

    def __getTriggerThreshold(self, notification):
        soundNotifications = avatar_getter.getSoundNotifications()
        if soundNotifications:
            value = soundNotifications.getEventInfo(notification, 'triggerThreshold')
            if value:
                return int(value)
        return self._DEFAULT_THRESHOLD_PERCENT
