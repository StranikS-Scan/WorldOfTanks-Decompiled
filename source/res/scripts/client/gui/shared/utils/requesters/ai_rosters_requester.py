# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/utils/requesters/ai_rosters_requester.py
import typing
import BigWorld
from adisp import async
from gui.shared.utils.requesters.abstract import AbstractSyncDataRequester
from skeletons.gui.shared.utils.requesters import IAIRostersRequester

class AIRostersRequester(AbstractSyncDataRequester, IAIRostersRequester):

    def getRosters(self):
        return self._data

    def getRTSRoster(self, bonusType):
        return self.getCacheValue(bonusType, {})

    @async
    def _requestCache(self, callback):
        BigWorld.player().aiRosters.getCache(lambda resID, value: self._response(resID, value, callback))
