# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/pve_base/stats_exchange.py
import typing
from TeamInfoLivesComponent import TeamInfoLivesComponent
from constants import BOT_DISPLAY_STATUS
from gui.Scaleform.daapi.view.battle.classic.stats_exchange import ClassicStatisticsDataController, DynamicVehicleStatsComponent
from gui.Scaleform.daapi.view.battle.shared.stats_exchange import broker
from gui.Scaleform.daapi.view.battle.shared.stats_exchange import createExchangeBroker
from gui.Scaleform.daapi.view.battle.shared.stats_exchange import vehicle
from gui.Scaleform.daapi.view.battle.shared.stats_exchange.vehicle import BiSortedIDsComposer, AllySortedIDsComposer, EnemySortedIDsComposer, VehicleInfoComponent
from gui.battle_control.arena_info.settings import VehicleSpottedStatus, INVALIDATE_OP
from gui.battle_control.arena_info.vos_collections import VehicleInfoSortKey
from helpers import dependency
from pve_battle_hud import WidgetType
from skeletons.gui.battle_session import IBattleSessionProvider
if typing.TYPE_CHECKING:
    from gui.battle_control.arena_info.arena_vos import VehicleArenaInfoVO

def updatedInfoPredicate(isEnemy, settings):
    return isEnemy and settings == WidgetType.ENEMY_LIST or not isEnemy and settings == WidgetType.ALLY_LIST


class PveVehicleInfoSortKey(VehicleInfoSortKey):
    __slots__ = ('_sortAlive',)

    def __init__(self, item):
        super(PveVehicleInfoSortKey, self).__init__(item)
        self._sortAlive = True

    def _cmp(self, other):
        aInfo = self.vInfoVO
        bInfo = other.vInfoVO
        result = cmp(aInfo.team, bInfo.team)
        if result:
            return result
        if self._sortAlive:
            result = -cmp(aInfo.isAlive(), bInfo.isAlive())
            if result:
                return result
        result = cmp(aInfo.player.isBot, bInfo.player.isBot)
        if result:
            return result
        result = -cmp(aInfo.vehicleType.level, bInfo.vehicleType.level)
        if result:
            return result
        result = -cmp(aInfo.botDisplayStatus, bInfo.botDisplayStatus)
        if result:
            return result
        result = cmp(aInfo.vehicleType.getOrderByClass(), bInfo.vehicleType.getOrderByClass())
        if result:
            return result
        result = cmp(aInfo.vehicleType.shortName, bInfo.vehicleType.shortName)
        return result if result else cmp(aInfo.player, bInfo.player)


class PveVehicleInfoSortKeyEnemyList(PveVehicleInfoSortKey):
    __slots__ = ()

    def __init__(self, item):
        super(PveVehicleInfoSortKeyEnemyList, self).__init__(item)
        self._sortAlive = False


class PveTeamsSortedIDsComposer(BiSortedIDsComposer):
    __slots__ = ()

    def __init__(self):
        super(PveTeamsSortedIDsComposer, self).__init__(left=AllySortedIDsComposer(voField='leftItemsIDs', sortKey=PveVehicleInfoSortKey), right=EnemySortedIDsComposer(voField='rightItemsIDs', sortKey=PveVehicleInfoSortKeyEnemyList))


class PveVehicleInfoComponent(VehicleInfoComponent):
    _sessionProvider = dependency.descriptor(IBattleSessionProvider)
    _EMPTY_LIVES_COUNTER = -1

    def addVehicleInfo(self, vInfoVO, overrides):
        super(PveVehicleInfoComponent, self).addVehicleInfo(vInfoVO, overrides)
        teamLives = TeamInfoLivesComponent.getInstance()
        livesCnt = teamLives.getLives(vInfoVO.vehicleID) if teamLives else self._EMPTY_LIVES_COUNTER
        self._data.update({'prestigeMarkId': 0,
         'prestigeLevel': 0,
         'teamPanelMode': vInfoVO.teamPanelMode,
         'highlight': False,
         'showFrags': True,
         'showVehicleTypeIcon': False,
         'countLives': livesCnt})
        canHighlight = vInfoVO.botDisplayStatus != BOT_DISPLAY_STATUS.REGULAR
        settingsCtrl = self._sessionProvider.dynamic.vseHUDSettings
        if settingsCtrl is not None:
            settings = settingsCtrl.getSettings(WidgetType.ENEMY_LIST)
            if settings is not None and vInfoVO.isEnemy() and canHighlight:
                self._data['highlight'] = settings.highlightElite
            settings = settingsCtrl.getSettings(WidgetType.ALLY_LIST)
            if settings is not None:
                self._data['showFrags'] = settings.showFrags
                self._data['showVehicleTypeIcon'] = settings.showVehicleTypeIcon
                if not vInfoVO.isEnemy() and canHighlight:
                    self._data['highlight'] = settings.highlightElite
        return


