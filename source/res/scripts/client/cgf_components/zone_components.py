# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_components/zone_components.py
import functools
import logging
import BigWorld
import CGF
import GenericComponents
import Triggers
import UIComponents
from cgf_script.component_meta_class import ComponentProperty as CompProp, CGFMetaTypes, registerComponent
from cgf_script.managers_registrator import onAddedQuery, onRemovedQuery, onProcessQuery, autoregister
from constants import IS_CLIENT, IS_CGF_DUMP
from helpers import dependency
from hints.battle import manager as battleHintsModelsMgr
from vehicle_systems.cgf_helpers import getVehicleEntityByGameObject
from PlayerEvents import g_playerEvents
from helpers import isPlayerAvatar
if IS_CLIENT:
    from skeletons.gui.battle_session import IBattleSessionProvider
    from gui.battle_control import avatar_getter
else:
    avatar_getter = None

    class IBattleSessionProvider(object):
        pass


_logger = logging.getLogger(__name__)

def _isAvatarReady():
    return isPlayerAvatar() and BigWorld.player().userSeesWorld()


class RandomEventZoneUINotificationType(object):
    DANGER_ZONE = 'dangerZone'
    WARNING_ZONE = 'warningZone'
    MAP_DEATH_ZONE = 'mapDeathZone'


class WeatherZoneUINotificationType(object):
    BLIZZARD_ZONE = 'blizzardZone'
    FIRE_ZONE = 'fireZone'
    FOG_ZONE = 'fogZone'
    RAIN_ZONE = 'rainZone'
    SANDSTORM_ZONE = 'sandstormZone'
    SMOKE_ZONE = 'smokeZone'
    TORNADO_ZONE = 'tornadoZone'


@registerComponent
class ZoneMarker(object):
    category = 'UI'
    domain = CGF.DomainOption.DomainClient | CGF.DomainOption.DomainEditor
    editorTitle = 'Zone Marker'
    isVisibleOnMinimap = CompProp(type=CGFMetaTypes.BOOL, value=True, editorName='Visible on minimap')
    isVisibleOn3DScene = CompProp(type=CGFMetaTypes.BOOL, value=False, editorName='Visible on 3D scene')
    reduceDuration = CompProp(type=CGFMetaTypes.FLOAT, value=0.0, editorName='Duration reduce')

    def __init__(self):
        super(ZoneMarker, self).__init__()
        self.id = None
        self.startTime = 0
        self.finishTime = 0
        return

    @property
    def duration(self):
        return max(self.finishTime - self.startTime, 0)

    @property
    def markerProgress(self):
        if self.isActive():
            restTime = self.finishTime - BigWorld.serverTime()
            if self.duration and restTime > 0:
                return float(restTime) / self.duration * 100

    def isActive(self):
        return self.finishTime >= BigWorld.serverTime() >= self.startTime


@registerComponent
class WeatherZoneUINotification(object):
    category = 'UI'
    domain = CGF.DomainOption.DomainClient | CGF.DomainOption.DomainEditor
    editorTitle = 'Zone with weather UI Notification'
    trigger = CompProp(type=CGFMetaTypes.LINK, editorName='Trigger', value=Triggers.AreaTriggerComponent)
    zoneType = CompProp(type=CGFMetaTypes.STRING, editorName='Zone Type', value=WeatherZoneUINotificationType.BLIZZARD_ZONE, annotations={'comboBox': {WeatherZoneUINotificationType.BLIZZARD_ZONE: WeatherZoneUINotificationType.BLIZZARD_ZONE,
                  WeatherZoneUINotificationType.FIRE_ZONE: WeatherZoneUINotificationType.FIRE_ZONE,
                  WeatherZoneUINotificationType.FOG_ZONE: WeatherZoneUINotificationType.FOG_ZONE,
                  WeatherZoneUINotificationType.RAIN_ZONE: WeatherZoneUINotificationType.RAIN_ZONE,
                  WeatherZoneUINotificationType.SANDSTORM_ZONE: WeatherZoneUINotificationType.SANDSTORM_ZONE,
                  WeatherZoneUINotificationType.SMOKE_ZONE: WeatherZoneUINotificationType.SMOKE_ZONE,
                  WeatherZoneUINotificationType.TORNADO_ZONE: WeatherZoneUINotificationType.TORNADO_ZONE}})

    def __init__(self):
        super(WeatherZoneUINotification, self).__init__()
        self.id = None
        self.enterReactionID = None
        self.exitReactionID = None
        self.inZoneVehicles = set([])
        return


