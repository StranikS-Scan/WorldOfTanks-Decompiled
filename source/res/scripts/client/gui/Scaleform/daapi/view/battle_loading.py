# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle_loading.py
import BattleReplay
import BigWorld
from account_helpers.settings_core import settings_constants
from account_helpers.settings_core.SettingsCore import g_settingsCore
from account_helpers.settings_core.options import BattleLoadingTipSetting
import constants
from gui.Scaleform.locale.BATTLE_TUTORIAL import BATTLE_TUTORIAL
from helpers import tips, i18n
from gui.Scaleform.locale.FALLOUT import FALLOUT
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.LobbyContext import g_lobbyContext
from gui.Scaleform import getNecessaryArenaFrameName
from gui.battle_control import g_sessionProvider, arena_info
from gui.battle_control.arena_info.interfaces import IArenaVehiclesController
from gui.battle_control.arena_info import isFalloutClassic, hasRespawns
from gui.battle_control.arena_info.arena_vos import VehicleActions
from gui.battle_control.arena_info.settings import INVALIDATE_OP
from gui.prb_control.formatters import getPrebattleFullDescription
from gui.shared.formatters import text_styles
from gui.shared.utils.functions import getBattleSubTypeWinText, getArenaSubTypeName, isBaseExists
from gui.Scaleform.Waiting import Waiting
from gui.Scaleform.daapi import LobbySubView
from gui.Scaleform.daapi.view.meta.BaseBattleLoadingMeta import BaseBattleLoadingMeta
from gui.Scaleform.daapi.view.fallout_info_panel_helper import getHelpTextAsDicts
from messenger.storage import storage_getter
from gui.shared.utils import toUpper
DEFAULT_BATTLES_COUNT = 100

