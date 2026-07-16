# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicle_systems/components/debris_crashed_track_manager.py
import logging
import random
import CGF
import Vehicular
from items.components.component_constants import MAIN_TRACK_PAIR_IDX
from items.vehicle_items import CHASSIS_ITEM_TYPE
from vehicle_systems import tankStructure
import math_utils
from vehicle_systems.components.CrashedTracks import CrashedTracksController
from vehicle_systems.components.vehicle_pickup_component import VehiclePickupComponent
from vehicle_systems.components.debris_crashed_track_component import DebrisCrashedTrackComponent, NodeRemapperComponent
from vehicle_systems.tankStructure import TankSoundObjectsIndexes
from constants import IS_CGF_DUMP, IS_EDITOR
from functools import partial
if not IS_CGF_DUMP:
    from CustomEffectManager import CustomEffectManager
_logger = logging.getLogger(__name__)

class DebrisCrashedTrackSystem(CGF.System):
    RTPC_OUTER_TRACK_STATE = 'RTPC_ext_treads_outer'
    DEBRIS_MAX_LIFETIME = 10
    Activated = CGF.ActivateReaction(CGF.Rw(Vehicular.CompositeTrack), CGF.ReactRw(DebrisCrashedTrackComponent))
    Deactivated = CGF.DeactivateReaction(CGF.Rw(Vehicular.CompositeTrack), CGF.ReactRw(DebrisCrashedTrackComponent))
    PickupActivated = CGF.ActivateReaction(CGF.ReactRw(VehiclePickupComponent))
    PickupDeactivated = CGF.DeactivateReaction(CGF.ReactRw(VehiclePickupComponent))
    TrackDebrisAccess = CGF.AccessReaction(CGF.Rw(DebrisCrashedTrackComponent))
    CompositeTrackAccess = CGF.AccessReaction(CGF.Rw(Vehicular.CompositeTrack))
    WheelsAccess = CGF.AccessReaction(CGF.Rw(Vehicular.GeneralWheelsAnimator))
    TrackAccess = CGF.AccessReaction(CGF.Rw(Vehicular.VehicleTracks))
    SuspensionAccess = CGF.AccessReaction(CGF.Rw(Vehicular.Suspension))
    NodeAccess = CGF.AccessReaction(CGF.Rw(NodeRemapperComponent))
    AuditionAccess = CGF.AccessReaction(CGF.Rw(Vehicular.VehicleAudition))
    CrashedTracksControllerAccess = CGF.AccessReaction(CGF.Rw(CrashedTracksController))
    if not IS_CGF_DUMP:
        EffectActivated = CGF.ActivateReaction(CGF.ReactRw(NodeRemapperComponent), CustomEffectManager)
        EffectDeactivated = CGF.ActivateReaction(CGF.ReactRw(NodeRemapperComponent), CustomEffectManager)
        Reactions = CGF.Reactions(Activated, Deactivated, PickupActivated, PickupDeactivated, CompositeTrackAccess, TrackDebrisAccess, EffectActivated, EffectDeactivated, WheelsAccess, TrackAccess, SuspensionAccess, NodeAccess, AuditionAccess, CrashedTracksControllerAccess)
    else:
        Reactions = CGF.Reactions(Activated, Deactivated, PickupActivated, PickupDeactivated, CompositeTrackAccess, TrackDebrisAccess, WheelsAccess, TrackAccess, SuspensionAccess, NodeAccess, AuditionAccess, CrashedTracksControllerAccess)

    def update(self):
        debrisTrackAccess = self.reaction(self.TrackDebrisAccess)
        compositeTrackAccess = self.reaction(self.CompositeTrackAccess)
        wheelsAccess = self.reaction(self.WheelsAccess)
        tracksAccess = self.reaction(self.TrackAccess)
        suspensionAccess = self.reaction(self.SuspensionAccess)
        remapperAccess = self.reaction(self.NodeAccess)
        auditionAccess = self.reaction(self.AuditionAccess)
        crashedTracksControllerAccess = self.reaction(self.CrashedTracksControllerAccess)
        queue = CGF.CommandQueue(self.gom)
        for track, debris in self.reaction(self.Deactivated):
            self.__unmapNodes(debris, queue, remapperAccess)
            amountOfBrokenTracks = self.__switchVehicleTrackVisibility(track, debris, True, wheelsAccess, tracksAccess, compositeTrackAccess, debrisTrackAccess, suspensionAccess)
            self.__adjustTrackAudition(amountOfBrokenTracks, debris.wheelsGameObject, auditionAccess)
            debris.removeDebrisGameObject()
            if debris.shouldCreateDebris:
                DebrisCrashedTrackComponent.CURRENT_DEBRIS_COUNT -= 1

        for pickup in self.reaction(self.PickupDeactivated):
            if pickup.appearance is not None:
                self.__recreatePhysicalDestroyedTracks(pickup.appearance, queue, compositeTrackAccess, debrisTrackAccess, tracksAccess)

        for pickup in self.reaction(self.PickupActivated):
            if pickup.appearance is not None:
                self.__removePhysicalDestroyedTracks(pickup.appearance, debrisTrackAccess)

        for track, debris in self.reaction(self.Activated):
            self.__createDebris(track, debris, queue, tracksAccess)
            amountOfBrokenTracks = self.__switchVehicleTrackVisibility(track, debris, False, wheelsAccess, tracksAccess, compositeTrackAccess, debrisTrackAccess, suspensionAccess)
            self.__adjustTrackAudition(amountOfBrokenTracks, debris.wheelsGameObject, auditionAccess)
            self.__generateDestructionEffect(debris)
            self.__remapNodes(debris, queue, remapperAccess)
            controller = crashedTracksControllerAccess.find(debris.wheelsGameObject)
            if controller and not controller.hasDebris(debris.isLeft, debris.pairIndex):
                queue.removeComponent(debris.object, DebrisCrashedTrackComponent)

        if not IS_CGF_DUMP:
            for node, effect in self.reaction(self.EffectDeactivated):
                for fromNode, _ in node.nodes.iteritems():
                    effect.remapNode(fromNode, '')

            for node, effect in self.reaction(self.EffectActivated):
                for fromNode, toNode in node.nodes.iteritems():
                    effect.remapNode(fromNode, toNode)

        queue.submit()
        return

    def __forEachValidTrackGameObject(self, appearance, predicate):
        if appearance is None or appearance.typeDescriptor is None or appearance.tracks is None:
            return
        else:
            chassis = appearance.typeDescriptor.chassis
            if chassis is None:
                return
            pairsCount = len(chassis.tracks.trackPairs) if chassis.tracks is not None else 1
            indices = xrange(pairsCount)
            for idx in indices:
                for isLeft in (True, False):
                    trackGO = appearance.tracks.getTrackGameObject(isLeft, idx)
                    if trackGO.valid:
                        predicate(trackGO)

            return

    def __removePhysicalDestroyedTrack(self, debrisTrackAccess, trackGO):
        debris = debrisTrackAccess.find(trackGO)
        if debris is not None:
            debris.removeDebrisGameObject()
        return

    def __removePhysicalDestroyedTracks(self, appearance, debrisTrackAccess):
        self.__forEachValidTrackGameObject(appearance, partial(self.__removePhysicalDestroyedTrack, debrisTrackAccess))

    def __recreatePhysicalDestroyedTrack(self, queue, compositeTrackAccess, debrisTrackAccess, tracksAccess, trackGO):
        compositeTrack = compositeTrackAccess.find(trackGO)
        debris = debrisTrackAccess.find(trackGO)
        if debris is not None and compositeTrack is not None:
            self.__createDebris(compositeTrack, debris, queue, tracksAccess)
        return

    def __recreatePhysicalDestroyedTracks(self, appearance, queue, compositeTrackAccess, debrisTrackAccess, tracksAccess):
        self.__forEachValidTrackGameObject(appearance, partial(self.__recreatePhysicalDestroyedTrack, queue, compositeTrackAccess, debrisTrackAccess, tracksAccess))

    def __switchVehicleTrackVisibility(self, track, debris, isVisible, wheelsAccess, tracksAccess, compositeTrackAccess, debrisTrackAccess, suspensionAccess):
        amountOfBrokenTracks = 0 if isVisible else 1
        track.disableTrack(not isVisible)
        if not debris.wheelsGameObject.valid:
            return amountOfBrokenTracks
        else:
            animator = wheelsAccess.find(debris.wheelsGameObject)
            chassisType = debris.vehicleDescriptor.chassis.chassisType
            isYohMechanics = chassisType == CHASSIS_ITEM_TYPE.TRACK_WITHIN_TRACK and debris.pairIndex != MAIN_TRACK_PAIR_IDX
            if animator is not None and isYohMechanics:
                for wheelIdx in track.connectedWheels:
                    if isVisible:
                        animator.relinkTrack(wheelIdx, track.trackThickness)
                    animator.unlinkFromTrack(wheelIdx, track.trackThickness)

            vehicleTracks = tracksAccess.find(debris.wheelsGameObject)
            amountOfBrokenTracks = 0
            if vehicleTracks is not None:
                for otherTrackIdx in xrange(vehicleTracks.getPairsCount()):
                    otherTrackGo = vehicleTracks.getTrackGameObject(track.isLeft, otherTrackIdx)
                    otherTrack = compositeTrackAccess.find(otherTrackGo)
                    thicknessAdjustment = 0 if isVisible else -track.trackThickness
                    otherTrack.adjustTrackThickness(thicknessAdjustment)
                    if animator is not None:
                        otherTrack.forceSendWheelScrollLinks(animator)
                    if debrisTrackAccess.contains(otherTrackGo):
                        amountOfBrokenTracks += 1
                    otherTrackGo = vehicleTracks.getTrackGameObject(not track.isLeft, otherTrackIdx)
                    if debrisTrackAccess.contains(otherTrackGo):
                        amountOfBrokenTracks += 1

            suspension = suspensionAccess.find(debris.wheelsGameObject)
            if suspension:
                suspension.forceCorrectionRecalculation()
            return amountOfBrokenTracks

    def __generateDestructionEffect(self, debris):
        if debris.trackPairDesc.tracksDebris is None:
            return
        else:
            debrisDesc = debris.debrisDesc
            effectData = debrisDesc.destructionEffectData
            if effectData is not None:
                keyPoints, effects, _ = random.choice(effectData)
                debris.boundEffects.addNewToNode(tankStructure.TankPartNames.CHASSIS, math_utils.createIdentityMatrix(), effects, keyPoints, isPlayerVehicle=debris.isPlayer)
            return

    def __remapNodes(self, debris, queue, remapperAccess):
        if debris.trackPairDesc.tracksDebris is None:
            return
        else:
            go = debris.wheelsGameObject
            if IS_EDITOR and not go.valid:
                return
            debrisDesc = debris.debrisDesc
            nodes = {}
            existingRemap = remapperAccess.find(go)
            if not existingRemap and queue.hasComponent(go, NodeRemapperComponent):
                existingRemap = queue.component(go, NodeRemapperComponent)
            if existingRemap:
                nodes = dict(existingRemap.nodes)
                queue.removeComponent(go, NodeRemapperComponent)
            for fromNode, toNode in debrisDesc.nodesRemap.iteritems():
                nodes[fromNode] = toNode

            queue.assignComponent(go, NodeRemapperComponent(nodes))
            return

    def __unmapNodes(self, debris, queue, remapperAccess):
        go = debris.wheelsGameObject
        if not go.valid:
            return
        existingRemap = remapperAccess.find(go)
        if not existingRemap:
            return
        nodes = dict(existingRemap.nodes)
        debrisDesc = debris.debrisDesc
        for fromNode, _ in debrisDesc.nodesRemap.iteritems():
            del nodes[fromNode]

        queue.removeComponent(go, NodeRemapperComponent)
        if nodes:
            queue.assignComponent(go, NodeRemapperComponent(nodes))

    def __adjustTrackAudition(self, amountOfBrokenTracks, appearanceGo, auditionAccess):
        if not appearanceGo.valid:
            return
        else:
            audition = auditionAccess.find(appearanceGo)
            if audition is None:
                return
            soundObject = audition.getSoundObject(TankSoundObjectsIndexes.CHASSIS)
            rtpcValue = 0 if amountOfBrokenTracks == 0 else 1
            soundObject.setRTPC(DebrisCrashedTrackSystem.RTPC_OUTER_TRACK_STATE, rtpcValue)
            return

    def __createDebris(self, track, debrisComponent, queue, tracksAccess):
        if not debrisComponent.shouldCreateDebris:
            return
        elif debrisComponent.trackPairDesc.tracksDebris is None or debrisComponent.debrisDesc.physicalParams is None or not debrisComponent.wheelsGameObject.valid:
            return
        else:
            vehicleTracks = tracksAccess.find(debrisComponent.wheelsGameObject)
            if vehicleTracks is None:
                return
            trackGO = vehicleTracks.getTrackGameObject(debrisComponent.isLeft, debrisComponent.pairIndex)
            go = debrisComponent.createDebrisGameObject(queue)
            queue.createComponent(go, CGF.HierarchyComponent, trackGO)
            track.createDebris(queue, go, debrisComponent.hitPoint, debrisComponent.vehicleFilter, debrisComponent.debrisDesc.physicalParams, debrisComponent.modelsSet, debrisComponent.isPlayer)
            queue.activateGameObject(go)
            return
