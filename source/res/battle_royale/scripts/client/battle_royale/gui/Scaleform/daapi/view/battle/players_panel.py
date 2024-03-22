# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/Scaleform/daapi/view/battle/players_panel.py
import logging
from functools import partial
from sys import maxint
import BigWorld
import typing
from battle_royale.gui.Scaleform.daapi.view.battle.respawn_message_panel import RESPAWNING_TIMER_DELAY
from battle_royale.gui.Scaleform.daapi.view.battle.shared.utils import getVehicleLevel
from battle_royale.gui.battle_control.controllers.spawn_ctrl import ISpawnListener
from PlayerEvents import g_playerEvents
from gui.Scaleform.daapi.view.meta.BattleRoyaleTeamPanelMeta import BattleRoyaleTeamPanelMeta
from gui.battle_control.arena_info import vos_collections
from gui.battle_control.arena_info.interfaces import IArenaVehiclesController
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE
from gui.battle_control.controllers.battle_field_ctrl import IBattleFieldListener
from gui.clans.formatters import getClanAbbrevString
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.gui_items.Vehicle import getTypeVPanelIconPath
from helpers import dependency, int2roman
from items.battle_royale import isSpawnedBot
from skeletons.gui.battle_session import IBattleSessionProvider
if typing.TYPE_CHECKING:
    from gui.battle_control.arena_info.arena_vos import VehicleArenaInfoVO
_logger = logging.getLogger(__name__)

