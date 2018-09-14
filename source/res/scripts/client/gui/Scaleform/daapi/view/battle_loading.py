# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle_loading.py
import BattleReplay
import BigWorld
from account_helpers.settings_core import settings_constants
from account_helpers.settings_core.SettingsCore import g_settingsCore
from account_helpers.settings_core.options import BattleLoadingTipSetting
from gui.Scaleform.locale.BATTLE_TUTORIAL import BATTLE_TUTORIAL
from helpers import tips
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.LobbyContext import g_lobbyContext
from gui.battle_control import g_sessionProvider
from gui.battle_control.arena_info.interfaces import IArenaVehiclesController
from gui.battle_control.arena_info import player_format
from gui.battle_control.arena_info import vos_collections
from gui.battle_control.arena_info.arena_vos import VehicleActions
from gui.battle_control.arena_info.settings import INVALIDATE_OP
from gui.battle_control.arena_info.settings import SMALL_MAP_IMAGE_SF_PATH
from gui.shared.formatters import text_styles
from gui.Scaleform.Waiting import Waiting
from gui.Scaleform.daapi import LobbySubView
from gui.Scaleform.daapi.view.meta.BaseBattleLoadingMeta import BaseBattleLoadingMeta
from gui.Scaleform.daapi.view.fallout_info_panel_helper import getHelpTextAsDicts
from messenger.storage import storage_getter
from messenger.m_constants import PROTO_TYPE
from messenger.proto import proto_getter
DEFAULT_BATTLES_COUNT = 100

