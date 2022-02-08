# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicle_systems/components/debris_crashed_tracks.py
import logging
import random
import CGF
import Vehicular
from cgf_script.managers_registrator import autoregister, onAddedQuery, onRemovedQuery
from vehicle_systems import tankStructure
import math_utils
from vehicle_systems.tankStructure import TankSoundObjectsIndexes
import GenericComponents
from constants import IS_CGF_DUMP
if not IS_CGF_DUMP:
    from CustomEffectManager import CustomEffectManager
_logger = logging.getLogger(__name__)

class TrackCrashWithDebrisComponent(object):
    isLeft = property(lambda self: self.__isLeft)
    pairIndex = property(lambda self: self.__pairIndex)
    vehicleDescriptor = property(lambda self: self.__vehicleDescriptor)
    wheelsGameObject = property(lambda self: self.__wheelsGameObject)
    boundEffects = property(lambda self: self.__boundEffects)
    repaired = property(lambda self: self.__repaired)
    debrisGameObject = property(lambda self: self.__debrisGameObject)
    trackPairDesc = property(lambda self: self.vehicleDescriptor.chassis.tracks.trackPairs[self.pairIndex])

    @property
    def debrisDesc(self):
        return self.trackPairDesc.tracksDebris.left if self.isLeft else self.trackPairDesc.tracksDebris.right

    @property
    def isTopPriority(self):
        return self.__isTopPriority

    @isTopPriority.setter
    def isTopPriority(self, value):
        self.__isTopPriority = value

    @property
    def isPlayer(self):
        return self.__isPlayer

    @isPlayer.setter
    def isPlayer(self, value):
        self.__isPlayer = value

    @property
    def isFlying(self):
        return self.__isSideFlying

    @isFlying.setter
    def isFlying(self, value):
        self.__isSideFlying = value

    def __init__(self, isLeft, pairIndex, vehicleDescriptor, wheelsGameObject, boundEffects):
        self.__isLeft = isLeft
        self.__pairIndex = pairIndex
        self.__vehicleDescriptor = vehicleDescriptor
        self.__wheelsGameObject = wheelsGameObject
        self.__boundEffects = boundEffects
        self.__debrisGameObject = None
        self.__repaired = False
        self.__isTopPriority = False
        self.__isPlayer = False
        self.__isFlying = False
        return

    def createDebrisGameObject(self, spaceID):
        if self.__debrisGameObject is not None:
            _logger.error('Debris go already created, something went wrong')
            CGF.removeGameObject(self.__debrisGameObject)
        self.__debrisGameObject = CGF.GameObject(spaceID)
        return self.__debrisGameObject

    def removeDebrisGameObject(self):
        if self.__debrisGameObject is not None:
            CGF.removeGameObject(self.__debrisGameObject)
            self.__debrisGameObject = None
        return

    def markAsRepaired(self):
        self.__repaired = True


class NodeRemapperComponent(object):
    nodes = property(lambda self: self.__nodes)

    def __init__(self, nodes):
        self.__nodes = nodes