class PlayersPanel(IBattleFieldListener, IArenaVehiclesController, ISpawnListener, BattleRoyaleTeamPanelMeta):
    __slots__ = ('__vehicleIDs', '__selectedByVehicleIds', '__spawnPointsViewActive', '__isRespawning', '__respawningDelayCallbackID')
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)
    _HEALTH_PERCENT = 100

    def __init__(self):
        super(PlayersPanel, self).__init__()
        self.__vehicleIDs = []
        self.__selectedByVehicleIds = set()
        self.__spawnPointsViewActive = False
        self.__isRespawning = {}
        self.__respawningDelayCallbackID = None
        return

    @property
    def selfVehicleIndex(self):
        return len(self.__vehicleIDs) - 1

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
            if vStatsVO.vehicleID in self.__vehicleIDs:
                index = self.__vehicleIDs.index(vStatsVO.vehicleID)
                self.as_setPlayerFragsS(index, self.__getFrags(vStatsVO.frags))

    def updateVehiclesInfo(self, updated, arenaDP):
        for _, vInfoVO in updated:
            if vInfoVO.vehicleID in self.__vehicleIDs:
                index = self.__vehicleIDs.index(vInfoVO.vehicleID)
                self.as_setVehicleLevelS(index, int2roman(getVehicleLevel(vInfoVO.vehicleType)))
                self.__updateVehicleStatus(vInfoVO)

    def invalidateVehicleStatus(self, _, vInfoVO, __):
        self.__updateVehicleStatus(vInfoVO)

    def __clearDelayCallback(self):
        if self.__respawningDelayCallbackID is not None:
            BigWorld.cancelCallback(self.__respawningDelayCallbackID)
            self.__respawningDelayCallbackID = None
        return

    def updateTeammateRespawnTime(self, teamtimeLeft):
        self.updateRespawnTime(teamtimeLeft, selfVehicle=False)

    def updateRespawnTime(self, timeLeft, selfVehicle=True):
        if not self.__sessionProvider.arenaVisitor.bonus.isSquadSupported():
            return
        if self.__respawningDelayCallbackID:
            self.__clearDelayCallback()
        self.__respawningDelayCallbackID = BigWorld.callback(RESPAWNING_TIMER_DELAY, partial(self.updateRespawningStatus, timeLeft, selfVehicle))

    def updateRespawningStatus(self, timeLeft, selfVehicle):
        self.__respawningDelayCallbackID = None
        if not self.__vehicleIDs:
            _logger.warning('PlayersPanel vehicleIDs empty')
            return
        else:
            arenaDP = self.__sessionProvider.getArenaDP()
            index = self.selfVehicleIndex if selfVehicle else self.selfVehicleIndex - 1
            if index < 0:
                return
            vehicleID = self.__vehicleIDs[index]
            vInfoVO = arenaDP.getVehicleInfo(vehicleID)
            self.__isRespawning[index] = bool(timeLeft)
            self.__updateVehicleStatus(vInfoVO)
            return

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
            ctrl = self.__sessionProvider.shared.vehicleState
            if ctrl is not None:
                ctrl.onVehicleStateUpdated += self.__onVehicleStateUpdated
        return

    def _dispose(self):
        if self.__sessionProvider.arenaVisitor.bonus.isSquadSupported():
            self.__sessionProvider.removeArenaCtrl(self)
            self.__vehicleIDs = None
            g_playerEvents.onTeamChanged -= self.__onPlayerTeamChanged
            ctrl = self.__sessionProvider.shared.vehicleState
            if ctrl is not None:
                ctrl.onVehicleStateUpdated -= self.__onVehicleStateUpdated
        super(PlayersPanel, self)._dispose()
        return

    def __onPlayerTeamChanged(self, _):
        self.__init()

    def __init(self):
        self.__initSquadPlayers()
        self.__initSquadState()

    def __initSquadPlayers(self):
        self.__vehicleIDs = []
        arenaDP = self.__sessionProvider.getArenaDP()
        collection = vos_collections.AllyItemsCollection().ids(arenaDP)
        playerVehId = BigWorld.player().observedVehicleID or arenaDP.getPlayerVehicleID()
        collection.sort(key=lambda vId: vId if playerVehId != vId else maxint)
        names = []
        clans = []
        for vId in collection:
            vInfoVO = arenaDP.getVehicleInfo(vId)
            if not vInfoVO.isObserver() and not isSpawnedBot(vInfoVO.vehicleType.tags):
                self.__vehicleIDs.append(vId)
                names.append(vInfoVO.player.name)
                clanAbbrev = getClanAbbrevString(vInfoVO.player.clanAbbrev) if vInfoVO.player.clanAbbrev else None
                clans.append(clanAbbrev)

        playerTeam = arenaDP.getVehicleInfo(arenaDP.getPlayerVehicleID()).team
        self.as_setInitDataS(backport.text(R.strings.battle_royale.playersPanel.title()), names, clans, playerTeam)
        return

    def __initSquadState(self):
        arenaDP = self.__sessionProvider.getArenaDP()
        for index, vId in enumerate(self.__vehicleIDs):
            vInfoVO = arenaDP.getVehicleInfo(vId)
            vStatsVO = arenaDP.getVehicleStats(vId)
            level = getVehicleLevel(vInfoVO.vehicleType)
            hpPercent = 0
            if vInfoVO.isAlive():
                healthInfo = self.__sessionProvider.dynamic.battleField.getVehicleHealthInfo(vId)
                if healthInfo is not None:
                    health, maxHealth = healthInfo
                    hpPercent = self._HEALTH_PERCENT * health / maxHealth
                else:
                    hpPercent = self._HEALTH_PERCENT
            self.as_setPlayerStateS(index, vInfoVO.player.accountDBID, vId, vInfoVO.team, vInfoVO.isAlive(), self.__isVehOpacityMax(vInfoVO), hpPercent, self.__getFrags(vStatsVO.frags), int2roman(level), getTypeVPanelIconPath(vInfoVO.vehicleType.classTag))

        return

    def __updateSquadStatus(self):
        arenaDP = self.__sessionProvider.getArenaDP()
        for vId in self.__vehicleIDs:
            vInfoVO = arenaDP.getVehicleInfo(vId)
            self.__updateVehicleStatus(vInfoVO)

    def __updateVehicleStatus(self, vInfoVO):
        if vInfoVO.vehicleID in self.__vehicleIDs:
            index = self.__vehicleIDs.index(vInfoVO.vehicleID)
            isRespawning = self.__isRespawning.get(index, False)
            if not vInfoVO.isAlive():
                self.as_setPlayerHPS(index, 0)
            _logger.debug('updateRespawnTime as_setPlayerStatusS %s %s %s %s', index, vInfoVO.isAlive(), self.__isVehOpacityMax(vInfoVO), isRespawning)
            self.as_setPlayerStatusS(index, vInfoVO.isAlive(), self.__isVehOpacityMax(vInfoVO), isRespawning)

    def __isVehOpacityMax(self, vInfoVO):
        return vInfoVO.isReady() and not (self.__spawnPointsViewActive and vInfoVO.vehicleID not in self.__selectedByVehicleIds)

    @staticmethod
    def __getFrags(frags):
        return frags if frags != 0 else ''

    def __onVehicleStateUpdated(self, state, value):
        if state in (VEHICLE_VIEW_STATE.SWITCHING, VEHICLE_VIEW_STATE.RESPAWNING):
            self.__init()
