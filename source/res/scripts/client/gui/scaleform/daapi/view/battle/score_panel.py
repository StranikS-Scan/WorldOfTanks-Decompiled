# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/score_panel.py
import BigWorld
from account_helpers.settings_core import g_settingsCore
from gui.Scaleform.daapi.view.battle.meta.FalloutScorePanelMeta import FalloutScorePanelMeta
from gui.battle_control import g_sessionProvider
from gui.Scaleform.daapi.view.battle import markerComparator, FALLOUT_SCORE_PANEL
from gui.battle_control.arena_info import isEventBattle

class _IScorePanel(object):

    def populate(self):
        pass

    def destroy(self):
        pass

    def clear(self, team = None):
        pass

    def addFrags(self, team, count = 1):
        pass

    def addKilled(self, team, count = 1):
        pass

    def addVehicle(self, team, vehicleID, vClassName, isAlive):
        pass

    def updateScore(self, playerTeam):
        pass

    def updateTeam(self, isEnemy, team):
        pass

    def showVehiclesCounter(self, isShown):
        pass


class _FragCorrelationPanel(_IScorePanel):

    def __init__(self, parentUI):
        self.__ui = parentUI
        self.__teamsFrags = [0, 0]
        self.__fragsCache = [0, 0]
        self.clear()

    def populate(self):
        getNumberOfTeam = g_sessionProvider.getArenaDP().getNumberOfTeam
        getTeamName = g_sessionProvider.getCtx().getTeamName
        playerTeamIdx = getNumberOfTeam()
        _alliedTeamName = getTeamName(playerTeamIdx, True)
        _enemyTeamName = getTeamName(playerTeamIdx, False)
        self.__callFlash('setTeamNames', [_alliedTeamName, _enemyTeamName])
        self.showVehiclesCounter(g_settingsCore.getSetting('showVehiclesCounter'))
        self.updateScore(playerTeamIdx)
        self.updateTeam(False, playerTeamIdx)
        self.updateTeam(True, getNumberOfTeam(True))

    def destroy(self):
        self.__ui = None
        self.__teamsFrags = None
        self.__fragsCache = None
        return

    def clear(self, team = None):
        if team is None:
            self.__teamsFrags = [0, 0]
            self.__teamsShortLists = {1: [],
             2: []}
        else:
            self.__teamsShortLists[team] = []
            oppositeTeamsIndexes = (1, 0)
            self.__teamsFrags[oppositeTeamsIndexes[team - 1]] = 0
        return

    def addFrags(self, team, count = 1):
        self.__teamsFrags[team - 1] += count

    def addKilled(self, team, count = 1):
        oppositeTeamsIndexes = (2, 1)
        self.addFrags(oppositeTeamsIndexes[team - 1], count=count)

    def addVehicle(self, team, vehicleID, vClassName, isAlive):
        self.__teamsShortLists[team].append([vehicleID, vClassName, isAlive])

    def updateScore(self, playerTeam):
        if not playerTeam:
            return
        teamIndex = playerTeam - 1
        enemyIndex = 1 - teamIndex
        if len(self.__teamsFrags):
            self.__callFlash('updateFrags', [self.__teamsFrags[teamIndex], self.__teamsFrags[enemyIndex]])

    def updateTeam(self, isEnemy, team):
        if not team:
            return
        sortedList = sorted(self.__teamsShortLists[team], cmp=markerComparator)
        team = [ pos for item in sortedList for pos in item ]
        if isEnemy:
            self.__callFlash('updateEnemyTeam', team)
        else:
            self.__callFlash('updatePlayerTeam', team)

    def showVehiclesCounter(self, isShown):
        self.__callFlash('showVehiclesCounter', [isShown])

    def __callFlash(self, funcName, args):
        self.__ui.call('battle.fragCorrelationBar.' + funcName, args)


class FalloutScorePanel(FalloutScorePanelMeta, _IScorePanel):

    def __init__(self, proxy):
        super(FalloutScorePanel, self).__init__()
        self.__proxy = proxy
        self.__ui = None
        self.__maxScore = BigWorld.player().arena.arenaType.winPoints['winPointsCAP']
        return

    def populate(self):
        self.__ui = self.__proxy.getMember(FALLOUT_SCORE_PANEL)
        super(FalloutScorePanel, self)._populate(self.__ui)
        self.__makeData()

    def destroy(self):
        self.__proxy = None
        self.__ui = None
        return

    def updateScore(self, playerTeam):
        if self.__ui is not None:
            self.__makeData()
        return

    def __makeData(self):
        arenaDP = g_sessionProvider.getArenaDP()
        playerVehID = BigWorld.player().playerVehicleID
        playerTeamVehIDs = g_sessionProvider.getArenaDP().getVehiclesIDs()
        allyScore = 0
        playerScore = 0
        for vID in playerTeamVehIDs:
            details = arenaDP.getVehicleInteractiveStats(vID)
            points = details.winPoints
            allyScore += points
            if vID == playerVehID:
                playerScore += points

        enemyTeamVehIDs = g_sessionProvider.getArenaDP().getVehiclesIDs(True)
        enemyScore = 0
        for vID in enemyTeamVehIDs:
            details = arenaDP.getVehicleInteractiveStats(vID)
            enemyScore += details.winPoints

        self.as_setDataS(self.__maxScore, allyScore, enemyScore, playerScore)


def scorePanelFactory(parentUI):
    if isEventBattle():
        return FalloutScorePanel(parentUI)
    return _FragCorrelationPanel(parentUI)
