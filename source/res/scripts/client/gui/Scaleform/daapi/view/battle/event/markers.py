# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/markers.py
import math
import logging
import weakref
from functools import partial
import BigWorld
import Math
from bootcamp.BootcampConstants import UI_STATE
from bootcamp.BootcampMarkers import _StaticWorldMarker2D, _IMarker, _DirectionIndicatorCtrl
from bootcamp.BootcampGUI import getDirectionIndicator
from ids_generators import SequenceIDGenerator
from constants import SERVER_TICK_LENGTH, EventMarkerBlinkingParams
from gui.shared import g_eventBus, EVENT_BUS_SCOPE, events
from gui.shared.utils.TimeInterval import TimeInterval
from gui.Scaleform.daapi.view.battle.event.marker_gui_provider import MarkerGUIProvider
from constants import MarkerTypes
_logger = logging.getLogger(__name__)
_DEATHZONES_MARKER_UPDATE_TICK_LENGTH = 0.0

class _EventDirectionIndicatorCtrl(_DirectionIndicatorCtrl):

    def __init__(self, shapes, position, offset, switchedToSniperMode=False, blinking=False, speed=EventMarkerBlinkingParams.BLINKING_SPEED_CUSTOM_MARKER_MS):
        super(_EventDirectionIndicatorCtrl, self).__init__(shapes, position + offset, switchedToSniperMode)
        self.__isBlinking = blinking
        self.__speed = speed
        self.__offset = offset

    @property
    def offset(self):
        return self.__offset

    def attachGUI(self, indicator):
        super(_EventDirectionIndicatorCtrl, self).attachGUI(indicator)
        self._indicator.setBlinking(self.__speed, self.__isBlinking)

    def setBlinking(self, speed, isShow):
        self.__isBlinking = isShow
        self.__speed = speed
        if self._indicator:
            self._indicator.setBlinking(self.__speed, self.__isBlinking)

    def setPosition(self, position):
        if self._indicator:
            self._indicator.setPosition(position + self.offset)


class _DynWorldMarker2D(_IMarker):
    _INVALID_MARKER_ID = ''

    def __init__(self, objectID, data, position, distance, switchedToSniperMode=True):
        super(_DynWorldMarker2D, self).__init__(switchedToSniperMode)
        self.__initData = data
        self.__matrix = Math.Matrix()
        self.__matrix.translation = position + self.__initData.get('offset', Math.Vector3(0, 0, 0))
        self.__objectID = objectID
        self.__distance = distance
        self.__visible = True
        self.__markers2D = lambda : None

    def attachGUI(self, markers2D):
        self.__markers2D = weakref.ref(markers2D)
        if self.__visible:
            if not self.addSetupObject(markers2D, self.__objectID, self.__distance):
                self.__markers2D = lambda : None
                self.__objectID = ''

    def detachGUI(self):
        markers2D = self.__markers2D()
        if self.__visible:
            if markers2D is not None and self.__objectID:
                markers2D.delStaticObject(self.__objectID)
        self.__markers2D = lambda : None
        return

    def addSetupObject(self, markers2D, objectID, distance):
        if markers2D.addDynObject(objectID, self.__matrix):
            markers2D.setupStaticObject(objectID, self.__initData.get('shape', 'arrow'), self.__initData.get('min-distance', 0), self.__initData.get('max-distance', 0), distance, self.__initData.get('color', 'yellow'))
            return True
        return False

    def update(self, distance):
        markers2D = self.__markers2D()
        self.__distance = distance
        if markers2D is not None and self.__objectID:
            if self.__visible:
                markers2D.setDistanceToObject(self.__objectID, distance)
        return

    def setPosition(self, position):
        self.__matrix.translation = position + self.__initData.get('offset', Math.Vector3(0, 0, 0))

    def clear(self):
        markers2D = self.__markers2D()
        if markers2D is not None and self.__objectID:
            markers2D.delStaticObject(self.__objectID)
        self.__objectID = self._INVALID_MARKER_ID
        self.__markers2D = lambda : None
        return

    def setVisible(self, isVisible):
        markers2D = self.__markers2D()
        if markers2D is not None and self.__objectID:
            if not self.__visible and isVisible:
                self.addSetupObject(markers2D, self.__objectID, self.__distance)
            elif self.__visible and not isVisible:
                markers2D.delStaticObject(self.__objectID)
        self.__visible = isVisible
        return


