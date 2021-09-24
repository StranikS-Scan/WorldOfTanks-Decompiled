# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/component_marker/markers_controller.py
import logging
from functools import partial
import BigWorld
import Event
from gui.battle_control.arena_info.interfaces import IArenaVehiclesController
from gui.shared import g_eventBus, EVENT_BUS_SCOPE, events
from gui.shared.utils.TimeInterval import TimeInterval
from gui.Scaleform.daapi.view.battle.shared.component_marker.markers_gui_provider import MarkerGUIProvider
from gui.Scaleform.daapi.view.battle.shared.component_marker.markers import AreaMarker
from gui.shared.gui_items.marker_items import MarkerParamsFactory
_logger = logging.getLogger(__name__)

class BaseMarkerController(IArenaVehiclesController):
    _UPDATE_TICK_LENGTH = 0.0

    def __init__(self):
        super(BaseMarkerController, self).__init__()
        self.onTickUpdate = Event.Event()
        self._gui = None
        self._attachGUIToMarkersCallback = {}
        self._markers = {}
        self._updateTI = None
        self._globalVisibility = True
        return

    def init(self):
        _logger.debug('BaseMarkerController.init')
        self._gui = MarkerGUIProvider(self.getPluginID())
        g_eventBus.addListener(events.GameEvent.GUI_VISIBILITY, self._handleGUIVisibility, scope=EVENT_BUS_SCOPE.BATTLE)

    @property
    def allMarkers(self):
        return self._markers.values()

    @property
    def allMarkersID(self):
        return self._markers.keys()

    def getPluginID(self):
        raise NotImplementedError

    def createMarker(self, matrix, markerType, clazz=AreaMarker, bitMask=0):
        markerData = MarkerParamsFactory.getMarkerParams(matrix, markerType, bitMask)
        return clazz(markerData)

    def addMarker(self, marker):
        markerID = marker.markerID
        if markerID in self._markers:
            _logger.error('Marker with Id=%s exists already', markerID)
            marker.clear()
            return None
        else:
            self._attachGUIToMarkersCallback[markerID] = BigWorld.callback(0, partial(self._attachGUIToMarkers, markerID))
            self._checkGlobalVisibilityForMarker(marker)
            self._markers[markerID] = marker
            self.checkStartTimer()
            return markerID

    def setMarkerMatrix(self, markerID, matrix):
        marker = self._markers.get(markerID, None)
        if marker:
            marker.setMatrix(matrix)
        return

    def removeMarker(self, markerID):
        if markerID not in self._markers:
            return
        else:
            if markerID in self._attachGUIToMarkersCallback:
                BigWorld.cancelCallback(self._attachGUIToMarkersCallback[markerID])
                self._attachGUIToMarkersCallback.pop(markerID)
            else:
                self._markers[markerID].detachGUI()
            self._markers[markerID].clear()
            self._markers.pop(markerID, None)
            return

    def removeAllMarkers(self):
        for markerID in self._markers:
            if markerID in self._attachGUIToMarkersCallback:
                BigWorld.cancelCallback(self._attachGUIToMarkersCallback[markerID])
                self._attachGUIToMarkersCallback.pop(markerID)
            else:
                self._markers[markerID].detachGUI()
            self._markers[markerID].clear()

        self._markers.clear()

    def showMarkers(self, unblock=True):
        if not self._globalVisibility:
            return
        for markerID in self._markers.iterkeys():
            self.showMarkersById(markerID, unblock)

        self.checkStartTimer()

    def hideMarkers(self, block=True):
        for marker in self._markers.values():
            marker.setVisible(False)
            if block:
                marker.blockChangVisibility = True

        if self._updateTI is not None:
            self._updateTI.stop()
        return

    def showMarkersById(self, markerID, unblock=True):
        player = BigWorld.player()
        marker = self._markers.get(markerID, None)
        if marker:
            if unblock:
                marker.blockChangVisibility = False
            if not self._globalVisibility:
                return
            if marker.isEmpty():
                return
            conditionDistance = marker.disappearingRadius
            if conditionDistance > 0:
                distanceToArea = BaseMarkerController.getDistanceToArea(marker, player)
                hide = conditionDistance < distanceToArea if marker.reverseDisappearing else conditionDistance > distanceToArea
                if hide:
                    marker.setVisible(False)
                    return
            marker.setVisible(True)
        self.checkStartTimer()
        return

    def hideMarkersById(self, markerID, block=True):
        if markerID in self._markers.keys():
            marker = self._markers[markerID]
            marker.setVisible(False)
            if block:
                marker.blockChangVisibility = True

    def getMarkerById(self, markerID):
        return self._markers.get(markerID)

    @staticmethod
    def getDistanceToArea(marker, player):
        absDistance = (marker.getMarkerPosition() - player.getOwnVehiclePosition()).length
        distanceToArea = max(0, absDistance - marker.areaRadius)
        return distanceToArea

    def start(self):
        if self._gui is None:
            return
        else:
            if self._updateTI:
                self._updateTI.stop()
            for markerID in self._markers.iterkeys():
                if markerID not in self._attachGUIToMarkersCallback:
                    self._attachGUIToMarkersCallback[markerID] = BigWorld.callback(0.0, partial(self._attachGUIToMarkers, markerID=markerID))

            self._updateTI = TimeInterval(self._UPDATE_TICK_LENGTH, self, '_tickUpdate')
            self._updateTI.start()
            return

    def checkStartTimer(self):
        if self._markers and self._updateTI and not self._updateTI.isStarted():
            self.start()

    def stop(self):
        if self._updateTI is not None:
            self._updateTI.stop()
            self._updateTI = None
        self._clear()
        return

    def checkStopTimer(self):
        if not self._markers and self._updateTI and self._updateTI.isStarted():
            self._updateTI.stop()

    def _tickUpdate(self):
        self.onTickUpdate()
        self.checkStopTimer()

    def _clear(self):
        g_eventBus.removeListener(events.GameEvent.GUI_VISIBILITY, self._handleGUIVisibility, scope=EVENT_BUS_SCOPE.BATTLE)
        self.removeAllMarkers()
        if self._gui is not None:
            self._gui.clear()
        self._gui = None
        return

    def _attachGUIToMarkers(self, markerID):
        self._attachGUIToMarkersCallback[markerID] = None
        if self._gui and markerID in self._markers:
            marker = self._markers[markerID]
            if self._checkInitedPlugin(marker):
                self._attachGUIToMarkersCallback.pop(markerID)
                self._markers[markerID].attachGUI(self._gui)
                return
        self._attachGUIToMarkersCallback[markerID] = BigWorld.callback(0, partial(self._attachGUIToMarkers, markerID))
        return

    def _handleGUIVisibility(self, event):
        self._globalVisibility = event.ctx['visible']
        if self._globalVisibility:
            self.showMarkers(unblock=False)
        else:
            self.hideMarkers(block=False)

    def _checkInitedPlugin(self, marker):
        if marker.hasMarker2D() and self._gui.getMarkers2DPlugin() is None:
            return False
        else:
            return False if marker.hasMinimap() and self._gui.getMinimapPlugin() is None else True

    def _checkGlobalVisibilityForMarker(self, marker):
        if not self._globalVisibility:
            marker.setVisible(False)
