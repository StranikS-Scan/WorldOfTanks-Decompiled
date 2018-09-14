# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle_loading.py
import BattleReplay
import BigWorld
import constants
from debug_utils import LOG_ERROR
from helpers import tips, i18n
from gui.Scaleform.locale.FALLOUT import FALLOUT
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.LobbyContext import g_lobbyContext
from gui.Scaleform import getNecessaryArenaFrameName
from gui.battle_control import g_sessionProvider
from gui.battle_control.arena_info.interfaces import IArenaVehiclesController
from gui.battle_control.arena_info import getClientArena, getArenaTypeID, getArenaIcon, getArenaGuiType
from gui.battle_control.arena_info import hasResourcePoints, hasFlags, getIsMultiteam
from gui.battle_control.arena_info.arena_vos import VehicleActions
from gui.battle_control.arena_info.settings import INVALIDATE_OP
from gui.prb_control.formatters import getPrebattleFullDescription
from gui.shared.formatters import text_styles
from gui.shared.utils.functions import getBattleSubTypeWinText, getArenaSubTypeName, isBaseExists
from gui.Scaleform.Waiting import Waiting
from gui.Scaleform.daapi import LobbySubView
from gui.Scaleform.daapi.view.meta.BattleLoadingMeta import BattleLoadingMeta
from gui.Scaleform.daapi.view.fallout_info_panel_helper import getHelpTextAsDicts
from messenger.storage import storage_getter
from gui.Scaleform.locale.MENU import MENU
DEFAULT_BATTLES_COUNT = 100

