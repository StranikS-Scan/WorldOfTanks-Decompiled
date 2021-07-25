# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/account_helpers/maps_training.py
from functools import partial
import AccountCommands
from Event import Event
from shared_utils.account_helpers.diff_utils import synchronizeDicts
from maps_training_common.helpers import extractScenarioProgress
from maps_training_common.maps_training_constants import DEFAULT_PROGRESS_VALUE, MT_PDATA_KEY, VEHICLE_TYPE, MAX_SCENARIO_PROGRESS

class MapsTraining(object):

    def __init__(self, syncData):
        self.__syncData = syncData
        self.__account = None
        self.__cache = {}
        self.onMapsTrainingDataChanged = Event()
        self.__ignore = True
        return

    def onAccountBecomePlayer(self):
        self.__ignore = False

    def onAccountBecomeNonPlayer(self):
        self.__ignore = True

    def setAccount(self, account):
        self.__account = account

    def synchronize(self, isFullSync, diff):
        if isFullSync:
            self.__cache.clear()
        dataResetKey = (MT_PDATA_KEY, '_r')
        if dataResetKey in diff:
            self.__cache[MT_PDATA_KEY] = diff[dataResetKey]
            self.onMapsTrainingDataChanged(diff)
        if MT_PDATA_KEY in diff:
            synchronizeDicts(diff[MT_PDATA_KEY], self.__cache.setdefault(MT_PDATA_KEY, {}))
            self.onMapsTrainingDataChanged(diff)

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

    def __getResult(self, progress, vehType, team):
        bestResult = extractScenarioProgress(progress, team, vehType)
        scenarioCompleted = MAX_SCENARIO_PROGRESS == bestResult
        return (scenarioCompleted, bestResult)

    def getGeometryData(self, geometryID):
        progress = self.__cache[MT_PDATA_KEY].get(geometryID, DEFAULT_PROGRESS_VALUE)
        results = {}
        total = 0
        for vehType in VEHICLE_TYPE.ALL_TYPES:
            for team in VEHICLE_TYPE.ALL_TEAMS:
                completed, bestResult = self.__getResult(progress, vehType, team)
                total += int(completed)
                results.setdefault(vehType, {})[team] = {'completed': completed,
                 'best': bestResult}

        results['total'] = total
        return results
