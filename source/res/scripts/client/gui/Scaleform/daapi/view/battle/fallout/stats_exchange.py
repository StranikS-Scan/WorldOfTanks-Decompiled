# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/fallout/stats_exchange.py
from collections import defaultdict
from gui import makeHtmlString
from gui.Scaleform.daapi.view.battle.shared.stats_exchage import BattleStatisticsDataController
from gui.Scaleform.daapi.view.battle.shared.stats_exchage import createExchangeBroker
from gui.Scaleform.daapi.view.battle.shared.stats_exchage import broker
from gui.Scaleform.daapi.view.battle.shared.stats_exchage import vehicle
from gui.Scaleform.locale.INGAME_GUI import INGAME_GUI
from gui.battle_control.arena_info import vos_collections
from helpers import i18n

class FalloutClassicTotalWinPoints(broker.CollectableStats):
    __slots__ = ('_personalWinPoints', '_winPoints', '_playerVehicleID')

    def __init__(self, playerVehicleID):
        super(FalloutClassicTotalWinPoints, self).__init__()
        self._personalWinPoints = 0
        self._winPoints = defaultdict(lambda : defaultdict(int))
        self._playerVehicleID = playerVehicleID

    def clear(self):
        self._personalWinPoints = 0
        self._winPoints.clear()
        super(FalloutClassicTotalWinPoints, self).clear()

    def addVehicleStatsUpdate(self, vInfoVO, vStatsVO):
        vehicleID = vStatsVO.vehicleID
        points = vStatsVO.winPoints
        if vehicleID == self._playerVehicleID:
            self._personalWinPoints = points
        self._winPoints[vInfoVO.team][vehicleID] = points

    def addVehicleStatusUpdate(self, vInfoVO):
        pass

    def getTotalStats(self, arenaDP):
        isTeamEnemy = arenaDP.isAllyTeam
        alliesPoints, enemiesPoints = (0, 0)
        for teamIdx, vehicles in self._winPoints.iteritems():
            if not vehicles:
                continue
            points = sum(vehicles.itervalues())
            if isTeamEnemy(teamIdx):
                alliesPoints += points
            enemiesPoints += points

        self._setTotalScore(alliesPoints, enemiesPoints)
        return {'personalWinPoints': self._personalWinPoints,
         'leftWinPoints': alliesPoints,
         'rightWinPoints': enemiesPoints}


class FalloutMltiteamTotalWinPoints(FalloutClassicTotalWinPoints):
    __slots__ = ('_vehiclesIDs',)

    def __init__(self, playerVehicleID):
        super(FalloutMltiteamTotalWinPoints, self).__init__(playerVehicleID)
        self._vehiclesIDs = defaultdict(list)

    def clear(self):
        self._vehiclesIDs.clear()
        super(FalloutMltiteamTotalWinPoints, self).clear()

    def addVehicleStatsUpdate(self, vInfoVO, vStatsVO):
        self._vehiclesIDs[vInfoVO.team].append(vInfoVO.vehicleID)
        super(FalloutMltiteamTotalWinPoints, self).addVehicleStatsUpdate(vInfoVO, vStatsVO)

    def getTotalStats(self, arenaDP):
        isTeamEnemy = arenaDP.isAllyTeam
        allyPoints, enemyPoints = (0, 0)
        allyLabel, enemyLabel = ('', '')
        for teamIdx, vehicles in self._winPoints.iteritems():
            if not vehicles:
                continue
            points = sum(vehicles.itervalues())
            if isTeamEnemy(teamIdx):
                allyPoints += points
            if points > enemyPoints:
                enemyPoints = points
                vInfo = arenaDP.getVehicleInfo(vehicles.keys()[0])
                if vInfo.squadIndex:
                    enemyLabel = i18n.makeString(INGAME_GUI.SCOREPANEL_SQUADLBL, sq_number=vInfo.squadIndex)
                else:
                    enemyLabel = vInfo.player.name

        if arenaDP.isSquadMan(self._playerVehicleID):
            allyLabel = i18n.makeString(INGAME_GUI.SCOREPANEL_MYSQUADLBL)
        else:
            vInfo = arenaDP.getVehicleInfo()
            allyLabel = vInfo.player.name
            if vInfo.isTeamKiller():
                allyLabel = makeHtmlString('html_templates:battle', 'fallouScorePanelTeamKiller', allyLabel)
        self._setTotalScore(allyPoints, enemyPoints)
        return {'personalWinPoints': self._personalWinPoints,
         'leftWinPoints': allyPoints,
         'rightWinPoints': enemyPoints,
         'leftLabel': allyLabel,
         'rightLabel': enemyLabel}


class FalloutMultiTeamSortedIDsComposer(vehicle.VehiclesSortedIDsComposer):

    def __init__(self, sortKey=None):
        super(FalloutMultiTeamSortedIDsComposer, self).__init__('leftItemsIDs', sortKey)

    def addSortIDs(self, isEnemy, arenaDP):
        self._items = vos_collections.FalloutMultiTeamItemsCollection(sortKey=self._sortKey).ids(arenaDP)


