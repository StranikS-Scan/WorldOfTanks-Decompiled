# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: cosmic_event/scripts/client/AccountCosmicEventComponent.py
import AccountCommands
from BaseAccountExtensionComponent import BaseAccountExtensionComponent
from PlayerEvents import g_playerEvents as events
from cosmic_event_common.cosmic_constants import QUEUE_TYPE

class AccountCosmicEventComponent(BaseAccountExtensionComponent):
    _QUEUE_TYPE = QUEUE_TYPE.COSMIC_EVENT

    def enqueue(self, vehInvID):
        if not events.isPlayerEntityChanging:
            self.base.doCmdIntArr(AccountCommands.REQUEST_ID_NO_RESPONSE, AccountCommands.CMD_ENQUEUE_IN_BATTLE_QUEUE, [self._QUEUE_TYPE, vehInvID])

    def dequeue(self):
        if not events.isPlayerEntityChanging:
            self.base.doCmdInt(AccountCommands.REQUEST_ID_NO_RESPONSE, AccountCommands.CMD_DEQUEUE_FROM_BATTLE_QUEUE, self._QUEUE_TYPE)
