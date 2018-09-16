# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/football_full_stats.py
from event_special_effects import TeamType
from gui.Scaleform.daapi.view.meta.FootballFullStatsMeta import FootballFullStatsMeta
from gui.battle_control.controllers.football_ctrl import IFootballView
from gui.Scaleform.locale.FOOTBALL2018 import FOOTBALL2018
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.battle_control.arena_info.settings import SMALL_MAP_IMAGE_SF_PATH
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from gui.battle_control import avatar_getter
_TANKCOLOR_RED = 'red'
_TANKCOLOR_GREEN = 'green'
_ICON_TEMPLATE = '../maps/icons/vehicleTypes/{}/{}.png'

class FootballFullStats(FootballFullStatsMeta, IFootballView):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(FootballFullStats, self).__init__()
        self.__isTeam1 = False
        self.__textUpdated = False

    def _populate(self):
        super(FootballFullStats, self)._populate()
        team = avatar_getter.getPlayerTeam()
        if team == 1:
            self.__isTeam1 = True
        self.as_initDataS({'mapText': self.sessionProvider.getCtx().getArenaTypeName(),
         'battleText': FOOTBALL2018.MESSAGES_FOOTBALL_FULLSTATS_BATTLETEXT,
         'winText': FOOTBALL2018.MESSAGES_FOOTBALL_FULLSTATS_WINTEXT,
         'team1Name': FOOTBALL2018.MESSAGES_FOOTBALL_FULLSTATS_TEAM1NAME,
         'team2Name': FOOTBALL2018.MESSAGES_FOOTBALL_FULLSTATS_TEAM2NAME,
         'commonStats': FOOTBALL2018.MESSAGES_FOOTBALL_FULLSTATS_COMMONSTATS,
         'goals': FOOTBALL2018.MESSAGES_FOOTBALL_FULLSTATS_GOALS,
         'ballPossession': FOOTBALL2018.MESSAGES_FOOTBALL_FULLSTATS_BALLPOSSESSION,
         'eventsTimeline': FOOTBALL2018.MESSAGES_FOOTBALL_FULLSTATS_EVENTSTIMELINE,
         'battleIcon': RES_ICONS.MAPS_ICONS_BATTLETYPES_128X128_FOOTBALL,
         'mapIcon': SMALL_MAP_IMAGE_SF_PATH % self.sessionProvider.arenaVisitor.type.getGeometryName()})
        self.as_updateBallPossessionS('0', '0')
        self.as_updateScoreS('0', '0', '0 : 0')
        self.as_showBallPossesionS(False)

    def updateScore(self, scores, scoreInfo):
        if self.__isTeam1:
            team0, team1 = scores[0], scores[1]
        else:
            team1, team0 = scores[0], scores[1]
        team0str = str(team0)
        team1str = str(team1)
        self.as_updateScoreS(team0str, team1str, team0str + ' : ' + team1str)

    def updateGoalTimeline(self, data):
        self.addTimelineEntry(data)

    def updateOvertimeScore(self, points):
        if points:
            if self.__isTeam1:
                team0, team1 = str(points[1]), str(points[2])
            else:
                team0, team1 = str(points[2]), str(points[1])
            self.as_updateBallPossessionS(team0, team1)
        if self.__textUpdated is False:
            self.__textUpdated = True
            self.as_updateWinTextS(FOOTBALL2018.MESSAGES_FOOTBALL_FULLSTATS_WINTEXTOVERTIME)
            self.as_showBallPossesionS(True)

    def addTimelineEntry(self, data):
        time = "{}'".format(data['time'] / 60)
        playerName = data['playerName']
        weight = data['weight']
        selfGoal = data['selfGoal']
        arenaDP = self.sessionProvider.getArenaDP()
        vehInfo = arenaDP.getVehicleInfo()
        playerTeam = vehInfo.team
        isInvertedColor = False
        if playerTeam in TeamType.PLAYABLE:
            isInvertedColor = vehInfo.team == TeamType.TEAM_RED
        allyScheme = 'vm_enemy' if isInvertedColor else 'vm_ally'
        enemyScheme = 'vm_ally' if isInvertedColor else 'vm_enemy'
        teamId = data['teamID']
        if self.sessionProvider.getArenaDP().isAllyTeam(teamId):
            self.as_addGoalLeftS(time, playerName, weight, enemyScheme if selfGoal else allyScheme)
        else:
            self.as_addGoalRightS(time, playerName, weight, allyScheme if selfGoal else enemyScheme)
