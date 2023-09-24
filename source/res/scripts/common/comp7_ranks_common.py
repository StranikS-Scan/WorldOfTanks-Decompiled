# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/comp7_ranks_common.py
import enum
from typing import Optional, FrozenSet, Tuple
from cache import cached_property
from intervals import Interval
from soft_exception import SoftException
COMP7_MASCOT_ID = 3
COMP7_SEASON_IDX = 1
COMP7_RATING_ENTITLEMENT_TMPL = 'comp7_rating_points'
COMP7_RATING_ENTITLEMENT = 'comp7_rating_points:{}:{}'.format(COMP7_MASCOT_ID, COMP7_SEASON_IDX)
COMP7_ELITE_ENTITLEMENT = 'comp7_elite_rank:{}:{}'.format(COMP7_MASCOT_ID, COMP7_SEASON_IDX)
COMP7_ACTIVITY_ENTITLEMENT = 'comp7_activity_points:{}:{}'.format(COMP7_MASCOT_ID, COMP7_SEASON_IDX)
COMP7_ENTITLEMENT_EXPIRES = None
EXTRA_RANK_TAG = 'extra'
COMP7_UNDEFINED_RANK_ID = 0
COMP7_UNDEFINED_DIVISION_ID = 0

class Comp7Division(object):
    __slots__ = ('range', 'tags', 'rank', 'dvsnID', 'index', 'activityPointsPerBattle', 'hasRankInactivity')

    def __init__(self, dvsnDict):
        pointsRange = dvsnDict['range']
        self.range = pointsRange if type(pointsRange) is Interval else Interval(*pointsRange)
        self.rank = dvsnDict['rank']
        self.dvsnID = dvsnDict['id']
        self.index = dvsnDict['index']
        self.tags = frozenset(dvsnDict.get('tags', ()))
        self.activityPointsPerBattle = dvsnDict['rankInactivity']['activityPointsPerBattle'] if 'rankInactivity' in dvsnDict else 0
        self.hasRankInactivity = dvsnDict.get('hasRankInactivity', False)

    def __cmp__(self, other):
        if not isinstance(other, Comp7Division):
            raise TypeError
        return cmp(self.rank, other.rank) or cmp(self.range, other.range)

    def __repr__(self):
        return '{}[{}]'.format(self.__class__.__name__, {s:getattr(self, s) for s in self.__slots__})


class Comp7Rank(object):
    __slots__ = ('id', 'name')

    def __init__(self, rankDict):
        self.id = rankDict['id']
        self.name = rankDict.get('name')

    @property
    def index(self):
        return self.id


class Comp7RanksConfig(object):

    def __init__(self, config):
        self._config = config

    @cached_property
    def divisions(self):
        divs = []
        for dvsnDict in self._config.get('divisions', ()):
            division = Comp7Division(dvsnDict)
            divs.append(division)

        return tuple(divs)

    @cached_property
    def ranks(self):
        ranks = self._config.get('ranks', {})
        ranksOrder = self._config.get('ranksOrder', ())
        return tuple((Comp7Rank(ranks[rankID]) for rankID in ranksOrder))

    def getDivisionByRating(self, points, hasEliteEntitlement):
        eliteDiv = self.eliteDivision
        if hasEliteEntitlement and points in eliteDiv.range:
            return eliteDiv
        for division in self.divisions:
            if points in division.range:
                return division

        raise SoftException('Comp7: No ranks configured for {}'.format(points))

    def getStartRatingForDivision(self, divisionSerialIdx):
        if not 0 <= divisionSerialIdx < len(self.divisions):
            raise SoftException('Comp7: Invalid division serial index', divisionSerialIdx)
        division = self.divisions[divisionSerialIdx]
        return division.range.begin

    @cached_property
    def eliteDivision(self):
        return self.divisions[-1]

    def getActivityPointsForBattle(self, rank, divisionIdx):
        for division in self.divisions:
            if division.rank == rank and division.index == divisionIdx:
                return division.activityPointsPerBattle


def checkIfRatingEnt(entCode):
    return entCode.startswith(COMP7_RATING_ENTITLEMENT_TMPL)


def parseRatingEnt(entCode):
    if not checkIfRatingEnt(entCode):
        return (None, None)
    else:
        _, mascotID, index = entCode.split(':', 3)
        return (int(mascotID), int(index))


def makeRatingEntForSeason(seasonNumber):
    return ':'.join([COMP7_RATING_ENTITLEMENT_TMPL, str(COMP7_MASCOT_ID), seasonNumber])


class Comp7EntitlementCodes(object):
    LEGEND_RANK = 'legendRank'
    RATING_POINTS = 'ratingPoints'
    ACTIVITY_POINTS = 'activityPoints'
    SEASON_POINTS = 'seasonPoints'
    ALL = (LEGEND_RANK,
     RATING_POINTS,
     ACTIVITY_POINTS,
     SEASON_POINTS)
