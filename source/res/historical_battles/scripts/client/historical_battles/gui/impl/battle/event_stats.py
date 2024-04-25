# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/battle/event_stats.py
import logging
import BigWorld
from PlayerEvents import g_playerEvents
from constants import ARENA_PERIOD
from frameworks.wulf import ViewFlags, ViewSettings, WindowFlags, WindowLayer
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor
from gui.battle_control.arena_info.interfaces import IArenaVehiclesController
from gui.battle_control import avatar_getter
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.shared.gui_items.Vehicle import VEHICLE_BATTLE_TYPES_ORDER_INDICES
from helpers import dependency
from historical_battles_common.helpers_common import getFrontmanRoleID
from historical_battles.gui.impl.gen.view_models.views.battle.event_stats_view_model import EventStatsViewModel
from historical_battles.gui.impl.gen.view_models.views.battle.event_stats_team_member_model import EventStatsTeamMemberModel
from historical_battles.gui.impl.lobby.platoon.platoon_helpers import FrontmanRoleIDToTeamMemberRole
from TeamInfoLivesComponent import TeamInfoLivesComponent
from gui.impl.gui_decorators import args2params
from gui.impl.pub import ViewImpl, WindowImpl
from gui.impl.gen import R
from historical_battles.gui.impl.gen.view_models.views.common.base_team_member_model import TeamMemberRoleType, TeamMemberBanType
from skeletons.gui.battle_session import IBattleSessionProvider
_logger = logging.getLogger(__name__)

class EventStatsInjected(InjectComponentAdaptor):

    def _makeInjectView(self):
        return EventStats(flags=ViewFlags.VIEW)

    @property
    def hasTabs(self):
        return False

    def onToggleVisibility(self, isVisible):
        pass


