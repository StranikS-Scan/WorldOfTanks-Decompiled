# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/battle_control/controllers/sound_ctrls/wt_battle_sounds.py
from gui.battle_control.controllers.sound_ctrls.common import ShotsResultSoundController
from gui.battle_control import avatar_getter
from constants import VEHICLE_HIT_FLAGS as VHF
from white_tiger_common.wt_constants import WT_TEAMS, WT_BATTLE_STAGE, WT_VEHICLE_TAGS
from white_tiger.cgf_components import wt_helpers

class WTBattleSoundController(ShotsResultSoundController):
    _SHOOTING_AT_SHIELD_NOTIFICATION = 'wt23_hunters_vo_shooting_at_wt_shield'
    _SHOOTING_AT_SHIELD_NOTIFICATION_RICOCHET = 'wt23_hunters_vo_shooting_at_wt_shield_ricochet'
    _DEFAULT_THRESHOLD_PERCENT = 3
    _INSTANT_STUN_SHOT_SKIP_HIT_NOTIFICATIONS = ('enemy_no_hp_damage_at_attempt_and_gun_damaged_by_player', 'enemy_no_hp_damage_at_no_attempt_and_gun_damaged_by_player', 'enemy_no_hp_damage_at_attempt_and_chassis_damaged_by_player', 'enemy_no_hp_damage_at_no_attempt_and_chassis_damaged_by_player', 'enemy_no_piercing_by_player', 'enemy_no_hp_damage_at_attempt_by_player', 'enemy_no_hp_damage_at_no_attempt_by_player', 'enemy_no_hp_damage_by_near_explosion_by_player', 'enemy_ricochet_by_player')
    _INSTANT_STUN_SHOT_SKIP_DAMAGE_HIT_NOTIFICATIONS = ('enemy_hp_damaged_by_projectile_by_player',)
    _ALTERNATIVE_SOUND_NOTIFICATIONS = {'enemy_no_hp_damage_at_attempt_by_player': 'wt23_hunters_vo_shooting_at_wt_shield',
     'enemy_no_hp_damage_at_no_attempt_by_player': 'wt23_hunters_vo_shooting_at_wt_shield',
     'enemy_hp_damaged_by_projectile_and_gun_damaged_by_player': 'wt23_hunters_vo_shooting_at_wt_shield',
     'enemy_hp_damaged_by_projectile_and_chassis_damaged_by_player': 'wt23_hunters_vo_shooting_at_wt_shield',
     'enemy_hp_damaged_by_projectile_by_player': 'wt23_hunters_vo_shooting_at_wt_shield',
     'enemy_hp_damaged_by_explosion_at_direct_hit_by_player': 'wt23_hunters_vo_shooting_at_wt_shield',
     'enemy_hp_damaged_by_near_explosion_by_player': 'wt23_hunters_vo_shooting_at_wt_shield',
     'enemy_ricochet_by_player': 'wt23_hunters_vo_shooting_at_wt_shield_ricochet'}

    def __init__(self):
        super(WTBattleSoundController, self).__init__()
        self._SHOT_RESULT_SOUND_PRIORITIES[self._SHOOTING_AT_SHIELD_NOTIFICATION] = 15
        self._SHOT_RESULT_SOUND_PRIORITIES[self._SHOOTING_AT_SHIELD_NOTIFICATION_RICOCHET] = 14

    def getVehicleHitResultSound(self, enemyVehID, hitFlags, enemiesHitCount):
        sound = super(WTBattleSoundController, self).getVehicleHitResultSound(enemyVehID, hitFlags, enemiesHitCount)
        team = avatar_getter.getPlayerTeam()
        arena = avatar_getter.getArena()
        vehicleInfo = arena.vehicles.get(enemyVehID)
        tags = vehicleInfo['vehicleType'].type.tags
        if team != WT_TEAMS.BOSS_TEAM:
            if WT_VEHICLE_TAGS.BOSS in tags:
                triggerThreshold = self.__getTriggerThreshold(self._SHOOTING_AT_SHIELD_NOTIFICATION)
                if wt_helpers.getBossVehicleHealthPercent() < triggerThreshold:
                    return sound
                if WT_BATTLE_STAGE.getCurrent(arena.arenaInfo) == WT_BATTLE_STAGE.INVINCIBLE:
                    return self.__getAlternativeSound(sound)
            elif hitFlags & VHF.STUN_STARTED and sound in self._INSTANT_STUN_SHOT_SKIP_HIT_NOTIFICATIONS:
                return None
        elif hitFlags & VHF.STUN_STARTED and (sound in self._INSTANT_STUN_SHOT_SKIP_HIT_NOTIFICATIONS or sound in self._INSTANT_STUN_SHOT_SKIP_DAMAGE_HIT_NOTIFICATIONS):
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
