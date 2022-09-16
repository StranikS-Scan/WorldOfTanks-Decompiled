# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/AccountFunRandomComponent.py
import AccountCommands
from BaseAccountExtensionComponent import BaseAccountExtensionComponent
from constants import QUEUE_TYPE
from PlayerEvents import g_playerEvents as events

class AccountFunRandomComponent(BaseAccountExtensionComponent):
    _QUEUE_TYPE = QUEUE_TYPE.FUN_RANDOM

    def enqueueFunRandom(self, vehInvID):
        if not events.isPlayerEntityChanging:
            self.base.doCmdIntArr(AccountCommands.REQUEST_ID_NO_RESPONSE, AccountCommands.CMD_ENQUEUE_IN_BATTLE_QUEUE, [self.getQueueType(), vehInvID])

    def dequeueFunRandom(self):
        if not events.isPlayerEntityChanging:
            self.base.doCmdInt(AccountCommands.REQUEST_ID_NO_RESPONSE, AccountCommands.CMD_DEQUEUE_FROM_BATTLE_QUEUE, self.getQueueType())
