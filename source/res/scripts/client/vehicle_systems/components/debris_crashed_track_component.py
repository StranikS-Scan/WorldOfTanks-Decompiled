# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicle_systems/components/debris_crashed_track_component.py
import logging
import CGF
_logger = logging.getLogger(__name__)

class DebrisCrashedTrackComponent(object):
    MAX_DEBRIS_COUNT = (14, 10, 4)
    CURRENT_DEBRIS_COUNT = 0
    isLeft = property(lambda self: self.__isLeft)
    pairIndex = property(lambda self: self.__pairIndex)
    vehicleDescriptor = property(lambda self: self.__vehicleDescriptor)
    wheelsGameObject = property(lambda self: self.__wheelsGameObject)
    boundEffects = property(lambda self: self.__boundEffects)
    vehicleFilter = property(lambda self: self.__vehicleFilter)
    debrisGameObject = property(lambda self: self.__debrisGameObject)
    trackPairDesc = property(lambda self: self.vehicleDescriptor.chassis.tracks.trackPairs[self.pairIndex])

    @property
    def debrisDesc(self):
        return self.trackPairDesc.tracksDebris.left if self.isLeft else self.trackPairDesc.tracksDebris.right

    @property
    def hitPoint(self):
        return self.__hitPoint

    @property
    def shouldCreateDebris(self):
        return self.__shouldCreateDebris

    @property
    def isPlayer(self):
        return self.__isPlayer

    @property
    def modelsSet(self):
        return self.__modelsSet

    def __init__(self, isLeft, pairIndex, vehicleDescriptor, wheelsGameObject, boundEffects, vehicleFilter, isPlayerVehicle, shouldCreateDebris, hitPoint, modelsSet='default'):
        self.__isLeft = isLeft
        self.__pairIndex = pairIndex
        self.__vehicleDescriptor = vehicleDescriptor
        self.__wheelsGameObject = wheelsGameObject
        self.__boundEffects = boundEffects
        self.__vehicleFilter = vehicleFilter
        self.__isPlayer = isPlayerVehicle
        self.__shouldCreateDebris = shouldCreateDebris
        self.__hitPoint = hitPoint
        self.__modelsSet = modelsSet
        self.__debrisGameObject = None
        if shouldCreateDebris:
            DebrisCrashedTrackComponent.CURRENT_DEBRIS_COUNT += 1
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


class NodeRemapperComponent(object):
    nodes = property(lambda self: self.__nodes)

    def __init__(self, nodes):
        self.__nodes = nodes
