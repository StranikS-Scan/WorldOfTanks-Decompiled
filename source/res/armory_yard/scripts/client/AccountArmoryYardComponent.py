# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: armory_yard/scripts/client/AccountArmoryYardComponent.py
from typing import Callable
import BigWorld
import armory_yard_constants

class AccountArmoryYardComponent(BigWorld.StaticScriptComponent):

    def collectAllRewards(self, callback=None):
        self.entity._doCmdInt(armory_yard_constants.CMD_COLLECT_REWARDS, 0, callback)

    def buyStepTokens(self, currency, count, callback=None):
        self.entity._doCmdIntStr(armory_yard_constants.CMD_BUY_STEP_TOKENS, count, currency, callback)

    def devAddToken(self, count, callback=None):
        self.entity._doCmdInt(armory_yard_constants.DEV_CMD_ADD_TOKEN_S, count, callback)

    def devAddArmoryCoin(self, count, callback=None):
        self.entity._doCmdInt(armory_yard_constants.DEV_CMD_ADD_ARMORY_COIN, count, callback)

    def devCompleteQuest(self, cycle, number, callback=None):
        self.entity._doCmdInt2(armory_yard_constants.DEV_CMD_SET_QUEST, cycle, number, callback)

    def devCompleteCycle(self, cycle, number, callback=None):
        self.entity._doCmdInt2(armory_yard_constants.DEV_CMD_SET_CYCLE, cycle, number, callback)

    def claimFinalReward(self, callback=None):
        self.entity._doCmdInt(armory_yard_constants.CMD_CLAIM_FINAL_REWARD, 0, callback)

    def buyShopProduct(self, product, count, data, callback=None):
        self.entity._doCmdInt2Str(armory_yard_constants.CMD_BUY_SHOP_PRODUCT, product, count, data, callback)
