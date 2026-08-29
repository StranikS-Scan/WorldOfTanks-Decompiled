# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/WhiteTigerDevComponent.py
from __future__ import absolute_import
import AccountCommands
from BaseAccountExtensionComponent import BaseAccountExtensionComponent
from constants import IS_DEVELOPMENT
from white_tiger_common import wt_account_commands as wtCmd

class WhiteTigerDevComponent(BaseAccountExtensionComponent):

    def addQuestVehicleKills(self, questID, delta):
        if not IS_DEVELOPMENT:
            return
        self.base.doCmdIntStr(AccountCommands.REQUEST_ID_NO_RESPONSE, wtCmd.CMD_WT_ADD_QUEST_VEHICLE_KILLS_DEV, delta, questID)

    def resetQuestProgress(self, questIDs):
        if not IS_DEVELOPMENT:
            return
        self.base.doCmdStrArr(AccountCommands.REQUEST_ID_NO_RESPONSE, wtCmd.CMD_WT_DISCARD_QUEST_PROGRESS_DEV, questIDs)
