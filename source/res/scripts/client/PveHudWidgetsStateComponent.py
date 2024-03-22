# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/PveHudWidgetsStateComponent.py
import typing
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import HasCtxEvent
from pve_battle_hud import getPveHudLogger, WidgetType
from script_component.DynamicScriptComponent import DynamicScriptComponent
_logger = getPveHudLogger()

class PveHudWidgetHasCtxEvent(HasCtxEvent):
    INIT_STATE = '{widgetType}_INIT_STATE'
    CHANGE_STATE = '{widgetType}_CHANGE_STATE'
    UPDATE_STATE = '{widgetType}_UPDATE_STATE'
    RESTORE_STATE = '{widgetType}_RESTORE_STATE'


class PveHudWidgetsStateComponent(DynamicScriptComponent):

    def __init__(self):
        super(PveHudWidgetsStateComponent, self).__init__()
        self._isReconnect = not self._isAvatarReady

    def initState(self, settings):
        self._sendEvent(PveHudWidgetHasCtxEvent.INIT_STATE, settings)

    def changeState(self, settings):
        self._sendEvent(PveHudWidgetHasCtxEvent.CHANGE_STATE, settings)

    def updateState(self, settings):
        self._sendEvent(PveHudWidgetHasCtxEvent.UPDATE_STATE, settings)

    def _onAvatarReady(self):
        if self._isReconnect:
            for settings in self.settings:
                self._sendEvent(PveHudWidgetHasCtxEvent.RESTORE_STATE, settings)

    @staticmethod
    def _sendEvent(eventType, settings):
        eventName = eventType.format(widgetType=WidgetType(settings['type']).name)
        _logger.debug('SendEvent: %s, %s', eventName, settings)
        g_eventBus.handleEvent(PveHudWidgetHasCtxEvent(eventType=eventName, ctx=settings), scope=EVENT_BUS_SCOPE.BATTLE)
