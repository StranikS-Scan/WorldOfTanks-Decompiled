# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/score_panel.py
import itertools
import win_points
from collections import defaultdict
from account_helpers.settings_core import g_settingsCore
from gui.Scaleform.daapi.view.battle.meta.FalloutScorePanelMeta import FalloutScorePanelMeta
from gui.Scaleform.daapi.view.battle import FALLOUT_SCORE_PANEL
from gui.Scaleform.locale.INGAME_GUI import INGAME_GUI
from gui.shared.gui_items.Vehicle import VEHICLE_BATTLE_TYPES_ORDER_INDICES
from gui.battle_control import g_sessionProvider
from gui.battle_control.arena_info import getArenaType, hasGasAttack
from gui.battle_control.avatar_getter import getPlayerVehicleID, getPlayerName
from helpers import i18n
_TEAM_PROPS = {'tf_width': 140,
 'tf_padding': 140,
 'y_position': 4}

def _markerComparator(x1, x2):
    INDEX_IS_ALIVE = 2
    INDEX_VEHICLE_CLASS = 1
    res = x2[INDEX_IS_ALIVE] - x1[INDEX_IS_ALIVE]
    if res:
        return res
    x1Index = VEHICLE_BATTLE_TYPES_ORDER_INDICES.get(x1[INDEX_VEHICLE_CLASS], 100)
    x2Index = VEHICLE_BATTLE_TYPES_ORDER_INDICES.get(x2[INDEX_VEHICLE_CLASS], 100)
    res = x1Index - x2Index
    if res:
        return res
    return 0


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

    def updateScore(self):
        pass

    def updateTeam(self, isEnemy, team):
        pass

    def showVehiclesCounter(self, isShown):
        pass


class _FragCorrelationPanel(_IScorePanel):

    def __init__(self, parentUI):
        self.__ui = parentUI
        self.clear()

    def populate(self):
        arenaDP = g_sessionProvider.getArenaDP()
        getTeamName = g_sessionProvider.getCtx().getTeamName
        getNumberOfTeam = arenaDP.getNumberOfTeam
        playerTeamIdx, enemyTeamIdx = getNumberOfTeam(), getNumberOfTeam(True)
        _alliedTeamName = getTeamName(playerTeamIdx)
        _enemyTeamName = getTeamName(enemyTeamIdx)
        self.__callFlash('setTeamNames', [_alliedTeamName, _enemyTeamName])
        self.showVehiclesCounter(g_settingsCore.getSetting('showVehiclesCounter'))
        self.updateScore()
        for isEnemy, team in arenaDP.getTeamIDsIterator():
            self.updateTeam(isEnemy, team)

    def destroy(self):
        self.__ui = None
        self.__teamsDeaths = None
        self.__teamsShortLists = None
        return

    def clear(self, team = None):
        if team is None:
            self.__teamsDeaths = defaultdict(int)
            self.__teamsShortLists = defaultdict(list)
        else:
            self.__teamsShortLists[team] = []
            self.__teamsDeaths[team] = 0
        return

    def addKilled(self, team, count = 1):
        self.__teamsDeaths[team] += count

    def addVehicle(self, team, vehicleID, vClassName, isAlive):
        self.__teamsShortLists[team].append([vehicleID, vClassName, isAlive])

    def updateScore(self):
        if len(self.__teamsDeaths):
            isTeamEnemy = g_sessionProvider.getArenaDP().isEnemyTeam
            ally, enemy = (0, 0)
            for teamIdx, score in self.__teamsDeaths.iteritems():
                if isTeamEnemy(teamIdx):
                    ally += score
                else:
                    enemy += score

            self.__callFlash('updateFrags', [ally, enemy])

    def updateTeam(self, isEnemy, team):
        if not team:
            return
        result = []
        isTeamEnemy = g_sessionProvider.getArenaDP().isEnemyTeam
        for teamIdx, vehs in self.__teamsShortLists.iteritems():
            if isEnemy is isTeamEnemy(teamIdx):
                result.extend(vehs)

        result = list(itertools.chain(*sorted(result, cmp=_markerComparator)))
        if isEnemy:
            self.__callFlash('updateEnemyTeam', result)
        else:
            self.__callFlash('updatePlayerTeam', result)

    def showVehiclesCounter(self, isShown):
        self.__callFlash('showVehiclesCounter', [isShown])

    def __callFlash(self, funcName, args):
        self.__ui.call('battle.fragCorrelationBar.' + funcName, args)


