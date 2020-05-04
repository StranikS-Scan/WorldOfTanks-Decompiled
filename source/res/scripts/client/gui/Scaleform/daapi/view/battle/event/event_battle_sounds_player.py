# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/event_battle_sounds_player.py
import time
import WWISE
import SoundGroups
from PlayerEvents import g_playerEvents
from gui.battle_control import avatar_getter
from gui.battle_control.battle_constants import FEEDBACK_EVENT_ID
from gui.battle_control.controllers.period_ctrl import IAbstractPeriodView
from gui.battle_control.view_components import IViewComponentsCtrlListener
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from constants import ARENA_PERIOD, ATTACK_REASON, ATTACK_REASONS

class EventArenaStatePlayer(IAbstractPeriodView, IViewComponentsCtrlListener):
    _EVENT_GAMEPLAY_STATE_GROUP = 'STATE_ev_2020_secret_event_gameplay'
    _EVENT_GAMEPLAY_ACTIVE_STATE = 'STATE_ev_2020_secret_event_gameplay_on'
    _EVENT_GAMEPLAY_INACTIVE_STATE = 'STATE_ev_2020_secret_event_gameplay_off'

    def __init__(self):
        self.__isActive = False

    def setPeriod(self, period):
        if period in (ARENA_PERIOD.WAITING, ARENA_PERIOD.PREBATTLE, ARENA_PERIOD.BATTLE):
            self.__activateEventGameplayState()
        elif period == ARENA_PERIOD.AFTERBATTLE:
            self.__deactivateEventGameplayState()

    def detachedFromCtrl(self, ctrlID):
        self.__deactivateEventGameplayState()

    def __activateEventGameplayState(self):
        if not self.__isActive:
            WWISE.WW_setState(self._EVENT_GAMEPLAY_STATE_GROUP, self._EVENT_GAMEPLAY_ACTIVE_STATE)
            self.__isActive = True

    def __deactivateEventGameplayState(self):
        if self.__isActive:
            WWISE.WW_setState(self._EVENT_GAMEPLAY_STATE_GROUP, self._EVENT_GAMEPLAY_INACTIVE_STATE)
            self.__isActive = False


class VehicleDestroyedSoundPlayer(IAbstractPeriodView):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)
    _VEHICLE_DESTROYED_NOTIFICATION = 'se20_vehicle_destroyed'

    def __init__(self):
        self.__initialized = False
        super(VehicleDestroyedSoundPlayer, self).__init__()

    def setPeriod(self, period):
        if period == ARENA_PERIOD.BATTLE:
            self.__initialize()
        elif period == ARENA_PERIOD.AFTERBATTLE:
            self.__finalize()

    def __initialize(self):
        self.__initialized = True
        respawnCtrl = self.sessionProvider.dynamic.respawn
        if respawnCtrl is not None:
            respawnCtrl.onRespawnInfoUpdated += self.__onRespawnInfoUpdated
        return

    def __finalize(self):
        self.__initialized = False
        respawnCtrl = self.sessionProvider.dynamic.respawn
        if respawnCtrl is not None:
            respawnCtrl.onRespawnInfoUpdated -= self.__onRespawnInfoUpdated
        return

    def __onRespawnInfoUpdated(self, respawnInfo):
        avatar_getter.getSoundNotifications().play(self._VEHICLE_DESTROYED_NOTIFICATION)


