# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/utils/requesters/RankedRequester.py
import BigWorld
from adisp import async
from gui.shared.utils.requesters.abstract import AbstractSyncDataRequester
from skeletons.gui.shared.utils.requesters import IRankedRequester

class RankedRequester(AbstractSyncDataRequester, IRankedRequester):
    """
    Requester for data of ranked battles.
    """

    @property
    def accRank(self):
        """
        Current account rank.
        :return: (currentRank, currentStep)
        """
        return self.getCacheValue('accRank', (0, 0))

    @property
    def vehRanks(self):
        """
        Current vehicles ranks.
        :return: {vehTypeCompDescr: (rank, step)}
        """
        return self.getCacheValue('vehRanks', {})

    @property
    def clientRank(self):
        """
        Last rank for which client animation was shown.
        :return: (currentRank, currentStep)
        """
        return self.getCacheValue('clientRank', (0, 0))

    @property
    def clientVehRanks(self):
        """
        Last vehicle rank for which client animation was shown.
        :return: {vehTypeCompDescr: (rank, step)}
        """
        return self.getCacheValue('clientVehRanks', {})

    @property
    def season(self):
        """
        Current season stamp.
        :return: (seasonID, cycleID)
        """
        return self.getCacheValue('season', (-1, -1))

    @property
    def maxRank(self):
        """
        Maximum achieved rank and step
        :return: (rankNumber, stepNumber)
        """
        return self.getCacheValue('maxRank', (0, 0))

    @property
    def maxVehRanks(self):
        """
        Max vehicles ranks.
        :return: {vehTypeCompDescr: (rank, step)}
        """
        return self.getCacheValue('maxVehRanks', {})

    @property
    def ladderPoints(self):
        """
        Ladder points earned in current cycle
        """
        return self.getCacheValue('ladderPts', 0)

    @property
    def seasonLadderPts(self):
        """
        Ladder points earned in current season
        """
        return self.getCacheValue('seasonLadderPts', 0)

    @property
    def stepsCount(self):
        """
        Steps count in current cycle
        """
        return self.getCacheValue('stepsCount', 0)

    @property
    def seasonStepsCount(self):
        """
        Steps count in current season
        """
        return self.getCacheValue('seasonStepsCount', 0)

    @property
    def maxRankWithAwardReceived(self):
        """
        Returns max rank for which award window was shown
        """
        return self.getCacheValue('clientMaxRank', (0, 0))

    @property
    def shields(self):
        """
        Returns rank shields data
        :return: () -> {rankId: (currentHP, maxHP), ...}
        """
        return self.getCacheValue('shields', {})

    @property
    def clientShields(self):
        """
        Returns previous ranks shields data shown to user
        :return: () -> {rankId: (currentHP, maxHP), ...}
        """
        return self.getCacheValue('clientShields', {})

    @async
    def _requestCache(self, callback):
        BigWorld.player().ranked.getCache(lambda resID, value: self._response(resID, value, callback))

    def _preprocessValidData(self, data):
        return dict(data['ranked']) if 'ranked' in data else dict()
