# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/classic/stats_exchange.py
from collections import defaultdict
from account_helpers.settings_core.settings_constants import BattleCommStorageKeys
from gui.Scaleform.daapi.view.battle.shared.stats_exchage import BattleStatisticsDataController
from gui.Scaleform.daapi.view.battle.shared.stats_exchage import createExchangeBroker
from gui.Scaleform.daapi.view.battle.shared.stats_exchage import broker
from gui.Scaleform.daapi.view.battle.shared.stats_exchage import vehicle
from gui.battle_control.arena_info.arena_vos import ChatCommandVO
from skeletons.account_helpers.settings_core import ISettingsCore
from helpers import dependency

class FragsCollectableStats(broker.CollectableStats):
    __slots__ = ('__teamsDeaths',)

    def __init__(self):
        super(FragsCollectableStats, self).__init__()
        self.__teamsDeaths = defaultdict(set)

    def clear(self):
        self.__teamsDeaths.clear()
        super(FragsCollectableStats, self).clear()

    def addVehicleStatsUpdate(self, vInfoVO, vStatsVO):
        self.addVehicleStatusUpdate(vInfoVO)

    def addVehicleStatusUpdate(self, vInfoVO):
        if not vInfoVO.isAlive():
            self.__teamsDeaths[vInfoVO.team].add(vInfoVO.vehicleID)

    def getTotalStats(self, arenaVisitor, sessionProvider):
        arenaDP = sessionProvider.getArenaDP()
        isEnemyTeam = arenaDP.isEnemyTeam
        allyScope, enemyScope = (0, 0)
        for teamIdx, vehicleIDs in self.__teamsDeaths.iteritems():
            score = len(vehicleIDs)
            if isEnemyTeam(teamIdx):
                allyScope += score
            enemyScope += score

        self._setTotalScore(allyScope, enemyScope)
        return {'leftScope': allyScope,
         'rightScope': enemyScope} if allyScope or enemyScope else {}


class DynamicVehicleStatsComponent(vehicle.VehicleStatsComponent):
    settingsCore = dependency.descriptor(ISettingsCore)
    __slots__ = ('_frags', '_vehicleID', '_chatCommand', '_chatCommandFlags')

    def __init__(self):
        super(DynamicVehicleStatsComponent, self).__init__()
        self._frags = 0
        self._chatCommand = ''
        self._chatCommandFlags = 0

    def clear(self):
        self._frags = 0
        self._chatCommand = ''
        self._chatCommandFlags = 0
        super(DynamicVehicleStatsComponent, self).clear()

    def get(self, forced=False):
        if forced or self._frags:
            data = super(DynamicVehicleStatsComponent, self).get()
            data['frags'] = self._frags
            data['chatCommand'] = self._chatCommand
            data['chatCommandFlags'] = self._chatCommandFlags
            return data
        return {}

    def addStats(self, vStatsVO):
        self._vehicleID = vStatsVO.vehicleID
        self._frags = vStatsVO.frags
        chatCmdState = vStatsVO.chatCommandState
        if chatCmdState and bool(self.settingsCore.getSetting(BattleCommStorageKeys.SHOW_COM_IN_PLAYER_LIST)) is True:
            self._chatCommand = chatCmdState.activeChatCommand
            self._chatCommandFlags = chatCmdState.chatCommandFlags


class ClassicStatisticsDataController(BattleStatisticsDataController):

    def _createExchangeBroker(self, exchangeCtx):
        exchangeBroker = createExchangeBroker(exchangeCtx)
        exchangeBroker.setVehiclesInfoExchange(vehicle.VehiclesExchangeBlock(vehicle.VehicleInfoComponent(), positionComposer=broker.BiDirectionComposer(), idsComposers=(vehicle.TeamsSortedIDsComposer(), vehicle.TeamsCorrelationIDsComposer()), statsComposers=None))
        exchangeBroker.setVehiclesStatsExchange(vehicle.VehiclesExchangeBlock(DynamicVehicleStatsComponent(), positionComposer=broker.BiDirectionComposer(), idsComposers=None, statsComposers=(vehicle.TotalStatsComposer(),)))
        exchangeBroker.setVehicleStatusExchange(vehicle.VehicleStatusComponent(idsComposers=(vehicle.TeamsSortedIDsComposer(), vehicle.TeamsCorrelationIDsComposer()), statsComposers=(vehicle.TotalStatsComposer(),)))
        return exchangeBroker

    def _createExchangeCollector(self):
        return FragsCollectableStats()
