# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/battle_control/controllers/br_battle_sounds.py
import logging
import BigWorld
import WWISE
from constants import ATTACK_REASON
from gui.Scaleform.daapi.view.common.battle_royale.br_helpers import getEquipmentById, getSmokeDataByPredicate
from gui.battle_control.battle_constants import PLAYER_GUI_PROPS
from gui.battle_control.controllers.period_ctrl import IAbstractPeriodView
from gui.battle_control.controllers.sound_ctrls.common import SoundPlayersController, VehicleStateSoundPlayer, BaseEfficiencySoundPlayer, EquipmentComponentSoundPlayer
from gui.doc_loaders.battle_royale_settings_loader import getBattleRoyaleSettings
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE, TIMER_VIEW_STATE, COUNTDOWN_STATE
from helpers.CallbackDelayer import CallbackDelayer
from constants import LootAction
from gui.shared.events import AirDropEvent
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.battle_control.view_components import IViewComponentsCtrlListener
from gui.shared.gui_items import GUI_ITEM_TYPE, isItemVehicleHull
from constants import ARENA_PERIOD
from gui.battle_control.battle_constants import FEEDBACK_EVENT_ID
from constants import EQUIPMENT_STAGES
from gui.battle_control.battle_constants import PERSONAL_EFFICIENCY_TYPE
from BattleFeedbackCommon import BATTLE_EVENT_TYPE
from battle_royale.gui.constants import BattleRoyaleEquipments, BattleRoyaleComponents
from battle_royale.gui.battle_control.controllers.progression_ctrl import IProgressionListener
from battle_royale.gui.battle_control.controllers.spawn_ctrl import ISpawnListener
from battle_royale.gui.battle_control.controllers.radar_ctrl import IRadarListener
from battle_royale.gui.battle_control.controllers.vehicles_count_ctrl import IVehicleCountListener
from vehicle_systems.tankStructure import TankSoundObjectsIndexes
import BattleReplay
from items import vehicles
from items.battle_royale import isSpawnedBot
from gui.battle_control.arena_info.settings import VehicleSpottedStatus
from constants import ARENA_BONUS_TYPE
_logger = logging.getLogger(__name__)

