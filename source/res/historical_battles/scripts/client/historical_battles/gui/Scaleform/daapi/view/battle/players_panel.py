# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/Scaleform/daapi/view/battle/players_panel.py
import typing
import BigWorld
from account_helpers.settings_core.settings_constants import BattleCommStorageKeys
from arena_components.advanced_chat_component import EMPTY_CHAT_CMD_FLAG, EMPTY_STATE
from constants import ARENA_PERIOD
from gui.Scaleform.framework.entities.DAAPIDataProvider import ListDAAPIDataProvider
from gui.Scaleform.settings import ICONS_SIZES
from gui.battle_control import avatar_getter
from gui.battle_control.arena_info.arena_vos import VehicleArenaInfoVO
from gui.battle_control.arena_info.interfaces import IArenaVehiclesController
from gui.battle_control.arena_info.settings import INVITATION_DELIVERY_STATUS, PLAYER_STATUS
from gui.battle_control.controllers.battle_field_ctrl import IBattleFieldListener
from gui.battle_control.controllers.period_ctrl import IAbstractPeriodView
from gui.shared.badges import buildBadge
from gui.shared.view_helpers import UsersInfoHelper
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
from historical_battles_common.hb_constants import HBVehicleState
from HBTeamInfoComponent import HBTeamInfoComponent
from historical_battles.gui.Scaleform.daapi.view.battle.plugins import HBPlayerPanelChatCommunicationPlugin
from historical_battles.gui.Scaleform.daapi.view.meta.HBPlayersPanelMeta import HBPlayersPanelMeta
from historical_battles.gui.Scaleform.genConsts.HB_PLAYERS_PANEL_ITEM_STATE import HB_PLAYERS_PANEL_ITEM_STATE
if typing.TYPE_CHECKING:
    from typing import Dict, List, Optional, Iterable