class _FalloutScorePanel(FalloutScorePanelMeta, _IScorePanel):
    WARNING_RATIO = 0.8

    def __init__(self, proxy, ctxType):
        super(_FalloutScorePanel, self).__init__()
        self._proxy = proxy
        self._contextType = ctxType
        self._maxScore = 0

    def populate(self):
        super(_FalloutScorePanel, self)._populate(self._proxy.getMember(FALLOUT_SCORE_PANEL))
        g_settingsCore.onSettingsChanged += self.__onSettingsChanged
        arenaType = getArenaType()
        if arenaType is not None:
            self._maxScore = win_points.g_cache[getArenaType().winPoints].pointsCAP
        self.as_initWarningValue(self.WARNING_RATIO * self._maxScore)
        self._makeData()
        return

    def __onSettingsChanged(self, diff = None):
        self.as_onSettingsChanged()

    def destroy(self):
        g_settingsCore.onSettingsChanged -= self.__onSettingsChanged
        self._proxy = None
        return

    def updateScore(self):
        if self._flashObject is not None:
            self._makeData()
        return

    def _makeData(self):
        arenaDP = g_sessionProvider.getArenaDP()
        playerVehID = getPlayerVehicleID()
        allyTeams = arenaDP.getAllyTeams()
        allyScore, enemyScore, playerScore = (0, 0, 0)
        for vInfoVO, _, viStatsVO in arenaDP.getAllVehiclesIterator():
            points = viStatsVO.winPoints
            if vInfoVO.team in allyTeams:
                allyScore += points
                if vInfoVO.vehicleID == playerVehID:
                    playerScore += points
            else:
                enemyScore += points

        self.as_setDataS(self._contextType, self._maxScore, playerScore, allyScore, enemyScore, '', '', {})


class _MultiteamFalloutPanel(_FalloutScorePanel):

    def __init__(self, proxy, ctxType):
        super(_MultiteamFalloutPanel, self).__init__(proxy, ctxType)
        self.__hasGasAttack = hasGasAttack()
        self.__allyScore = 0
        self.__enemyScore = 0
        if self.__hasGasAttack:
            g_sessionProvider.getGasAttackCtrl().onPreparing += self.__onGasAttackPreparing
            g_sessionProvider.getGasAttackCtrl().onStarted += self.__onGasAttackStarted

    def destroy(self):
        if self.__hasGasAttack:
            g_sessionProvider.getGasAttackCtrl().onPreparing -= self.__onGasAttackPreparing
            g_sessionProvider.getGasAttackCtrl().onStarted -= self.__onGasAttackStarted
        super(_MultiteamFalloutPanel, self).destroy()

    def _makeData(self):
        arenaDP = g_sessionProvider.getArenaDP()
        teamIds = arenaDP.getMultiTeamsIndexes()
        playerVehID = getPlayerVehicleID()
        allyTeams = arenaDP.getAllyTeams()
        isSquadPlayer = arenaDP.isSquadMan(playerVehID)
        teamScores = {}
        enemyScore = 0
        enemyName = ''
        allyScore = 0
        for vInfoVO, _, viStatsVO in arenaDP.getAllVehiclesIterator():
            points = viStatsVO.winPoints
            if vInfoVO.team in allyTeams:
                allyScore += points
            else:
                if vInfoVO.team in teamScores:
                    currentScore = teamScores[vInfoVO.team]
                    totalScore = currentScore + points
                else:
                    totalScore = points
                teamScores[vInfoVO.team] = totalScore
                if totalScore > enemyScore:
                    enemyScore = totalScore
                    squadIndex = teamIds[vInfoVO.team]
                    enemyName = i18n.makeString(INGAME_GUI.SCOREPANEL_SQUADLBL, sq_number=squadIndex) if squadIndex else vInfoVO.player.name

        if isSquadPlayer:
            playerName = i18n.makeString(INGAME_GUI.SCOREPANEL_MYSQUADLBL)
        else:
            playerName = getPlayerName()
        self.__allyScore = allyScore
        self.__enemyScore = enemyScore
        self.as_setDataS(self._contextType, self._maxScore, 0, allyScore, enemyScore, playerName, enemyName, _TEAM_PROPS)

    def __onGasAttackPreparing(self, state):
        if self.__allyScore != self.__enemyScore:
            self.as_playScoreHighlightAnim(self.__allyScore > self.__enemyScore)
        else:
            self.as_playScoreHighlightAnim(True)
            self.as_playScoreHighlightAnim(False)

    def __onGasAttackStarted(self, state):
        self.as_stopScoreHighlightAnim()


def scorePanelFactory(parentUI, isEvent = False, isMutlipleTeams = False):
    if isEvent:
        if isMutlipleTeams:
            return _MultiteamFalloutPanel(parentUI, 'multi')
        return _FalloutScorePanel(parentUI, 'single')
    return _FragCorrelationPanel(parentUI)
