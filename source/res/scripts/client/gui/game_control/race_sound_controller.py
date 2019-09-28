# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/race_sound_controller.py
import WWISE
import BigWorld
from math_utils import clamp
from helpers import dependency
from constants import ARENA_PERIOD, CURRENT_REALM, EQUIPMENT_STAGES
from skeletons.gui.battle_session import IBattleSessionProvider
from skeletons.gui.game_control import IRacingEventController
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE
from PlayerEvents import g_playerEvents
from vehicle_systems.tankStructure import TankSoundObjectsIndexes

class Callback(object):
    __slots__ = ('__time', '__callback', '__called', '__repeat')

    def __init__(self, callback, repeat=False, time=-1):
        self.__time = time
        self.__callback = callback
        self.__called = False
        self.__repeat = repeat

    def destroy(self):
        self.__callback = None
        return

    def invoke(self):
        if self.__repeat or not self.__called:
            self.__called = True
            self.__callback()

    def invokeByTime(self, timeleft):
        if (self.__repeat or not self.__called) and timeleft <= self.__time:
            self.__called = True
            self.__callback()


class RaceSoundController(object):
    RACE_RTPC_ELECTRIC = 'RTPC_ev_race_electric'
    RACE_RTPC_FLYING_GLOBAL = 'RTPC_ext_flying_global'
    STATE_RACE_GAMEPLAY = 'STATE_RACE_gameplay'
    STATE_RACE_GAMEPLAY_ON = 'STATE_RACE_gameplay_on'
    STATE_RACE_GAMEPLAY_OFF = 'STATE_RACE_gameplay_off'
    LOW_PRESTART_NOTIFICATION_TIME = 10
    HIGH_PRESTART_NOTIFICATION_TIME = 5
    SOUND_NTF_PRESTART = 'event_race_vo_pre_start'
    SOUND_NTF_ONSTART = 'event_race_vo_start'
    SOUND_NTF_ONREPAIR = 'event_race_vo_tank_repair'
    SOUND_NTF_ONCAPTURING_BASE = 'event_race_vo_neutral_zone_enter'
    SOUND_NTF_WIN = 'event_race_vo_victory'
    SOUND_NTF_LOSE = 'event_race_vo_defeat'
    SOUND_NTF_DRAW = 'event_race_vo_draw'
    EVENT_RACE_MUSIC = 'ev_race_music_gameplay'
    EVENT_RACE_PRE_START = 'ev_race_pre_start'
    EVENT_RACE_START = 'ev_race_start'
    EVENT_RACE_TANK_REPAIR = 'ev_race_tank_repair'
    EVENT_RACE_LOADING = 'ev_race_setting_set'
    EVENT_RACE_EXIT = 'ev_race_setting_reset'
    EVENTS_TO_BASE_POINTS = {'ev_race_neutral_zone_progress_0': (1, 49),
     'ev_race_neutral_zone_progress_50': (50, 79),
     'ev_race_neutral_zone_progress_80': (80, 100)}
    EVENT_SPEED_BOOST_READY = 'ev_race_afterburner_ready'
    SWITCHER = 'SWITCH_ext_ev_race_speaker'
    REAL_TO_SWITCH = 'SWITCH_ext_ev_race_speaker_ru' if CURRENT_REALM == 'RU' else 'SWITCH_ext_ev_race_speaker_eng'
    _sessionProvider = dependency.descriptor(IBattleSessionProvider)
    _racingEventController = dependency.descriptor(IRacingEventController)

    def __init__(self):
        self.__prevArenaPeriod = -1
        self.__vehicleMaxSpeed = None
        self.__firstTimeZoneEntered = False
        self.__countdownCallbacks = [Callback(self.__onLowPrestartNotification, time=self.LOW_PRESTART_NOTIFICATION_TIME)]
        self.__lastCapturingEvent = None
        self.__afterBattleSoundsCallback = Callback(self.__initSoundsOnArenaAfterBattle)
        self.__arenaPeriodHandlers = [(ARENA_PERIOD.WAITING, None, Callback(self.__initSoundsOnArenaWating)),
         (ARENA_PERIOD.PREBATTLE, None, Callback(self.__initSoundsOnArenaPreBattle)),
         (ARENA_PERIOD.BATTLE, None, Callback(self.__initSoundsOnArenaBattle)),
         (ARENA_PERIOD.AFTERBATTLE, None, self.__afterBattleSoundsCallback)]
        return

    def init(self):
        self.__addListeners()
        self.__initSoundByArenaPeriod(BigWorld.player().arena.period)

    def destroy(self):
        WWISE.WW_eventGlobal(self.EVENT_RACE_EXIT)
        self.__afterBattleSoundsCallback.invoke()
        self.__removeListeners()
        for el in self.__countdownCallbacks:
            el.destroy()

        self.__countdownCallbacks = None
        self.__afterBattleSoundsCallback = None
        for _, cl1, cl2 in self.__arenaPeriodHandlers:
            if cl1 is not None:
                cl1.destroy()
            if cl2 is not None:
                cl2.destroy()

        self.__arenaPeriodHandlers = None
        return

    def __addListeners(self):
        repairCtrl = self._sessionProvider.dynamic.eventRepair
        if repairCtrl is not None:
            repairCtrl.onPlayerRepaired += self.__onRepair
        vStateCtrl = self._sessionProvider.shared.vehicleState
        if vStateCtrl is not None:
            vStateCtrl.onVehicleStateUpdated += self.__onVehicleStateUpdated
            vStateCtrl.onSurfaceContactChanged += self.__onSurfaceContactChanged
        arenaPeriodCtrl = self._sessionProvider.shared.arenaPeriod
        if arenaPeriodCtrl is not None:
            arenaPeriodCtrl.onCountdown += self.__onCountdown
        teamBasses = self._sessionProvider.dynamic.teamBases
        if teamBasses is not None:
            teamBasses.onStartCapturingBase += self.__onStartCapturingBase
            teamBasses.onPointsUpdated += self.__onBasePointsUpdated
        eqCtrl = self._sessionProvider.shared.equipments
        if eqCtrl is not None:
            eqCtrl.onEquipmentUpdated += self.__onEquipmentUpdated
        g_playerEvents.onArenaPeriodChange += self.__onArenaPeriodChange
        g_playerEvents.onRoundFinished += self.__onRoundFinish
        raceCtrl = self._sessionProvider.dynamic.eventRacePosition
        if eqCtrl is not None:
            raceCtrl.onRaceFirstLights += self.__onHighPrestartNotification
            raceCtrl.onRaceLastLights += self.__initSoundsOnArenaBattleStart
        return

    def __removeListeners(self):
        repairCtrl = self._sessionProvider.dynamic.eventRepair
        if repairCtrl is not None:
            repairCtrl.onPlayerRepaired -= self.__onRepair
        vStateCtrl = self._sessionProvider.shared.vehicleState
        if vStateCtrl is not None:
            vStateCtrl.onVehicleStateUpdated -= self.__onVehicleStateUpdated
            vStateCtrl.onSurfaceContactChanged -= self.__onSurfaceContactChanged
        arenaPerionCtrl = self._sessionProvider.shared.arenaPeriod
        if arenaPerionCtrl is not None:
            arenaPerionCtrl.onCountdown -= self.__onCountdown
        teamBasses = self._sessionProvider.dynamic.teamBases
        if teamBasses is not None:
            teamBasses.onStartCapturingBase -= self.__onStartCapturingBase
            teamBasses.onPointsUpdated -= self.__onBasePointsUpdated
        eqCtrl = self._sessionProvider.shared.equipments
        if eqCtrl is not None:
            eqCtrl.onEquipmentUpdated -= self.__onEquipmentUpdated
        g_playerEvents.onArenaPeriodChange -= self.__onArenaPeriodChange
        g_playerEvents.onRoundFinished -= self.__onRoundFinish
        raceCtrl = self._sessionProvider.dynamic.eventRacePosition
        if eqCtrl is not None:
            raceCtrl.onRaceFirstLights -= self.__onHighPrestartNotification
            raceCtrl.onRaceLastLights -= self.__initSoundsOnArenaBattleStart
        return

    def __defineMaxVehicleSpeed(self):
        if self.__vehicleMaxSpeed is None:
            vehicle = BigWorld.player().vehicle
            defaultVehicleCfg = vehicle.typeDescriptor.type.xphysics['engines'][vehicle.typeDescriptor.engine.name]
            self.__vehicleMaxSpeed = defaultVehicleCfg['smplFwMaxSpeed']
        return

    def __initSoundsOnArenaWating(self):
        WWISE.WW_eventGlobal(self.EVENT_RACE_LOADING)
        WWISE.WW_eventGlobal(self.EVENT_RACE_MUSIC)

    def __initSoundsOnArenaPreBattle(self):
        WWISE.WW_setSwitch(self.SWITCHER, self.REAL_TO_SWITCH)

    def __initSoundsOnArenaBattleStart(self):
        WWISE.WW_eventGlobal(self.EVENT_RACE_START)
        self.__playSoundNotification(self.SOUND_NTF_ONSTART)

    def __initSoundsOnArenaBattle(self):
        WWISE.WW_setState(self.STATE_RACE_GAMEPLAY, self.STATE_RACE_GAMEPLAY_ON)

    def __initSoundsOnArenaAfterBattle(self):
        WWISE.WW_setState(self.STATE_RACE_GAMEPLAY, self.STATE_RACE_GAMEPLAY_OFF)

    def __initSoundByArenaPeriod(self, period):
        for p, initCallback, callback in self.__arenaPeriodHandlers:
            if p == period and initCallback is not None:
                initCallback.invoke()
            if callback is not None:
                callback.invoke()
            if p == period:
                break

        return

    def __onArenaPeriodChange(self, period, *args):
        self.__initSoundByArenaPeriod(period)

    def __onCountdown(self, timeleft):
        for el in self.__countdownCallbacks:
            el.invokeByTime(timeleft)

    def __onEquipmentUpdated(self, intCD, item):
        if 'speedboost' in item.getDescriptor().name and item.getStage() == EQUIPMENT_STAGES.READY:
            WWISE.WW_eventGlobal(self.EVENT_SPEED_BOOST_READY)

    def __onLowPrestartNotification(self):
        self.__playSoundNotification(self.SOUND_NTF_PRESTART)

    def __onHighPrestartNotification(self):
        WWISE.WW_eventGlobal(self.EVENT_RACE_PRE_START)

    def __onRepair(self, amount, repaired):
        if repaired:
            self.__playSoundNotification(self.SOUND_NTF_ONREPAIR)
        WWISE.WW_eventGlobal(self.EVENT_RACE_TANK_REPAIR)

    def __onRoundFinish(self, winnerTeam, reason):
        sound = self.SOUND_NTF_DRAW
        if winnerTeam != 0:
            player = BigWorld.player()
            sound = self.SOUND_NTF_WIN if player.team == winnerTeam else self.SOUND_NTF_LOSE
        self.__playSoundNotification(sound)

    def __getEventByBasePoints(self, points):
        for event, (mn, mx) in self.EVENTS_TO_BASE_POINTS.iteritems():
            if mn <= points <= mx:
                return event

        return None

    def __onBasePointsUpdated(self, isEnemyBase, points):
        if isEnemyBase:
            return
        else:
            event = self.__getEventByBasePoints(points)
            if event is not None and self.__lastCapturingEvent != event:
                WWISE.WW_eventGlobal(event)
                self.__lastCapturingEvent = event
            return

    def __onStartCapturingBase(self, isEnemyBase):
        if not isEnemyBase and not self.__firstTimeZoneEntered:
            self.__playSoundNotification(self.SOUND_NTF_ONCAPTURING_BASE)
        self.__firstTimeZoneEntered = True

    def __onVehicleStateUpdated(self, stateID, value):
        if stateID == VEHICLE_VIEW_STATE.SPEED:
            self.__defineMaxVehicleSpeed()
            speedNorm = clamp(-1.0, 1.0, value / self.__vehicleMaxSpeed)
            vehicleID = self._sessionProvider.shared.vehicleState.getControllingVehicleID()
            vehicle = BigWorld.entity(vehicleID)
            if vehicle is not None and vehicle.appearance is not None and vehicle.appearance.engineAudition is not None:
                soundObject = vehicle.appearance.engineAudition.getSoundObject(TankSoundObjectsIndexes.ENGINE)
                soundObject.setRTPC(self.RACE_RTPC_ELECTRIC, speedNorm * 100)
        return

    def __onSurfaceContactChanged(self, isSurfaceContact):
        WWISE.WW_setRTCPGlobal(self.RACE_RTPC_FLYING_GLOBAL, 100 if isSurfaceContact else 0)

    @staticmethod
    def __playSoundNotification(eventName):
        soundNfs = BigWorld.player().soundNotifications
        soundNfs.play(eventName)
