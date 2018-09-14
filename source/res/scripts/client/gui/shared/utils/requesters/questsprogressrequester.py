# Embedded file name: scripts/client/gui/shared/utils/requesters/QuestsProgressRequester.py
import BigWorld
from adisp import async
from abstract import AbstractRequester

class QuestsProgressRequester(AbstractRequester):

    def getQuestProgress(self, qID):
        return self.__getQuestsData().get(qID, {}).get('progress')

    def getTokenCount(self, tokenID):
        tokenData = self.__getTokensData().get(tokenID, {})
        return tokenData.get('count', 0)

    @async
    def _requestCache(self, callback = None):
        BigWorld.player().questProgress.getCache(lambda resID, value: self._response(resID, value, callback))

    def __getQuestsData(self):
        return self.getCacheValue('quests', {})

    def __getTokensData(self):
        return self.getCacheValue('tokens', {})
