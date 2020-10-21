# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/event_battle_sounds_player.py
import time
import BigWorld
import Event
import SoundGroups
import TriggersManager
from constants import ECP_HUD_INDEXES, ECP_HUD_TOGGLES, EVENT_BOT_ROLE, EVENT_SOULS_CHANGE_REASON, EQUIPMENT_STAGES
from gui.Scaleform.daapi.view.battle.event.game_event_getter import GameEventGetterMixin
from gui.battle_control.avatar_getter import getSoundNotifications, isVehicleAlive
from gui.battle_control.controllers.battle_field_ctrl import IBattleFieldListener
from gui.battle_control.controllers.period_ctrl import IAbstractPeriodView
from gui.battle_control.view_components import IViewComponentsCtrlListener
from helpers import dependency
from shared_utils import CONST_CONTAINER
from skeletons.gui.battle_session import IBattleSessionProvider
from constants import ARENA_PERIOD
from constants import EVENT
from items import vehicles
from vehicle_systems.tankStructure import TankSoundObjectsIndexes

def _playSoundNotification(notification):
    if not notification:
        return
    else:
        notifications = getSoundNotifications()
        if notifications is not None:
            notifications.play(notification, vehicleIdToBind=BigWorld.player().playerVehicleID)
        return


class _SoulsInfoProvider(GameEventGetterMixin):
    battleSessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        self.onVehicleSoulsUpdate = Event.Event()
        self.onPlayersHasEnoughSouls = Event.Event()
        self.__soulsByVehicle = {}
        self.__wasEnoughSouls = False
        self.__collectorCollected = None
        self.__collectorCapacity = None
        self.__collectorECPIdy = None
        self.__collectorECPPosition = None
        super(_SoulsInfoProvider, self).__init__()
        return

    def start(self):
        self.souls.onSoulsChanged += self.__vehicleSoulsWasUpdated
        self.soulCollector.onSoulsChanged += self._collectorSoulsWasUpdated
        ecpComp = getattr(self.sessionProvider.arenaVisitor.getComponentSystem(), 'ecp', None)
        if ecpComp is not None:
            ecpComp.ecpHUDEvents[ECP_HUD_INDEXES.marker][ECP_HUD_TOGGLES.on] += self.__onCollectorAdded
            ecpComp.ecpHUDEvents[ECP_HUD_INDEXES.marker][ECP_HUD_TOGGLES.off] += self.__onCollectorRemoved
            for ecp in ecpComp.getECPEntities().values():
                self.__onCollectorAdded(ecp)

        return

    def stop(self):
        self.souls.onSoulsChanged -= self.__vehicleSoulsWasUpdated
        self.soulCollector.onSoulsChanged -= self._collectorSoulsWasUpdated
        ecpComp = getattr(self.sessionProvider.arenaVisitor.getComponentSystem(), 'ecp', None)
        if ecpComp is not None:
            ecpComp.ecpHUDEvents[ECP_HUD_INDEXES.marker][ECP_HUD_TOGGLES.on] -= self.__onCollectorAdded
            ecpComp.ecpHUDEvents[ECP_HUD_INDEXES.marker][ECP_HUD_TOGGLES.off] -= self.__onCollectorRemoved
        return

    def getSoulsInVehicle(self, vehId):
        return self.souls.getSouls(vehId)

    @property
    def totalSoulsOnVehicles(self):
        return sum(self.__soulsByVehicle.itervalues())

    @property
    def soulsInCollector(self):
        return self.__collectorCollected

    @property
    def collectorCapacity(self):
        return self.__collectorCapacity

    def __vehicleSoulsWasUpdated(self, diff):
        for vehId, (souls, reason) in diff.iteritems():
            vehicle = BigWorld.entities.get(vehId)
            if vehicle and vehicle.isAlive():
                self.__soulsByVehicle[vehId] = souls
            else:
                self.__soulsByVehicle[vehId] = 0
            self.onVehicleSoulsUpdate(vehId=vehId, souls=souls, reason=reason)

        if self.__collectorCapacity is not None and self.__collectorCollected is not None:
            isEnough = self.totalSoulsOnVehicles >= self.__collectorCapacity - self.__collectorCollected
            wasEnough, self.__wasEnoughSouls = self.__wasEnoughSouls, isEnough
            if isEnough and not wasEnough:
                self.onPlayersHasEnoughSouls()
        return

    def _collectorSoulsWasUpdated(self, diff):
        self.__collectorCollected, self.__collectorCapacity = (None, None)
        if self.soulCollector is not None and self.__collectorECPIdy is not None:
            soulCollectorsData = self.soulCollector.getSoulCollectorData()
            if soulCollectorsData is not None and isinstance(soulCollectorsData, dict):
                collectorSoulsInfo = soulCollectorsData.get(self.__collectorECPIdy)
                if collectorSoulsInfo is not None and collectorSoulsInfo[1] > 0:
                    self.__collectorCollected, self.__collectorCapacity = collectorSoulsInfo
        return

    def __onCollectorAdded(self, ecp):
        self.__collectorECPIdy = ecp.id
        self.__collectorECPPosition = ecp.position
        self._collectorSoulsWasUpdated(None)
        return

    def __onCollectorRemoved(self, ecp):
        if self.__collectorECPIdy == ecp.id:
            self.__collectorECPIdy = None
            self.__collectorECPPosition = None
            self._collectorSoulsWasUpdated(None)
        return


