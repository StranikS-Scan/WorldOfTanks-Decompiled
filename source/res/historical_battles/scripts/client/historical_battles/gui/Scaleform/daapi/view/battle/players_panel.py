# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/Scaleform/daapi/view/battle/players_panel.py
import typing
import BigWorld
from HBTeamInfoComponent import HBTeamInfoComponent
from account_helpers.settings_core.settings_constants import BattleCommStorageKeys
from arena_components.advanced_chat_component import EMPTY_CHAT_CMD_FLAG, EMPTY_STATE
from constants import ARENA_PERIOD
from gui.Scaleform.framework.entities.DAAPIDataProvider import ListDAAPIDataProvider
from gui.Scaleform.settings import ICONS_SIZES
from gui.battle_control import avatar_getter
from gui.battle_control.arena_info.arena_vos import VehicleArenaInfoVO
from gui.battle_control.arena_info.settings import INVITATION_DELIVERY_STATUS, PLAYER_STATUS
from gui.battle_control.controllers.battle_field_ctrl import IBattleFieldListener
from gui.battle_control.controllers.period_ctrl import IAbstractPeriodView
from gui.shared.badges import buildBadge
from gui.shared.view_helpers import UsersInfoHelper
from helpers import dependency
from historical_battles.gui.Scaleform.daapi.view.battle.plugins import HBPlayerPanelChatCommunicationPlugin
from historical_battles.gui.Scaleform.daapi.view.meta.HBPlayersPanelMeta import HBPlayersPanelMeta
from historical_battles.gui.Scaleform.genConsts.HB_PLAYERS_PANEL_ITEM_STATE import HB_PLAYERS_PANEL_ITEM_STATE
from skeletons.account_helpers.settings_core import ISettingsCore
if typing.TYPE_CHECKING:
    from typing import Dict, List, Optional

