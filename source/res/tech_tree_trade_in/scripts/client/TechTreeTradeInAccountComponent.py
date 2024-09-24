# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: tech_tree_trade_in/scripts/client/TechTreeTradeInAccountComponent.py
from debug_utils import LOG_DEBUG_DEV
from BaseAccountExtensionComponent import BaseAccountExtensionComponent
from AccountCommands import CMD_TRADE_IN_TREES, CMD_TRADE_IN_TREES_DRY_RUN, CMD_TRADE_IN_TREES_PRICE

class TechTreeTradeInAccountComponent(BaseAccountExtensionComponent):

    def requestTradeIn(self, branchToTrade, branchToReceive, price, callback):
        LOG_DEBUG_DEV('TechTreeTradeIn: requestTradeIn', branchToTrade, branchToReceive, price)
        self.entity._doCmdIntArr(CMD_TRADE_IN_TREES, branchToTrade + branchToReceive + price, lambda requestID, resultID, errorStr, ctx=None: callback(resultID, errorStr, ctx))
        return

    def requestTradeInDryRun(self, branchToTrade, branchToReceive, callback):
        self.entity._doCmdIntArr(CMD_TRADE_IN_TREES_DRY_RUN, branchToTrade + branchToReceive, lambda *args: callback(args))

    def requestTradeInPrice(self, branchToTrade, branchToReceive, callback):
        self.entity._doCmdIntArr(CMD_TRADE_IN_TREES_PRICE, branchToTrade + branchToReceive, lambda *args: callback(args))
