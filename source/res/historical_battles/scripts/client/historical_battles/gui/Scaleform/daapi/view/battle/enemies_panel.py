# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/Scaleform/daapi/view/battle/enemies_panel.py
import BigWorld
from HBVehicleRoleArenaComponent import HBVehicleRoleArenaComponent
from gui.battle_control.arena_info.interfaces import IArenaVehiclesController
from gui.battle_control.controllers.battle_field_ctrl import IBattleFieldListener
from gui.shared.gui_items.Vehicle import VEHICLE_BATTLE_TYPES_ORDER_INDICES
from gui.shared.view_helpers import UsersInfoHelper
from helpers import dependency
from gui.Scaleform.framework.entities.DAAPIDataProvider import ListDAAPIDataProvider
from skeletons.gui.battle_session import IBattleSessionProvider
from skeletons.account_helpers.settings_core import ISettingsCore
from account_helpers.settings_core.settings_constants import BattleCommStorageKeys
from arena_components.advanced_chat_component import EMPTY_CHAT_CMD_FLAG, EMPTY_STATE
from constants import ARENA_PERIOD
from helpers.CallbackDelayer import CallbackDelayer
from gui.battle_control.controllers.period_ctrl import IAbstractPeriodView
from historical_battles_common.hb_constants import VehicleRole
from historical_battles.gui.Scaleform.daapi.view.battle.plugins import HBEnemyPanelChatCommunicationPlugin
from historical_battles.gui.Scaleform.daapi.view.meta.HBEnemiesPanelMeta import HBEnemiesPanelMeta

class EnemiesListDataProvider(ListDAAPIDataProvider):

    def __init__(self):
        super(EnemiesListDataProvider, self).__init__()
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


