# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/ranked/stats_exchange.py
import typing
import VOIP
from gui.Scaleform.daapi.view.battle.classic.stats_exchange import ClassicStatisticsDataController, DynamicVehicleStatsComponent
from gui.Scaleform.daapi.view.battle.shared.stats_exchange import broker
from gui.Scaleform.daapi.view.battle.shared.stats_exchange import createExchangeBroker
from gui.Scaleform.daapi.view.battle.shared.stats_exchange import vehicle
from gui.battle_control.arena_info import vos_collections
from gui.battle_control.arena_info.arena_vos import RankedKeys
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from skeletons.gui.game_control import IRankedBattlesController
if typing.TYPE_CHECKING:
    from gui.battle_control.arena_info.interfaces import IRankedVOIPController

class RankedVehicleInfoComponent(vehicle.VehicleInfoComponent):
    __rankedController = dependency.descriptor(IRankedBattlesController)
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def addVehicleInfo(self, vInfoVO, overrides):
        super(RankedVehicleInfoComponent, self).addVehicleInfo(vInfoVO, overrides)
        displayInfo = self.__rankedController.getRankDisplayInfoForBattle(vInfoVO.ranked.rank)
        return self._data.update({'level': displayInfo.level,
         'division': displayInfo.division,
         'isGroup': displayInfo.isGroup,
         'voiceChatConnected': self.__getVoiceChatConnected(vInfoVO)})

    @classmethod
    def __getVoiceChatConnected(cls, vInfoVO):
        voipCtrl = cls.__sessionProvider.dynamic.rankedVOIPController
        if voipCtrl is None or not voipCtrl.isTeamVoipEnabled:
            return True
        else:
            return True if vInfoVO.isEnemy() or not vInfoVO.isPlayer() else vInfoVO.gameModeSpecific.getValue(RankedKeys.VOIP_CONNECTED, default=False)


class RankedStatisticsDataController(ClassicStatisticsDataController):

    def _createExchangeBroker(self, exchangeCtx):
        exchangeBroker = createExchangeBroker(exchangeCtx)
        exchangeBroker.setVehiclesInfoExchange(vehicle.VehiclesExchangeBlock(RankedVehicleInfoComponent(), positionComposer=broker.BiDirectionComposer(), idsComposers=(vehicle.TeamsSortedIDsComposer(sortKey=vos_collections.RankSortKey), vehicle.TeamsCorrelationIDsComposer()), statsComposers=None))
        exchangeBroker.setVehiclesStatsExchange(vehicle.VehiclesExchangeBlock(DynamicVehicleStatsComponent(), positionComposer=broker.BiDirectionComposer(), idsComposers=None, statsComposers=(vehicle.TotalStatsComposer(),)))
        exchangeBroker.setVehicleStatusExchange(vehicle.VehicleStatusComponent(idsComposers=(vehicle.TeamsSortedIDsComposer(sortKey=vos_collections.RankSortKey), vehicle.TeamsCorrelationIDsComposer()), statsComposers=(vehicle.TotalStatsComposer(),)))
        return exchangeBroker

    def startControl(self, battleCtx, arenaVisitor):
        super(RankedStatisticsDataController, self).startControl(battleCtx, arenaVisitor)
        voipMgr = VOIP.getVOIPManager()
        if voipMgr is not None:
            voipMgr.onChannelAvailable += self.__onChannelUpdated
            voipMgr.onChannelLost += self.__onChannelUpdated
        return

    def stopControl(self):
        voipMgr = VOIP.getVOIPManager()
        if voipMgr is not None:
            voipMgr.onChannelAvailable -= self.__onChannelUpdated
            voipMgr.onChannelLost -= self.__onChannelUpdated
        super(RankedStatisticsDataController, self).stopControl()
        return

    def __onChannelUpdated(self, *_, **__):
        self.invalidateVehiclesInfo(self.sessionProvider.getArenaDP())
