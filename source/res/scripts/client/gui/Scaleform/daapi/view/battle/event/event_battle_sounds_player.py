# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/event_battle_sounds_player.py
from math import ceil
import WWISE
import BigWorld
import SoundGroups
import TriggersManager
from wotdecorators import condition
from constants import ECP_HUD_INDEXES, ECP_HUD_TOGGLES, EVENT_BOT_ROLE, ARENA_PERIOD, EVENT, EVENT_BOT_NAME, EQUIPMENT_STAGES, VEHICLE_HIT_FLAGS, EVENT_BOSSFIGHT_PHASE
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE, FEEDBACK_EVENT_ID
from gui.battle_control.avatar_getter import getSoundNotifications, isVehicleAlive, getPlayerVehicleID
from gui.battle_control.controllers.period_ctrl import IAbstractPeriodView
from gui.battle_control.view_components import IViewComponentsCtrlListener
from helpers import dependency, isPlayerAvatar
from helpers.CallbackDelayer import CallbackDelayer
from skeletons.gui.game_event_controller import IGameEventController
from skeletons.account_helpers.settings_core import ISettingsCore
from items import vehicles
from vehicle_systems.tankStructure import TankSoundObjectsIndexes
from account_helpers.settings_core.settings_constants import OnceOnlyHints
from gui.Scaleform.daapi.view.battle.event.components import GameEventComponent

def _playSoundNotification(notification, vehicleID=None, checkFn=None, position=None, boundVehicleID=None):
    if not notification:
        return
    else:
        notifications = getSoundNotifications()
        if notifications is not None:
            notifications.play(notification, vehicleID, checkFn, position, boundVehicleID)
        return


class _SoundsPlayer(IAbstractPeriodView, IViewComponentsCtrlListener, GameEventComponent):
    WIN_SOUND_ENV_NUM = 5
    currentSoundEnvID = property(lambda self: self.__currentSoundEnvID)
    isCorrectSoundEnvironment = property(lambda self: self.__currentSoundEnvID != EVENT.INVALID_SOUND_ENVIRONMENT_ID)
    isFight = property(lambda self: self.currentSoundEnvID != self.WIN_SOUND_ENV_NUM)

    def __init__(self):
        super(_SoundsPlayer, self).__init__()
        GameEventComponent.__init__(self)
        self.__currentSoundEnvID = EVENT.INVALID_SOUND_ENVIRONMENT_ID

    def detachedFromCtrl(self, ctrlID):
        self._finalize()

    def setPeriod(self, period):
        if period == ARENA_PERIOD.BATTLE and not self.isCorrectSoundEnvironment:
            self._initialize()
        elif period == ARENA_PERIOD.AFTERBATTLE:
            self._finalize()

    def _initialize(self):
        GameEventComponent.start(self)

    @condition('isCorrectSoundEnvironment')
    def _finalize(self):
        GameEventComponent.stop(self)

    def _onEnvironmentEventIDUpdate(self, eventEnvID):
        GameEventComponent._onEnvironmentEventIDUpdate(self, eventEnvID)
        self.__currentSoundEnvID = EVENT.INVALID_SOUND_ENVIRONMENT_ID if self.currentEventEnvID == EVENT.INVALID_ENVIRONMENT_ID else self.environmentData.getSoundEnvironmentID(self.currentEventEnvID)

    @condition('isCorrectSoundEnvironment')
    @condition('isFight')
    def _onTrigger(self, eventId, extra):
        GameEventComponent._onTrigger(self, eventId, extra)


class PeriodSoundPlayer(_SoundsPlayer):
    _gameEventController = dependency.descriptor(IGameEventController)
    _settingsCore = dependency.descriptor(ISettingsCore)
    RTPC_NAME = 'RTPC_ext_hw19_world'
    STATE_NAME = 'STATE_ev_halloween_2019_world'
    BATTLE_STATE = 'STATE_ev_halloween_2019_world_m{}'
    GAMEPLAY_START = 'hw21_fx_notification_gameplay_start'
    GAMEPLAY_STOP = 'hw21_fx_notification_gameplay_stop'
    NOTIFICATION_WORLD_SWITCH = 'hw21_vo_notification_world_{}'
    NOTIFICATION_WORLD_BOSSFIGHT_SWITCH = 'hw21_vo_notification_world_{}_{}'
    NOTIFICATION_WORLD_WIN = 'hw21_fx_notification_world_after_win'
    PLAYER_TELEPORT = 'hw21_fx_notification_player_teleport'
    BOSSFIGHT_DEFAULT_STATE = 1

    def _initialize(self):
        super(PeriodSoundPlayer, self)._initialize()
        _playSoundNotification(self.GAMEPLAY_START)

    def _finalize(self):
        super(PeriodSoundPlayer, self)._finalize()
        _playSoundNotification(self.GAMEPLAY_STOP)

    def _onEnvironmentEventIDUpdate(self, eventEnvID):
        soundEnvID = self.environmentData.getSoundEnvironmentID(eventEnvID) if eventEnvID != EVENT.INVALID_ENVIRONMENT_ID else 0
        if self.currentEventEnvID != eventEnvID and self.currentSoundEnvID != soundEnvID:
            if soundEnvID == self.WIN_SOUND_ENV_NUM:
                notification = self.NOTIFICATION_WORLD_WIN
            else:
                if eventEnvID == self.environmentData.getBossFightEnvironmentID():
                    WWISE.WW_setState(self.STATE_NAME, self.BATTLE_STATE.format(self.BOSSFIGHT_DEFAULT_STATE))
                    difficulty = self._gameEventController.getSelectedDifficultyLevel()
                    serverSettings = self._settingsCore.serverSettings
                    if not serverSettings.getOnceOnlyHintsSetting(OnceOnlyHints.EVENT_BOSSFIGHT_HINT, default=int(False)):
                        serverSettings.setOnceOnlyHintsSettings({OnceOnlyHints.EVENT_BOSSFIGHT_HINT: int(True)})
                        notification = self.NOTIFICATION_WORLD_SWITCH.format(soundEnvID)
                    else:
                        notification = self.NOTIFICATION_WORLD_BOSSFIGHT_SWITCH.format(soundEnvID, difficulty)
                else:
                    self.__setRTPCValue(soundEnvID)
                    notification = self.NOTIFICATION_WORLD_SWITCH.format(soundEnvID) if soundEnvID else ''
                if eventEnvID > 0:
                    _playSoundNotification(self.PLAYER_TELEPORT)
            if notification:
                _playSoundNotification(notification)
        super(PeriodSoundPlayer, self)._onEnvironmentEventIDUpdate(eventEnvID)

    def __setRTPCValue(self, soundEnvID):
        rtcpArenaWorldParam = WWISE.WW_getRTPCValue(self.RTPC_NAME)
        rtcpArenaWorldParam.set(soundEnvID)
        WWISE.WW_setState(self.STATE_NAME, self.BATTLE_STATE.format(soundEnvID))


