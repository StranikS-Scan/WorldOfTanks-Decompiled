# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/utils/requesters/BattleRoyaleRequester.py
import BigWorld
from adisp import async
from gui.shared.utils.requesters.abstract import AbstractSyncDataRequester
from skeletons.gui.shared.utils.requesters import IBattleRoyaleRequester

class BattleRoyaleRequester(AbstractSyncDataRequester, IBattleRoyaleRequester):

    @property
    def accTitle(self):
        return self.getCacheValue('accBRTitle', (1, 0))

    @property
    def battleCount(self):
        return self.getCacheValue('BRBattlesCount', 0)

    @property
    def killCount(self):
        return self.getCacheValue('BRTotalKills', 0)

    @property
    def topCount(self):
        return self.getCacheValue('BRSoloTop1Count') + self.getCacheValue('BRSquadTop1Count')

    @async
    def _requestCache(self, callback):
        BigWorld.player().battleRoyale.getCache(lambda resID, value: self._response(resID, value, callback))

    def _preprocessValidData(self, data):
        return dict(data['battleRoyale']) if 'battleRoyale' in data else dict()
