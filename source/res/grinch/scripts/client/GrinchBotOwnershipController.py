# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: grinch/scripts/client/GrinchBotOwnershipController.py
from script_component.DynamicScriptComponent import DynamicScriptComponent

class GrinchBotOwnershipController(DynamicScriptComponent):

    def _onAvatarReady(self):
        super(GrinchBotOwnershipController, self)._onAvatarReady()
        self._sendOwnershipStateChangedEvent()

    def set_slavesLimit(self, _):
        self._sendOwnershipStateChangedEvent()

    def set_slavesCount(self, _):
        self._sendOwnershipStateChangedEvent()

    def _sendOwnershipStateChangedEvent(self):
        from grinch.gui.shared.events import BotOwnershipEvent
        from gui.shared import g_eventBus, EVENT_BUS_SCOPE
        g_eventBus.handleEvent(BotOwnershipEvent(BotOwnershipEvent.OWNERSHIP_STATE_CHANGED, slavesLimit=self.slavesLimit, slavesCount=self.slavesCount), scope=EVENT_BUS_SCOPE.BATTLE)
