# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/gui/Scaleform/daapi/view/battle/portal_players_data_panel.py
import typing
import BigWorld
from portal.gui.Scaleform.daapi.view.meta.PortalPlayersPanelMeta import PortalPlayersPanelMeta
from PortalTeamInfoComponent import PortalTeamInfoComponent
from gui.Scaleform.framework.entities.DAAPIDataProvider import ListDAAPIDataProvider
from gui.Scaleform.settings import ICONS_SIZES
from gui.battle_control import avatar_getter
from gui.battle_control.arena_info.arena_vos import VehicleArenaInfoVO
from gui.battle_control.arena_info.settings import INVITATION_DELIVERY_STATUS, PLAYER_STATUS
from gui.battle_control.controllers.battle_field_ctrl import IBattleFieldListener
from gui.battle_control.controllers.period_ctrl import IAbstractPeriodView
from gui.battle_control.arena_info.interfaces import IArenaVehiclesController
from gui.shared.badges import buildBadge
from gui.shared.view_helpers import UsersInfoHelper
from helpers import dependency, int2roman
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.battle_session import IBattleSessionProvider
if typing.TYPE_CHECKING:
    from typing import Dict, Optional, List

class PortalPlayersDataPanel(IBattleFieldListener, PortalPlayersPanelMeta, IAbstractPeriodView, IArenaVehiclesController):
    settingsCore = dependency.descriptor(ISettingsCore)
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(PortalPlayersDataPanel, self).__init__()
        self.__arenaDP = self.sessionProvider.getArenaDP()
        self.__playersListDP = PlayersListDataProvider()
        self.__vehListIndices = {}
        self.__prevVehHP = {}
        self.__userInfoHelper = UsersInfoHelper()

    @property
    def teamInfo(self):
        if BigWorld.player() is not None:
            arena = BigWorld.player().arena
            if arena:
                return arena.teamInfo.dynamicComponents.get('portalTeamInfoComponent')
        return

    def updateVehicleHealth(self, vehicleID, newHealth, maxHealth):
        if vehicleID in self.__vehListIndices:
            self.__setVehicleHealth(vehicleID, newHealth)

    def _populate(self):
        super(PortalPlayersDataPanel, self)._populate()
        self.__playersListDP.setFlashObject(self.as_getDPS())
        PortalTeamInfoComponent.onAllyInfoUpdated += self.__onVehicleUpdated
        self.sessionProvider.addArenaCtrl(self)
        self.__updateAllTeammates()

    def _dispose(self):
        self.sessionProvider.removeArenaCtrl(self)
        PortalTeamInfoComponent.onAllyInfoUpdated -= self.__onVehicleUpdated
        self.__playersListDP.dispose()
        self.__playersListDP = None
        self.__arenaDP = None
        self.__vehListIndices = None
        self.__prevVehHP = None
        self.__userInfoHelper = None
        super(PortalPlayersDataPanel, self)._dispose()
        return

    def invalidateVehicleStatus(self, _, vInfoVO, __):
        self.__updateOneTeammate(vInfoVO.vehicleID)

    def updateVehiclesInfo(self, updated, _):
        for _, vInfo in updated:
            self.__updateOneTeammate(vInfo.vehicleID)

    def __onVehicleUpdated(self, vehID):
        self.__updateOneTeammate(vehID)

    def __updateAllTeammates(self):
        arenaDP = self.__arenaDP
        vInfos = arenaDP.getVehiclesInfoIterator()
        teammateInfos = (v for v in vInfos if not v.isBot and arenaDP.isAlly(v.vehicleID))
        usersList = [ self.__getUserVo(vInfo) for vInfo in teammateInfos ]
        self.__sortTeammates(usersList)
        self.__saveVehicleListIndices(usersList)
        self.__playersListDP.buildList(usersList)

    def __updateOneTeammate(self, vehicleID):
        index = self.__vehListIndices.get(vehicleID, None)
        if index is None:
            self.__updateAllTeammates()
            return
        else:
            arenaDP = self.__arenaDP
            vInfo = arenaDP.getVehicleInfo(vehicleID)
            self.__playersListDP.updateItemData(index, self.__getUserVo(vInfo))
            return

    def __sortTeammates(self, usersList):
        usersList.sort(key=lambda x: (-self.__getVehicleLevel(x['vehicleID']), x['playerName'], x['vehicleType']))

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
         'vehicleLevel': int2roman(self.__getVehicleLevel(vInfo.vehicleID)),
         'vehicleStatus': vInfo.vehicleStatus,
         'hpMax': vType.maxHealth,
         'hpCurrent': vehicleHealthInfo[0] if vehicleHealthInfo and vehicleHealthInfo[0] > 0 else 0,
         'secondsToRespawn': self.__getSecondsToRespawn(vInfo.vehicleID)}
        badge = buildBadge(vInfo.selectedBadge, vInfo.getBadgeExtraInfo())
        if badge is not None:
            userVO['badge'] = badge.getBadgeVO(ICONS_SIZES.X24, {'isAtlasSource': True}, shortIconName=True)
        return userVO

    def __getVehicleLevel(self, vehID):
        return self.teamInfo.getVehicleLevel(vehID) if self.teamInfo else 0

    def __getSecondsToRespawn(self, vehID):
        return self.teamInfo.getRespawnTime(vehID) if self.teamInfo else 0.0

    def __setVehicleHealth(self, vehID, health):
        vInfo = self.__arenaDP.getVehicleInfo(vehID)
        if self.__arenaDP.isAlly(vInfo.vehicleID):
            isSkipAnimation = True
            if 0 < self.__prevVehHP.setdefault(vehID, health) < vInfo.vehicleType.maxHealth:
                isSkipAnimation = False
            self.as_setPlayerHpS(vehID, vInfo.vehicleType.maxHealth, health, isSkipAnimation)
            self.__prevVehHP[vehID] = health

    def __getTeammatePlayerStatus(self, vInfo):
        return PLAYER_STATUS.IS_SQUAD_PERSONAL if vInfo.isSquadMan(self.__arenaDP.getVehicleInfo(avatar_getter.getPlayerVehicleID()).prebattleID) else vInfo.playerStatus


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
