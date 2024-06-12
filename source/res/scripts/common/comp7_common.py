# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/comp7_common.py
import enum
ROLE_EQUIPMENT_TAG = 'roleEquipment'
COMP7_QUEST_PREFIX = 'comp7_3_4'
COMP7_TOKEN_PREFIX = 'comp7_3_4'
COMP7_QUEST_DELIMITER = '_'
COMP7_TOKEN_WEEKLY_REWARD_ID = 'comp7_3_4_weekly_rewards_token'
COMP7_TOKEN_WEEKLY_REWARD_NAME = 'comp7TokenWeeklyReward'
COMP7_TOKEN_COUPON_REWARD_ID = 'comp7:coupon'
COMP7_TOKEN_COUPON_REWARD_NAME = 'comp7TokenCouponReward'
COMP7_QUALIFICATION_QUEST_ID = 'comp7_3_4_ranks_65'
COMP7_CURRENT_SEASON = 4
COMP7_MASKOT_ID = '4'
SEASONS_IN_YEAR = 4
COMP7_SEASON_POINTS_ENTITLEMENT_TMPL = 'comp7_season_points'

def seasonPointsCodeBySeasonNumber(seasonNumber):
    return ':'.join((COMP7_SEASON_POINTS_ENTITLEMENT_TMPL, COMP7_MASKOT_ID, str(seasonNumber)))


SEASON_POINTS_ENTITLEMENTS = [ seasonPointsCodeBySeasonNumber(n + 1) for n in range(SEASONS_IN_YEAR) ]

@enum.unique
class Comp7QuestType(enum.Enum):
    RANKS = 'ranks'
    TOKENS = 'token'
    PERIODIC = 'period'
    ACTIVITY = 'activity'
    WEEKLY = 'weekly'


CLIENT_VISIBLE_QUESTS_TYPE = (Comp7QuestType.TOKENS,
 Comp7QuestType.RANKS,
 Comp7QuestType.PERIODIC,
 Comp7QuestType.WEEKLY)

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
