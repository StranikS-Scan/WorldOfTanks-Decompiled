# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/battle_results/rating_reward.py
import enum
import operator
from items import vehicles
from items.artefacts_helpers import VehicleFilter
from collections import namedtuple
from bisect import bisect
Bonus = namedtuple('Bonus', ['xp', 'credits'])

class AwardType(enum.Enum):
    DRAW = 0
    WIN = 1
    LOSE = 2


DEFAULT_BONUS = {result:Bonus(0, 0) for result in AwardType}

class _Award(object):

    def __init__(self, breakPoints=None, bonuses=None, filter=None):
        self._breakPoints = breakPoints or []
        self._bonuses = bonuses or [DEFAULT_BONUS]
        self._filter = filter

    def isAwardedVehicle(self, vehicleType):
        return self._filter is None or self._filter.checkCompatibilityWithVehType(vehicleType)

    def getBonus(self, place, awardType):
        return self._bonuses[bisect(self._breakPoints, place)][awardType]

    @staticmethod
    def _readAwardConfig(xmlCtx, section):
        filter = None
        if section.has_key('vehicleFilter'):
            filter = VehicleFilter.readVehicleFilter((xmlCtx, 'vehicleFilter'), section['vehicleFilter'])
        baseBonus = DEFAULT_BONUS
        table = {}
        for sname, subsection in section['places'].items():
            if sname == 'place':
                bonuses = DEFAULT_BONUS.copy()
                for result in AwardType:
                    if subsection.has_key(result.name.lower()):
                        bonusSec = subsection[result.name.lower()]
                        bonuses[result] = Bonus(xp=bonusSec.readInt('xp', 0), credits=bonusSec.readInt('credits', 0))

                placements = set()
                for part in subsection.readString('', '').split(','):
                    if '-' in part:
                        a, b = part.split('-')
                        placements.update(range(int(a), int(b) + 1))
                    if part:
                        placements.add(int(part))
                    baseBonus = bonuses

                for place in placements:
                    if place in table:
                        table[place] = {r:Bonus(*map(sum, zip(*[b, bonuses[r]]))) for r, b in table[place].items()}
                    table[place] = bonuses

        sorted_t = sorted(table.items(), key=operator.itemgetter(0))
        breakPoints = []
        bonuses = []
        if sorted_t:
            for idx, cur in enumerate(sorted_t[1:]):
                cur_p, cur_b = cur
                prv_p, prv_b = sorted_t[idx]
                if cur_p - prv_p != 1:
                    breakPoints.extend([prv_p + 1, cur_p])
                    bonuses.extend([prv_b, baseBonus])
                    continue
                if cur_b != prv_b:
                    breakPoints.append(prv_p + 1)
                    bonuses.append(prv_b)

            last_p, last_b = sorted_t[-1]
            breakPoints.append(last_p + 1)
            bonuses.append(last_b)
        bonuses.append(baseBonus)
        return _Award(breakPoints, bonuses, filter)


class AwardsList(object):

    def __init__(self, xmlCtx, section):
        self._awards = [ _Award._readAwardConfig((xmlCtx, 'AwardList'), subsec) for name, subsec in section.items() ]

    def getAwards(self, vehTypeCompDescr):
        return [ aw for aw in self._awards if aw.isAwardedVehicle(vehicles.getVehicleType(vehTypeCompDescr)) ]


def _readAwardList(section, config):
    config['awardList'] = AwardsList(None, section['awardLists'])
    return
