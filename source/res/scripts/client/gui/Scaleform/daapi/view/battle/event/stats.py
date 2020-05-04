# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/stats.py
import BigWorld
from PlayerEvents import g_playerEvents
from constants import ARENA_PERIOD
from gui.Scaleform.daapi.view.meta.EventStatsMeta import EventStatsMeta
from gui.Scaleform.settings import ICONS_SIZES
from gui.battle_control.arena_info.interfaces import IArenaVehiclesController
from gui.shared.badges import buildBadge
from gui.shared.gui_items.Vehicle import VEHICLE_TABLE_TYPES_ORDER_INDICES as VEHICLE_ORDER
from game_event_getter import GameEventGetterMixin

class EventStats(EventStatsMeta, GameEventGetterMixin, IArenaVehiclesController):
    _FINAL_ENV_ID = 4

    def __init__(self):
        super(EventStats, self).__init__()
        self.__arenaDP = self.sessionProvider.getArenaDP()

    def invalidateArenaInfo(self):
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
        if self.teammateVehicleHealth is not None:
            self.teammateVehicleHealth.onTeammateVehicleHealthUpdate += self.__onTeammateVehicleHealthUpdate
        self.__updateStats()
        return

    def _dispose(self):
        g_playerEvents.onArenaPeriodChange -= self.__onArenaPeriodChange
        if self.teammateVehicleHealth is not None:
            self.teammateVehicleHealth.onTeammateVehicleHealthUpdate -= self.__onTeammateVehicleHealthUpdate
        self.sessionProvider.removeArenaCtrl(self)
        super(EventStats, self)._dispose()
        return

    def __updateStats(self):
        infoIterator = self.__arenaDP.getVehiclesInfoIterator()
        generalLevels = BigWorld.player().arena.extraData.get('playerAdditionalInfo', {})
        playersVehicles = sorted([ v for v in infoIterator if v.player.accountDBID > 0 and self.__arenaDP.isAllyTeam(v.team) ], key=lambda x: (-generalLevels.get(x.player.accountDBID, -1), VEHICLE_ORDER[x.vehicleType.classTag], x.player.name))
        for i, vInfo in enumerate(playersVehicles):
            info = self.__makePlayerInfo(vInfo)
            self.as_updatePlayerStatsS(info, i)

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
        badgeVO = badge.getBadgeVO(ICONS_SIZES.X24, {'isAtlasSource': True}, shortIconName=True) if badge else None
        return {'playerName': playerName,
         'squadIndex': str(vInfo.squadIndex) if vInfo.squadIndex else '',
         'badgeVisualVO': badgeVO,
         'suffixBadgeIcon': 'badge_{}'.format(suffixBadgeId) if suffixBadgeId else '',
         'isAlive': self.__getHealthPoints(vehID) > 0,
         'isSquad': isSquad,
         'damage': str(vStats.interactive.damageDealt),
         'kills': str(int(frags)),
         'vehicleName': vInfo.vehicleType.shortName,
         'vehicleTypeIcon': vehicleTypeIcon.format(vInfo.vehicleType.classTag),
         'isPlayerHimself': isPlayerHimself}

    def __getHealthPoints(self, vehID):
        return 0 if self.teammateVehicleHealth is None else self.teammateVehicleHealth.getTeammateHealth(vehID)

    def __onArenaPeriodChange(self, period, periodEndTime, periodLength, periodAdditionalInfo):
        if period == ARENA_PERIOD.BATTLE:
            self.__updateStats()

    def __onTeammateVehicleHealthUpdate(self, _):
        self.__updateStats()