class HistoricalBattlesPlayersPanel(HBPlayersPanelMeta, IAbstractPeriodView, IBattleFieldListener, HBPlayerPanelChatCommunicationPlugin):
    settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self):
        super(HistoricalBattlesPlayersPanel, self).__init__()
        self.__userInfoHelper = UsersInfoHelper()
        self.__arenaDP = self.sessionProvider.getArenaDP()
        self.__playersListDP = PlayersListDataProvider()
        self.__vehListIndices = {}
        self.__isChatCommandVisible = True
        self.__prevVehHP = {}
        self.__isBattle = False
        self.__playersVehicles = []

    @property
    def teamInfo(self):
        if BigWorld.player() is not None:
            arena = BigWorld.player().arena
            if arena:
                return arena.teamInfo.dynamicComponents.get('hbTeamInfoComponent')
        return

    def setPeriod(self, period):
        if period == ARENA_PERIOD.BATTLE:
            self.__updateAllTeammates(startBattle=True)
            self.__isBattle = True
            self.__playersVehicles = []
            BigWorld.player().arena.onVehicleUpdated -= self.__onVehicleUpdated
        elif period == ARENA_PERIOD.AFTERBATTLE:
            self._clearMarkers()
            self._clearChatCommandList()

    def updateVehicleHealth(self, vehicleID, newHealth, maxHealth):
        self.__setVehicleHealth(vehicleID, newHealth)

    def postUpdateVehicleHealth(self):
        self.__updateAllTeammates()

    def _populate(self):
        super(HistoricalBattlesPlayersPanel, self)._populate()
        self.__playersListDP.setFlashObject(self.as_getDPS())
        vehicleCtrl = self.sessionProvider.shared.vehicleState
        if vehicleCtrl is not None:
            vehicleCtrl.onPostMortemSwitched += self.__onPostMortemSwitched
            vehicleCtrl.onRespawnBaseMoving += self.__onRespawnBaseMoving
        self.settingsCore.onSettingsChanged += self.__onSettingsChange
        self.__isChatCommandVisible = bool(self.settingsCore.getSetting(BattleCommStorageKeys.SHOW_COM_IN_PLAYER_LIST))
        self.as_setChatCommandsVisibilityS(self.__isChatCommandVisible)
        BigWorld.player().arena.onVehicleUpdated += self.__onVehicleUpdated
        HBTeamInfoComponent.onAllyInfoUpdated += self.__onAllyInfoUpdated
        HBPlayerPanelChatCommunicationPlugin.start(self)
        return

    def _dispose(self):
        vehicleCtrl = self.sessionProvider.shared.vehicleState
        if vehicleCtrl is not None:
            vehicleCtrl.onPostMortemSwitched -= self.__onPostMortemSwitched
            vehicleCtrl.onRespawnBaseMoving -= self.__onRespawnBaseMoving
        self.settingsCore.onSettingsChanged -= self.__onSettingsChange
        HBPlayerPanelChatCommunicationPlugin.stop(self)
        HBTeamInfoComponent.onAllyInfoUpdated -= self.__onAllyInfoUpdated
        if BigWorld.player() is not None:
            arena = BigWorld.player().arena
            if arena is not None:
                arena.onVehicleUpdated -= self.__onVehicleUpdated
        self.__playersListDP.dispose()
        self.__playersListDP = None
        self.__userInfoHelper = None
        self.__arenaDP = None
        self.__vehListIndices = None
        self.__prevVehHP = None
        self.__playersVehicles = None
        super(HistoricalBattlesPlayersPanel, self)._dispose()
        return

    def __onSettingsChange(self, diff):
        if BattleCommStorageKeys.SHOW_COM_IN_PLAYER_LIST in diff:
            self.__isChatCommandVisible = bool(diff.get(BattleCommStorageKeys.SHOW_COM_IN_PLAYER_LIST, self.__isChatCommandVisible))
            self._clearChatCommandList()
            self.as_setChatCommandsVisibilityS(self.__isChatCommandVisible)

    def __onVehicleUpdated(self, vehId):
        if self.__isBattle:
            return
        if not self.__playersVehicles:
            self.__updateAllTeammates()
        if vehId in self.__playersVehicles:
            self.as_setPlayerStateS(vehId, HB_PLAYERS_PANEL_ITEM_STATE.SPAWN_VEHICLE_SELECTED)

    def __updatePlayersStates(self, usersList, startBattle=False):
        if startBattle:
            for info in usersList:
                self.as_setPlayerStateS(info['vehicleID'], HB_PLAYERS_PANEL_ITEM_STATE.DEFAULT)

            return
        if not self.__playersVehicles:
            self.__playersVehicles = [ info['vehicleID'] for info in usersList ]
            for vehicleID in self.__playersVehicles:
                self.as_setPlayerStateS(vehicleID, HB_PLAYERS_PANEL_ITEM_STATE.SPAWN_VEHICLE_NOT_SELECTED)

    def __updateAllTeammates(self, startBattle=False):
        arenaDP = self.__arenaDP
        vInfos = arenaDP.getVehiclesInfoIterator()
        teammateInfos = (v for v in vInfos if not v.isBot and arenaDP.isAlly(v.vehicleID))
        usersList = [ self.__getUserVo(vInfo) for vInfo in teammateInfos ]
        self.__sortTeammates(usersList)
        self.__saveVehicleListIndices(usersList)
        self.__playersListDP.buildList(usersList)
        if not self.__isBattle:
            self.__updatePlayersStates(usersList, startBattle)

    def __sortTeammates(self, userVOs):
        userVOs.sort(key=lambda x: (x['countLives'] == 0, -self.__getDivisionLevel(x['vehicleID']), x['playerName']))

    def __saveVehicleListIndices(self, usersList):
        self.__vehListIndices.clear()
        self.__vehListIndices = {item['vehicleID']:i for i, item in enumerate(usersList)}

    def __getUserVo(self, vInfo):
        vehicleHealthInfo = self.sessionProvider.dynamic.battleField.getVehicleHealthInfo(vInfo.vehicleID)
        player = vInfo.player
        sessionID = player.avatarSessionID
        vType = vInfo.vehicleType
        userVO = {'accountDBID': player.accountDBID,
         'sessionID': sessionID,
         'playerName': player.name,
         'playerFakeName': player.fakeName,
         'clanAbbrev': player.clanAbbrev,
         'region': '',
         'igrType': player.igrType,
         'userTags': self.__userInfoHelper.getUserTags(sessionID, player.igrType),
         'squadIndex': vInfo.squadIndex,
         'playerStatus': self.__getTeammatePlayerStatus(vInfo),
         'invitationStatus': INVITATION_DELIVERY_STATUS.NONE,
         'vehicleID': vInfo.vehicleID,
         'vehicleName': vType.shortName,
         'vehicleType': vType.classTag,
         'vehicleLevel': vType.level,
         'vehicleStatus': vInfo.vehicleStatus,
         'playerRole': '',
         'hpMax': vType.maxHealth,
         'hpCurrent': vehicleHealthInfo[0] if vehicleHealthInfo and vehicleHealthInfo[0] > 0 else 0,
         'secondsToRespawn': self.__getSecondsToRespawn(vInfo.vehicleID),
         'countLives': self.__getAliveVehicleCount(vInfo.vehicleID)}
        badge = buildBadge(vInfo.selectedBadge, vInfo.getBadgeExtraInfo())
        if badge is not None:
            userVO['badge'] = badge.getBadgeVO(ICONS_SIZES.X24, {'isAtlasSource': True}, shortIconName=True)
        return userVO

    def __onPostMortemSwitched(self, noRespawnPossible, respawnAvailable):
        self.as_setPlayersSwitchingAllowedS(True)

    def __onRespawnBaseMoving(self):
        self.as_setPlayersSwitchingAllowedS(False)

    def __getSecondsToRespawn(self, vehID):
        return self.teamInfo.getRespawnTime(vehID) - BigWorld.serverTime() if self.teamInfo else 0.0

    def __getDivisionLevel(self, vehID):
        return self.teamInfo.getDivisionLevel(vehID) if self.teamInfo else 1

    def __getAliveVehicleCount(self, vehID):
        return self.teamInfo.getAliveVehicleCount(vehID) if self.teamInfo else 0

    def __setVehicleHealth(self, vehID, health):
        HBPlayerPanelChatCommunicationPlugin._setVehicleHealth(self, vehID, health)
        vInfo = self.__arenaDP.getVehicleInfo(vehID)
        if self.__arenaDP.isAlly(vInfo.vehicleID):
            isSkipAnimation = True
            if 0 < self.__prevVehHP.setdefault(vehID, health) < vInfo.vehicleType.maxHealth:
                isSkipAnimation = False
            self.as_setPlayerHpS(vehID, vInfo.vehicleType.maxHealth, health, isSkipAnimation)
            self.__prevVehHP[vehID] = health

    def _updateChatCommand(self, vehicleID, chatCommandName=EMPTY_STATE, chatCommandFlags=EMPTY_CHAT_CMD_FLAG, forceUpdate=False):
        if (self.__isChatCommandVisible or forceUpdate) and vehicleID in self.__vehListIndices:
            self.as_setChatCommandS(vehicleID, str(chatCommandName), chatCommandFlags)

    def __getTeammatePlayerStatus(self, vInfo):
        return PLAYER_STATUS.IS_SQUAD_PERSONAL if vInfo.isSquadMan(self.__arenaDP.getVehicleInfo(avatar_getter.getPlayerVehicleID()).prebattleID) else vInfo.playerStatus

    def __onAllyInfoUpdated(self):
        self.__updateAllTeammates()


class PlayersListDataProvider(ListDAAPIDataProvider):

    def __init__(self):
        super(PlayersListDataProvider, self).__init__()
        self._list = []

    @property
    def collection(self):
        return self._list

    def emptyItem(self):
        return {}

    def clear(self):
        self._list = []

    def dispose(self):
        self.clear()
        self.destroy()

    def buildList(self, itemsVoList):
        if itemsVoList != self._list and self._isDAAPIInited():
            self._list = itemsVoList
            self.refresh()
