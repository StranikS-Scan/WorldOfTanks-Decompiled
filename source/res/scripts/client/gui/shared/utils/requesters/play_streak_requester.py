# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/utils/requesters/play_streak_requester.py
import BigWorld
from adisp import adisp_async
from account_helpers.play_streak import PS_PDATA_KEY
from gui.shared.utils.requesters.abstract import AbstractSyncDataRequester
from skeletons.gui.shared.utils.requesters import IPlayStreakRequester

class PlayStreakRequester(AbstractSyncDataRequester, IPlayStreakRequester):

    def getRedemptionDay(self):
        return self.getCacheValue('freezeDay')

    def getDailyConditionCompleted(self):
        return self.getCacheValue('dailyConditionCompleted')

    def _preprocessValidData(self, data):
        return dict(data.get(PS_PDATA_KEY, {}))

    @adisp_async
    def _requestCache(self, callback):
        BigWorld.player().playStreak.getCache(lambda resID, value: self._response(resID, value, callback))