class TimerSoundPlayer(_SoundsPlayer):
    EVENT_TIMER_NOTIFICATION_TIME = 60
    EVENT_TIMER_SOUND_NOTIFICATION_TEMPLATE = 'hw21_one_minute_left_{}'
    EVENT_TIMER_SOUND_NOTIFICATION_WORLDS = (1, 2, 3, 4, 6)

    def __init__(self):
        super(TimerSoundPlayer, self).__init__()
        self.__lastTimerNotificationEnvId = (EVENT.INVALID_SOUND_ENVIRONMENT_ID, EVENT.INVALID_BOSSFIGHT_PHASE_ID)

    def _initialize(self):
        super(TimerSoundPlayer, self)._initialize()
        ctrl = self.sessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onUpdateScenarioTimer += self.__onUpdateScenarioTimer
        return

    def _finalize(self):
        ctrl = self.sessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onUpdateScenarioTimer -= self.__onUpdateScenarioTimer
        super(TimerSoundPlayer, self)._finalize()
        return

    @condition('isCorrectSoundEnvironment')
    @condition('isFight')
    def __onUpdateScenarioTimer(self, waitTime, *args):
        if waitTime == self.EVENT_TIMER_NOTIFICATION_TIME and self.currentSoundEnvID in self.EVENT_TIMER_SOUND_NOTIFICATION_WORLDS and self.currentSoundEnvID != self.__lastTimerNotificationEnvId:
            self.__lastTimerNotificationEnvId = (self.currentSoundEnvID, self.currentBossFightPhase)
            _playSoundNotification(self.EVENT_TIMER_SOUND_NOTIFICATION_TEMPLATE.format(self.currentSoundEnvID), checkFn=lambda envID=self.currentEventEnvID, bossfight=self.currentBossFightPhase: envID == self.currentEventEnvID and bossfight == self.currentBossFightPhase)


