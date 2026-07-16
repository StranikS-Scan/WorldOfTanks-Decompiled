# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/challenges/challenge_item.py
from __future__ import absolute_import
import logging
import typing
from account_helpers.AccountSettings import ChallengesMissions
from helpers import dependency, time_utils
from gui.challenges.challenges_helpers import TIME_BEFORE_END_OF_EXPIRATION, getSettings
from gui.impl import backport
from gui.impl.gen import R
from shared_utils import first
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from typing import Iterator, List
    from challenges_common import ChallengeConfig, ChallengeTypes, ChallengeDifficulties, ChallengeMainRewardTypes
    from gui.server_events.event_items import Quest
_logger = logging.getLogger(__name__)

class ChallengeItem(object):
    __itemsCache = dependency.descriptor(IItemsCache)
    __eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self, config):
        self.config = config

    @property
    def challengeID(self):
        return self.config.challengeID

    @property
    def isAvailable(self):
        return self.config.isAvailable(time_utils.getServerUTCTime())

    @property
    def difficulty(self):
        return self.config.difficulty

    @property
    def priority(self):
        return self.config.priority

    @property
    def challengeType(self):
        return self.config.challengeType

    @property
    def startTime(self):
        return self.config.startTime

    @property
    def finishTime(self):
        return self.config.finishTime

    @property
    def expireTime(self):
        return max(self.finishTime + time_utils.ONE_MINUTE - time_utils.getServerUTCTime(), 0)

    @property
    def isExpiringSoon(self):
        return self.isAvailable and self.expireTime <= TIME_BEFORE_END_OF_EXPIRATION

    @property
    def allowedCompletions(self):
        return self.config.allowedCompletions

    @property
    def freeRestartsPerCompletion(self):
        return self.config.freeRestartsPerCompletion

    @property
    def attempts(self):
        return self.config.attempts

    @property
    def questsIDs(self):
        return self.config.quests

    @property
    def usedFreeRestarts(self):
        return self.__itemsCache.items.challenges.getUsedFreeRestarts(self.challengeID)

    @property
    def isVisited(self):
        return self.challengeID in getSettings(ChallengesMissions.VISITED_CHALLENGES, set())

    @property
    def restartPrice(self):
        return self.config.restartPrice

    @property
    def name(self):
        questID = first(self.questsIDs)
        challengeName = backport.text(R.strings.user_missions.hub.challenge_missions.name.default())
        if questID is not None:
            quest = self.__eventsCache.getHiddenQuests(lambda q: q.getID() == questID).get(questID)
            if quest is not None:
                challengeName = quest.getUserName()
        return challengeName

    @property
    def mainRewardType(self):
        return self.config.mainRewardType

    def getTokenID(self, tokenType):
        return self.config.getTokenID(tokenType)

    def iterQuests(self):
        questIDs = self.questsIDs
        quests = self.__eventsCache.getHiddenQuests(lambda q: q.getID() in questIDs)
        for questID in questIDs:
            if questID in quests:
                yield quests[questID]
            _logger.error('Challenge quest %s is missing in eventsCache!', questID)