class _BattleSoundsConstants(CONST_CONTAINER):
    SOULS_ARE_ON_VEHICLE_EVENT = 'ev_halloween_2019_gameplay_device'
    MAX_VEHICLE_SOULS_FOR_SOUND = 150
    VEHICLE_DEVICE_RTCP = 'RTPC_ext_hw19_device_capacity'
    NOT_COLLECTING_WARNING_TIME = 90
    ALLIES_REMAINED_NOTIFICATION_WAIT_TIME = 2.5
    PLAYER_DEATH_NOTIFICATION = 'hw20_vo_notification_player_dead'
    REMAINED_ALLIES_NOTIFICATION_TEMPLATE = 'hw19_vo_notification_allies_{}_remained'
    REMAINED_ALLIES_NOTIFICATION_ON_COUNT = (1, 2, 3, 4)
    PLAYER_LAST_ALIVE_EVENT = 'hw19_vo_notification_player_last_alive'
    BOSS_INSIGHT_NOTIFICATION = 'hw19_vo_notification_boss_insight'
    BOMBER_INSIGHT_NOTIFICATION = 'hw19_vo_notification_bomber_insight'
    BOT_SPAWN_SOUND_BY_ROLE = {EVENT_BOT_ROLE.HUNTER: 'ev_halloween_2019_gameplay_spawn_hunter',
     EVENT_BOT_ROLE.BOMBER: 'ev_halloween_2019_gameplay_spawn_yorsh',
     EVENT_BOT_ROLE.RUNNER: 'ev_halloween_2019_gameplay_spawn_bunny',
     EVENT_BOT_ROLE.SENTRY: 'ev_halloween_2019_gameplay_spawn_default'}
    EVENT_TIMER_NOTIFICATION_TIME = 60
    EVENT_TIMER_SOUND_NOTIFICATION_TEMPLATE = 'hw19_one_minute_left_0{}'
    EVENT_TIMER_SOUND_NOTIFICATION_WORLDS = (1, 2, 3, 4)
    NOT_COLLECTING_WARNING_NOTIFICATION = 'hw19_vo_notification_player_is_not_collecting'
    NOT_COLLECTING_WARNING_ENV_IDS = (1, 2, 3, 4)
    ENOUGH_MATTER_COLLECTED_NOTIFICATION = 'hw19_vo_notification_enough_matter_was_collected'
    BOSS_EATING_START_NOTIFICATION = 'hw19_boss_eating_start'
    BOSS_EATING_STOP_NOTIFICATION = 'hw19_boss_eating_stop'


