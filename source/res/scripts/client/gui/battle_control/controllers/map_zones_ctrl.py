# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/map_zones_ctrl.py
import Event
import SoundGroups
from cgf_components.zone_components import RandomEventZoneUINotificationType, WeatherZoneUINotificationType
from gui.battle_control.arena_info.interfaces import IMapZonesController
from gui.battle_control.battle_constants import BATTLE_CTRL_ID, VEHICLE_VIEW_STATE, DestroyTimerViewState, TIMER_VIEW_STATE
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider

class SoundNotifications(object):
    DANGER_ZONE_MARKER_START = 'dstrct_death_zone_marker_start'
    DANGER_ZONE_MARKER_STOP = 'dstrct_death_zone_marker_stop'
    DANGER_ZONE_ENTER = 'dstrct_death_zone_enter'
    DANGER_ZONE_EXIT = 'dstrct_death_zone_exit'


_randomEventsNotificationMapping = {RandomEventZoneUINotificationType.WARNING_ZONE: (VEHICLE_VIEW_STATE.WARNING_ZONE, TIMER_VIEW_STATE.WARNING),
 RandomEventZoneUINotificationType.DANGER_ZONE: (VEHICLE_VIEW_STATE.DANGER_ZONE, TIMER_VIEW_STATE.CRITICAL),
 RandomEventZoneUINotificationType.MAP_DEATH_ZONE: (VEHICLE_VIEW_STATE.MAP_DEATH_ZONE, TIMER_VIEW_STATE.WARNING)}
_weatherNotificationMapping = {WeatherZoneUINotificationType.BLIZZARD_ZONE: (VEHICLE_VIEW_STATE.BLIZZARD_ZONE, TIMER_VIEW_STATE.WARNING),
 WeatherZoneUINotificationType.FIRE_ZONE: (VEHICLE_VIEW_STATE.FIRE_ZONE, TIMER_VIEW_STATE.WARNING),
 WeatherZoneUINotificationType.FOG_ZONE: (VEHICLE_VIEW_STATE.FOG_ZONE, TIMER_VIEW_STATE.WARNING),
 WeatherZoneUINotificationType.RAIN_ZONE: (VEHICLE_VIEW_STATE.RAIN_ZONE, TIMER_VIEW_STATE.WARNING),
 WeatherZoneUINotificationType.SANDSTORM_ZONE: (VEHICLE_VIEW_STATE.SANDSTORM_ZONE, TIMER_VIEW_STATE.WARNING),
 WeatherZoneUINotificationType.SMOKE_ZONE: (VEHICLE_VIEW_STATE.SMOKE_ZONE, TIMER_VIEW_STATE.WARNING),
 WeatherZoneUINotificationType.TORNADO_ZONE: (VEHICLE_VIEW_STATE.TORNADO_ZONE, TIMER_VIEW_STATE.WARNING)}

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
        self.__activeRandomEventZones = set()
        self.__activeWeatherZones = set()
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

    def enterRandomEventZone(self, zone):
        self.__activeRandomEventZones.add(zone.id)
        vehicleState, timerState = _randomEventsNotificationMapping[zone.zoneType]
        state = DestroyTimerViewState(vehicleState, zone.finishTime - zone.startTime, timerState, startTime=zone.startTime)
        self.sessionProvider.invalidateVehicleState(vehicleState, state)
        if vehicleState == VEHICLE_VIEW_STATE.DANGER_ZONE:
            SoundGroups.g_instance.playSound2D(SoundNotifications.DANGER_ZONE_ENTER)

    def exitRandomEventZone(self, zone):
        self.__activeRandomEventZones.discard(zone.id)
        vehicleState, _ = _randomEventsNotificationMapping[zone.zoneType]
        state = DestroyTimerViewState.makeCloseTimerState(vehicleState)
        self.sessionProvider.invalidateVehicleState(vehicleState, state)
        if vehicleState == VEHICLE_VIEW_STATE.DANGER_ZONE:
            SoundGroups.g_instance.playSound2D(SoundNotifications.DANGER_ZONE_EXIT)

    def removeRandomEventZone(self, zone):
        if zone.id in self.__activeRandomEventZones:
            self.exitRandomEventZone(zone)

    def enterWeatherZone(self, zone):
        self.__activeWeatherZones.add(zone.id)
        vehicleState, timerState = _weatherNotificationMapping[zone.zoneType]
        state = DestroyTimerViewState(vehicleState, 0, timerState)
        self.sessionProvider.invalidateVehicleState(vehicleState, state)

    def exitWeatherZone(self, zone):
        self.__activeWeatherZones.discard(zone.id)
        vehicleState, _ = _weatherNotificationMapping[zone.zoneType]
        state = DestroyTimerViewState.makeCloseTimerState(vehicleState)
        self.sessionProvider.invalidateVehicleState(vehicleState, state)

    def removeWeatherZone(self, zone):
        if zone.id in self.__activeWeatherZones:
            self.exitWeatherZone(zone)

    def getZoneMarkers(self):
        return self.__zoneMarkers

    def getTransformedZones(self):
        return self.__transformedZones