class FalloutMultiTeamItemsComposer(broker.SingleSideComposer):

    def __init__(self, sortKey=None):
        super(FalloutMultiTeamItemsComposer, self).__init__('leftItems', sortKey)


class FalloutStatsComponent(vehicle.VehicleStatsComponent):
    __slots__ = ('_winPoints', '_frags', '_deaths', '_damage', '_specialPoints', '_vehicleID')

    def __init__(self):
        super(FalloutStatsComponent, self).__init__()
        self._frags = 0
        self._winPoints = 0
        self._deaths = 0
        self._damage = 0
        self._specialPoints = 0

    def clear(self):
        self._frags = 0
        self._winPoints = 0
        self._deaths = 0
        self._damage = 0
        self._specialPoints = 0
        super(FalloutStatsComponent, self).clear()

    def get(self, forced=False):
        stats = {'winPoints': self._winPoints,
         'frags': self._frags,
         'deaths': self._deaths,
         'damage': self._damage,
         'specialPoints': self._specialPoints}
        if forced or sum(stats.itervalues()):
            data = super(FalloutStatsComponent, self).get()
            data.update(stats)
            return data
        return {}

    def addStats(self, vStatsVO):
        self._vehicleID = vStatsVO.vehicleID
        self._frags = vStatsVO.frags
        viStatsVO = vStatsVO.interactive
        self._winPoints = viStatsVO.winPoints
        self._deaths = viStatsVO.deathCount
        self._damage = viStatsVO.getTotalDamage()


class FalloutFlagsStatsComponent(FalloutStatsComponent):

    def addStats(self, vStatsVO):
        self._specialPoints = vStatsVO.interactive.getCapturedFlags()
        super(FalloutFlagsStatsComponent, self).addStats(vStatsVO)


class FalloutResourceStatsComponent(FalloutStatsComponent):

    def addStats(self, vStatsVO):
        self._specialPoints = vStatsVO.interactive.resourceAbsorbed
        super(FalloutResourceStatsComponent, self).addStats(vStatsVO)


class FalloutStatisticsDataController(BattleStatisticsDataController):

    def _createExchangeBroker(self, exchangeCtx):
        exchangeBroker = createExchangeBroker(exchangeCtx)
        if self._arenaVisitor.gui.isFalloutClassic():
            self.__configureClassicBroker(exchangeBroker)
        elif self._arenaVisitor.gui.isFalloutMultiTeam():
            self.__configureMultiTeamBroker(exchangeBroker)
        return exchangeBroker

    def _createExchangeCollector(self):
        if self._arenaVisitor.gui.isFalloutClassic():
            return FalloutClassicTotalWinPoints(self._personalInfo.vehicleID)
        return FalloutMltiteamTotalWinPoints(self._personalInfo.vehicleID) if self._arenaVisitor.gui.isFalloutMultiTeam() else broker.NoCollectableStats()

    def __getStatsComponentClass(self):
        if self._arenaVisitor.hasResourcePoints():
            clazz = FalloutResourceStatsComponent
        else:
            clazz = FalloutFlagsStatsComponent
        return clazz

    def __configureClassicBroker(self, exchangeBroker):
        if self._arenaVisitor.hasRespawns():
            sortKey = vos_collections.RespawnSortKey
        else:
            sortKey = vos_collections.VehicleInfoSortKey
        exchangeBroker.setVehiclesInfoExchange(vehicle.VehiclesExchangeBlock(vehicle.VehicleInfoComponent(), positionComposer=broker.BiDirectionComposer(), idsComposers=(vehicle.TeamsSortedIDsComposer(sortKey=sortKey),), statsComposers=None))
        exchangeBroker.setVehiclesStatsExchange(vehicle.VehiclesExchangeBlock(self.__getStatsComponentClass()(), positionComposer=broker.BiDirectionComposer(), idsComposers=None, statsComposers=(vehicle.TotalStatsComposer(),)))
        exchangeBroker.setVehicleStatusExchange(vehicle.VehicleStatusComponent(idsComposers=(vehicle.TeamsSortedIDsComposer(sortKey=sortKey),), statsComposers=None))
        return

    def __configureMultiTeamBroker(self, exchangeBroker):
        if self._arenaVisitor.hasRespawns():
            sortKey = vos_collections.WinPointsAndRespawnSortKey
        else:
            sortKey = vos_collections.WinPointsAndVehicleInfoSortKey
        exchangeBroker.setVehiclesInfoExchange(vehicle.VehiclesExchangeBlock(vehicle.VehicleInfoComponent(), positionComposer=FalloutMultiTeamItemsComposer(), idsComposers=(FalloutMultiTeamSortedIDsComposer(sortKey=sortKey),), statsComposers=None))
        exchangeBroker.setVehiclesStatsExchange(vehicle.VehiclesExchangeBlock(self.__getStatsComponentClass()(), positionComposer=FalloutMultiTeamItemsComposer(), idsComposers=(FalloutMultiTeamSortedIDsComposer(sortKey=sortKey),), statsComposers=(vehicle.TotalStatsComposer(),)))
        exchangeBroker.setVehicleStatusExchange(vehicle.VehicleStatusComponent(idsComposers=(FalloutMultiTeamSortedIDsComposer(sortKey=sortKey),), statsComposers=None))
        return
