# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/utils/requesters/game_restrictions_requester.py
import typing
import BigWorld
from adisp import adisp_async
from gui.shared.utils.requesters.abstract import AbstractSyncDataRequester
from skeletons.gui.shared.utils.requesters import IGameRestrictionsRequester

class GameRestrictionsRequester(AbstractSyncDataRequester, IGameRestrictionsRequester):

    @property
    def session(self):
        return self.getCacheValue('session', {})

    @property
    def hasSessionLimit(self):
        return len(self.session) > 0

    def getKickAt(self):
        return self.getCacheValue('session', {}).get('kick_at', 0)

    @property
    def settings(self):
        return self.getCacheValue('settings', {})

    @adisp_async
    def _requestCache(self, callback):
        BigWorld.player().gameRestrictions.getCache(lambda resID, value: self._response(resID, value, callback))