class BotVehicleSoundPlayer(_SoundsPlayer):
    BOT_SPOTTED_SOUND = {EVENT_BOT_ROLE.BOSS: 'hw21_vo_notification_boss_insight',
     EVENT_BOT_ROLE.BOMBER: 'hw21_vo_notification_bomber_insight',
     EVENT_BOT_ROLE.QUEEN_BOMBER: 'hw21_vo_notification_queen_bomber_insight'}
    BOT_SPAWN_SOUND_BY_ROLE = {EVENT_BOT_ROLE.HUNTER: 'hw21_fx_notification_hunter',
     EVENT_BOT_ROLE.BOMBER: 'hw21_fx_notification_yorsh',
     EVENT_BOT_ROLE.RUNNER: 'hw21_fx_notification_bunny',
     EVENT_BOT_ROLE.RUNNER_SHOOTER: 'hw21_fx_notification_bunny',
     EVENT_BOT_ROLE.SENTRY: 'hw21_fx_notification_default',
     EVENT_BOT_ROLE.QUEEN_BOMBER: 'hw21_fx_notification_bomber_queen_spawn'}

    def __init__(self):
        super(BotVehicleSoundPlayer, self).__init__()
        self.__vehicleSpottedCountData = dict()

    def _initialize(self):
        super(BotVehicleSoundPlayer, self)._initialize()
        if self.isCorrectSoundEnvironment:
            if self.enemySpottedData is not None:
                self.enemySpottedData.onEnemySpottedDataUpdate += self.__onEnemySpottedDataUpdate
            player = BigWorld.player()
            player.onVehicleSpawnEffectStarted += self.__vehicleSpawnSoundNotification
        return

    def _finalize(self):
        self.__vehicleSpottedCountData = dict()
        if self.enemySpottedData is not None:
            self.enemySpottedData.onEnemySpottedDataUpdate -= self.__onEnemySpottedDataUpdate
        if isPlayerAvatar():
            player = BigWorld.player()
            player.onVehicleSpawnEffectStarted -= self.__vehicleSpawnSoundNotification
        super(BotVehicleSoundPlayer, self)._finalize()
        return

    def _onEnvironmentEventIDUpdate(self, eventEnvID):
        super(BotVehicleSoundPlayer, self)._onEnvironmentEventIDUpdate(eventEnvID)
        self.__vehicleSpottedCountData.update(dict(((botRole, 0) for botRole in self.BOT_SPOTTED_SOUND.iterkeys() if botRole != EVENT_BOT_ROLE.BOSS)))

    @condition('isCorrectSoundEnvironment')
    def __onEnemySpottedDataUpdate(self, diff):
        isBossFight = self.currentBossFightPhase != EVENT.INVALID_BOSSFIGHT_PHASE_ID
        for botRole in diff.iterkeys():
            if botRole not in self.BOT_SPOTTED_SOUND or isBossFight and botRole == EVENT_BOT_ROLE.BOSS or botRole == EVENT_BOT_ROLE.BOMBER and self.__getQueenBomberID():
                continue
            if not self.__vehicleSpottedCountData.get(botRole, False):
                self.__vehicleSpottedCountData[botRole] = int(diff[botRole])
                _playSoundNotification(self.BOT_SPOTTED_SOUND[botRole], checkFn=lambda envID=self.currentEventEnvID, bossfight=self.currentBossFightPhase: envID == self.currentEventEnvID and bossfight == self.currentBossFightPhase)

    @condition('isCorrectSoundEnvironment')
    def __vehicleSpawnSoundNotification(self, position, botRole):
        if botRole in self.BOT_SPAWN_SOUND_BY_ROLE and self.currentSoundEnvID > 1:
            _playSoundNotification(self.BOT_SPAWN_SOUND_BY_ROLE[botRole], position=position)

    def __getQueenBomberID(self):
        for vehInfo in self.sessionProvider.getArenaDP().getVehiclesInfoIterator():
            vehicleName = vehicles.getVehicleType(vehInfo.vehicleType.compactDescr).name
            if vehicleName == EVENT_BOT_NAME.QUEEN_BOMBER:
                return vehInfo.vehicleID


