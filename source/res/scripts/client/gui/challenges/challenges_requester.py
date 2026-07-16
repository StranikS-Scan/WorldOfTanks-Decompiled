# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/challenges/challenges_requester.py
from __future__ import absolute_import
import BigWorld
from challenges_common import CHALLENGES_PDATA_KEY
from gui.shared.utils.requesters.abstract import AbstractSyncDataRequester
from skeletons.gui.shared.utils.requesters import IChallengesRequester

class ChallengesRequester(AbstractSyncDataRequester, IChallengesRequester):

    def getUsedFreeRestarts(self, challengeID):
        return self.getCacheValue(challengeID, {}).get('restartsUsed', 0)

    def _preprocessValidData(self, data):
        return dict(data.get(CHALLENGES_PDATA_KEY, {}))

    def _requestCache(self, callback=None):
        BigWorld.player().challenges.getCache(lambda resID, value: self._response(resID, value, callback))
