# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/event_mode_controller.py
from CurrentVehicle import g_currentVehicle
from event_mode.event_aop import _PointcutDisableSettingsControls
from constants import ARENA_GUI_TYPE
from gui.battle_control.arena_visitor import _getClientArena
from gui.shared import g_eventBus, events
from helpers import aop
from skeletons.gui.game_control import IEventModeController

class EventModeController(IEventModeController):

    def __init__(self):
        self._weaver = None
        self._pointcutIndex = None
        return

    def init(self):
        add = g_eventBus.addListener
        add(events.SettingsWindowEvent.POPULATE_WINDOW, self._onPopulate)
        add(events.SettingsWindowEvent.DISPOSE_WINDOW, self._onDispose)

    def fini(self):
        remove = g_eventBus.removeListener
        remove(events.SettingsWindowEvent.POPULATE_WINDOW, self._onPopulate)
        remove(events.SettingsWindowEvent.DISPOSE_WINDOW, self._onDispose)

    @property
    def _isEvent(self):
        arena = _getClientArena()
        return g_currentVehicle.isEvent() or hasattr(arena, 'guiType') and arena.guiType == ARENA_GUI_TYPE.EVENT_BATTLES

    def _onPopulate(self, event):
        if self._isEvent:
            self._weaver = aop.Weaver()
            self._pointcutIndex = self._weaver.weave(pointcut=_PointcutDisableSettingsControls)

    def _onDispose(self, event):
        if self._isEvent and self._weaver is not None and self._pointcutIndex is not None:
            self._weaver.clear(self._pointcutIndex)
        return