class EventAreaMarker(_IMarker):

    def __init__(self, triggerID, position, marker2D, dIndicator, markerType, isVisible=False, switchedToSniperMode=False):
        super(EventAreaMarker, self).__init__(switchedToSniperMode)
        self.__position = position
        self.__marker2D = marker2D
        self.__dIndicator = dIndicator
        self.__triggerID = triggerID
        self.__markerType = markerType
        self.setVisible(isVisible)

    def setInSniperMode(self, value):
        if self.__dIndicator is not None:
            self.__dIndicator.isSwitchedToSniperMode = value
        return

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

    def update(self, distance, position=None):
        if self.__marker2D is not None:
            self.__marker2D.update(distance)
        if self.__dIndicator is not None:
            self.__dIndicator.update(distance, position)
        return

    def updatePosition(self, position):
        self.__position = position
        if self.__marker2D is not None:
            self.__marker2D.setPosition(position)
        dIndicator = self.__dIndicator
        if dIndicator is not None:
            dIndicator.setPosition(position)
        return

    def setBlinking(self, speed, isShow):
        if self.__marker2D is not None:
            self.__marker2D.setBlinking(speed, isShow)
        if self.__dIndicator is not None:
            self.__dIndicator.setBlinking(speed, isShow)
        return

    @property
    def position(self):
        return self.__position

    @property
    def triggerID(self):
        return self.__triggerID

    @property
    def markerType(self):
        return self.__markerType


class MarkerFactory(object):
    _markerIdGenerator = SequenceIDGenerator()
    STYLES = {MarkerTypes.DEFAULT: {'offset': (0, 10, 0),
                           'shape': 'arrow',
                           'blindShape': 'arrow'},
     MarkerTypes.AREA_BOSS: {'offset': (0, 15, 0),
                             'shape': 'eventKill',
                             'blindShape': 'eventKill',
                             'color': 'white'},
     MarkerTypes.POINT_A: {'offset': (0, 15, 0),
                           'shape': 'CapturePointA',
                           'blindShape': 'CapturePointA'},
     MarkerTypes.POINT_B: {'offset': (0, 15, 0),
                           'shape': 'CapturePointB',
                           'blindShape': 'CapturePointB'},
     MarkerTypes.POINT_C: {'offset': (0, 15, 0),
                           'shape': 'CapturePointC',
                           'blindShape': 'CapturePointC'},
     MarkerTypes.COUNTER_ATTACK: {'offset': (0, 10, 0),
                                  'shape': 'CounterAttack',
                                  'blindShape': 'CounterAttack'},
     MarkerTypes.COUNTER_ATTACK_RED: {'offset': (0, 10, 0),
                                      'shape': 'CounterAttackRed',
                                      'blindShape': 'CounterAttackRed'},
     MarkerTypes.COUNTER_ATTACK_RECTANGLE: {'offset': (0, 10, 0),
                                            'shape': 'CounterAttackRectangle',
                                            'blindShape': 'CounterAttackRectangle'},
     MarkerTypes.CAPTURE_BASE: {'offset': (0, 10, 0),
                                'shape': 'CaptureBase',
                                'blindShape': 'CaptureBase',
                                'color': 'white'},
     MarkerTypes.OUR_BASE: {'offset': (0, 10, 0),
                            'shape': 'OurBase',
                            'blindShape': 'OurBase',
                            'color': 'white'},
     MarkerTypes.EVENT_DEATHZONE: {'offset': (0, 5, 0),
                                   'shape': 'EventDeathZone',
                                   'blindShape': 'EventDeathZone'}}
    DISAPPEARING = {MarkerTypes.POINT_A: 100.0,
     MarkerTypes.POINT_B: 100.0,
     MarkerTypes.POINT_C: 100.0,
     MarkerTypes.COUNTER_ATTACK_RED: 100.0,
     MarkerTypes.CAPTURE_BASE: 100.0,
     MarkerTypes.OUR_BASE: 100.0}

    @classmethod
    def getShape(cls, markerType):
        style = MarkerFactory.STYLES.get(markerType, {})
        shapeType = style.get('shape', 'arrow')
        blindShapeType = style.get('blindShape', 'arrow')
        return (shapeType, blindShapeType)

    @classmethod
    def createMarker(cls, position, areaRadius, markerType=MarkerTypes.DEFAULT, isVisible=False, showIndicator=True):
        markerType, markerID, shape, offset = MarkerFactory.getMarkerParams(markerType)
        indicatorCtrl = _EventDirectionIndicatorCtrl(shape, position, offset) if showIndicator else None
        marker2d = _StaticWorldMarker2D(markerID, cls.STYLES[markerType], position, areaRadius)
        return EventAreaMarker(markerID, position, marker2d, indicatorCtrl, markerType, isVisible)

    @classmethod
    def createDynMarker(cls, position, areaRadius, markerType=MarkerTypes.DEFAULT, isVisible=False, showIndicator=True):
        markerType, markerID, shape, offset = MarkerFactory.getMarkerParams(markerType)
        indicatorCtrl = _EventDirectionIndicatorCtrl(shape, position, offset) if showIndicator else None
        marker2d = _DynWorldMarker2D(markerID, cls.STYLES[markerType], position, areaRadius)
        return EventAreaMarker(markerID, position, marker2d, indicatorCtrl, markerType, isVisible)

    @classmethod
    def getMarkerParams(cls, markerType):
        if markerType not in cls.STYLES:
            markerType = MarkerTypes.DEFAULT
        return (markerType,
         cls._markerIdGenerator.next(),
         cls.getShape(markerType),
         cls.STYLES[markerType]['offset'])