class BattleLoading(LobbySubView, BaseBattleLoadingMeta, IArenaVehiclesController):
    __background_alpha__ = 0.0

    def __init__(self, _=None):
        super(BattleLoading, self).__init__()
        self._battleCtx = None
        self._arenaVisitor = None
        self._isArenaTypeDataInited = False
        self.__isTipInited = False
        return

    @storage_getter('users')
    def usersStorage(self):
        return None

    @proto_getter(PROTO_TYPE.BW_CHAT2)
    def bwProto(self):
        return None

    def _populate(self):
        super(BattleLoading, self)._populate()
        g_sessionProvider.addArenaCtrl(self)
        BigWorld.wg_updateColorGrading()
        BigWorld.wg_enableGUIBackground(True, False)
        self._addArenaTypeData()
        Waiting.close()

    def _dispose(self):
        Waiting.close()
        g_sessionProvider.removeArenaCtrl(self)
        if not BattleReplay.isPlaying():
            BigWorld.wg_enableGUIBackground(False, True)
        super(BattleLoading, self)._dispose()

    def startControl(self, battleCtx, arenaVisitor):
        self._battleCtx = battleCtx
        self._arenaVisitor = arenaVisitor

    def stopControl(self):
        self._battleCtx = None
        self._arenaVisitor = None
        return

    def invalidateArenaInfo(self):
        arenaDP = self._battleCtx.getArenaDP()
        self._setTipsInfo()
        self._addArenaExtraData(arenaDP)
        self.__addPlayerData(arenaDP)
        self.invalidateVehiclesInfo(arenaDP)

    def invalidateVehiclesInfo(self, arenaDP):
        regionGetter = player_format.getRegionCode
        isSpeaking = self.bwProto.voipController.isPlayerSpeaking
        userGetter = self.usersStorage.getUser
        actionGetter = VehicleActions.getBitMask
        playerTeam = arenaDP.getNumberOfTeam()
        if self._arenaVisitor.hasRespawns():
            sortKey = vos_collections.RespawnSortKey
        else:
            sortKey = vos_collections.VehicleInfoSortKey
        isFallout = self._arenaVisitor.gui.isFalloutClassic()
        for isEnemy, collection in ((False, vos_collections.AllyItemsCollection(sortKey=sortKey)), (True, vos_collections.EnemyItemsCollection(sortKey=sortKey))):
            result = []
            for vInfoVO, vStatsVO in collection.iterator(arenaDP):
                result.append(self._makeItem(vInfoVO, vStatsVO, userGetter, isSpeaking, actionGetter, regionGetter, playerTeam, isEnemy, self._getSquadIdx(arenaDP, vInfoVO), isFallout))

            self.as_setVehiclesDataS({'vehiclesInfo': result,
             'isEnemy': isEnemy})

    def addVehicleInfo(self, vo, arenaDP):
        playerTeam = arenaDP.getNumberOfTeam()
        isEnemy = arenaDP.isEnemyTeam(vo.team)
        vStatsVO = arenaDP.getVehicleStats(vo.vehicleID)
        item = self._makeItem(vo, vStatsVO, self.usersStorage.getUser, self.bwProto.voipController.isPlayerSpeaking, VehicleActions.getBitMask, player_format.getRegionCode, playerTeam, isEnemy, self._getSquadIdx(arenaDP, vo))
        data = {'vehicleInfo': item,
         'vehiclesIDs': self._getInfoCollection(isEnemy).ids(self._battleCtx.getArenaDP()),
         'isEnemy': isEnemy}
        self.as_addVehicleInfoS(data)

    def updateVehiclesInfo(self, updated, arenaDP):
        playerTeam = arenaDP.getNumberOfTeam()
        for flags, vo in updated:
            isEnemy = arenaDP.isEnemyTeam(vo.team)
            vStatsVO = arenaDP.getVehicleStats(vo.vehicleID)
            if flags & INVALIDATE_OP.SORTING > 0:
                vehiclesIDs = self._getInfoCollection(isEnemy).ids(self._battleCtx.getArenaDP())
            else:
                vehiclesIDs = None
            item = self._makeItem(vo, vStatsVO, self.usersStorage.getUser, self.bwProto.voipController.isPlayerSpeaking, VehicleActions.getBitMask, player_format.getRegionCode, playerTeam, isEnemy, self._getSquadIdx(arenaDP, vo))
            self.as_updateVehicleInfoS({'vehicleInfo': item,
             'vehiclesIDs': vehiclesIDs,
             'isEnemy': isEnemy})

        return

    def invalidateVehicleStatus(self, flags, vo, arenaDP):
        isEnemy = arenaDP.isEnemyTeam(vo.team)
        if flags & INVALIDATE_OP.SORTING > 0:
            vehiclesIDs = self._getInfoCollection(isEnemy).ids(self._battleCtx.getArenaDP())
        else:
            vehiclesIDs = None
        self.as_setVehicleStatusS({'vehicleID': vo.vehicleID,
         'status': vo.vehicleStatus,
         'vehiclesIDs': vehiclesIDs,
         'isEnemy': isEnemy})
        return

    def invalidatePlayerStatus(self, flags, vo, arenaDP):
        self.as_setPlayerStatusS({'vehicleID': vo.vehicleID,
         'status': vo.playerStatus,
         'isEnemy': arenaDP.isEnemyTeam(vo.team)})

    def invalidateUsersTags(self):
        self.invalidateVehiclesInfo(self._battleCtx.getArenaDP())

    def updateSpaceLoadProgress(self, progress):
        self.as_setProgressS(progress)

    def arenaLoadCompleted(self):
        if not BattleReplay.isPlaying():
            self.destroy()
        else:
            BigWorld.wg_enableGUIBackground(False, False)

    def _getInfoCollection(self, isEnemy):
        if self._arenaVisitor.hasRespawns():
            sortKey = vos_collections.RespawnSortKey
        else:
            sortKey = vos_collections.VehicleInfoSortKey
        if isEnemy:
            collection = vos_collections.EnemyItemsCollection(sortKey=sortKey)
        else:
            collection = vos_collections.AllyItemsCollection(sortKey=sortKey)
        return collection

    def _makeItem(self, vInfoVO, vStatsVO, userGetter, isSpeaking, actionGetter, regionGetter, playerTeam, isEnemy, squadIdx, isFallout=False):
        player = vInfoVO.player
        vTypeVO = vInfoVO.vehicleType
        dbID = player.accountDBID
        user = userGetter(dbID)
        if user:
            isMuted = user.isMuted()
        else:
            isMuted = False
        alias = 'vm_enemy' if isEnemy else 'vm_ally'
        return {'accountDBID': dbID,
         'isMuted': isMuted,
         'isSpeaking': isSpeaking(dbID),
         'vehicleID': vInfoVO.vehicleID,
         'prebattleID': vInfoVO.prebattleID,
         'vehicleStatus': vInfoVO.vehicleStatus,
         'playerStatus': vInfoVO.getPlayerStatusInTeam(playerTeam=playerTeam),
         'squadIndex': squadIdx,
         'vehicleAction': actionGetter(vInfoVO.events),
         'vehicleIcon': vTypeVO.iconPath,
         'vehicleName': vTypeVO.shortName,
         'vehicleGuiName': vTypeVO.guiName,
         'playerName': player.getPlayerLabel(),
         'igrType': player.igrType,
         'clanAbbrev': player.clanAbbrev,
         'region': regionGetter(dbID),
         'vehicleType': vTypeVO.getClassName(),
         'teamColor': self.app.colorManager.getColorScheme(alias).get('aliasColor'),
         'vLevel': vTypeVO.level,
         'isFallout': isFallout}

    def _updateTipsInfo(self):
        pass

    def _setTipsInfo(self):
        arenaDP = self._battleCtx.getArenaDP()
        if self._arenaVisitor.hasResourcePoints():
            bgUrl = RES_ICONS.MAPS_ICONS_EVENTINFOPANEL_FALLOUTRESOURCEPOINTSEVENT
        elif self._arenaVisitor.hasFlags():
            bgUrl = RES_ICONS.MAPS_ICONS_EVENTINFOPANEL_FALLOUTFLAGSEVENT
        else:
            bgUrl = ''
        if self._arenaVisitor.gui.isFalloutClassic():
            self.as_setEventInfoPanelDataS({'bgUrl': bgUrl,
             'items': getHelpTextAsDicts(self._arenaVisitor)})
            self.as_setVisualTipInfoS(self.__makeVisualTipVO(arenaDP))
        elif not self.__isTipInited:
            battlesCount = DEFAULT_BATTLES_COUNT
            if g_lobbyContext.getBattlesCount() is not None:
                battlesCount = g_lobbyContext.getBattlesCount()
            classTag, vLvl, nation = arenaDP.getVehicleInfo().getTypeInfo()
            criteria = tips.getTipsCriteria(self._arenaVisitor)
            criteria.setBattleCount(battlesCount)
            criteria.setClassTag(classTag)
            criteria.setLevel(vLvl)
            criteria.setNation(nation)
            tip = criteria.find()
            self.as_setTipTitleS(text_styles.highTitle(tip.status))
            self.as_setTipS(text_styles.playerOnline(tip.body))
            self.as_setVisualTipInfoS(self.__makeVisualTipVO(arenaDP, tip))
            self.__isTipInited = True
        return

    def _getSquadIdx(self, arenaDP, vInfoVO):
        return vInfoVO.squadIndex

    def _addArenaTypeData(self):
        self.as_setMapIconS(SMALL_MAP_IMAGE_SF_PATH % self._arenaVisitor.type.getGeometryName())
        BigWorld.wg_setGUIBackground(self._battleCtx.getArenaScreenIcon())

    def _addArenaExtraData(self, arenaDP):
        arenaInfoData = {'mapName': self._battleCtx.getArenaTypeName(isInBattle=False),
         'winText': self._battleCtx.getArenaWinString(isInBattle=False),
         'battleTypeLocaleStr': self._battleCtx.getArenaDescriptionString(isInBattle=False),
         'battleTypeFrameLabel': self._battleCtx.getArenaFrameLabel(),
         'allyTeamName': self._battleCtx.getTeamName(enemy=False),
         'enemyTeamName': self._battleCtx.getTeamName(enemy=True)}
        if self._arenaVisitor.gui.isTutorialBattle():
            arenaInfoData['tipText'] = text_styles.main(BATTLE_TUTORIAL.LOADING_HINT_TEXT)
        self.as_setArenaInfoS(arenaInfoData)

    def __addPlayerData(self, arenaDP):
        vInfoVO = arenaDP.getVehicleInfo()
        self.as_setPlayerDataS(vInfoVO.vehicleID, vInfoVO.getSquadID())

    def __makeVisualTipVO(self, arenaDP, tip=None):
        setting = g_settingsCore.options.getSetting(settings_constants.GAME.BATTLE_LOADING_INFO)
        settingID = setting.getSettingID(isVisualOnly=self._arenaVisitor.gui.isSandboxBattle() or self._arenaVisitor.gui.isEventBattle(), isFallout=self._arenaVisitor.gui.isFalloutBattle())
        return {'settingID': settingID,
         'tipIcon': tip.icon if settingID == BattleLoadingTipSetting.OPTIONS.VISUAL else None,
         'arenaTypeID': self._arenaVisitor.type.getID(),
         'minimapTeam': arenaDP.getNumberOfTeam(),
         'showMinimap': settingID == BattleLoadingTipSetting.OPTIONS.MINIMAP}


