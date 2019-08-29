# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/br_battle_sounds.py
import BigWorld
import WWISE
from gui.battle_control.controllers.period_ctrl import IAbstractPeriodView
from gui.battle_control.controllers.spawn_ctrl import ISpawnListener
from gui.doc_loaders.battle_royale_settings_loader import getBattleRoyaleSettings
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE, TIMER_VIEW_STATE, COUNTDOWN_STATE
from helpers.CallbackDelayer import CallbackDelayer
from constants import LootAction
from gui.shared.events import AirDropEvent
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.battle_control.controllers.radar_ctrl import IRadarListener
from gui.battle_control.controllers.progression_ctrl import IProgressionListener
from gui.battle_control.controllers.vehicles_count_ctrl import IVehicleCountListener
from gui.battle_control.view_components import IViewComponentsCtrlListener
from items import getTypeOfCompactDescr
from gui.shared.gui_items.Vehicle import Vehicle
from gui.shared.gui_items import GUI_ITEM_TYPE, isItemVehicleHull
from constants import ARENA_PERIOD
from gui.battle_control.battle_constants import FEEDBACK_EVENT_ID
from constants import EQUIPMENT_STAGES

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
    INSTALL_MODULE = {GUI_ITEM_TYPE.RADIO: 'BR_upgrade_radio',
     GUI_ITEM_TYPE.GUN: 'BR_upgrade_weapons',
     GUI_ITEM_TYPE.ENGINE: 'BR_upgrade_engine',
     GUI_ITEM_TYPE.TURRET: 'BR_upgrade_turret'}
    INSTALL_MODULE_CHASSIS = 'BR_upgrade_treads'
    INSTALL_MODULE_HULL = 'BR_upgrade_hull'
    PHASE_MIDDLE = 'BR_combat_phase_activated'
    PLAYER_LEVEL_MIDDLE = 'BR_combat_phase_our'
    ENEMIES_AMOUNT = {10: 'BR_enemy_remained_10',
     5: 'BR_enemy_remained_05',
     2: 'BR_enemy_remained_02',
     1: 'BR_enemy_remained_01'}
    ENEMY_KILLED = 'BR_enemy_killed'
    BATTLE_STARTED = 'BR_start_battle'
    BATTLE_WIN = 'BR_win'
    BATTLE_DEFEAT = 'BR_defeat'
    EQUIPMENT_ACTIVATED = {'large_repairkit_battle_royale': 'BR_perk_repair_activation',
     'regenerationKit': 'BR_perk_hp_restore_activation',
     'selfBuff': 'BR_perk_selfbuff_activation',
     'trappoint': 'BR_perk_trap_slowdown_activation',
     'healPoint': 'BR_perk_healzone_activation',
     'bomber_battle_royale': 'BR_perk_airstrike_activation',
     'smoke_battle_royale': 'BR_perk_smoke_activation'}
    EQUIPMENT_DEACTIVATED = {'regenerationKit': 'BR_perk_hp_restore_deactivation',
     'selfBuff': 'BR_perk_selfbuff_deactivation'}
    TRAP_POINT_ENTER = 'BR_perk_trap_slowdown_affects'
    TRAP_POINT_EXIT = 'BR_perk_trap_slowdown_affects_off'

    @staticmethod
    def playSound(eventName):
        WWISE.WW_eventGlobal(eventName)


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


class BRBattleSoundController(object):

    def __init__(self):
        self.__soundPlayers = (LootSoundPlayer(),
         DeathzoneSoundPlayer(),
         AirDropSoundPlayer(),
         StatusSoundPlayer(),
         ArenaTypeSoundPlayer(),
         DeathScreenSoundPlayer())

    def init(self):
        for player in self.__soundPlayers:
            player.init()

    def destroy(self):
        for player in self.__soundPlayers:
            player.destroy()

        self.__soundPlayers = None
        return