class MatterCollectingSoundPlayer(_SoundsPlayer):
    NOT_COLLECTING_WARNING_NOTIFICATION = 'hw21_vo_notification_player_is_not_collecting'
    ENOUGH_MATTER_COLLECTED_NOTIFICATION = 'hw21_vo_notification_enough_matter_was_collected'
    FILL_NOTIFICATIONS_BY_ENV_ID = {0: [(1.0, 'hw21_vo_notification_collector_fill_100')],
     1: [(0.5, 'hw21_vo_notification_collector_fill_50'), (1.0, 'hw21_vo_notification_collector_fill_100')],
     2: [(0.5, 'hw21_vo_notification_collector_fill_50'), (0.75, 'hw21_vo_notification_collector_fill_75'), (1.0, 'hw21_vo_notification_collector_fill_100')]}
    NOT_COLLECTING_WARNING_SOUND_ENV_IDS = (1, 2, 3, 4)
    NOT_COLLECTING_WARNING_TIME = 90

    def __init__(self):
        super(MatterCollectingSoundPlayer, self).__init__()
        self.__soulsByVehicle = {}
        self.__wasEnoughSouls = False
        self.__collectorCollected = None
        self.__collectorCapacity = None
        self.__collectorECPIdy = None
        self.__collectorECPPosition = None
        self.__lastNotifiedSoulsQuantity = 0
        return

    def _initialize(self):
        super(MatterCollectingSoundPlayer, self)._initialize()
        if self.isCorrectSoundEnvironment:
            self.souls.onSoulsChanged += self.__vehicleSoulsWasUpdated
            self.soulCollector.onSoulsChanged += self.__collectorSoulsWasUpdated
            ecpComp = getattr(self.sessionProvider.arenaVisitor.getComponentSystem(), 'ecp', None)
            if ecpComp is not None:
                ecpComp.ecpHUDEvents[ECP_HUD_INDEXES.marker][ECP_HUD_TOGGLES.on] += self.__onCollectorAdded
                ecpComp.ecpHUDEvents[ECP_HUD_INDEXES.marker][ECP_HUD_TOGGLES.off] += self.__onCollectorRemoved
                for ecp in ecpComp.getECPEntities().values():
                    self.__onCollectorAdded(ecp)

        return

    def _finalize(self):
        self.souls.onSoulsChanged -= self.__vehicleSoulsWasUpdated
        self.soulCollector.onSoulsChanged -= self.__collectorSoulsWasUpdated
        ecpComp = getattr(self.sessionProvider.arenaVisitor.getComponentSystem(), 'ecp', None)
        if ecpComp is not None:
            ecpComp.ecpHUDEvents[ECP_HUD_INDEXES.marker][ECP_HUD_TOGGLES.on] -= self.__onCollectorAdded
            ecpComp.ecpHUDEvents[ECP_HUD_INDEXES.marker][ECP_HUD_TOGGLES.off] -= self.__onCollectorRemoved
        super(MatterCollectingSoundPlayer, self)._finalize()
        return

    def _onEnvironmentEventIDUpdate(self, eventEnvID):
        super(MatterCollectingSoundPlayer, self)._onEnvironmentEventIDUpdate(eventEnvID)
        if self.currentSoundEnvID in self.NOT_COLLECTING_WARNING_SOUND_ENV_IDS:
            self.__wasEnoughSouls = False
            self.__lastNotifiedSoulsQuantity = 0
            self.__playerIsNotCollectingMatter()

    def __vehicleSoulsWasUpdated(self, diff):
        totalBefore = sum(self.__soulsByVehicle.itervalues())
        for vehId, (souls, _) in diff.iteritems():
            vehicle = BigWorld.entities.get(vehId)
            if vehicle and vehicle.isAlive():
                self.__soulsByVehicle[vehId] = souls
            self.__soulsByVehicle[vehId] = 0

        if self.__collectorCapacity is not None and self.__collectorCollected is not None:
            totalCurrent = sum(self.__soulsByVehicle.itervalues())
            if totalCurrent > totalBefore:
                isEnough = totalCurrent >= self.__collectorCapacity - self.__collectorCollected
                wasEnough, self.__wasEnoughSouls = self.__wasEnoughSouls, isEnough
                if isEnough and not wasEnough:
                    self.__enoughMatterWasCollected()
        return

    def __collectorSoulsWasUpdated(self, diff):
        self.__collectorCollected, self.__collectorCapacity = (None, None)
        if self.soulCollector is not None and self.__collectorECPIdy is not None:
            soulCollectorsData = self.soulCollector.getSoulCollectorData()
            if soulCollectorsData is not None and isinstance(soulCollectorsData, dict):
                collectorSoulsInfo = soulCollectorsData.get(self.__collectorECPIdy)
                if collectorSoulsInfo is not None and collectorSoulsInfo[1] > 0:
                    self.__onCollectorFill(*collectorSoulsInfo)
        return

    def __onCollectorFill(self, *args):
        self.__collectorCollected, self.__collectorCapacity = args
        collectorPrev, self.__lastNotifiedSoulsQuantity = self.__lastNotifiedSoulsQuantity, self.__collectorCollected
        notifications = self.FILL_NOTIFICATIONS_BY_ENV_ID.get(self.currentEventEnvID, [])
        for notification in (notification for coef, notification in notifications if collectorPrev < ceil(coef * self.__collectorCapacity) <= self.__collectorCollected):
            _playSoundNotification(notification)

    def __onCollectorAdded(self, ecp):
        self.__collectorECPIdy = ecp.id
        self.__collectorECPPosition = ecp.position
        self.__collectorSoulsWasUpdated(None)
        return

    def __onCollectorRemoved(self, ecp):
        if self.__collectorECPIdy == ecp.id:
            self.__collectorECPIdy = None
            self.__collectorECPPosition = None
            self.__collectorSoulsWasUpdated(None)
        return

    @condition('isCorrectSoundEnvironment')
    @condition('isFight')
    def __playerIsNotCollectingMatter(self):
        _playSoundNotification(self.NOT_COLLECTING_WARNING_NOTIFICATION, checkFn=lambda envID=self.currentEventEnvID, souls=self.souls.getSouls(getPlayerVehicleID()): souls >= self.souls.getSouls(getPlayerVehicleID()) and envID == self.environmentData.getCurrentEnvironmentID() and isVehicleAlive())

    @condition('isCorrectSoundEnvironment')
    @condition('isFight')
    def __enoughMatterWasCollected(self):
        if self.currentSoundEnvID in self.NOT_COLLECTING_WARNING_SOUND_ENV_IDS:
            _playSoundNotification(self.ENOUGH_MATTER_COLLECTED_NOTIFICATION, checkFn=lambda envID=self.currentEventEnvID: envID == self.environmentData.getCurrentEnvironmentID())


