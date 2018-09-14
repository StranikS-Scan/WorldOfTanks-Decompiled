# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/items/prb_items.py
from collections import namedtuple
from account_helpers import getAccountDatabaseID, getPlayerID
from constants import PREBATTLE_ACCOUNT_STATE, PREBATTLE_TEAM_STATE
from gui.prb_control.settings import PREBATTLE_PLAYERS_COMPARATORS
from gui.shared.gui_items.Vehicle import Vehicle

class PlayerPrbInfo(object):
    __slots__ = ('accID', 'name', 'dbID', 'state', 'time', 'vehCompDescr', 'igrType', 'clanDBID', 'clanAbbrev', 'roster', 'isCreator', 'regionCode')

    def __init__(self, accID, name='', dbID=0, state=PREBATTLE_ACCOUNT_STATE.UNKNOWN, time=0.0, vehCompDescr=0, igrType=0, clanDBID=0, clanAbbrev='', roster=0, entity=None):
        self.accID = accID
        self.name = name
        self.dbID = dbID
        self.state = state
        self.time = time
        self.vehCompDescr = vehCompDescr
        self.igrType = igrType
        self.clanDBID = clanDBID
        self.clanAbbrev = clanAbbrev
        self.roster = roster
        if entity is not None:
            self.isCreator = entity.isCommander(pDatabaseID=self.dbID)
        else:
            self.isCreator = False
        return

    def __repr__(self):
        return 'PlayerPrbInfo(accID = {0:n}, dbID = {1:n}, fullName = {2:>s}, state = {3:n}, isCreator = {4!r:s}, time = {5:n}, vehCompDescr = {6!r:s})'.format(self.accID, self.dbID, self.getFullName(), self.state, self.isCreator, self.time, self.getVehicle().name if self.isVehicleSpecified() else None)

    def getFullName(self, isClan=True, isRegion=True):
        if isClan:
            clanAbbrev = self.clanAbbrev
        else:
            clanAbbrev = None
        if isRegion:
            pDBID = self.dbID
        else:
            pDBID = None
        from gui.LobbyContext import g_lobbyContext
        return g_lobbyContext.getPlayerFullName(self.name, clanAbbrev=clanAbbrev, pDBID=pDBID)

    def isVehicleSpecified(self):
        return self.isReady() or self.inBattle()

    def getVehicle(self):
        return Vehicle(self.vehCompDescr)

    def isCurrentPlayer(self):
        if self.dbID > 0:
            result = self.dbID == getAccountDatabaseID()
        else:
            result = self.accID == getPlayerID()
        return result

    def isReady(self):
        return self.state & PREBATTLE_ACCOUNT_STATE.READY != 0

    def inBattle(self):
        return self.state & PREBATTLE_ACCOUNT_STATE.IN_BATTLE != 0

    def isOffline(self):
        return self.state & PREBATTLE_ACCOUNT_STATE.OFFLINE != 0


class TeamStateInfo(object):
    __slots__ = ('state',)

    def __init__(self, state):
        super(TeamStateInfo, self).__init__()
        self.state = state

    def __repr__(self):
        return 'TeamStateInfo(state = {0:n}, isNotReady = {1!r:s}, isReady = {2!r:s}, isLocked = {3!r:s}, isInQueue = {4:n}'.format(self.state, self.isNotReady(), self.isReady(), self.isLocked(), self.isInQueue())

    def isNotReady(self):
        return self.state is PREBATTLE_TEAM_STATE.NOT_READY

    def isReady(self):
        return self.state is PREBATTLE_TEAM_STATE.READY

    def isLocked(self):
        return self.state is PREBATTLE_TEAM_STATE.LOCKED

    def isInQueue(self):
        return self.state in [PREBATTLE_TEAM_STATE.READY, PREBATTLE_TEAM_STATE.LOCKED]


PlayersStateStats = namedtuple('PlayersStateStats', ('notReadyCount', 'haveInBattle', 'playersCount', 'limitMaxCount'))

class PrbPropsInfo(object):
    __slots__ = ('wins', 'battlesCount', 'createTime')

    def __init__(self, wins=None, battlesCount=0, createTime=None):
        super(PrbPropsInfo, self).__init__()
        self.wins = wins or [0, 0, 0]
        self.battlesCount = battlesCount
        self.createTime = createTime

    def getBattlesScore(self):
        return '%d:%d' % (self.wins[1], self.wins[2])

    def __repr__(self):
        return 'PrbPropsInfo(wins = {0!r:s}, battlesCount = {1:n}, createTime = {2:n}'.format(self.wins, self.battlesCount, self.createTime)


def getPlayersComparator(playerComparatorType=PREBATTLE_PLAYERS_COMPARATORS.REGULAR):
    """
    Sort criteria for players:
    mode PREBATTLE_PLAYERS_COMPARATORS.REGULAR:
    1. time of accession (common criteria).
    2. first in the list is commander.
    mode PREBATTLE_PLAYERS_COMPARATORS.OBSERVERS_TO_BOTTOM:
    1. time of accession (common criteria).
    2. observers sorts to bottom list.
    
    Args:
        playerComparatorType: PREBATTLE_PLAYERS_COMPARATORS type
    
    Returns:
        cmp function according to PREBATTLE_PLAYERS_COMPARATORS type request
    """

    def comparator(player, other):
        if player.isCreator ^ other.isCreator:
            result = -1 if player.isCreator else 1
        else:
            result = cmp(player.time, other.time)
        return result

    def comparator_observers_to_bottom(player, other):
        player_is_observer = player.isVehicleSpecified() and player.getVehicle().isObserver
        other_is_observer = other.isVehicleSpecified() and other.getVehicle().isObserver
        if player_is_observer ^ other_is_observer:
            result = 1 if player_is_observer else -1
        else:
            result = cmp(player.time, other.time)
        return result

    comparators = {PREBATTLE_PLAYERS_COMPARATORS.REGULAR: comparator,
     PREBATTLE_PLAYERS_COMPARATORS.OBSERVERS_TO_BOTTOM: comparator_observers_to_bottom}
    return comparators.get(playerComparatorType, comparator)
