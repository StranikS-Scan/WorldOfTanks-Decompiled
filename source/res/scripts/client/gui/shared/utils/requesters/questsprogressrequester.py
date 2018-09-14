# Embedded file name: scripts/client/gui/shared/utils/requesters/QuestsProgressRequester.py
from collections import namedtuple
import BigWorld
from debug_utils import LOG_DEBUG
import potapov_quests
from adisp import async
from gui.shared.utils.requesters.abstract import AbstractSyncDataRequester
_Token = namedtuple('_Token', ('expireTime', 'count'))

class _QuestsProgressRequester(AbstractSyncDataRequester):

    @async
    def _requestCache(self, callback = None):
        BigWorld.player().questProgress.getCache(lambda resID, value: self._response(resID, value, callback))


class QuestsProgressRequester(_QuestsProgressRequester):

    def getQuestProgress(self, qID):
        return self.__getQuestsData().get(qID, {}).get('progress')

    def getTokenCount(self, tokenID):
        return self.__getToken(tokenID).count

    def getTokenExpiryTime(self, tokenID):
        return self.__getToken(tokenID).expireTime

    def __getQuestsData(self):
        return self.getCacheValue('quests', {})

    def __getTokensData(self):
        return self.getCacheValue('tokens', {})

    def __getToken(self, tokenID):
        return _Token(*self.__getTokensData().get(tokenID, (0, 0)))


class _PotapovQuestsProgressRequester(_QuestsProgressRequester):
    PotapovQuestProgress = namedtuple('PotapovQuestProgress', ['state',
     'selected',
     'rewards',
     'unlocked'])

    def __init__(self, questsType):
        super(_PotapovQuestsProgressRequester, self).__init__()
        self.__pqStorage = None
        self._questsType = questsType
        return

    def getPotapovQuestProgress(self, pqType, potapovQuestID):
        potapovQuestsProgress = self.__getQuestsData()
        return self.PotapovQuestProgress(self.__pqStorage.get(potapovQuestID, (0, potapov_quests.PQ_STATE.NONE))[1], potapovQuestID in potapovQuestsProgress['selected'], potapovQuestsProgress['rewards'].get(potapovQuestID, {}), pqType.maySelectQuest(self.__pqStorage.keys()))

    def getPotapovQuestsStorage(self):
        return self.__pqStorage

    def getPotapovQuestsFreeSlots(self, removedCount = 0):
        pqProgress = self.__getQuestsData()
        return pqProgress['slots'] - len(pqProgress['selected']) + removedCount

    def getSelectedPotapovQuestsIDs(self):
        return self.__getQuestsData()['selected']

    def getTankmanLastIDs(self, nationID):
        return self.__getQuestsData()['lastIDs'].get(nationID, (-1, -1, -1))

    def _response(self, resID, value, callback):
        self.__pqStorage = potapov_quests.PQStorage(value['potapovQuests']['compDescr'])
        super(_QuestsProgressRequester, self)._response(resID, value, callback)

    def __getPotapovQuestsData(self):
        return self.getCacheValue('potapovQuests', {})

    def __getQuestsData(self):
        return self.__getPotapovQuestsData().get(self._questsType, {})


class RandomQuestsProgressRequester(_PotapovQuestsProgressRequester):

    def __init__(self):
        super(RandomQuestsProgressRequester, self).__init__('regular')


class FalloutQuestsProgressRequester(_PotapovQuestsProgressRequester):

    def __init__(self):
        super(FalloutQuestsProgressRequester, self).__init__('fallout')
