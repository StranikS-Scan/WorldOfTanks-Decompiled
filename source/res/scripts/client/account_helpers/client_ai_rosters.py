# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/account_helpers/client_ai_rosters.py
import logging
from functools import partial
import AccountCommands
from gui.shared.utils.requesters import REQ_CRITERIA
from shared_utils.account_helpers.diff_utils import synchronizeDicts
_logger = logging.getLogger(__name__)

def _getUnsuitableVehicleCriteria(vehicleConfig):
    allowedLevels = vehicleConfig.get('levels', frozenset())
    allowedTags = vehicleConfig.get('allowedTags', frozenset())
    forbiddenTags = vehicleConfig.get('forbiddenTags', frozenset())
    forbiddenTypes = vehicleConfig.get('forbiddenTypes', frozenset())
    hasCriteria = False
    resultCriteria = REQ_CRITERIA.NONE
    if allowedLevels:
        resultCriteria ^= ~REQ_CRITERIA.VEHICLE.LEVELS(allowedLevels)
        hasCriteria = True
    if allowedTags:
        resultCriteria ^= ~REQ_CRITERIA.VEHICLE.HAS_ANY_OF_TAGS(allowedTags)
        hasCriteria = True
    if forbiddenTags:
        resultCriteria ^= REQ_CRITERIA.VEHICLE.HAS_ANY_OF_TAGS(forbiddenTags)
        hasCriteria = True
    if forbiddenTypes:
        resultCriteria ^= REQ_CRITERIA.VEHICLE.SPECIFIC_BY_CD(forbiddenTypes)
        hasCriteria = True
    return resultCriteria if hasCriteria else None


def _getSuitableVehicleCriteria(vehicleConfig):
    allowedLevels = vehicleConfig.get('levels', frozenset())
    allowedTags = vehicleConfig.get('allowedTags', frozenset())
    forbiddenTags = vehicleConfig.get('forbiddenTags', frozenset())
    forbiddenTypes = vehicleConfig.get('forbiddenTypes', frozenset())
    hasCriteria = False
    resultCriteria = REQ_CRITERIA.EMPTY
    if allowedLevels:
        resultCriteria |= REQ_CRITERIA.VEHICLE.LEVELS(allowedLevels)
        hasCriteria = True
    if allowedTags:
        resultCriteria |= REQ_CRITERIA.VEHICLE.HAS_ANY_OF_TAGS(allowedTags)
        hasCriteria = True
    if forbiddenTags:
        resultCriteria |= ~REQ_CRITERIA.VEHICLE.HAS_ANY_OF_TAGS(forbiddenTags)
        hasCriteria = True
    if forbiddenTypes:
        resultCriteria |= ~REQ_CRITERIA.VEHICLE.SPECIFIC_BY_CD(forbiddenTypes)
        hasCriteria = True
    return resultCriteria if hasCriteria else None


def getUnsuitableVehiclesCriteria(vehicleConfigs):
    hasCriteria = False
    resultCriteria = REQ_CRITERIA.EMPTY
    for vehicleConfig in vehicleConfigs:
        vehicleCriteria = _getUnsuitableVehicleCriteria(vehicleConfig)
        if vehicleCriteria:
            resultCriteria |= vehicleCriteria
            hasCriteria = True

    return REQ_CRITERIA.INVENTORY | resultCriteria if hasCriteria else REQ_CRITERIA.NONE


def getSuitableVehiclesCriteria(vehicleConfigs):
    hasCriteria = False
    resultCriteria = REQ_CRITERIA.NONE
    for vehicleConfig in vehicleConfigs:
        vehicleCriteria = _getSuitableVehicleCriteria(vehicleConfig)
        if vehicleCriteria:
            resultCriteria ^= vehicleCriteria
            hasCriteria = True

    return resultCriteria if hasCriteria else REQ_CRITERIA.EMPTY


def getSuitableVehicleCriteriaForRoster(vehicleConfig):
    allowedLevels = vehicleConfig.get('levels', frozenset())
    forbiddenTags = vehicleConfig.get('forbiddenTags', frozenset())
    forbiddenTypes = vehicleConfig.get('forbiddenTypes', frozenset())
    hasCriteria = False
    resultCriteria = REQ_CRITERIA.EMPTY
    if allowedLevels:
        resultCriteria |= REQ_CRITERIA.VEHICLE.LEVELS(allowedLevels)
        hasCriteria = True
    if forbiddenTags:
        resultCriteria |= ~REQ_CRITERIA.VEHICLE.HAS_ANY_OF_TAGS(forbiddenTags)
        hasCriteria = True
    if forbiddenTypes:
        resultCriteria |= ~REQ_CRITERIA.VEHICLE.SPECIFIC_BY_CD(forbiddenTypes)
        hasCriteria = True
    return resultCriteria if hasCriteria else REQ_CRITERIA.EMPTY


class ClientAIRosters(object):

    def __init__(self, syncData):
        super(ClientAIRosters, self).__init__()
        self.__account = None
        self.__syncData = syncData
        self.__cache = {}
        self.__ignore = True
        return

    def onAccountBecomePlayer(self):
        self.__ignore = False

    def onAccountBecomeNonPlayer(self):
        self.__ignore = True

    def setAccount(self, account):
        self.__account = account

    def synchronize(self, isFullSync, diff):
        _logger.debug('Synchronize AI rosters')
        if isFullSync:
            self.__cache.clear()
        synchronizeDicts(diff.get('aiRosters', {}), self.__cache)
        _logger.debug('AI rosters info: %s', self.__cache)

    def getCache(self, callback=None):
        if self.__ignore:
            if callback is not None:
                callback(AccountCommands.RES_NON_PLAYER, None)
            return
        else:
            self.__syncData.waitForSync(partial(self.__onGetCacheResponse, callback))
            return

    def __onGetCacheResponse(self, callback, resultID):
        if resultID < 0:
            if callback is not None:
                callback(resultID, None)
            return
        else:
            if callback is not None:
                callback(resultID, self.__cache)
            return
