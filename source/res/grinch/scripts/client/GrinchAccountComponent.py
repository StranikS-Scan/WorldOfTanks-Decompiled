# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: grinch/scripts/client/GrinchAccountComponent.py
import AccountCommands
from BaseAccountExtensionComponent import BaseAccountExtensionComponent
from constants import QUEUE_TYPE
from PlayerEvents import g_playerEvents as events

class GrinchAccountComponent(BaseAccountExtensionComponent):

    def enqueueBattle(self, vehInvID):
        self.base.doCmdIntArr(AccountCommands.REQUEST_ID_NO_RESPONSE, AccountCommands.CMD_ENQUEUE_IN_BATTLE_QUEUE, [QUEUE_TYPE.GRINCH, vehInvID])

    def dequeueBattle(self):
        if not events.isPlayerEntityChanging:
            self.base.doCmdInt(AccountCommands.REQUEST_ID_NO_RESPONSE, AccountCommands.CMD_DEQUEUE_FROM_BATTLE_QUEUE, QUEUE_TYPE.GRINCH)
