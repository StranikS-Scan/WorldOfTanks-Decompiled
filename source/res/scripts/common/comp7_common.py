# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/comp7_common.py
import enum
import re
ROLE_EQUIPMENT_TAG = 'roleEquipment'
__COMP7_QUEST_PREFIX = 'comp7'
__COMP7_MASKOT_ID = '4'
SEASONS_IN_YEAR = 3
__COMP7_QUALIFICATION_TOKEN_TEMPLATE = 'comp7_{maskot}_{season}:qualification'
__COMP7_QUALIFICATION_QUEST_ID_TEMPLATE = 'comp7_{maskot}_{season}_ranks_65'
__COMP7_RENT_VEHICLES_QUEST_ID_TEMPLATE = 'comp7_{maskot}_{season}_rent_vehicles'
__COMP7_TOKEN_PREFIX_TEMPLATE = 'comp7_{maskot}_{season}'
__COMP7_WEEKLY_REWARD_TOKEN_TEMPLATE = 'comp7_{maskot}_{season}_weekly_rewards_token'
__COMP7_SEASON_POINT_ASSET_TEMPLATE = 'comp7_season_points:{maskot}:{season}'
__COMP7_YEARLY_REWARD_TEMPLATE = 'comp7_{maskot}_yearly_reward'
__COMP7_SEASON_NAME_TEMPLATE = 'comp7_{maskot}_{season}'
__COMP7_SEASON_POINTS_ENTITLEMENT_TEMPLATE = 'comp7_season_points:{maskot}:{season}'
__COMP7_RATING_ENTITLEMENT_PREFIX = 'comp7_rating_points'
__COMP7_RATING_ENTITLEMENT_TEMPLATE = __COMP7_RATING_ENTITLEMENT_PREFIX + ':{maskot}:{season}'
__COMP7_ELITE_ENTITLEMENT_TEMPLATE = 'comp7_elite_rank:{maskot}:{season}'
__COMP7_ACTIVITY_ENTITLEMENT_TEMPLATE = 'comp7_activity_points:{maskot}:{season}'
__COMP7_MAX_RANK_ENTITLEMENT_TEMPLATE = 'comp7_max_achieved_rank:{maskot}:{season}'
COMP7_OFFER_PREFIX = 'offer:comp7_{}'.format(__COMP7_MASKOT_ID)
COMP7_OFFER_GIFT_PREFIX = '{}:deluxe_gift:'.format(COMP7_OFFER_PREFIX)
COMP7_WEEKLY_REWARD_TOKEN_REGEXP = re.compile(__COMP7_WEEKLY_REWARD_TOKEN_TEMPLATE.format(maskot='\\d', season='\\d'))
COMP7_ENTITLEMENT_EXPIRES = None
COMP7_YEARLY_REWARD_TOKEN = __COMP7_YEARLY_REWARD_TEMPLATE.format(maskot=__COMP7_MASKOT_ID)
COMP7_YEARLY_ACHIEVEMENT_PREFIX = 'comp7_{}_yearly'.format(__COMP7_MASKOT_ID)

def isComp7YearlyAchievement(achievementName):
    return achievementName.startswith(COMP7_YEARLY_ACHIEVEMENT_PREFIX)


def seasonPointsCodeBySeasonNumber(seasonNumber):
    return __COMP7_SEASON_POINTS_ENTITLEMENT_TEMPLATE.format(maskot=__COMP7_MASKOT_ID, season=seasonNumber)


def qualificationTokenBySeasonNumber(seasonNumber):
    return __COMP7_QUALIFICATION_TOKEN_TEMPLATE.format(maskot=__COMP7_MASKOT_ID, season=seasonNumber)


def seasonPointsAssetBySeasonNumber(seasonNumber):
    return __COMP7_SEASON_POINT_ASSET_TEMPLATE.format(maskot=__COMP7_MASKOT_ID, season=seasonNumber)


def qualificationQuestIDBySeasonNumber(seasonNumber):
    return __COMP7_QUALIFICATION_QUEST_ID_TEMPLATE.format(maskot=__COMP7_MASKOT_ID, season=seasonNumber)


def rentVehiclesQuestIDBySeasonNumber(seasonNumber):
    return __COMP7_RENT_VEHICLES_QUEST_ID_TEMPLATE.format(maskot=__COMP7_MASKOT_ID, season=seasonNumber)


def tokenPrefixBySeasonNumber(seasonNumber):
    return __COMP7_TOKEN_PREFIX_TEMPLATE.format(maskot=__COMP7_MASKOT_ID, season=seasonNumber)


