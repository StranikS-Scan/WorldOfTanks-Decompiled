# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/utils/requesters/session_progress_rewards_requester.py
import BigWorld
from adisp import adisp_async
from gui.shared.utils.requesters.abstract import AbstractSyncDataRequester
from session_progress_rewards_common import SESSION_PROGRESS_REWARDS_PDATA_KEY, CURRENT_STEP_PDATA_KEY, LAST_REWARD_GAME_DAY_PDATA_KEY
from skeletons.gui.shared.utils.requesters import ISessionProgressRewardsRequester

class SessionProgressRewardsRequester(AbstractSyncDataRequester, ISessionProgressRewardsRequester):

    def isCompleted(self):
        return not self._data

    def getCurrentStep(self):
        return self.getCacheValue(CURRENT_STEP_PDATA_KEY, defaultValue=0)

    def getLastRewardGameDay(self):
        return self.getCacheValue(LAST_REWARD_GAME_DAY_PDATA_KEY, defaultValue=0)

    def _preprocessValidData(self, data):
        return dict(data.get(SESSION_PROGRESS_REWARDS_PDATA_KEY, {}))

    @adisp_async
    def _requestCache(self, callback):
        BigWorld.player().sessionProgressRewards.getCache(lambda resID, value: self._response(resID, value, callback))
