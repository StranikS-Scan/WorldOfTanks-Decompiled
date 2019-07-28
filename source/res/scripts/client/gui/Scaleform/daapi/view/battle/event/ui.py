# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/ui.py
from bootcamp.BootcampConstants import UI_STATE
from bootcamp.BootcampGUI import BootcampStaticObjectsPlugin
from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES
from gui.shared import g_eventBus, EVENT_BUS_SCOPE, events

class LootSignPlugin(BootcampStaticObjectsPlugin):

    def start(self):
        self._fireUIComponentLifetimeEvent(BATTLE_VIEW_ALIASES.MARKERS_2D, self)

    def stop(self):
        self._fireUIComponentLifetimeEvent(BATTLE_VIEW_ALIASES.MARKERS_2D, None)
        return

    def _fireUIComponentLifetimeEvent(self, alias, component):
        g_eventBus.handleEvent(events.GameEvent(events.GameEvent.LOOTSIGN_COMPONENT_LIFETIME, {'alias': alias,
         'component': component}), scope=EVENT_BUS_SCOPE.BATTLE)


class LootSignUI(object):

    def __init__(self):
        super(LootSignUI, self).__init__()
        self._markers2D = None
        self._inited = False
        g_eventBus.addListener(events.GameEvent.LOOTSIGN_COMPONENT_LIFETIME, self.onUIComponentLifetime, scope=EVENT_BUS_SCOPE.BATTLE)
        return

    @property
    def inited(self):
        return self._inited

    def getMarkers2DPlugin(self):
        return self._markers2D

    def onUIComponentLifetime(self, event):
        alias = event.ctx['alias']
        component = event.ctx['component']
        if alias == BATTLE_VIEW_ALIASES.MARKERS_2D:
            self._markers2D = component
            self._checkState()

    def _clear(self):
        self._markers2D = None
        self._inited = False
        g_eventBus.removeListener(events.GameEvent.LOOTSIGN_COMPONENT_LIFETIME, self.onUIComponentLifetime, scope=EVENT_BUS_SCOPE.BATTLE)
        return

    def _checkState(self):
        isInited = self._markers2D is not None
        if isInited is not self._inited:
            self._inited = isInited
            uiState = UI_STATE.START if self._inited else UI_STATE.STOP
            self._fireUIStateChangedEvent(uiState)
            if uiState == UI_STATE.STOP:
                self._clear()
        return

    def _fireUIStateChangedEvent(self, uiState):
        g_eventBus.handleEvent(events.GameEvent(events.GameEvent.LOOTSIGN_STATE_CHANGED, {'state': uiState}), scope=EVENT_BUS_SCOPE.BATTLE)
