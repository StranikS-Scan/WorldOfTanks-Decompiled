# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/stats.py
from skeletons.gui.game_event_controller import IGameEventController
from PlayerEvents import g_playerEvents
from constants import ARENA_PERIOD
from gui.Scaleform.daapi.view.meta.EventStatsMeta import EventStatsMeta
from game_event_getter import GameEventGetterMixin
from debug_utils import LOG_DEBUG_DEV
from gui.impl import backport
from gui.impl.gen import R
from gui.battle_control.arena_info.interfaces import IArenaVehiclesController
from gui.shared.badges import buildBadge
from gui.Scaleform.settings import ICONS_SIZES
from helpers import dependency

def _getL10nID(envID):
    return envID % 10


class EventStats(EventStatsMeta, GameEventGetterMixin, IArenaVehiclesController):
    _gameEventController = dependency.descriptor(IGameEventController)
    _FINAL_ENV_ID = 4

    def __init__(self):
        super(EventStats, self).__init__()
        self.__arenaDP = self.sessionProvider.getArenaDP()

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
        if self.souls is not None:
            self.souls.onSoulsChanged += self.__onSoulsChanged
        if self.environmentData is not None:
            self.environmentData.onUpdated += self.__onEnvironmentChanged
        if self.teammateVehicleHealth is not None:
            self.teammateVehicleHealth.onTeammateVehicleHealthUpdate += self.__onTeammateVehicleHealthUpdate
        self.__updateTitleAndDescription()
        self.__updateStats()
        return

    def _dispose(self):
        g_playerEvents.onArenaPeriodChange -= self.__onArenaPeriodChange
        if self.souls is not None:
            self.souls.onSoulsChanged -= self.__onSoulsChanged
        if self.environmentData is not None:
            self.environmentData.onUpdated -= self.__onEnvironmentChanged
        if self.teammateVehicleHealth is not None:
            self.teammateVehicleHealth.onTeammateVehicleHealthUpdate -= self.__onTeammateVehicleHealthUpdate
        self.sessionProvider.removeArenaCtrl(self)
        super(EventStats, self)._dispose()
        return

    def __updateTitleAndDescription(self):
        envID = self.__getEnvironmentId()
        l10nID = _getL10nID(envID)
        LOG_DEBUG_DEV('EventStats::__updateTitleAndDescription', envID, l10nID)
        if l10nID != self._FINAL_ENV_ID:
            title = backport.text(R.strings.event.stats.world.num(l10nID).title())
            desc = backport.text(R.strings.event.stats.world.num(l10nID).desc())
            playerVehicleID = self.__arenaDP.getPlayerVehicleID()
            if self.__arenaDP.isSquadMan(vID=playerVehicleID):
                difficultyLevel = self._gameEventController.getSquadDifficultyLevel()
            else:
                difficultyLevel = self._gameEventController.getSelectedDifficultyLevel()
            self.as_updateTitleS(title, desc, difficultyLevel)

    def __updateStats(self):
        infoIterator = self.__arenaDP.getVehiclesInfoIterator()
        self.as_updatePlayerStatsS([ self.__makePlayerInfo(vInfo) for vInfo in infoIterator if self.__arenaDP.isAllyTeam(vInfo.team) ])

    def __makePlayerInfo(self, vInfo):
        playerVehicle = self.__arenaDP.getVehicleInfo()
        playerSquad = playerVehicle.squadIndex
        vehID = vInfo.vehicleID
        badgeID = vInfo.selectedBadge
        suffixBadgeId = vInfo.selectedSuffixBadge
        vStats = self.__arenaDP.getVehicleStats(vehID)
        frags = vStats.frags if vStats is not None else 0
        isSquad = playerSquad > 0 and playerSquad == vInfo.squadIndex
        isPlayerHimself = vehID == playerVehicle.vehicleID
        vehicleTypeIcon = 'eventStatsVehicleType_platoon_{}' if isSquad or isPlayerHimself else 'eventStatsVehicleType_{}'
        playerName = vInfo.player.name
        if vInfo.player.clanAbbrev:
            playerName = '{}[{}]'.format(vInfo.player.name, vInfo.player.clanAbbrev)
        badge = buildBadge(badgeID, vInfo.getBadgeExtraInfo())
        resultVO = {'playerName': playerName,
         'squadIndex': str(vInfo.squadIndex) if vInfo.squadIndex else '',
         'suffixBadgeIcon': 'badge_{}'.format(suffixBadgeId) if suffixBadgeId else '',
         'suffixBadgeStripIcon': 'strip_{}'.format(suffixBadgeId) if suffixBadgeId else '',
         'isAlive': self.__getHealthPoints(vehID) > 0,
         'isSquad': isSquad,
         'energy': str(int(self.__getSouls(vehID))),
         'kills': str(int(frags)),
         'vehicleName': vInfo.vehicleType.shortName,
         'vehicleTypeIcon': vehicleTypeIcon.format(vInfo.vehicleType.classTag),
         'isPlayerHimself': isPlayerHimself}
        if badge is not None:
            resultVO['badgeVisualVO'] = badge.getBadgeVO(ICONS_SIZES.X24, {'isAtlasSource': True}, shortIconName=True)
        return resultVO

    def __getSouls(self, vehID):
        return 0 if self.souls is None else self.souls.getSouls(vehID)

    def __getHealthPoints(self, vehID):
        return 0 if self.teammateVehicleHealth is None else self.teammateVehicleHealth.getTeammateHealth(vehID)

    def __getEnvironmentId(self):
        return 0 if self.environmentData is None else self.environmentData.getCurrentEnvironmentID()

    def __onArenaPeriodChange(self, period, periodEndTime, periodLength, periodAdditionalInfo):
        if period == ARENA_PERIOD.BATTLE:
            self.__updateStats()

    def __onSoulsChanged(self, diff):
        self.__updateStats()

    def __onEnvironmentChanged(self):
        self.__updateTitleAndDescription()

    def __onTeammateVehicleHealthUpdate(self, _):
        self.__updateStats()
