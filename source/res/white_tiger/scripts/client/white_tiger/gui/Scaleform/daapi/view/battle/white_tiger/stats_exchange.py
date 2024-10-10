# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/Scaleform/daapi/view/battle/white_tiger/stats_exchange.py
import BigWorld
import BattleReplay
from gui.battle_control.arena_info.settings import VEHICLE_STATUS
from gui.battle_control.arena_info.arena_vos import EventKeys
from gui.Scaleform.daapi.view.battle.shared.stats_exchange import vehicle, createExchangeBroker, broker
from gui.Scaleform.daapi.view.battle.classic.stats_exchange import ClassicStatisticsDataController, DynamicVehicleStatsComponent
from gui.shared.gui_items.Vehicle import VEHICLE_TAGS
from gui.wt_event.wt_event_helpers import isBossTeam, isBoss, getSpeed
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
_DEFAULT_LEVEL = 0

def _isEventVehicle(vInfoVO):
    return VEHICLE_TAGS.WT_VEHICLES & vInfoVO.vehicleType.tags


class WhiteTigerVehicleInfoComponent(vehicle.VehicleInfoComponent):

    def addVehicleInfo(self, vInfoVO, overrides):
        if not _isEventVehicle(vInfoVO):
            return None
        else:
            super(WhiteTigerVehicleInfoComponent, self).addVehicleInfo(vInfoVO, overrides)
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


class WhiteTigerVehicleStatsComponent(DynamicVehicleStatsComponent):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def addStats(self, vStatsVO):
        arenaDP = self.__sessionProvider.getArenaDP()
        vInfoVO = arenaDP.getVehicleInfo(vStatsVO.vehicleID)
        if not _isEventVehicle(vInfoVO):
            return
        super(WhiteTigerVehicleStatsComponent, self).addStats(vStatsVO)


class WhiteTigerVehicleStatusComponent(vehicle.VehicleStatusComponent):

    def addVehicleInfo(self, vInfoVO):
        if not _isEventVehicle(vInfoVO):
            return
        super(WhiteTigerVehicleStatusComponent, self).addVehicleInfo(vInfoVO)
        if not isBossTeam(vInfoVO.team):
            if self.__isAlive(vInfoVO):
                self._status |= VEHICLE_STATUS.IS_ALIVE

    def __isAlive(self, vInfoVO):
        teamLivesComponent = BigWorld.player().arena.arenaInfo.dynamicComponents.get('teamLivesComponent')
        return teamLivesComponent.getLives(vInfoVO.vehicleID) > 0 if teamLivesComponent else vInfoVO.isAlive()


class WhiteTigerStatisticsDataController(ClassicStatisticsDataController):

    def startControl(self, battleCtx, arenaVisitor):
        super(WhiteTigerStatisticsDataController, self).startControl(battleCtx, arenaVisitor)
        teleport = self.sessionProvider.dynamic.teleport
        if teleport is not None:
            teleport.onTeamRespawnInfoUpdated += self.__onTeamRespawnInfoUpdated
        return

    def stopControl(self):
        teleport = self.sessionProvider.dynamic.teleport
        if teleport is not None:
            teleport.onTeamRespawnInfoUpdated -= self.__onTeamRespawnInfoUpdated
        super(WhiteTigerStatisticsDataController, self).stopControl()
        return

    def _createExchangeBroker(self, exchangeCtx):
        exchangeBroker = createExchangeBroker(exchangeCtx)
        exchangeBroker.setVehiclesInfoExchange(vehicle.VehiclesExchangeBlock(WhiteTigerVehicleInfoComponent(), positionComposer=broker.BiDirectionComposer(), idsComposers=(vehicle.TeamsSortedIDsComposer(), vehicle.TeamsCorrelationIDsComposer()), statsComposers=None))
        exchangeBroker.setVehiclesStatsExchange(vehicle.VehiclesExchangeBlock(WhiteTigerVehicleStatsComponent(), positionComposer=broker.BiDirectionComposer(), idsComposers=None, statsComposers=(vehicle.TotalStatsComposer(),)))
        exchangeBroker.setVehicleStatusExchange(WhiteTigerVehicleStatusComponent(idsComposers=(vehicle.TeamsSortedIDsComposer(), vehicle.TeamsCorrelationIDsComposer()), statsComposers=(vehicle.TotalStatsComposer(),)))
        return exchangeBroker

    def __onTeamRespawnInfoUpdated(self, vehiclesIDs):
        updated = []
        teamLivesComponent = BigWorld.player().arena.arenaInfo.dynamicComponents.get('teamLivesComponent')
        arenaDP = self._battleCtx.getArenaDP()
        for vID in vehiclesIDs:
            vInfo = arenaDP.getVehicleInfo(vID)
            if not isBossTeam(vInfo.team) and teamLivesComponent:
                vehicleID = vInfo.vehicleID
                _, updatedData = self.__getActualSpawnTimeData(teamLivesComponent, vehicleID)
                updated.append(arenaDP.updateGameModeSpecificStats(vehicleID, True, updatedData))

        if updated:
            super(WhiteTigerStatisticsDataController, self).updateVehiclesInfo(updated, arenaDP)

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

        super(WhiteTigerStatisticsDataController, self).updateVehiclesInfo(customUpdate, arenaDP)

    def invalidateVehicleStatus(self, flags, vo, arenaDP):
        super(WhiteTigerStatisticsDataController, self).invalidateVehicleStatus(flags, vo, arenaDP)
        self.__onTeamRespawnInfoUpdated([vo.vehicleID])

    def __getActualSpawnTimeData(self, teamLivesComponent, vehicleID):
        endTime, totalTime = teamLivesComponent.getRespawnInfo(vehicleID)
        leftTime = endTime - BigWorld.serverTime()
        if leftTime < 0:
            leftTime = 0
        return (leftTime, {EventKeys.RESURRECT_TIME_LEFT.value: leftTime,
          EventKeys.RESURRECT_TIME_TOTAL.value: totalTime})