class RadarSoundPlayer(IRadarListener):

    def radarInfoReceived(self, radarInfo):
        isPlayer = BigWorld.player().playerVehicleID == radarInfo[0]
        eventName = BREvents.RADAR_ACTIVATED if isPlayer else BREvents.RADAR_ACTIVATED_SQUAD
        BREvents.playSound(eventName)


class LootSoundPlayer(object):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def init(self):
        ctrl = self.__sessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onVehicleStateUpdated += self.__onVehicleStateUpdated
        return

    def destroy(self):
        ctrl = self.__sessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onVehicleStateUpdated -= self.__onVehicleStateUpdated
        return

    def __onVehicleStateUpdated(self, state, value):
        if state == VEHICLE_VIEW_STATE.LOOT:
            _, action, _ = value
            if action == LootAction.PICKUP_STARTED:
                BREvents.playSound(BREvents.LOOT_PICKUP_START)
            elif action == LootAction.PICKUP_SUCCEEDED:
                BREvents.playSound(BREvents.LOOT_PICKUP_DONE)
            elif action == LootAction.PICKUP_FAILED:
                BREvents.playSound(BREvents.LOOT_PICKUP_STOP)


class DeathScreenSoundPlayer(object):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def init(self):
        deathScreenCtrl = self.__sessionProvider.dynamic.deathScreen
        if deathScreenCtrl:
            deathScreenCtrl.onShowDeathScreen += self.__onShowDeathScreen

    def destroy(self):
        deathScreenCtrl = self.__sessionProvider.dynamic.deathScreen
        if deathScreenCtrl:
            deathScreenCtrl.onShowDeathScreen -= self.__onShowDeathScreen

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


class DeathzoneSoundPlayer(object):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(DeathzoneSoundPlayer, self).__init__()
        self.__isInZone = None
        return

    def init(self):
        ctrl = self.__sessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onVehicleStateUpdated += self.__onVehicleStateUpdated
        return

    def destroy(self):
        ctrl = self.__sessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onVehicleStateUpdated -= self.__onVehicleStateUpdated
        return

    def __onVehicleStateUpdated(self, state, value):
        if state == VEHICLE_VIEW_STATE.DEATHZONE_TIMER:
            if value.level is None and value.isCausingDamage:
                vehicle = self.__sessionProvider.shared.vehicleState.getControllingVehicle()
                isAlive = vehicle is not None and vehicle.isAlive()
                zoneLevel = TIMER_VIEW_STATE.CRITICAL if isAlive else None
            else:
                zoneLevel = value.level
            if zoneLevel != self.__isInZone:
                if self.__isInZone:
                    BREvents.playSound(BREvents.DEATHZONE_EXIT[self.__isInZone])
                    BRStates.setState(BRStates.STATE_DEATHZONE[self.__isInZone], BRStates.STATE_DEATHZONE_OUT[self.__isInZone])
                if zoneLevel:
                    BREvents.playSound(BREvents.DEATHZONE_ENTER[zoneLevel])
                    BRStates.setState(BRStates.STATE_DEATHZONE[zoneLevel], BRStates.STATE_DEATHZONE_IN[zoneLevel])
                self.__isInZone = zoneLevel
        return


class InstallModuleSoundPlayer(IProgressionListener, IViewComponentsCtrlListener):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(InstallModuleSoundPlayer, self).__init__()
        self.__vehicle = None
        arenaDP = self.__sessionProvider.getArenaDP()
        self.__vehicle = Vehicle(strCompactDescr=arenaDP.getVehicleInfo().vehicleType.strCompactDescr)
        return

    def detachedFromCtrl(self, _):
        self.__vehicle = None
        return

    def setVehicleChangeResponse(self, itemCD, success):
        if not success:
            return
        else:
            typeCD = getTypeOfCompactDescr(itemCD)
            if typeCD == GUI_ITEM_TYPE.CHASSIS:
                if isItemVehicleHull(itemCD, self.__vehicle):
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
    __PLAYER_MIDDLE_LEVEL = 5.0

    def __init__(self):
        super(LevelSoundPlayer, self).__init__()
        self.__level = None
        return

    def setLevel(self, level, *args):
        progressionCtrl = self.__sessionProvider.dynamic.progression
        if self.__level != level:
            self.__level is not None and level < progressionCtrl.maxLevel and BREvents.playSound(BREvents.LEVEL_UP)
        if self.__level is not None:
            if self.__level < self.__PLAYER_MIDDLE_LEVEL <= level:
                BREvents.playSound(BREvents.PLAYER_LEVEL_MIDDLE)
            self.__level = level
        return

    def onMaxLvlAchieved(self):
        BREvents.playSound(BREvents.LEVEL_UP_MAX)