class BREvents(object):
    LOOT_PICKUP_START = 'BR_loot_pickup_start'
    LOOT_PICKUP_DONE = 'BR_loot_pickup_end'
    LOOT_PICKUP_STOP = 'BR_loot_pickup_stop'
    RADAR_ACTIVATED = 'BR_radar_mine'
    RADAR_ACTIVATED_SQUAD = 'BR_radar_ally'
    SPAWN_MINE = 'BR_spawn_mine'
    SPAWN_ALLY = 'BR_spawn_ally'
    SPAWN_TIMER = 'BR_timer'
    SPAWN_TIMER_WARNING = 'BR_timer_warning'
    AIRDROP_SPAWNED = 'BR_airdrop'
    DEATHZONE_ENTER = {TIMER_VIEW_STATE.CRITICAL: 'BR_death_zone_red_enter',
     TIMER_VIEW_STATE.WARNING: 'BR_death_zone_yellow_enter'}
    DEATHZONE_EXIT = {TIMER_VIEW_STATE.CRITICAL: 'BR_death_zone_red_exit',
     TIMER_VIEW_STATE.WARNING: 'BR_death_zone_yellow_exit'}
    LEVEL_UP = 'BR_levelup'
    LEVEL_UP_MAX = 'BR_levelup_max'
    UPGRADE_PANEL_SHOW = 'BR_widget_on'
    UPGRADE_PANEL_HIDE = 'BR_widget_off'
    VEH_CONFIGURATOR_SHOW = 'BR_upgrade_view_on'
    VEH_CONFIGURATOR_HIDE = 'BR_upgrade_view_off'
    BATTLE_SUMMARY_SHOW = 'BR_result_screen'
    BR_RESULT_PROGRESS_BAR_STOP = 'BR_result_progress_bar_stop'
    INSTALL_MODULE = {GUI_ITEM_TYPE.RADIO: 'BR_upgrade_radio',
     GUI_ITEM_TYPE.GUN: 'BR_upgrade_weapons',
     GUI_ITEM_TYPE.ENGINE: 'BR_upgrade_engine',
     GUI_ITEM_TYPE.TURRET: 'BR_upgrade_turret'}
    INSTALL_MODULE_CHASSIS = 'BR_upgrade_treads'
    INSTALL_MODULE_HULL = 'BR_upgrade_hull'
    PHASE_MIDDLE = 'BR_combat_phase_activated'
    PLAYER_LEVEL_MIDDLE = 'BR_combat_phase_our'
    SOLO_ENEMIES_AMOUNT = {10: 'BR_enemy_remained_10',
     5: 'BR_enemy_remained_05',
     2: 'BR_enemy_remained_02',
     1: 'BR_enemy_remained_01'}
    SQUAD_ENEMIES_AMOUNT = {10: 'BR_enemy_remained_platoon_10',
     5: 'BR_enemy_remained_platoon_05',
     2: 'BR_enemy_remained_platoon_02',
     1: 'BR_enemy_remained_platoon_01'}
    ENEMY_KILLED = 'BR_enemy_killed'
    BATTLE_STARTED = 'BR_start_battle'
    BATTLE_WIN = 'BR_win'
    BATTLE_DEFEAT = 'BR_defeat'
    EQUIPMENT_ACTIVATED = {BattleRoyaleEquipments.LARGE_REPAIRKIT: 'BR_perk_repair_activation',
     BattleRoyaleEquipments.REGENERATION_KIT: 'BR_perk_hp_restore_activation',
     BattleRoyaleEquipments.SELF_BUFF: 'BR_perk_selfbuff_activation',
     BattleRoyaleEquipments.TRAP_POINT: 'BR_perk_trap_slowdown_activation',
     BattleRoyaleEquipments.REPAIR_POINT: 'BR_perk_repairpoint_activation',
     BattleRoyaleEquipments.HEAL_POINT: 'BR_perk_healzone_activation',
     BattleRoyaleEquipments.SMOKE_WITH_DAMAGE: 'BR_perk_smoke_zone_applied',
     BattleRoyaleEquipments.KAMIKAZE: 'BR_perk_kamikaze_zone_applied',
     BattleRoyaleEquipments.MINE_FIELD: 'BR_perk_minefield_zone',
     BattleRoyaleEquipments.ADAPTATION_HEALTH_RESTORE: 'BR_perk_hp_restore2_activation',
     BattleRoyaleEquipments.FIRE_CIRCLE: 'BR_perk_fire_circle_activation',
     BattleRoyaleEquipments.CLING_BRANDER: 'BR_perk_clingbrander_zone_applied',
     BattleRoyaleEquipments.SHOT_PASSION: 'BR_perk_shotpassion_activation',
     BattleRoyaleEquipments.BOMBER: 'BR_perk_airstrike_zone_applied',
     BattleRoyaleEquipments.THUNDER_STRIKE: 'BR_perk_thundersrtike_zone_applied'}
    EQUIPMENT_DEACTIVATED = {BattleRoyaleEquipments.REGENERATION_KIT: 'BR_perk_hp_restore_deactivation',
     BattleRoyaleEquipments.SELF_BUFF: 'BR_perk_selfbuff_deactivation',
     BattleRoyaleEquipments.ADAPTATION_HEALTH_RESTORE: 'BR_perk_hp_restore2_deactivation'}
    TRAP_POINT_ENTER = 'BR_perk_trap_slowdown_affects'
    TRAP_POINT_EXIT = 'BR_perk_trap_slowdown_affects_off'
    REPAIR_POINT_ENTER = 'BR_perk_repairpoint_affects'
    REPAIR_POINT_EXIT = 'BR_perk_repairpoint_affects_off'
    HEAL_POINT_ENTER = 'BR_perk_healzone_affects'
    HEAL_POINT_EXIT = 'BR_perk_healzone_affects_off'
    AIRSTRIKE_AFFECTS = 'BR_perk_airstrike_affects'
    BERSERKER_ACTIVATION = 'BR_perk_berserker_activation'
    BERSERKER_DEACTIVATION = 'BR_perk_berserker_deactivation'
    BERSERKER_PULSE_RED = 'BR_perk_berserker_pulse_red'
    KAMIKAZE_HITS_TARGET = 'BR_perk_kamikaze_hits_target'
    KAMIKAZE_TARGET_LOST = 'BR_perk_kamikaze_target_lost'
    KAMIKAZE_DETECTED = 'BR_brander_detected'
    MINEFIELD_ACTIVATION = 'BR_perk_minefield_activation'
    MINEFIELD_HIT_TARGET = 'BR_perk_minefield_hits_target'
    BR_SMOKE_DAMGE_AREA_ENTER = 'BR_smoke_damge_affects'
    BR_SMOKE_DAMGE_AREA_EXIT = 'BR_smoke_damage_affects_off'
    BR_FIRE_CIRCLE_ENTERED = 'BR_perk_fire_circle_affect'
    BR_FIRE_CIRCLE_LEFT = 'BR_perk_fire_circle_affect_off'
    BR_CLING_BRANDER_DESTROYED = 'BR_perk_clingbrander_destroyed'
    BR_SHOT_PASSION_AFFECT = 'BR_perk_shotpassion_affect'
    BR_SHOT_PASSION_AFFECT_OFF = 'BR_perk_shotpassion_affect_off'
    EQUIPMENT_PREPARING = {BattleRoyaleEquipments.MINE_FIELD: MINEFIELD_ACTIVATION,
     BattleRoyaleEquipments.CLING_BRANDER: 'BR_perk_clingbrander_activation',
     BattleRoyaleEquipments.BOMBER: 'BR_perk_airstrike_activation',
     BattleRoyaleEquipments.THUNDER_STRIKE: 'BR_perk_thundersrtike_activation',
     BattleRoyaleEquipments.KAMIKAZE: 'BR_perk_kamikaze_activation',
     BattleRoyaleEquipments.SMOKE_WITH_DAMAGE: 'BR_perk_smoke_activation',
     BattleRoyaleEquipments.CORRODING_SHOT: 'BR_perk_corroding_shot_activation'}

    @staticmethod
    def playSound(eventName):
        if BattleReplay.g_replayCtrl.isPlaying and BattleReplay.g_replayCtrl.isTimeWarpInProgress:
            return
        WWISE.WW_eventGlobal(eventName)

    @staticmethod
    def playSoundPos(eventName, pos):
        if BattleReplay.g_replayCtrl.isPlaying and BattleReplay.g_replayCtrl.isTimeWarpInProgress:
            return
        WWISE.WW_eventGlobalPos(eventName, pos)