class _VehicleDevices(TriggersManager.ITriggerListener):

    def __init__(self):
        self.__vehSounds = {}
        self.__vehiclesWithDevice = set()
        self.__soulsInfo = _SoulsInfoProvider()

    def start(self):
        TriggersManager.g_manager.addListener(self)
        self.__soulsInfo.onVehicleSoulsUpdate += self.__updateVehicleDevice
        self.__soulsInfo.start()

    def stop(self):
        self.__soulsInfo.stop()
        self.__soulsInfo.onVehicleSoulsUpdate -= self.__updateVehicleDevice
        TriggersManager.g_manager.delListener(self)

    def initDeviceForVehicleIds(self, vehiclesIds):
        self.__vehiclesWithDevice.update(vehiclesIds)
        for vehicleId in vehiclesIds:
            self.__updateVehicleDevice(vehicleId, self.__soulsInfo.getSoulsInVehicle(vehicleId))

    def __updateVehicleDevice(self, vehId, souls, reason=None):
        if vehId not in self.__vehiclesWithDevice:
            return
        else:
            vehicle = BigWorld.entities.get(vehId)
            if vehicle is not None and vehId not in self.__vehSounds and vehicle.appearance is not None and vehicle.appearance.engineAudition is not None:
                self.__vehSounds[vehId] = vehicle.appearance.engineAudition.getSoundObject(TankSoundObjectsIndexes.ENGINE)
                self.__vehSounds[vehId].play(_BattleSoundsConstants.SOULS_ARE_ON_VEHICLE_EVENT)
            if vehId in self.__vehSounds:
                fillPercentage = int(100.0 * souls / _BattleSoundsConstants.MAX_VEHICLE_SOULS_FOR_SOUND)
                minValue = 1 if souls > 0 else 0
                fillPercentage = max(minValue, min(100, fillPercentage))
                self.__vehSounds[vehId].setRTPC(_BattleSoundsConstants.VEHICLE_DEVICE_RTCP, fillPercentage)
            return

    def onTriggerActivated(self, params):
        if params['type'] == TriggersManager.TRIGGER_TYPE.VEHICLE_VISUAL_VISIBILITY_CHANGED:
            self.__updateVehicleDevice(params['vehicleId'], self.__soulsInfo.getSoulsInVehicle(params['vehicleId']))

    def onTriggerDeactivated(self, params):
        pass


