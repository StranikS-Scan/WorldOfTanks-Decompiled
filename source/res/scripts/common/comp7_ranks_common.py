# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/comp7_ranks_common.py
from typing import Optional, FrozenSet, Tuple
from cache import cached_property
from intervals import Interval
from soft_exception import SoftException
COMP7_RATING_ENTITLEMENT = 'comp7_rating_points:2023:1'
COMP7_ELITE_ENTITLEMENT = 'comp7_elite_rank:2023:1'
COMP7_ACTIVITY_ENTITLEMENT = 'comp7_activity_points:2023:1'
COMP7_ENTITLEMENT_EXPIRES = None
MAIN_RANK_NAME = 'main'
EXTRA_RANK_NAME = 'extra'

class Comp7Division(object):
    __slots__ = ('range', 'tags', 'rank', 'dvsnID', 'name', 'index', 'activityPointsPerBattle', 'hasRankInactivity')

    def __init__(self, dvsnDict):
        pointsRange = dvsnDict['range']
        self.range = pointsRange if type(pointsRange) is Interval else Interval(*pointsRange)
        self.rank = dvsnDict['rank']
        self.dvsnID = dvsnDict['id']
        self.name = dvsnDict['name']
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

    def getDivisionByRating(self, points, hasEliteEntitlement):
        eliteDiv = self.eliteDivision
        if hasEliteEntitlement and points in eliteDiv.range:
            return eliteDiv
        for division in self.divisions:
            if points in division.range:
                return division

        raise SoftException('Comp7: No ranks configured for {}'.format(points))

    @cached_property
    def eliteDivision(self):
        return self.divisions[-1]

    def getActivityPointsForBattle(self, rank, divisionIdx):
        for division in self.divisions:
            if division.rank == rank and division.index == divisionIdx:
                return division.activityPointsPerBattle
