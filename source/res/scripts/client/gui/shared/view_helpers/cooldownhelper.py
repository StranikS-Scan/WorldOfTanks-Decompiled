# Embedded file name: scripts/client/gui/shared/view_helpers/CooldownHelper.py
import BigWorld
from gui.shared import g_eventBus, EVENT_BUS_SCOPE

class CooldownHelper(object):

    def __init__(self, requestIDs, handler, eventType, eventScope = EVENT_BUS_SCOPE.LOBBY):
        raise len(requestIDs) or AssertionError
        self._eventType = eventType
        self._eventScope = eventScope
        self._requestIDs = requestIDs
        self._cooldownCbID = None
        self.__handler = handler
        return

    def start(self):
        g_eventBus.addListener(self._eventType, self._handleSetClubCoolDown, scope=self._eventScope)

    def stop(self):
        self._cancelCallback()
        g_eventBus.removeListener(self._eventType, self._handleSetClubCoolDown, scope=self._eventScope)

    def _handleSetClubCoolDown(self, event):
        if event.requestID in self._requestIDs and event.coolDown > 0:
            self.__handler(True)
            self._loadCallback(event.coolDown)

    def _loadCallback(self, cooldown):
        self._cancelCallback()
        self._cooldownCbID = BigWorld.callback(cooldown, self._onCooldownTimeLeft)

    def _cancelCallback(self):
        if self._cooldownCbID is not None:
            BigWorld.cancelCallback(self._cooldownCbID)
            self._cooldownCbID = None
        return

    def _onCooldownTimeLeft(self):
        self._cancelCallback()
        self.__handler(False)
