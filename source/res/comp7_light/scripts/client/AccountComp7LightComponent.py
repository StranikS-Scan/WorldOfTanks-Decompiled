# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_light/scripts/client/AccountComp7LightComponent.py
import AccountCommands
from BaseAccountExtensionComponent import BaseAccountExtensionComponent
from PlayerEvents import g_playerEvents as events
from constants import QUEUE_TYPE

class AccountComp7LightComponent(BaseAccountExtensionComponent):

    def enqueueComp7Light(self, vehInvID):
        if not events.isPlayerEntityChanging:
            self.base.doCmdIntArr(AccountCommands.REQUEST_ID_NO_RESPONSE, AccountCommands.CMD_ENQUEUE_IN_BATTLE_QUEUE, [QUEUE_TYPE.COMP7_LIGHT, vehInvID])

    def dequeueComp7Light(self):
        if not events.isPlayerEntityChanging:
            self.base.doCmdInt(AccountCommands.REQUEST_ID_NO_RESPONSE, AccountCommands.CMD_DEQUEUE_FROM_BATTLE_QUEUE, QUEUE_TYPE.COMP7_LIGHT)
