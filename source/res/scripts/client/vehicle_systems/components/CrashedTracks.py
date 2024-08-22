# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicle_systems/components/CrashedTracks.py
import weakref
import math_utils
import Math
import BigWorld
from cgf_obsolete_script.auto_properties import AutoProperty
from cgf_obsolete_script.py_component import Component
from items.components.component_constants import MAIN_TRACK_PAIR_IDX, DEFAULT_TRACK_HIT_VECTOR, TrackState
from items.vehicle_items import CHASSIS_ITEM_TYPE
from vehicle_systems import model_assembler
from vehicle_systems.tankStructure import getPartModelsFromDesc, TankPartNames, ModelsSetParams
from vehicle_systems.stricted_loading import loadingPriority, makeCallbackWeak
from constants import IS_EDITOR

class _TRACK_SIDE(object):
    LEFT = 'left'
    RIGHT = 'right'


class CrashedTrackController(Component):
    baseTracksComponent = AutoProperty()

    def __init__(self, vehicleDesc, trackFashion, modelsSet):
        self.__vehicleDesc = vehicleDesc
        self.__entity = None
        self.__modelsSet = modelsSet
        self.__baseTrackFashion = trackFashion
        self.baseTracksComponent = None
        self.__crashedTracks = None
        self.__resetBrokenTracks()
        self.__model = None
        self.__fashion = None
        self.__loading = False
        self.__isActive = False
        self.__visibilityMask = 15
        return

    def isLeftTrackBroken(self):
        return any([ state.isBroken for state in self.__crashedTracks[_TRACK_SIDE.LEFT] ])

    def isRightTrackBroken(self):
        return any([ state.isBroken for state in self.__crashedTracks[_TRACK_SIDE.RIGHT] ])

    def getTrackStates(self, isLeft):
        side = _TRACK_SIDE.LEFT if isLeft else _TRACK_SIDE.RIGHT
        return [ dict(state._asdict()) for state in self.__crashedTracks[side] ]

    def getPairsCnt(self):
        if self.__vehicleDesc.chassis.tracks is not None:
            pairsCount = len(self.__vehicleDesc.chassis.tracks.trackPairs)
        else:
            pairsCount = 1
        return pairsCount

    def setVehicle(self, entity):
        self.__entity = weakref.proxy(entity)

    def activate(self):
        if self.__entity is not None and self.__model is not None:
            self.__entity.addModel(self.__model)
            self.__applyVisibilityMask()
        self.__isActive = True
        return

    def deactivate(self):
        if self.__entity is not None and not self.__entity.isDestroyed and self.__model is not None:
            self.__entity.delModel(self.__model)
        self.__isActive = False
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

    def receiveShotImpulse(self, direction, impulse):
        pass

    def addCrashedTrack(self, isLeft, pairIndex, hitPoint=None, isFlying=False, isDebris=False):
        if self.__entity is None and not isDebris:
            return
        else:
            self.__setCrashedTrack(isLeft, pairIndex, True, hitPoint if hitPoint else DEFAULT_TRACK_HIT_VECTOR, isDebris)
            if isDebris:
                return
            trackAssembler = self.__setupTrackAssembler(self.__entity)
            if self.__model is None and not isFlying:
                if not self.__loading:
                    self.__loadModel(trackAssembler)
            else:
                self.__setupTracksHiding()
            return

    def delCrashedTrack(self, isLeft, pairIndex):
        self.__setCrashedTrack(isLeft, pairIndex, False, DEFAULT_TRACK_HIT_VECTOR, False)
        hasCrashedTracks = self.__hasCrashedTracks()
        self.__loading = hasCrashedTracks and self.__loading
        if self.__entity is None:
            return
        else:
            if not hasCrashedTracks and self.__model is not None:
                if self.__model.isInWorld:
                    self.__entity.delModel(self.__model)
                self.__model = None
                self.__fashion = None
            self.__setupTracksHiding()
            return

    def __setupTrackAssembler(self, entity):
        modelNames = getPartModelsFromDesc(self.__vehicleDesc, ModelsSetParams(self.__modelsSet, 'destroyed', []))
        compoundAssembler = BigWorld.CompoundAssembler()
        compoundAssembler.addRootPart(modelNames.chassis, TankPartNames.CHASSIS, entity.filter.groundPlacingMatrix)
        compoundAssembler.name = TankPartNames.CHASSIS
        compoundAssembler.spaceID = entity.spaceID
        return compoundAssembler

    def __hasCrashedTracks(self):
        for side in self.__crashedTracks.values():
            for trackState in side:
                if trackState.isBroken:
                    return True

        return False

    def __setCrashedTrack(self, isLeft, pairIndex, isBroken, hitPoint, isDebris):
        side = _TRACK_SIDE.LEFT if isLeft else _TRACK_SIDE.RIGHT
        self.__crashedTracks[side][pairIndex] = TrackState(isBroken, hitPoint, isDebris)

    def __loadModel(self, trackAssembler):
        if not IS_EDITOR:
            BigWorld.loadResourceListBG((trackAssembler,), makeCallbackWeak(self.__onModelLoaded), loadingPriority(self.__entity.id))
            self.__loading = True
        else:
            self.__loading = True
            resourceRefs = BigWorld.loadResourceListFG([trackAssembler])
            self.__onModelLoaded(resourceRefs)

    def __getEmptyTrackStates(self, pairsCount):
        return [ TrackState(False, DEFAULT_TRACK_HIT_VECTOR, False) for _ in range(pairsCount) ]

    def __resetBrokenTracks(self):
        pairsCount = self.getPairsCnt()
        self.__crashedTracks = {_TRACK_SIDE.LEFT: self.__getEmptyTrackStates(pairsCount),
         _TRACK_SIDE.RIGHT: self.__getEmptyTrackStates(pairsCount)}

    def __reset(self):
        if self.__entity is None:
            return
        else:
            self.__resetBrokenTracks()
            if self.__model is not None:
                if self.__model.isInWorld:
                    self.__entity.delModel(self.__model)
                self.__model = None
                self.__fashion = None
                self.__baseTrackFashion = None
            return

    def __isBrokenButDebris(self, side, index):
        state = self.__crashedTracks[side][index]
        return state.isBroken and not state.isDebris

    def __setupTracksHiding(self):
        force = self.__visibilityMask == 0
        trackIndices = []
        tracksPresent = self.__vehicleDesc.chassis.tracks is not None
        if (self.__vehicleDesc.chassis.chassisType == CHASSIS_ITEM_TYPE.MONOLITHIC or self.__vehicleDesc.chassis.chassisType == CHASSIS_ITEM_TYPE.TRACK_WITHIN_TRACK) and tracksPresent:
            trackIndices = list(xrange(len(self.__vehicleDesc.chassis.tracks.trackPairs)))
        elif tracksPresent:
            trackIndices = [MAIN_TRACK_PAIR_IDX]
        if self.baseTracksComponent is not None and self.baseTracksComponent.valid:
            for i in trackIndices:
                hideLeftTrack = force or self.__crashedTracks[_TRACK_SIDE.LEFT][i].isBroken
                hideRightTrack = force or self.__crashedTracks[_TRACK_SIDE.RIGHT][i].isBroken
                self.baseTracksComponent.disableTrack(hideLeftTrack, hideRightTrack, i)

        if self.__fashion is not None:
            for i in trackIndices:
                showLeftDestroyed = force or self.__isBrokenButDebris(_TRACK_SIDE.LEFT, i)
                showRightDestroyed = force or self.__isBrokenButDebris(_TRACK_SIDE.RIGHT, i)
                self.__fashion.changeTrackVisibility(True, showLeftDestroyed, i)
                self.__fashion.changeTrackVisibility(False, showRightDestroyed, i)

        return

    def __applyVisibilityMask(self):
        colorPassEnabled = self.__visibilityMask & BigWorld.ColorPassBit != 0
        if self.__model is not None and self.__model.isValid and self.__model.isInWorld:
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
            if self.__isActive:
                self.__entity.addModel(self.__model)
                self.__applyVisibilityMask()
            return
