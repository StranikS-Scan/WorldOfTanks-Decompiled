# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/utils/requesters/QuestsProgressRequester.py
from collections import namedtuple
import BigWorld
import personal_missions
from adisp import async
from gui.shared.utils.requesters.abstract import AbstractSyncDataRequester
_Token = namedtuple('_Token', ('expireTime', 'count'))

class _QuestsProgressRequester(AbstractSyncDataRequester):

    def getTokenCount(self, tokenID):
        return self.__getToken(tokenID).count

    def getTokenExpiryTime(self, tokenID):
        return self.__getToken(tokenID).expireTime

    @async
    def _requestCache(self, callback=None):
        BigWorld.player().questProgress.getCache(lambda resID, value: self._response(resID, value, callback))

    def __getTokensData(self):
        return self.getCacheValue('tokens', {})

    def __getToken(self, tokenID):
        return _Token(*self.__getTokensData().get(tokenID, (0, 0)))


class QuestsProgressRequester(_QuestsProgressRequester):

    def getQuestProgress(self, qID):
        return self.__getQuestsData().get(qID, {}).get('progress')

    def hasQuestDelayedRewards(self, qID):
        return qID in self.__getQuestsRewards()

    def __getQuestsData(self):
        return self.getCacheValue('quests', {})

    def __getQuestsRewards(self):
        return self.getCacheValue('questsRewards', {})


PersonalMissionProgress = namedtuple('PersonalMissionProgress', ('state', 'selected', 'unlocked', 'pawned'))

class _PersonalMissionsProgressRequester(_QuestsProgressRequester):

    def __init__(self, questsType):
        super(_PersonalMissionsProgressRequester, self).__init__()
        self.__pmStorage = None
        self._questsType = questsType
        return

    def getPersonalMissionProgress(self, pqType, personalMissionID):
        personalMissionsProgress = self.__getQuestsData()
        return PersonalMissionProgress(self.__pmStorage.get(personalMissionID, (0, personal_missions.PM_STATE.NONE))[1], personalMissionID in personalMissionsProgress['selected'], pqType.maySelectQuest(self.__pmStorage.keys()), self.getTokenCount(pqType.mainAwardListQuestID) > 0)

    def getPersonalMissionsStorage(self):
        return self.__pmStorage

    def getPersonalMissionsFreeSlots(self, removedCount=0):
        pqProgress = self.__getQuestsData()
        return pqProgress['slots'] - len(pqProgress['selected']) + removedCount

    def getSelectedPersonalMissionsIDs(self):
        return self.__getQuestsData()['selected']

    def getTankmanLastIDs(self, nationID):
        return self.__getQuestsData()['lastIDs'].get(nationID, (-1, -1, -1))

    def _response(self, resID, value, callback=None):
        if value is not None:
            self.__pmStorage = personal_missions.PMStorage(value['potapovQuests']['compDescr'])
        super(_QuestsProgressRequester, self)._response(resID, value, callback)
        return

    def __getPersonalMissionsData(self):
        return self.getCacheValue('potapovQuests', {})

    def __getQuestsData(self):
        return self.__getPersonalMissionsData().get(self._questsType, {})


class RandomQuestsProgressRequester(_PersonalMissionsProgressRequester):

    def __init__(self):
        super(RandomQuestsProgressRequester, self).__init__('regular')
