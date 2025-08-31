# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/AccountWhiteTigerComponent.py
import AccountCommands
from BaseAccountExtensionComponent import BaseAccountExtensionComponent
from PlayerEvents import g_playerEvents as events
from white_tiger_common import account_commands_extension
from white_tiger_common.wt_constants import QUEUE_TYPE

class AccountWhiteTigerComponent(BaseAccountExtensionComponent):
    _QUEUE_TYPE = QUEUE_TYPE.WHITE_TIGER

    def enqueue(self, vehInvID):
        if not events.isPlayerEntityChanging:
            self.base.doCmdIntArr(AccountCommands.REQUEST_ID_NO_RESPONSE, AccountCommands.CMD_ENQUEUE_IN_BATTLE_QUEUE, [self._QUEUE_TYPE, vehInvID])

    def dequeue(self):
        if not events.isPlayerEntityChanging:
            self.base.doCmdInt(AccountCommands.REQUEST_ID_NO_RESPONSE, AccountCommands.CMD_DEQUEUE_FROM_BATTLE_QUEUE, self._QUEUE_TYPE)

    def openTankLootBox(self, callback=None):
        self.account._doCmdInt(account_commands_extension.CMD_WT_OPEN_TANK_LOOT_BOX, 0, callback)
