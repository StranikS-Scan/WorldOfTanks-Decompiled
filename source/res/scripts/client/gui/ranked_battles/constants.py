# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/ranked_battles/constants.py
import sys
from gui.Scaleform.genConsts.RANKEDBATTLES_CONSTS import RANKEDBATTLES_CONSTS
from gui.shared.money import Currency
from shared_utils import CONST_CONTAINER

class RANK_TYPES(object):
    ACCOUNT = 'account'
    VEHICLE = 'vehicle'


RANKED_QUEST_ID_PREFIX = 'ranked'
YEAR_POINTS_TOKEN = 'rb2019'

class YearAwardsNames(CONST_CONTAINER):
    SMALL = RANKEDBATTLES_CONSTS.RANKED_REWARDS_YEAR_SMALL
    MEDIUM = RANKEDBATTLES_CONSTS.RANKED_REWARDS_YEAR_MEDIUM
    BIG = RANKEDBATTLES_CONSTS.RANKED_REWARDS_YEAR_BIG
    LARGE = RANKEDBATTLES_CONSTS.RANKED_REWARDS_YEAR_LARGE


YEAR_AWARDS_POINTS_MAP = {YearAwardsNames.SMALL: (3, 6),
 YearAwardsNames.MEDIUM: (7, 9),
 YearAwardsNames.BIG: (10, 14),
 YearAwardsNames.LARGE: (15, sys.maxint)}
YEAR_AWARDS_ORDER = (YearAwardsNames.SMALL,
 YearAwardsNames.MEDIUM,
 YearAwardsNames.BIG,
 YearAwardsNames.LARGE)

class PRIME_TIME_STATUS(object):
    DISABLED = 0
    NOT_SET = 1
    FROZEN = 2
    NO_SEASON = 3
    NOT_AVAILABLE = 4
    AVAILABLE = 5


ZERO_RANK_ID = 0
AWARDS_ORDER = ['battleToken',
 'items',
 Currency.CREDITS,
 'premium',
 Currency.GOLD,
 Currency.CRYSTAL,
 'oneof']
DEFAULT_REWARDS_COUNT = 7

class RankedDossierKeys(object):
    ARCHIVE = 'Archive'
    SEASON = 'Season%s'


ARCHIVE_SEASON_ID = 0