def getHints():
    if IS_CGF_DUMP:
        return dict()
    battleHintsModelsMgr.init()
    return {v.uniqueName:v.uniqueName for v in battleHintsModelsMgr.get().getAll()}


@registerComponent
class ZoneHint(object):
    category = 'UI'
    domain = CGF.DomainOption.DomainClient | CGF.DomainOption.DomainEditor
    editorTitle = 'Zone hint'
    trigger = CompProp(type=CGFMetaTypes.LINK, editorName='Trigger', value=Triggers.AreaTriggerComponent)
    hintUniqName = CompProp(type=CGFMetaTypes.STRING, editorName='zone battle hint', value='', annotations={'comboBox': getHints()})

    def __init__(self):
        super(ZoneHint, self).__init__()
        self.id = None
        self.enterReactionID = None
        self.exitReactionID = None
        self.inZoneVehicles = set([])
        return


@registerComponent
class RandomEventZoneUINotification(object):
    category = 'UI'
    domain = CGF.DomainOption.DomainClient | CGF.DomainOption.DomainEditor
    editorTitle = 'Zone with timer UI Notification'
    trigger = CompProp(type=CGFMetaTypes.LINK, editorName='Trigger', value=Triggers.AreaTriggerComponent)
    zoneType = CompProp(type=CGFMetaTypes.STRING, editorName='Zone Type', value=RandomEventZoneUINotificationType.DANGER_ZONE, annotations={'comboBox': {RandomEventZoneUINotificationType.WARNING_ZONE: RandomEventZoneUINotificationType.WARNING_ZONE,
                  RandomEventZoneUINotificationType.DANGER_ZONE: RandomEventZoneUINotificationType.DANGER_ZONE,
                  RandomEventZoneUINotificationType.MAP_DEATH_ZONE: RandomEventZoneUINotificationType.MAP_DEATH_ZONE}})

    def __init__(self):
        super(RandomEventZoneUINotification, self).__init__()
        self.id = None
        self.startTime = 0
        self.finishTime = 0
        self.enterReactionID = None
        self.exitReactionID = None
        self.inZoneVehicles = set([])
        return

    def isActive(self):
        return self.finishTime >= BigWorld.serverTime()


