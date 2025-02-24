# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: cosmic_event/scripts/client/cosmic_sound.py
import WWISE
from typing import TYPE_CHECKING
from debug_utils import LOG_ERROR

def play2DSoundEvent(name):
    import SoundGroups
    return SoundGroups.g_instance.playSound2D(name)


def play3DSoundEvent(name, point):
    import SoundGroups
    return SoundGroups.g_instance.playSoundPos(name, point)


def playVoiceover(eventName):
    from gui.battle_control import avatar_getter
    soundNotifications = avatar_getter.getSoundNotifications()
    if soundNotifications:
        soundNotifications.play(eventName)
    else:
        LOG_ERROR('[COSMIC] Error on playing voiceover event {}'.format(eventName))


if TYPE_CHECKING:
    from Math import Vector3

class CosmicHangarSounds(object):
    _COSMIC_PRB_ENTER = 'ev_cosmic_lobby_enter'
    _COSMIC_PRB_EXIT = 'ev_cosmic_lobby_exit'
    _COSMIC_BATTLE_RESULTS = 'ev_cosmic_music_pbs'

    @classmethod
    def playCosmicPrbEnter(cls):
        play2DSoundEvent(cls._COSMIC_PRB_ENTER)

    @classmethod
    def playCosmicPrbExit(cls):
        play2DSoundEvent(cls._COSMIC_PRB_EXIT)

    @classmethod
    def playCosmicBattleResultsEnter(cls):
        play2DSoundEvent(cls._COSMIC_BATTLE_RESULTS)

    class CosmicProgression(object):
        COSMIC_RTPC_PROGRESSION = 'RTPC_ext_cosmic_lobby_progress'
        _COSMIC_PROGRESSION_STAGES = ('ev_cosmic_vo_lobby_progression_0_1', 'ev_cosmic_vo_lobby_progression_1_2', 'ev_cosmic_vo_lobby_progression_2_3', 'ev_cosmic_vo_lobby_progression_3_4', 'ev_cosmic_vo_lobby_progression_4_5', 'ev_cosmic_vo_lobby_progression_5_6', 'ev_cosmic_vo_lobby_progression_6_7', 'ev_cosmic_vo_lobby_progression_7_8', 'ev_cosmic_vo_lobby_progression_8_9', 'ev_cosmic_vo_lobby_progression_9_10', 'ev_cosmic_vo_lobby_progression_completed')
        _COSMIC_PROGRESSION_AMBIENT_START = 'ev_cosmic_hangar_object_drone'
        _COSMIC_PROGRESSION_AMBIENT_STOP = 'ev_cosmic_hangar_object_drone_stop'

        @classmethod
        def getSoundObject(cls, currentStage):
            import SoundGroups
            if not 0 <= currentStage < len(cls._COSMIC_PROGRESSION_STAGES):
                LOG_ERROR('[COSMIC_SOUND] Incorrect stage of cosmic progression when getting sound object')
                return
            else:
                return SoundGroups.g_instance.getSound2D(cls._COSMIC_PROGRESSION_STAGES[currentStage])

        @classmethod
        def playAmbient(cls):
            play2DSoundEvent(cls._COSMIC_PROGRESSION_AMBIENT_START)

        @classmethod
        def stopAmbient(cls):
            play2DSoundEvent(cls._COSMIC_PROGRESSION_AMBIENT_STOP)