class VehicleDevicesSoundPlayer(_SoundsPlayer, TriggersManager.ITriggerListener):
    SOULS_ARE_ON_VEHICLE_EVENT = 'ev_halloween_2019_gameplay_device'
    VEHICLE_DEVICE_RTCP = 'RTPC_ext_hw19_device_capacity'
    MAX_VEHICLE_SOULS_FOR_SOUND = 150

    def __init__(self):
        super(VehicleDevicesSoundPlayer, self).__init__()
        self.__vehSounds = {}

    def _initialize(self):
        super(VehicleDevicesSoundPlayer, self)._initialize()
        if self.isCorrectSoundEnvironment:
            self.souls.onSoulsChanged += self.__updateVehicleDevice
            TriggersManager.g_manager.addListener(self)

    def _finalize(self):
        self.souls.onSoulsChanged -= self.__updateVehicleDevice
        TriggersManager.g_manager.delListener(self)
        super(VehicleDevicesSoundPlayer, self)._finalize()

    def _onEnvironmentEventIDUpdate(self, eventEnvID):
        super(VehicleDevicesSoundPlayer, self)._onEnvironmentEventIDUpdate(eventEnvID)
        if self.isCorrectSoundEnvironment:
            for vInfo in self.sessionProvider.getArenaDP().getVehiclesInfoIterator():
                if vInfo.team == EVENT.PLAYERS_TEAM:
                    self.__updateVehicleDevice(diff={vInfo.vehicleID: (0, None)})

        return None

    @condition('isCorrectSoundEnvironment')
    def __updateVehicleDevice(self, diff):
        for vehicleID in diff.iterkeys():
            if vehicleID not in self.__vehSounds:
                vehicle = BigWorld.entities.get(vehicleID)
                if vehicle is not None and vehicle.publicInfo['team'] == BigWorld.player().team and vehicle.appearance is not None and vehicle.appearance.engineAudition is not None:
                    engineAudition = vehicle.appearance.engineAudition
                    self.__vehSounds[vehicleID] = engineAudition.getSoundObject(TankSoundObjectsIndexes.ENGINE)
                    self.__vehSounds[vehicleID].play(self.SOULS_ARE_ON_VEHICLE_EVENT)
                    self.__vehSounds[vehicleID].setRTPC(self.VEHICLE_DEVICE_RTCP, 0)
            souls = self.souls.getSouls(vehicleID)
            if souls and vehicleID in self.__vehSounds:
                fillPercentage = int(100.0 * souls / self.MAX_VEHICLE_SOULS_FOR_SOUND)
                self.__vehSounds[vehicleID].setRTPC(self.VEHICLE_DEVICE_RTCP, max(1, min(100, fillPercentage)))

        return

    @condition('isCorrectSoundEnvironment')
    def onTriggerActivated(self, params):
        if params['type'] == TriggersManager.TRIGGER_TYPE.VEHICLE_VISUAL_VISIBILITY_CHANGED:
            self.__updateVehicleDevice(diff={params['vehicleId']: (0, None)})
        return None

    @condition('isCorrectSoundEnvironment')
    def onTriggerDeactivated(self, params):
        if params['type'] == TriggersManager.TRIGGER_TYPE.VEHICLE_VISUAL_VISIBILITY_CHANGED:
            vehicleID = params['vehicleId']
            if vehicleID in self.__vehSounds:
                del self.__vehSounds[vehicleID]