@autoregister(presentInAllWorlds=True, presentInEditor=True)
class DebrisCrashedTracksManager(CGF.ComponentManager):
    RTPC_OUTER_TRACK_STATE = 'RTPC_ext_treads_outer'
    DEBRIS_MAX_LIFETIME = 10

    def __switchVehicleTrackVisibility(self, track, debris, isVisible):
        amountOfBrokenTracks = 0 if isVisible else 1
        track.disableTrack(not isVisible)
        if not debris.wheelsGameObject.isValid():
            return amountOfBrokenTracks
        else:
            animator = debris.wheelsGameObject.findComponentByType(Vehicular.GeneralWheelsAnimator)
            if animator is not None:
                for wheelIdx in track.connectedWheels:
                    if isVisible:
                        animator.relinkTrack(wheelIdx, track.trackThickness)
                    animator.unlinkFromTrack(wheelIdx, track.trackThickness)

            vehicleTracks = debris.wheelsGameObject.findComponentByType(Vehicular.VehicleTracks)
            amountOfBrokenTracks = 0
            if vehicleTracks is not None:
                for otherTrackIdx in xrange(vehicleTracks.getPairsCount()):
                    otherTrackGo = vehicleTracks.getTrackGameObject(track.isLeft, otherTrackIdx)
                    otherTrack = otherTrackGo.findComponentByType(Vehicular.CompositeTrack)
                    thicknessAdjustment = 0 if isVisible else -track.trackThickness
                    otherTrack.adjustTrackThickness(thicknessAdjustment)
                    otherTrack.forceSendLeadingWheelScrollLinks(animator)
                    if otherTrackGo.findComponentByType(TrackCrashWithDebrisComponent) is not None:
                        amountOfBrokenTracks += 1
                    otherTrackGo = vehicleTracks.getTrackGameObject(not track.isLeft, otherTrackIdx)
                    if otherTrackGo.findComponentByType(TrackCrashWithDebrisComponent) is not None:
                        amountOfBrokenTracks += 1

            suspension = debris.wheelsGameObject.findComponentByType(Vehicular.Suspension)
            if suspension is not None:
                suspension.forceCorrectionRecalculation()
            return amountOfBrokenTracks

    def __generateDestructionEffect(self, debris):
        debrisDesc = debris.debrisDesc
        effectData = debrisDesc.destructionEffectData
        if effectData is not None:
            keyPoints, effects, _ = random.choice(effectData)
            debris.boundEffects.addNewToNode(tankStructure.TankPartNames.CHASSIS, math_utils.createIdentityMatrix(), effects, keyPoints, isPlayerVehicle=debris.isPlayer)
        return

    def __remapNodes(self, debris):
        go = debris.wheelsGameObject
        debrisDesc = debris.debrisDesc
        nodes = {}
        existingRemap = go.findComponentByType(NodeRemapperComponent)
        if existingRemap is not None:
            nodes = dict(existingRemap.nodes)
            go.removeComponentByType(NodeRemapperComponent)
        for fromNode, toNode in debrisDesc.nodesRemap.iteritems():
            nodes[fromNode] = toNode

        go.createComponent(NodeRemapperComponent, nodes)
        return

    def __unmapNodes(self, debris):
        go = debris.wheelsGameObject
        if not go.isValid():
            return
        else:
            existingRemap = go.findComponentByType(NodeRemapperComponent)
            if existingRemap is None:
                return
            nodes = dict(existingRemap.nodes)
            debrisDesc = debris.debrisDesc
            for fromNode, _ in debrisDesc.nodesRemap.iteritems():
                del nodes[fromNode]

            go.removeComponentByType(NodeRemapperComponent)
            if nodes:
                go.createComponent(NodeRemapperComponent, nodes)
            return

    def __adjustTrackAudition(self, amountOfBrokenTracks, appearanceGo):
        if not appearanceGo.isValid():
            return
        else:
            audition = appearanceGo.findComponentByType(Vehicular.VehicleAudition)
            if audition is None:
                return
            soundObject = audition.getSoundObject(TankSoundObjectsIndexes.CHASSIS)
            rtpcValue = 0 if amountOfBrokenTracks == 0 else 1
            soundObject.setRTPC(DebrisCrashedTracksManager.RTPC_OUTER_TRACK_STATE, rtpcValue)
            return

    def __createDebris(self, track, debrisComponent):
        if debrisComponent.debrisDesc.physicalParams is None:
            return
        elif debrisComponent.isFlying:
            return
        else:
            go = debrisComponent.createDebrisGameObject(self.spaceID)
            track.createDebris(go, debrisComponent.isTopPriority, debrisComponent.debrisDesc.physicalParams.hingeJointStiffness)
            go.activate()
            return

    @onAddedQuery(Vehicular.CompositeTrack, TrackCrashWithDebrisComponent)
    def processCrash(self, track, debris):
        self.__createDebris(track, debris)
        amountOfBrokenTracks = self.__switchVehicleTrackVisibility(track, debris, False)
        self.__adjustTrackAudition(amountOfBrokenTracks, debris.wheelsGameObject)
        self.__generateDestructionEffect(debris)
        self.__remapNodes(debris)

    @onRemovedQuery(Vehicular.CompositeTrack, TrackCrashWithDebrisComponent)
    def processRepair(self, track, debris):
        self.__unmapNodes(debris)
        amountOfBrokenTracks = self.__switchVehicleTrackVisibility(track, debris, True)
        self.__adjustTrackAudition(amountOfBrokenTracks, debris.wheelsGameObject)
        if debris.repaired:
            debris.removeDebrisGameObject()
        else:
            go = debris.debrisGameObject
            if go is not None:
                go.createComponent(GenericComponents.RemoveGoDelayedComponent, self.DEBRIS_MAX_LIFETIME)
        return


if not IS_CGF_DUMP:

    @onAddedQuery(NodeRemapperComponent, CustomEffectManager)
    def performNodeRemap(self, nodeRemapper, customEffectManager):
        for fromNode, toNode in nodeRemapper.nodes.iteritems():
            customEffectManager.remapNode(fromNode, toNode)


    @onRemovedQuery(NodeRemapperComponent, CustomEffectManager)
    def performNodeUnmap(self, nodeRemapper, customEffectManager):
        for fromNode, _ in nodeRemapper.nodes.iteritems():
            customEffectManager.remapNode(fromNode, '')
