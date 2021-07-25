# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/battle_royale/observer_players_panel.py
import BigWorld
from aih_constants import CTRL_MODE_NAME
from nations import NAMES
from helpers import dependency, int2roman
from gui.impl import backport
from gui.impl.gen import R
from gui.battle_control import avatar_getter
from items.vehicles import VehicleDescr
from gui.battle_control.arena_info.interfaces import IArenaVehiclesController
from gui.battle_control.controllers.battle_field_ctrl import IBattleFieldListener
from gui.Scaleform.daapi.view.meta.BattleRoyalePlayersPanelMeta import BattleRoyalePlayersPanelMeta
from skeletons.gui.battle_session import IBattleSessionProvider
from Event import EventsSubscriber

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
        if self.__isSyncPlayerList:
            self.__init()
            self.__sessionProvider.addArenaCtrl(self)
            self.__es.subscribeToEvent(BigWorld.player().onObserverVehicleChanged, self.__onObserverVehicleChanged)
            componentSystem = self.__sessionProvider.arenaVisitor.getComponentSystem()
            self.__es.subscribeToEvent(componentSystem.battleRoyaleComponent.onBattleRoyaleDefeatedTeamsUpdate, self.__onTeamDeath)

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
        attached = BigWorld.player().getVehicleAttached()
        if attached:
            if self.__observedVehID is not None:
                self.__clearObservedVehicle(self.__observedVehID)
            self.__observedVehID = attached.id
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
        self.__updateRanks(BigWorld.player().avatarBattleRoyaleComponent.defeatedTeams)
        if len(self.__playerList) != len({player['teamIndex'] for player in self.__playerList.itervalues()}):
            self.as_setSeparatorVisibilityS(True)
        self.__panelUpdate()

    def __convertToUIVo(self, inData):
        requiredFields = ['isAlive',
         'playerName',
         'vehicleID',
         'teamIndex',
         'vehicleLevel',
         'nationIcon',
         'vehicleName',
         'fragsCount',
         'isObserved']
        return {key:value for key, value in inData.items() if key in requiredFields}

    def __getPlayerData(self, vehicleID):
        return self.__playerList.get(vehicleID)

    def __updateLevel(self, vInfo):
        data = self.__getPlayerData(vInfo)
        if data is not None:
            data['vehicleLevel'] = int2roman(self._getVehicleLevel(vInfo))
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
            data['vehicleLevel'] = int2roman(self._getVehicleLevel(vInfo))
            updated = True
        return updated

    def __panelUpdate(self):
        outList = [ ((p['rank'],
          p['teamIndex'],
          not p['isCommander'],
          p['playerName']), self.__convertToUIVo(p)) for p in self.__playerList.itervalues() ]
        outList.sort()
        deadsIdx = next((idx for idx, item in enumerate(outList) if item[0][0] > 0), -1)
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
         'vehicleLevel': int2roman(self._getVehicleLevel(vInfo)),
         'nationIcon': self.__getNationIcon(NAMES[vInfo.vehicleType.nationID]),
         'vehicleName': vInfo.vehicleType.name,
         'fragsCount': self.__getFrags(vStats),
         'rank': 0,
         'isCommander': isCommander,
         'isObserved ': False,
         'strCompactDescr': vInfo.vehicleType.strCompactDescr}

    def __getNationIcon(self, nationName):
        nationEmblems = R.images.gui.maps.icons.battleRoyale.emblems
        nationEmblemImage = None
        if hasattr(nationEmblems, nationName):
            nationEmblem = getattr(nationEmblems, nationName)
            nationEmblemImage = backport.image(nationEmblem())
        return nationEmblemImage

    def _getVehicleLevel(self, vInfoVO):
        descriptor = VehicleDescr(compactDescr=vInfoVO.vehicleType.strCompactDescr)
        return max(descriptor.chassis.level, descriptor.turret.level, descriptor.gun.level, descriptor.radio.level, descriptor.engine.level)