class PlayerVehicleSoundPlayer(_SoundsPlayer, CallbackDelayer):
    LOW_HEALTH_NOTIFICATION = 'hw21_vo_notification_player_low_hp'
    LOW_HEALTH_PERCENTS = 0.25
    BOSS_ABILITY = 'STATE_ev_halloween_2021_ability_boss'
    BOSS_ABILITY_ENTER = 'STATE_ev_halloween_2021_ability_boss_enter'
    BOSS_ABILITY_EXIT = 'STATE_ev_halloween_2021_ability_boss_exit'
    BOSS_ABILITY_ACTIVATION = 'hw21_fx_notification_ability_death_zone_activation'
    BOSS_ABILITY_DEACTIVATION = 'hw21_fx_notification_ability_death_zone_deactivation'
    BOSS_EATING_START_NOTIFICATION = 'hw21_fx_notification_boss_eating_start'
    BOSS_EATING_STOP_NOTIFICATION = 'hw21_fx_notification_boss_eating_stop'
    RED_ZONE_OUT = 'hw21_fx_notification_red_zone_red_exit'
    RED_ZONE_IN = 'hw21_fx_notification_red_zone_red_enter'
    RED_ZONE_DAMAGE = 'hw21_fx_notification_red_zone_red_damage'
    POSTMORTEM_MODE_ON = 'hw21_fx_notification_postmortem_on'
    POSTMORTEM_MODE_OFF = 'hw21_fx_notification_postmortem_off'
    ACTIVE_EQUIPMENT_STAGES = (EQUIPMENT_STAGES.DEPLOYING,
     EQUIPMENT_STAGES.PREPARING,
     EQUIPMENT_STAGES.ACTIVE,
     EQUIPMENT_STAGES.COOLDOWN)

    def __init__(self):
        super(PlayerVehicleSoundPlayer, self).__init__()
        CallbackDelayer.__init__(self)
        self.__wasNotifiedLowVehicleHealth = False
        self.__isWithinBossAura = False
        self.__isWithinRedZone = False
        self.__isWithinBossDeathZone = False
        self.__isBossDeathZoneActivated = False
        self.__isAlive = False

    def _initialize(self):
        super(PlayerVehicleSoundPlayer, self)._initialize()
        if self.isCorrectSoundEnvironment:
            ctrl = self.sessionProvider.shared.equipments
            if ctrl is not None:
                ctrl.onEquipmentUpdated += self.__onEquipmentUpdated
            ctrl = self.sessionProvider.shared.vehicleState
            if ctrl is not None:
                ctrl.onVehicleStateUpdated += self.__onVehicleStateUpdated
            ctrl = self.sessionProvider.shared.feedback
            if ctrl is not None:
                ctrl.onPlayerFeedbackReceived += self.__onPlayerFeedbackReceived
        return

    def _finalize(self):
        CallbackDelayer.destroy(self)
        ctrl = self.sessionProvider.shared.equipments
        if ctrl is not None:
            ctrl.onEquipmentUpdated -= self.__onEquipmentUpdated
        ctrl = self.sessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onVehicleStateUpdated -= self.__onVehicleStateUpdated
        ctrl = self.sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onPlayerFeedbackReceived -= self.__onPlayerFeedbackReceived
        super(PlayerVehicleSoundPlayer, self)._finalize()
        return

    def _onEnvironmentEventIDUpdate(self, eventEnvID):
        super(PlayerVehicleSoundPlayer, self)._onEnvironmentEventIDUpdate(eventEnvID)
        self.__wasNotifiedLowVehicleHealth = False

    @condition('isCorrectSoundEnvironment')
    def __onEquipmentUpdated(self, intCD, item):
        if item.getPrevStage() == EQUIPMENT_STAGES.READY and item.getStage() in self.ACTIVE_EQUIPMENT_STAGES:
            equipment = vehicles.g_cache.equipments().get(item.getEquipmentID())
            if equipment and equipment.activationWWSoundFeedback:
                SoundGroups.g_instance.playSound2D(equipment.activationWWSoundFeedback)
        elif item.getPrevStage() == EQUIPMENT_STAGES.COOLDOWN and item.getStage() == EQUIPMENT_STAGES.READY:
            equipment = vehicles.g_cache.equipments().get(item.getEquipmentID())
            if equipment and equipment.soundNotification:
                _playSoundNotification(equipment.soundNotification)
        elif item.getPrevStage() == EQUIPMENT_STAGES.ACTIVE and item.getStage() in self.ACTIVE_EQUIPMENT_STAGES:
            equipment = vehicles.g_cache.equipments().get(item.getEquipmentID())
            if equipment and equipment.deactivationWWSoundFeedback:
                SoundGroups.g_instance.playSound2D(equipment.deactivationWWSoundFeedback)

    def __playPersonalDeathZoneSound(self, enable, strikeTime, isCallback=False):
        if enable:
            if not self.__isBossDeathZoneActivated:
                self.__isBossDeathZoneActivated = True
                _playSoundNotification(self.BOSS_ABILITY_ACTIVATION)
            timeToStrike = ceil(strikeTime - BigWorld.serverTime())
            if timeToStrike > 0:
                self.delayCallback(timeToStrike, self.__playPersonalDeathZoneSound, False, 0, True)
        elif isCallback:
            self.__isBossDeathZoneActivated = False
            _playSoundNotification(self.BOSS_ABILITY_DEACTIVATION)
        if self.__isWithinBossDeathZone != enable:
            self.__isWithinBossDeathZone = enable
            WWISE.WW_setState(self.BOSS_ABILITY, self.BOSS_ABILITY_ENTER if enable else self.BOSS_ABILITY_EXIT)

    @condition('isCorrectSoundEnvironment')
    def __onVehicleStateUpdated(self, state, value):
        notification = None
        if state == VEHICLE_VIEW_STATE.PERSONAL_DEATHZONE:
            enable, _, strikeTime = value
            self.__playPersonalDeathZoneSound(enable, strikeTime)
        elif state in (VEHICLE_VIEW_STATE.LOSE_SOULS_IN_AURA, VEHICLE_VIEW_STATE.FIRE_WITH_MESSAGE):
            if self.__isWithinBossAura != value:
                self.__isWithinBossAura = value
                notification = self.BOSS_EATING_START_NOTIFICATION if value else self.BOSS_EATING_STOP_NOTIFICATION
        elif state == VEHICLE_VIEW_STATE.DEATHZONE:
            enable, _, _ = value
            if self.__isWithinRedZone != enable:
                self.__isWithinRedZone = enable
                notification = self.RED_ZONE_IN if enable else self.RED_ZONE_OUT
        elif state in (VEHICLE_VIEW_STATE.SWITCHING, VEHICLE_VIEW_STATE.RESPAWNING):
            isSpawnRespawn = not self.sessionProvider.getCtx().isPlayerObserver() and isVehicleAlive()
            if self.__isAlive != isSpawnRespawn:
                self.__isAlive = isSpawnRespawn
                notification = self.POSTMORTEM_MODE_OFF if isSpawnRespawn else self.POSTMORTEM_MODE_ON
        elif state == VEHICLE_VIEW_STATE.HEALTH and not self.__wasNotifiedLowVehicleHealth:
            playerVehicle = BigWorld.player().getVehicleAttached()
            if playerVehicle is not None and playerVehicle.isPlayerVehicle:
                self.__updateVehicleHealth(playerVehicle)
        if notification is not None:
            _playSoundNotification(notification)
        return

    @condition('isCorrectSoundEnvironment')
    def __updateVehicleHealth(self, playerVehicle):
        if playerVehicle.health > 0 and playerVehicle.isCrewActive:
            if playerVehicle.health <= self.LOW_HEALTH_PERCENTS * playerVehicle.maxHealth:
                self.__wasNotifiedLowVehicleHealth = True
                _playSoundNotification(self.LOW_HEALTH_NOTIFICATION, checkFn=isVehicleAlive)

    @condition('isCorrectSoundEnvironment')
    def __onPlayerFeedbackReceived(self, feedback):
        for event in feedback:
            eventType = event.getType()
            if eventType == FEEDBACK_EVENT_ID.ENEMY_DAMAGED_HP_PLAYER:
                damageExtra = event.getExtra()
                if damageExtra.isDeathZone():
                    _playSoundNotification(self.RED_ZONE_DAMAGE)


