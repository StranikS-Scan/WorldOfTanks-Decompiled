# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/event_mode/markers.py
import logging
import math
from functools import partial
import BattleReplay
import BigWorld
import TriggersManager
from bootcamp.BootcampConstants import UI_STATE
from bootcamp.BootcampMarkers import _DirectionIndicatorCtrl, _AreaMarker, _StaticWorldMarker2D
from constants import SERVER_TICK_LENGTH, HALLOWEEN_STATE
from event_mode.event_ui import EventUI
from event_mode.events import g_eventModeEvents
from gui.shared import g_eventBus, EVENT_BUS_SCOPE, events
from event_mode.context import Chapter as EventChapter
from gui.shared.utils.TimeInterval import TimeInterval
from helpers import dependency
from ids_generators import SequenceIDGenerator
from shared_utils import CONST_CONTAINER
from skeletons.gui.battle_session import IBattleSessionProvider
_logger = logging.getLogger(__name__)

class ObjectiveTypes(CONST_CONTAINER):
    BASE = 'BaseMarker'
    CHEST = 'ChestMarker'


class EventObjectMarkerFactory(object):
    _markerIdGenerator = SequenceIDGenerator()

    @classmethod
    def createMarker(cls, objType, position, areaRadius, styleCollection=None, styleName=None):
        style = cls._getMarkerStyle(objType, styleCollection, styleName)
        typeID = 1
        markerID = cls._markerIdGenerator.next()
        indicatorCtrl = None
        if style.isIndicatorCreate():
            color = cls._getMarkerShapeName(objType)
            indicatorCtrl = _DirectionIndicatorCtrl((color, color), position)
        return _AreaMarker(typeID, markerID, position, _StaticWorldMarker2D(markerID, style.getWorldData(), position, areaRadius), None, None, None, indicatorCtrl)

    @classmethod
    def _getMarkerStyle(cls, objType, styleCollection, styleName):
        if styleCollection is not None and styleName is not None:
            return styleCollection.getEntity(styleName)
        elif objType == ObjectiveTypes.BASE:
            return EventChapter().getEntity('MoveToBase')
        else:
            return EventChapter().getEntity('MoveToObjective') if objType == ObjectiveTypes.CHEST else None

    @classmethod
    def _getMarkerShapeName(cls, objType):
        if objType is ObjectiveTypes.BASE:
            return 'base'
        return 'quest' if objType is ObjectiveTypes.CHEST else 'green'