class EventBattleSoundsPlayer(IAbstractPeriodView, IViewComponentsCtrlListener, GameEventGetterMixin):
    battleSessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        self.__initialized = False
        self.__notCollectingWarningTimerId = None
        self.__alliesRemainedNotificationTimerId = None
        self.__alliesRemained = set()
        self.__alliesVehIdBecameDead = set()
        self.__bossVehicleSpotted = False
        self.__bomberVehiclesNotificationActive = True
        self.__bomberVehiclesSpottedCount = 0
        self.__currentEventEnvID = 0
        self.__notCollectingWarningHasPlayed = False
        self.__soulsInfoProvider = _SoulsInfoProvider()
        self.__vehicleDevices = _VehicleDevices()
        self.__envStartTime = None
        self.__lastTimerNotificationEnvId = None
        super(EventBattleSoundsPlayer, self).__init__()
        GameEventGetterMixin.__init__(self)
        return

    def detachedFromCtrl(self, ctrlID):
        if self.__initialized:
            self.__finalize()

    def setPeriod(self, period):
        if period == ARENA_PERIOD.BATTLE and not self.__initialized:
            self.__initialize()

    def __initialize(self):
        self.__initialized = True
        self.__soulsInfoProvider.onVehicleSoulsUpdate += self.__playerCollectedMatter
        self.__soulsInfoProvider.onPlayersHasEnoughSouls += self.__enoughMatterWasCollected
        self.__soulsInfoProvider.start()
        player = BigWorld.player()
        player.onVehicleSpawnEffectStarted += self.__vehicleSpawnSoundNotification
        player.onAuraVictimNotification += self.__notifyVehicleInBossAura
        arenaDP = self.sessionProvider.getArenaDP()
        self.__alliesRemained = playersVehiclesIds = {vInfo.vehicleID for vInfo in arenaDP.getVehiclesInfoIterator() if vInfo.team == EVENT.PLAYERS_TEAM}
        self.__vehicleDevices.start()
        self.__vehicleDevices.initDeviceForVehicleIds(playersVehiclesIds)
        self.__initTimerForNotCollectingWarning()
        if self.teammateVehicleHealth is not None:
            self.teammateVehicleHealth.onTeammateVehicleHealthUpdate += self.__onTeammateVehicleHealthUpdate
        if self.enemySpottedData is not None:
            self.enemySpottedData.onEnemySpottedDataUpdate += self.__onEnemySpottedDataUpdate
        if self.environmentData is not None:
            self.environmentData.onEnvironmentEventIDUpdate += self.__initTimerForNotCollectingWarning
            self.environmentData.onEnvironmentEventIDUpdate += self.__resetBomberSpottedData
            self.environmentData.onEnvironmentEventIDUpdate += self.__cancelAlliesRemainedNotification
        ctrl = self.battleSessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onUpdateScenarioTimer += self.__onUpdateScenarioTimer
        eqCtrl = self.battleSessionProvider.shared.equipments
        if eqCtrl is not None:
            eqCtrl.onEquipmentUpdated += self.__onEquipmentUpdated
        return

    def __finalize(self):
        self.__initialized = False
        self.__soulsInfoProvider.stop()
        self.__soulsInfoProvider.onVehicleSoulsUpdate -= self.__playerCollectedMatter
        self.__soulsInfoProvider.onPlayersHasEnoughSouls -= self.__enoughMatterWasCollected
        self.__vehicleDevices.stop()
        player = BigWorld.player()
        player.onVehicleSpawnEffectStarted -= self.__vehicleSpawnSoundNotification
        if self.teammateVehicleHealth is not None:
            self.teammateVehicleHealth.onTeammateVehicleHealthUpdate -= self.__onTeammateVehicleHealthUpdate
        if self.enemySpottedData is not None:
            self.enemySpottedData.onEnemySpottedDataUpdate -= self.__onEnemySpottedDataUpdate
        if self.environmentData is not None:
            self.environmentData.onEnvironmentEventIDUpdate -= self.__initTimerForNotCollectingWarning
            self.environmentData.onEnvironmentEventIDUpdate -= self.__resetBomberSpottedData
            self.environmentData.onEnvironmentEventIDUpdate -= self.__cancelAlliesRemainedNotification
        if self.__notCollectingWarningTimerId is not None:
            BigWorld.cancelCallback(self.__notCollectingWarningTimerId)
        self.__cancelAlliesRemainedNotificationTimer()
        ctrl = self.battleSessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onUpdateScenarioTimer -= self.__onUpdateScenarioTimer
        player.onAuraVictimNotification -= self.__notifyVehicleInBossAura
        eqCtrl = self.battleSessionProvider.shared.equipments
        if eqCtrl is not None:
            eqCtrl.onEquipmentUpdated -= self.__onEquipmentUpdated
        return

    def __vehicleSpawnSoundNotification(self, position, botRole):
        if botRole in _BattleSoundsConstants.BOT_SPAWN_SOUND_BY_ROLE and self.__getEventSoundEnvID() > 1:
            SoundGroups.g_instance.playSoundPos(_BattleSoundsConstants.BOT_SPAWN_SOUND_BY_ROLE[botRole], position)

    def __notifyVehicleInBossAura(self, show):
        if show:
            notification = _BattleSoundsConstants.BOSS_EATING_START_NOTIFICATION
        else:
            notification = _BattleSoundsConstants.BOSS_EATING_STOP_NOTIFICATION
        _playSoundNotification(notification)

    def __initTimerForNotCollectingWarning(self, envId=None):
        if self.__notCollectingWarningHasPlayed:
            return
        else:
            if self.__getEventSoundEnvID() in _BattleSoundsConstants.NOT_COLLECTING_WARNING_ENV_IDS:
                if self.__notCollectingWarningTimerId is not None:
                    BigWorld.cancelCallback(self.__notCollectingWarningTimerId)
                self.__notCollectingWarningTimerId = BigWorld.callback(_BattleSoundsConstants.NOT_COLLECTING_WARNING_TIME, self.__playerIsNotCollectingMatter)
            return

    def __playerIsNotCollectingMatter(self):
        self.__notCollectingWarningTimerId = None
        if isVehicleAlive():
            self.__notCollectingWarningHasPlayed = True
            _playSoundNotification(_BattleSoundsConstants.NOT_COLLECTING_WARNING_NOTIFICATION)
        return

    def __playerCollectedMatter(self, vehId, souls, reason):
        if self.__notCollectingWarningTimerId is None or reason != EVENT_SOULS_CHANGE_REASON.ADD:
            return
        else:
            if BigWorld.player().playerVehicleID == vehId:
                BigWorld.cancelCallback(self.__notCollectingWarningTimerId)
                self.__notCollectingWarningTimerId = None
            return

    def __enoughMatterWasCollected(self):
        _playSoundNotification(_BattleSoundsConstants.ENOUGH_MATTER_COLLECTED_NOTIFICATION)

    def __onTeammateVehicleHealthUpdate(self, diff):
        for vehID, health in diff.iteritems():
            if health > 0 and vehID not in self.__alliesRemained:
                self.__alliesRemained.add(vehID)
                self.__alliesVehIdBecameDead.discard(vehID)
            if health <= 0 and vehID in self.__alliesRemained:
                self.__alliesRemained.remove(vehID)
                self.__alliesVehIdBecameDead.add(vehID)
                self.__notifyAllyRemained()

    def __cancelAlliesRemainedNotification(self, envId=None):
        self.__cancelAlliesRemainedNotificationTimer()
        self.__envStartTime = time.time()

    def __cancelAlliesRemainedNotificationTimer(self, envId=None):
        if self.__alliesRemainedNotificationTimerId is not None:
            BigWorld.cancelCallback(self.__alliesRemainedNotificationTimerId)
            self.__alliesRemainedNotificationTimerId = None
        return

    def __notifyAllyRemained(self):
        self.__cancelAlliesRemainedNotificationTimer()
        self.__alliesRemainedNotificationTimerId = BigWorld.callback(_BattleSoundsConstants.ALLIES_REMAINED_NOTIFICATION_WAIT_TIME, self.__playNotifyAllyRemained)

    def __playNotifyAllyRemained(self):
        if self.__envStartTime and time.time() - self.__envStartTime <= _BattleSoundsConstants.ALLIES_REMAINED_NOTIFICATION_WAIT_TIME:
            self.__cancelAlliesRemainedNotificationTimer()
            return
        else:
            alliesRemainedCount = len(self.__alliesRemained)
            playerVehicleID = BigWorld.player().playerVehicleID
            if alliesRemainedCount > 0 and playerVehicleID in self.__alliesVehIdBecameDead:
                _playSoundNotification(_BattleSoundsConstants.PLAYER_DEATH_NOTIFICATION)
            elif alliesRemainedCount == 1 and playerVehicleID in self.__alliesRemained:
                _playSoundNotification(_BattleSoundsConstants.PLAYER_LAST_ALIVE_EVENT)
            elif alliesRemainedCount in _BattleSoundsConstants.REMAINED_ALLIES_NOTIFICATION_ON_COUNT:
                notification = _BattleSoundsConstants.REMAINED_ALLIES_NOTIFICATION_TEMPLATE.format(alliesRemainedCount)
                _playSoundNotification(notification)
            self.__alliesRemainedNotificationTimerId = None
            self.__alliesVehIdBecameDead.clear()
            return

    def __resetBomberSpottedData(self, *args):
        self.__bomberVehiclesNotificationActive = True

    def __onEnemySpottedDataUpdate(self, *args):
        if not self.__bossVehicleSpotted:
            if self.enemySpottedData.checkBossVehicleSpotted():
                _playSoundNotification(_BattleSoundsConstants.BOSS_INSIGHT_NOTIFICATION)
                self.__bossVehicleSpotted = True
        bombersSpotted = self.enemySpottedData.checkBomberVehicleSpotted()
        if self.__bomberVehiclesNotificationActive and bombersSpotted > self.__bomberVehiclesSpottedCount:
            _playSoundNotification(_BattleSoundsConstants.BOMBER_INSIGHT_NOTIFICATION)
            self.__bomberVehiclesNotificationActive = False
        self.__bomberVehiclesSpottedCount = bombersSpotted

    def __onUpdateScenarioTimer(self, waitTime, alarmTime, visible):
        if waitTime == _BattleSoundsConstants.EVENT_TIMER_NOTIFICATION_TIME:
            soundEnvId = self.__getEventSoundEnvID()
            if soundEnvId in _BattleSoundsConstants.EVENT_TIMER_SOUND_NOTIFICATION_WORLDS and soundEnvId != self.__lastTimerNotificationEnvId:
                notification = _BattleSoundsConstants.EVENT_TIMER_SOUND_NOTIFICATION_TEMPLATE.format(soundEnvId)
                _playSoundNotification(notification)
                self.__lastTimerNotificationEnvId = soundEnvId

    def __getEventSoundEnvID(self):
        if self.environmentData is not None:
            self.__currentEventEnvID = self.environmentData.getCurrentEnvironmentID() + 1
        return self.__currentEventEnvID

    def __onEquipmentUpdated(self, intCD, item):
        activatedStages = (EQUIPMENT_STAGES.DEPLOYING,
         EQUIPMENT_STAGES.PREPARING,
         EQUIPMENT_STAGES.ACTIVE,
         EQUIPMENT_STAGES.COOLDOWN)
        if item.getPrevStage() == EQUIPMENT_STAGES.READY and item.getStage() in activatedStages:
            equipment = vehicles.g_cache.equipments().get(item.getEquipmentID())
            if equipment and equipment.activationWWSoundFeedback:
                SoundGroups.g_instance.playSound2D(equipment.activationWWSoundFeedback)
        elif item.getPrevStage() == EQUIPMENT_STAGES.COOLDOWN and item.getStage() == EQUIPMENT_STAGES.READY:
            equipment = vehicles.g_cache.equipments().get(item.getEquipmentID())
            if equipment and equipment.soundNotification:
                _playSoundNotification(equipment.soundNotification)
        elif item.getPrevStage() == EQUIPMENT_STAGES.ACTIVE and item.getStage() in activatedStages:
            equipment = vehicles.g_cache.equipments().get(item.getEquipmentID())
            if equipment and equipment.deactivationWWSoundFeedback:
                SoundGroups.g_instance.playSound2D(equipment.deactivationWWSoundFeedback)


class VehicleHealthSoundPlayer(IBattleFieldListener):
    _LOW_HEALTH_NOTIFICATION = 'hw20_vo_notification_player_low_hp'
    _LOW_HEALTH_PERCENTS = 25
    battleSessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        self.__lastNotifiedVehicleHealthPercents = None
        return

    def updateVehicleHealth(self, vehicleID, newHealth, maxHealth):
        playerVehicleId = BigWorld.player().playerVehicleID
        if vehicleID == playerVehicleId and not self.battleSessionProvider.getCtx().isObserver(playerVehicleId):
            healthPercentage = int(100.0 * newHealth / maxHealth)
            healthPrev, healthCurrent = self.__lastNotifiedVehicleHealthPercents, healthPercentage
            self.__lastNotifiedVehicleHealthPercents = healthPercentage
            lowHpPointWasCrossed = healthPrev > self._LOW_HEALTH_PERCENTS >= healthCurrent
            if healthCurrent != healthPrev and lowHpPointWasCrossed and healthCurrent > 0:
                _playSoundNotification(self._LOW_HEALTH_NOTIFICATION)
