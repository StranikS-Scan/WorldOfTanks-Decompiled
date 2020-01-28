# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/utils/requesters/bob_requester.py
import BigWorld
from adisp import async
from gui.shared.utils.requesters.abstract import AbstractSyncDataRequester
from skeletons.gui.shared.utils.requesters import IBobRequester

class BobRequester(AbstractSyncDataRequester, IBobRequester):

    @property
    def teamToken(self):
        return self.bobData.get('team_token', '')

    @property
    def teamRank(self):
        return self.bobData.get('rank', 1)

    @property
    def teamScore(self):
        return self.bobData.get('score', 0)

    @property
    def activeSkill(self):
        return self.bobData.get('skill', '')

    @property
    def skillExpiresTime(self):
        return self.bobData.get('expires_at', 0)

    @property
    def bobData(self):
        return self.getCacheValue('bob', {})

    @async
    def _requestCache(self, callback):
        BigWorld.player().bob.getCache(lambda resID, value: self._response(resID, value, callback))
