# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/utils/requesters/rts_statistics_requester.py
import BigWorld
from adisp import async
from gui.shared.utils.requesters.abstract import AbstractSyncDataRequester
from skeletons.gui.shared.utils.requesters import IRtsStatisticsRequester

class RtsStatisticsRequester(AbstractSyncDataRequester, IRtsStatisticsRequester):

    def getRts1x7(self):
        return self.getCacheValue('rts_1x7', {})

    def getRts1x1(self):
        return self.getCacheValue('rts_1x1', {})

    def getTankist(self):
        return self.getCacheValue('tankist', {})

    def _preprocessValidData(self, data):
        return dict(data.get('rtsStatistics', {}))

    @async
    def _requestCache(self, callback):
        BigWorld.player().rtsStatistics.getCache(lambda resID, value: self._response(resID, value, callback))
