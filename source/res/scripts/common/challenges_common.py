# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/challenges_common.py
from __future__ import absolute_import
import time
from enum import Enum, unique
from future.utils import viewitems
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Dict, List, Optional, Set
CHALLENGES_PDATA_KEY = 'challenges'
CHALLENGES_QUEST_PREFIX = 'challenge:'
CHALLENGES_FAIL_QUEST_POSTFIX = ':fail'

class ChallengeTokenType(object):
    ACTIVE = 'active'
    ATTEMPT = 'attempt'
    QUEST = 'quest'
    WIN = 'win'
    ALL = (ACTIVE,
     ATTEMPT,
     QUEST,
     WIN)


class ChallengeTokenPrefixes(object):
    BASE = 'challenge:'
    ACTIVE = BASE + 'active:'
    ATTEMPT = BASE + 'attempt:'
    QUEST = BASE + 'quest:'
    WIN = BASE + 'win:'


CHALLENGE_TOKEN_TYPE_TO_PREFIX = {ChallengeTokenType.ACTIVE: ChallengeTokenPrefixes.ACTIVE,
 ChallengeTokenType.ATTEMPT: ChallengeTokenPrefixes.ATTEMPT,
 ChallengeTokenType.QUEST: ChallengeTokenPrefixes.QUEST,
 ChallengeTokenType.WIN: ChallengeTokenPrefixes.WIN}
CHALLENGE_MIN_VEHICLE_LEVEL = 6

class _Enum(Enum):

    @classmethod
    def hasValue(cls, value):
        return value in cls._value2member_map_

    @classmethod
    def makeValue(cls, value):
        return cls(value) if value in cls._value2member_map_ else None


@unique
class ChallengeTypes(_Enum):
    REGULAR = 'regular'
    SPECIAL = 'special'


@unique
class ChallengeDifficulties(_Enum):
    HARD = 1
    MEDIUM = 2
    EASY = 3


@unique
class ChallengeMainRewardTypes(_Enum):
    VEHICLE = 'vehicle'
    ATTACHMENTS_SET = 'attachments_set'
    STYLE_3D = 'style_3d'
    STYLE_2D = 'style_2d'
    CREW_MEMBER = 'crew_member'
    IMPROVED_EQUIPMENT = 'improved_equipment'
    GOLD = 'gold'
    CREDITS = 'credits'
    CRYSTAL = 'crystal'
    FREE_XP = 'freeXP'
    EQUIP_COIN = 'equipCoin'
    EMPTY = ''


class ChallengesConfig(object):

    def __init__(self, config):
        self._config = config
        self._challengesConfigs = {id_:ChallengeConfig(data) for id_, data in viewitems(self._config.get('challenges') or {})}
        self._challenges = set()
        self._enabledChallenges = set()
        self._specialChallenges = set()
        for challengeID, challengeConfig in viewitems(self._challengesConfigs):
            self._challenges.add(challengeID)
            if challengeConfig.isEnabled:
                self._enabledChallenges.add(challengeID)
            if challengeConfig.challengeType == ChallengeTypes.SPECIAL:
                self._specialChallenges.add(challengeID)

    @property
    def isEnabled(self):
        return self._config.get('isEnabled', False)

    @property
    def challengesIDs(self):
        return self._challenges

    @property
    def specialChallengesIDs(self):
        return self._specialChallenges

    @property
    def enabledChallengesIDs(self):
        return self._enabledChallenges

    @property
    def challengesConfigs(self):
        return self._challengesConfigs

    def getChallengeConfig(self, challengeID):
        return self._challengesConfigs.get(challengeID)


class ChallengeConfig(object):

    def __init__(self, config):
        self._config = config
        self._type = ChallengeTypes.makeValue(config.get('type')) or ChallengeTypes.REGULAR
        self._difficulty = ChallengeDifficulties.makeValue(config.get('difficulty')) or ChallengeDifficulties.EASY
        self._mainRewardType = ChallengeMainRewardTypes.makeValue(config.get('mainRewardType')) or ChallengeMainRewardTypes.EMPTY
        self._tokenIDs = None
        return

    @property
    def isEnabled(self):
        return self._config.get('isEnabled', False)

    @property
    def challengeID(self):
        return self._config.get('id', 0)

    @property
    def startTime(self):
        return self._config.get('startTime', 0)

    @property
    def finishTime(self):
        return self._config.get('finishTime', 0)

    @property
    def challengeType(self):
        return self._type

    @property
    def difficulty(self):
        return self._difficulty

    @property
    def mainRewardType(self):
        return self._mainRewardType

    @property
    def priority(self):
        return self._config.get('priority', 0)

    @property
    def allowedCompletions(self):
        return self._config.get('allowedCompletions', 0)

    @property
    def freeRestartsPerCompletion(self):
        return self._config.get('freeRestartsPerCompletion', 0)

    @property
    def restartPrice(self):
        return self._config.get('restartPrice') or {'credits': 0}

    @property
    def attempts(self):
        return self._config.get('attempts', 0)

    @property
    def quests(self):
        return self._config.get('quests') or []

    @property
    def tokenIDs(self):
        if self._tokenIDs is None:
            self._tokenIDs = {tokenType:makeChallengeTokenID(tokenType, self.challengeID) for tokenType in ChallengeTokenType.ALL}
        return self._tokenIDs

    def getTokenID(self, tokenType):
        return self.tokenIDs.get(tokenType)

    def isAvailable(self, curTime=None):
        if curTime is None:
            curTime = int(time.time())
        return self.isEnabled and self.startTime <= curTime < self.finishTime


def isChallengeToken(tokenID):
    return tokenID.startswith(ChallengeTokenPrefixes.BASE)


def isChallengeQuest(questID):
    return questID.startswith(CHALLENGES_QUEST_PREFIX)


def isChallengeFailQuest(questID):
    return questID.startswith(CHALLENGES_QUEST_PREFIX) and questID.endswith(CHALLENGES_FAIL_QUEST_POSTFIX)


def makeChallengeFailQuestID(questID):
    return questID + CHALLENGES_FAIL_QUEST_POSTFIX


def makeChallengeTokenID(tokenType, challengeID):
    return CHALLENGE_TOKEN_TYPE_TO_PREFIX[tokenType] + str(challengeID)
