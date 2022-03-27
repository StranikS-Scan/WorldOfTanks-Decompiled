# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/rts_battles/rts_helpers.py
import constants
from account_helpers import AccountSettings
from account_helpers.AccountSettings import GUI_START_BEHAVIOR
from account_helpers.settings_core.settings_constants import GuiSettingsBehavior
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import dependency
from skeletons.gui.battle_results import IBattleResultsService
from skeletons.gui.game_control import IRTSBattlesController
from skeletons.gui.shared import IItemsCache

def isRTSBootcampComplete():
    defaults = AccountSettings.getFilterDefault(GUI_START_BEHAVIOR)
    guiStartBehavior = AccountSettings.settingsCore.serverSettings.getSection(GUI_START_BEHAVIOR, defaults)
    return bool(guiStartBehavior.get(GuiSettingsBehavior.IS_HIDE_RTS_BOOTCAMP_BANNER))


def markRTSBootcampComplete(isComplete=True):
    defaults = AccountSettings.getFilterDefault(GUI_START_BEHAVIOR)
    settingsCore = AccountSettings.settingsCore
    guiStartBehavior = settingsCore.serverSettings.getSection(GUI_START_BEHAVIOR, defaults)
    guiStartBehavior[GuiSettingsBehavior.IS_HIDE_RTS_BOOTCAMP_BANNER] = isComplete
    settingsCore.serverSettings.setSectionSettings(GUI_START_BEHAVIOR, guiStartBehavior)


def onShowRTSBootcampResult(arenaUniqueID):
    from gui.impl.lobby.rts.tutorial.rts_tutorial_helpers import showVictoryDialog, showDefeatDialog
    battleResults = dependency.instance(IBattleResultsService)
    result = battleResults.getResultsVO(arenaUniqueID)
    if result is None:
        return
    else:
        isWin = result.get('isWin', None)
        if isWin is None:
            return
        if isWin:
            markRTSBootcampComplete(isComplete=True)
            showVictoryDialog()
        else:
            showDefeatDialog()
        return


def playedRandomBattleOnTierXVehicle(itemsCache, rtsController):
    minNumOfBattles = rtsController.getSettings().getMinNumberOfBattlesPlayedWithTierX()
    if minNumOfBattles == 0:
        return True
    criteria = REQ_CRITERIA.VEHICLE.LEVELS([constants.MAX_VEHICLE_LEVEL])
    invVehiclesCDs = itemsCache.items.getVehicles(criteria).viewkeys()
    accountDossier = itemsCache.items.getAccountDossier()
    vehStatsRandom = accountDossier.getRandomStats().getVehicles()
    vehStatsEpicRandom = accountDossier.getEpicRandomStats().getVehicles()
    numOfBattles = sum((vehStatsRandom[vehCD].battlesCount for vehCD in invVehiclesCDs if vehCD in vehStatsRandom)) + sum((vehStatsEpicRandom[vehCD].battlesCount for vehCD in invVehiclesCDs if vehCD in vehStatsEpicRandom))
    return numOfBattles >= minNumOfBattles