class BattleLoading(LobbySubView, BaseBattleLoadingMeta, IArenaVehiclesController):
    MAP_BG_SOURCE = 'gui/maps/icons/map/screen/%s.dds'
    SMALL_MAP_SOURCE = '../maps/icons/map/battleLoading/%s.png'
    __background_alpha__ = 0.0

    def __init__(self, _=None):
        super(BattleLoading, self).__init__()
        self._battleCtx = None
        self._isArenaTypeDataInited = False
        self.__isTipInited = False
        self.__isFallout = isFalloutClassic()
        return

    @storage_getter('users')
    def usersStorage(self):
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

    def setBattleCtx(self, battleCtx):
        self._battleCtx = battleCtx

    def invalidateArenaInfo(self):
        arenaDP = self._battleCtx.getArenaDP()
        self._setTipsInfo()
        self._addArenaExtraData(arenaDP)
        self.__addPlayerData(arenaDP)
        self.invalidateVehiclesInfo(arenaDP)

    def invalidateVehiclesInfo(self, arenaDP):
        regionGetter = self._battleCtx.getRegionCode
        isSpeaking = self.app.voiceChatManager.isPlayerSpeaking
        userGetter = self.usersStorage.getUser
        actionGetter = VehicleActions.getBitMask
        playerTeam = arenaDP.getNumberOfTeam()
        for isEnemy in (False, True):
            result = []
            for vInfoVO, _, viStatsVO in arenaDP.getVehiclesIterator(isEnemy, hasRespawns()):
                result.append(self._makeItem(vInfoVO, viStatsVO, userGetter, isSpeaking, actionGetter, regionGetter, playerTeam, isEnemy, self._getSquadIdx(arenaDP, vInfoVO), self.__isFallout))

            self.as_setVehiclesDataS({'vehiclesInfo': result,
             'isEnemy': isEnemy})

    def addVehicleInfo(self, vo, arenaDP):
        playerTeam = arenaDP.getNumberOfTeam()
        isEnemy = arenaDP.isEnemyTeam(vo.team)
        viStatsVO = arenaDP.getVehicleInteractiveStats(vo.vehicleID)
        item = self._makeItem(vo, viStatsVO, self.usersStorage.getUser, self.app.voiceChatManager.isPlayerSpeaking, VehicleActions.getBitMask, self._battleCtx.getRegionCode, playerTeam, isEnemy, self._getSquadIdx(arenaDP, vo))
        data = {'vehicleInfo': item,
         'vehiclesIDs': arenaDP.getVehiclesIDs(isEnemy),
         'isEnemy': isEnemy}
        self.as_addVehicleInfoS(data)

    def invalidateVehicleInfo(self, flags, vo, arenaDP):
        playerTeam = arenaDP.getNumberOfTeam()
        isEnemy = arenaDP.isEnemyTeam(vo.team)
        viStatsVO = arenaDP.getVehicleInteractiveStats(vo.vehicleID)
        if flags & INVALIDATE_OP.SORTING > 0:
            vehiclesIDs = arenaDP.getVehiclesIDs(isEnemy)
        else:
            vehiclesIDs = None
        item = self._makeItem(vo, viStatsVO, self.usersStorage.getUser, self.app.voiceChatManager.isPlayerSpeaking, VehicleActions.getBitMask, self._battleCtx.getRegionCode, playerTeam, isEnemy, self._getSquadIdx(arenaDP, vo))
        self.as_updateVehicleInfoS({'vehicleInfo': item,
         'vehiclesIDs': vehiclesIDs,
         'isEnemy': isEnemy})
        return

    def invalidateVehicleStatus(self, flags, vo, arenaDP):
        isEnemy = arenaDP.isEnemyTeam(vo.team)
        if flags & INVALIDATE_OP.SORTING > 0:
            vehiclesIDs = arenaDP.getVehiclesIDs(isEnemy)
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

    def _makeItem(self, vInfoVO, viStatsVO, userGetter, isSpeaking, actionGetter, regionGetter, playerTeam, isEnemy, squadIdx, isFallout=False):
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
        arena = arena_info.getClientArena()
        arenaDP = self._battleCtx.getArenaDP()
        if arena_info.hasResourcePoints():
            bgUrl = RES_ICONS.MAPS_ICONS_EVENTINFOPANEL_FALLOUTRESOURCEPOINTSEVENT
        elif arena_info.hasFlags():
            bgUrl = RES_ICONS.MAPS_ICONS_EVENTINFOPANEL_FALLOUTFLAGSEVENT
        else:
            bgUrl = ''
        if self.__isFallout:
            self.as_setEventInfoPanelDataS({'bgUrl': bgUrl,
             'items': getHelpTextAsDicts(arena_info.getArenaType())})
            self.as_setVisualTipInfoS(self.__makeVisualTipVO(arenaDP, arena))
        elif not self.__isTipInited:
            battlesCount = DEFAULT_BATTLES_COUNT
            if g_lobbyContext.getBattlesCount() is not None:
                battlesCount = g_lobbyContext.getBattlesCount()
            classTag, vLvl, nation = arenaDP.getVehicleInfo().getTypeInfo()
            criteria = tips.getTipsCriteria(arena)
            criteria.setBattleCount(battlesCount)
            criteria.setClassTag(classTag)
            criteria.setLevel(vLvl)
            criteria.setNation(nation)
            tip = criteria.find()
            self.as_setTipTitleS(text_styles.highTitle(tip.status))
            self.as_setTipS(text_styles.playerOnline(tip.body))
            self.as_setVisualTipInfoS(self.__makeVisualTipVO(arenaDP, arena, tip))
            self.__isTipInited = True
        return

    def _getSquadIdx(self, arenaDP, vInfoVO):
        return vInfoVO.squadIndex

    def _addArenaTypeData(self):
        arenaType = arena_info.getArenaType()
        if arenaType:
            self.as_setMapIconS(BattleLoading.SMALL_MAP_SOURCE % arenaType.geometryName)
        BigWorld.wg_setGUIBackground(arena_info.getArenaIcon(BattleLoading.MAP_BG_SOURCE))

    def _addArenaExtraData(self, arenaDP):
        arena = arena_info.getClientArena()
        if arena:
            arenaType = arena.arenaType
            extraData = arena.extraData or {}
            descExtra = getPrebattleFullDescription(extraData)
            arenaTypeID = arena_info.getArenaTypeID()
            arenaSubType = getArenaSubTypeName(arenaTypeID)
            team = arenaDP.getNumberOfTeam()
            enemy = arenaDP.getNumberOfTeam(True)
            hasBase = isBaseExists(arenaTypeID, team)
            allyTeamName, enemyTeamName = self._battleCtx.getTeamName(team), self._battleCtx.getTeamName(enemy)
            if self.__isFallout:
                winText = i18n.makeString('#arenas:type/%s/description' % arenaSubType)
            else:
                winText = getBattleSubTypeWinText(arenaTypeID, 1 if hasBase else 2)
            if descExtra:
                battleTypeLocaleStr = descExtra
                if arena.guiType != constants.ARENA_GUI_TYPE.UNKNOWN and arena.guiType in constants.ARENA_GUI_TYPE_LABEL.LABELS:
                    battleTypeFrameLabel = constants.ARENA_GUI_TYPE_LABEL.LABELS[arena.guiType]
                else:
                    battleTypeFrameLabel = 'neutral'
            elif arena.guiType in (constants.ARENA_GUI_TYPE.RANDOM, constants.ARENA_GUI_TYPE.TRAINING):
                battleTypeLocaleStr = '#arenas:type/%s/name' % arenaSubType
                battleTypeFrameLabel = getNecessaryArenaFrameName(arenaSubType, hasBase)
            elif arena.guiType != constants.ARENA_GUI_TYPE.UNKNOWN and arena.guiType in constants.ARENA_GUI_TYPE_LABEL.LABELS:
                battleTypeLocaleStr = '#menu:loading/battleTypes/%d' % arena.guiType
                battleTypeFrameLabel = constants.ARENA_GUI_TYPE_LABEL.LABELS[arena.guiType]
            else:
                battleTypeLocaleStr = '#menu:loading/battleTypes/%d' % arena.guiType
                battleTypeFrameLabel = 'neutral'
            arenaInfoData = {'mapName': toUpper(arenaType.name),
             'winText': winText,
             'battleTypeLocaleStr': battleTypeLocaleStr,
             'battleTypeFrameLabel': battleTypeFrameLabel,
             'allyTeamName': allyTeamName,
             'enemyTeamName': enemyTeamName}
            arena = arena_info.getClientArena()
            if arena.guiType == constants.ARENA_GUI_TYPE.TUTORIAL:
                arenaInfoData['tipText'] = text_styles.main(BATTLE_TUTORIAL.LOADING_HINT_TEXT)
            self.as_setArenaInfoS(arenaInfoData)

    def __addPlayerData(self, arenaDP):
        vInfoVO = arenaDP.getVehicleInfo()
        self.as_setPlayerDataS(vInfoVO.vehicleID, vInfoVO.getSquadID())

    def __makeVisualTipVO(self, arenaDP, arena, tip=None):
        setting = g_settingsCore.options.getSetting(settings_constants.GAME.BATTLE_LOADING_INFO)
        settingID = setting.getSettingID(isInSandbox=arena_info.isInSandboxBattle(arena), isFallout=arena_info.isFalloutBattle())
        return {'settingID': settingID,
         'tipIcon': tip.icon if settingID == BattleLoadingTipSetting.OPTIONS.VISUAL else None,
         'arenaTypeID': arena_info.getArenaTypeID(),
         'minimapTeam': arenaDP.getNumberOfTeam(),
         'showMinimap': settingID == BattleLoadingTipSetting.OPTIONS.MINIMAP}