class FalloutMultiTeamBattleLoading(BattleLoading):

    def addVehicleInfo(self, vo, arenaDP):
        playerTeam = arenaDP.getNumberOfTeam()
        isEnemy = arenaDP.isEnemyTeam(vo.team)
        vStatsVO = arenaDP.getVehicleStats(vo.vehicleID)
        item = self._makeItem(vo, vStatsVO, self.usersStorage.getUser, self.bwProto.voipController.isPlayerSpeaking, VehicleActions.getBitMask, player_format.getRegionCode, playerTeam, isEnemy, self._getSquadIdx(arenaDP, vo))
        self.as_addVehicleInfoS({'vehicleInfo': item,
         'vehiclesIDs': self._getInfoCollection(True).ids(self._battleCtx.getArenaDP())})

    def updateVehiclesInfo(self, updated, arenaDP):
        playerTeam = arenaDP.getNumberOfTeam()
        for flags, vo in updated:
            isEnemy = arenaDP.isEnemyTeam(vo.team)
            vStatsVO = arenaDP.getVehicleStats(vo.vehicleID)
            if flags & INVALIDATE_OP.SORTING > 0:
                vehiclesIDs = self._getInfoCollection(isEnemy).ids(self._battleCtx.getArenaDP())
            else:
                vehiclesIDs = None
            item = self._makeItem(vo, vStatsVO, self.usersStorage.getUser, self.bwProto.voipController.isPlayerSpeaking, VehicleActions.getBitMask, player_format.getRegionCode, playerTeam, isEnemy, self._getSquadIdx(arenaDP, vo))
            self.as_updateVehicleInfoS({'vehicleInfo': item,
             'vehiclesIDs': vehiclesIDs})

        return

    def invalidateVehicleStatus(self, flags, vo, arenaDP):
        if flags & INVALIDATE_OP.SORTING > 0:
            vehiclesIDs = self._getInfoCollection(arenaDP.isEnemyTeam(vo.team)).ids(self._battleCtx.getArenaDP())
        else:
            vehiclesIDs = None
        self.as_setVehicleStatusS({'vehicleID': vo.vehicleID,
         'status': vo.vehicleStatus,
         'vehiclesIDs': vehiclesIDs})
        return

    def invalidatePlayerStatus(self, flags, vo, arenaDP):
        self.as_setPlayerStatusS({'vehicleID': vo.vehicleID,
         'status': vo.playerStatus})

    def invalidateVehiclesInfo(self, arenaDP):
        regionGetter = player_format.getRegionCode
        isSpeaking = self.bwProto.voipController.isPlayerSpeaking
        userGetter = self.usersStorage.getUser
        actionGetter = VehicleActions.getBitMask
        playerTeam = arenaDP.getNumberOfTeam()
        result = []
        collection = self._getInfoCollection(True)
        for vInfoVO, vStatsVO in collection.iterator(arenaDP):
            result.append(self._makeItem(vInfoVO, vStatsVO, userGetter, isSpeaking, actionGetter, regionGetter, playerTeam, playerTeam != vInfoVO.team, self._getSquadIdx(arenaDP, vInfoVO)))

        self.as_setVehiclesDataS({'vehiclesInfo': result})

    def _getInfoCollection(self, isEnemy):
        if self._arenaVisitor.hasRespawns():
            sortKey = vos_collections.WinPointsAndRespawnSortKey
        else:
            sortKey = vos_collections.WinPointsAndVehicleInfoSortKey
        return vos_collections.FalloutMultiTeamItemsCollection(sortKey=sortKey)

    def _makeItem(self, vInfoVO, vStatsVO, userGetter, isSpeaking, actionGetter, regionGetter, playerTeam, isEnemy, squadIdx, isFallout=True):
        result = super(FalloutMultiTeamBattleLoading, self)._makeItem(vInfoVO, vStatsVO, userGetter, isSpeaking, actionGetter, regionGetter, playerTeam, isEnemy, squadIdx, isFallout)
        result['points'] = vStatsVO.winPoints
        return result

    def _setTipsInfo(self):
        self.as_setEventInfoPanelDataS({'bgUrl': RES_ICONS.MAPS_ICONS_EVENTINFOPANEL_FALLOUTFLAGSEVENT,
         'items': getHelpTextAsDicts(self._arenaVisitor)})

    def _addArenaExtraData(self, arenaDP):
        arenaInfoData = {'mapName': self._battleCtx.getArenaTypeName(isInBattle=False),
         'battleTypeLocaleStr': self._battleCtx.getArenaDescriptionString(isInBattle=False),
         'winText': text_styles.main(self._battleCtx.getArenaWinString(isInBattle=False)),
         'battleTypeFrameLabel': self._battleCtx.getArenaFrameLabel()}
        self.as_setArenaInfoS(arenaInfoData)
