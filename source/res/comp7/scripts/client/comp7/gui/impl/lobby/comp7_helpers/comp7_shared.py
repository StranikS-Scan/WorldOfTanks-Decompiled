# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/lobby/comp7_helpers/comp7_shared.py
import typing
from gui.shared.utils.requesters import REQ_CRITERIA
from shared_utils import findFirst
from comp7.gui.impl.gen.view_models.views.lobby.enums import Division, Rank
from helpers import dependency
from skeletons.gui.game_control import IComp7Controller
if typing.TYPE_CHECKING:
    from comp7_ranks_common import Comp7Division
    from comp7.helpers.comp7_server_settings import Comp7RanksConfig
    from gui.shared.utils.requesters import RequestCriteria

def getDivisionEnumValue(division):
    return tuple(Division)[division.index - 1] if division is not None else None


def getRankEnumValue(division):
    return tuple(Rank)[division.rank - 1]


def getRankById(rankId):
    return Rank(rankId)


@dependency.replace_none_kwargs(comp7Controller=IComp7Controller)
def getRating(comp7Controller=None):
    return comp7Controller.rating


@dependency.replace_none_kwargs(comp7Controller=IComp7Controller)
def isElite(seasonNumber=None, comp7Controller=None):
    return comp7Controller.isEliteForSeason(seasonNumber)


@dependency.replace_none_kwargs(comp7Controller=IComp7Controller)
def isQualification(comp7Controller=None):
    return comp7Controller.isQualificationActive()


@dependency.replace_none_kwargs(comp7Controller=IComp7Controller)
def getPlayerDivisionByRating(rating, seasonNumber=None, comp7Controller=None):
    ranksConfig = comp7Controller.getRanksConfig()
    division = findFirst(lambda d: rating in d.range, ranksConfig.divisions if not isElite(seasonNumber) else reversed(ranksConfig.divisions))
    return division


@dependency.replace_none_kwargs(comp7Controller=IComp7Controller)
def getPlayerDivisionByRankAndIndex(rank, divisionIdx, comp7Controller=None):
    ranksConfig = comp7Controller.getRanksConfig()
    division = findFirst(lambda d: d.index == divisionIdx, ranksConfig.divisionsByRank[rank])
    return division


def getPlayerDivision():
    rating = getRating()
    return getPlayerDivisionByRating(rating)


@dependency.replace_none_kwargs(comp7Controller=IComp7Controller)
def hasRankInactivity(rank, comp7Controller=None):
    isRankInactivityAvailable = comp7Controller.isAvailable() and comp7Controller.hasActiveSeason() and not comp7Controller.isOffline
    if not isRankInactivityAvailable:
        return False
    ranksConfig = comp7Controller.getRanksConfig()
    return any((division.hasRankInactivity for division in ranksConfig.divisionsByRank[rank]))


@dependency.replace_none_kwargs(comp7Controller=IComp7Controller)
def hasPlayerRankInactivityWarning(comp7Controller=None):
    ranksConfig = comp7Controller.getRanksConfig()
    rankInactivityThreshold = ranksConfig.rankInactivityNotificationThreshold
    return getPlayerDivision().hasRankInactivity and comp7Controller.activityPoints <= rankInactivityThreshold


@dependency.replace_none_kwargs(comp7Controller=IComp7Controller)
def getRankByName(rankName, comp7Controller=None):
    config = comp7Controller.getRanksConfig()
    rank = findFirst(lambda rankData: rankData['name'].lower() == rankName.lower(), config.ranks.values())
    return Rank(rank['id'])


@dependency.replace_none_kwargs(comp7Controller=IComp7Controller)
def getRankOrder(rank, comp7Controller=None):
    config = comp7Controller.getRanksConfig()
    return config.ranksOrder.index(rank.value) + 1


def getComp7Criteria():
    comp7Criteria = REQ_CRITERIA.INVENTORY
    comp7Criteria |= ~REQ_CRITERIA.VEHICLE.MODE_HIDDEN
    comp7Criteria |= ~REQ_CRITERIA.VEHICLE.BATTLE_ROYALE
    comp7Criteria |= ~REQ_CRITERIA.VEHICLE.EVENT_BATTLE
    return comp7Criteria
