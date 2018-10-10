# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/team_health_bar_ctrl.py
import weakref
from gui.battle_control import avatar_getter
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from gui.battle_control.view_components import ViewComponentsController
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE

class ITeamHealthBarListener(object):

    def updateTeamHealthPercent(self, allyPercentage, enemyPercentage):
        pass


class TeamHealthBarController(ViewComponentsController):

    def __init__(self, setup):
        super(TeamHealthBarController, self).__init__()
        self.__arenaVisitor = weakref.proxy(setup.arenaVisitor)
        self.__arenaDP = weakref.proxy(setup.arenaDP)
        self.__latestHealthBarData = None
        self.__loadingFinished = False
        return

    def getControllerID(self):
        return BATTLE_CTRL_ID.TEAM_HEALTH_BAR

    def startControl(self):
        arena = avatar_getter.getArena()
        if arena:
            arena.onTeamHealthPercentUpdate += self.__onTeamHealthPercentUpdate
        g_eventBus.addListener(events.GameEvent.BATTLE_LOADING, self.__handleBattleLoading, EVENT_BUS_SCOPE.BATTLE)

    def stopControl(self):
        arena = avatar_getter.getArena()
        if arena:
            arena.onTeamHealthPercentUpdate -= self.__onTeamHealthPercentUpdate
        g_eventBus.removeListener(events.GameEvent.BATTLE_LOADING, self.__handleBattleLoading, EVENT_BUS_SCOPE.BATTLE)
        self.__arenaVisitor = None
        self.__arenaDP = None
        return

    def setViewComponents(self, *components):
        super(TeamHealthBarController, self).setViewComponents(*components)
        if self.__latestHealthBarData:
            self.__onTeamHealthPercentUpdate(avatar_getter.getHealthPercentage())

    def __handleBattleLoading(self, event):
        if not event.ctx['isShown']:
            self._onBattleLoadingFinish()

    def _onBattleLoadingFinish(self):
        self.__loadingFinished = True
        self.__onTeamHealthPercentUpdate(avatar_getter.getHealthPercentage())

    def __onTeamHealthPercentUpdate(self, percentages):
        self.__latestHealthBarData = list
        if not self._viewComponents or not percentages:
            return
        allyPercentage = 0
        enemyPercentage = 0
        listLength = len(percentages)
        playerTeam = avatar_getter.getPlayerTeam()
        for i in range(0, listLength):
            if playerTeam == i + 1:
                allyPercentage = percentages[i]
            enemyPercentage += percentages[i]

        for viewCmp in self._viewComponents:
            viewCmp.updateTeamHealthPercent(allyPercentage, enemyPercentage / (listLength - 1))
