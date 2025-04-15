# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/common/comp7_ranks_common.py
from typing import Optional, FrozenSet, Tuple, Dict
from cache import cached_property
from intervals import Interval
from soft_exception import SoftException
EXTRA_RANK_TAG = 'extra'
COMP7_UNDEFINED_RANK_ID = 0
COMP7_UNDEFINED_DIVISION_ID = 0
COMP7_UNDEFINED_DIVISION_SERIAL_IDX = 0

class Comp7Division(object):
    __slots__ = ('range', 'tags', 'rank', 'dvsnID', 'index', 'activityPointsPerBattle', 'hasRankInactivity', 'seasonPoints', 'serialIdx', 'ratingPointsPenalty')

    def __init__(self, serialIdx, divisionInfo):
        pointsRange = divisionInfo['range']
        self.range = pointsRange if isinstance(pointsRange, Interval) else Interval(*pointsRange)
        self.rank = divisionInfo['rank']
        self.dvsnID = divisionInfo['id']
        self.index = divisionInfo['index']
        self.tags = frozenset(divisionInfo.get('tags', ()))
        self.activityPointsPerBattle = divisionInfo.get('rankInactivity', {}).get('activityPointsPerBattle', 0)
        self.ratingPointsPenalty = divisionInfo.get('rankInactivity', {}).get('ratingPointsPenalty', 0)
        self.hasRankInactivity = divisionInfo.get('hasRankInactivity', False)
        self.seasonPoints = divisionInfo.get('seasonPoints', 0)
        self.serialIdx = serialIdx

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
        divisions = self._config.get('divisions', ())
        return tuple((Comp7Division(serialIdx, divisionInfo) for serialIdx, divisionInfo in enumerate(divisions)))

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
