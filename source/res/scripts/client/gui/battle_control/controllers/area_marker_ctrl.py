# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/area_marker_ctrl.py
import logging
from functools import partial
import Math
import math_utils
import BigWorld
from helpers import dependency
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from shared_utils import findFirst
from skeletons.gui.battle_session import IBattleSessionProvider
from gui.Scaleform.daapi.view.battle.shared.component_marker.markers_controller import BaseMarkerController
_logger = logging.getLogger(__name__)

def fetchEntityMatrix(entityID):
    entity = BigWorld.entities.get(entityID)
    return None if entity is None else entity.matrix


class AreaMarkersController(BaseMarkerController):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(AreaMarkersController, self).__init__()
        self._battleCtx = None
        self._arenaVisitor = None
        self._vehiclesAreaMarkerHandler = VehiclesAreaMarkerHandler(self)
        self._prevGlobalVisibility = None
        return

    def startControl(self, battleCtx, arenaVisitor):
        self._battleCtx = battleCtx
        self._arenaVisitor = arenaVisitor
        self.init()

    def stopControl(self):
        self._battleCtx = None
        self._arenaVisitor = None
        self._vehiclesAreaMarkerHandler.clear()
        self.stop()
        return

    def getControllerID(self):
        return BATTLE_CTRL_ID.AREA_MARKER

    def getPluginID(self):
        pass

    def spaceLoadCompleted(self):
        self.start()

    def setVehiclesAreaMarkerParams(self, vehiclesAreaMarkerParams):
        handler = self._vehiclesAreaMarkerHandler
        handler.unpackVehiclesAreaMarkerParams(vehiclesAreaMarkerParams)
        handler.vehiclesAreaMarkerUpdate()

    def _tickUpdate(self):
        super(AreaMarkersController, self)._tickUpdate()
        player = BigWorld.player()
        if player is None:
            return
        else:
            vehicle = player.getVehicleAttached()
            observableVehiclePosition = vehicle.position if vehicle else None
            for marker in self._markers.itervalues():
                if marker.isEmpty():
                    continue
                distanceToArea = marker.getDistanceToArea(observableVehiclePosition)
                if not self._isMarkerActuallyVisibleImpl(marker, distanceToArea):
                    marker.setVisible(False)
                    continue
                if self._prevGlobalVisibility != self._globalVisibility:
                    self._prevGlobalVisibility = self._globalVisibility
                    marker.setVisible(self._globalVisibility)
                if marker.isVisible:
                    marker.update(int(round(max(0, distanceToArea))))

            return

    def removeAllMarkersAtPoint(self):
        markersIDs = self.allMarkersID
        vehiclesMarkersIDs = self._vehiclesAreaMarkerHandler.getVehiclesMarkersIDs()
        removeList = set(markersIDs) - set(vehiclesMarkersIDs)
        for markerID in removeList:
            self.removeMarker(markerID)

    def isMarkerActuallyVisible(self, marker):
        player = BigWorld.player()
        if player is None:
            return False
        else:
            vehicle = player.getVehicleAttached()
            observableVehiclePosition = vehicle.position if vehicle else None
            distanceToArea = marker.getDistanceToArea(observableVehiclePosition)
            return self._isMarkerActuallyVisibleImpl(marker, distanceToArea)

    def _isMarkerActuallyVisibleImpl(self, marker, distanceToArea):
        conditionDistance = marker.disappearingRadius
        if conditionDistance <= 0:
            return True
        else:
            isHidden = distanceToArea is None or (conditionDistance < distanceToArea if marker.reverseDisappearing else conditionDistance > distanceToArea)
            return not isHidden


