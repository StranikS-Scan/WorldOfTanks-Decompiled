# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/Scaleform/daapi/view/battle/observer_players_panel.py
import BigWorld
from battle_royale.gui.Scaleform.daapi.view.battle.shared.utils import getVehicleLevel
from Event import EventsSubscriber
from aih_constants import CTRL_MODE_NAME
from arena_bonus_type_caps import ARENA_BONUS_TYPE
from gui.Scaleform.daapi.view.meta.BattleRoyalePlayersPanelMeta import BattleRoyalePlayersPanelMeta
from gui.battle_control import avatar_getter
from gui.battle_control.arena_info.interfaces import IArenaVehiclesController
from gui.battle_control.controllers.battle_field_ctrl import IBattleFieldListener
from gui.shared.gui_items.Vehicle import getTypeVPanelIconPath
from helpers import dependency, int2roman
from skeletons.gui.battle_session import IBattleSessionProvider

def _comapareAndSet(data, key, value):
    if value != data[key]:
        data[key] = value
        return True
    return False


class ObserverPlayersPanel(IBattleFieldListener, IArenaVehiclesController, BattleRoyalePlayersPanelMeta):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(ObserverPlayersPanel, self).__init__()
        self.__isSyncPlayerList = False
        self.__observedVehID = None
        self.__es = EventsSubscriber()
        self.__playerList = {}
        return

    def switchToPlayer(self, vehicleID):
        handler = avatar_getter.getInputHandler()
        modeName = handler.ctrlModeName if handler is not None else ''
        arenaDP = self.__sessionProvider.getArenaDP()
        vehInfo = arenaDP.getVehicleInfo(vehicleID)
        if vehInfo.isAlive() and modeName != CTRL_MODE_NAME.VIDEO:
            if handler.isControlModeChangeAllowed():
                self.__sessionProvider.shared.viewPoints.selectVehicle(vehicleID)
        return

    def updateVehiclesStats(self, updatedItems, arenaDP):
        updated = False
        for _, vStatsVO in updatedItems:
            updated |= self.__updateStats(vStatsVO)

        if updated:
            self.__panelUpdate()

    def invalidateVehicleStatus(self, flags, vInfoVO, arenaDP):
        if self.__updateInfo(vInfoVO):
            self.__panelUpdate()

    def updateVehiclesInfo(self, updatedItems, arenaDP):
        updated = False
        for _, vInfoVO in updatedItems:
            updated |= self.__updateInfo(vInfoVO)

        if updated:
            self.__panelUpdate()

    def _populate(self):
        super(ObserverPlayersPanel, self)._populate()
        self.__isSyncPlayerList = BigWorld.player().observerSeesAll()
        if not self.__isSyncPlayerList:
            self.__isSyncPlayerList = avatar_getter.isBecomeObserverAfterDeath()
        if self.__isSyncPlayerList:
            self.__init()
            self.__sessionProvider.addArenaCtrl(self)
            self.__es.subscribeToEvent(BigWorld.player().onObserverVehicleChanged, self.__onObserverVehicleChanged)
            battleRoyaleComponent = self.__sessionProvider.arenaVisitor.getComponentSystem().battleRoyaleComponent
            self.__es.subscribeToEvent(battleRoyaleComponent.onBattleRoyaleDefeatedTeamsUpdate, self.__onTeamDeath)
            self.__es.subscribeToEvent(battleRoyaleComponent.onRespawnTimeFinished, self.__onRespawnTimeFinished)
            from BattleRoyaleObserverInfoComponent import BattleRoyaleObserverInfoComponent
            self.__es.subscribeToEvent(BattleRoyaleObserverInfoComponent.onTeamsMayRespawnChanged, self.__onTeamsMayRespawnChanged)

    def _dispose(self):
        if self.__isSyncPlayerList:
            self.__sessionProvider.removeArenaCtrl(self)
            self.__es.unsubscribeFromAllEvents()
        self.__playerList = {}
        super(ObserverPlayersPanel, self)._dispose()

    def __onTeamDeath(self, defeatedTeams):
        self.__updateRanks(defeatedTeams)
        self.__panelUpdate()

    def __onObserverVehicleChanged(self):
        vehicle = BigWorld.player().vehicle
        if vehicle:
            if self.__observedVehID is not None:
                self.__clearObservedVehicle(self.__observedVehID)
            self.__observedVehID = vehicle.id
            self.__setObservedVehicle(self.__observedVehID)
            self.__panelUpdate()
        return

    def __clearObservedVehicle(self, vehID):
        data = self.__getPlayerData(vehID)
        if data:
            data['isObserved'] = False

    def __setObservedVehicle(self, vehID):
        data = self.__getPlayerData(vehID)
        if data:
            data['isObserved'] = True

    def __init(self):
        self.__playerList = self.__getInitialPlayersList()
        self.__updateRanks(BigWorld.player().arena.arenaInfo.abilityNotifierComponent.defeatedTeams)
        arenaObserverInfo = BigWorld.player().arena.arenaObserverInfo
        if arenaObserverInfo:
            brObserverInfoComponent = arenaObserverInfo.dynamicComponents.get('battleRoyaleObserverInfoComponent')
            if brObserverInfoComponent:
                self.__updateTeamRespawns(brObserverInfoComponent.teamsMayRespawn)
            battleRoyaleComponent = self.__sessionProvider.arenaVisitor.getComponentSystem().battleRoyaleComponent
            if battleRoyaleComponent.isRespawnFinished:
                self.__onRespawnTimeFinished()
        self.as_setRespawnVisibilityS(True)
        isSquadMode = BigWorld.player().arenaBonusType in ARENA_BONUS_TYPE.BATTLE_ROYALE_SQUAD_RANGE
        self.as_setIsSquadModeS(isSquadMode)
        self.__panelUpdate()

    def __convertToUIVo(self, inData):
        requiredFields = ['isAlive',
         'playerName',
         'vehicleID',
         'teamIndex',
         'vehicleLevel',
         'vehicleTypeIcon',
         'vehicleName',
         'fragsCount',
         'isObserved',
         'hasRespawn']
        return {key:value for key, value in inData.items() if key in requiredFields}

    def __getPlayerData(self, vehicleID):
        return self.__playerList.get(vehicleID)

    def __updateLevel(self, vInfo):
        data = self.__getPlayerData(vInfo)
        if data is not None:
            data['vehicleLevel'] = int2roman(getVehicleLevel(vInfo.vehicleType))
        self.__panelUpdate()
        return

    def __updateStats(self, vStats):
        data = self.__getPlayerData(vStats.vehicleID)
        return False if not data else _comapareAndSet(data, 'fragsCount', self.__getFrags(vStats))

    def __updateInfo(self, vInfo):
        data = self.__getPlayerData(vInfo.vehicleID)
        if not data:
            return False
        updated = _comapareAndSet(data, 'isAlive', vInfo.isAlive())
        if _comapareAndSet(data, 'strCompactDescr', vInfo.vehicleType.strCompactDescr):
            data['vehicleLevel'] = int2roman(getVehicleLevel(vInfo.vehicleType))
            updated = True
        return updated

    def __panelUpdate(self):
        outList = [ ((p['rank'],
          p['teamIndex'],
          not p['isCommander'],
          p['playerName']), self.__convertToUIVo(p)) for p in self.__playerList.itervalues() ]
        outList.sort()
        deadsIdx = next((idx for idx, item in enumerate(outList) if item[0][0] > 0 and not item[1]['isAlive']), -1)
        self.as_setPlayersDataS([ item[1] for item in outList ], deadsIdx)

    def __updateRanks(self, defeatedTeams):
        ranks = {team:rank + 1 for rank, team in enumerate(defeatedTeams)}
        for player in self.__playerList.itervalues():
            player['rank'] = ranks.get(player['teamIndex'], 0)

    def __getInitialPlayersList(self):
        arenaDP = self.__sessionProvider.getArenaDP()
        comanders = BigWorld.player().arenaExtraData.get('commanders', [])
        commandersVehID = {arenaDP.getVehIDByAccDBID(comanderDBID) for comanderDBID in comanders}
        isCommander = lambda vID: vID in commandersVehID
        playersList = {}
        for vInfo, vStats in arenaDP.getActiveVehiclesGenerator():
            playersList[vInfo.vehicleID] = self.__makeVOData(vInfo, vStats, isCommander(vInfo.vehicleID))

        return playersList

    def __getFrags(self, vStats):
        if not vStats:
            return ''
        return str(vStats.frags) if vStats.frags != 0 else ''

    def __makeVOData(self, vInfo, vStats, isCommander):
        return {'isAlive': vInfo.isAlive(),
         'playerName': vInfo.player.name,
         'vehicleID': vInfo.vehicleID,
         'teamIndex': vInfo.team,
         'vehicleLevel': int2roman(getVehicleLevel(vInfo.vehicleType)),
         'vehicleTypeIcon': getTypeVPanelIconPath(vInfo.vehicleType.classTag),
         'vehicleName': vInfo.vehicleType.name,
         'hasRespawn': False,
         'fragsCount': self.__getFrags(vStats),
         'rank': 0,
         'isCommander': isCommander,
         'isObserved ': False,
         'strCompactDescr': vInfo.vehicleType.strCompactDescr}

    def __onTeamsMayRespawnChanged(self, teamsWithRespawn):
        self.__updateTeamRespawns(teamsWithRespawn)
        self.__panelUpdate()

    def __onRespawnTimeFinished(self):
        self.as_setRespawnVisibilityS(False)

    def __updateTeamRespawns(self, teamsWithRespawn):
        for player in self.__playerList.itervalues():
            player['hasRespawn'] = player['teamIndex'] in teamsWithRespawn