class BRStates(object):
    STATE_PHASE = 'STATE_BR_gameplay_music_phase'
    STATE_PHASE_START = 'STATE_BR_gameplay_music_phase_start'
    STATE_PHASE_MIDDLE = 'STATE_BR_gameplay_music_phase_middle'
    STATE_PHASE_FINAL = 'STATE_BR_gameplay_music_phase_final'
    STATE_STATUS = 'STATE_BR_gameplay_music_status'
    STATE_STATUS_EXPLORING = 'STATE_BR_gameplay_music_status_exploring'
    STATE_STATUS_COMBAT = 'STATE_BR_gameplay_music_status_combat'
    STATE_POSTMORTEM = 'STATE_postmortem_mode'
    STATE_POSTMORTEM_OFF = 'STATE_postmortem_mode_off'
    STATE_POSTMORTEM_ON = 'STATE_postmortem_mode_on'
    STATE_BR = 'STATE_BR_gameplay'
    STATE_BR_ON = 'STATE_BR_gameplay_on'
    STATE_BR_OFF = 'STATE_BR_gameplay_off'
    STATE_DEATHZONE = {TIMER_VIEW_STATE.CRITICAL: 'STATE_BR_death_zone_red',
     TIMER_VIEW_STATE.WARNING: 'STATE_BR_death_zone_yellow'}
    STATE_DEATHZONE_IN = {TIMER_VIEW_STATE.CRITICAL: 'STATE_BR_death_zone_red_in',
     TIMER_VIEW_STATE.WARNING: 'STATE_BR_death_zone_yellow_in'}
    STATE_DEATHZONE_OUT = {TIMER_VIEW_STATE.CRITICAL: 'STATE_BR_death_zone_red_out',
     TIMER_VIEW_STATE.WARNING: 'STATE_BR_death_zone_yellow_out'}

    @staticmethod
    def setState(stateName, stateValue):
        WWISE.WW_setState(stateName, stateValue)


class BREventParams(object):
    SHOT_PASSION_MULTIPLIER = 'RTPC_ext_shotpassion_affect'

    @staticmethod
    def setEventParam(paramName, paramValue):
        WWISE.WW_setRTCPGlobal(paramName, paramValue)


class BRBattleSoundController(SoundPlayersController):

    def __init__(self):
        super(BRBattleSoundController, self).__init__()
        self._soundPlayers = (LootSoundPlayer(),
         DeathzoneSoundPlayer(),
         AirDropSoundPlayer(),
         StatusSoundPlayer(),
         ArenaTypeSoundPlayer(),
         DeathScreenSoundPlayer(),
         BomberHitSoundPlayer(),
         KamikazeSoundPlayer(),
         BerserkerSoundPlayer(),
         MineFieldSoundPlayer(),
         _HealingRepairSoundPlayer(),
         _DamagingSmokeAreaSoundPlayer(),
         ClingBranderSoundPlayer(),
         ShotPassionSoundPlayer())


class RadarSoundPlayer(IRadarListener):

    def radarInfoReceived(self, radarInfo):
        isPlayer = BigWorld.player().playerVehicleID == radarInfo[0]
        eventName = BREvents.RADAR_ACTIVATED if isPlayer else BREvents.RADAR_ACTIVATED_SQUAD
        BREvents.playSound(eventName)


class LootSoundPlayer(VehicleStateSoundPlayer):

    def _onVehicleStateUpdated(self, state, value):
        if state == VEHICLE_VIEW_STATE.LOOT:
            _, _, action, _ = value
            if action == LootAction.PICKUP_STARTED:
                BREvents.playSound(BREvents.LOOT_PICKUP_START)
            elif action == LootAction.PICKUP_SUCCEEDED:
                BREvents.playSound(BREvents.LOOT_PICKUP_DONE)
            elif action == LootAction.PICKUP_FAILED:
                BREvents.playSound(BREvents.LOOT_PICKUP_STOP)

    def _onSwitchViewPoint(self):
        BREvents.playSound(BREvents.LOOT_PICKUP_STOP)


class ClingBranderSoundPlayer(object):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)
    __CLING_BRANDER_VEH_NAME = 'china:Ch00_ClingeBot_SH'

    def init(self):
        ctrl = self.__sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onVehicleFeedbackReceived += self.__onVehicleFeedbackReceived
        return

    def destroy(self):
        ctrl = self.__sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onVehicleFeedbackReceived -= self.__onVehicleFeedbackReceived
        return

    def __onVehicleFeedbackReceived(self, eventID, vehicleID, _):
        if eventID == FEEDBACK_EVENT_ID.VEHICLE_DEAD:
            vehicle = BigWorld.entities[vehicleID]
            if vehicle.masterVehID == BigWorld.player().playerVehicleID and vehicle.typeDescriptor.name == self.__CLING_BRANDER_VEH_NAME:
                BREvents.playSound(BREvents.BR_CLING_BRANDER_DESTROYED)


