# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/markers.py
import math
import logging
import sys
from functools import partial
import BigWorld
import Math
from bootcamp.BootcampConstants import UI_STATE
from bootcamp.BootcampMarkers import _DirectionIndicatorCtrl, _StaticWorldMarker2D, _IMarker
from ids_generators import SequenceIDGenerator
from constants import SERVER_TICK_LENGTH
from gui.shared import g_eventBus, EVENT_BUS_SCOPE, events
from gui.shared.utils.TimeInterval import TimeInterval
from gui.Scaleform.daapi.view.battle.event.ui import LootSignUI
from bootcamp.BootcampGUI import getDirectionIndicator
_logger = logging.getLogger(__name__)

class EventAreaMarker(_IMarker):

    def __init__(self, triggerID, position, marker2D, dIndicator):
        self.__position = position
        self.__marker2D = marker2D
        self.__dIndicator = dIndicator
        self.__triggerID = triggerID

    def attachGUI(self, markers2D):
        if self.__marker2D is not None:
            self.__marker2D.attachGUI(markers2D)
        if self.__dIndicator is not None:
            indicator = getDirectionIndicator()
            if indicator is not None:
                self.__dIndicator.attachGUI(indicator)
        return

    def detachGUI(self):
        if self.__marker2D is not None:
            self.__marker2D.detachGUI()
        if self.__dIndicator is not None:
            self.__dIndicator.detachGUI()
        return

    def clear(self):
        if self.__marker2D is not None:
            self.__marker2D.clear()
        self.__marker2D = None
        if self.__dIndicator is not None:
            self.__dIndicator.clear()
        self.__dIndicator = None
        return

    def setVisible(self, isVisible):
        if self.__marker2D is not None:
            self.__marker2D.setVisible(isVisible)
        if self.__dIndicator is not None:
            self.__dIndicator.setVisible(isVisible)
        return

    def update(self, distance):
        if self.__marker2D is not None:
            self.__marker2D.update(distance)
        if self.__dIndicator is not None:
            self.__dIndicator.update(distance)
        return

    @property
    def position(self):
        return self.__position

    @property
    def triggerID(self):
        return self.__triggerID


class LootSignTypes(object):
    AMMO = 'ammo'


class LootSignFactory(object):
    _markerIdGenerator = SequenceIDGenerator()
    STYLES = {LootSignTypes.AMMO: {'offset': Math.Vector3(0, 10, 0),
                          'shape': 'eventAmmo'}}

    @classmethod
    def createMarker(cls, position, areaRadius, signType=LootSignTypes.AMMO):
        markerID = cls._markerIdGenerator.next()
        indicatorCtrl = _DirectionIndicatorCtrl(('eventAmmo', 'eventAmmo'), position + cls.STYLES[signType]['offset'])
        marker2d = _StaticWorldMarker2D(markerID, cls.STYLES[signType], position, areaRadius)
        return EventAreaMarker(markerID, position, marker2d, indicatorCtrl)


