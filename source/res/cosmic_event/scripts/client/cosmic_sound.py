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
        _COSMIC_PROGRESSION_STAGES = ('ev_cosmic_vo_lobby_progression_0_1', 'ev_cosmic_vo_lobby_progression_1_2', 'ev_cosmic_vo_lobby_progression_2_3', 'ev_cosmic_vo_lobby_progression_3_4', 'ev_cosmic_vo_lobby_progression_4_5', 'ev_cosmic_vo_lobby_progression_5_6', 'ev_cosmic_vo_lobby_progression_6_7', 'ev_cosmic_vo_lobby_progression_7_8', 'ev_cosmic_vo_lobby_progression_8_9', 'ev_cosmic_vo_lobby_progression_9_10', 'ev_cosmic_vo_lobby_progression_completed')

        @classmethod
        def getSoundObject(cls, currentStage):
            import SoundGroups
            if not 0 <= currentStage < len(cls._COSMIC_PROGRESSION_STAGES):
                LOG_ERROR('[COSMIC_SOUND] Incorrect stage of cosmic progression when getting sound object')
                return
            else:
                return SoundGroups.g_instance.getSound2D(cls._COSMIC_PROGRESSION_STAGES[currentStage])


class CosmicBattleSounds(object):
    START_BATTLE = 'ev_cosmic_vo_gameplay_start_battle'
    ABILITY_PICK_UP_VOICE = 'ev_cosmic_vo_gameplay_booster'
    ENEMY_KILLED_VOICE = 'ev_cosmic_vo_gameplay_enemy_destroyed'
    PLAYER_RESPAWN = 'ev_cosmic_vo_gameplay_respawn'
    _SCORE_NOTIFICATION = 'ev_cosmic_score_notification'
    _ABILITY_PICK_UP_NOTIFICATION = 'ev_cosmic_pickup_notification'
    _ENEMY_KILLED_NOTIFICATION = 'ev_cosmic_enemy_killed'
    _ABILITY_PICK_UP = 'ev_cosmic_ability_pickup'
    _ABILITY_PICK_UP_MUSIC = 'ev_cosmic_music_pickup'
    _BATTLE_PERIOD_MUSIC = 'ev_cosmic_music_start_battle'
    _AFTERBATTLE_PERIOD_MUSIC = 'ev_cosmic_music_end_battle'
    _RAMMING = 'ev_cosmic_tank_ram'
    _CHEERUP_VOICE_FOR_FIRST_PHASE = ('ev_cosmic_vo_gameplay_cheerup1_high_place', 'ev_cosmic_vo_gameplay_cheerup1_medium_place', 'ev_cosmic_vo_gameplay_cheerup1_low_place')
    _CHEERUP_VOICE_FOR_SECOND_PHASE = ('ev_cosmic_vo_gameplay_cheerup2_high_place', 'ev_cosmic_vo_gameplay_cheerup2_medium_place', 'ev_cosmic_vo_gameplay_cheerup2_low_place')
    _AFTER_BATTLE_RESULTS_VOICES = ('ev_cosmic_vo_gameplay_finish_battle_first_place', 'ev_cosmic_vo_gameplay_finish_battle_second_third_place', 'ev_cosmic_vo_gameplay_finish_battle_medium_place', 'ev_cosmic_vo_gameplay_finish_battle_low_place')

    class ScanningZone(object):
        SCANNING_ZONE_PREPARING = 'ev_cosmic_vo_gameplay_scan_prepare'
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
    def playScoreNotification(cls):
        play2DSoundEvent(cls._SCORE_NOTIFICATION)

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
    def playCheerupVoiceForFirstPhase(cls, playerPositionInRankedTable):
        cls.__playCheerupVoice(playerPositionInRankedTable, cls._CHEERUP_VOICE_FOR_FIRST_PHASE)

    @classmethod
    def playCheerupVoiceForSecondPhase(cls, playerPositionInRankedTable):
        cls.__playCheerupVoice(playerPositionInRankedTable, cls._CHEERUP_VOICE_FOR_SECOND_PHASE)

    @classmethod
    def __playCheerupVoice(cls, playerPositionInRankedTable, cheerupVoices):
        if 1 <= playerPositionInRankedTable <= 3:
            playVoiceover(cheerupVoices[0])
        elif 3 < playerPositionInRankedTable <= 7:
            playVoiceover(cheerupVoices[1])
        elif playerPositionInRankedTable > 7:
            playVoiceover(cheerupVoices[2])

    @classmethod
    def playAfterBattleResultVoice(cls, playerPositionInRankedTable):
        if playerPositionInRankedTable == 1:
            playVoiceover(cls._AFTER_BATTLE_RESULTS_VOICES[0])
        elif 1 < playerPositionInRankedTable <= 3:
            playVoiceover(cls._AFTER_BATTLE_RESULTS_VOICES[1])
        elif 3 < playerPositionInRankedTable <= 7:
            playVoiceover(cls._AFTER_BATTLE_RESULTS_VOICES[2])
        elif playerPositionInRankedTable > 7:
            playVoiceover(cls._AFTER_BATTLE_RESULTS_VOICES[3])

    @classmethod
    def playRammingSound(cls, point):
        play3DSoundEvent(cls._RAMMING, point)
