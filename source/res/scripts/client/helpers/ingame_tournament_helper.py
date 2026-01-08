# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/helpers/ingame_tournament_helper.py
from enum import Enum

class IngameTournamentType(Enum):
    WCI = 'wci'
    OLS = 'ols'


class IngameTournamentState(Enum):
    INTRO = 'tournament_intro'
    IN_PROGRESS = 'tournament_in_live'
    BETWEEN_SHOWMATCHES = 'tournament_between_showmatch_days'
    FINISHED = 'tournament_finished'


class IngameTournamentBracketType(Enum):
    RR = 'RR'
    DE = 'DE'


class IngameTournamentMatchState(Enum):
    UPCOMING = 'upcoming'
    IN_LIVE = 'in_live'
    COMPLETED = 'completed'


class IngameTournamentUrlType(Enum):
    YOUTUBE = 'youtube'
    TWITCH = 'twitch'
    DOUYIN = 'douyin'
    HUYA = 'huya'


class IngameTournamentLogoSize(Enum):
    SMALL = '48x48'
    MEDIUM = '86x86'
    LARGE = '260x260'
    EXTRA_LARGE = '522x522'
