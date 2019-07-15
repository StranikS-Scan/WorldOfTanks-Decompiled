# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicle_systems/components/CrashedTracks.py
import weakref
import math_utils
import Math
import BigWorld
import TriggersManager
from TriggersManager import TRIGGER_TYPE
from svarog_script.auto_properties import AutoProperty
from svarog_script.py_component import Component
from vehicle_systems import model_assembler
from vehicle_systems.tankStructure import getPartModelsFromDesc, TankPartNames, ModelsSetParams
from vehicle_systems.stricted_loading import loadingPriority

class CrashedTrackController(Component):
    baseTracksComponent = AutoProperty()

    def __init__(self, vehicleDesc, trackFashion, modelsSet):
        self.__vehicleDesc = vehicleDesc
        self.__entity = None
        self.__modelsSet = modelsSet
        self.__baseTrackFashion = trackFashion
        self.baseTracksComponent = None
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
        self.baseTracksComponent = None
        return

    def setVisible(self, visibilityMask):
        self.__visibilityMask = visibilityMask
        self.__applyVisibilityMask()
        self.__setupTracksHiding()

    def __setupTrackAssembler(self, entity):
        modelNames = getPartModelsFromDesc(self.__vehicleDesc, ModelsSetParams(self.__modelsSet, 'destroyed', []))
        compoundAssembler = BigWorld.CompoundAssembler()
        compoundAssembler.addRootPart(modelNames.chassis, TankPartNames.CHASSIS, entity.filter.groundPlacingMatrix)
        compoundAssembler.name = TankPartNames.CHASSIS
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
                    BigWorld.loadResourceListBG((trackAssembler,), self.__onModelLoaded, loadingPriority(self.__entity.id))
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
            if self.__flags == 0 and self.__triggerEvents:
                TriggersManager.g_manager.deactivateTrigger(TRIGGER_TYPE.PLAYER_VEHICLE_TRACKS_DAMAGED)
            return

    def receiveShotImpulse(self, direction, impulse):
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
            hideLeftTrack = True
            hideRightTrack = True
        else:
            hideLeftTrack, hideRightTrack = self.__flags & 1, self.__flags & 2
        if self.baseTracksComponent is not None:
            self.baseTracksComponent.disableTrack(hideLeftTrack, hideRightTrack)
        if self.__fashion is not None:
            self.__fashion.changeTrackVisibility(True, hideLeftTrack)
            self.__fashion.changeTrackVisibility(False, hideRightTrack)
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
            self.__fashion = BigWorld.WGVehicleFashion()
            matHandlers = self.__baseTrackFashion.getMaterialHandlers()
            for handler in matHandlers:
                self.__fashion.addMaterialHandler(handler)

            matHandlers = self.__baseTrackFashion.getTrackMaterialHandlers()
            for handler in matHandlers:
                self.__fashion.addTrackMaterialHandler(handler)

            model_assembler.setupTracksFashion(self.__vehicleDesc, self.__fashion)
            self.__model.setupFashions([self.__fashion])
            rotationMProv = math_utils.MatrixProviders.product(self.__entity.model.node('hull'), Math.MatrixInverse(self.__model.node('Tank')))
            self.__model.node('V', rotationMProv)
            self.__setupTracksHiding()
            self.__entity.addModel(self.__model)
            self.__applyVisibilityMask()
            return
