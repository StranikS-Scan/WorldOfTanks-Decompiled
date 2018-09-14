# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicle_systems/vehicle_assembler.py
from CustomEffectManager import CustomEffectManager
import functools
from constants import VEHICLE_PHYSICS_MODE
from vehicle_systems.vehicle_audition_wwise import EngineAuditionWWISE, TrackCrashAuditionWWISE
import weakref
import BigWorld
from VehicleAppearance import VehicleAppearance
from vehicle_systems.engine_state import DetailedEngineStateWWISE
import WoT

def createAssembler(vehicle):
    return PanzerAssemblerWWISE(vehicle)


class VehicleAssembler(object):
    appearance = property(lambda self: self.__appearance)

    def __init__(self, vehicle):
        self.__appearance = VehicleAppearance()
        self.__vehicleRef = weakref.ref(vehicle)

    def prerequisites(self):
        prereqs = self.__appearance.prerequisites(self.__vehicleRef())
        return prereqs

    def _assembleParts(self, vehicle, appearance):
        pass

    def constructAppearance(self, prereqs):
        self._assembleParts(self.__vehicleRef(), self.__appearance)
        return self.__appearance


class PanzerAssemblerWWISE(VehicleAssembler):

    @staticmethod
    def __assembleEngineState(vehicle):
        detailedEngineState = DetailedEngineStateWWISE()
        isPlayerVehicle = vehicle.isPlayerVehicle
        if isPlayerVehicle:
            detailedEngineState.physicRPMLink = lambda : WoT.unpackAuxVehiclePhysicsData(BigWorld.player().ownVehicleAuxPhysicsData)[5]
            detailedEngineState.physicGearLink = lambda : BigWorld.player().ownVehicleGear
        else:
            detailedEngineState.physicRPMLink = lambda : 0.0
            detailedEngineState.physicGearLink = lambda : 0
        return detailedEngineState

    @staticmethod
    def __assembleEngineAudition(vehicle, appearance):
        vehicle = weakref.proxy(vehicle)
        appearance = weakref.proxy(appearance)
        engineAudition = EngineAuditionWWISE(vehicle.physicsMode, vehicle.isPlayerVehicle, appearance.modelsDesc, vehicle.typeDescriptor, vehicle.id)
        e = engineAudition
        e.isUnderwaterLink = lambda : appearance.isUnderwater
        e.isInWaterLink = lambda : appearance.isInWater
        e.isFlyingLink = functools.partial(PanzerAssemblerWWISE.__isFlying, vehicle, appearance)
        e.curTerrainMatKindLink = lambda : appearance.terrainMatKind
        e.leftTrackScrollLink = lambda : appearance.leftTrackScroll
        e.leftTrackScrollRelativeLink = lambda : appearance._VehicleAppearance__customEffectManager.getParameter('deltaL')
        e.rightTrackScrollLink = lambda : appearance.rightTrackScroll
        e.rightTrackScrollRelativeLink = lambda : appearance._VehicleAppearance__customEffectManager.getParameter('deltaR')
        e.detailedEngineState = appearance.detailedEngineState
        e.vehicleFilter = vehicle.filter
        return e

    @staticmethod
    def __isFlying(vehicle, appearance):
        filter = vehicle.filter
        if filter.placingOnGround:
            contactsWithGround = filter.numLeftTrackContacts + filter.numRightTrackContacts
            return contactsWithGround == 0
        else:
            return appearance.fashion.isFlying

    @staticmethod
    def __createTrackCrashControl(vehicle, appearance):
        if vehicle.physicsMode == VEHICLE_PHYSICS_MODE.DETAILED:
            trackCenterNodes = tuple((appearance._VehicleAppearance__customEffectManager.getTrackCenterNode(x) for x in xrange(2)))
        else:
            trackCenterNodes = tuple((appearance._VehicleAppearance__trailEffects.getTrackCenterNode(x) for x in xrange(2)))
        appearance.trackCrashAudition = TrackCrashAuditionWWISE(trackCenterNodes)

    def _assembleParts(self, vehicle, appearance):
        appearance.detailedEngineState = self.__assembleEngineState(vehicle)
        if not appearance.destroyedState:
            if vehicle.physicsMode == VEHICLE_PHYSICS_MODE.DETAILED:
                appearance.customEffectManager = CustomEffectManager(vehicle, appearance.detailedEngineState)
            self.__createTrackCrashControl(vehicle, appearance)
        if vehicle.isAlive() and not appearance.isPillbox:
            appearance.engineAudition = self.__assembleEngineAudition(vehicle, appearance)
            appearance.detailedEngineState.onEngineStart += appearance.engineAudition.onEngineStart
        if vehicle.isPlayerVehicle:
            soundEffect = BigWorld.player().gunRotator.soundEffect
            if soundEffect is not None:
                BigWorld.player().gunRotator.soundEffect.connectSoundToMatrix(self.appearance.modelsDesc['turret']['model'].matrix)
        return
