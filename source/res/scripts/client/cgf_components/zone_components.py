# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_components/zone_components.py
import functools
import logging
import BigWorld
import CGF
import GenericComponents
import Triggers
from cgf_script.component_meta_class import ComponentProperty as CompProp, CGFMetaTypes, registerComponent
from cgf_script.managers_registrator import onAddedQuery, onRemovedQuery, onProcessQuery, autoregister
from constants import IS_CLIENT
from helpers import dependency
if IS_CLIENT:
    from skeletons.gui.battle_session import IBattleSessionProvider
    from Vehicle import Vehicle
    from gui.battle_control import avatar_getter
else:
    avatar_getter = None

    class IBattleSessionProvider(object):
        pass


    class Vehicle(object):
        pass


_logger = logging.getLogger(__name__)

@registerComponent
class MinimapChanger(object):
    category = 'UI'
    domain = CGF.DomainOption.DomainClient | CGF.DomainOption.DomainEditor
    editorTitle = 'Minimap Changer'
    minimapLayer = CompProp(type=CGFMetaTypes.STRING, value='spaces/02_malinovka/mmap.dds', editorName='Layer', annotations={'path': '*.dds'})

    def __init__(self):
        super(MinimapChanger, self).__init__()
        self.id = None
        return


@registerComponent
class ZoneMarker(object):
    category = 'UI'
    domain = CGF.DomainOption.DomainClient | CGF.DomainOption.DomainEditor
    editorTitle = 'Zone Marker'

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
class ZoneUINotification(object):
    category = 'UI'
    domain = CGF.DomainOption.DomainClient | CGF.DomainOption.DomainEditor
    editorTitle = 'Zone UI Notification'
    trigger = CompProp(type=CGFMetaTypes.LINK, editorName='Trigger', value=Triggers.AreaTriggerComponent)

    def __init__(self):
        super(ZoneUINotification, self).__init__()
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
    queryUINotifications = CGF.QueryConfig(ZoneUINotification)

    def __init__(self):
        super(MapZoneManager, self).__init__()
        self.__subscriptionsCount = 0

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
        if mapZones and zoneMarker.isActive():
            mapZones.onMarkerProgressUpdated(zoneMarker)

    @onAddedQuery(CGF.GameObject, ZoneUINotification)
    def onZoneUINotificationAdded(self, go, zoneUINotification):
        _logger.debug('on danger zone added')
        zoneUINotification.id = go.id
        trigger = zoneUINotification.trigger()
        if trigger:
            self.__subscribeVehicleChanges()
            zoneUINotification.enterReactionID = trigger.addEnterReaction(functools.partial(self.__onEnterDangerZone, zoneUINotification))
            zoneUINotification.exitReactionID = trigger.addExitReaction(functools.partial(self.__onExitDangerZone, zoneUINotification))

    @onRemovedQuery(ZoneUINotification)
    def onZoneUINotificationRemoved(self, zoneUINotification):
        _logger.debug('on danger zone removed')
        trigger = zoneUINotification.trigger()
        if trigger:
            self.__unsubscribeVehicleChanges()
            if zoneUINotification.enterReactionID:
                trigger.removeEnterReaction(zoneUINotification.enterReactionID)
            if zoneUINotification.exitReactionID:
                trigger.removeExitReaction(zoneUINotification.exitReactionID)
        mapZones = self.__guiSessionProvider.shared.mapZones
        if mapZones:
            mapZones.removeDangerZone(zoneUINotification)

    @onAddedQuery(CGF.GameObject, MinimapChanger)
    def onTransformedZoneAdded(self, go, changer):
        _logger.debug('on transformed zone added')
        changer.id = go.id
        mapZones = self.__guiSessionProvider.shared.mapZones
        if mapZones:
            mapZones.addTransformedZone(changer)

    @onRemovedQuery(MinimapChanger)
    def onTransformedZoneRemoved(self, transformedZone):
        _logger.debug('on transformed zone removed')
        mapZones = self.__guiSessionProvider.shared.mapZones
        if mapZones:
            mapZones.removeTransformedZone(transformedZone)

    def __onEnterDangerZone(self, zoneUINotification, go, _):
        _logger.debug('on enter danger zone')
        mapZones = self.__guiSessionProvider.shared.mapZones
        if mapZones:
            vehicle = self.__getVehicleFromGO(go)
            if zoneUINotification.isActive():
                if vehicle:
                    zoneUINotification.inZoneVehicles.add(vehicle.id)
                    if vehicle.id == avatar_getter.getVehicleIDAttached():
                        mapZones.enterDangerZone(zoneUINotification)

    def __onExitDangerZone(self, zoneUINotification, go, _):
        _logger.debug('on exit danger zone')
        mapZones = self.__guiSessionProvider.shared.mapZones
        if mapZones:
            vehicle = self.__getVehicleFromGO(go)
            if vehicle:
                zoneUINotification.inZoneVehicles.discard(vehicle.id)
                if vehicle.id == avatar_getter.getVehicleIDAttached():
                    mapZones.exitDangerZone(zoneUINotification)

    def __getVehicleFromGO(self, obj):
        hierarchyManager = CGF.HierarchyManager(self.spaceID)
        if not hierarchyManager:
            return None
        else:
            vehicleGO = hierarchyManager.getTopMostParent(obj)
            vehicle = vehicleGO.findComponentByType(Vehicle)
            return None if not vehicle else vehicle

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
        if avatarVehicle is None or not avatarVehicle.isAlive():
            return
        else:
            for dZone in self.queryUINotifications:
                if avatarVehicle.id in dZone.inZoneVehicles:
                    mapZones = self.__guiSessionProvider.shared.mapZones
                    if mapZones:
                        mapZones.enterDangerZone(dZone)
                        return

            return