class DeathScreenSoundPlayer(object):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def init(self):
        ctrl = self.__sessionProvider.dynamic.deathScreen
        ctrl.onShowDeathScreen += self.__onShowDeathScreen

    def destroy(self):
        ctrl = self.__sessionProvider.dynamic.deathScreen
        if ctrl is not None:
            ctrl.onShowDeathScreen -= self.__onShowDeathScreen
        return

    def __onShowDeathScreen(self):
        BREvents.playSound(BREvents.BATTLE_SUMMARY_SHOW)
        arena = BigWorld.player().arena
        wwSetup = arena.arenaType.wwmusicSetup
        if wwSetup is None:
            return
        else:
            eventName = wwSetup.get('wwmusicResultDefeat', '')
            if eventName:
                BREvents.playSound(eventName)
            return


class DeathzoneSoundPlayer(VehicleStateSoundPlayer):

    def __init__(self):
        super(DeathzoneSoundPlayer, self).__init__()
        self.__isInZone = None
        return

    def destroy(self):
        self.__stopEvent()
        super(DeathzoneSoundPlayer, self).destroy()

    def _onVehicleStateUpdated(self, state, value):
        if state == VEHICLE_VIEW_STATE.DEATHZONE_TIMER:
            if value.level is None and value.isCausingDamage:
                vehicle = self._sessionProvider.shared.vehicleState.getControllingVehicle()
                isAlive = vehicle is not None and vehicle.isAlive()
                zoneLevel = TIMER_VIEW_STATE.CRITICAL if isAlive else None
            else:
                zoneLevel = value.level
            if zoneLevel != self.__isInZone:
                self.__stopEvent()
                if zoneLevel:
                    BREvents.playSound(BREvents.DEATHZONE_ENTER[zoneLevel])
                    BRStates.setState(BRStates.STATE_DEATHZONE[zoneLevel], BRStates.STATE_DEATHZONE_IN[zoneLevel])
                self.__isInZone = zoneLevel
        return

    def _onSwitchViewPoint(self):
        self.__stopEvent()

    def __stopEvent(self):
        if self.__isInZone is not None:
            BREvents.playSound(BREvents.DEATHZONE_EXIT[self.__isInZone])
            BRStates.setState(BRStates.STATE_DEATHZONE[self.__isInZone], BRStates.STATE_DEATHZONE_OUT[self.__isInZone])
            self.__isInZone = None
        return


class InstallModuleSoundPlayer(IProgressionListener, IViewComponentsCtrlListener):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)
    __PLAYER_MIDDLE_LEVEL = 4

    def setVehicleChangeResponse(self, itemCD, success):
        if not success:
            return
        else:
            progressionCtrl = self.__sessionProvider.dynamic.progression
            module = progressionCtrl.getModule(itemCD)
            typeCD = module.descriptor.typeID
            moduleLevel = module.level
            if moduleLevel == self.__PLAYER_MIDDLE_LEVEL:
                eventName = BREvents.PLAYER_LEVEL_MIDDLE
            elif moduleLevel == progressionCtrl.maxLevel:
                eventName = BREvents.LEVEL_UP_MAX
            elif typeCD == GUI_ITEM_TYPE.CHASSIS:
                if isItemVehicleHull(itemCD, progressionCtrl.getCurrentVehicle()):
                    eventName = BREvents.INSTALL_MODULE_HULL
                else:
                    eventName = BREvents.INSTALL_MODULE_CHASSIS
            else:
                eventName = BREvents.INSTALL_MODULE.get(typeCD)
            if eventName is not None:
                BREvents.playSound(eventName)
            return


class AirDropSoundPlayer(object):

    def init(self):
        g_eventBus.addListener(AirDropEvent.AIR_DROP_SPAWNED, self.__onAirDropSpawned, scope=EVENT_BUS_SCOPE.BATTLE)

    def destroy(self):
        g_eventBus.removeListener(AirDropEvent.AIR_DROP_SPAWNED, self.__onAirDropSpawned, scope=EVENT_BUS_SCOPE.BATTLE)

    def __onAirDropSpawned(self, _):
        BREvents.playSound(BREvents.AIRDROP_SPAWNED)


class LevelSoundPlayer(IProgressionListener):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(LevelSoundPlayer, self).__init__()
        self.__level = None
        return

    def updateData(self, arenaLevelData):
        progressionCtrl = self.__sessionProvider.dynamic.progression
        if self.__level != arenaLevelData.level:
            if self.__level is not None and arenaLevelData.level < progressionCtrl.maxLevel:
                BREvents.playSound(BREvents.LEVEL_UP)
            self.__level = arenaLevelData.level
        return


class EnemiesAmountSoundPlayer(IVehicleCountListener):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(EnemiesAmountSoundPlayer, self).__init__()
        self.__enemiesCount = None
        self.__frags = None
        return

    def setVehicles(self, count, _, teams):
        if self.__enemiesCount is not None and count != self.__enemiesCount:
            bonusType = self.__sessionProvider.arenaVisitor.getArenaBonusType()
            isSquad = bonusType in ARENA_BONUS_TYPE.BATTLE_ROYALE_SQUAD_RANGE
            _data = BREvents.SQUAD_ENEMIES_AMOUNT if isSquad else BREvents.SOLO_ENEMIES_AMOUNT
            eventName = _data.get(count)
            if eventName is not None:
                BREvents.playSound(eventName)
        self.__enemiesCount = count
        return

    def setFrags(self, frags, isPlayerVehicle):
        if isPlayerVehicle:
            if self.__frags is not None and self.__frags != frags and self.__enemiesCount > 1:
                BREvents.playSound(BREvents.ENEMY_KILLED)
            self.__frags = frags
        return