class UIMarkerController(object):
    _UPDATE_TICK_LENGTH = SERVER_TICK_LENGTH

    def __init__(self):
        self._gui = None
        self._attachGUIToMarkersCallback = {}
        self._markersByObjId = {}
        self._areaRadiusByObjId = {}
        self._updateTI = None
        self._globalVisibility = True
        return

    def init(self):
        raise NotImplementedError

    def addMarker(self, objectId, marker, areaRadius):
        if objectId in self._markersByObjId:
            self.removeMarkerByObjId(objectId)
        if self._gui and self._gui.inited:
            self._attachGUIToMarkersCallback[objectId] = BigWorld.callback(0, partial(self._attachGUIToMarkers, objID=objectId))
        self._markersByObjId[objectId] = marker
        self._areaRadiusByObjId[objectId] = areaRadius

    def removeInactiveMarkers(self, activeMarkerObjIds):
        keys = self._markersByObjId.keys()
        for objId in keys:
            if objId not in activeMarkerObjIds:
                self.removeMarkerByObjId(objId)

    def removeMarkerByObjId(self, objectId):
        if objectId not in self._markersByObjId:
            return
        else:
            if objectId in self._attachGUIToMarkersCallback:
                BigWorld.cancelCallback(self._attachGUIToMarkersCallback[objectId])
                self._attachGUIToMarkersCallback.pop(objectId)
            else:
                self._markersByObjId[objectId].detachGUI()
            self._markersByObjId[objectId].clear()
            self._markersByObjId.pop(objectId, None)
            self._areaRadiusByObjId.pop(objectId, None)
            return

    def showMarkers(self):
        if not self._globalVisibility:
            return
        else:
            for marker in self._markersByObjId.values():
                marker.setVisible(True)

            if self._updateTI is not None:
                self._updateTI.start()
            return

    def hideMarkers(self):
        for marker in self._markersByObjId.values():
            marker.setVisible(False)

        if self._updateTI is not None:
            self._updateTI.stop()
        return

    def showMarkersByObjId(self, objectId):
        if not self._globalVisibility:
            return
        if objectId in self._markersByObjId.keys():
            self._markersByObjId[objectId].setVisible(True)

    def hideMarkersByObjId(self, objectId):
        if objectId in self._markersByObjId.keys():
            self._markersByObjId[objectId].setVisible(False)

    def blinkingByObjId(self, objectId, speed=EventMarkerBlinkingParams.BLINKING_SPEED_CUSTOM_MARKER_MS, show=True):
        if objectId in self._markersByObjId.keys():
            self._markersByObjId[objectId].setBlinking(speed, show)

    def updateMarkersPositionByObjId(self, objectId, position):
        if objectId in self._markersByObjId.keys():
            self._markersByObjId[objectId].updatePosition(position)

    def _start(self):
        if self._gui and self._gui.inited:
            if self._updateTI:
                self._updateTI.stop()
            for objID in self._markersByObjId.iterkeys():
                if objID not in self._attachGUIToMarkersCallback:
                    self._attachGUIToMarkersCallback[objID] = BigWorld.callback(0.0, partial(self._attachGUIToMarkers, objID=objID))

            self._updateTI = TimeInterval(self._UPDATE_TICK_LENGTH, self, '_tickUpdate')

    def _stop(self):
        if self._updateTI is not None:
            self._updateTI.stop()
            self._updateTI = None
        self._clear()
        return

    def _tickUpdate(self):
        raise NotImplementedError

    def _onUIStateChanged(self, event):
        state = event.ctx['state']
        if state == UI_STATE.START:
            self._start()
        elif state == UI_STATE.STOP:
            self._stop()

    def _clear(self):
        raise NotImplementedError

    def _attachGUIToMarkers(self, objID):
        self._attachGUIToMarkersCallback[objID] = None
        self._attachGUIToMarkersCallback.pop(objID)
        if self._gui and self._gui.inited:
            if objID in self._markersByObjId:
                self._markersByObjId[objID].attachGUI(self._gui.getMarkers2DPlugin())
        else:
            self._attachGUIToMarkersCallback[objID] = BigWorld.callback(0, partial(self._attachGUIToMarkers, objID))
        return

    def _handleGUIVisibility(self, event):
        self._globalVisibility = event.ctx['visible']
        if self._globalVisibility:
            self.showMarkers()
        else:
            self.hideMarkers()


