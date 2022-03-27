# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/utils/requesters/QuestsProgressRequester.py
import functools
from collections import namedtuple
import copy
import logging
import typing
import BigWorld
import personal_missions
from account_helpers.AccountSettings import QUEST_DELTAS_PROGRESS, QUEST_DELTAS_COMPLETION
from adisp import async
from gui.server_events import events_helpers
from gui.shared.utils.requesters.quest_deltas_settings import QuestDeltasSettings
from gui.shared.utils.requesters.token import Token
from gui.shared.utils.requesters.abstract import AbstractSyncDataRequester
from gui.shared.utils.requesters.common import BaseDelta
from helpers import dependency
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from gui.server_events.event_items import Quest
_logger = logging.getLogger(__name__)

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
        return Token(*self.getTokensData().get(tokenID, (0, 0)))


class QuestsProgressRequester(_QuestsProgressRequester):

    def __init__(self):
        super(QuestsProgressRequester, self).__init__()
        self.__questProgressDelta = _QuestProgressDelta(functools.partial(QuestDeltasSettings, QUEST_DELTAS_PROGRESS))
        self.__questCompletion = _QuestCompletionDelta(functools.partial(QuestDeltasSettings, QUEST_DELTAS_COMPLETION))

    def getQuestCompletionChanged(self, questId):
        return self.__questCompletion.getQuestCompletionChanged(questId)

    def getQuestProgress(self, questId):
        return self.getQuestsData().get(questId, {}).get('progress')

    def getLastViewedProgress(self, questId):
        return self.__questProgressDelta.getPrevValue(questId)

    def hasQuestProgressed(self, questId):
        return self.__questProgressDelta.hasDiff(questId)

    def markQuestProgressAsViewed(self, questId):
        self.__questProgressDelta.updatePrevValueToCurrentValue(questId)
        self.__questCompletion.markVisited(questId)

    def hasQuestDelayedRewards(self, questId):
        return questId in self.__getQuestsRewards()

    def getQuestsData(self):
        return self.getCacheValue('quests', {})

    def clear(self):
        self.__questProgressDelta.clear()
        self.__questCompletion.clear()
        super(QuestsProgressRequester, self).clear()

    def _preprocessValidData(self, data):
        self.__questProgressDelta.update(data)
        self.__questCompletion.update(data)
        return data

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


class _QuestProgressDelta(BaseDelta):

    def _getDataIterator(self, data):
        for questId, quest in data.get('quests', {}).iteritems():
            yield (questId, copy.deepcopy(quest.get('progress', {})))

    def _getDefaultValue(self):
        return {}


class _QuestCompletionDelta(BaseDelta):

    @staticmethod
    def questFilter(quest):
        return events_helpers.isDailyQuest(quest.getID()) or events_helpers.isPremium(quest.getID()) or events_helpers.isRts(quest.getID())

    def _getDataIterator(self, data):
        events = self.eventsCache.getEvents(self.questFilter)
        for questId in data.get('quests', {}).keys():
            quest = events.get(questId)
            if quest:
                yield (questId, quest.isCompleted(data['quests'][questId]['progress']))

    def _getDefaultValue(self):
        return False

    def getQuestCompletionChanged(self, questId):
        return self.hasDiff(questId)

    def markVisited(self, questId):
        self.updatePrevValueToCurrentValue(questId)