class PhaseSoundPlayer(IProgressionListener, IVehicleCountListener):
    __slots__ = ('__averageLevel', '__enemyTeamsCount', '__currentState', '__finalPhaseEnemiesCount', '__middlePhaseAverageLevel')

    def __init__(self):
        super(PhaseSoundPlayer, self).__init__()
        self.__averageLevel = None
        self.__enemyTeamsCount = None
        self.__currentState = None
        brSettings = getBattleRoyaleSettings().sounds
        self.__finalPhaseEnemiesCount = brSettings.finalEnemiesCount
        self.__middlePhaseAverageLevel = brSettings.middleAverageLevel
        self.__updatePhase()
        return

    def setVehicles(self, count, _, teams):
        self.__enemyTeamsCount = teams
        self.__updatePhase()

    def setAverageBattleLevel(self, level):
        self.__averageLevel = level
        self.__updatePhase()

    def __updatePhase(self):
        if self.__enemyTeamsCount is not None and self.__averageLevel is not None:
            if self.__enemyTeamsCount <= self.__finalPhaseEnemiesCount:
                self.__setSoundState(BRStates.STATE_PHASE_FINAL)
            elif self.__middlePhaseAverageLevel <= self.__averageLevel:
                self.__setSoundState(BRStates.STATE_PHASE_MIDDLE)
            else:
                self.__setSoundState(BRStates.STATE_PHASE_START)
        return

    def __setSoundState(self, state):
        if self.__currentState != state:
            BRStates.setState(BRStates.STATE_PHASE, state)


class StatusSoundPlayer(VehicleStateSoundPlayer, CallbackDelayer):
    __ON_OBSERVED_DURATION = 20.0

    def __init__(self):
        super(StatusSoundPlayer, self).__init__()
        self.__seenEnemies = set()
        self.__isObservedByEnemy = False

    def init(self):
        super(StatusSoundPlayer, self).init()
        ctrl = self._sessionProvider.shared.feedback
        ctrl.onVehicleFeedbackReceived += self.__onVehicleFeedbackReceived
        ctrl.onMinimapVehicleAdded += self.__onVehicleEnterWorld
        ctrl.onMinimapVehicleRemoved += self.__onVehicleLeaveWorld
        self.__updateStatus()

    def destroy(self):
        ctrl = self._sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onVehicleFeedbackReceived -= self.__onVehicleFeedbackReceived
            ctrl.onMinimapVehicleAdded -= self.__onVehicleEnterWorld
            ctrl.onMinimapVehicleRemoved -= self.__onVehicleLeaveWorld
        self.__seenEnemies.clear()
        VehicleStateSoundPlayer.destroy(self)
        CallbackDelayer.destroy(self)
        return

    def __onVehicleFeedbackReceived(self, eventID, vehicleID, _):
        if eventID == FEEDBACK_EVENT_ID.VEHICLE_DEAD:
            self.__seenEnemies.discard(vehicleID)
            self.__updateStatus()

    def __onVehicleLeaveWorld(self, vId):
        self.__seenEnemies.discard(vId)
        self.__updateStatus()

    def _onVehicleStateUpdated(self, state, value):
        if state == VEHICLE_VIEW_STATE.OBSERVED_BY_ENEMY:
            self.__isObservedByEnemy = value
            self.__updateStatus()
            if self.__isObservedByEnemy:
                self.stopCallback(self.__onObservationDone)
                self.delayCallback(self.__ON_OBSERVED_DURATION, self.__onObservationDone)

    def __onObservationDone(self):
        self.__isObservedByEnemy = False
        self.__updateStatus()

    def __onVehicleEnterWorld(self, vProxy, vInfo, _):
        player = BigWorld.player()
        if player.team != vInfo.team and vProxy.isAlive():
            self.__seenEnemies.add(vProxy.id)
            self.__updateStatus()

    def __updateStatus(self):
        isCombat = self.__isObservedByEnemy or len(self.__seenEnemies) > 0
        status = BRStates.STATE_STATUS_COMBAT if isCombat else BRStates.STATE_STATUS_EXPLORING
        BRStates.setState(BRStates.STATE_STATUS, status)