class UIMarkerController(object):
    __UPDATE_TICK_LENGTH = SERVER_TICK_LENGTH

    def __init__(self):
        self.__gui = None
        self.__attachGUIToMarkersCallback = {}
        self.__markersByObjId = {}
        self.__areaRadiusByObjId = {}
        self.__updateTI = None
        self.__globalVisibility = True
        return

    def init(self):
        _logger.debug('UIMarkerController.init')
        self.__gui = LootSignUI()
        g_eventBus.addListener(events.GameEvent.LOOTSIGN_STATE_CHANGED, self._onUIStateChanged, scope=EVENT_BUS_SCOPE.BATTLE)
        g_eventBus.addListener(events.GameEvent.GUI_VISIBILITY, self.__handleGUIVisibility, scope=EVENT_BUS_SCOPE.BATTLE)

    def putMarker(self, objectId, marker, areaRadius):
        if objectId in self.__markersByObjId:
            self.removeMarkerByObjId(objectId)
        if self.__gui and self.__gui.inited:
            self.__attachGUIToMarkersCallback[objectId] = BigWorld.callback(0, partial(self.__attachGUIToMarkers, objID=objectId))
        marker.setVisible(False)
        self.__markersByObjId[objectId] = marker
        self.__areaRadiusByObjId[objectId] = areaRadius

    def removeInactiveMarkers(self, activeMarkerObjIds):
        keys = self.__markersByObjId.keys()
        for objId in keys:
            if objId not in activeMarkerObjIds:
                self.removeMarkerByObjId(objId)

    def removeMarkerByObjId(self, objectId):
        if objectId not in self.__markersByObjId:
            return
        else:
            if objectId in self.__attachGUIToMarkersCallback:
                BigWorld.cancelCallback(self.__attachGUIToMarkersCallback[objectId])
                self.__attachGUIToMarkersCallback.pop(objectId)
            else:
                self.__markersByObjId[objectId].detachGUI()
            self.__markersByObjId[objectId].clear()
            self.__markersByObjId.pop(objectId, None)
            self.__areaRadiusByObjId.pop(objectId, None)
            return

    def showMarkers(self):
        if not self.__globalVisibility:
            return
        else:
            if self.__updateTI is not None:
                self.__updateTI.start()
            return

    def hideMarkers(self):
        for marker in self.__markersByObjId.values():
            marker.setVisible(False)

        if self.__updateTI is not None:
            self.__updateTI.stop()
        return

    def _start(self):
        if self.__gui and self.__gui.inited:
            if self.__updateTI:
                self.__updateTI.stop()
            for objID in self.__markersByObjId.iterkeys():
                if objID not in self.__attachGUIToMarkersCallback:
                    self.__attachGUIToMarkersCallback[objID] = BigWorld.callback(0.0, partial(self.__attachGUIToMarkers, objID=objID))

            self.__updateTI = TimeInterval(self.__UPDATE_TICK_LENGTH, self, '_tickUpdate')

    def _stop(self):
        if self.__updateTI is not None:
            self.__updateTI.stop()
            self.__updateTI = None
        self._clear()
        return

    def _tickUpdate(self):
        if not self.__markersByObjId:
            return
        else:
            minDistanceToPlayer = sys.maxint
            closestMarker = None
            for objId, marker in self.__markersByObjId.iteritems():
                absDistance = (marker.position - BigWorld.player().getOwnVehiclePosition()).length
                distanceToArea = max(0, absDistance - self.__areaRadiusByObjId[objId])
                if distanceToArea > 0:
                    marker.update(int(math.ceil(distanceToArea)))
                if distanceToArea < minDistanceToPlayer:
                    closestMarker = objId
                    minDistanceToPlayer = distanceToArea

            if closestMarker is not None:
                for objId, marker in self.__markersByObjId.iteritems():
                    marker.setVisible(bool(minDistanceToPlayer > 0 and self.__globalVisibility and objId == closestMarker))

            return

    def _onUIStateChanged(self, event):
        state = event.ctx['state']
        if state == UI_STATE.START:
            self._start()
        elif state == UI_STATE.STOP:
            self._stop()

    def _clear(self):
        g_eventBus.removeListener(events.GameEvent.LOOTSIGN_STATE_CHANGED, self._onUIStateChanged, scope=EVENT_BUS_SCOPE.BATTLE)
        g_eventBus.removeListener(events.GameEvent.GUI_VISIBILITY, self.__handleGUIVisibility, scope=EVENT_BUS_SCOPE.BATTLE)
        self.removeInactiveMarkers([])
        self.__gui = None
        return

    def __attachGUIToMarkers(self, objID):
        self.__attachGUIToMarkersCallback[objID] = None
        self.__attachGUIToMarkersCallback.pop(objID)
        if self.__gui and self.__gui.inited:
            if objID in self.__markersByObjId:
                self.__markersByObjId[objID].attachGUI(self.__gui.getMarkers2DPlugin())
        else:
            self.__attachGUIToMarkersCallback[objID] = BigWorld.callback(0, partial(self.__attachGUIToMarkers, objID))
        return

    def __handleGUIVisibility(self, event):
        self.__globalVisibility = event.ctx['visible']
        if self.__globalVisibility:
            self.showMarkers()
        else:
            self.hideMarkers()
