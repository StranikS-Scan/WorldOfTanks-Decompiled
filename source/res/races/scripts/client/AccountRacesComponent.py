# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: races/scripts/client/AccountRacesComponent.py
from races_common.races_constants import QUEUE_TYPE
import AccountCommands
from BaseAccountExtensionComponent import BaseAccountExtensionComponent
from PlayerEvents import g_playerEvents as events

class AccountRacesComponent(BaseAccountExtensionComponent):
    _QUEUE_TYPE = QUEUE_TYPE.RACES

    def enqueue(self, vehInvID):
        if not events.isPlayerEntityChanging:
            self.base.doCmdIntArr(AccountCommands.REQUEST_ID_NO_RESPONSE, AccountCommands.CMD_ENQUEUE_IN_BATTLE_QUEUE, [self._QUEUE_TYPE, vehInvID])

    def dequeue(self):
        if not events.isPlayerEntityChanging:
            self.base.doCmdInt(AccountCommands.REQUEST_ID_NO_RESPONSE, AccountCommands.CMD_DEQUEUE_FROM_BATTLE_QUEUE, self._QUEUE_TYPE)