class HistoricalBattlesEnemiesPanel(IBattleFieldListener, HBEnemiesPanelMeta, IAbstractPeriodView, IArenaVehiclesController, HBEnemyPanelChatCommunicationPlugin):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)
    settingsCore = dependency.descriptor(ISettingsCore)
    RETIRED_CLEAR_DELAY = 3.0
    _VEHICLE_ROLE_PRIORITIES = {VehicleRole.boss: 0,
     VehicleRole.aimer: 1,
     VehicleRole.runner: 2,
     VehicleRole.elite: 3,
     VehicleRole.regular: 4}

    def __init__(self):
        super(HistoricalBattlesEnemiesPanel, self).__init__()
        self.__userInfoHelper = UsersInfoHelper()
        self.__enemiesListDP = EnemiesListDataProvider()
        self.__arenaDP = self.sessionProvider.getArenaDP()
        self.__isChatCommandVisible = True
        self.__cachedIDs = set()
        self.__retiredIDs = set()
        self.__updateDelayer = CallbackDelayer()

    def setPeriod(self, period):
        if period == ARENA_PERIOD.BATTLE:
            self.__updateAll()
        elif period == ARENA_PERIOD.AFTERBATTLE:
            self._clearMarkers()
            self._clearChatCommandList()

    def _populate(self):
        super(HistoricalBattlesEnemiesPanel, self)._populate()
        self.__enemiesListDP.setFlashObject(self.as_getEnemyInfoDPS())
        self.settingsCore.onSettingsChanged += self.__onSettingsChange
        self.__isChatCommandVisible = bool(self.settingsCore.getSetting(BattleCommStorageKeys.SHOW_COM_IN_PLAYER_LIST))
        self.as_setChatCommandsVisibilityS(self.__isChatCommandVisible)
        self.sessionProvider.addArenaCtrl(self)
        HBEnemyPanelChatCommunicationPlugin.start(self)
        HBVehicleRoleArenaComponent.onRoleInfosUpdated += self.__updateAll

    def _dispose(self):
        self.__updateDelayer.destroy()
        self.__cachedIDs.clear()
        self.__retiredIDs.clear()
        self.__enemiesListDP.dispose()
        self.__enemiesListDP = None
        self.__userInfoHelper = None
        self.__arenaDP = None
        self.__cachedIDs = None
        self.__retiredIDs = None
        self.__updateDelayer = None
        HBEnemyPanelChatCommunicationPlugin.stop(self)
        HBVehicleRoleArenaComponent.onRoleInfosUpdated -= self.__updateAll
        self.settingsCore.onSettingsChanged -= self.__onSettingsChange
        self.sessionProvider.removeArenaCtrl(self)
        super(HistoricalBattlesEnemiesPanel, self)._dispose()
        return

    def invalidateVehicleStatus(self, _, vInfoVO, __):
        vehId = vInfoVO.vehicleID
        if vehId in self.__cachedIDs and not vInfoVO.isAlive():
            self.as_setEnemyHpS(vehId, vInfoVO.vehicleType.maxHealth, 0)
            self.__retiredIDs.add(vehId)
            self.__updateDelayer.delayCallback(self.RETIRED_CLEAR_DELAY, self.__clearRetired)

    def updateVehicleHealth(self, vehicleID, newHealth, maxHealth):
        HBEnemyPanelChatCommunicationPlugin._setVehicleHealth(self, vehicleID, newHealth)
        if vehicleID in self.__cachedIDs and newHealth > 0:
            self.as_setEnemyHpS(vehicleID, maxHealth, newHealth)

    def postUpdateVehicleHealth(self):
        self.__updateAll()

    def addVehicleInfo(self, vo, arenaDP):
        if arenaDP.isEnemyTeam(vo.team):
            self.__updateAll()

    def __clearRetired(self):
        self.__retiredIDs.clear()
        self.__updateAll()

    def __sortVehicles(self, vInfos):
        arena = getattr(BigWorld.player(), 'arena', None)
        if not arena:
            return
        else:
            vehicleRoleArenaComponent = arena.arenaInfo.vehicleRoleArenaComponent
            vInfos.sort(key=lambda vInfo: (self._VEHICLE_ROLE_PRIORITIES[vehicleRoleArenaComponent.getRole(vInfo.vehicleID)], VEHICLE_BATTLE_TYPES_ORDER_INDICES[vInfo.vehicleType.classTag]))
            return

    def __getUserVo(self, vInfo):
        battleFieldCtrl = self.sessionProvider.dynamic.battleField
        vehicleHealthInfo = battleFieldCtrl.getVehicleHealthInfo(vInfo.vehicleID)
        if vInfo.isAlive():
            hpCurrent = max(0, vehicleHealthInfo[0]) if vehicleHealthInfo else vInfo.vehicleType.maxHealth
        else:
            hpCurrent = 0
        player = vInfo.player
        sessionID = player.avatarSessionID
        tags = self.__userInfoHelper.getUserTags(sessionID, player.igrType)
        arena = getattr(BigWorld.player(), 'arena', None)
        vehicleID = vInfo.vehicleID
        userVO = {'accountDBID': player.accountDBID,
         'sessionID': sessionID,
         'playerName': player.name,
         'playerFakeName': player.fakeName,
         'clanAbbrev': player.clanAbbrev,
         'region': '',
         'userTags': tags,
         'squadIndex': vInfo.squadIndex,
         'playerStatus': vInfo.playerStatus,
         'invitationStatus': vInfo.invitationDeliveryStatus,
         'vehicleID': vehicleID,
         'vehicleType': arena.arenaInfo.vehicleRoleArenaComponent.getRoleName(vehicleID) if arena else None,
         'vehicleName': vInfo.vehicleType.shortName,
         'hpMax': vInfo.vehicleType.maxHealth,
         'hpCurrent': hpCurrent}
        return userVO

    def __updateAll(self):
        vInfos = [ v for v in self.__arenaDP.getVehiclesInfoIterator() if v.isEnemy() and (v.isAlive() or v.vehicleID in self.__retiredIDs) ]
        self.__sortVehicles(vInfos)
        self.__enemiesListDP.buildList([ self.__getUserVo(vInfo) for vInfo in vInfos ])
        self.__cachedIDs = set((vInfo.vehicleID for vInfo in vInfos))

    def _updateChatCommand(self, vehicleID, chatCommandName=EMPTY_STATE, chatCommandFlags=EMPTY_CHAT_CMD_FLAG, forceUpdate=False):
        if (self.__isChatCommandVisible or forceUpdate) and vehicleID in self.__cachedIDs:
            self.as_setChatCommandS(vehicleID, str(chatCommandName), chatCommandFlags)

    def __onSettingsChange(self, diff):
        if BattleCommStorageKeys.SHOW_COM_IN_PLAYER_LIST in diff:
            self.__isChatCommandVisible = bool(diff.get(BattleCommStorageKeys.SHOW_COM_IN_PLAYER_LIST, self.__isChatCommandVisible))
            self._clearChatCommandList()
            self.as_setChatCommandsVisibilityS(self.__isChatCommandVisible)
