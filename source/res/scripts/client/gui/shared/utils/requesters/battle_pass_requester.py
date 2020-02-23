# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/utils/requesters/battle_pass_requester.py
import BigWorld
from adisp import async
from gui.shared.utils.requesters.abstract import AbstractSyncDataRequester

class BattlePassRequester(AbstractSyncDataRequester):

    def getSeasonID(self):
        return self.getCacheValue('seasonID', 0)

    def getPoints(self):
        return self.getCacheValue('sumPoints', 0)

    def getCurrentLevel(self):
        return self.getCacheValue('level', 0)

    def getState(self):
        return self.getCacheValue('state', 0)

    def getBoughtLevels(self):
        return self.getCacheValue('boughtLevels', 0)

    def getVoteOption(self):
        return self.getCacheValue('voteOption', 0)

    def getPointsForVehicle(self, vehicleID, default=0):
        return self.getCacheValue('vehiclePoints', {}).get(vehicleID, default)

    def _preprocessValidData(self, data):
        return dict(data.get('battlePass', {}))

    @async
    def _requestCache(self, callback):
        BigWorld.player().battlePass.getCache(lambda resID, value: self._response(resID, value, callback))