class EnemiesAmountSoundPlayer(IVehicleCountListener):

    def __init__(self):
        super(EnemiesAmountSoundPlayer, self).__init__()
        self.__enemiesCount = None
        self.__frags = None
        return

    def setEnemiesCount(self, vehicles, teams):
        if self.__enemiesCount is not None and vehicles != self.__enemiesCount:
            eventName = BREvents.ENEMIES_AMOUNT.get(vehicles)
            if eventName is not None:
                BREvents.playSound(eventName)
        self.__enemiesCount = vehicles
        return

    def setFrags(self, frags, isPlayerVehicle):
        if isPlayerVehicle:
            if self.__frags is not None and self.__frags != frags:
                BREvents.playSound(BREvents.ENEMY_KILLED)
            self.__frags = frags
        return


class PhaseSoundPlayer(IProgressionListener, IVehicleCountListener):
    __PHASE_FINAL_ENEMIES_COUNT = 2
    __PHASE_MIDDLE_AVERAGE_LEVEL = 5.0

    def __init__(self):
        super(PhaseSoundPlayer, self).__init__()
        self.__averageLevel = None
        self.__enemyTeamsCount = None
        self.__updatePhase()
        return

    def setEnemiesCount(self, vehicles, teams):
        self.__enemyTeamsCount = teams
        self.__updatePhase()

    def setAverageBattleLevel(self, level):
        if self.__averageLevel is not None:
            self.__averageLevel < self.__PHASE_MIDDLE_AVERAGE_LEVEL <= level and BREvents.playSound(BREvents.PHASE_MIDDLE)
        self.__averageLevel = level
        self.__updatePhase()
        return

    def __updatePhase(self):
        if self.__enemyTeamsCount is not None and self.__enemyTeamsCount <= self.__PHASE_FINAL_ENEMIES_COUNT:
            BRStates.setState(BRStates.STATE_PHASE, BRStates.STATE_PHASE_FINAL)
        elif self.__averageLevel is not None and self.__PHASE_MIDDLE_AVERAGE_LEVEL <= self.__averageLevel:
            BRStates.setState(BRStates.STATE_PHASE, BRStates.STATE_PHASE_MIDDLE)
        else:
            BRStates.setState(BRStates.STATE_PHASE, BRStates.STATE_PHASE_START)
        return


