# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/utils/requesters/BattleRoyaleRequester.py
import BigWorld
from adisp import async
from gui.shared.utils.requesters.abstract import AbstractSyncDataRequester
from skeletons.gui.shared.utils.requesters import IBattleRoyaleRequester

class BattleRoyaleRequester(AbstractSyncDataRequester, IBattleRoyaleRequester):

    @property
    def accTitle(self):
        return self.getCacheValue('accBRTitle', (0, 0))

    @property
    def maxTitle(self):
        return self.getCacheValue('maxAchievedBRTitle', (0, 0))

    @property
    def battlesAmount(self):
        return self.getCacheValue('BRBattlesCount', 0)

    @property
    def top1SoloAmount(self):
        return self.getCacheValue('BRSoloTop1Count', 0)

    @property
    def top1SquadAmount(self):
        return self.getCacheValue('BRSquadTop1Count', 0)

    @property
    def killsAmount(self):
        return self.getCacheValue('BRTotalKills', 0)

    @property
    def maxKillsCount(self):
        return self.getCacheValue('BRMaxKills', 0)

    @async
    def _requestCache(self, callback):
        BigWorld.player().battleRoyale.getCache(lambda resID, value: self._response(resID, value, callback))

    def _preprocessValidData(self, data):
        return dict(data['battleRoyale']) if 'battleRoyale' in data else dict()