class EventAreaPointUIMarkerController(UIMarkerController):

    def init(self):
        _logger.debug('EventAreaPointUIMarkerController.init')
        self._gui = MarkerGUIProvider(events.GameEvent.AREA_POINT_MARKER_CHANGED, events.GameEvent.AREA_POINT_MARKER_LIFETIME)
        g_eventBus.addListener(events.GameEvent.AREA_POINT_MARKER_CHANGED, self._onUIStateChanged, scope=EVENT_BUS_SCOPE.BATTLE)
        g_eventBus.addListener(events.GameEvent.GUI_VISIBILITY, self._handleGUIVisibility, scope=EVENT_BUS_SCOPE.BATTLE)
        player = BigWorld.player()
        if player is not None and player.inputHandler is not None:
            player.inputHandler.onCameraChanged += self.__onCameraChanged
        return

    def __onCameraChanged(self, cameraName, currentVehicleId=None):
        for marker in self._markersByObjId.itervalues():
            marker.setInSniperMode(bool(cameraName == 'sniper'))

    def _start(self):
        super(EventAreaPointUIMarkerController, self)._start()
        if self._updateTI:
            self._updateTI.start()

    def _tickUpdate(self):
        player = BigWorld.player()
        if player is None:
            return
        else:
            disappearing = MarkerFactory.DISAPPEARING
            for objId, marker in self._markersByObjId.iteritems():
                distanceToArea = self._getDistanceToArea(marker, objId, player)
                conditionDistance = disappearing.get(marker.markerType, 0.0)
                if conditionDistance > distanceToArea:
                    marker.setVisible(False)
                    continue
                marker.setVisible(True)
                if distanceToArea >= 0:
                    marker.update(int(math.ceil(distanceToArea)))

            return

    def _clear(self):
        g_eventBus.removeListener(events.GameEvent.AREA_POINT_MARKER_CHANGED, self._onUIStateChanged, scope=EVENT_BUS_SCOPE.BATTLE)
        g_eventBus.removeListener(events.GameEvent.GUI_VISIBILITY, self._handleGUIVisibility, scope=EVENT_BUS_SCOPE.BATTLE)
        player = BigWorld.player()
        if player is not None and player.inputHandler is not None:
            player.inputHandler.onCameraChanged -= self.__onCameraChanged
        self.removeInactiveMarkers([])
        self._gui = None
        return

    def showMarkers(self):
        if not self._globalVisibility:
            return
        else:
            player = BigWorld.player()
            disappearing = MarkerFactory.DISAPPEARING
            for objId, marker in self._markersByObjId.iteritems():
                conditionDistance = disappearing.get(marker.markerType, 0.0)
                if conditionDistance > 0:
                    distanceToArea = self._getDistanceToArea(marker, objId, player)
                    if conditionDistance > distanceToArea:
                        continue
                marker.setVisible(True)

            if self._updateTI is not None:
                self._updateTI.start()
            return

    def _getDistanceToArea(self, marker, objId, player):
        absDistance = (marker.position - player.getOwnVehiclePosition()).length
        distanceToArea = max(0, absDistance - self._areaRadiusByObjId[objId])
        return distanceToArea