class StatusSoundPlayer(CallbackDelayer):
    __ON_OBSERVED_DURATION = 20.0
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(StatusSoundPlayer, self).__init__()
        self.__seenEnemies = set()
        self.__isObservedByEnemy = False

    def init(self):
        ctrl = self.__sessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onVehicleStateUpdated += self.__onVehicleStateUpdated
        ctrl = self.__sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onVehicleFeedbackReceived += self.__onVehicleFeedbackReceived
            ctrl.onMinimapVehicleAdded += self.__onVehicleEnterWorld
            ctrl.onMinimapVehicleRemoved += self.__onVehicleLeaveWorld
        self.__updateStatus()
        return

    def destroy(self):
        ctrl = self.__sessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onVehicleStateUpdated -= self.__onVehicleStateUpdated
        ctrl = self.__sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onVehicleFeedbackReceived -= self.__onVehicleFeedbackReceived
            ctrl.onMinimapVehicleAdded -= self.__onVehicleEnterWorld
            ctrl.onMinimapVehicleRemoved -= self.__onVehicleLeaveWorld
        self.__seenEnemies.clear()
        super(StatusSoundPlayer, self).destroy()
        return

    def __onVehicleFeedbackReceived(self, eventID, vehicleID, _):
        if eventID == FEEDBACK_EVENT_ID.VEHICLE_DEAD:
            self.__seenEnemies.discard(vehicleID)
            self.__updateStatus()

    def __onVehicleLeaveWorld(self, vId):
        self.__seenEnemies.discard(vId)
        self.__updateStatus()

    def __onVehicleStateUpdated(self, state, value):
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
        if period == ARENA_PERIOD.PREBATTLE:
            BREvents.playSound(BREvents.BATTLE_STARTED)
        else:
            self.__checkBattleEnd()

    def setAdditionalInfo(self, additionalInfo):
        self.__winStatus = additionalInfo.getWinStatus()
        self.__checkBattleEnd()

    def setPlayerVehicleAlive(self, isAlive):
        if self.__isAlive and not isAlive:
            BREvents.playSound(BREvents.BATTLE_DEFEAT)
        self.__isAlive = isAlive

    def __checkBattleEnd(self):
        if self.__period == ARENA_PERIOD.AFTERBATTLE and self.__winStatus is not None and self.__isAlive:
            eventName = BREvents.BATTLE_WIN if self.__winStatus.isWin() else BREvents.BATTLE_DEFEAT
            BREvents.playSound(eventName)
        return


class PostmortemSoundPlayer(IVehicleCountListener):

    def setPlayerVehicleAlive(self, isAlive):
        stateValue = BRStates.STATE_POSTMORTEM_OFF if isAlive else BRStates.STATE_POSTMORTEM_ON
        BRStates.setState(BRStates.STATE_POSTMORTEM, stateValue)


class ArenaTypeSoundPlayer(object):

    def init(self):
        BRStates.setState(BRStates.STATE_BR, BRStates.STATE_BR_ON)

    def destroy(self):
        BRStates.setState(BRStates.STATE_BR, BRStates.STATE_BR_OFF)


class SelectRespawnSoundPlayer(ISpawnListener, IAbstractPeriodView):
    __slots__ = ('__isSpawnTimerWorking', '__isSpawnTimerStopped', '__mainTimerStopped')

    def __init__(self):
        super(SelectRespawnSoundPlayer, self).__init__()
        self.__isSpawnTimerWorking = False
        self.__isSpawnTimerStopped = False
        self.__mainTimerStopped = False

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
        selectEndingSoonTime = getBattleRoyaleSettings()['spawn']['selectEndingSoonTime']
        eventName = BREvents.SPAWN_TIMER_WARNING if timeLeft < selectEndingSoonTime else BREvents.SPAWN_TIMER
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
        if ctrl is not None:
            ctrl.onEquipmentUpdated += self.__onEquipmentUpdated
        ctrl = self.__sessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onVehicleStateUpdated += self.__onVehicleStateUpdated
        return

    def detachedFromCtrl(self, ctrlID):
        self.__currentEquipment = None
        ctrl = self.__sessionProvider.shared.equipments
        if ctrl is not None:
            ctrl.onEquipmentUpdated -= self.__onEquipmentUpdated
        ctrl = self.__sessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onVehicleStateUpdated -= self.__onVehicleStateUpdated
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

    def __onVehicleStateUpdated(self, state, value):
        if state == VEHICLE_VIEW_STATE.INSPIRE:
            if value.get('isInactivation') is None:
                BREvents.playSound(BREvents.EQUIPMENT_DEACTIVATED['selfBuff'])
                self.__currentEquipment.discard('selfBuff')
        return

    def setPlayerVehicleAlive(self, isAlive):
        if not isAlive:
            for eq in self.__currentEquipment:
                eventName = BREvents.EQUIPMENT_DEACTIVATED.get(eq)
                if eventName is not None:
                    BREvents.playSound(eventName)

        return