class TeamFightSoundPlayer(_SoundsPlayer):
    PLAYER_DEATH_NOTIFICATION = 'hw21_vo_notification_player_death'
    REMAINED_ALLIES_NOTIFICATION_TEMPLATE = 'hw21_vo_notification_allies_{}_remained'
    PLAYER_LAST_ALIVE_EVENT = 'hw21_vo_notification_player_last_alive'
    REMAINED_ALLIES_NOTIFICATION_ON_COUNT = (1, 2, 3, 4)

    def __init__(self):
        super(TeamFightSoundPlayer, self).__init__()
        self.__alliesRemained = set()
        self.__lastAllyCountNotified = 0

    @property
    def alliesRemainedCount(self):
        return len(self.__alliesRemained)

    def _initialize(self):
        super(TeamFightSoundPlayer, self)._initialize()
        if self.isCorrectSoundEnvironment:
            ctrl = self.sessionProvider.shared.vehicleState
            if ctrl is not None:
                ctrl.onVehicleStateUpdated += self.__onVehicleStateUpdated
            ctrl = self.sessionProvider.shared.feedback
            if ctrl is not None:
                ctrl.onVehicleFeedbackReceived += self.__onVehicleFeedbackReceived
        return

    def _finalize(self):
        ctrl = self.sessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onVehicleStateUpdated -= self.__onVehicleStateUpdated
        ctrl = self.sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onVehicleFeedbackReceived -= self.__onVehicleFeedbackReceived
        super(TeamFightSoundPlayer, self)._finalize()
        return

    def _onEnvironmentEventIDUpdate(self, eventEnvID):
        super(TeamFightSoundPlayer, self)._onEnvironmentEventIDUpdate(eventEnvID)
        if self.isCorrectSoundEnvironment:
            arenaDP = self.sessionProvider.getArenaDP()
            self.__alliesRemained = {vInfo.vehicleID for vInfo in arenaDP.getVehiclesInfoIterator() if vInfo.team == EVENT.PLAYERS_TEAM}
            self.__lastAllyCountNotified = self.alliesRemainedCount

    @condition('isCorrectSoundEnvironment')
    def __onVehicleStateUpdated(self, state, _):
        vehicleID = getPlayerVehicleID()
        if state in (VEHICLE_VIEW_STATE.DESTROYED, VEHICLE_VIEW_STATE.CREW_DEACTIVATED):
            if vehicleID in self.__alliesRemained:
                self.__alliesRemained.remove(vehicleID)
                self._onDeadVehicle(vehicleID)
        elif state in (VEHICLE_VIEW_STATE.SWITCHING, VEHICLE_VIEW_STATE.RESPAWNING):
            if not self.sessionProvider.getCtx().isPlayerObserver() and isVehicleAlive():
                self.__alliesRemained.add(vehicleID)

    @condition('isCorrectSoundEnvironment')
    def __onVehicleFeedbackReceived(self, eventID, vehicleID, value):
        if eventID == FEEDBACK_EVENT_ID.VEHICLE_HEALTH:
            health, _, _ = value
            if self.sessionProvider.getArenaDP().isAlly(vehicleID):
                if health > 0:
                    self.__alliesRemained.add(vehicleID)
                elif vehicleID in self.__alliesRemained:
                    self.__alliesRemained.remove(vehicleID)
                    self._onDeadVehicle(vehicleID)
            elif health <= 0:
                self._onDeadVehicle(vehicleID)

    @condition('isCorrectSoundEnvironment')
    @condition('isFight')
    def _onDeadVehicle(self, vehicleID):
        if self.sessionProvider.getArenaDP().isAlly(vehicleID) and self.alliesRemainedCount and self.__lastAllyCountNotified != self.alliesRemainedCount:
            if vehicleID == getPlayerVehicleID():
                if self.currentBossFightPhase == EVENT.INVALID_BOSSFIGHT_PHASE_ID:
                    _playSoundNotification(self.PLAYER_DEATH_NOTIFICATION, checkFn=lambda envID=self.currentEventEnvID, phaseID=self.currentBossFightPhase: envID == self.environmentData.getCurrentEnvironmentID() and phaseID == self.currentBossFightPhase and self.alliesRemainedCount)
            elif self.alliesRemainedCount == 1 and isVehicleAlive():
                _playSoundNotification(self.PLAYER_LAST_ALIVE_EVENT, checkFn=lambda envID=self.currentEventEnvID, phaseID=self.currentBossFightPhase: envID == self.environmentData.getCurrentEnvironmentID() and phaseID == self.currentBossFightPhase and self.alliesRemainedCount and isVehicleAlive())
            elif self.alliesRemainedCount in self.REMAINED_ALLIES_NOTIFICATION_ON_COUNT:
                _playSoundNotification(self.REMAINED_ALLIES_NOTIFICATION_TEMPLATE.format(self.alliesRemainedCount), checkFn=lambda envID=self.currentEventEnvID, phaseID=self.currentBossFightPhase: envID == self.environmentData.getCurrentEnvironmentID() and phaseID == self.currentBossFightPhase and self.alliesRemainedCount)
            self.__lastAllyCountNotified = self.alliesRemainedCount