class ArenaPeriodSoundPlayer(IAbstractPeriodView, IViewComponentsCtrlListener, IVehicleCountListener):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(ArenaPeriodSoundPlayer, self).__init__()
        self.__period = None
        self.__winStatus = None
        self.__isAlive = None
        return

    def detachedFromCtrl(self, ctrlID):
        self.__winStatus = None
        return

    def setPeriod(self, period):
        self.__period = period
        if period == ARENA_PERIOD.PREBATTLE and not BigWorld.player().isObserver():
            BREvents.playSound(BREvents.BATTLE_STARTED)
        else:
            self.__checkBattleEnd()

    def setAdditionalInfo(self, additionalInfo):
        self.__winStatus = additionalInfo.getWinStatus()
        self.__checkBattleEnd()

    def setPlayerVehicleAlive(self, isAlive):
        if self.__isAlive and not isAlive and not BigWorld.player().isObserver():
            BREvents.playSound(BREvents.BATTLE_DEFEAT)
        self.__isAlive = isAlive

    def __checkBattleEnd(self):
        if BigWorld.player().isObserver():
            return
        else:
            if self.__period == ARENA_PERIOD.AFTERBATTLE and self.__winStatus is not None and self.__isAlive:
                eventName = BREvents.BATTLE_WIN if self.__winStatus.isWin() else BREvents.BATTLE_DEFEAT
                BREvents.playSound(eventName)
                self.__period = None
                self.__winStatus = None
            return


class PostmortemSoundPlayer(IVehicleCountListener):

    def setPlayerVehicleAlive(self, isAlive):
        isOff = isAlive and not BigWorld.player().isObserver()
        stateValue = BRStates.STATE_POSTMORTEM_OFF if isOff else BRStates.STATE_POSTMORTEM_ON
        BRStates.setState(BRStates.STATE_POSTMORTEM, stateValue)


class ArenaTypeSoundPlayer(object):

    def init(self):
        BRStates.setState(BRStates.STATE_BR, BRStates.STATE_BR_ON)

    def destroy(self):
        BRStates.setState(BRStates.STATE_BR, BRStates.STATE_BR_OFF)


class SelectRespawnSoundPlayer(ISpawnListener, IAbstractPeriodView):
    __slots__ = ('__isSpawnTimerWorking', '__isSpawnTimerStopped', '__mainTimerStopped', '__selectEndingSoonTime')

    def __init__(self):
        super(SelectRespawnSoundPlayer, self).__init__()
        self.__isSpawnTimerWorking = False
        self.__isSpawnTimerStopped = False
        self.__mainTimerStopped = False
        self.__selectEndingSoonTime = getBattleRoyaleSettings().spawn.selectEndingSoonTime

    def closeSpawnPoints(self):
        self.__isSpawnTimerStopped = True

    def updateCloseTime(self, timeLeft, state):
        if state == COUNTDOWN_STATE.WAIT:
            return
        if self.__isSpawnTimerStopped:
            self.__isSpawnTimerWorking = False
            return
        if self.__mainTimerStopped:
            return
        self.__isSpawnTimerWorking = not timeLeft == 0
        eventName = BREvents.SPAWN_TIMER_WARNING if timeLeft < self.__selectEndingSoonTime else BREvents.SPAWN_TIMER
        BREvents.playSound(eventName)

    def setCountdown(self, state, timeLeft):
        if state != COUNTDOWN_STATE.START:
            return
        self.__mainTimerStopped = False
        if self.__isSpawnTimerStopped or not self.__isSpawnTimerWorking:
            BREvents.playSound(BREvents.SPAWN_TIMER)

    def hideCountdown(self, state, speed):
        self.__mainTimerStopped = True

    def updatePoint(self, vehicleId, pointId, prevPointId):
        BREvents.playSound(BREvents.SPAWN_ALLY)

    def onSelectPoint(self, pointId):
        BREvents.playSound(BREvents.SPAWN_MINE)


class EquipmentSoundPlayer(IVehicleCountListener, IViewComponentsCtrlListener):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        self.__currentEquipment = set()
        ctrl = self.__sessionProvider.shared.equipments
        ctrl.onEquipmentUpdated += self.__onEquipmentUpdated

    def detachedFromCtrl(self, ctrlID):
        self.__currentEquipment = None
        ctrl = self.__sessionProvider.shared.equipments
        ctrl.onEquipmentUpdated -= self.__onEquipmentUpdated
        return

    def __onEquipmentUpdated(self, _, item):
        if item.getPrevStage() == item.getStage():
            return
        else:
            prevStageIsReady = item.getPrevStage() in (EQUIPMENT_STAGES.READY, EQUIPMENT_STAGES.PREPARING)
            currentStageIsActive = item.getStage() in (EQUIPMENT_STAGES.ACTIVE, EQUIPMENT_STAGES.COOLDOWN, EQUIPMENT_STAGES.EXHAUSTED)
            if prevStageIsReady and currentStageIsActive:
                itemName = item.getDescriptor().name
                eventName = BREvents.EQUIPMENT_ACTIVATED.get(itemName)
                if eventName is not None:
                    BREvents.playSound(eventName)
                self.__currentEquipment.add(itemName)
            elif item.getStage() == EQUIPMENT_STAGES.PREPARING and item.getStage() != item.getPrevStage():
                eventName = BREvents.EQUIPMENT_PREPARING.get(item.getDescriptor().name)
                if eventName is not None:
                    BREvents.playSound(eventName)
            else:
                prevStageIsActive = item.getPrevStage() == EQUIPMENT_STAGES.ACTIVE
                currentStageIsCooldown = item.getStage() in (EQUIPMENT_STAGES.COOLDOWN, EQUIPMENT_STAGES.READY, EQUIPMENT_STAGES.UNAVAILABLE)
                if prevStageIsActive and currentStageIsCooldown:
                    itemName = item.getDescriptor().name
                    eventName = BREvents.EQUIPMENT_DEACTIVATED.get(itemName)
                    if eventName is not None:
                        BREvents.playSound(eventName)
                    self.__currentEquipment.discard(itemName)
            return

    def setPlayerVehicleAlive(self, isAlive):
        if not isAlive:
            for eq in self.__currentEquipment:
                eventName = BREvents.EQUIPMENT_DEACTIVATED.get(eq)
                if eventName is not None:
                    BREvents.playSound(eventName)

        return


