# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/account_helpers/abilities.py
import AccountCommands
from items.AbilitiesManager import AbilitiesManager
from CurrentVehicle import g_currentVehicle

class AbilitiesHelper(object):

    def __init__(self):
        self.__account = None
        self.__ignore = True
        self.__abilities = AbilitiesManager()
        return

    def onAccountBecomePlayer(self):
        self.__ignore = False

    def onAccountBecomeNonPlayer(self):
        self.__ignore = True

    def setAccount(self, account):
        self.__account = account

    @property
    def abilitiesManager(self):
        return self.__abilities

    def addPerks(self, battle, vehicleID, scopeIndex, perksList, callback=None):
        if battle:
            if self.__ignore:
                if callback is not None:
                    callback(AccountCommands.RES_NON_PLAYER)
                return
            if callback is not None:
                proxy = lambda requestID, resultID, errorStr, ext={}: callback(resultID)
            else:
                proxy = None
            perksListRes = [vehicleID, scopeIndex]
            perksListRes.extend(perksList)
            self.__account._doCmdIntArr(AccountCommands.CMD_ADD_PERK_TO_BATTLE, perksListRes, proxy)
        else:
            perks = [ (perksList[i], perksList[i + 1]) for i in range(0, len(perksList), 2) ]
            self.abilitiesManager.addBuild(vehicleID, 'debug' + str(scopeIndex), perks)
            if not g_currentVehicle.item:
                return
            self.reloadPerks(vehicleID)
        return

    def resetPerks(self, battle, vehicleID, callback=None):
        if battle:
            if self.__ignore:
                if callback is not None:
                    callback(AccountCommands.RES_NON_PLAYER)
                return
            if callback is not None:
                proxy = lambda requestID, resultID, errorStr, ext={}: callback(resultID)
            else:
                proxy = None
            self.__account._doCmdInt2(AccountCommands.CMD_RESET_PERK_FOR_BATTLE, vehicleID, 0, proxy)
        else:
            self.abilitiesManager.removePerksByVehicle(vehicleID)
        self.reloadPerks(vehicleID)
        return

    def reloadPerks(self, vehicleID):
        if vehicleID != g_currentVehicle.invID:
            return
        perksController = g_currentVehicle.item.getPerksController()
        if perksController:
            scopedPerks = self.abilitiesManager.getPerksByVehicle(vehicleID)
            perksController.reload(scopedPerks)