@autoregister(presentInAllWorlds=True, domain=CGF.DomainOption.DomainClient)
class MapZoneManager(CGF.ComponentManager):
    __guiSessionProvider = dependency.descriptor(IBattleSessionProvider)
    queryRandomEventUINotifications = CGF.QueryConfig(RandomEventZoneUINotification)
    queryWeatherUINotifications = CGF.QueryConfig(WeatherZoneUINotification)
    queryZoneHints = CGF.QueryConfig(ZoneHint)

    def __init__(self):
        super(MapZoneManager, self).__init__()
        self.__subscriptionsCount = 0
        if _isAvatarReady():
            self.__onAvatarReady()
        else:
            g_playerEvents.onAvatarReady += self.__onAvatarReady

    def deactivate(self):
        self.__subscriptionsCount = 0
        g_playerEvents.onAvatarReady -= self.__onAvatarReady
        if BigWorld.player() and isPlayerAvatar():
            BigWorld.player().onVehicleLeaveWorld -= self.__onVehicleLeaveWorld

    @onAddedQuery(CGF.GameObject, ZoneMarker, GenericComponents.TransformComponent, tickGroup='PostHierarchy')
    def onMarkerToZoneAdded(self, go, zoneMarker, transform):
        _logger.debug('on marker to zone added')
        zoneMarker.id = go.id
        mapZones = self.__guiSessionProvider.shared.mapZones
        if mapZones:
            mapZones.addMarkerToZone(zoneMarker, transform.worldTransform)

    @onRemovedQuery(ZoneMarker)
    def onMakerFromZoneRemoved(self, zoneMarker):
        _logger.debug('on maker from zone removed')
        mapZones = self.__guiSessionProvider.shared.mapZones
        if mapZones:
            mapZones.removeMarkerFromZone(zoneMarker)

    @onProcessQuery(ZoneMarker, tickGroup='Simulation', period=1.0)
    def onMarkerUpdated(self, zoneMarker):
        _logger.debug('on marker updated')
        mapZones = self.__guiSessionProvider.shared.mapZones
        if mapZones:
            mapZones.onMarkerProgressUpdated(zoneMarker)

    @onAddedQuery(CGF.GameObject, RandomEventZoneUINotification)
    def onRandomEventZoneUINotificationAdded(self, go, randomEventZoneUINotification):
        _logger.debug('on random event zone added')
        self.__subscribeTrigger(go, randomEventZoneUINotification, self.__onEnterRandomEventZone, self.__onExitRandomEventZone)

    @onRemovedQuery(RandomEventZoneUINotification)
    def onRandomEventZoneUINotificationRemoved(self, randomEventZoneUINotification):
        _logger.debug('on random event zone removed')
        self.__unsubscribeTrigger(randomEventZoneUINotification)
        mapZones = self.__guiSessionProvider.shared.mapZones
        if mapZones:
            mapZones.removeRandomEventZone(randomEventZoneUINotification)

    @onAddedQuery(CGF.GameObject, WeatherZoneUINotification)
    def onWeatherZoneUINotificationAdded(self, go, weatherEventZoneUINotification):
        _logger.debug('on weather zone added')
        self.__subscribeTrigger(go, weatherEventZoneUINotification, self.__onEnterWeatherZone, self.__onExitWeatherZone)

    @onRemovedQuery(WeatherZoneUINotification)
    def onWeatherZoneUINotificationRemoved(self, weatherEventZoneUINotification):
        _logger.debug('on weather zone removed')
        self.__unsubscribeTrigger(weatherEventZoneUINotification)
        mapZones = self.__guiSessionProvider.shared.mapZones
        if mapZones:
            mapZones.removeWeatherZone(weatherEventZoneUINotification)

    @onAddedQuery(CGF.GameObject, ZoneHint)
    def onZoneHintAdded(self, go, zoneHint):
        _logger.debug('on zone hint added')
        self.__subscribeTrigger(go, zoneHint, self.__onEnterZoneHint, self.__onExitZoneHint)

    @onRemovedQuery(ZoneHint)
    def onZoneHintRemoved(self, zoneHint):
        _logger.debug('on zone hint removed')
        self.__unsubscribeTrigger(zoneHint)

    @onAddedQuery(UIComponents.MinimapChangerComponent)
    def onTransformedZoneAdded(self, changer):
        _logger.debug('on transformed zone added: %s', changer.layerId)
        mapZones = self.__guiSessionProvider.shared.mapZones
        if mapZones:
            mapZones.addTransformedZone(changer)

    @onRemovedQuery(UIComponents.MinimapChangerComponent)
    def onTransformedZoneRemoved(self, changer):
        _logger.debug('on transformed zone removed: %s', changer.layerId)
        mapZones = self.__guiSessionProvider.shared.mapZones
        if mapZones:
            mapZones.removeTransformedZone(changer)

    @onAddedQuery(ZoneMarker, GenericComponents.TimedActivatedComponent)
    def onActivationAndZone(self, marker, activator):
        reduce = max(marker.reduceDuration, 0.0)
        marker.startTime = activator.serverStartTime
        marker.finishTime = max(activator.serverStartTime, activator.serverEndTime - reduce)

    @onAddedQuery(RandomEventZoneUINotification, GenericComponents.TimedActivatedComponent)
    def onActivationMarker(self, zone, activator):
        zone.startTime = activator.serverStartTime
        zone.finishTime = activator.serverEndTime

    def __subscribeTrigger(self, go, zone, enterCallback, exitCallback):
        zone.id = go.id
        trigger = zone.trigger()
        if trigger:
            self.__subscribeVehicleChanges()
            zone.enterReactionID = trigger.addEnterReaction(functools.partial(self.__onEnterZone, zone, enterCallback))
            zone.exitReactionID = trigger.addExitReaction(functools.partial(self.__onExitZone, zone, exitCallback))

    def __unsubscribeTrigger(self, zone):
        trigger = zone.trigger()
        if trigger:
            self.__unsubscribeVehicleChanges()
            if zone.enterReactionID:
                trigger.removeEnterReaction(zone.enterReactionID)
            if zone.exitReactionID:
                trigger.removeExitReaction(zone.exitReactionID)

    def __onEnterZone(self, zoneNotification, enterCallback, go, _):
        vehicle = getVehicleEntityByGameObject(go)
        if vehicle:
            zoneNotification.inZoneVehicles.add(vehicle.id)
            if vehicle.id == avatar_getter.getVehicleIDAttached() and vehicle.isAlive():
                enterCallback(zoneNotification)

    def __onExitZone(self, zoneNotification, exitCallback, go, _):
        vehicle = getVehicleEntityByGameObject(go)
        if vehicle:
            zoneNotification.inZoneVehicles.discard(vehicle.id)
            if vehicle.id == avatar_getter.getVehicleIDAttached():
                exitCallback(zoneNotification)

    def __onEnterRandomEventZone(self, zoneNotification):
        _logger.debug('on enter random event zone')
        mapZones = self.__guiSessionProvider.shared.mapZones
        if mapZones and zoneNotification.isActive():
            mapZones.enterRandomEventZone(zoneNotification)

    def __onExitRandomEventZone(self, zoneNotification):
        _logger.debug('on exit random event zone')
        mapZones = self.__guiSessionProvider.shared.mapZones
        if mapZones:
            mapZones.exitRandomEventZone(zoneNotification)

    def __onEnterWeatherZone(self, zoneNotification):
        _logger.debug('on enter weather zone')
        mapZones = self.__guiSessionProvider.shared.mapZones
        if mapZones:
            mapZones.enterWeatherZone(zoneNotification)

    def __onExitWeatherZone(self, zoneNotification):
        _logger.debug('on exit weather zone')
        mapZones = self.__guiSessionProvider.shared.mapZones
        if mapZones:
            mapZones.exitWeatherZone(zoneNotification)

    def __onEnterZoneHint(self, zoneHint):
        _logger.debug('on enter zone hint')
        controller = self.__guiSessionProvider.dynamic.battleHints
        if controller:
            controller.showHint(hintName=zoneHint.hintUniqName)
        else:
            _logger.warning('No battle hints controller on show hint call.')

    def __onExitZoneHint(self, zoneHint):
        _logger.debug('on exit zone hint')
        controller = self.__guiSessionProvider.dynamic.battleHints
        if controller:
            controller.removeHint(hintName=zoneHint.hintUniqName, hide=True)
        else:
            _logger.warning('No battle hints controller on hide hint call.')

    def __subscribeVehicleChanges(self):
        player = BigWorld.player()
        if player:
            consistentMatrices = player.consistentMatrices
            if not self.__subscriptionsCount and consistentMatrices:
                consistentMatrices.onVehicleMatrixBindingChanged += self.__onVehicleChanged
            self.__subscriptionsCount += 1

    def __unsubscribeVehicleChanges(self):
        player = BigWorld.player()
        if player:
            consistentMatrices = player.consistentMatrices
            self.__subscriptionsCount -= 1
            if not self.__subscriptionsCount and consistentMatrices:
                consistentMatrices.onVehicleMatrixBindingChanged -= self.__onVehicleChanged

    def __onVehicleChanged(self, *args, **kwargs):
        avatarVehicle = BigWorld.player().getVehicleAttached()
        mapZones = self.__guiSessionProvider.shared.mapZones
        if avatarVehicle is None or not avatarVehicle.isAlive() or mapZones is None:
            return
        else:
            for reZone in sorted([ zone for zone in self.queryRandomEventUINotifications ], key=lambda z: z.zoneType == RandomEventZoneUINotificationType.DANGER_ZONE, reverse=True):
                if avatarVehicle.id in reZone.inZoneVehicles:
                    mapZones.enterRandomEventZone(reZone)

            for wZone in self.queryWeatherUINotifications:
                if avatarVehicle.id in wZone.inZoneVehicles:
                    mapZones.enterWeatherZone(wZone)

            return

    def __onAvatarReady(self):
        BigWorld.player().onVehicleLeaveWorld += self.__onVehicleLeaveWorld

    def __onVehicleLeaveWorld(self, vehicle):
        for reZone in self.queryRandomEventUINotifications:
            reZone.inZoneVehicles.discard(vehicle.id)

        for wZone in self.queryWeatherUINotifications:
            wZone.inZoneVehicles.discard(vehicle.id)

        for hintZone in self.queryZoneHints:
            hintZone.inZoneVehicles.discard(vehicle.id)
