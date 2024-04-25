# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/Scaleform/daapi/view/battle/players_panel.py
from typing import Dict, List
from TeamInfoLivesComponent import TeamInfoLivesComponent
import BigWorld
from constants import ARENA_PERIOD
from debug_utils import LOG_WARNING
from gui.Scaleform.daapi.view.meta.HBPlayersPanelMeta import HBPlayersPanelMeta
from gui.Scaleform.framework.entities.DAAPIDataProvider import ListDAAPIDataProvider
from gui.Scaleform.settings import ICONS_SIZES
from gui.battle_control import avatar_getter
from gui.battle_control.arena_info.arena_vos import VehicleArenaInfoVO
from gui.battle_control.arena_info.settings import INVITATION_DELIVERY_STATUS, PLAYER_STATUS
from gui.battle_control.controllers.battle_field_ctrl import IBattleFieldListener
from gui.battle_control.controllers.period_ctrl import IAbstractPeriodView
from gui.shared.badges import buildBadge
from gui.shared.gui_items.Vehicle import VEHICLE_BATTLE_TYPES_ORDER_INDICES
from gui.shared.view_helpers import UsersInfoHelper
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
from account_helpers.settings_core.settings_constants import BattleCommStorageKeys
from arena_components.advanced_chat_component import EMPTY_CHAT_CMD_FLAG, EMPTY_STATE
from historical_battles_common.helpers_common import getFrontmanRoleID
from historical_battles.gui.Scaleform.daapi.view.battle.plugins import HBPlayerPanelChatCommunicationPlugin
from historical_battles.gui.impl.gen.view_models.views.common.base_team_member_model import TeamMemberRoleType
from historical_battles.gui.impl.lobby.platoon.platoon_helpers import FrontmanRoleIDToTeamMemberRole
from VehicleRespawnComponent import VehicleRespawnComponent

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

    def setPeriod(self, period):
        if period == ARENA_PERIOD.BATTLE:
            self.__updateAllTeammates()
        elif period == ARENA_PERIOD.AFTERBATTLE:
            self._clearMarkers()
            self._clearChatCommandList()

    def updateVehicleHealth(self, vehicleID, newHealth, maxHealth):
        self.__setVehicleHealth(vehicleID, newHealth)

    def _populate(self):
        super(HistoricalBattlesPlayersPanel, self)._populate()
        self.__playersListDP.setFlashObject(self.as_getDPS())
        vehicleCtrl = self.sessionProvider.shared.vehicleState
        if vehicleCtrl is not None:
            vehicleCtrl.onPostMortemSwitched += self.__onPostMortemSwitched
            vehicleCtrl.onRespawnBaseMoving += self.__onRespawnBaseMoving
        TeamInfoLivesComponent.onTeamLivesUpdated += self._onTeamLivesUpdated
        VehicleRespawnComponent.onSetSpawnTime += self._onVehicleSpawnTime
        self.settingsCore.onSettingsChanged += self.__onSettingsChange
        self.__isChatCommandVisible = bool(self.settingsCore.getSetting(BattleCommStorageKeys.SHOW_COM_IN_PLAYER_LIST))
        self.as_setChatCommandsVisibilityS(self.__isChatCommandVisible)
        HBPlayerPanelChatCommunicationPlugin.start(self)
        return

    def _dispose(self):
        TeamInfoLivesComponent.onTeamLivesUpdated -= self._onTeamLivesUpdated
        vehicleCtrl = self.sessionProvider.shared.vehicleState
        if vehicleCtrl is not None:
            vehicleCtrl.onPostMortemSwitched -= self.__onPostMortemSwitched
            vehicleCtrl.onRespawnBaseMoving -= self.__onRespawnBaseMoving
        VehicleRespawnComponent.onSetSpawnTime -= self._onVehicleSpawnTime
        self.settingsCore.onSettingsChanged -= self.__onSettingsChange
        HBPlayerPanelChatCommunicationPlugin.stop(self)
        super(HistoricalBattlesPlayersPanel, self)._dispose()
        return

    def _onVehicleSpawnTime(self, vehicleID, spawnTime):
        if vehicleID not in self.__vehListIndices:
            return
        idx = self.__vehListIndices[vehicleID]
        secondsUntilRespawn = {'secondsToRespawn': spawnTime - BigWorld.serverTime()}
        self.__playersListDP.refreshSingleItem(idx, secondsUntilRespawn)

    def __onSettingsChange(self, diff):
        if BattleCommStorageKeys.SHOW_COM_IN_PLAYER_LIST in diff:
            self.__isChatCommandVisible = bool(diff.get(BattleCommStorageKeys.SHOW_COM_IN_PLAYER_LIST, self.__isChatCommandVisible))
            self._clearChatCommandList()
            self.as_setChatCommandsVisibilityS(self.__isChatCommandVisible)

    def _onTeamLivesUpdated(self):
        self.__updateAllTeammates()

    def __updateAllTeammates(self):
        arenaDP = self.__arenaDP
        vInfos = arenaDP.getVehiclesInfoIterator()
        teammateInfos = (v for v in vInfos if not v.isBot and arenaDP.isAlly(v.vehicleID))
        usersList = [ self.__getUserVo(vInfo) for vInfo in teammateInfos ]
        self.__sortTeammates(usersList)
        self.__saveVehicleListIndices(usersList)
        self.__playersListDP.buildList(usersList)

    def __sortTeammates(self, userVOs):
        userVOs.sort(key=lambda x: (0 if x['countLives'] > 0 else 1,
         0 if x['vehicleLevel'] > 1 else 1,
         VEHICLE_BATTLE_TYPES_ORDER_INDICES[x['vehicleType']],
         x['playerName']))

    def __saveVehicleListIndices(self, usersList):
        self.__vehListIndices.clear()
        for i, item in enumerate(usersList):
            self.__vehListIndices[item['vehicleID']] = i

    def __getUserVo(self, vInfo):
        battleFieldCtrl = self.sessionProvider.dynamic.battleField
        vehicleHealthInfo = battleFieldCtrl.getVehicleHealthInfo(vInfo.vehicleID)
        hpCurrent = vehicleHealthInfo[0] if vehicleHealthInfo and vehicleHealthInfo[0] > 0 else 0
        badgeID = vInfo.selectedBadge
        player = vInfo.player
        sessionID = player.avatarSessionID
        tags = self.__userInfoHelper.getUserTags(sessionID, player.igrType)
        vType = vInfo.vehicleType
        frontmanRoleID = getFrontmanRoleID(vInfo.vehicleID)
        role = FrontmanRoleIDToTeamMemberRole.get(frontmanRoleID, TeamMemberRoleType.NONE).value
        userVO = {'accountDBID': player.accountDBID,
         'sessionID': sessionID,
         'playerName': player.name,
         'playerFakeName': player.fakeName,
         'clanAbbrev': player.clanAbbrev,
         'region': '',
         'igrType': player.igrType,
         'userTags': tags,
         'squadIndex': vInfo.squadIndex,
         'playerStatus': self.__getTeammatePlayerStatus(vInfo),
         'invitationStatus': INVITATION_DELIVERY_STATUS.NONE,
         'vehicleID': vInfo.vehicleID,
         'vehicleName': vType.shortName,
         'vehicleType': vType.classTag,
         'vehicleLevel': vType.level,
         'vehicleStatus': vInfo.vehicleStatus,
         'playerRole': role,
         'hpMax': vType.maxHealth,
         'hpCurrent': hpCurrent,
         'countLives': self._getVehicleLives(vInfo.vehicleID)}
        badge = buildBadge(badgeID, vInfo.getBadgeExtraInfo())
        if badge is not None:
            userVO['badge'] = badge.getBadgeVO(ICONS_SIZES.X24, {'isAtlasSource': True}, shortIconName=True)
        userVO['secondsToRespawn'] = self._getSecondsToRespawn(vInfo.vehicleID)
        return userVO

    def __onPostMortemSwitched(self, noRespawnPossible, respawnAvailable):
        self.as_setPlayersSwitchingAllowedS(True)

    def __onRespawnBaseMoving(self):
        self.as_setPlayersSwitchingAllowedS(False)

    @staticmethod
    def _getVehicleLives(vehicleID):
        teamLivesComponent = BigWorld.player().arena.teamInfo.dynamicComponents.get('teamLivesComponent')
        return teamLivesComponent.getLives(vehicleID) if teamLivesComponent else 0

    @staticmethod
    def _getSecondsToRespawn(vehicleID):
        vehicle = BigWorld.entities.get(vehicleID)
        if vehicle:
            vehicleRespawnComponent = vehicle.dynamicComponents.get('VehicleRespawnComponent')
            if vehicleRespawnComponent:
                secondsToRespawn = vehicleRespawnComponent.spawnTime - BigWorld.serverTime()
                if secondsToRespawn > 0:
                    return secondsToRespawn
                return 0
            LOG_WARNING('Vehicle with id {} has no `VehicleRespawnComponent`'.format(vehicle.id))

    def __setVehicleHealth(self, vehID, health):
        HBPlayerPanelChatCommunicationPlugin._setVehicleHealth(self, vehID, health)
        vInfo = self.__arenaDP.getVehicleInfo(vehID)
        if self.__arenaDP.isAlly(vInfo.vehicleID):
            isSkipAnimation = True
            if 0 < self.__prevVehHP.setdefault(vehID, health) < vInfo.vehicleType.maxHealth:
                isSkipAnimation = False
            self.as_setPlayerHpS(vehID, vInfo.vehicleType.maxHealth, health, isSkipAnimation)
            self.__updateAllTeammates()
            self.__prevVehHP[vehID] = health

    def _updateChatCommand(self, vehicleID, chatCommandName=EMPTY_STATE, chatCommandFlags=EMPTY_CHAT_CMD_FLAG, forceUpdate=False):
        if (self.__isChatCommandVisible or forceUpdate) and vehicleID in self.__vehListIndices:
            self.as_setChatCommandS(vehicleID, str(chatCommandName), chatCommandFlags)

    def __getTeammatePlayerStatus(self, vInfo):
        teammatePlayerStatus = vInfo.playerStatus
        playerVehInfo = self.__arenaDP.getVehicleInfo(avatar_getter.getPlayerVehicleID())
        if vInfo.isSquadMan(playerVehInfo.prebattleID):
            teammatePlayerStatus = PLAYER_STATUS.IS_SQUAD_PERSONAL
        return teammatePlayerStatus


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
