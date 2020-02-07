# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/ranked_battles/constants.py
from gui.Scaleform.genConsts.RANKEDBATTLES_CONSTS import RANKEDBATTLES_CONSTS
from gui.shared.money import Currency
from shared_utils import CONST_CONTAINER

class RankTypes(CONST_CONTAINER):
    ACCOUNT = 'account'
    VEHICLE = 'vehicle'


class YearAwardsNames(CONST_CONTAINER):
    SMALL = RANKEDBATTLES_CONSTS.RANKED_REWARDS_YEAR_SMALL
    MEDIUM = RANKEDBATTLES_CONSTS.RANKED_REWARDS_YEAR_MEDIUM
    BIG = RANKEDBATTLES_CONSTS.RANKED_REWARDS_YEAR_BIG
    LARGE = RANKEDBATTLES_CONSTS.RANKED_REWARDS_YEAR_LARGE


YEAR_AWARDS_ORDER = (YearAwardsNames.SMALL,
 YearAwardsNames.MEDIUM,
 YearAwardsNames.BIG,
 YearAwardsNames.LARGE)

class PrimeTimeStatus(CONST_CONTAINER):
    DISABLED = 0
    NOT_SET = 1
    FROZEN = 2
    NO_SEASON = 3
    NOT_AVAILABLE = 4
    AVAILABLE = 5


ZERO_RANK_ID = 0
ZERO_DIVISION_ID = 0
MAX_GROUPS_IN_DIVISION = 3
AWARDS_ORDER = ('battleToken',
 'items',
 Currency.CREDITS,
 'premium',
 Currency.GOLD,
 Currency.CRYSTAL)
YEAR_AWARDS_BONUS_ORDER = (Currency.CRYSTAL,
 'customizations',
 'items',
 'vehicles')
DEFAULT_REWARDS_COUNT = 7

class RankedDossierKeys(CONST_CONTAINER):
    ARCHIVE = 'Archive'
    SEASON = 'Season%s'


ARCHIVE_SEASON_ID = 0
STANDARD_POINTS_COUNT = 1
NOT_IN_LEAGUES_QUEST = 'ranked_{}_0_common'
FINAL_QUEST_PATTERN = 'ranked_{}_final'
RANKED_QUEST_ID_PREFIX = 'ranked'
YEAR_POINTS_TOKEN = 'rb2019'

class RankedTokenQuestPostfix(CONST_CONTAINER):
    COMMON = 'common'
    SPRINTER = 'sprinter'
    FINAL = 'final'


class SeasonResultTokenPatterns(CONST_CONTAINER):
    RANKED_OFF_BANNED = 'ranked_{}_banned'
    RANKED_OFF_SPRINTER = 'ranked_{}_sprinter'
    RANKED_OFF_GOLD_LEAGUE_TOKEN = 'ranked_{}_top_1'
    RANKED_OFF_SILVER_LEAGUE_TOKEN = 'ranked_{}_top_2'
    RANKED_OFF_BRONZE_LEAGUE_TOKEN = 'ranked_{}_top_3'


class SeasonGapStates(CONST_CONTAINER):
    WAITING_IN_LEAGUES = 0
    IN_LEAGUES = 1
    BANNED_IN_LEAGUES = 2
    WAITING_IN_DIVISIONS = 3
    IN_DIVISIONS = 4
    BANNED_IN_DIVISIONS = 5
    WAITING_NOT_IN_DIVISIONS = 6
    NOT_IN_DIVISIONS = 7
    BANNED_NOT_IN_DIVISIONS = 8
    WAITING_NOT_IN_SEASON = 9
    NOT_IN_SEASON = 10
    BANNED_NOT_IN_SEASON = 11