class FalloutMultiTeamBattleLoading(BattleLoading):

    def addVehicleInfo(self, vo, arenaDP):
        playerTeam = arenaDP.getNumberOfTeam()
        isEnemy = arenaDP.isEnemyTeam(vo.team)
        viStatsVO = arenaDP.getVehicleInteractiveStats(vo.vehicleID)
        item = self._makeItem(vo, viStatsVO, self.usersStorage.getUser, self.app.voiceChatManager.isPlayerSpeaking, VehicleActions.getBitMask, self._battleCtx.getRegionCode, playerTeam, isEnemy, self._getSquadIdx(arenaDP, vo))
        self.as_addVehicleInfoS({'vehicleInfo': item,
         'vehiclesIDs': arenaDP.getAllVehiclesIDs()})

    def invalidateVehicleInfo(self, flags, vo, arenaDP):
        playerTeam = arenaDP.getNumberOfTeam()
        isEnemy = arenaDP.isEnemyTeam(vo.team)
        viStatsVO = arenaDP.getVehicleInteractiveStats(vo.vehicleID)
        if flags & INVALIDATE_OP.SORTING > 0:
            vehiclesIDs = arenaDP.getAllVehiclesIDs()
        else:
            vehiclesIDs = None
        item = self._makeItem(vo, viStatsVO, self.usersStorage.getUser, self.app.voiceChatManager.isPlayerSpeaking, VehicleActions.getBitMask, self._battleCtx.getRegionCode, playerTeam, isEnemy, self._getSquadIdx(arenaDP, vo))
        self.as_updateVehicleInfoS({'vehicleInfo': item,
         'vehiclesIDs': vehiclesIDs})
        return

    def invalidateVehicleStatus(self, flags, vo, arenaDP):
        if flags & INVALIDATE_OP.SORTING > 0:
            vehiclesIDs = arenaDP.getAllVehiclesIDs()
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
        regionGetter = self._battleCtx.getRegionCode
        isSpeaking = self.app.voiceChatManager.isPlayerSpeaking
        userGetter = self.usersStorage.getUser
        actionGetter = VehicleActions.getBitMask
        playerTeam = arenaDP.getNumberOfTeam()
        result = []
        for vInfoVO, _, viStatsVO in sorted(arenaDP.getAllVehiclesIteratorByTeamScore(hasRespawns())):
            result.append(self._makeItem(vInfoVO, viStatsVO, userGetter, isSpeaking, actionGetter, regionGetter, playerTeam, playerTeam != vInfoVO.team, self._getSquadIdx(arenaDP, vInfoVO)))

        self.as_setVehiclesDataS({'vehiclesInfo': result})

    def _makeItem(self, vInfoVO, viStatsVO, userGetter, isSpeaking, actionGetter, regionGetter, playerTeam, isEnemy, squadIdx, isFallout=True):
        result = super(FalloutMultiTeamBattleLoading, self)._makeItem(vInfoVO, viStatsVO, userGetter, isSpeaking, actionGetter, regionGetter, playerTeam, isEnemy, squadIdx, isFallout)
        result['points'] = viStatsVO.winPoints
        return result

    def _setTipsInfo(self):
        self.as_setEventInfoPanelDataS({'bgUrl': RES_ICONS.MAPS_ICONS_EVENTINFOPANEL_FALLOUTFLAGSEVENT,
         'items': getHelpTextAsDicts(arena_info.getArenaType())})

    def _getSquadIdx(self, arenaDP, vInfoVO):
        return arenaDP.getMultiTeamsIndexes()[vInfoVO.team]

    def _addArenaExtraData(self, arenaDP):
        winText = text_styles.main(FALLOUT.BATTLELOADING_MULTITEAM_WINTEXT)
        arenaInfoData = {'mapName': toUpper(arena_info.getArenaType().name),
         'battleTypeLocaleStr': '#menu:loading/battleTypes/%d' % arena_info.getArenaGuiType(),
         'winText': winText,
         'battleTypeFrameLabel': arena_info.getArenaGuiTypeLabel()}
        self.as_setArenaInfoS(arenaInfoData)
