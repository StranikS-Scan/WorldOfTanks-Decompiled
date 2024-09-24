# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/utils/requesters/game_restrictions_requester.py
import typing
import BigWorld
from adisp import adisp_async
from constants import RESTRICTION_KEY
from gui.shared.utils.requesters.abstract import AbstractSyncDataRequester
from skeletons.gui.shared.utils.requesters import IGameRestrictionsRequester

class GameRestrictionsRequester(AbstractSyncDataRequester, IGameRestrictionsRequester):

    @property
    def session(self):
        return self.getCacheValue(RESTRICTION_KEY.SESSION) or {}

    @property
    def hasSessionLimit(self):
        return len(self.session) > 0

    def getKickAt(self):
        return self.session.get('kick_at', 0)

    @property
    def settings(self):
        return self.getCacheValue(RESTRICTION_KEY.SETTINGS) or {}

    @property
    def privateChat(self):
        return self.getCacheValue(RESTRICTION_KEY.PRIVATE_CHAT) or {}

    @adisp_async
    def _requestCache(self, callback):
        BigWorld.player().gameRestrictions.getCache(lambda resID, value: self._response(resID, value, callback))
