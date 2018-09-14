# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicle_systems/components/CrashedTracks.py
import weakref
import BigWorld
import TriggersManager
from TriggersManager import TRIGGER_TYPE
from VehicleUtils import setupTracksFashion
from vehicle_systems.tankStructure import getPartModelsFromDesc, TankPartNames
from collections import deque

def testAllocate(spaceID):
    import items.vehicles
    vehicleDesc = items.vehicles.VehicleDescr(typeName=items.vehicles.g_cache.vehicle(0, 1).name)
    entityId = BigWorld.createEntity('OfflineEntity', spaceID, 0, BigWorld.camera().position, (0, 0, 0), dict())
    return CrashedTrackController(vehicleDesc, BigWorld.entity(entityId))


class CrashedTrackController:

    class __HIDING_FLAGS:
        NONE = 0
        LEFT = 1
        RIGHT = 2
        STEERING = 4
        LEADING = 8

    class __CRASHED_WHEELS_MATERIALS:
        RIGHT_STEER = 'chassis_WD_R0'
        RIGHT_LEAD = 'chassis_WD_R1'
        LEFT_STEER = 'chassis_WD_L0'
        LEFT_LEAD = 'chassis_WD_L1'

    class __WHEELS_MATERIALS:
        RIGHT_STEER = 'chassis_WD_R0_skinned'
        RIGHT_LEAD = 'chassis_WD_R1_skinned'
        LEFT_STEER = 'chassis_WD_L0_skinned'
        LEFT_LEAD = 'chassis_WD_L1_skinned'

    def __init__(self, vehicleDesc, entity=None, trackFashion=None, triggerEvents=False):
        self.__vehicleDesc = vehicleDesc
        self.__entity = weakref.proxy(entity)
        self.__baseTrackFashion = trackFashion
        self.__triggerEvents = triggerEvents
        self.__flags = self.__HIDING_FLAGS.NONE
        self.__model = None
        self.__fashion = None
        self.__loading = False
        self.__wreckedWheels = None
        self.__visibilityMask = 15
        return

    def isLeftTrackBroken(self):
        return self.__flags & self.__HIDING_FLAGS.LEFT

    def isRightTrackBroken(self):
        return self.__flags & self.__HIDING_FLAGS.RIGHT

    def destroy(self):
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

    def __setupTrackAssembler(self):
        modelNames = getPartModelsFromDesc(self.__vehicleDesc, 'destroyed')
        compoundAssembler = BigWorld.CompoundAssembler()
        compoundAssembler.addRootPart(modelNames.chassis, TankPartNames.CHASSIS, [('Tank', ''), ('V', 'Tank')], self.__entity.matrix)
        compoundAssembler.assemblerName = TankPartNames.CHASSIS
        compoundAssembler.spaceID = self.__entity.spaceID
        return compoundAssembler

    def __getMaterial(self, isLeft, isLeading, crashed=False):
        if isLeft:
            if isLeading:
                if crashed:
                    return self.__CRASHED_WHEELS_MATERIALS.LEFT_LEAD
                else:
                    return self.__WHEELS_MATERIALS.LEFT_LEAD
            elif crashed:
                return self.__CRASHED_WHEELS_MATERIALS.LEFT_STEER
            else:
                return self.__WHEELS_MATERIALS.LEFT_STEER

        elif isLeading:
            if crashed:
                return self.__CRASHED_WHEELS_MATERIALS.RIGHT_LEAD
            else:
                return self.__WHEELS_MATERIALS.RIGHT_LEAD
        else:
            if crashed:
                return self.__CRASHED_WHEELS_MATERIALS.RIGHT_STEER
            return self.__WHEELS_MATERIALS.RIGHT_STEER

    def addWheel(self, isLeft, isLeading):
        if self.__entity is None:
            return
        else:
            if self.__wreckedWheels is None:
                self.__wreckedWheels = deque()
            self.__wreckedWheels.append((isLeft, isLeading))
            if self.__model is None:
                if not self.__loading:
                    BigWorld.loadResourceListBG((self.__setupTrackAssembler(),), self.__onModelLoaded)
                    self.__loading = True
            else:
                self.__setupTracksHiding()
            return

    def delWheel(self, isLeft, isLeading):
        if self.__entity is None:
            return
        else:
            self.__wreckedWheels.remove((isLeft, isLeading))
            materialName = self.__getMaterial(isLeft, isLeading)
            crashedMaterialName = self.__getMaterial(isLeft, isLeading, True)
            if self.__baseTrackFashion is not None:
                self.__baseTrackFashion.setWheelVisibility(materialName, True)
            if self.__fashion is not None:
                self.__fashion.setWheelVisibility(crashedMaterialName, False)
            return

    def addTrack(self, isLeft):
        if self.__entity is None:
            return
        else:
            if self.__flags == self.__HIDING_FLAGS.NONE and self.__triggerEvents:
                TriggersManager.g_manager.activateTrigger(TriggersManager.TRIGGER_TYPE.PLAYER_VEHICLE_TRACKS_DAMAGED)
            if self.__entity.filter.placingOnGround:
                flying = self.__entity.filter.numLeftTrackContacts == 0
                self.__flags |= self.__HIDING_FLAGS.LEFT if isLeft else self.__HIDING_FLAGS.RIGHT
            elif isLeft:
                flying = self.__baseTrackFashion.isFlyingLeft
                self.__flags |= self.__HIDING_FLAGS.LEFT
            else:
                flying = self.__baseTrackFashion.isFlyingRight
                self.__flags |= self.__HIDING_FLAGS.RIGHT
            if isLeft:
                self.__flags |= self.__HIDING_FLAGS.LEFT
            else:
                self.__flags |= self.__HIDING_FLAGS.RIGHT
            if self.__model is None and (not flying or 'wheeledVehicle' in self.__vehicleDesc.type.tags):
                if not self.__loading:
                    BigWorld.loadResourceListBG((self.__setupTrackAssembler(),), self.__onModelLoaded)
                    self.__loading = True
            else:
                self.__setupTracksHiding()
            return

    def delTrack(self, isLeft):
        if isLeft:
            self.__flags &= ~self.__HIDING_FLAGS.LEFT
        else:
            self.__flags &= ~self.__HIDING_FLAGS.RIGHT
        self.__loading = bool(self.__flags) and self.__loading
        if self.__entity is None:
            return
        else:
            if self.__flags == self.__HIDING_FLAGS.NONE and self.__model is not None:
                self.__entity.delModel(self.__model)
                self.__model = None
                self.__fashion = None
            self.__setupTracksHiding()
            if self.__flags != self.__HIDING_FLAGS.NONE and self.__triggerEvents:
                TriggersManager.g_manager.deactivateTrigger(TRIGGER_TYPE.PLAYER_VEHICLE_TRACKS_DAMAGED)
            return

    def receiveShotImpulse(self, dir, impulse):
        pass

    def reset(self):
        if self.__entity is None:
            return
        else:
            if self.__fashion is not None:
                self.__fashion.setCrashEffectCoeff(-1.0)
            self.__flags = self.__HIDING_FLAGS.NONE
            if self.__model is not None:
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
            tracks = (self.__flags & self.__HIDING_FLAGS.LEFT, self.__flags & self.__HIDING_FLAGS.RIGHT)
            invTracks = (not tracks[0], not tracks[1])
        if self.__wreckedWheels is not None:
            for wheel in self.__wreckedWheels:
                materialName = self.__getMaterial(wheel[0], wheel[1])
                crashedMaterialName = self.__getMaterial(wheel[0], wheel[1], True)
                if self.__baseTrackFashion is not None:
                    self.__baseTrackFashion.setWheelVisibility(materialName, False)
                if self.__fashion is not None:
                    self.__fashion.setWheelVisibility(crashedMaterialName, True)

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
        if self.__entity is None or not self.__entity.isAlive() or not self.__loading:
            return
        else:
            self.__loading = False
            model = resources[TankPartNames.CHASSIS]
            self.__model = model
            self.__fashion = BigWorld.WGVehicleFashion(True, 1.0, True, 'wheeledVehicle' in self.__vehicleDesc.type.tags)
            setupTracksFashion(self.__fashion, self.__vehicleDesc, True)
            self.__model.setupFashions([self.__fashion])
            if self.__baseTrackFashion is not None and self.__baseTrackFashion.localSwingingMatrix is not None:
                self.__fashion.setupSwinging(self.__baseTrackFashion.localSwingingMatrix, 'V')
            self.__model.node('V', self.__fashion.localSwingingMatrix)
            self.__fashion.setCrashEffectCoeff(0.0)
            self.__setupTracksHiding()
            self.__entity.addModel(self.__model)
            self.__applyVisibilityMask()
            return
