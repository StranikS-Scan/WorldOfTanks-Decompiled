# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/utils/requesters/RankedRequester.py
import BigWorld
from adisp import async
from gui.shared.utils.requesters.abstract import AbstractSyncDataRequester
from skeletons.gui.shared.utils.requesters import IRankedRequester

class RankedRequester(AbstractSyncDataRequester, IRankedRequester):

    @property
    def season(self):
        return self.getCacheValue('season', (-1, -1))

    @property
    def accRank(self):
        return self.getCacheValue('accRank', (0, 0))

    @property
    def maxRank(self):
        return self.getCacheValue('maxRank', (0, 0))

    @property
    def stepsCount(self):
        return self.getCacheValue('stepsCount', 0)

    @property
    def seasonStepsCount(self):
        return self.getCacheValue('seasonStepsCount', 0)

    @property
    def seasonEfficiencyStamp(self):
        return self.getCacheValue('currentEfficiency', {})

    @property
    def divisionsStats(self):
        return self.getCacheValue('divisions', {})

    @property
    def shields(self):
        return self.getCacheValue('shields', {})

    @property
    def persistentBonusBattles(self):
        return self.getCacheValue('bonusBattlesCount', 0)

    @property
    def dailyBonusBattles(self):
        return self.getCacheValue('dailyBonusBattlesCount', 0)

    @async
    def _requestCache(self, callback):
        BigWorld.player().ranked.getCache(lambda resID, value: self._response(resID, value, callback))

    def _preprocessValidData(self, data):
        return dict(data['ranked']) if 'ranked' in data else dict()
