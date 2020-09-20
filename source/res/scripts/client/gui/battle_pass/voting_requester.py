# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_pass/voting_requester.py
import logging
import weakref
from adisp import process
from Event import Event, EventManager
from gui.shared.utils.scheduled_notifications import SimpleNotifier
from gui.wgcg.battle_pass.contexts import BattlePassGetVotingDataCtx
from helpers import dependency
from skeletons.gui.web import IWebController
_logger = logging.getLogger(__name__)

class BattlePassVotingRequester(object):
    __slots__ = ('__battlePassController', '__isAvailableService', '__isStarted', '__requestNotifier', '__cache', '__eventsManager', 'onVotingResultsUpdated', '__isNeedActualData')
    __webController = dependency.descriptor(IWebController)
    CALLBACK_REPEAT_TIME = 60
    UPDATE_DATA_TIME = 300

    def __init__(self, battlePassController):
        super(BattlePassVotingRequester, self).__init__()
        self.__battlePassController = weakref.proxy(battlePassController)
        self.__eventsManager = EventManager()
        self.__requestNotifier = SimpleNotifier(self.__getTimeToRepeatRequest, self.__requestVotingData)
        self.__isStarted = False
        self.__isAvailableService = True
        self.__isNeedActualData = False
        self.__cache = {}
        self.onVotingResultsUpdated = Event(self.__eventsManager)

    def start(self):
        if not self.__isStarted and self.__battlePassController.isEnabled():
            self.__isStarted = True
            self.__requestVotingData(self.__getDefaultSeasonIDs())

    def startGettingResults(self, seasonID):
        if not self.__isStarted:
            logging.warning('Battle Pass voting requester is not started.')
            return (False, {})
        self.__isNeedActualData = True
        result = {}
        if self.__cache.get(seasonID):
            result = self.__cache[seasonID]
            if seasonID == self.__battlePassController.getSeasonID():
                self.__requestVotingData([seasonID])
        else:
            self.__requestVotingData([seasonID])
        return (self.__isAvailableService, result)

    def stopGetting(self):
        self.__isNeedActualData = False
        self.__requestNotifier.stopNotification()

    def stop(self):
        self.__isStarted = False
        self.__isNeedActualData = False
        self.__requestNotifier.stopNotification()
        self.__eventsManager.clear()

    @process
    def __requestVotingData(self, seasons=None):
        if seasons is None:
            seasons = self.__getDefaultSeasonIDs()
        ctx = BattlePassGetVotingDataCtx(seasons)
        response = yield self.__webController.sendRequest(ctx=ctx)
        if not self.__isStarted:
            return
        else:
            self.__isAvailableService = response.isSuccess()
            result = {}
            if self.__isAvailableService:
                result = ctx.getDataObj(response.getData())
            else:
                _logger.warning('Bad response from Get Battle Pass Voting Data')
            if self.__isNeedActualData:
                self.__requestNotifier.startNotification()
            self.__updateCache(result)
            return

    def __updateCache(self, votingResults):
        isCacheUpdated = False
        for seasonID, votingResult in votingResults.iteritems():
            if not self.__cache.get(seasonID):
                self.__cache[seasonID] = votingResult
                isCacheUpdated = True
                continue
            for vehCD, countVoices in votingResult.iteritems():
                if self.__cache[seasonID].get(vehCD) != countVoices:
                    self.__cache[seasonID] = votingResult
                    isCacheUpdated = True
                    break

        if isCacheUpdated:
            self.onVotingResultsUpdated()

    def __getTimeToRepeatRequest(self):
        return self.UPDATE_DATA_TIME if self.__isAvailableService else self.CALLBACK_REPEAT_TIME

    def __getDefaultSeasonIDs(self):
        result = [self.__battlePassController.getSeasonID()]
        allSeasonStats = self.__battlePassController.getPrevSeasonsStats()
        if not allSeasonStats:
            return result
        for seasonStats in allSeasonStats:
            result.append(seasonStats.seasonID)

        return result
