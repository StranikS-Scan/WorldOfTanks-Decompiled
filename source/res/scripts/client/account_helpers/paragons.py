# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/account_helpers/paragons.py
import logging
from functools import partial
import typing
import AccountCommands
from account_helpers.paragons_storage import ParagonsStorage
from gui.shared.utils.requesters import REQ_CRITERIA
from gui.shared.utils.requesters.ItemsRequester import RESEARCH_CRITERIA
from items import vehicles
from helpers import dependency
from skeletons.gui.shared import IItemsCache
from paragons_common import ErrorReasons, BaseParagons, PARAGONS_MAX_VEHICLE_LEVEL
if typing.TYPE_CHECKING:
    from typing import Dict, Set, Callable, Optional
    from Account import _ClientCommandProxy
    from paragons_common import BaseParagonsBranchState
    T_COMMAND_CALLBACK = Callable[[int, int, str], None]
_logger = logging.getLogger()

class Paragons(BaseParagons):
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, commandProxy):
        super(Paragons, self).__init__(ParagonsStorage())
        self.__commandProxy = commandProxy
        self.onParagonsStateChanged = self.storage.onParagonsStateChanged
        self.onLevelIncreased = self.storage.onLevelIncreased
        self.onParagonsUnlocksGranted = self.storage.onParagonsUnlocksGranted

    @property
    def resetBranchesIds(self):
        return self.storage.resetBranchesIds

    @property
    def resetBranchesCount(self):
        return self.storage.resetBranchesCount

    def clear(self):
        self.__commandProxy = None
        self.destroy()
        return

    def synchronize(self, isFullSync, diff):
        self.storage.synchronize(isFullSync, diff)

    def isVehicleReset(self, compDescr):
        resetBranchIds = vehicles.g_cache.paragonsBranchesToReset.getResetBranchIdsByVehicleCd(compDescr)
        return any((self.storage.branchPendingVehicles(resetBranchId) and compDescr in self.storage.branchPendingVehicles(resetBranchId) and self.storage.getBranchStateById(resetBranchId).resetsCount for resetBranchId in resetBranchIds))

    def getBranchStateById(self, branchID):
        resetBranch = vehicles.g_cache.paragonsBranchesToReset.getResetBranchById(branchID)
        return None if not resetBranch else self.storage.getBranchStateById(branchID)

    def resetBranch(self, branchID, isStock=0, callback=None):
        self.__commandProxy.perform(AccountCommands.CMD_PARAGONS_RESET_BRANCH, branchID, isStock, callback)

    def setChapter(self, chapterID, callback=None):
        self.__commandProxy.perform(AccountCommands.CMD_PARAGONS_SELECT_CHAPTER, chapterID, callback)

    def markSelectedRewards(self, chapterID, levelID, tokenID, callback=None):
        self.__commandProxy.perform(AccountCommands.CMD_PARAGONS_MARK_SELECTED_REWARDS, chapterID, levelID, tokenID, callback)

    def getUnlockedNecessaryLevelVehiclesCDs(self):
        criteria = RESEARCH_CRITERIA.UNLOCKED_VEHICLES
        criteria |= REQ_CRITERIA.VEHICLE.LEVEL(PARAGONS_MAX_VEHICLE_LEVEL)
        getResetBranchIdsByVehicleCd = vehicles.g_cache.paragonsBranchesToReset.getResetBranchIdsByVehicleCd
        criteria |= REQ_CRITERIA.CUSTOM(lambda item: bool(getResetBranchIdsByVehicleCd(item.intCD)))
        eliteVehiclesCDs = set(self.__itemsCache.items.getVehicles(criteria))
        return eliteVehiclesCDs

    def setResetBranchState(self, branchID, resetsCount=1):
        self.__commandProxy.perform(AccountCommands.CMD_PARAGONS_SET_RESET_BRANCH_STATE, branchID, resetsCount, partial(self.__onDevCommandExecuted, 'setResetBranchState', {'branchID': branchID,
         'resetsCount': resetsCount}))

    def clearResetBranchState(self, branchID):
        self.__commandProxy.perform(AccountCommands.CMD_PARAGONS_CLEAR_RESET_BRANCH_STATE, branchID, partial(self.__onDevCommandExecuted, 'clearResetBranchStats', {'branchID': branchID}))

    def grantParagonsUnlock(self, paragonsUnlockID):
        self.__commandProxy.perform(AccountCommands.CMD_PARAGONS_GRANT_PARAGONS_UNLOCK, paragonsUnlockID, partial(self.__onDevCommandExecuted, 'grantParagonsUnlock', {'paragonsUnlockID': paragonsUnlockID}))

    def consumeParagonsUnlock(self, paragonsUnlockID):
        self.__commandProxy.perform(AccountCommands.CMD_PARAGONS_CONSUME_PARAGONS_UNLOCK, paragonsUnlockID, partial(self.__onDevCommandExecuted, 'consumeParagonsUnlock', {'paragonsUnlockID': paragonsUnlockID}))

    def __onDevCommandExecuted(self, commandName, callArgs, _, resultID, reason):
        if resultID == AccountCommands.RES_SUCCESS:
            return
        if resultID == AccountCommands.RES_FAILURE and reason in ErrorReasons.all():
            _logger.error('[Paragons]: %s failed: callArgs = %s, reason = %s', commandName, callArgs, reason)
        else:
            _logger.error('[Paragons]: %s command unexpected result: resultID = %s, reason = %s', commandName, resultID, reason)