class VehiclesAreaMarkerHandler(object):
    _TELEPORT_DISTANCE = 5.0
    _TICK_UPDATE = 0.01

    def __init__(self, parent):
        super(VehiclesAreaMarkerHandler, self).__init__()
        self._parent = parent
        self._vehiclesAreaMarker = {'ID': {},
         'matrix': {},
         'lastCheckTime': {},
         'prevData': {}}
        self._vehiclesAreaMarkerParams = {}
        self._vehiclesCallback = {}

    def clear(self):
        for callbackID in self._vehiclesCallback.itervalues():
            if callbackID:
                BigWorld.cancelCallback(callbackID)

        self._vehiclesCallback.clear()
        self._parent = None
        self._vehiclesAreaMarker.clear()
        self._vehiclesAreaMarkerParams.clear()
        return

    def getVehiclesMarkersIDs(self):
        vehiclesID = self._vehiclesAreaMarker['ID']
        return [ markerID for markerData in vehiclesID.itervalues() for markerID in markerData.itervalues() ]

    def vehiclesAreaMarkerUpdate(self):
        player = BigWorld.player()
        playerVehicleID = player.playerVehicleID if player else None
        if playerVehicleID is None:
            return
        else:
            markerIDs = self._vehiclesAreaMarker.get('ID')
            for vehicleID, params in self._vehiclesAreaMarkerParams.iteritems():
                if vehicleID == playerVehicleID:
                    continue
                markersData = params['markersData']
                for markerData in markersData:
                    vehMarkerList = markerIDs.get(vehicleID)
                    serverID = markerData['markerID']
                    if vehMarkerList is None:
                        self.__addVehicleMarker(markerData, vehicleID, params)
                        self._vehiclesCallback[vehicleID] = BigWorld.callback(self._TICK_UPDATE, partial(self.__updateVehicleMarker, vehicleID, params))
                    elif serverID not in vehMarkerList:
                        self.__addVehicleMarker(markerData, vehicleID, params, False)
                    markerID = markerIDs[vehicleID][serverID]
                    self.__updateVisibility(markerID, markerData['visibility'])

            return

    def unpackVehiclesAreaMarkerParams(self, params):
        for marker in params:
            vehicleID = marker['vehicleID']
            if vehicleID in self._vehiclesAreaMarkerParams:
                continue
            self._vehiclesAreaMarkerParams[vehicleID] = marker

        removeVehicleList = []
        removeMarkerList = []
        markerIDs = self._vehiclesAreaMarker['ID']
        for vehicleID in self._vehiclesAreaMarkerParams.iterkeys():
            marker = findFirst(lambda item: item['vehicleID'] == vehicleID, params)
            if marker is None:
                removeVehicleList.append(vehicleID)
            if vehicleID in markerIDs:
                serverIDs = [ data['markerID'] for data in marker['markersData'] ]
                clientIDs = markerIDs[vehicleID].keys()
                removeMarkerList.extend([ (vehicleID, ID) for ID in clientIDs if ID not in serverIDs ])

        for vehicleID in removeVehicleList:
            self.__removeAllVehicleMarkers(vehicleID)

        for vehicleID, markerID in removeMarkerList:
            self.__removeVehicleMarkerByID(vehicleID, markerID)

        return

    def __addVehicleMarker(self, markerData, vehicleID, params, createMatrix=True):
        vehicle = BigWorld.entities.get(vehicleID)
        vehiclesMatrix = self._vehiclesAreaMarker['matrix']
        positionData = params['positionData']
        position = positionData['position']
        ypr = positionData['ypr']
        parent = self._parent
        if createMatrix:
            vehiclePrevData = self._vehiclesAreaMarker['prevData']
            lastCheckTime = self._vehiclesAreaMarker['lastCheckTime']
            if vehicle:
                vehiclesMatrix.update({vehicleID: {'matrix': vehicle.matrix,
                             'inAoI': True}})
            else:
                vehiclesMatrix.update({vehicleID: {'matrix': math_utils.createRTMatrix(ypr, position),
                             'inAoI': False}})
            vehiclePrevData.update({vehicleID: {'position': position,
                         'ypr': Math.Vector3(ypr)}})
            lastCheckTime.update({vehicleID: BigWorld.time()})
        marker = parent.createMarker(vehiclesMatrix[vehicleID]['matrix'], markerData['markerType'])
        markerID = parent.addMarker(marker)
        self._vehiclesAreaMarker['ID'].setdefault(vehicleID, {}).update({markerData['markerID']: markerID})

    def __removeAllVehicleMarkers(self, vehicleID):
        if vehicleID in self._vehiclesCallback:
            callbackID = self._vehiclesCallback[vehicleID]
            if callbackID:
                BigWorld.cancelCallback(callbackID)
            del self._vehiclesCallback[vehicleID]
        vehiclesAreaMarker = self._vehiclesAreaMarker
        markerIDs = vehiclesAreaMarker['ID']
        if vehicleID in markerIDs:
            for markerID in markerIDs[vehicleID].itervalues():
                self._parent.removeMarker(markerID)

        for dictData in vehiclesAreaMarker.itervalues():
            if vehicleID in dictData:
                del dictData[vehicleID]

        if vehicleID in self._vehiclesAreaMarkerParams:
            del self._vehiclesAreaMarkerParams[vehicleID]

    def __removeVehicleMarkerByID(self, vehicleID, serverID):
        markerIDs = self._vehiclesAreaMarker['ID']
        if vehicleID in markerIDs:
            count = len(markerIDs[vehicleID])
            if count > 1:
                markerID = markerIDs[vehicleID][serverID]
                self._parent.removeMarker(markerID)
                del markerIDs[vehicleID][serverID]
            else:
                self.__removeAllVehicleMarkers(vehicleID)

    def __updateVehicleMarker(self, vehicleID, params):
        self._vehiclesCallback[vehicleID] = None
        markerIDs = self._vehiclesAreaMarker['ID']
        if vehicleID not in markerIDs:
            return
        else:
            vehicle = BigWorld.entities.get(vehicleID)
            vehiclesMatrix = self._vehiclesAreaMarker['matrix']
            markerIDs = markerIDs[vehicleID].values()
            prevDataByVehID = self._vehiclesAreaMarker['prevData'][vehicleID]
            lastCheckTime = self._vehiclesAreaMarker['lastCheckTime']
            if vehicle:
                matrix = vehicle.matrix
                if not vehiclesMatrix[vehicleID]['inAoI']:
                    vehiclesMatrix.update({vehicleID: {'matrix': matrix,
                                 'inAoI': True}})
                    for markerID in markerIDs:
                        self._parent.setMarkerMatrix(markerID, matrix)

            else:
                positionData = params['positionData']
                position = positionData['position']
                ypr = positionData['ypr']
                if vehiclesMatrix[vehicleID]['inAoI']:
                    vehiclesMatrix.update({vehicleID: {'matrix': math_utils.createRTMatrix(ypr, position),
                                 'inAoI': False}})
                    for markerID in markerIDs:
                        self._parent.setMarkerMatrix(markerID, vehiclesMatrix[vehicleID]['matrix'])

                else:
                    matrix = vehiclesMatrix[vehicleID]['matrix']
                    if (prevDataByVehID['position'] - position).length < self._TELEPORT_DISTANCE:
                        dt = BigWorld.time() - lastCheckTime[vehicleID]
                        position = matrix.translation + positionData['velocity'] * dt
                    if prevDataByVehID['position'] != ypr:
                        matrix.setRotateYPR(ypr)
                        prevDataByVehID['ypr'] = ypr
                    matrix.translation = position
                prevDataByVehID['position'] = position
                lastCheckTime[vehicleID] = BigWorld.time()
            self._vehiclesCallback[vehicleID] = BigWorld.callback(self._TICK_UPDATE, partial(self.__updateVehicleMarker, vehicleID, params))
            return

    def __updateVisibility(self, markerID, visibility):
        parent = self._parent
        if visibility:
            parent.showMarkersById(markerID)
        else:
            parent.hideMarkersById(markerID)
