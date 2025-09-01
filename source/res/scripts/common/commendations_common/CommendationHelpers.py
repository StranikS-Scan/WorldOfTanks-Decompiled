# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/commendations_common/CommendationHelpers.py
import typing
from collections import namedtuple
import BigWorld
from constants import CommendationsState, IS_CLIENT, ARENA_PERIOD
AVATAR_COMPONENT_NAME = 'commendations'
ARENA_COMPONENT_NAME = 'ArenaCommendationsMasterComponent'
ARENA_CONTROLLER_NAME = 'commendationsController'
TEAM_INFO_LIVETAGS_COMPONENT = 'liveTagsInfoComponent'

class CommendationsSource(object):
    EARS = 'ears'
    TAB_SCREEN = 'tab'
    CALLOUT = 'callout'


def canCommendNow(period):
    return period in (ARENA_PERIOD.PREBATTLE, ARENA_PERIOD.BATTLE)


CommendationStatistics = namedtuple('CommendationStatistics', 'received, sent')
if typing.TYPE_CHECKING:
    CommendationsStatisticsType = typing.Union[CommendationStatistics, typing.Tuple]

def getCommendationState(vehicleID):
    cmpt = getAvatarComponent(BigWorld.player())
    return cmpt.getMessageStateForVehID(vehicleID)


def getAvatarComponent(entity):
    return None if not entity else entity.dynamicComponents.get(AVATAR_COMPONENT_NAME, None)


def getArenaComponent(entity):
    return None if not entity else entity.components.get(ARENA_COMPONENT_NAME, None)


def getArenaController(entity):
    return None if not entity else entity.dynamicComponents.get(ARENA_CONTROLLER_NAME, None)


def getTeamInfoLiveTagsComponent(entity):
    return None if not entity else entity.dynamicComponents.get(TEAM_INFO_LIVETAGS_COMPONENT, None)


CommendationStateType = typing.Union[CommendationsState, int]
