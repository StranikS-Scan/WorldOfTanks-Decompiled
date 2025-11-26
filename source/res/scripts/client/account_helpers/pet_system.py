# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/account_helpers/pet_system.py
import typing
from functools import partial
import AccountCommands
from pet_system_common.pet_constants import PETS_SYSTEM_PDATA_KEY, SYNERGY_POINTS_TYPE, SYNERGY_POINTS_TYPE_TO_IDX
from shared_utils.account_helpers.diff_utils import synchronizeDicts
if typing.TYPE_CHECKING:
    from typing import Callable, Dict, Optional

def _getProxy(callback):
    return (lambda requestID, resultID, errorStr, ext={}: callback(resultID, errorStr, ext)) if callback is not None else None


class PetSystem(object):

    def __init__(self, syncData, commandsProxy):
        self.__cache = {}
        self.__ignore = True
        self.__syncData = syncData
        self.__commandsProxy = commandsProxy

    def onAccountBecomePlayer(self):
        self.__ignore = False

    def onAccountBecomeNonPlayer(self):
        self.__ignore = True

    def getCache(self, callback=None):
        if self.__ignore:
            if callback is not None:
                callback(AccountCommands.RES_NON_PLAYER, None)
            return
        else:
            self.__syncData.waitForSync(partial(self.__onGetCacheResponse, callback))
            return

    def synchronize(self, isFullSync, diff):
        if isFullSync and self.__cache:
            self.__cache.clear()
        if PETS_SYSTEM_PDATA_KEY in diff:
            synchronizeDicts(diff[PETS_SYSTEM_PDATA_KEY], self.__cache.setdefault(PETS_SYSTEM_PDATA_KEY, {}))

    def addPetDev(self, petId, callback=None):
        self.__commandsProxy.perform(AccountCommands.CMD_PET_SYSTEM_ADD_PET_DEV, int(petId), _getProxy(callback))

    def activateEventDev(self, eventId, callback=None):
        self.__commandsProxy.perform(AccountCommands.CMD_PET_ACTIVATE_EVENT_DEV, int(eventId), _getProxy(callback))

    def buyPet(self, petId, callback=None):
        self.__commandsProxy.perform(AccountCommands.CMD_PET_SYSTEM_BUY_PET, int(petId), _getProxy(callback))

    def selectActivePet(self, petId, callback=None):
        self.__commandsProxy.perform(AccountCommands.CMD_PET_SYSTEM_SELECT_ACTIVE_PET, int(petId), _getProxy(callback))

    def interactWithEvent(self, callback=None):
        self.__commandsProxy.perform(AccountCommands.CMD_PET_SYSTEM_INTERACT_WITH_EVENT, _getProxy(callback))

    def selectActiveBonus(self, bonusId, callback=None):
        self.__commandsProxy.perform(AccountCommands.CMD_PET_SYSTEM_SELECT_ACTIVE_PET_BONUS, int(bonusId), _getProxy(callback))

    def selectPetStateBehavior(self, stateBehavior, callback=None):
        self.__commandsProxy.perform(AccountCommands.CMD_PET_SYSTEM_SELECT_PET_STATE_BEHAVIOR, int(stateBehavior), _getProxy(callback))

    def selectPetName(self, petID, nameID, callback=None):
        self.__commandsProxy.perform(AccountCommands.CMD_PET_SYSTEM_SELECT_PET_NAME, int(petID), int(nameID), _getProxy(callback))

    def addFirstClickSynergy(self, petID, callback=None):
        self.__commandsProxy.perform(AccountCommands.CMD_PET_SYSTEM_ADD_SYNERGY, int(petID), SYNERGY_POINTS_TYPE_TO_IDX[SYNERGY_POINTS_TYPE.FIRST_CLICK], _getProxy(callback))

    def addSynergyDev(self, petID, synergyPoints, callback=None):
        self.__commandsProxy.perform(AccountCommands.CMD_PET_SYSTEM_ADD_SYNERGY_DEV, int(petID), int(synergyPoints), _getProxy(callback))

    def __onGetCacheResponse(self, callback, resultID):
        if resultID < 0:
            if callback is not None:
                callback(resultID, None)
            return
        else:
            if callback is not None:
                callback(resultID, self.__cache)
            return