class PveDynamicVehicleStatsComponent(DynamicVehicleStatsComponent):
    __slots__ = ()
    _sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def get(self, forced=False):
        data = super(PveDynamicVehicleStatsComponent, self).get(forced)
        if data:
            settingsCtrl = self._sessionProvider.dynamic.vseHUDSettings
            if settingsCtrl is not None:
                settings = settingsCtrl.getSettings(WidgetType.ENEMY_LIST)
                if settings is not None and not settings.showSpottedIcon:
                    data['spottedStatus'] = VehicleSpottedStatus.DEFAULT
        return data


class PveStatisticsDataController(ClassicStatisticsDataController):
    _sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def startControl(self, battleCtx, arenaVisitor):
        super(PveStatisticsDataController, self).startControl(battleCtx, arenaVisitor)
        settingsCtrl = self._sessionProvider.dynamic.vseHUDSettings
        if settingsCtrl:
            settingsCtrl.onSettingsChanged += self._settingsChangeHandler
        teamLives = TeamInfoLivesComponent.getInstance()
        if teamLives is not None:
            teamLives.onTeamLivesUpdated += self._onTeamLivesUpdated
        return

    def stopControl(self):
        settingsCtrl = self._sessionProvider.dynamic.vseHUDSettings
        if settingsCtrl:
            settingsCtrl.onSettingsChanged -= self._settingsChangeHandler
        teamLives = TeamInfoLivesComponent.getInstance()
        if teamLives is not None:
            teamLives.onTeamLivesUpdated -= self._onTeamLivesUpdated
        super(PveStatisticsDataController, self).stopControl()
        return

    def _settingsChangeHandler(self, settingsID):
        arenaDP = self._sessionProvider.getArenaDP()
        if settingsID == WidgetType.ENEMY_LIST:
            updatedStats = [ (INVALIDATE_OP.VEHICLE_STATS, arenaDP.getVehicleStats(vInfo.vehicleID)) for vInfo in arenaDP.getVehiclesInfoIterator() if arenaDP.isEnemyTeam(vInfo.team) ]
            self.updateVehiclesStats(updatedStats, arenaDP)
        updatedInfo = [ (INVALIDATE_OP.VEHICLE_INFO, arenaDP.getVehicleInfo(vInfo.vehicleID)) for vInfo in arenaDP.getVehiclesInfoIterator() if updatedInfoPredicate(arenaDP.isEnemyTeam(vInfo.team), settingsID) ]
        self.updateVehiclesInfo(updatedInfo, arenaDP)

    def _onTeamLivesUpdated(self):
        self._settingsChangeHandler(WidgetType.ALLY_LIST)

    def _createExchangeBroker(self, exchangeCtx):
        exchangeBroker = createExchangeBroker(exchangeCtx)
        exchangeBroker.setVehiclesInfoExchange(vehicle.VehiclesExchangeBlock(PveVehicleInfoComponent(), positionComposer=broker.BiDirectionComposer(), idsComposers=(PveTeamsSortedIDsComposer(),), statsComposers=None))
        exchangeBroker.setVehiclesStatsExchange(vehicle.VehiclesExchangeBlock(PveDynamicVehicleStatsComponent(), positionComposer=broker.BiDirectionComposer(), idsComposers=None, statsComposers=(vehicle.TotalStatsComposer(),)))
        exchangeBroker.setVehicleStatusExchange(vehicle.VehicleStatusComponent(idsComposers=(PveTeamsSortedIDsComposer(),), statsComposers=(vehicle.TotalStatsComposer(),)))
        return exchangeBroker
