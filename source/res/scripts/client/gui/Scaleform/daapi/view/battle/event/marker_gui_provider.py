# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/marker_gui_provider.py
from bootcamp.BootcampConstants import UI_STATE
from bootcamp.BootcampGUI import BootcampStaticObjectsPlugin
from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES
from gui.shared import g_eventBus, EVENT_BUS_SCOPE, events

class EventMarkerPlugin(BootcampStaticObjectsPlugin):

    def start(self):
        self._uiComponentLifeTimeEvent(BATTLE_VIEW_ALIASES.MARKERS_2D, self)

    def stop(self):
        self._uiComponentLifeTimeEvent(BATTLE_VIEW_ALIASES.MARKERS_2D, None)
        return

    def _uiComponentLifeTimeEvent(self, alias, component):
        raise NotImplementedError


class EventAreaPointMarkerPlugin(EventMarkerPlugin):

    def _uiComponentLifeTimeEvent(self, alias, component):
        g_eventBus.handleEvent(events.GameEvent(events.GameEvent.AREA_POINT_MARKER_LIFETIME, {'alias': alias,
         'component': component}), scope=EVENT_BUS_SCOPE.BATTLE)


class EventDeathZonesMarkersPlugin(EventMarkerPlugin):

    def _uiComponentLifeTimeEvent(self, alias, component):
        g_eventBus.handleEvent(events.GameEvent(events.GameEvent.EVENT_DEATHZONE_MARKER_LIFETIME, {'alias': alias,
         'component': component}), scope=EVENT_BUS_SCOPE.BATTLE)


class MarkerGUIProvider(object):

    def __init__(self, changeListener, lifeTimeListener):
        super(MarkerGUIProvider, self).__init__()
        self._markers2D = None
        self._inited = False
        self._changeListener = changeListener
        self._lifeTimeListener = lifeTimeListener
        g_eventBus.addListener(lifeTimeListener, self.onUIComponentLifeTime, scope=EVENT_BUS_SCOPE.BATTLE)
        return

    @property
    def inited(self):
        return self._inited

    def getMarkers2DPlugin(self):
        return self._markers2D

    def onUIComponentLifeTime(self, event):
        alias = event.ctx['alias']
        component = event.ctx['component']
        if alias == BATTLE_VIEW_ALIASES.MARKERS_2D:
            self._markers2D = component
            self._checkState()

    def _clear(self):
        self._markers2D = None
        self._inited = False
        g_eventBus.removeListener(self._lifeTimeListener, self.onUIComponentLifeTime, scope=EVENT_BUS_SCOPE.BATTLE)
        return

    def _checkState(self):
        isInited = self._markers2D is not None
        if isInited is not self._inited:
            self._inited = isInited
            uiState = UI_STATE.START if self._inited else UI_STATE.STOP
            self._uiStateChangedEvent(uiState)
            if uiState == UI_STATE.STOP:
                self._clear()
        return

    def _uiStateChangedEvent(self, uiState):
        g_eventBus.handleEvent(events.GameEvent(self._changeListener, {'state': uiState}), scope=EVENT_BUS_SCOPE.BATTLE)
