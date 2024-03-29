# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/Scaleform/daapi/view/battle/players_panel.py
import BigWorld
import typing
from PlayerEvents import g_playerEvents
from battle_royale.gui.battle_control.controllers.spawn_ctrl import ISpawnListener
from constants import ARENA_BONUS_TYPE
from gui.Scaleform.daapi.view.meta.BattleRoyaleTeamPanelMeta import BattleRoyaleTeamPanelMeta
from gui.battle_control.arena_info import vos_collections
from gui.battle_control.arena_info.interfaces import IArenaVehiclesController
from gui.battle_control.controllers.battle_field_ctrl import IBattleFieldListener
from gui.clans.formatters import getClanAbbrevString
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.gui_items.Vehicle import getTypeVPanelIconPath
from helpers import dependency, int2roman
from items.battle_royale import isSpawnedBot
from items.vehicles import VehicleDescr
from skeletons.gui.battle_session import IBattleSessionProvider
if typing.TYPE_CHECKING:
    from gui.battle_control.arena_info.arena_vos import VehicleArenaInfoVO

class PlayersPanel(IBattleFieldListener, IArenaVehiclesController, ISpawnListener, BattleRoyaleTeamPanelMeta):
    __slots__ = ('__vehicleIDs', '__selectedByVehicleIds', '__spawnPointsViewActive')
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)
    _HEALTH_PERCENT = 100

    def __init__(self):
        super(PlayersPanel, self).__init__()
        self.__vehicleIDs = []
        self.__selectedByVehicleIds = set()
        self.__spawnPointsViewActive = False

    def showSpawnPoints(self):
        self.__spawnPointsViewActive = True
        self.__updateSquadStatus()

    def closeSpawnPoints(self):
        self.__spawnPointsViewActive = False
        self.__updateSquadStatus()

    def updatePoint(self, vehicleId, pointId, prevPointId):
        if pointId:
            self.__selectedByVehicleIds.add(vehicleId)
        else:
            self.__selectedByVehicleIds.discard(vehicleId)
        arenaDP = self.__sessionProvider.getArenaDP()
        vInfoVO = arenaDP.getVehicleInfo(vehicleId)
        self.__updateVehicleStatus(vInfoVO)

    def updateVehiclesStats(self, updated, arenaDP):
        for _, vStatsVO in updated:
            index = vStatsVO.vehicleID in self.__vehicleIDs and self.__vehicleIDs.index(vStatsVO.vehicleID)
            self.as_setPlayerFragsS(index, self.__getFrags(vStatsVO.frags))
            continue

    def updateVehiclesInfo(self, updated, arenaDP):
        for _, vInfoVO in updated:
            if vInfoVO.vehicleID in self.__vehicleIDs:
                index = self.__vehicleIDs.index(vInfoVO.vehicleID)
                self.as_setVehicleLevelS(index, int2roman(self._getVehicleLevel(vInfoVO)))

    def invalidateVehicleStatus(self, _, vInfoVO, __):
        self.__updateVehicleStatus(vInfoVO)

    def updateVehicleHealth(self, vehicleID, newHealth, maxHealth):
        if vehicleID in self.__vehicleIDs:
            index = self.__vehicleIDs.index(vehicleID)
            self.as_setPlayerHPS(index, self._HEALTH_PERCENT * newHealth / maxHealth)

    def _populate(self):
        super(PlayersPanel, self)._populate()
        if self.__sessionProvider.arenaVisitor.bonus.isSquadSupported():
            self.__init()
            self.__sessionProvider.addArenaCtrl(self)
            g_playerEvents.onTeamChanged += self.__onPlayerTeamChanged

    def _dispose(self):
        if self.__sessionProvider.arenaVisitor.bonus == ARENA_BONUS_TYPE.BATTLE_ROYALE_SQUAD:
            self.__sessionProvider.removeArenaCtrl(self)
            self.__vehicleIDs = None
            g_playerEvents.onTeamChanged -= self.__onPlayerTeamChanged
        super(PlayersPanel, self)._dispose()
        return

    def _getVehicleLevel(self, vInfoVO):
        descriptor = VehicleDescr(compactDescr=vInfoVO.vehicleType.strCompactDescr)
        return max(descriptor.chassis.level, descriptor.turret.level, descriptor.gun.level, descriptor.radio.level, descriptor.engine.level)

    def __onPlayerTeamChanged(self, _):
        self.__init()

    def __init(self):
        self.__initSquadPlayers()
        self.__initSquadState()

    def __initSquadPlayers(self):
        self.__vehicleIDs = []
        arenaDP = self.__sessionProvider.getArenaDP()
        collection = vos_collections.AllyItemsCollection().ids(arenaDP)
        names = []
        clans = []
        for vId in collection:
            vInfoVO = arenaDP.getVehicleInfo(vId)
            playerVehId = BigWorld.player().observedVehicleID or arenaDP.getPlayerVehicleID()
            if not vInfoVO.isObserver() and playerVehId != vId and not isSpawnedBot(vInfoVO.vehicleType.tags):
                self.__vehicleIDs.append(vId)
                names.append(vInfoVO.player.name)
                clanAbbrev = getClanAbbrevString(vInfoVO.player.clanAbbrev) if vInfoVO.player.clanAbbrev else None
                clans.append(clanAbbrev)

        self.as_setInitDataS(backport.text(R.strings.battle_royale.playersPanel.title()), names, clans)
        return

    def __initSquadState(self):
        arenaDP = self.__sessionProvider.getArenaDP()
        for index, vId in enumerate(self.__vehicleIDs):
            vInfoVO = arenaDP.getVehicleInfo(vId)
            vStatsVO = arenaDP.getVehicleStats(vId)
            level = self._getVehicleLevel(vInfoVO)
            hpPercent = 0
            if vInfoVO.isAlive():
                healthInfo = self.__sessionProvider.dynamic.battleField.getVehicleHealthInfo(vId)
                if healthInfo is not None:
                    health, maxHealth = healthInfo
                    hpPercent = self._HEALTH_PERCENT * health / maxHealth
                else:
                    hpPercent = self._HEALTH_PERCENT
            self.as_setPlayerStateS(index, vInfoVO.isAlive(), self.__isVehOpacityMax(vInfoVO), hpPercent, self.__getFrags(vStatsVO.frags), int2roman(level), getTypeVPanelIconPath(vInfoVO.vehicleType.classTag))

        return

    def __updateSquadStatus(self):
        arenaDP = self.__sessionProvider.getArenaDP()
        for vId in self.__vehicleIDs:
            vInfoVO = arenaDP.getVehicleInfo(vId)
            self.__updateVehicleStatus(vInfoVO)

    def __updateVehicleStatus(self, vInfoVO):
        if vInfoVO.vehicleID in self.__vehicleIDs:
            index = self.__vehicleIDs.index(vInfoVO.vehicleID)
            if not vInfoVO.isAlive():
                self.as_setPlayerHPS(index, 0)
            self.as_setPlayerStatusS(index, vInfoVO.isAlive(), self.__isVehOpacityMax(vInfoVO))

    def __isVehOpacityMax(self, vInfoVO):
        return vInfoVO.isReady() and not (self.__spawnPointsViewActive and vInfoVO.vehicleID not in self.__selectedByVehicleIds)

    @staticmethod
    def __getFrags(frags):
        return frags if frags != 0 else ''
