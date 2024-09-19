# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/stats_exchange.py
import BigWorld
import BattleReplay
from gui.battle_control.arena_info.settings import VEHICLE_STATUS
from gui.battle_control.arena_info.arena_vos import EventKeys, VehicleArenaInfoVO
from gui.Scaleform.daapi.view.battle.shared.stats_exchange import vehicle, createExchangeBroker, broker
from gui.Scaleform.daapi.view.battle.classic.stats_exchange import ClassicStatisticsDataController, DynamicVehicleStatsComponent
from gui.battle_control.arena_info.vos_collections import VehicleInfoSortKey
from gui.battle_control.controllers.players_panel_ctrl import isBossBot
from gui.shared.gui_items.Vehicle import VEHICLE_TAGS
from gui.wt_event.wt_event_helpers import isBossTeam, isBoss, getSpeed
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
_DEFAULT_LEVEL = 0

def _isEventVehicle(vInfoVO):
    return VEHICLE_TAGS.EVENT_VEHS & vInfoVO.vehicleType.tags


class EventVehicleInfoComponent(vehicle.VehicleInfoComponent):

    def addVehicleInfo(self, vInfoVO, overrides):
        if not _isEventVehicle(vInfoVO):
            return None
        else:
            super(EventVehicleInfoComponent, self).addVehicleInfo(vInfoVO, overrides)
            if BattleReplay.isPlaying():
                self._data.update({EventKeys.SPEED.value: getSpeed()})
            if not isBossTeam(vInfoVO.team):
                self.__updateResurrect(vInfoVO)
                self.__updatePlasmaCount(vInfoVO)
            return self._data.update({'vehicleType': 'boss' if isBoss(vInfoVO.vehicleType.tags) else vInfoVO.vehicleType.getClassName(),
             'vehicleLevel': _DEFAULT_LEVEL})

    def __updateResurrect(self, vInfoVO):
        vSpecific = vInfoVO.gameModeSpecific
        self._data.update({EventKeys.RESURRECT_TIME_LEFT.value: vSpecific.getValue(EventKeys.RESURRECT_TIME_LEFT.value),
         EventKeys.RESURRECT_TIME_TOTAL.value: vSpecific.getValue(EventKeys.RESURRECT_TIME_TOTAL.value)})

    def __updatePlasmaCount(self, vInfoVO):
        vSpecific = vInfoVO.gameModeSpecific
        self._data.update({EventKeys.PLASMA_COUNT.value: vSpecific.getValue(EventKeys.PLASMA_COUNT.value) if vSpecific else 0})


class EventVehicleStatsComponent(DynamicVehicleStatsComponent):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def addStats(self, vStatsVO):
        arenaDP = self.__sessionProvider.getArenaDP()
        vInfoVO = arenaDP.getVehicleInfo(vStatsVO.vehicleID)
        if not _isEventVehicle(vInfoVO):
            return
        super(EventVehicleStatsComponent, self).addStats(vStatsVO)


class EventVehicleStatusComponent(vehicle.VehicleStatusComponent):

    def addVehicleInfo(self, vInfoVO):
        if not _isEventVehicle(vInfoVO):
            return
        super(EventVehicleStatusComponent, self).addVehicleInfo(vInfoVO)
        if not isBossTeam(vInfoVO.team):
            if self.__isAlive(vInfoVO):
                self._status |= VEHICLE_STATUS.IS_ALIVE

    def __isAlive(self, vInfoVO):
        teamLivesComponent = BigWorld.player().arena.arenaInfo.dynamicComponents.get('teamLivesComponent')
        return teamLivesComponent.getLives(vInfoVO.vehicleID) > 0 if teamLivesComponent else vInfoVO.isAlive()