class EnemyDamageSoundPlayer(IAbstractPeriodView):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)
    _ATTACK_REASONS_TO_NOTIFY = (ATTACK_REASON.BOMBERS,
     ATTACK_REASON.BOMBER_EQ,
     ATTACK_REASON.ARTILLERY_EQ,
     ATTACK_REASON.MINEFIELD_EQ)
    _MIN_DAMAGE_TO_NOTIFY = 700
    _MAX_TIME_TO_AGGREGATE_DAMAGE = 2
    _ENEMY_ABILITY_DAMAGE_NOTIFICATION = 'se20_enemy_ability_damage'
    _ENEMY_ABILITY_DAMAGE_AMOUNT = 100
    _ENEMY_ON_FIRE_NOTIFICATION = 'se20_enemy_on_fire'

    def __init__(self):
        self.__initialized = False
        self.__abilityDamageEvents = []
        super(EnemyDamageSoundPlayer, self).__init__()

    def setPeriod(self, period):
        if period == ARENA_PERIOD.BATTLE:
            self.__initialize()
        elif period == ARENA_PERIOD.AFTERBATTLE:
            self.__finalize()

    def __initialize(self):
        self.__initialized = True
        ctrl = self.sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onVehicleFeedbackReceived += self.__onVehicleFeedbackReceived
            ctrl.onPlayerFeedbackReceived += self.__onPlayerFeedbackReceived
        return

    def __finalize(self):
        self.__initialized = False
        ctrl = self.sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onVehicleFeedbackReceived -= self.__onVehicleFeedbackReceived
            ctrl.onPlayerFeedbackReceived -= self.__onPlayerFeedbackReceived
        return

    def __onVehicleFeedbackReceived(self, eventID, vehicleID, value):
        if eventID != FEEDBACK_EVENT_ID.VEHICLE_HEALTH:
            return
        else:
            attackerInfo, attackReasonID = value[1], value[2]
            if attackerInfo is None or attackerInfo.vehicleID != avatar_getter.getPlayerVehicleID():
                return
            if attackReasonID == ATTACK_REASON.getIndex(ATTACK_REASON.FIRE):
                avatar_getter.getSoundNotifications().play(self._ENEMY_ON_FIRE_NOTIFICATION)
            return

    def __onPlayerFeedbackReceived(self, playerFeedbackEvents):
        for event in playerFeedbackEvents:
            if event.getType() == FEEDBACK_EVENT_ID.PLAYER_DAMAGED_HP_ENEMY:
                self.__onPlayerDamagedEnemy(event.getExtra().getAttackReasonID(), event.getExtra().getDamage())

    def __onPlayerDamagedEnemy(self, attackReasonID, damage):
        attackReason = ATTACK_REASONS[attackReasonID]
        timestampNow = time.time()
        if attackReason in self._ATTACK_REASONS_TO_NOTIFY:
            self.__abilityDamageEvents.append((timestampNow, damage))
        self.__abilityDamageEvents = [ (timestamp, damage) for timestamp, damage in self.__abilityDamageEvents if timestampNow - timestamp <= self._MAX_TIME_TO_AGGREGATE_DAMAGE ]
        if sum((t[1] for t in self.__abilityDamageEvents)) >= self._MIN_DAMAGE_TO_NOTIFY:
            avatar_getter.getSoundNotifications().play(self._ENEMY_ABILITY_DAMAGE_NOTIFICATION)
            self.__abilityDamageEvents = []


class FinishSoundPlayer(IAbstractPeriodView, IViewComponentsCtrlListener):
    _ENDBATTLE_SOUND = 'end_battle_last_kill'

    def __init__(self):
        super(FinishSoundPlayer, self).__init__()
        self.__isActive = False
        self.__arenaPeriod = None
        return

    def detachedFromCtrl(self, ctrlID):
        g_playerEvents.onRoundFinished -= self.__onRoundFinished
        self.__isActive = False

    def setPeriod(self, period):
        if not self.__isActive and period == ARENA_PERIOD.BATTLE:
            g_playerEvents.onRoundFinished += self.__onRoundFinished
            self.__isActive = True
        elif self.__isActive and period == ARENA_PERIOD.AFTERBATTLE:
            g_playerEvents.onRoundFinished -= self.__onRoundFinished
            self.__isActive = False

    def __onRoundFinished(self, winningTeam, reason):
        SoundGroups.g_instance.playSound2D(self._ENDBATTLE_SOUND)
