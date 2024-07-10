# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/settings.py


class BATTLE_RESULTS_RECORD(object):
    ARENA_UNIQUE_ID = 'arenaUniqueID'
    COMMON = 'common'
    PERSONAL = 'personal'
    PLAYERS = 'players'
    VEHICLES = 'vehicles'
    AVATARS = 'avatars'
    TOP_LEVEL_RECORDS = (COMMON,
     PERSONAL,
     PLAYERS,
     VEHICLES,
     AVATARS)
    PERSONAL_AVATAR = 'avatar'
    COMMON_BOTS = 'bots'


class PREMIUM_STATE(object):
    NONE = 0
    HAS_ALREADY = 1
    BUY_ENABLED = 2
    BOUGHT = 4


class PROGRESS_ACTION(object):
    RESEARCH_UNLOCK_TYPE = 'UNLOCK_LINK_TYPE'
    PURCHASE_UNLOCK_TYPE = 'PURCHASE_LINK_TYPE'
    NEW_SKILL_UNLOCK_TYPE = 'NEW_SKILL_LINK_TYPE'
    NEW_FREE_SKILL_UNLOCK_TYPE = 'NEW_FREE_SKILL_LINK_TYPE'


class PLAYER_TEAM_RESULT(object):
    WIN = 'win'
    DEFEAT = 'lose'
    DRAW = 'tie'
    ENDED = 'ended'


class FACTOR_VALUE(object):
    BASE_CREDITS_FACTOR = 100
    BASE_XP_FACTOR = 100
    BASE_TMEN_XP_FACTOR = 100
    ADDITIONAL_BONUS_ZERO_FACTOR = 0
    ADDITIONAL_BONUS_ONE_FACTOR = 10


class EMBLEM_TYPE(object):
    CLAN = 1


class UI_VISIBILITY(object):
    SHOW_SQUAD = 1
    SHOW_RESOURCES = 2


class CurrenciesConstants(object):
    GOLD = 'gold'
    CREDITS = 'credits'
    CRYSTAL = 'crystal'
    XP_COST = 'xp'
    FREE_XP = 'freeXP'
    MULTY_XP = 'multyXp'
    MULTY_FREE_XP = 'multyFreeXp'
    TMEN_XP = 'tankmenXP'
