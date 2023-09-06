# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/map_zones_ctrl.py
import Event
import SoundGroups
from cgf_components.zone_components import ZoneUINotificationType
from gui.battle_control.arena_info.interfaces import IMapZonesController
from gui.battle_control.battle_constants import BATTLE_CTRL_ID, VEHICLE_VIEW_STATE, DestroyTimerViewState, TIMER_VIEW_STATE
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider

class SoundNotifications(object):
    DANGER_ZONE_MARKER_START = 'dstrct_death_zone_marker_start'
    DANGER_ZONE_MARKER_STOP = 'dstrct_death_zone_marker_stop'
    DANGER_ZONE_ENTER = 'dstrct_death_zone_enter'
    DANGER_ZONE_EXIT = 'dstrct_death_zone_exit'


_notificationMapping = {ZoneUINotificationType.WARNING_ZONE: (VEHICLE_VIEW_STATE.WARNING_ZONE, TIMER_VIEW_STATE.WARNING),
 ZoneUINotificationType.DANGER_ZONE: (VEHICLE_VIEW_STATE.DANGER_ZONE, TIMER_VIEW_STATE.CRITICAL),
 ZoneUINotificationType.MAP_DEATH_ZONE: (VEHICLE_VIEW_STATE.MAP_DEATH_ZONE, TIMER_VIEW_STATE.WARNING)}

class MapZonesController(IMapZonesController):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, setup):
        super(MapZonesController, self).__init__()
        self.__eManager = Event.EventManager()
        self.onMarkerToZoneAdded = Event.Event(self.__eManager)
        self.onMarkerFromZoneRemoved = Event.Event(self.__eManager)
        self.onMarkerProgressUpdated = Event.Event(self.__eManager)
        self.onZoneTransformed = Event.Event(self.__eManager)
        self.onTransformedZoneRemoved = Event.Event(self.__eManager)
        self.__activeDangerZones = set()
        self.__zoneMarkers = {}
        self.__transformedZones = {}

    def startControl(self, *args):
        pass

    def stopControl(self):
        self.__eManager.clear()
        self.__zoneMarkers.clear()
        self.__transformedZones.clear()

    def getControllerID(self):
        return BATTLE_CTRL_ID.MAP_ZONES_CONTROLLER

    def addMarkerToZone(self, zoneMarker, matrix):
        self.__zoneMarkers[zoneMarker.id] = (zoneMarker, matrix)
        self.onMarkerToZoneAdded(zoneMarker, matrix)
        SoundGroups.g_instance.playSoundPos(SoundNotifications.DANGER_ZONE_MARKER_START, matrix.translation)

    def removeMarkerFromZone(self, zoneMarker):
        self.onMarkerFromZoneRemoved(zoneMarker)
        _, matrix = self.__zoneMarkers.pop(zoneMarker.id)
        SoundGroups.g_instance.playSoundPos(SoundNotifications.DANGER_ZONE_MARKER_STOP, matrix.translation)

    def addTransformedZone(self, zone):
        self.__transformedZones[zone.layerId] = zone
        self.onZoneTransformed(zone)

    def removeTransformedZone(self, zone):
        self.__transformedZones.pop(zone.layerId)
        self.onTransformedZoneRemoved(zone)

    def enterDangerZone(self, zone):
        self.__activeDangerZones.add(zone.id)
        vehicleState, timerState = _notificationMapping[zone.zoneType]
        state = DestroyTimerViewState(vehicleState, zone.finishTime - zone.startTime, timerState, startTime=zone.startTime)
        self.sessionProvider.invalidateVehicleState(vehicleState, state)
        if vehicleState == VEHICLE_VIEW_STATE.DANGER_ZONE:
            SoundGroups.g_instance.playSound2D(SoundNotifications.DANGER_ZONE_ENTER)

    def exitDangerZone(self, zone):
        self.__activeDangerZones.discard(zone.id)
        vehicleState, _ = _notificationMapping[zone.zoneType]
        state = DestroyTimerViewState.makeCloseTimerState(vehicleState)
        self.sessionProvider.invalidateVehicleState(vehicleState, state)
        if vehicleState == VEHICLE_VIEW_STATE.DANGER_ZONE:
            SoundGroups.g_instance.playSound2D(SoundNotifications.DANGER_ZONE_EXIT)

    def removeDangerZone(self, zone):
        if zone.id in self.__activeDangerZones:
            self.exitDangerZone(zone)

    def getZoneMarkers(self):
        return self.__zoneMarkers

    def getTransformedZones(self):
        return self.__transformedZones