class EventDeathZonesUIMarkerController(UIMarkerController):
    _UPDATE_TICK_LENGTH = _DEATHZONES_MARKER_UPDATE_TICK_LENGTH

    def __init__(self):
        super(EventDeathZonesUIMarkerController, self).__init__()
        self._zones = {}

    def init(self):
        self._gui = MarkerGUIProvider(events.GameEvent.EVENT_DEATHZONE_MARKER_CHANGED, events.GameEvent.EVENT_DEATHZONE_MARKER_LIFETIME)
        g_eventBus.addListener(events.GameEvent.EVENT_DEATHZONE_MARKER_CHANGED, self._onUIStateChanged, scope=EVENT_BUS_SCOPE.BATTLE)
        g_eventBus.addListener(events.GameEvent.GUI_VISIBILITY, self._handleGUIVisibility, scope=EVENT_BUS_SCOPE.BATTLE)

    def registerZone(self, zone):
        self._zones[zone.zoneId] = weakref.ref(zone)

    def _start(self):
        super(EventDeathZonesUIMarkerController, self)._start()
        if self._updateTI:
            self._updateTI.start()

    def _clear(self):
        g_eventBus.removeListener(events.GameEvent.EVENT_DEATHZONE_MARKER_CHANGED, self._onUIStateChanged, scope=EVENT_BUS_SCOPE.BATTLE)
        g_eventBus.removeListener(events.GameEvent.GUI_VISIBILITY, self._handleGUIVisibility, scope=EVENT_BUS_SCOPE.BATTLE)
        self.removeInactiveMarkers([])
        self._gui = None
        self._zones.clear()
        return

    def _tickUpdate(self):
        player = BigWorld.player()
        if player is None:
            return
        else:
            for zoneId, marker in self._markersByObjId.iteritems():
                playerPosition = player.getOwnVehiclePosition()
                zone = self._zones[zoneId]()
                if zone is None:
                    self.hideMarkersByObjId(zoneId)
                    continue
                closestPointOnDeathZone = zone.getClosestPoint(playerPosition)
                distanceSquared = (closestPointOnDeathZone - playerPosition).lengthSquared
                vehicle = player.vehicle
                isAlive = vehicle.isAlive() if vehicle is not None else False
                if distanceSquared < self._areaRadiusByObjId[zoneId] ** 2 and not zone.isPlayerInDeathZone and isAlive:
                    self.showMarkersByObjId(zoneId)
                    marker.updatePosition(closestPointOnDeathZone)
                    marker.update(int(math.ceil(math.sqrt(distanceSquared))), closestPointOnDeathZone)
                self.hideMarkersByObjId(zoneId)

            return