class CosmicBattleSounds(object):
    START_BATTLE = 'ev_cosmic_vo_gameplay_start_battle'
    ENEMY_KILLED_VOICE = 'ev_cosmic_vo_gameplay_enemy_destroyed'
    FIRST_BLOOD = 'ev_cosmic_vo_gameplay_first_blood'
    REVENGE = 'ev_cosmic_vo_gameplay_enemy_destroyed_revenge'
    PLAYER_RESPAWN = 'ev_cosmic_vo_gameplay_respawn'
    _SCORE_NOTIFICATION = 'ev_cosmic_score_notification'
    _SPECIAL_HINT = 'ev_cosmic_special_hint'
    _KILL_STREAK_NOTIFICATION = {2: 'ev_cosmic_x2_kill_hint',
     3: 'ev_cosmic_x3_kill_hint',
     4: 'ev_cosmic_x4_kill_hint'}
    _ABILITY_PICK_UP_NOTIFICATION = 'ev_cosmic_pickup_notification'
    _ENEMY_KILLED_NOTIFICATION = 'ev_cosmic_enemy_killed'
    _ABILITY_PICK_UP = 'ev_cosmic_ability_pickup'
    _ABILITY_PICK_UP_MUSIC = 'ev_cosmic_music_pickup'
    _BATTLE_PERIOD_MUSIC = 'ev_cosmic_music_start_battle'
    _AFTERBATTLE_PERIOD_MUSIC = 'ev_cosmic_music_end_battle'
    _RAMMING = 'ev_cosmic_tank_ram'
    _DRON_APPEAR_3D = 'ev_cosmic_ability_drone_appear'
    _DRON_DISAPPEAR_3D = 'ev_cosmic_ability_drone_disappear'
    _BOARD_JUMP_3D = 'ev_cosmic_booster_jump'
    _GEYSER_SPLASH_3D = 'ev_cosmic_geyser_big'
    _CHEERUP_VOICE_FOR_SECOND_PHASE = ('ev_cosmic_vo_gameplay_cheerup2_high_place',)
    _AFTER_BATTLE_RESULTS_VOICES = ('ev_cosmic_vo_gameplay_finish_battle_first_place', 'ev_cosmic_vo_gameplay_finish_battle_other_place')

    class ScanningZone(object):
        SCANNING_ZONE_PREPARING = 'ev_cosmic_vo_gameplay_scan_prepare'
        SCANNING_ZONE_FINAL_PREPARING = 'ev_cosmic_vo_gameplay_scan_prepare_final'
        _STATE_GROUP = 'STATE_ev_cosmic_object'
        _ACTIVE_STATE_VAL = 'STATE_ev_cosmic_object_active_on'
        _INACTIVE_STATE_VAL = 'STATE_ev_cosmic_object_active_off'
        _FINAL_CYCLE = 'ev_cosmic_coda'
        _SCANNING_ZONE_ACTIVE = 'ev_cosmic_music_object_active'
        _SCANNING_ZONE_INACTIVE = 'ev_cosmic_music_object_inactive'

        @classmethod
        def setActive(cls, isLast):
            WWISE.WW_setState(cls._STATE_GROUP, cls._ACTIVE_STATE_VAL)
            if isLast:
                play2DSoundEvent(cls._FINAL_CYCLE)
            else:
                play2DSoundEvent(cls._SCANNING_ZONE_ACTIVE)

        @classmethod
        def setInactive(cls, isLast):
            cls.switchInactiveState()
            if not isLast:
                play2DSoundEvent(cls._SCANNING_ZONE_INACTIVE)

        @classmethod
        def switchInactiveState(cls):
            WWISE.WW_setState(cls._STATE_GROUP, cls._INACTIVE_STATE_VAL)

    class Announcements(object):
        PICK_UP_ANNOUNCE_START = 'ev_cosmic_ability_announce'
        PICK_UP_ANNOUNCE_END = 'ev_cosmic_ability_appear'
        ABILITIES_SPAWNED = 'ev_cosmic_vo_gameplay_booster_spawn'
        _STEP = 'ev_cosmic_timer_1shot'
        FINISHED = 'ev_cosmic_timer_last'

        @classmethod
        def playStep(cls):
            play2DSoundEvent(cls._STEP)

        @classmethod
        def playFinish(cls):
            play2DSoundEvent(cls.FINISHED)

    class Abilities(object):
        _NOT_READY = 'ev_cosmic_ability_not_ready'
        _ACTIVATED = 'ev_cosmic_ability_apply'
        _BOOSTER_ACTIVATED = 'ev_cosmic_ability_booster'
        _HOOK_SHOT_ACTIVATED = 'ev_cosmic_ability_overcharge_shot_start'
        _HOOK_SHOT_ELAPSED = 'ev_cosmic_ability_overcharge_shot_stop'
        _BLACK_HOLE_ACTIVATED = 'ev_cosmic_ability_supernova_charge'
        _BLACK_HOLE_CANCELED = 'ev_cosmic_ability_supernova_cancel'
        _RESPAWN_PROTECTION_ACTIVATED = 'ev_cosmic_ability_respawn_protection_start'
        _RESPAWN_PROTECTION_ELAPSED = 'ev_cosmic_ability_respawn_protection_stop'
        _POWER_SHOT_ACTIVATED = 'ev_cosmic_ability_superShot_start'
        _POWER_SHOT_ELAPSED = 'ev_cosmic_ability_superShot_stop'
        _STUN_SHOT_ACTIVATED = 'ev_cosmic_ability_superShot_start'
        _STUN_SHOT_ELAPSED = 'ev_cosmic_ability_superShot_stop'

        @classmethod
        def playActivated(cls):
            play2DSoundEvent(cls._ACTIVATED)

        @classmethod
        def playNotReady(cls):
            play2DSoundEvent(cls._NOT_READY)

        @classmethod
        def playBoosterActivated(cls):
            play2DSoundEvent(cls._BOOSTER_ACTIVATED)

        @classmethod
        def playHookShotActivated(cls):
            play2DSoundEvent(cls._HOOK_SHOT_ACTIVATED)

        @classmethod
        def playHookShotElapsed(cls):
            play2DSoundEvent(cls._HOOK_SHOT_ELAPSED)

        @classmethod
        def blackHoleActivated(cls, reset):
            if reset:
                play2DSoundEvent(cls._BLACK_HOLE_CANCELED)
            else:
                play2DSoundEvent(cls._BLACK_HOLE_ACTIVATED)

        @classmethod
        def playRespawnProtectionActivated(cls):
            play2DSoundEvent(cls._RESPAWN_PROTECTION_ACTIVATED)

        @classmethod
        def playRespawnProtectionElapsed(cls):
            play2DSoundEvent(cls._RESPAWN_PROTECTION_ELAPSED)

        @classmethod
        def playPowerShotActivated(cls):
            play2DSoundEvent(cls._POWER_SHOT_ACTIVATED)

        @classmethod
        def playPowerShotElapsed(cls):
            play2DSoundEvent(cls._POWER_SHOT_ELAPSED)

        @classmethod
        def playStunShotActivated(cls):
            play2DSoundEvent(cls._STUN_SHOT_ACTIVATED)

        @classmethod
        def playStunShotElapsed(cls):
            play2DSoundEvent(cls._STUN_SHOT_ELAPSED)

    @classmethod
    def playScoreNotification(cls):
        play2DSoundEvent(cls._SCORE_NOTIFICATION)

    @classmethod
    def playSpecialHint(cls):
        play2DSoundEvent(cls._SPECIAL_HINT)

    @classmethod
    def playKillStreak(cls, killStreak):
        if killStreak > 1:
            event = cls._KILL_STREAK_NOTIFICATION.get(killStreak, 'ev_cosmic_x4_kill_hint')
            play2DSoundEvent(event)

    @classmethod
    def playAbilityPickup(cls):
        play2DSoundEvent(cls._ABILITY_PICK_UP_NOTIFICATION)
        play2DSoundEvent(cls._ABILITY_PICK_UP_MUSIC)
        play2DSoundEvent(cls._ABILITY_PICK_UP)

    @classmethod
    def playEnemyKilled(cls):
        play2DSoundEvent(cls._ENEMY_KILLED_NOTIFICATION)

    @classmethod
    def startBattlePeriodMusic(cls):
        play2DSoundEvent(cls._BATTLE_PERIOD_MUSIC)

    @classmethod
    def startAfterBattlePeriodMusic(cls):
        play2DSoundEvent(cls._AFTERBATTLE_PERIOD_MUSIC)

    @classmethod
    def playCheerupVoiceForSecondPhase(cls, playerPositionInRankedTable):
        cls.__playCheerupVoice(playerPositionInRankedTable, cls._CHEERUP_VOICE_FOR_SECOND_PHASE)

    @classmethod
    def __playCheerupVoice(cls, playerPositionInRankedTable, cheerupVoices):
        if 1 <= playerPositionInRankedTable <= 3:
            playVoiceover(cheerupVoices[0])

    @classmethod
    def playAfterBattleResultVoice(cls, playerPositionInRankedTable):
        if playerPositionInRankedTable == 1:
            playVoiceover(cls._AFTER_BATTLE_RESULTS_VOICES[0])
        elif playerPositionInRankedTable > 1:
            playVoiceover(cls._AFTER_BATTLE_RESULTS_VOICES[1])

    @classmethod
    def playRammingSound(cls, point):
        play3DSoundEvent(cls._RAMMING, point)

    @classmethod
    def playDronAppear(cls, point):
        play3DSoundEvent(cls._DRON_APPEAR_3D, point)

    @classmethod
    def playDronDisappear(cls, point):
        play3DSoundEvent(cls._DRON_DISAPPEAR_3D, point)

    @classmethod
    def playBoardJump(cls, point):
        play3DSoundEvent(cls._BOARD_JUMP_3D, point)

    @classmethod
    def playGeyserSplash(cls, point):
        play3DSoundEvent(cls._GEYSER_SPLASH_3D, point)