class BossFightSoundPlayer(TeamFightSoundPlayer):
    BOSS_PHASE_START_MUSIC = 'hw21_fx_music_bf_start_{}'
    BOSS_PHASE_FIRST_SHOT_EVENTS = 'hw21_fx_music_bf_shot_{}'
    ALL_PLAYERS_DIED_EVENT = 'hw21_fx_music_bf_lose_{}_{}'
    BOSS_FIGHT_WIN_EVENT = 'hw21_fx_music_bf_win'
    BOSS_ANY_DAMAGE_EVENT = 'hw21_fx_notification_boss_damage'
    BOSS_PHASE_START_NOTIFICATION = 'hw21_vo_notification_bossfight_phase'
    PLAYER_DEATH_IN_BOSSFIGHT_NOTIFICATION = 'hw21_vo_notification_player_death_bossfight'
    SUPPORTED_BOSSFIGHT_PHASES = (EVENT_BOSSFIGHT_PHASE.PHASE_1, EVENT_BOSSFIGHT_PHASE.PHASE_2)

    def __init__(self):
        super(BossFightSoundPlayer, self).__init__()
        self._bossVehicleId = 0
        self.__lastBossShotPhase = EVENT.INVALID_BOSSFIGHT_PHASE_ID

    def _initialize(self):
        super(BossFightSoundPlayer, self)._initialize()
        if self.isCorrectSoundEnvironment:
            player = BigWorld.player()
            player.onShotResultReceived += self._onPlayerShotResult

    def _finalize(self):
        if isPlayerAvatar():
            player = BigWorld.player()
            player.onShotResultReceived -= self._onPlayerShotResult
        super(BossFightSoundPlayer, self)._finalize()

    def _onEnvironmentEventIDUpdate(self, eventEnvID):
        super(BossFightSoundPlayer, self)._onEnvironmentEventIDUpdate(eventEnvID)
        if self.isCorrectSoundEnvironment:
            if not self._bossVehicleId:
                for vehInfo in self.sessionProvider.getArenaDP().getVehiclesInfoIterator():
                    vehicleName = vehicles.getVehicleType(vehInfo.vehicleType.compactDescr).name
                    if vehicleName == EVENT_BOT_NAME.BOSS:
                        self._bossVehicleId = vehInfo.vehicleID
                        break

            if self.currentBossFightPhase in self.SUPPORTED_BOSSFIGHT_PHASES:
                self._playPhaseStartEvent()

    @condition('isCorrectSoundEnvironment')
    @condition('isFight')
    def _onDeadVehicle(self, vehicleID):
        if self.currentBossFightPhase in self.SUPPORTED_BOSSFIGHT_PHASES and self._bossVehicleId:
            if vehicleID == self._bossVehicleId:
                self._bossVehicleId = 0
                _playSoundNotification(self.BOSS_FIGHT_WIN_EVENT)
            elif vehicleID == getPlayerVehicleID() and self.alliesRemainedCount and self.currentBossFightPhase != self.SUPPORTED_BOSSFIGHT_PHASES[-1]:
                _playSoundNotification(self.PLAYER_DEATH_IN_BOSSFIGHT_NOTIFICATION, checkFn=lambda envID=self.currentEventEnvID, phaseID=self.currentBossFightPhase: envID == self.currentEventEnvID and phaseID == self.currentBossFightPhase and self.alliesRemainedCount)
            elif self.sessionProvider.getArenaDP().isAlly(vehicleID) and not self.alliesRemainedCount:
                wasShotWithinPhase = self.currentBossFightPhase == self.__lastBossShotPhase
                _playSoundNotification(self.ALL_PLAYERS_DIED_EVENT.format(self.currentBossFightPhase, int(wasShotWithinPhase) + 1))

    @condition('isCorrectSoundEnvironment')
    @condition('isFight')
    def _playPhaseStartEvent(self):
        if self.currentBossFightPhase > EVENT_BOSSFIGHT_PHASE.PHASE_1:
            _playSoundNotification(self.BOSS_PHASE_START_NOTIFICATION)
        musicID = self.BOSS_PHASE_START_MUSIC.format(self.currentBossFightPhase)
        _playSoundNotification(musicID)

    @condition('isCorrectSoundEnvironment')
    @condition('isFight')
    def _onPlayerShotResult(self, vehicleID, flags):
        if self.currentBossFightPhase in self.SUPPORTED_BOSSFIGHT_PHASES and vehicleID == self._bossVehicleId:
            if flags & VEHICLE_HIT_FLAGS.IS_ANY_DAMAGE_MASK:
                _playSoundNotification(self.BOSS_ANY_DAMAGE_EVENT, vehicleID=self._bossVehicleId)
            if self.currentBossFightPhase != self.__lastBossShotPhase:
                self.__lastBossShotPhase = self.currentBossFightPhase
                _playSoundNotification(self.BOSS_PHASE_FIRST_SHOT_EVENTS.format(self.currentBossFightPhase))


class WinFightSoundPlayer(BossFightSoundPlayer):

    def __init__(self):
        super(WinFightSoundPlayer, self).__init__()
        self.__wasBossFight = False

    @condition('isCorrectSoundEnvironment')
    def _onDeadVehicle(self, vehicleID):
        if vehicleID == self._bossVehicleId:
            if self.currentBossFightPhase in self.SUPPORTED_BOSSFIGHT_PHASES:
                self._bossVehicleId = 0
            elif not self.isFight and self.__wasBossFight:
                _playSoundNotification(self.BOSS_FIGHT_WIN_EVENT, checkFn=lambda envID=self.currentEventEnvID: envID == self.currentEventEnvID)

    @condition('isCorrectSoundEnvironment')
    @condition('isFight')
    def _playPhaseStartEvent(self):
        self.__wasBossFight = True
