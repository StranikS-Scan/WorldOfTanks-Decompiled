# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/event_battle_sounds_player.py
import BigWorld
import SoundGroups
import WWISE
from PlayerEvents import g_playerEvents
from constants import ARENA_PERIOD, LootAction, CURRENT_REALM
from gui.Scaleform.daapi.view.battle.shared.formatters import getHealthPercent
from gui.battle_control import avatar_getter
from gui.battle_control.arena_info.settings import ARENA_LISTENER_SCOPE as _SCOPE
from gui.battle_control.arena_info.interfaces import IArenaVehiclesController
from gui.battle_control.battle_constants import BATTLE_CTRL_ID, VEHICLE_VIEW_STATE
from gui.shared.gui_items.Vehicle import VEHICLE_EVENT_TYPE
from gui.wt_event.wt_event_helpers import LOWER_LIMIT_OF_MEDIUM_LVL, LOWER_LIMIT_OF_HIGH_LVL
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from wt_event.wt_energy_shield import WtEnergyShieldConfig
_RU_REALMS = ('DEV', 'QA', 'RU')
_SWITCH_RU = 'SWITCH_ext_WT_vo_language'
_SWITCH_RU_ON = 'SWITCH_ext_WT_vo_language_RU'
_SWITCH_RU_OFF = 'SWITCH_ext_WT_vo_language_nonRU'

