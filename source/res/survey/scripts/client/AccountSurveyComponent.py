# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: survey/scripts/client/AccountSurveyComponent.py
import AccountCommands
from BaseAccountExtensionComponent import BaseAccountExtensionComponent
from SurveyConstants import CMD_SURVEY_RES

class AccountSurveyComponent(BaseAccountExtensionComponent):

    def sendSurveyResult(self, databaseID, arenaID, result):
        self.base.doCmdInt3(AccountCommands.REQUEST_ID_NO_RESPONSE, CMD_SURVEY_RES, databaseID, arenaID, result)
