# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/AccountBattleRoyaleComponent.py
import logging
import BigWorld
import BattleRoyaleConstants as brc
_logger = logging.getLogger(__name__)

class AccountBattleRoyaleComponent(BigWorld.StaticScriptComponent):

    def applyTestDrive(self, invID, callback=None):
        _logger.debug("apply test drive for: '%r'", invID)
        self.entity._doCmdIntStr(brc.CMD_BATTLE_ROYALE_TEST_DRIVE, invID, '', callback)

    def applyRent(self, invID, callback=None):
        _logger.debug("apply rent for: '%r'", invID)
        self.entity._doCmdIntStr(brc.CMD_BATTLE_ROYALE_RENT, invID, '', callback)

    def setBrCoin(self, amount, callback=None):
        _logger.debug("set battle royale coin amount: '%r'", amount)
        self.entity._doCmdIntStr(brc.CMD_BATTLE_ROYALE_OPERATE_BRCOIN, amount, '', callback)
