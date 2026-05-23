# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/AccountComp7Component.py
from BaseAccountExtensionComponent import BaseAccountExtensionComponent
import comp7_account_commands

class AccountComp7Component(BaseAccountExtensionComponent):

    def setVehicleSkill(self, vehInvID, equipmentID, callback=None):
        if callback is not None:
            proxy = lambda requestID, resultID, errorStr: callback(resultID, errorStr)
        else:
            proxy = None
        self.entity._doCmdInt2(comp7_account_commands.CMD_EQUIP_COMP7_SKILL, vehInvID, equipmentID, proxy)
        return