class EventStatisticsDataController(ClassicStatisticsDataController):

    def startControl(self, battleCtx, arenaVisitor):
        super(EventStatisticsDataController, self).startControl(battleCtx, arenaVisitor)
        teleport = self.sessionProvider.dynamic.teleport
        if teleport is not None:
            teleport.onTeamRespawnInfoUpdated += self.__onTeamRespawnInfoUpdated
        return

    def stopControl(self):
        teleport = self.sessionProvider.dynamic.teleport
        if teleport is not None:
            teleport.onTeamRespawnInfoUpdated -= self.__onTeamRespawnInfoUpdated
        super(EventStatisticsDataController, self).stopControl()
        return

    def _createExchangeBroker(self, exchangeCtx):
        exchangeBroker = createExchangeBroker(exchangeCtx)
        exchangeBroker.setVehiclesInfoExchange(vehicle.VehiclesExchangeBlock(EventVehicleInfoComponent(), positionComposer=broker.BiDirectionComposer(), idsComposers=(vehicle.TeamsSortedIDsComposer(EventVehicleInfoSortKey), vehicle.TeamsCorrelationIDsComposer()), statsComposers=None))
        exchangeBroker.setVehiclesStatsExchange(vehicle.VehiclesExchangeBlock(EventVehicleStatsComponent(), positionComposer=broker.BiDirectionComposer(), idsComposers=None, statsComposers=(vehicle.TotalStatsComposer(),)))
        exchangeBroker.setVehicleStatusExchange(EventVehicleStatusComponent(idsComposers=(vehicle.TeamsSortedIDsComposer(EventVehicleInfoSortKey), vehicle.TeamsCorrelationIDsComposer()), statsComposers=(vehicle.TotalStatsComposer(),)))
        return exchangeBroker

    def __onTeamRespawnInfoUpdated(self, vehiclesIDs):
        updated = []
        teamLivesComponent = BigWorld.player().arena.arenaInfo.dynamicComponents.get('teamLivesComponent')
        arenaDP = self._battleCtx.getArenaDP()
        for vID in vehiclesIDs:
            vInfo = arenaDP.getVehicleInfo(vID)
            if not isBossTeam(vInfo.team):
                vehicleID = vInfo.vehicleID
                _, updatedData = self.__getActualSpawnTimeData(teamLivesComponent, vehicleID)
                updated.append(arenaDP.updateGameModeSpecificStats(vehicleID, True, updatedData))

        if updated:
            super(EventStatisticsDataController, self).updateVehiclesInfo(updated, arenaDP)

    def updateVehiclesInfo(self, updated, arenaDP):
        teamLivesComponent = BigWorld.player().arena.arenaInfo.dynamicComponents.get('teamLivesComponent')
        customUpdate = []
        for flag, vInfoVO in updated:
            oldTimeLeftValue = vInfoVO.gameModeSpecific.getValue(EventKeys.RESURRECT_TIME_LEFT.value)
            if oldTimeLeftValue:
                vehicleID = vInfoVO.vehicleID
                actualLeftTime, actualData = self.__getActualSpawnTimeData(teamLivesComponent, vehicleID)
                if oldTimeLeftValue != actualLeftTime:
                    flag, vInfoVO = arenaDP.updateGameModeSpecificStats(vehicleID, True, actualData)
            customUpdate.append((flag, vInfoVO))

        super(EventStatisticsDataController, self).updateVehiclesInfo(customUpdate, arenaDP)

    def __getActualSpawnTimeData(self, teamLivesComponent, vehicleID):
        endTime, totalTime = teamLivesComponent.getRespawnInfo(vehicleID)
        leftTime = endTime - BigWorld.serverTime()
        if leftTime < 0:
            leftTime = 0
        return (leftTime, {EventKeys.RESURRECT_TIME_LEFT.value: leftTime,
          EventKeys.RESURRECT_TIME_TOTAL.value: totalTime})


class EventVehicleInfoSortKey(VehicleInfoSortKey):
    __slots__ = ('_sortAlive',)

    def __init__(self, item):
        super(EventVehicleInfoSortKey, self).__init__(item)
        self._sortAlive = True

    def _cmp(self, other):
        aInfo = self.vInfoVO
        bInfo = other.vInfoVO
        result = cmp(aInfo.team, bInfo.team)
        if result:
            return result
        result = cmp(isBossBot(vInfo=aInfo), isBossBot(vInfo=bInfo))
        if result:
            return result
        if self._sortAlive:
            result = -cmp(aInfo.isAlive(), bInfo.isAlive())
            if result:
                return result
        result = cmp(aInfo.player.isBot, bInfo.player.isBot)
        if result:
            return result
        result = cmp(aInfo.vehicleType.getOrderByClass(), bInfo.vehicleType.getOrderByClass())
        if result:
            return result
        result = cmp(aInfo.vehicleType.shortName, bInfo.vehicleType.shortName)
        return result if result else cmp(aInfo.player, bInfo.player)
