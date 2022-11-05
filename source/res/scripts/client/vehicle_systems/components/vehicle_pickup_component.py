# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicle_systems/components/vehicle_pickup_component.py
import CGF
import Vehicular
import Math
import math
from cgf_script.managers_registrator import autoregister, onAddedQuery, onProcessQuery
from vehicle_systems.components.debris_crashed_tracks import TrackCrashWithDebrisComponent, DebrisCrashedTracksManager
import GenericComponents

class VehiclePickupComponent(object):
    MAX_ANGLE_DEVIATION = 5.0
    MAX_LIFETIME = 1.0

    def __init__(self, appearance, vehicleGameObject):
        self.__appearance = appearance
        self.__vehicleGameObject = vehicleGameObject
        self.time = 0.0

    def __forEachValidTrackGameObject(self, predicate):
        chassis = self.__appearance.typeDescriptor.chassis
        pairsCount = len(chassis.tracks.trackPairs) if chassis.tracks is not None else 1
        indices = xrange(pairsCount)
        if self.__appearance.tracks is not None:
            for idx in indices:
                for isLeft in (True, False):
                    trackGO = self.__appearance.tracks.getTrackGameObject(isLeft, idx)
                    if trackGO.isValid():
                        predicate(trackGO)

        return

    def removePhysicalDestroyedTracks(self):

        def removePhysicalDestroyedTrack(trackGO):
            debris = trackGO.findComponentByType(TrackCrashWithDebrisComponent)
            if debris is not None:
                debris.removeDebrisGameObject()
            return

        self.__forEachValidTrackGameObject(removePhysicalDestroyedTrack)

    def recreatePhysicalDestroyedTracks(self):

        def recreatePhysicalDestroyedTrack(trackGO):
            compositeTrack = trackGO.findComponentByType(Vehicular.CompositeTrack)
            debris = trackGO.findComponentByType(TrackCrashWithDebrisComponent)
            manager = CGF.getManager(self.__appearance.spaceID, DebrisCrashedTracksManager)
            if debris is not None and compositeTrack is not None and manager is not None:
                manager.createDebris(compositeTrack, debris)
            return

        self.__forEachValidTrackGameObject(recreatePhysicalDestroyedTrack)

    def onPickupComplete(self):
        self.recreatePhysicalDestroyedTracks()
        self.__vehicleGameObject.removeComponent(self)


@autoregister(presentInAllWorlds=True, presentInEditor=True)
class VehiclePickupManager(CGF.ComponentManager):

    @onAddedQuery(VehiclePickupComponent)
    def startPickup(self, vehiclePickupComponent):
        vehiclePickupComponent.removePhysicalDestroyedTracks()

    @onProcessQuery(VehiclePickupComponent, GenericComponents.TransformComponent)
    def processPickup(self, vehiclePickupComponent, vehicleTransform):
        dt = self.clock.gameDelta
        vehiclePickupComponent.time += dt
        if vehiclePickupComponent.time > VehiclePickupComponent.MAX_LIFETIME:
            vehiclePickupComponent.onPickupComplete()
        tankUp = vehicleTransform.worldTransform.applyToAxis(1)
        angle = math.degrees(tankUp.angle(Math.Vector3(0, 1, 0)))
        if angle < VehiclePickupComponent.MAX_ANGLE_DEVIATION:
            vehiclePickupComponent.onPickupComplete()