class EventStats(ViewImpl, IArenaVehiclesController):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, flags=ViewFlags.VIEW, *args, **kwargs):
        settings = ViewSettings(layoutID=R.views.historical_battles.battle.EventStats(), flags=flags, model=EventStatsViewModel())
        settings.args = args
        settings.kwargs = kwargs
        super(EventStats, self).__init__(settings)
        self.__arenaDP = self.sessionProvider.getArenaDP()

    @property
    def viewModel(self):
        return super(EventStats, self).getViewModel()

    def invalidateArenaInfo(self):
        self.__updateHeader()
        self.__updateColumns()
        self.__updateStats()

    def invalidateVehiclesStats(self, arenaDP):
        self.__updateStats()

    def addVehicleInfo(self, vo, arenaDP):
        if not arenaDP.isAllyTeam(vo.team):
            return
        self.__updateStats()

    def updateVehiclesInfo(self, updated, arenaDP):
        self.__updateStats()

    def invalidateVehicleStatus(self, flags, vInfoVO, arenaDP):
        self.__updateStats()

    def updateVehiclesStats(self, updated, arenaDP):
        self.__updateStats()

    def _onTeamLivesUpdated(self):
        self.__updateStats()

    def _initialize(self, *args, **kwargs):
        super(EventStats, self)._initialize(*args, **kwargs)
        self.sessionProvider.addArenaCtrl(self)
        TeamInfoLivesComponent.onTeamLivesUpdated += self._onTeamLivesUpdated
        g_playerEvents.onArenaPeriodChange += self.__onArenaPeriodChange
        if self.vehicleStats:
            self.vehicleStats.onTeamStatsUpdated += self.__updateStatsOnChangeParams
        with self.viewModel.transaction() as tx:
            self.__updateHeader(model=tx)
            self.__updateColumns(model=tx)
            self.__updateStats(model=tx)
            tx.onPlayerClick += self.__onPlayerClicked

    def _finalize(self):
        g_playerEvents.onArenaPeriodChange -= self.__onArenaPeriodChange
        self.sessionProvider.removeArenaCtrl(self)
        self.viewModel.onPlayerClick -= self.__onPlayerClicked
        if self.vehicleStats:
            self.vehicleStats.onTeamStatsUpdated -= self.__updateStatsOnChangeParams
        TeamInfoLivesComponent.onTeamLivesUpdated -= self._onTeamLivesUpdated
        super(EventStats, self)._finalize()

    @property
    def vehicleStats(self):
        if BigWorld.player() is not None:
            arena = BigWorld.player().arena
            if arena:
                return arena.teamInfo.dynamicComponents.get('hbTeamStatsComponent')
        return

    def __createTeamMember(self, index, vInfo):
        member = EventStatsTeamMemberModel()
        playerVehicle = self.__arenaDP.getVehicleInfo()
        playerSquad = playerVehicle.squadIndex
        vehID = vInfo.vehicleID
        vStats = self.__arenaDP.getVehicleStats(vehID)
        isSquad = playerSquad > 0 and playerSquad == vInfo.squadIndex
        if self.vehicleStats:
            damage = self.vehicleStats.getDamage(vehID)
            block = self.vehicleStats.getBlocked(vehID)
            assist = self.vehicleStats.getAssist(vehID)
            member.stats.setAssist(assist)
            member.stats.setDamage(damage)
            member.stats.setBlocked(block)
        member.setId(index)
        member.setIsAlive(vInfo.isAlive())
        member.setIsCurrentPlayer(vehID == playerVehicle.vehicleID)
        member.setIsOwnSquad(isSquad)
        member.setSquadNum(vInfo.squadIndex)
        frontmanRoleID = getFrontmanRoleID(vInfo.vehicleID)
        member.setRoleType(FrontmanRoleIDToTeamMemberRole.get(frontmanRoleID, TeamMemberRoleType.NONE))
        member.setBanType(TeamMemberBanType.NOTBANNED)
        member.setIsReady(vInfo.isConnected() and vInfo.isReady())
        member.stats.setKills(vStats.frags)
        member.user.setIsFakeNameVisible(False)
        member.user.setUserName(vInfo.player.name)
        member.user.setClanAbbrev(vInfo.player.clanAbbrev)
        member.user.badge.setBadgeID(str(vInfo.selectedBadge) if vInfo.selectedBadge != 0 else '')
        member.vehicle.setVehicleName(vInfo.vehicleType.shortName)
        member.vehicle.setVehicleType(vInfo.vehicleType.classTag)
        return member

    @replaceNoneKwargsModel
    def __updateHeader(self, model=None):
        info = model.info
        arena = avatar_getter.getArena()
        geometryName = arena.arenaType.geometryName
        info.setMapName(R.strings.hb_arenas.num(geometryName).upperName())
        info.setMissionIcon(R.images.gui.maps.icons.mode_selector.mode.historicalBattles.icon_huge())
        info.setMissionTitle(R.strings.hb_battle.eventStats.missionTitle())
        info.setMissionTask(R.strings.hb_battle.eventStats.missionTask())
        model.setIsHeaderVisible(True)

    @replaceNoneKwargsModel
    def __updateColumns(self, model=None):
        columns = model.columnSettings.getVisibleColumns()
        columns.clear()
        columns.addString('damage')
        columns.addString('kills')
        columns.addString('assist')
        columns.addString('blocked')
        columns.invalidate()

    @replaceNoneKwargsModel
    def __updateStats(self, model=None):
        arenaDP = self.__arenaDP
        infoIterator = arenaDP.getVehiclesInfoIterator()
        team = model.getTeam()
        team.clear()
        allyTeam = [ v for v in infoIterator if not v.isBot and arenaDP.isAllyTeam(v.team) ]
        self.__sortTeammates(allyTeam)
        for idx, vInfo in enumerate(allyTeam):
            team.addViewModel(self.__createTeamMember(idx, vInfo))

        team.invalidate()

    def __updateStatsOnChangeParams(self, *args, **kwars):
        self.__updateStats()

    @args2params(int)
    def __onPlayerClicked(self, memberId):
        _logger.info('Team member clicked: %s', memberId)

    def __onArenaPeriodChange(self, period, periodEndTime, periodLength, periodAdditionalInfo):
        if period == ARENA_PERIOD.BATTLE:
            self.__updateStats()

    def __sortTeammates(self, userVOs):
        userVOs.sort(key=lambda x: (0 if self.__getVehicleLives(x.vehicleID) > 0 else 1,
         0 if x.vehicleType.level > 1 else 1,
         VEHICLE_BATTLE_TYPES_ORDER_INDICES[x.vehicleType.classTag],
         x.player.name))

    @staticmethod
    def __getVehicleLives(vehicleID):
        teamLivesComponent = BigWorld.player().arena.teamInfo.dynamicComponents.get('teamLivesComponent')
        return teamLivesComponent.getLives(vehicleID) if teamLivesComponent else 0


class EventStatsWindow(WindowImpl):
    __slots__ = ()

    def __init__(self, parent=None):
        super(EventStatsWindow, self).__init__(wndFlags=WindowFlags.WINDOW_FULLSCREEN | WindowFlags.WINDOW, content=EventStats(), layer=WindowLayer.OVERLAY, parent=parent)