class HistoricalBattlesPlayersPanel(HBPlayersPanelMeta, IAbstractPeriodView, IBattleFieldListener, HBPlayerPanelChatCommunicationPlugin, IArenaVehiclesController):
    settingsCore = dependency.descriptor(ISettingsCore)
    __TIME_BEFORE_BATTLE_TO_UPDATE = (0, 2)

    def __init__(self):
        super(HistoricalBattlesPlayersPanel, self).__init__()
        self.__userInfoHelper = UsersInfoHelper()
        self.__arenaDP = self.sessionProvider.getArenaDP()
        self.__playersListDP = PlayersListDataProvider()
        self.__vehListIndices = {}
        self.__isChatCommandVisible = True
        self.__prevVehHP = {}
        self.__isBattle = False

    @property
    def teamInfo(self):
        if BigWorld.player() is not None:
            arena = BigWorld.player().arena
            if arena:
                return arena.teamInfo.dynamicComponents.get('hbTeamInfoComponent')
        return

    def setPeriod(self, period):
        if period == ARENA_PERIOD.PREBATTLE:
            self.__scheduleStatesUpdate()
        if period == ARENA_PERIOD.BATTLE:
            self.__updatePlayersStates(HB_PLAYERS_PANEL_ITEM_STATE.DEFAULT)
            self.__isBattle = True
        elif period == ARENA_PERIOD.AFTERBATTLE:
            self._clearMarkers()
            self._clearChatCommandList()

    def updateVehicleHealth(self, vehicleID, newHealth, maxHealth):
        self.__setVehicleHealth(vehicleID, newHealth)

    def updateVehiclesInfo(self, updated, _):
        for _, vInfo in updated:
            if not self.__isPlayer(vInfo):
                continue
            self.__updateTeammate(vInfo.vehicleID)
            if not self.__isBattle:
                self.as_setPlayerStateS(vInfo.vehicleID, HB_PLAYERS_PANEL_ITEM_STATE.SPAWN_VEHICLE_SELECTED)

    def invalidateVehicleStatus(self, _, vInfoVO, __):
        if self.__isPlayer(vInfoVO):
            self.__updateTeammate(vInfoVO.vehicleID)

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
        HBTeamInfoComponent.onAllyInfoUpdated += self.__onAllyInfoUpdated
        HBPlayerPanelChatCommunicationPlugin.start(self)
        self.sessionProvider.addArenaCtrl(self)
        self.__updateAllTeammates()
        self.__updatePlayersStates(HB_PLAYERS_PANEL_ITEM_STATE.SPAWN_VEHICLE_NOT_SELECTED)
        return

    def _dispose(self):
        self.sessionProvider.removeArenaCtrl(self)
        vehicleCtrl = self.sessionProvider.shared.vehicleState
        if vehicleCtrl is not None:
            vehicleCtrl.onPostMortemSwitched -= self.__onPostMortemSwitched
            vehicleCtrl.onRespawnBaseMoving -= self.__onRespawnBaseMoving
        self.settingsCore.onSettingsChanged -= self.__onSettingsChange
        HBPlayerPanelChatCommunicationPlugin.stop(self)
        HBTeamInfoComponent.onAllyInfoUpdated -= self.__onAllyInfoUpdated
        self.__playersListDP.dispose()
        self.__playersListDP = None
        self.__userInfoHelper = None
        self.__arenaDP = None
        self.__vehListIndices = None
        self.__prevVehHP = None
        super(HistoricalBattlesPlayersPanel, self)._dispose()
        return

    def _updateChatCommand(self, vehicleID, chatCommandName=EMPTY_STATE, chatCommandFlags=EMPTY_CHAT_CMD_FLAG, forceUpdate=False):
        if (self.__isChatCommandVisible or forceUpdate) and vehicleID in self.__vehListIndices:
            self.as_setChatCommandS(vehicleID, str(chatCommandName), chatCommandFlags)

    def __isPlayer(self, vInfo):
        return not vInfo.isBot and self.__arenaDP.isAlly(vInfo.vehicleID)

    def __getPlayersInfos(self):
        vInfos = self.__arenaDP.getVehiclesInfoIterator()
        return (v for v in vInfos if self.__isPlayer(v))

    def __onSettingsChange(self, diff):
        if BattleCommStorageKeys.SHOW_COM_IN_PLAYER_LIST in diff:
            self.__isChatCommandVisible = bool(diff.get(BattleCommStorageKeys.SHOW_COM_IN_PLAYER_LIST, self.__isChatCommandVisible))
            self._clearChatCommandList()
            self.as_setChatCommandsVisibilityS(self.__isChatCommandVisible)

    def __updatePlayersStates(self, state):
        playersInfos = self.__getPlayersInfos()
        for playerInfo in playersInfos:
            self.as_setPlayerStateS(playerInfo.vehicleID, state)

    def __updateTeammate(self, vehID):
        if not self.__playersListDP.collection:
            return
        else:
            vehInd = self.__vehListIndices.get(vehID)
            if vehInd is None:
                self.__updateAllTeammates()
                return
            vInfo = self.__arenaDP.getVehicleInfo(vehID)
            newVO = self.__getUserVo(vInfo)
            self.__playersListDP.updateItemData(vehInd, newVO)
            return

    def __updateAllTeammates(self):
        usersList = [ self.__getUserVo(vInfo) for vInfo in self.__getPlayersInfos() ]
        self.__sortTeammates(usersList)
        self.__saveVehicleListIndices(usersList)
        self.__playersListDP.buildList(usersList)

    def __sortTeammates(self, userVOs):
        userVOs.sort(key=lambda x: (x['countLives'] == 0, -self.__getDivisionLevel(x['vehicleID']), x['playerName']))

    def __saveVehicleListIndices(self, usersList):
        self.__vehListIndices.clear()
        self.__vehListIndices = {item['vehicleID']:i for i, item in enumerate(usersList)}

    def __getUserVo(self, vInfo):
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
         'hpCurrent': self.__getVehicleHealth(vInfo.vehicleID),
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

    def __isInLastStand(self, vehID):
        return self.teamInfo.getVehicleState(vehID) == HBVehicleState.LAST_STAND.value if self.teamInfo else False

    def __getVehicleHealth(self, vehID):
        if self.__isInLastStand(vehID):
            return 0.0
        vehicleHealthInfo = self.sessionProvider.dynamic.battleField.getVehicleHealthInfo(vehID)
        return vehicleHealthInfo[0] if vehicleHealthInfo and vehicleHealthInfo[0] > 0 else 0

    def __setVehicleHealth(self, vehID, health):
        HBPlayerPanelChatCommunicationPlugin._setVehicleHealth(self, vehID, health)
        vInfo = self.__arenaDP.getVehicleInfo(vehID)
        if self.__isPlayer(vInfo):
            isSkipAnimation = True
            if 0 < self.__prevVehHP.setdefault(vehID, health) < vInfo.vehicleType.maxHealth:
                isSkipAnimation = False
            self.as_setPlayerHpS(vehID, vInfo.vehicleType.maxHealth, health, isSkipAnimation)
            self.__prevVehHP[vehID] = health

    def __getTeammatePlayerStatus(self, vInfo):
        return PLAYER_STATUS.IS_SQUAD_PERSONAL if vInfo.isSquadMan(self.__arenaDP.getVehicleInfo(avatar_getter.getPlayerVehicleID()).prebattleID) else vInfo.playerStatus

    def __onAllyInfoUpdated(self):
        self.__updateAllTeammates()

    def __scheduleStatesUpdate(self):
        m, s = self.__TIME_BEFORE_BATTLE_TO_UPDATE
        arenaPeriod = self.sessionProvider.shared.arenaPeriod
        arenaPeriod.addRemainingTimeNotification(m, s, self.__updateStatesBeforeBattle)

    def __updateStatesBeforeBattle(self, *_):
        self.__updatePlayersStates(HB_PLAYERS_PANEL_ITEM_STATE.SPAWN_VEHICLE_SELECTED)


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

    def updateItemData(self, index, itemVO):
        if self._isDAAPIInited():
            self._list[index] = itemVO
            self.refreshSingleItem(index, itemVO)