class BerserkerSoundPlayer(VehicleStateSoundPlayer, CallbackDelayer):

    def __init__(self):
        CallbackDelayer.__init__(self)
        self.__period = None
        return

    def destroy(self):
        self.__stopEffect()
        CallbackDelayer.destroy(self)
        super(BerserkerSoundPlayer, self).destroy()

    def _onVehicleStateUpdated(self, state, berserkerData):
        if state == VEHICLE_VIEW_STATE.BERSERKER:
            if berserkerData['duration'] <= 0:
                self.__stopEffect()
                return
            BREvents.playSound(BREvents.BERSERKER_ACTIVATION)
            self.__stopEffect()
            self.__period = berserkerData['tickInterval']
            self.delayCallback(self.__period, self.__updateEffect)

    def __updateEffect(self):
        BREvents.playSound(BREvents.BERSERKER_PULSE_RED)
        return self.__period

    def _onSwitchViewPoint(self):
        self.__stopEffect()

    def __stopEffect(self):
        if self.__period is not None:
            self.stopCallback(self.__updateEffect)
            self.__period = None
            BREvents.playSound(BREvents.BERSERKER_DEACTIVATION)
        return


class BomberHitSoundPlayer(BaseEfficiencySoundPlayer):
    __DAMAGE_TYPE = (PERSONAL_EFFICIENCY_TYPE.RECEIVED_DAMAGE, PERSONAL_EFFICIENCY_TYPE.RECEIVED_CRITICAL_HITS, PERSONAL_EFFICIENCY_TYPE.STUN)

    def _onEfficiencyReceived(self, events):
        for e in events:
            if e.getType() in self.__DAMAGE_TYPE and e.isBomberEqDamage():
                BREvents.playSound(BREvents.AIRSTRIKE_AFFECTS)
                break


class KamikazeSoundPlayer(BaseEfficiencySoundPlayer):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)
    __KAMIKAZE_VEH_NAME = 'germany:G00_Bomber_SH'

    def init(self):
        super(KamikazeSoundPlayer, self).init()
        ctrl = self.__sessionProvider.dynamic.battleField
        if ctrl is not None:
            ctrl.onSpottedStatusChanged += self.updateVehiclesStats
        ctrl = self.__sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onMinimapVehicleAdded += self.__onVehicleEnterWorld
        arena = self.__sessionProvider.arenaVisitor.getArenaSubscription()
        if arena is not None:
            arena.onVehicleKilled += self.__onVehicleKilled
        return

    def destroy(self):
        arena = self.__sessionProvider.arenaVisitor.getArenaSubscription()
        if arena is not None:
            arena.onVehicleKilled -= self.__onVehicleKilled
        ctrl = self.__sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onMinimapVehicleAdded -= self.__onVehicleEnterWorld
        ctrl = self.__sessionProvider.dynamic.battleField
        if ctrl is not None:
            ctrl.onSpottedStatusChanged -= self.updateVehiclesStats
        super(KamikazeSoundPlayer, self).destroy()
        return

    def updateVehiclesStats(self, updated, arenaDP):
        getVehicleInfo = arenaDP.getVehicleInfo
        for _, vStatsVO in updated:
            vInfoVO = getVehicleInfo(vStatsVO.vehicleID)
            if isSpawnedBot(vInfoVO.vehicleType.tags) and vStatsVO.spottedStatus == VehicleSpottedStatus.SPOTTED:
                vehicleDescr = vehicles.VehicleDescr(compactDescr=vInfoVO.vehicleType.strCompactDescr)
                if vehicleDescr.type.name == self.__KAMIKAZE_VEH_NAME:
                    BREvents.playSound(BREvents.KAMIKAZE_DETECTED)

    def __onVehicleKilled(self, targetID, attackerID, equipmentID, reason, numVehiclesAffected):
        targetVeh = BigWorld.entity(targetID)
        playerVehID = BigWorld.player().playerVehicleID
        if targetVeh is not None and targetVeh.masterVehID == playerVehID and targetVeh.typeDescriptor.name == self.__KAMIKAZE_VEH_NAME:
            if attackerID == playerVehID and numVehiclesAffected > 0 and reason == ATTACK_REASON.getIndex(ATTACK_REASON.SPAWNED_BOT_EXPLOSION):
                BREvents.playSound(BREvents.KAMIKAZE_HITS_TARGET)
            else:
                BREvents.playSound(BREvents.KAMIKAZE_TARGET_LOST)
        return

    def __onVehicleEnterWorld(self, vProxy, vInfo, guiProps):
        vehicle = BigWorld.entity(vInfo.vehicleID)
        if vehicle.typeDescriptor.name == self.__KAMIKAZE_VEH_NAME and guiProps != PLAYER_GUI_PROPS.ally:
            audition = vehicle.appearance.engineAudition
            if audition is not None:
                audition.getSoundObject(TankSoundObjectsIndexes.ENGINE).play('BR_perk_kamikaze_distance_timer')
        return


