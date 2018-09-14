# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicle_systems/components/CrashedTracks.py
import weakref
from AvatarInputHandler import mathUtils
import Math
import BigWorld
import TriggersManager
from TriggersManager import TRIGGER_TYPE
from vehicle_systems import model_assembler
from vehicle_systems.tankStructure import getPartModelsFromDesc, TankPartNames

def testAllocate(spaceID):
    import items.vehicles
    vehicleDesc = items.vehicles.VehicleDescr(typeName=items.vehicles.g_cache.vehicle(0, 1).name)
    entityId = BigWorld.createEntity('OfflineEntity', spaceID, 0, BigWorld.camera().position, (0, 0, 0), dict())
    return CrashedTrackController(vehicleDesc, BigWorld.entity(entityId))


class CrashedTrackController:

    def __init__(self, vehicleDesc, trackFashion=None):
        self.__vehicleDesc = vehicleDesc
        self.__entity = None
        self.__baseTrackFashion = trackFashion
        self.__triggerEvents = False
        self.__flags = 0
        self.__model = None
        self.__fashion = None
        self.__loading = False
        self.__visibilityMask = 15
        return

    def isLeftTrackBroken(self):
        return self.__flags & 1

    def isRightTrackBroken(self):
        return self.__flags & 2

    def setVehicle(self, entity):
        self.__entity = weakref.proxy(entity)
        self.__triggerEvents = entity.isPlayerVehicle

    def activate(self):
        if self.__entity is not None and self.__model is not None:
            self.__entity.addModel(self.__model)
        return

    def deactivate(self):
        if self.__entity is not None and self.__model is not None:
            self.__entity.delModel(self.__model)
        self.__loading = False
        return

    def destroy(self):
        self.__reset()
        self.__entity = None
        self.__model = None
        self.__loading = False
        self.__baseTrackFashion = None
        self.__fashion = None
        return

    def setVisible(self, visibilityMask):
        self.__visibilityMask = visibilityMask
        self.__applyVisibilityMask()
        self.__setupTracksHiding()

    def __setupTrackAssembler(self, entity):
        modelNames = getPartModelsFromDesc(self.__vehicleDesc, 'destroyed')
        compoundAssembler = BigWorld.CompoundAssembler()
        compoundAssembler.addRootPart(modelNames.chassis, TankPartNames.CHASSIS, entity.filter.groundPlacingMatrix)
        compoundAssembler.assemblerName = TankPartNames.CHASSIS
        compoundAssembler.spaceID = entity.spaceID
        return compoundAssembler

    def addTrack(self, isLeft, isFlying=False):
        if self.__entity is None:
            return
        else:
            if self.__flags == 0 and self.__triggerEvents:
                TriggersManager.g_manager.activateTrigger(TriggersManager.TRIGGER_TYPE.PLAYER_VEHICLE_TRACKS_DAMAGED)
            if isLeft:
                self.__flags |= 1
            else:
                self.__flags |= 2
            trackAssembler = self.__setupTrackAssembler(self.__entity)
            if self.__model is None and not isFlying:
                if not self.__loading:
                    BigWorld.loadResourceListBG((trackAssembler,), self.__onModelLoaded)
                    self.__loading = True
            else:
                self.__setupTracksHiding()
            return

    def delTrack(self, isLeft):
        if isLeft:
            self.__flags &= -2
        else:
            self.__flags &= -3
        self.__loading = bool(self.__flags) and self.__loading
        if self.__entity is None:
            return
        else:
            if self.__flags == 0 and self.__model is not None:
                self.__entity.delModel(self.__model)
                self.__model = None
                self.__fashion = None
            self.__setupTracksHiding()
            if self.__flags != 0 and self.__triggerEvents:
                TriggersManager.g_manager.deactivateTrigger(TRIGGER_TYPE.PLAYER_VEHICLE_TRACKS_DAMAGED)
            return

    def receiveShotImpulse(self, dir, impulse):
        pass

    def __reset(self):
        if self.__entity is None:
            return
        else:
            self.__flags = 0
            if self.__model is not None:
                if self.__model.isInWorld:
                    self.__entity.delModel(self.__model)
                self.__model = None
                self.__fashion = None
                self.__baseTrackFashion = None
            return

    def __setupTracksHiding(self):
        force = self.__visibilityMask == 0
        if force:
            tracks = (True, True)
            invTracks = (True, True)
        else:
            tracks = (self.__flags & 1, self.__flags & 2)
            invTracks = (not tracks[0], not tracks[1])
        if self.__baseTrackFashion is not None:
            self.__baseTrackFashion.hideTracks(*tracks)
        if self.__fashion is not None:
            self.__fashion.hideTracks(*invTracks)
        return

    def __applyVisibilityMask(self):
        colorPassEnabled = self.__visibilityMask & BigWorld.ColorPassBit != 0
        if self.__model is not None:
            self.__model.visible = self.__visibilityMask
            self.__model.skipColorPass = not colorPassEnabled
        return

    def __onModelLoaded(self, resources):
        if self.__entity is None or not self.__loading:
            return
        else:
            self.__loading = False
            model = resources[TankPartNames.CHASSIS]
            self.__model = model
            self.__model.matrix = self.__entity.filter.groundPlacingMatrix
            self.__fashion = BigWorld.WGVehicleFashion(True)
            model_assembler.setupTracksFashion(self.__fashion, self.__vehicleDesc, True)
            self.__model.setupFashions([self.__fashion])
            rotationMProv = mathUtils.MatrixProviders.product(self.__entity.model.node('hull'), Math.MatrixInverse(self.__model.node('Tank')))
            self.__model.node('V', rotationMProv)
            self.__fashion.setCrashEffectCoeff(0.0)
            self.__setupTracksHiding()
            self.__entity.addModel(self.__model)
            self.__applyVisibilityMask()
            return
