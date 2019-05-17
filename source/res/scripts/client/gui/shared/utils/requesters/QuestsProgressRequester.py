# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/utils/requesters/QuestsProgressRequester.py
from collections import namedtuple
import BigWorld
import personal_missions
from adisp import async
from gui.shared.utils.requesters.abstract import AbstractSyncDataRequester
from skeletons.gui.shared import IItemsCache
from helpers import dependency
_Token = namedtuple('_Token', ('expireTime', 'count'))

class _QuestsProgressRequester(AbstractSyncDataRequester):
    itemsCache = dependency.descriptor(IItemsCache)

    def getTokenCount(self, tokenID):
        return self.__getToken(tokenID).count

    def getTokenExpiryTime(self, tokenID):
        return self.__getToken(tokenID).expireTime

    def getTokenNames(self):
        tokens = self.getTokensData()
        return tokens.keys()

    def getTokensData(self):
        return self.itemsCache.items.tokens.getTokens()

    @async
    def _requestCache(self, callback=None):
        BigWorld.player().questProgress.getCache(lambda resID, value: self._response(resID, value, callback))

    def __getToken(self, tokenID):
        return _Token(*self.getTokensData().get(tokenID, (0, 0)))


class QuestsProgressRequester(_QuestsProgressRequester):

    def getQuestProgress(self, qID):
        return self.getQuestsData().get(qID, {}).get('progress')

    def hasQuestDelayedRewards(self, qID):
        return qID in self.__getQuestsRewards()

    def getQuestsData(self):
        return self.getCacheValue('quests', {})

    def __getQuestsRewards(self):
        return self.getCacheValue('questsRewards', {})


class PersonalMissionsProgressRequester(_QuestsProgressRequester):
    PersonalMissionProgress = namedtuple('PersonalMissionProgress', ['state',
     'flags',
     'selected',
     'unlocked',
     'pawned'])
    _DefaultLastWomanIDs = (-1, -1, -1)

    def __init__(self, questsType):
        super(PersonalMissionsProgressRequester, self).__init__()
        self.__pmStorage = None
        self._questsType = questsType
        return

    def getPersonalMissionProgress(self, pqType, personalMissionID):
        personalMissionsProgress = self.__getQuestsData()
        if personalMissionsProgress:
            flags, state = self.__pmStorage.get(personalMissionID)
            return self.PersonalMissionProgress(state, flags, personalMissionID in personalMissionsProgress['selected'], pqType.maySelectQuest(self.__pmStorage.unlockedPQIDs()), self.getTokenCount(pqType.mainAwardListQuestID) > 0)
        return self.PersonalMissionProgress(personal_missions.PM_STATE.NONE, (), 0, False)

    def getConditionsProgress(self, conditionsProgressID):
        return self.__getConditionsProgress().get(conditionsProgressID, {})

    def getPersonalMissionsStorage(self):
        return self.__pmStorage

    def getPersonalMissionsFreeSlots(self, removedCount=0):
        pqProgress = self.__getQuestsData()
        return pqProgress['slots'] - len(pqProgress['selected']) + removedCount if pqProgress else 0

    def getSelectedPersonalMissionsIDs(self):
        pqProgress = self.__getQuestsData()
        return self.__getQuestsData()['selected'] if pqProgress else []

    def getTankmanLastIDs(self, nationID):
        pqProgress = self.__getQuestsData()
        return self.__getQuestsData()['lastIDs'].get(nationID, self._DefaultLastWomanIDs) if pqProgress else self._DefaultLastWomanIDs

    def _response(self, resID, value, callback=None):
        if value is not None:
            self.__pmStorage = personal_missions.PMStorage(value['potapovQuests']['compDescr'])
        super(_QuestsProgressRequester, self)._response(resID, value, callback)
        return

    def __getPersonalMissionsData(self):
        return self.getCacheValue('potapovQuests', {})

    def __getConditionsProgress(self):
        return self.getCacheValue('pm2_progress', {})

    def __getQuestsData(self):
        return self.__getPersonalMissionsData().get(self._questsType, {})
