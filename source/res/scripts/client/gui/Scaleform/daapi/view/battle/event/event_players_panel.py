# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/event_players_panel.py
import BigWorld
from constants import ARENA_PERIOD
from gui.battle_control import avatar_getter
from gui.battle_control.arena_info.interfaces import IArenaVehiclesController
from gui.battle_control.arena_info.settings import ARENA_LISTENER_SCOPE as _SCOPE
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from gui.Scaleform.daapi.view.meta.EventPlayersPanelMeta import EventPlayersPanelMeta
from helpers import dependency, i18n, isPlayerAvatar
from skeletons.gui.battle_session import IBattleSessionProvider
from gui.Scaleform.locale.EVENT import EVENT
from PlayerEvents import g_playerEvents

class EventPlayersPanel(EventPlayersPanelMeta, IArenaVehiclesController):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(EventPlayersPanel, self).__init__()
        self._botsCache = {}
        self.__arenaDP = self.sessionProvider.getArenaDP()
        self._teammateVehiclesHealth = None
        return

    def getControllerID(self):
        return BATTLE_CTRL_ID.GUI

    def getCtrlScope(self):
        return _SCOPE.VEHICLES

    def invalidateVehiclesInfo(self, _):
        self.__updateBots()
        self.__updtateAllTeammates()

    def addVehicleInfo(self, vInfo, _):
        self.__updateBot(vInfo)
        self.__updateTeammate(vInfo)

    def invalidateVehicleStatus(self, flags, vInfo, arenaDP):
        if vInfo and vInfo.vehicleID in self._botsCache:
            if not vInfo.isAlive():
                self.as_setBotDeadS(vInfo.vehicleID)

    def invalidateArenaInfo(self):
        self.invalidateVehiclesInfo(self.sessionProvider.getArenaDP())

    def updateVehiclesInfo(self, updated, arenaDP):
        for _, vInfo in updated:
            self.__updateTeammate(vInfo)

    def _populate(self):
        super(EventPlayersPanel, self)._populate()
        self.as_setPlayerPanelDescriptionsS(i18n.makeString(EVENT.BUTTON_DESCRIPTION_TAB), i18n.makeString(EVENT.BUTTON_DESCRIPTION_Z))
        ctrl = self.sessionProvider.dynamic.respawn
        if ctrl is not None:
            ctrl.onTeammateRespawnLivesUpdated += self.__onTeammateRespawnLivesUpdated
        componentSystem = self.sessionProvider.arenaVisitor.getComponentSystem()
        gameEventStorage = getattr(componentSystem, 'gameEventComponent', None)
        if gameEventStorage:
            self._teammateVehiclesHealth = gameEventStorage.getTeammateVehicleHealth()
            self._teammateVehiclesHealth.onTeammateVehicleHealthUpdate += self.__onTeammateVehicleHealthUpdate
        self.sessionProvider.addArenaCtrl(self)
        if isPlayerAvatar():
            player = BigWorld.player()
            player.onDamageByVehTypeChanged += self.__onDamageByVehTypeChanged
        g_playerEvents.onArenaPeriodChange += self.__onArenaPeriodChange
        self.__updateBots()
        self.__updtateAllTeammates()
        return

    def _dispose(self):
        ctrl = self.sessionProvider.dynamic.respawn
        if ctrl is not None:
            ctrl.onTeammateRespawnLivesUpdated -= self.__onTeammateRespawnLivesUpdated
        componentSystem = self.sessionProvider.arenaVisitor.getComponentSystem()
        gameEventStorage = getattr(componentSystem, 'gameEventComponent', None)
        if gameEventStorage:
            self._teammateVehiclesHealth = gameEventStorage.getTeammateVehicleHealth()
            self._teammateVehiclesHealth.onTeammateVehicleHealthUpdate -= self.__onTeammateVehicleHealthUpdate
        self.sessionProvider.removeArenaCtrl(self)
        if isPlayerAvatar():
            player = BigWorld.player()
            player.onDamageByVehTypeChanged -= self.__onDamageByVehTypeChanged
        self._botsCache = None
        g_playerEvents.onArenaPeriodChange -= self.__onArenaPeriodChange
        super(EventPlayersPanel, self)._dispose()
        return

    def __onArenaPeriodChange(self, period, periodEndTime, periodLength, periodAdditionalInfo):
        if period == ARENA_PERIOD.BATTLE:
            self.__updtateAllTeammates()

    def __onTeammateRespawnLivesUpdated(self, vehID, respawnLives):
        if respawnLives > 0:
            self.as_setPlayerPanelCountLivesS(vehID, respawnLives)
        else:
            self.as_setPlayerDeadS(vehID)

    def __onDamageByVehTypeChanged(self):
        self.__updateBots()

    def __updateBots(self):
        for vInfo in self.__arenaDP.getVehiclesInfoIterator():
            self.__updateBot(vInfo)

    def __updateBot(self, vInfo):
        player = BigWorld.player()
        isEnemy = vInfo.team != player.team
        if isEnemy and player.damageByVehType:
            vehicleID = vInfo.vehicleID
            if vehicleID not in self._botsCache:
                damage = player.damageByVehType.get(vInfo.vehicleType.compactDescr, 1)
                vType = vInfo.vehicleType
                self.as_setBotPanelInfoS(vehicleID, damage, vType.shortName, vType.classTag)
                self._botsCache[vehicleID] = vInfo
            if not vInfo.isAlive():
                self.as_setBotDeadS(vehicleID)

    def __updtateAllTeammates(self):
        for vInfo in self.__arenaDP.getVehiclesInfoIterator():
            self.__updateTeammate(vInfo)

    def __updateTeammate(self, vInfo):
        if vInfo.player.accountDBID > 0 and vInfo.team == self.__arenaDP.getAllyTeams()[0]:
            ctrl = self.sessionProvider.dynamic.respawn
            if ctrl is None or self._teammateVehiclesHealth is None:
                return
            teammateRespawnLives = ctrl.teammateRespawnLives
            hpCurrent = self._teammateVehiclesHealth.getTeammateHealth(vInfo.vehicleID)
            countLives = teammateRespawnLives.get(vInfo.vehicleID, 0)
            playerVehicleID = avatar_getter.getPlayerVehicleID()
            playerSquad = self.__arenaDP.getVehicleInfo(playerVehicleID).squadIndex
            isSquad = False
            if playerSquad > 0 and playerSquad == vInfo.squadIndex or playerSquad == 0 and vInfo.vehicleID == playerVehicleID:
                isSquad = True
            self.as_setPlayerPanelInfoS({'vehID': vInfo.vehicleID,
             'name': vInfo.player.name,
             'nameVehicle': vInfo.vehicleType.shortName,
             'typeVehicle': vInfo.vehicleType.classTag,
             'hpMax': vInfo.vehicleType.maxHealth,
             'hpCurrent': hpCurrent,
             'countLives': countLives,
             'isSquad': isSquad})
        return

    def __onTeammateVehicleHealthUpdate(self, diff):
        for vehID, newHealth in diff.items():
            vInfo = self.__arenaDP.getVehicleInfo(vehID)
            self.as_setPlayerPanelHpS(vehID, vInfo.vehicleType.maxHealth, newHealth)
