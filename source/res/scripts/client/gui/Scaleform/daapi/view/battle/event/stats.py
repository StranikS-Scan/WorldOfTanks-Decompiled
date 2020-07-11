# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/stats.py
from PlayerEvents import g_playerEvents
from constants import ARENA_PERIOD
from gui.Scaleform.daapi.view.meta.EventStatsMeta import EventStatsMeta
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from gui.battle_control.arena_info.interfaces import IArenaVehiclesController

class EventStats(EventStatsMeta, IArenaVehiclesController):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(EventStats, self).__init__()
        self._title = None
        self._desc = None
        self._points = dict()
        self.__arenaDP = self.sessionProvider.getArenaDP()
        return

    def invalidateArenaInfo(self):
        self.__updateTitleAndDescription()
        self.__updateStats()

    def invalidateVehiclesStats(self, arenaDP):
        self.__updateStats()

    def addVehicleInfo(self, vo, arenaDP):
        if not arenaDP.isAllyTeam(vo.team):
            return
        self.__updateStats()

    def updateVehiclesInfo(self, updated, arenaDP):
        self.__updateStats()

    def updateVehiclesStats(self, updated, arenaDP):
        self.__updateStats()

    def _populate(self):
        super(EventStats, self)._populate()
        self.sessionProvider.addArenaCtrl(self)
        g_playerEvents.onArenaPeriodChange += self.__onArenaPeriodChange
        self.__updateTitleAndDescription()
        self.__updateStats()

    def _dispose(self):
        g_playerEvents.onArenaPeriodChange -= self.__onArenaPeriodChange
        self.sessionProvider.removeArenaCtrl(self)
        super(EventStats, self)._dispose()

    def __updateTitleAndDescription(self):
        if self._title and self._desc:
            self.as_updateTitleS(self._title, self._desc)

    def __updateStats(self):
        infoIterator = self.__arenaDP.getVehiclesInfoIterator()
        playersVehicles = [ vInfo for vInfo in infoIterator if self.__arenaDP.isAllyTeam(vInfo.team) ]
        for i, vInfo in enumerate(playersVehicles):
            info = self.__makePlayerInfo(vInfo)
            self.as_updatePlayerStatsS(info, i)

    def __makePlayerInfo(self, vInfo):
        playerVehicle = self.__arenaDP.getVehicleInfo()
        playerSquad = playerVehicle.squadIndex
        vehID = vInfo.vehicleID
        badgeId = vInfo.selectedBadge
        suffixBadgeId = vInfo.selectedSuffixBadge
        vStats = self.__arenaDP.getVehicleStats(vehID)
        frags = vStats.frags if vStats is not None else 0
        isSquad = playerSquad > 0 and playerSquad == vInfo.squadIndex
        isPlayerHimself = vehID == playerVehicle.vehicleID
        playerName = vInfo.player.name
        if vInfo.player.clanAbbrev:
            playerName = '{}[{}]'.format(vInfo.player.name, vInfo.player.clanAbbrev)
        return {'playerName': playerName,
         'squadIndex': str(vInfo.squadIndex) if vInfo.squadIndex else '',
         'badgeIcon': 'badge_{}'.format(badgeId) if badgeId else '',
         'suffixBadgeIcon': 'badge_{}'.format(suffixBadgeId) if suffixBadgeId else '',
         'isAlive': vInfo.isAlive(),
         'isSquad': isSquad,
         'points': str(int(self.getPoints(vehID))),
         'kills': str(int(frags)),
         'vehicleName': vInfo.vehicleType.shortName,
         'vehicleTypeIcon': 'fullStatsVehicleType_green_{}'.format(vInfo.vehicleType.classTag),
         'isPlayerHimself': isPlayerHimself}

    def getPoints(self, vehID):
        return self._points.get(vehID, 0)

    def setPoints(self, vehID, points):
        self._points[vehID] = points

    def setTitle(self, title):
        self._title = title

    def setDescription(self, desc):
        self._desc = desc

    def __onArenaPeriodChange(self, period, periodEndTime, periodLength, periodAdditionalInfo):
        if period == ARENA_PERIOD.BATTLE:
            self.__updateStats()
