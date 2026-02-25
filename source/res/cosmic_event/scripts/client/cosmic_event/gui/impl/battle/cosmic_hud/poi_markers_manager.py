# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: cosmic_event/scripts/client/cosmic_event/gui/impl/battle/cosmic_hud/poi_markers_manager.py
import functools
import logging
import typing
import BigWorld
from helpers import time_utils
from shared_utils import safeCancelCallback
from cosmic_event.gui.impl.gen.view_models.views.battle.cosmic_hud.direction_marker_model import DirectionMarkerModel
if typing.TYPE_CHECKING:
    from frameworks.wulf import Array
_logger = logging.getLogger(__name__)

class CosmicPOIMarkersManager(object):

    def __init__(self, markersArray, markersCtrl):
        self._markers = markersArray
        self._markersCtrl = markersCtrl
        self.__markerTimers = {}
        self.__markerIdToArrayID = {}

    def stop(self):
        for markerID in self.__markerIdToArrayID.keys():
            self.destroyMarker(markerID)

    def createMarker(self, matrix, markerType, markerID):
        if markerID in self.__markerIdToArrayID:
            return
        markerModel = DirectionMarkerModel()
        markerModel.setMarkerType(markerType)
        markerModel.setMarkerVisibility(True)
        self._markers.addViewModel(markerModel)
        self._markersCtrl.add(markerModel.proxy, matrix)
        arrID = len(self._markers) - 1
        self.__markerIdToArrayID[markerID] = arrID

    def destroyMarker(self, markerID):
        arrID = self.__markerIdToArrayID.get(markerID, -1)
        if arrID == -1:
            return
        else:
            markerModel = self._markers.getValue(arrID)
            if not markerModel:
                _logger.error('Marker with id %s not found!', markerID)
                return
            timerID = self.__markerTimers.pop(markerID, None)
            if timerID is not None:
                safeCancelCallback(timerID)
            self._markers.remove(arrID)
            self._markersCtrl.remove(markerModel.proxy)
            self.__markerIdToArrayID.pop(markerID)
            for keyID, arrayID in self.__markerIdToArrayID.iteritems():
                if arrayID > arrID:
                    self.__markerIdToArrayID[keyID] = arrayID - 1

            return

    def isMarkerVisible(self, markerID):
        arrID = self.__markerIdToArrayID.get(markerID, -1)
        if arrID == -1:
            _logger.error('Marker with id %s not found!', markerID)
            return
        markerModel = self._markers.getValue(arrID)
        return markerModel.getMarkerVisibility()

    def setMarkerVisibility(self, markerID, visibility):
        arrID = self.__markerIdToArrayID.get(markerID, -1)
        if arrID == -1:
            _logger.error('Marker with id %s not found!', markerID)
            return
        markerModel = self._markers.getValue(arrID)
        markerModel.setMarkerVisibility(visibility)

    def setMarkerTimer(self, markerID, timeLeft):
        arrID = self.__markerIdToArrayID.get(markerID, -1)
        if arrID == -1:
            _logger.error('Marker with id %s not found!', markerID)
            return
        else:
            markerModel = self._markers.getValue(arrID)
            timerID = self.__markerTimers.pop(markerID, None)
            if timerID is not None:
                _logger.info('Timer for markerID %s already exists! Replacing by new one', markerID)
                safeCancelCallback(timerID)
            markerModel.setMarkerTimer(timeLeft)
            timerID = BigWorld.callback(time_utils.ONE_SECOND, functools.partial(self.__onTimerTick, markerID, markerModel, timeLeft))
            self.__markerTimers[markerID] = timerID
            return

    def __onTimerTick(self, markerID, markerModel, timeLeft):
        timerID = self.__markerTimers.pop(markerID, None)
        if timerID is None:
            _logger.error('Timer for markerID %s not found! but onTimerTick has called', markerID)
            return
        else:
            timeLeft -= 1
            if timeLeft <= 0:
                return
            markerModel.setMarkerTimer(timeLeft)
            timerID = BigWorld.callback(time_utils.ONE_SECOND, functools.partial(self.__onTimerTick, markerID, markerModel, timeLeft))
            self.__markerTimers[markerID] = timerID
            return
