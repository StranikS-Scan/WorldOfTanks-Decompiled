# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/impl/lobby/widgets/event_stats.py
import logging
from PlayerEvents import g_playerEvents
from constants import ARENA_PERIOD
from frameworks.wulf import ViewFlags, ViewSettings
from gui.battle_control.arena_info.interfaces import IArenaVehiclesController
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.shared.gui_items.Vehicle import VEHICLE_BATTLE_TYPES_ORDER_INDICES, VEHICLE_TAGS
from helpers import dependency
from last_stand.gui.impl.gen.view_models.views.common.stat_column_settings_model import ColumnEnum
from last_stand.gui.impl.gen.view_models.views.battle.event_stats_view_model import EventStatsViewModel
from last_stand.gui.impl.gen.view_models.views.battle.event_stats_team_member_model import EventStatsTeamMemberModel
from gui.impl.pub import ViewImpl
from gui.impl.gen import R
from gui.shared.utils import toUpper
from last_stand.gui.impl.gen.view_models.views.common.base_team_member_model import TeamMemberBanType
from skeletons.gui.battle_session import IBattleSessionProvider
from LSTeamInfoStatsComponent import LSTeamInfoStatsComponent
_logger = logging.getLogger(__name__)

class EventStats(ViewImpl, IArenaVehiclesController):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, flags=ViewFlags.VIEW, *args, **kwargs):
        settings = ViewSettings(layoutID=R.aliases.last_stand.shared.TeamStats(), flags=flags, model=EventStatsViewModel())
        settings.args = args
        settings.kwargs = kwargs
        super(EventStats, self).__init__(settings)
        self.__arenaDP = self.sessionProvider.getArenaDP()

    @property
    def viewModel(self):
        return super(EventStats, self).getViewModel()

    @property
    def vehicleStats(self):
        return LSTeamInfoStatsComponent.getInstance()

    def invalidateArenaInfo(self):
        self._updateColumns()
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

    def _onLoading(self, *args, **kwargs):
        super(EventStats, self)._onLoading(*args, **kwargs)
        with self.viewModel.transaction() as tx:
            self._updateColumns(model=tx)
            self.__updateStats(model=tx)

    def _subscribe(self):
        super(EventStats, self)._subscribe()
        g_playerEvents.onArenaPeriodChange += self.__onArenaPeriodChange
        if self.vehicleStats:
            self.vehicleStats.onTeamStatsUpdated += self.__updateStatsOnChangeParams

    def _unsubscribe(self):
        super(EventStats, self)._unsubscribe()
        g_playerEvents.onArenaPeriodChange -= self.__onArenaPeriodChange
        self.sessionProvider.removeArenaCtrl(self)
        if self.vehicleStats:
            self.vehicleStats.onTeamStatsUpdated -= self.__updateStatsOnChangeParams

    @replaceNoneKwargsModel
    def _updateColumns(self, model=None):
        columns = model.columnSettings.getVisibleColumns()
        columns.clear()
        columns.addString(ColumnEnum.DAMAGE.value)
        columns.addString(ColumnEnum.KILLS.value)
        columns.invalidate()

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
            souls = 0
            member.stats.setAssist(assist)
            member.stats.setDamage(damage)
            member.stats.setBlocked(block)
            member.stats.setSouls(souls)
        member.setId(index)
        member.setIsAlive(vInfo.isAlive())
        member.setIsCurrentPlayer(vehID == playerVehicle.vehicleID)
        member.setIsOwnSquad(isSquad)
        member.setSquadNum(vInfo.squadIndex)
        member.setBanType(TeamMemberBanType.NOTBANNED)
        member.setIsReady(vInfo.isReady())
        member.stats.setKills(vStats.frags)
        member.user.setIsFakeNameVisible(False)
        member.user.setUserName(vInfo.player.name)
        member.user.setClanAbbrev(vInfo.player.clanAbbrev)
        member.user.badge.setBadgeID(str(vInfo.selectedBadge) if vInfo.selectedBadge != 0 else '')
        member.user.suffixBadge.setBadgeID(str(vInfo.selectedSuffixBadge) if vInfo.selectedSuffixBadge != 0 else '')
        member.vehicle.setVehicleName(vInfo.vehicleType.name)
        member.vehicle.setVehicleShortName(vInfo.vehicleType.shortName)
        member.vehicle.setVehicleType(vInfo.vehicleType.classTag)
        if vInfo.vehicleType.isPremiumIGR:
            member.vehicle.setTags(VEHICLE_TAGS.PREMIUM_IGR)
        return member

    @replaceNoneKwargsModel
    def __updateStats(self, model=None):
        arenaDP = self.__arenaDP
        infoIterator = arenaDP.getVehiclesInfoIterator()
        team = model.getTeam()
        team.clear()
        allyTeam = [ v for v in infoIterator if arenaDP.isAllyTeam(v.team) ]
        self.__sortTeammates(allyTeam)
        for idx, vInfo in enumerate(allyTeam):
            team.addViewModel(self.__createTeamMember(idx, vInfo))

        team.invalidate()

    def __updateStatsOnChangeParams(self, *args, **kwars):
        self.__updateStats()

    def __onArenaPeriodChange(self, period, periodEndTime, periodLength, periodAdditionalInfo):
        if period == ARENA_PERIOD.BATTLE:
            self.__updateStats()

    def __sortTeammates(self, userVOs):
        userVOs.sort(key=lambda x: (0 if x.isAlive() else 1,
         VEHICLE_BATTLE_TYPES_ORDER_INDICES[x.vehicleType.classTag],
         x.vehicleType.shortName,
         toUpper(x.player.name)))
