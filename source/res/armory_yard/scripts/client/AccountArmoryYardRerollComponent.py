# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: armory_yard/scripts/client/AccountArmoryYardRerollComponent.py
import BigWorld
import armory_yard_constants

class AccountArmoryYardRerollComponent(BigWorld.StaticScriptComponent):

    def rerollArmoryQuestPaid(self, questID, rerollCost, rerollCurrency, callback=None):
        self.entity._doCmdIntStrArr(armory_yard_constants.CMD_REROLL_ARMORY_QUEST, rerollCost, (rerollCurrency, questID), callback)

    def rerollArmoryQuestFree(self, questID, callback=None):
        self.entity._doCmdIntStrArr(armory_yard_constants.CMD_REROLL_ARMORY_QUEST, 0, ('', questID), callback)

    def acceptReroll(self, conditionID, questID, callback=None):
        self.entity._doCmdIntStr(armory_yard_constants.CMD_ACCEPT_REROLL_ARMORY_QUEST, conditionID, questID, callback)