def weeklyRewardTokenBySeasonNumber(seasonNumber):
    return __COMP7_WEEKLY_REWARD_TOKEN_TEMPLATE.format(maskot=__COMP7_MASKOT_ID, season=seasonNumber)


def ratingEntNameBySeasonNumber(seasonNumber):
    return __COMP7_RATING_ENTITLEMENT_TEMPLATE.format(maskot=__COMP7_MASKOT_ID, season=seasonNumber)


def eliteRankEntNameBySeasonNumber(seasonNumber):
    return __COMP7_ELITE_ENTITLEMENT_TEMPLATE.format(maskot=__COMP7_MASKOT_ID, season=seasonNumber)


def activityPointsEntNameBySeasonNumber(seasonNumber):
    return __COMP7_ACTIVITY_ENTITLEMENT_TEMPLATE.format(maskot=__COMP7_MASKOT_ID, season=seasonNumber)


def maxRankEntNameBySeasonNumber(seasonNumber):
    return __COMP7_MAX_RANK_ENTITLEMENT_TEMPLATE.format(maskot=__COMP7_MASKOT_ID, season=seasonNumber)


def seasonNameBySeasonNumber(seasonNumber):
    return __COMP7_SEASON_NAME_TEMPLATE.format(maskot=__COMP7_MASKOT_ID, season=seasonNumber)


SEASON_POINTS_ENTITLEMENTS = [ seasonPointsCodeBySeasonNumber(n + 1) for n in range(SEASONS_IN_YEAR) ]
SEASON_POINTS_ASSETS = [ seasonPointsAssetBySeasonNumber(n + 1) for n in range(SEASONS_IN_YEAR) ]

def parseRatingEnt(entCode):
    if not entCode.startswith(__COMP7_RATING_ENTITLEMENT_PREFIX):
        return (None, None)
    else:
        _, mascotID, index = entCode.split(':', 2)
        return (int(mascotID), int(index))


class Comp7EntitlementCodes(object):
    LEGEND_RANK = 'legendRank'
    RATING_POINTS = 'ratingPoints'
    ACTIVITY_POINTS = 'activityPoints'
    SEASON_POINTS = 'seasonPoints'
    ALL = (LEGEND_RANK,
     RATING_POINTS,
     ACTIVITY_POINTS,
     SEASON_POINTS)


@enum.unique
class Comp7QuestType(enum.Enum):
    RANKS = 'ranks'
    TOKENS = 'token_rewards'
    PERIODIC = 'period'
    ACTIVITY = 'activity'
    WEEKLY = 'weekly'


__ALL_QUEST_TYPES = [ qType.value for qType in Comp7QuestType ]
CLIENT_VISIBLE_QUESTS_TYPE = (Comp7QuestType.TOKENS,
 Comp7QuestType.RANKS,
 Comp7QuestType.PERIODIC,
 Comp7QuestType.WEEKLY)
COMP7_QUEST_ID_REGEXP = __COMP7_QUEST_PREFIX + '_(\\d)_(\\d)_({types})_(.+)'.format(types='|'.join(__ALL_QUEST_TYPES))

class BattleStatuses(object):
    STARTED = 0
    WIN = 1
    LOSE = 2
    DESERTER = 3
    FINISHED_WITH_ERROR = 4
    STARTED_RANGE = (STARTED,
     WIN,
     LOSE,
     DESERTER)
    FINISHED_RANGE = (WIN, LOSE, DESERTER)


class Comp7QualificationState(object):
    NOT_STARTED = 'not_started'
    IN_PROGRESS = 'in_progress'
    WAITING_BATTLE_RESULTS = 'wait_battle_results'
    FINALIZING = 'finalizing'
    COMPLETED = 'completed'
    states = (NOT_STARTED,
     IN_PROGRESS,
     WAITING_BATTLE_RESULTS,
     FINALIZING,
     COMPLETED)

    @classmethod
    def isBattleAllowed(cls, state):
        return state in (cls.IN_PROGRESS, cls.COMPLETED)

    @classmethod
    def isUnitAllowed(cls, state):
        return state == cls.COMPLETED

    @classmethod
    def isQualificationActive(cls, state):
        return state != cls.COMPLETED

    @classmethod
    def isResultsProcessing(cls, state):
        return state in (cls.WAITING_BATTLE_RESULTS, cls.FINALIZING)

    @classmethod
    def isCalculationQualificationRating(cls, state):
        return state in (Comp7QualificationState.NOT_STARTED,)
