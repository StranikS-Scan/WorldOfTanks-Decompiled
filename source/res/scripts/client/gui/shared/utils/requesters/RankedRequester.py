# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/utils/requesters/RankedRequester.py
import BigWorld
from adisp import async
from gui.shared.utils.requesters.abstract import AbstractSyncDataRequester
from skeletons.gui.shared.utils.requesters import IRankedRequester

class RankedRequester(AbstractSyncDataRequester, IRankedRequester):

    @property
    def accRank(self):
        return self.getCacheValue('accRank', (0, 0))

    @property
    def vehRanks(self):
        return self.getCacheValue('vehRanks', {})

    @property
    def clientRank(self):
        return self.getCacheValue('clientRank', (0, 0))

    @property
    def clientVehRanks(self):
        return self.getCacheValue('clientVehRanks', {})

    @property
    def season(self):
        return self.getCacheValue('season', (-1, -1))

    @property
    def maxRank(self):
        return self.getCacheValue('maxRank', (0, 0))

    @property
    def maxVehRanks(self):
        return self.getCacheValue('maxVehRanks', {})

    @property
    def ladderPoints(self):
        return self.getCacheValue('ladderPts', 0)

    @property
    def seasonLadderPts(self):
        return self.getCacheValue('seasonLadderPts', 0)

    @property
    def stepsCount(self):
        return self.getCacheValue('stepsCount', 0)

    @property
    def seasonStepsCount(self):
        return self.getCacheValue('seasonStepsCount', 0)

    @property
    def maxRankWithAwardReceived(self):
        return self.getCacheValue('clientMaxRank', (0, 0))

    @property
    def shields(self):
        return self.getCacheValue('shields', {})

    @property
    def clientShields(self):
        return self.getCacheValue('clientShields', {})

    @async
    def _requestCache(self, callback):
        BigWorld.player().ranked.getCache(lambda resID, value: self._response(resID, value, callback))

    def _preprocessValidData(self, data):
        return dict(data['ranked']) if 'ranked' in data else dict()
