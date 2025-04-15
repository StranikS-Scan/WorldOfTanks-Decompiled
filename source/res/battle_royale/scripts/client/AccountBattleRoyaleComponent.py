# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/AccountBattleRoyaleComponent.py
import logging
import BattleRoyaleConstants as brc
import AccountCommands
from BaseAccountExtensionComponent import BaseAccountExtensionComponent
from battle_royale.gui.constants import BattleRoyaleSubMode
from battle_royale.gui.prb_control.entities.regular.pre_queue.entity import BRQueueCtx
from PlayerEvents import g_playerEvents as events
_logger = logging.getLogger(__name__)

class AccountBattleRoyaleComponent(BaseAccountExtensionComponent):

    def setBrCoin(self, amount, callback=None):
        _logger.debug("set battle royale coin amount: '%r'", amount)
        self.entity._doCmdIntStr(brc.CMD_BATTLE_ROYALE_OPERATE_BRCOIN, amount, '', callback)

    def enqueueBattleRoyale(self, ctx):
        if not events.isPlayerEntityChanging:
            self.base.doCmdInt3(AccountCommands.REQUEST_ID_NO_RESPONSE, AccountCommands.CMD_ENQUEUE_BATTLE_ROYALE, ctx.getVehicleInventoryID(), int(ctx.getCurrentSubModeID() == BattleRoyaleSubMode.SOLO_DYNAMIC_MODE_ID), 0)

    def dequeueBattleRoyale(self):
        if not events.isPlayerEntityChanging:
            self.base.doCmdInt3(AccountCommands.REQUEST_ID_NO_RESPONSE, AccountCommands.CMD_DEQUEUE_BATTLE_ROYALE, 0, 0, 0)