class UIMarkerController(object):
    __UPDATE_TICK_LENGTH = SERVER_TICK_LENGTH

    def __init__(self):
        self.__nextMarkerId = 1
        self.__markerVisibilityState = {}
        self.__gui = None
        self.__attachGUIToMarkersCallback = {}
        self.__markersByObjId = {}
        self.__areaRadiusByObjId = {}
        self.__updateTI = None
        self.__isInSniperMode = False
        self.__globalVisibility = True
        self.__markerVisibility = True
        return

    def init(self):
        _logger.debug('UIMarkerController.init')
        self.__gui = EventUI()
        if not BattleReplay.g_replayCtrl.isPlaying:
            TriggersManager.g_manager.addListener(self)
        g_eventModeEvents.onUIStateChanged += self._onUIStateChanged
        g_eventBus.addListener(events.GameEvent.GUI_VISIBILITY, self.__handleGUIVisibility, scope=EVENT_BUS_SCOPE.BATTLE)

    def putMarker(self, objectId, marker, areaRadius):
        if objectId in self.__markersByObjId:
            self.removeMarkerByObjId(objectId)
        if self.__gui and self.__gui.inited:
            self.__attachGUIToMarkersCallback[objectId] = BigWorld.callback(0, partial(self.__attachGUIToMarkers, objID=objectId))
        marker.setVisible(self.canMarkersBeShown())
        self.__markersByObjId[objectId] = marker
        self.__areaRadiusByObjId[objectId] = areaRadius

    def removeInactiveMarkers(self, activeMarkerObjIds):
        keys = self.__markersByObjId.keys()
        for objId in keys:
            if objId not in activeMarkerObjIds:
                self.removeMarkerByObjId(objId)

    def removeMarkerByObjId(self, objectId):
        if objectId in self.__attachGUIToMarkersCallback:
            BigWorld.cancelCallback(self.__attachGUIToMarkersCallback[objectId])
            self.__attachGUIToMarkersCallback.pop(objectId)
        else:
            self.__markersByObjId[objectId].detachGUI()
        self.__markersByObjId[objectId].clear()
        self.__markersByObjId.pop(objectId, None)
        self.__areaRadiusByObjId.pop(objectId, None)
        return

    def setVisible(self, visible):
        self.__markerVisibility = visible
        if visible:
            self.showMarkers()
        else:
            self.hideMarkers()

    def showMarkers(self):
        if not self.canMarkersBeShown():
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

    def canMarkersBeShown(self):
        return not self.__isInSniperMode and self.__globalVisibility and self.__markerVisibility

    def onTriggerActivated(self, params):
        if params['type'] == TriggersManager.TRIGGER_TYPE.SNIPER_MODE:
            self.__isInSniperMode = True
            self.hideMarkers()

    def onTriggerDeactivated(self, params):
        if params['type'] == TriggersManager.TRIGGER_TYPE.SNIPER_MODE:
            self.__isInSniperMode = False
            self.showMarkers()

    def _start(self):
        if self.__gui and self.__gui.inited:
            if self.__updateTI:
                self.__updateTI.stop()
            for objID in self.__markersByObjId.iterkeys():
                if objID not in self.__attachGUIToMarkersCallback:
                    self.__attachGUIToMarkersCallback[objID] = BigWorld.callback(0.0, partial(self.__attachGUIToMarkers, objID=objID))

            self.__updateTI = TimeInterval(self.__UPDATE_TICK_LENGTH, self, '_tickUpdate')
            if self.canMarkersBeShown():
                self.__updateTI.start()

    def _stop(self):
        if self.__updateTI is not None:
            self.__updateTI.stop()
            self.__updateTI = None
        self._clear()
        return

    def _tickUpdate(self):
        if not self.__markersByObjId:
            return
        for objId, marker in self.__markersByObjId.iteritems():
            absDistance = (marker.position - BigWorld.player().getOwnVehiclePosition()).length
            distanceToArea = max(0, absDistance - self.__areaRadiusByObjId[objId])
            if distanceToArea > 0:
                marker.update(int(math.ceil(distanceToArea)))
            marker.setVisible(bool(distanceToArea > 0 and not self.__isInSniperMode))

    def _onUIStateChanged(self, state):
        if state == UI_STATE.START:
            self._start()
        elif state == UI_STATE.STOP:
            self._stop()

    def _clear(self):
        g_eventModeEvents.onUIStateChanged -= self._onUIStateChanged
        g_eventBus.removeListener(events.GameEvent.GUI_VISIBILITY, self.__handleGUIVisibility, scope=EVENT_BUS_SCOPE.BATTLE)
        if not BattleReplay.g_replayCtrl.isPlaying:
            TriggersManager.g_manager.delListener(self)
        self.removeInactiveMarkers([])
        self.__gui = None
        return

    def __attachGUIToMarkers(self, objID):
        self.__attachGUIToMarkersCallback[objID] = None
        self.__attachGUIToMarkersCallback.pop(objID)
        if self.__gui and self.__gui.inited:
            if objID in self.__markersByObjId:
                self.__markersByObjId[objID].attachGUI(self.__gui.getMarkers2DPlugin(), None)
        else:
            self.__attachGUIToMarkersCallback[objID] = BigWorld.callback(0, partial(self.__attachGUIToMarkers, objID))
        return

    def __handleGUIVisibility(self, event):
        self.__globalVisibility = event.ctx['visible']
        if self.__globalVisibility:
            self.showMarkers()
        else:
            self.hideMarkers()


class EventMarkersManager(object):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)
    _markerFactory = EventObjectMarkerFactory
    _OBJECTIVE_AREA_RADIUS = 1
    _BASE_ID = 'base'

    def __init__(self):
        self.__uiMarkerController = None
        return

    def init(self, uiMarkerController):
        _logger.debug('EventMarkersManager.init')
        player = BigWorld.player()
        self.__uiMarkerController = uiMarkerController
        randomEventComponent = self._getRandomEventComponent()
        if randomEventComponent:
            randomEventComponent.onScenarioUpdated += self.onScenarioUpdated
        eventPointsBaseComponent = player.arena.componentSystem.eventPointsBaseComponent
        if eventPointsBaseComponent and eventPointsBaseComponent.isInitialized():
            basePosition = eventPointsBaseComponent.position
            baseRadius = eventPointsBaseComponent.radius
            baseMarker = self._markerFactory.createMarker(ObjectiveTypes.BASE, basePosition, areaRadius=baseRadius)
            self.__uiMarkerController.putMarker(self._BASE_ID, baseMarker, baseRadius)
        self.onScenarioUpdated()

    def fini(self):
        randomEventComponent = self._getRandomEventComponent()
        if randomEventComponent:
            randomEventComponent.onScenarioUpdated -= self.onScenarioUpdated

    def onScenarioUpdated(self):
        objectives = self._getObjectivesToView()
        activeMarkerObjIds = {self._BASE_ID}
        for objective in objectives:
            marker = self._markerFactory.createMarker(ObjectiveTypes.CHEST, objective.getPosition(), self._OBJECTIVE_AREA_RADIUS)
            activeMarkerObjIds.add(objective.getId())
            self.__uiMarkerController.putMarker(objective.getId(), marker, self._OBJECTIVE_AREA_RADIUS)

        self.__uiMarkerController.removeInactiveMarkers(activeMarkerObjIds)

    def _getRandomEventComponent(self):
        componentSystem = self.sessionProvider.arenaVisitor.getComponentSystem()
        return getattr(componentSystem, 'randomEventComponent', None)

    def _getObjectivesToView(self):
        randomEventComponent = self._getRandomEventComponent()
        if randomEventComponent:
            scenario = randomEventComponent.getScenario()
            if scenario:
                return [ t for t in scenario.getObjectives() if t.getState() == HALLOWEEN_STATE.ACTIVE and t.getPosition() is not None ]
        return []