class MineFieldSoundPlayer(BaseEfficiencySoundPlayer):

    def _onEfficiencyReceived(self, events):
        for e in events:
            if e.getBattleEventType() == BATTLE_EVENT_TYPE.DAMAGE and e.isMineFieldDamage():
                BREvents.playSound(BREvents.MINEFIELD_HIT_TARGET)
                break


class _HealingRepairSoundPlayer(VehicleStateSoundPlayer):

    def __init__(self):
        super(_HealingRepairSoundPlayer, self).__init__()
        self.__lastHealingSenderKey = None
        return

    def destroy(self):
        super(_HealingRepairSoundPlayer, self).destroy()
        self.__lastHealingSenderKey = None
        return

    def _onVehicleStateUpdated(self, state, value):
        if state in (VEHICLE_VIEW_STATE.HEALING, VEHICLE_VIEW_STATE.REPAIR_POINT):
            self.__updateHealingEffect(value)

    def __updateHealingEffect(self, value):
        if not value['isSourceVehicle']:
            senderKey = value.get('senderKey')
            if senderKey is not None:
                self.__onHealingActivate(senderKey)
            else:
                self.__onHealingDeactivate()
        return

    def __onHealingActivate(self, senderKey):
        if self.__lastHealingSenderKey is not None:
            self.__healingDeactivatePlayEvent(self.__lastHealingSenderKey)
        self.__lastHealingSenderKey = senderKey
        self.__healingActivatePlayEvent(self.__lastHealingSenderKey)
        return

    def __onHealingDeactivate(self):
        if self.__lastHealingSenderKey is not None:
            self.__healingDeactivatePlayEvent(self.__lastHealingSenderKey)
            self.__lastHealingSenderKey = None
        return

    def __healingActivatePlayEvent(self, senderKey):
        if senderKey == 'healPoint':
            eventName = BREvents.HEAL_POINT_ENTER
            _logger.debug('[HEAL_POINT] on activate play sound %s', eventName)
            BREvents.playSound(eventName)

    def __healingDeactivatePlayEvent(self, senderKey):
        if senderKey == 'healPoint':
            eventName = BREvents.HEAL_POINT_EXIT
            _logger.debug('[HEAL_POINT] on deactivate play sound %s', eventName)
            BREvents.playSound(eventName)


class _DamagingSmokeAreaSoundPlayer(VehicleStateSoundPlayer):

    def __init__(self):
        self.__effectIsWorking = False

    def destroy(self):
        self.__stopEvent()
        super(_DamagingSmokeAreaSoundPlayer, self).destroy()

    def _onVehicleStateUpdated(self, state, value):
        if state == VEHICLE_VIEW_STATE.SMOKE:
            _, self._smokeEquipment = getSmokeDataByPredicate(value, self.__isEquipmentWithDamage)
            if self._smokeEquipment:
                if not self.__effectIsWorking:
                    self.__effectIsWorking = True
                    BREvents.playSound(BREvents.BR_SMOKE_DAMGE_AREA_ENTER)
                return
            if self.__effectIsWorking:
                self.__stopEvent()

    def _onSwitchViewPoint(self):
        self.__stopEvent()

    def __stopEvent(self):
        if self.__effectIsWorking:
            self.__effectIsWorking = False
            BREvents.playSound(BREvents.BR_SMOKE_DAMGE_AREA_EXIT)

    def __isEquipmentWithDamage(self, equipmentId):
        equipment = getEquipmentById(equipmentId)
        return equipment.dotParams is not None if equipment else False


class ShotPassionSoundPlayer(EquipmentComponentSoundPlayer):
    __slots__ = ('__isActive',)
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(ShotPassionSoundPlayer, self).__init__()
        self.__isActive = False

    def destroy(self):
        super(ShotPassionSoundPlayer, self).destroy()
        self._stopSounds()

    def _onEquipmentComponentUpdated(self, _, vehicleID, equipmentInfo):
        if vehicleID == self.__sessionProvider.shared.vehicleState.getControllingVehicleID():
            duration = equipmentInfo.get('duration', 0)
            if duration > 0:
                if not self.__isActive:
                    BREvents.playSound(BREvents.BR_SHOT_PASSION_AFFECT)
                    self.__isActive = True
                else:
                    stage = equipmentInfo.get('stage', 0)
                    BREventParams.setEventParam(BREventParams.SHOT_PASSION_MULTIPLIER, stage)
            else:
                self._stopSounds()

    def _getComponentName(self):
        return BattleRoyaleComponents.SHOT_PASSION

    def _getEquipmentName(self):
        return BattleRoyaleEquipments.SHOT_PASSION

    def _stopSounds(self):
        if self.__isActive:
            BREventParams.setEventParam(BREventParams.SHOT_PASSION_MULTIPLIER, 0)
            BREvents.playSound(BREvents.BR_SHOT_PASSION_AFFECT_OFF)
            self.__isActive = False