class BattleLoading(LobbySubView, BattleLoadingMeta, IArenaVehiclesController):
    MAP_BG_SOURCE = 'gui/maps/icons/map/screen/%s.dds'
    SMALL_MAP_SOURCE = '../maps/icons/map/battleLoading/%s.png'
    __background_alpha__ = 0.0

    def __init__(self, _ = None):
        super(BattleLoading, self).__init__()
        self._battleCtx = None
        self._isArenaTypeDataInited = False
        self.__isTipInited = False
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
        arena = getClientArena()
        isFallout = arena.guiType == constants.ARENA_GUI_TYPE.EVENT_BATTLES
        for isEnemy in (False, True):
            result = []
            for vInfoVO, _, viStatsVO in arenaDP.getVehiclesIterator(isEnemy):
                result.append(self._makeItem(vInfoVO, viStatsVO, userGetter, isSpeaking, actionGetter, regionGetter, playerTeam, isEnemy, self._getSquadIdx(arenaDP, vInfoVO), isFallout))

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

    def _makeItem(self, vInfoVO, viStatsVO, userGetter, isSpeaking, actionGetter, regionGetter, playerTeam, isEnemy, squadIdx, isFallout = False):
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
        arena = getClientArena()
        isFallout = arena.guiType == constants.ARENA_GUI_TYPE.EVENT_BATTLES
        arenaDP = self._battleCtx.getArenaDP()
        if hasResourcePoints():
            bgUrl = RES_ICONS.MAPS_ICONS_EVENTINFOPANEL_FALLOUTRESOURCEPOINTSEVENT
        elif hasFlags():
            bgUrl = RES_ICONS.MAPS_ICONS_EVENTINFOPANEL_FALLOUTFLAGSEVENT
        else:
            bgUrl = ''
        if isFallout:
            self.as_setEventInfoPanelDataS({'bgUrl': bgUrl,
             'items': getHelpTextAsDicts(arena.arenaType)})
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
            self.__isTipInited = True
        return

    def _getSquadIdx(self, arenaDP, vInfoVO):
        return vInfoVO.squadIndex

    def _addArenaTypeData(self):
        arena = getClientArena()
        if arena:
            arenaType = arena.arenaType
            self.as_setMapIconS(BattleLoading.SMALL_MAP_SOURCE % arenaType.geometryName)
        BigWorld.wg_setGUIBackground(getArenaIcon(BattleLoading.MAP_BG_SOURCE))

    def _addArenaExtraData(self, arenaDP):
        arena = getClientArena()
        if arena:
            arenaType = arena.arenaType
            extraData = arena.extraData or {}
            descExtra = getPrebattleFullDescription(extraData)
            arenaTypeID = getArenaTypeID()
            arenaSubType = getArenaSubTypeName(arenaTypeID)
            team = arenaDP.getNumberOfTeam()
            enemy = arenaDP.getNumberOfTeam(True)
            hasBase = isBaseExists(arenaTypeID, team)
            allyTeamName, enemyTeamName = self._battleCtx.getTeamName(team), self._battleCtx.getTeamName(enemy)
            if arena.guiType == constants.ARENA_GUI_TYPE.EVENT_BATTLES:
                winText = i18n.makeString('#arenas:type/%s/description' % arenaSubType)
            else:
                winText = getBattleSubTypeWinText(arenaTypeID, 1 if hasBase else 2)
            if descExtra:
                battleTypeLocaleStr = descExtra
                if arena.guiType != constants.ARENA_GUI_TYPE.UNKNOWN and arena.guiType in constants.ARENA_GUI_TYPE_LABEL.LABELS:
                    battleTypeFrameLabel = constants.ARENA_GUI_TYPE_LABEL.LABELS[arena.guiType]
                else:
                    battleTypeFrameLabel = 'neutral'
            elif arena.guiType in [constants.ARENA_GUI_TYPE.RANDOM, constants.ARENA_GUI_TYPE.TRAINING]:
                battleTypeLocaleStr = '#arenas:type/%s/name' % arenaSubType
                battleTypeFrameLabel = getNecessaryArenaFrameName(arenaSubType, hasBase)
            elif arena.guiType == constants.ARENA_GUI_TYPE.EVENT_BATTLES and hasResourcePoints():
                battleTypeFrameLabel = 'resourcePoints'
                battleTypeLocaleStr = MENU.LOADING_BATTLETYPES_RESOURCEPOINTS
            else:
                battleTypeLocaleStr = '#menu:loading/battleTypes/%d' % arena.guiType
                if arena.guiType != constants.ARENA_GUI_TYPE.UNKNOWN and arena.guiType in constants.ARENA_GUI_TYPE_LABEL.LABELS:
                    battleTypeFrameLabel = constants.ARENA_GUI_TYPE_LABEL.LABELS[arena.guiType]
                else:
                    battleTypeFrameLabel = 'neutral'
            arenaInfoData = {'mapName': arenaType.name,
             'winText': winText,
             'battleTypeLocaleStr': battleTypeLocaleStr,
             'battleTypeFrameLabel': battleTypeFrameLabel,
             'allyTeamName': allyTeamName,
             'enemyTeamName': enemyTeamName}
            self.as_setArenaInfoS(arenaInfoData)

    def __addPlayerData(self, arenaDP):
        vInfoVO = arenaDP.getVehicleInfo()
        self.as_setPlayerDataS(vInfoVO.vehicleID, vInfoVO.getSquadID())


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
        for vInfoVO, _, viStatsVO in sorted(arenaDP.getAllVehiclesIteratorByTeamScore()):
            result.append(self._makeItem(vInfoVO, viStatsVO, userGetter, isSpeaking, actionGetter, regionGetter, playerTeam, playerTeam != vInfoVO.team, self._getSquadIdx(arenaDP, vInfoVO)))

        self.as_setVehiclesDataS({'vehiclesInfo': result})

    def _makeItem(self, vInfoVO, viStatsVO, userGetter, isSpeaking, actionGetter, regionGetter, playerTeam, isEnemy, squadIdx, isFallout = True):
        result = super(FalloutMultiTeamBattleLoading, self)._makeItem(vInfoVO, viStatsVO, userGetter, isSpeaking, actionGetter, regionGetter, playerTeam, isEnemy, squadIdx, isFallout)
        result['points'] = viStatsVO.winPoints
        return result

    def _setTipsInfo(self):
        self.as_setEventInfoPanelDataS({'bgUrl': RES_ICONS.MAPS_ICONS_EVENTINFOPANEL_FALLOUTFLAGSEVENT,
         'items': getHelpTextAsDicts(getClientArena().arenaType)})

    def _getSquadIdx(self, arenaDP, vInfoVO):
        return arenaDP.getMultiTeamsIndexes()[vInfoVO.team]

    def _addArenaExtraData(self, arenaDP):
        arena = getClientArena()
        winText = text_styles.main(FALLOUT.BATTLELOADING_MULTITEAM_WINTEXT)
        arenaInfoData = {'battleTypeLocaleStr': arena.arenaType.name,
         'winText': winText}
        self.as_setArenaInfoS(arenaInfoData)
