# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/Scaleform/daapi/view/battle/stats_exchange.py
import BigWorld
import BattleReplay
from gui.battle_control.arena_info.settings import VEHICLE_STATUS
from gui.battle_control.arena_info.arena_vos import VehicleArenaInfoVO
from gui.Scaleform.daapi.view.battle.shared.stats_exchange import vehicle, createExchangeBroker, broker
from gui.Scaleform.daapi.view.battle.classic.stats_exchange import ClassicStatisticsDataController, DynamicVehicleStatsComponent
from gui.battle_control.arena_info.vos_collections import VehicleInfoSortKey
from white_tiger.gui.wt_event_helpers import isBossTeam, isBoss, getSpeed
from helpers import dependency
from white_tiger.cgf_components.wt_helpers import isBossBot
from skeletons.gui.battle_session import IBattleSessionProvider
from white_tiger_common.wt_constants import WhiteTigerKeys
from white_tiger_common.wt_constants import WT_VEHICLE_TAGS
_DEFAULT_LEVEL = 0

def _isEventVehicle(vInfoVO):
    return WT_VEHICLE_TAGS.EVENT_VEHS & vInfoVO.vehicleType.tags


class WhiteTigerVehicleInfoComponent(vehicle.VehicleInfoComponent):

    def addVehicleInfo(self, vInfoVO, overrides):
        if not _isEventVehicle(vInfoVO):
            return None
        else:
            super(WhiteTigerVehicleInfoComponent, self).addVehicleInfo(vInfoVO, overrides)
            if BattleReplay.isPlaying():
                self._data.update({WhiteTigerKeys.SPEED.value: getSpeed()})
            if not isBossTeam(vInfoVO.team):
                self.__updateResurrect(vInfoVO)
            return self._data.update({'vehicleType': 'boss' if isBoss(vInfoVO.vehicleType.tags) else vInfoVO.vehicleType.getClassName(),
             'vehicleLevel': _DEFAULT_LEVEL})

    def __updateResurrect(self, vInfoVO):
        vSpecific = vInfoVO.gameModeSpecific
        self._data.update({WhiteTigerKeys.RESURRECT_TIME_LEFT.value: vSpecific.getValue(WhiteTigerKeys.RESURRECT_TIME_LEFT.value),
         WhiteTigerKeys.RESURRECT_TIME_TOTAL.value: vSpecific.getValue(WhiteTigerKeys.RESURRECT_TIME_TOTAL.value)})


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
        return vInfoVO.isAlive()


class WhiteTigerStatisticsDataController(ClassicStatisticsDataController):

    def startControl(self, battleCtx, arenaVisitor):
        super(WhiteTigerStatisticsDataController, self).startControl(battleCtx, arenaVisitor)
        wtRespawnTimeInfoComponent = BigWorld.player().arena.arenaInfo.dynamicComponents.get('wtRespawnTimeInfo')
        if wtRespawnTimeInfoComponent is not None:
            wtRespawnTimeInfoComponent.onRespawnInfoUpdated += self.__onRespawnInfoUpdated
        return

    def _createExchangeBroker(self, exchangeCtx):
        exchangeBroker = createExchangeBroker(exchangeCtx)
        exchangeBroker.setVehiclesInfoExchange(vehicle.VehiclesExchangeBlock(WhiteTigerVehicleInfoComponent(), positionComposer=broker.BiDirectionComposer(), idsComposers=(vehicle.TeamsSortedIDsComposer(WhiteTigerVehicleInfoSortKey), vehicle.TeamsCorrelationIDsComposer()), statsComposers=None))
        exchangeBroker.setVehiclesStatsExchange(vehicle.VehiclesExchangeBlock(WhiteTigerVehicleStatsComponent(), positionComposer=broker.BiDirectionComposer(), idsComposers=None, statsComposers=(vehicle.TotalStatsComposer(),)))
        exchangeBroker.setVehicleStatusExchange(WhiteTigerVehicleStatusComponent(idsComposers=(vehicle.TeamsSortedIDsComposer(WhiteTigerVehicleInfoSortKey), vehicle.TeamsCorrelationIDsComposer()), statsComposers=(vehicle.TotalStatsComposer(),)))
        return exchangeBroker

    def __onRespawnInfoUpdated(self, vehiclesIDs):
        arenaDP = self._battleCtx.getArenaDP()
        self.updateVehiclesInfo([ (0, arenaDP.getVehicleInfo(vID)) for vID in vehiclesIDs ], arenaDP)

    def updateVehiclesInfo(self, updated, arenaDP):
        wtRespawnTimeInfoComponent = BigWorld.player().arena.arenaInfo.dynamicComponents.get('wtRespawnTimeInfo')
        customUpdate = []
        for flag, vInfoVO in updated:
            oldTimeLeftValue = vInfoVO.gameModeSpecific.getValue(WhiteTigerKeys.RESURRECT_TIME_LEFT.value)
            if oldTimeLeftValue or not isBossTeam(vInfoVO.team):
                vehicleID = vInfoVO.vehicleID
                actualLeftTime, actualData = self.__getActualSpawnTimeData(wtRespawnTimeInfoComponent, vehicleID, vInfoVO)
                if oldTimeLeftValue != actualLeftTime:
                    flag, vInfoVO = arenaDP.updateGameModeSpecificStats(vehicleID, True, actualData)
            customUpdate.append((flag, vInfoVO))

        if customUpdate:
            super(WhiteTigerStatisticsDataController, self).updateVehiclesInfo(customUpdate, arenaDP)

    def __getActualSpawnTimeData(self, wtRespawnTimeInfoComponent, vehicleID, vInfoVO):
        endTime, totalTime = wtRespawnTimeInfoComponent.getRespawnInfo(vehicleID)
        leftTime = endTime - BigWorld.serverTime()
        if leftTime < 0 or vInfoVO.isAlive():
            leftTime = 0
        return (leftTime, {WhiteTigerKeys.RESURRECT_TIME_LEFT.value: leftTime,
          WhiteTigerKeys.RESURRECT_TIME_TOTAL.value: totalTime})


class WhiteTigerVehicleInfoSortKey(VehicleInfoSortKey):
    __slots__ = ('_sortAlive',)

    def __init__(self, item):
        super(WhiteTigerVehicleInfoSortKey, self).__init__(item)
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