class EventBattleSoundController(IArenaVehiclesController):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)
    _EVENT_GAMEPLAY_ACTIVE_STATE = 'ev_white_tiger_gameplay_enter'
    _EVENT_GAMEPLAY_INACTIVE_STATE = 'ev_white_tiger_gameplay_exit'
    _VEHICLE_SPAWN_NOTIFICATION = 'ev_white_tiger_spawn_T55'
    _PICKUP_LOOT_STARTED = 'ev_white_tiger_gain_energy_start'
    _PICKUP_LOOT_STOPPED = 'ev_white_tiger_gain_energy_stop'
    _EVENT_STUN_START = 'ev_white_tiger_stun_effect_imp_start'
    _EVENT_STUN_END = 'ev_white_tiger_stun_effect_imp_end'
    _RTPC_OBJECT = 'RTPC_ext_white_tiger_object'
    _RTPC_POWER = 'RTPC_ext_white_tiger_power_up'
    _RTPC_STUN = 'RTPC_ext_white_tiger_stun'
    _LOW_HIT_ON_BOSS = 'ev_white_tiger_gameplay_impact_wt_small'
    _MEDIUM_HIT_ON_BOSS = 'ev_white_tiger_gameplay_impact_wt_medium'
    _HIGH_HIT_ON_BOSS = 'ev_white_tiger_gameplay_impact_wt_large'
    _VO_BOSS_LOOT_TAKEN_BY_ENEMY = 'ev_wt_w_vo_loot_taken_by_enemy'
    _VO_HUNTER_LOOT_TAKEN_BY_ENEMY = 'ev_wt_t55a_vo_loot_taken_by_enemy'
    _VO_BOSS_WIN = 'ev_wt_w_vo_win'
    _VO_HUNTER_WIN = 'ev_wt_t55a_vo_win'
    _VO_HUNTER_LOSE = 'ev_wt_krieger_vo_wt_win'
    _MUSIC_START = 'ev_white_tiger_gameplay_music_start'
    _SWITCH_CHAR = 'SWITCH_ext_WT_vo_char'
    _SWITCH_CHAR_FOR_PLAYER = {0: 'SWITCH_ext_WT_vo_char_T55',
     1: 'SWITCH_ext_WT_vo_char_WT'}
    _HUNTER_LIVES_LIMIT = 5
    WT_EVENT_SOUND_BANKS = ('ev_white_tiger_2020_voiceover.pck', 'ev_white_tiger_2020_voiceover.bnk')

    def __init__(self):
        super(EventBattleSoundController, self).__init__()
        self.__isSoundActive = False
        self.__stunActived = False
        self.__isPlayerBoss = False
        self.__bossVehID = None
        self.__maxHealth = 0
        self.__soundPlayed = []
        return

    def startControl(self, *args):
        g_playerEvents.onArenaPeriodChange += self.__onArenaPeriodChange

    def stopControl(self):
        g_playerEvents.onArenaPeriodChange -= self.__onArenaPeriodChange
        self.__finalize()
        self.__deactivateEventGameplaySound()

    def getControllerID(self):
        return BATTLE_CTRL_ID.EVENT_SOUND_CTRL

    def getCtrlScope(self):
        return _SCOPE.LOAD

    def arenaLoadCompleted(self):
        self.__activateEventGameplaySound()
        self.__initialize()

    def playHitOnBoss(self, soundObject):
        if soundObject is not None:
            powerPoints = self.sessionProvider.dynamic.arenaInfo.powerPoints
            if powerPoints < LOWER_LIMIT_OF_MEDIUM_LVL:
                soundObject.play(self._LOW_HIT_ON_BOSS)
            elif powerPoints < LOWER_LIMIT_OF_HIGH_LVL:
                soundObject.play(self._MEDIUM_HIT_ON_BOSS)
            else:
                soundObject.play(self._HIGH_HIT_ON_BOSS)
        return

    def playStartMusic(self):
        if self.__isSoundActive:
            self.__playStartMusic()
            return self._MUSIC_START in self.__soundPlayed
        return False

    def __onArenaPeriodChange(self, period, periodEndTime, periodLength, periodAdditionalInfo):
        if period == ARENA_PERIOD.AFTERBATTLE:
            winStatus = self.sessionProvider.getCtx().getLastArenaWinStatus()
            if winStatus is not None:
                if self.__isPlayerBoss and winStatus.isWin():
                    SoundGroups.g_instance.playSound2D(self._VO_BOSS_WIN)
                elif not self.__isPlayerBoss and winStatus.isWin():
                    SoundGroups.g_instance.playSound2D(self._VO_HUNTER_WIN)
                elif not self.__isPlayerBoss and winStatus.isLose():
                    SoundGroups.g_instance.playSound2D(self._VO_HUNTER_LOSE)
        return

    def __initialize(self):
        respawnCtrl = self.sessionProvider.dynamic.respawn
        if respawnCtrl is not None:
            respawnCtrl.onVehicleDeployed += self.__onVehicleDeployed
        vehicleCtrl = self.sessionProvider.shared.vehicleState
        if vehicleCtrl is not None:
            vehicleCtrl.onVehicleStateUpdated += self.__onVehicleStateUpdated
            vehicleCtrl.onVehicleControlling += self.__onVehicleControlling
            vehicleCtrl.onPostMortemSwitched += self.__onPostMortemSwitched
        arenaInfoCtrl = self.sessionProvider.dynamic.arenaInfo
        if arenaInfoCtrl is not None:
            arenaInfoCtrl.onBossHealthChanged += self.__onBossHealthChanged
            arenaInfoCtrl.onPowerPointsChanged += self.__onPowerPointsChanged
            self.__onPowerPointsChanged(arenaInfoCtrl.powerPoints)
        respawnCtrl = self.sessionProvider.dynamic.respawn
        if respawnCtrl is not None:
            respawnCtrl.onTeammatesRespawnLivesUpdated += self.__onTeammatesRespawnLivesUpdated
        vehicleDescr = avatar_getter.getVehicleTypeDescriptor()
        if vehicleDescr is not None:
            self.__isPlayerBoss = VEHICLE_EVENT_TYPE.EVENT_BOSS in vehicleDescr.type.tags
            self.__maxHealth = vehicleDescr.maxHealth
        arenaDP = self.sessionProvider.getArenaDP()
        if arenaDP is not None:
            for vInfo in arenaDP.getVehiclesInfoIterator():
                if VEHICLE_EVENT_TYPE.EVENT_BOSS in vInfo.vehicleType.tags:
                    self.__bossVehID = vInfo.vehicleID
                    break

        self.__validateBossHealth()
        WWISE.WW_setSwitch(self._SWITCH_CHAR, self._SWITCH_CHAR_FOR_PLAYER[int(self.__isPlayerBoss)])
        WWISE.WW_setRTCPGlobal(self._RTPC_OBJECT, int(self.__isPlayerBoss))
        WWISE.WW_setSwitch(_SWITCH_RU, self.__switchRuValue)
        return

    def __finalize(self):
        respawnCtrl = self.sessionProvider.dynamic.respawn
        if respawnCtrl is not None:
            respawnCtrl.onVehicleDeployed -= self.__onVehicleDeployed
        vehicleCtrl = self.sessionProvider.shared.vehicleState
        if vehicleCtrl is not None:
            vehicleCtrl.onVehicleStateUpdated -= self.__onVehicleStateUpdated
            vehicleCtrl.onVehicleControlling -= self.__onVehicleControlling
            vehicleCtrl.onPostMortemSwitched -= self.__onPostMortemSwitched
        arenaInfoCtrl = self.sessionProvider.dynamic.arenaInfo
        if arenaInfoCtrl is not None:
            arenaInfoCtrl.onPowerPointsChanged -= self.__onPowerPointsChanged
            arenaInfoCtrl.onBossHealthChanged -= self.__onBossHealthChanged
        respawnCtrl = self.sessionProvider.dynamic.respawn
        if respawnCtrl is not None:
            respawnCtrl.onTeammatesRespawnLivesUpdated -= self.__onTeammatesRespawnLivesUpdated
        if self.__stunActived:
            self.__playEndStun()
        return

    def __onVehicleStateUpdated(self, state, value):
        if state == VEHICLE_VIEW_STATE.LOOT:
            _, _, action, _ = value
            if action == LootAction.PICKUP_STARTED:
                self.__playSound(self._PICKUP_LOOT_STARTED)
            else:
                self.__playSound(self._PICKUP_LOOT_STOPPED)
        elif state == VEHICLE_VIEW_STATE.STUN and not self.__isPlayerBoss:
            if value.duration > 0.0:
                WWISE.WW_setRTCPGlobal(self._RTPC_STUN, 100)
                if not self.__stunActived:
                    self.__stunActived = True
                    self.__playSound('ev_wt_t55a_vo_stun_shell')
                    self.__playSound(self._EVENT_STUN_START)
            elif self.__stunActived:
                self.__playEndStun()
        elif state == VEHICLE_VIEW_STATE.HEALTH:
            shieldDescr = WtEnergyShieldConfig.shieldDescriptor()
            if self.__isPlayerBoss and shieldDescr is not None:
                healthPercent = getHealthPercent(value, self.__maxHealth)
                halfHealtShieldhPercantage = 0.5 + shieldDescr.healthPercentage / 2
                if healthPercent <= shieldDescr.healthPercentage:
                    self.__playSoundOnce('ev_wt_w_vo_shield_destroyed')
                    self.__playSoundOnce('ev_white_tiger_force_field_off')
                    self.__playStartMusic()
                elif healthPercent < halfHealtShieldhPercantage:
                    self.__playSoundOnce('ev_wt_w_vo_shield_half')
                elif healthPercent < 0.99:
                    self.__playSoundOnce('ev_wt_w_vo_shield_full')
            elif not self.__isPlayerBoss and value == 0:
                respawnCtrl = self.sessionProvider.dynamic.respawn
                if respawnCtrl is not None:
                    if respawnCtrl.playerLives > 1:
                        self.__playSound('ev_wt_t55a_vo_vehicle_destroyed')
                    else:
                        self.__playSound('ev_wt_t55a_vo_vehicle_dead')
        return

    def __onBossHealthChanged(self, _):
        self.__checkBossHealth()

    def __checkBossHealth(self):
        if self.__bossVehID is not None and not self.__isPlayerBoss:
            shieldDescr = WtEnergyShieldConfig.shieldDescriptor()
            vehicle = BigWorld.entities.get(self.__bossVehID)
            if shieldDescr is not None and vehicle is not None:
                healthPercent = getHealthPercent(vehicle.health, vehicle.maxHealth)
                halfHealtShieldhPercantage = 0.5 + shieldDescr.healthPercentage / 2
                if healthPercent <= shieldDescr.healthPercentage:
                    self.__playSoundOnce('ev_wt_krieger_vo_shield_destroyed')
                    self.__playStartMusic()
                elif healthPercent < halfHealtShieldhPercantage:
                    self.__playSoundOnce('ev_wt_krieger_vo_shield_half')
                elif healthPercent < 0.99:
                    self.__playSoundOnce('ev_wt_krieger_vo_shield_full')
        return

    def __onPostMortemSwitched(self, noRespawnPossible, respawnAvailable):
        if not respawnAvailable:
            avatar_getter.getSoundNotifications().play(self._VEHICLE_SPAWN_NOTIFICATION)

    def __onVehicleControlling(self, vehicle):
        shieldDescr = WtEnergyShieldConfig.shieldDescriptor()
        if self.__isPlayerBoss and shieldDescr is not None:
            healthPercent = getHealthPercent(vehicle.health, self.__maxHealth)
            if healthPercent <= shieldDescr.healthPercentage:
                self.__playSoundOnce('ev_white_tiger_force_field_off')
            else:
                self.__playSoundOnce('ev_white_tiger_force_field_on')
        return

    def __onPowerPointsChanged(self, points):
        WWISE.WW_setRTCPGlobal(self._RTPC_POWER, points)
        if points > 0:
            if self.__isPlayerBoss:
                self.__playSound(self._VO_BOSS_LOOT_TAKEN_BY_ENEMY)
            else:
                self.__playSound(self._VO_HUNTER_LOOT_TAKEN_BY_ENEMY)
        if self.sessionProvider.dynamic.arenaInfo.maxPowerPoints == points:
            self.__playStartMusic()

    def __activateEventGameplaySound(self):
        if not self.__isSoundActive:
            WWISE.WW_eventGlobal(self._EVENT_GAMEPLAY_ACTIVE_STATE)
            self.__isSoundActive = True

    def __deactivateEventGameplaySound(self):
        if self.__isSoundActive:
            WWISE.WW_eventGlobal(self._EVENT_GAMEPLAY_INACTIVE_STATE)
            self.__isSoundActive = False

    def __onVehicleDeployed(self):
        self.__playSound(self._VEHICLE_SPAWN_NOTIFICATION)

    def __onTeammatesRespawnLivesUpdated(self, lives):
        livesCount = 0
        for _, vehLives in lives.iteritems():
            livesCount += vehLives

        if livesCount <= self._HUNTER_LIVES_LIMIT:
            self.__playStartMusic()

    def __playSoundOnce(self, sound):
        if sound not in self.__soundPlayed and self.__playSound(sound):
            self.__soundPlayed.append(sound)

    def __playEndStun(self):
        WWISE.WW_setRTCPGlobal(self._RTPC_STUN, 0)
        self.__stunActived = False
        WWISE.WW_eventGlobal(self._EVENT_STUN_END)

    def __playStartMusic(self):
        arena = avatar_getter.getArena()
        if self._MUSIC_START not in self.__soundPlayed and arena is not None and arena.period == ARENA_PERIOD.BATTLE:
            WWISE.WW_eventGlobal(self._MUSIC_START)
            self.__soundPlayed.append(self._MUSIC_START)
        return

    def __validateBossHealth(self):
        if self.__bossVehID is not None and not self.__isPlayerBoss:
            shieldDescr = WtEnergyShieldConfig.shieldDescriptor()
            vehicle = BigWorld.entities.get(self.__bossVehID)
            if shieldDescr is not None and vehicle is not None:
                healthPercent = getHealthPercent(vehicle.health, vehicle.maxHealth)
                halfHealtShieldhPercantage = 0.5 + shieldDescr.healthPercentage / 2
                if healthPercent <= shieldDescr.healthPercentage:
                    self.__soundPlayed.append('ev_wt_krieger_vo_shield_destroyed')
                    self.__soundPlayed.append('ev_wt_w_vo_shield_destroyed')
                    self.__playStartMusic()
                if healthPercent < halfHealtShieldhPercantage:
                    self.__soundPlayed.append('ev_wt_krieger_vo_shield_half')
                    self.__soundPlayed.append('ev_wt_w_vo_shield_half')
                if healthPercent < 0.99:
                    self.__soundPlayed.append('ev_wt_krieger_vo_shield_full')
                    self.__soundPlayed.append('ev_wt_w_vo_shield_full')
        return

    @property
    def __isRuRealm(self):
        return CURRENT_REALM in _RU_REALMS

    @property
    def __switchRuValue(self):
        return _SWITCH_RU_ON if self.__isRuRealm else _SWITCH_RU_OFF

    @classmethod
    def __playSound(cls, eventName):
        soundNotifications = avatar_getter.getSoundNotifications()
        if soundNotifications and hasattr(soundNotifications, 'play'):
            soundNotifications.play(eventName)
            return True
        return False
