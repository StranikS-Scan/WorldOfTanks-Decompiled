# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/FLAccountComponent.py
import AccountCommands
from BaseAccountExtensionComponent import BaseAccountExtensionComponent
from PlayerEvents import g_playerEvents as events
from debug_utils import LOG_DEBUG_DEV
from frontline_common import frontline_account_commands
from constants import QUEUE_TYPE

def skipResponse(resultID, errorCode):
    LOG_DEBUG_DEV('skipResponse', resultID, errorCode)


class FLAccountComponent(BaseAccountExtensionComponent):

    def createEpicTrainingPrebattle(self, arenaTypeID, roundLength, isOpened, comment):
        if not events.isPlayerEntityChanging:
            self.base.doCmdInt2Str(AccountCommands.REQUEST_ID_NO_RESPONSE, frontline_account_commands.CMD_CREATE_PREBATTLE_EPIC_TRAINING, arenaTypeID, int(isOpened), comment)

    def createDevEpicPrebattle(self, arenaTypeID, roundLength, isOpened, comment):
        if not events.isPlayerEntityChanging:
            self.base.doCmdIntStr(AccountCommands.REQUEST_ID_NO_RESPONSE, frontline_account_commands.CMD_CREATE_PREBATTLE_EPIC, arenaTypeID, comment)

    def enqueueEpic(self, vehInvID):
        if not events.isPlayerEntityChanging:
            self.base.doCmdIntArr(AccountCommands.REQUEST_ID_NO_RESPONSE, AccountCommands.CMD_ENQUEUE_IN_BATTLE_QUEUE, [QUEUE_TYPE.EPIC, vehInvID])

    def dequeueEpic(self):
        if not events.isPlayerEntityChanging:
            self.base.doCmdInt(AccountCommands.REQUEST_ID_NO_RESPONSE, AccountCommands.CMD_DEQUEUE_FROM_BATTLE_QUEUE, QUEUE_TYPE.EPIC)

    def forceEpicDevStart(self):
        if not events.isPlayerEntityChanging:
            self.base.doCmdInt3(AccountCommands.REQUEST_ID_NO_RESPONSE, frontline_account_commands.CMD_FORCE_EPIC_DEV_START, 0, 0, 0)

    def setSelectedAbilities(self, listOfAbilities, vehicleCD, callback, isForVehsClass):
        callback = callback or skipResponse
        cmd = frontline_account_commands.CMD_UPDATE_SELECTED_EPIC_META_ABILITY_VEHICLES if isForVehsClass else frontline_account_commands.CMD_UPDATE_SELECTED_EPIC_META_ABILITY
        self.entity._doCmdIntArr(cmd, listOfAbilities + [vehicleCD], lambda requestID, resultID, errorCode: callback(resultID, errorCode))

    def increaseAbility(self, abilityID, callback=skipResponse):
        self.entity._doCmdInt(frontline_account_commands.CMD_INCREASE_EPIC_META_ABILITY, abilityID, lambda requestID, resultID, errorCode: callback(resultID, errorCode))

    def resetEpicMetaGame(self, metaLevel=0, abilityPoints=0, callback=skipResponse):
        self.entity._doCmdInt2(frontline_account_commands.CMD_RESET_EPIC_META_GAME, metaLevel, abilityPoints, lambda requestID, resultID, errorCode: callback(resultID, errorCode))

    def flGameModeSetup(self, mode):
        self.entity._doCmdInt(frontline_account_commands.CMD_FL_GAME_MODE_SETUP, mode, None)
        return

    def unlockFrontlineReserves(self):
        self.entity._doCmdInt(frontline_account_commands.CMD_FRONTLINE_UNLOCK_RESERVES, 0, None)
        return

    def showFrontlineSysMessage(self, msgID):
        self.entity._doCmdInt(frontline_account_commands.CMD_SHOW_FRONTLINE_SYS_MSG, msgID, None)
        return

    def resetScreenShown(self, screenName):
        from account_helpers.AccountSettings import GUI_START_BEHAVIOR
        from account_helpers import AccountSettings
        from helpers import dependency
        from skeletons.account_helpers.settings_core import ISettingsCore
        settingsCore = dependency.instance(ISettingsCore)
        defaults = AccountSettings.getFilterDefault(GUI_START_BEHAVIOR)
        settings = settingsCore.serverSettings.getSection(GUI_START_BEHAVIOR, defaults)
        settings[screenName] = False
        settingsCore.serverSettings.setSectionSettings(GUI_START_BEHAVIOR, settings)
