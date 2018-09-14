# Embedded file name: scripts/client/gui/Scaleform/daapi/view/BattleLoading.py
import BattleReplay
import BigWorld
import constants
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.shared.utils.TimeInterval import TimeInterval
from gui.LobbyContext import g_lobbyContext
from gui.Scaleform import getNecessaryArenaFrameName
from gui.battle_control import g_sessionProvider
from gui.battle_control.arena_info import IArenaController, getClientArena, getArenaTypeID
from gui.battle_control.arena_info.arena_vos import VehicleActions
from gui.battle_control.arena_info.settings import INVALIDATE_OP
from gui.prb_control.formatters import getPrebattleFullDescription
from gui.shared.formatters import text_styles
from gui.shared.utils.functions import getBattleSubTypeWinText, getArenaSubTypeName, isBaseExists
from gui.Scaleform.Waiting import Waiting
from gui.Scaleform.daapi import LobbySubView
from gui.Scaleform.daapi.view.meta.BattleLoadingMeta import BattleLoadingMeta
from gui.shared.view_helpers import FalloutInfoPanelHelper
from messenger.storage import storage_getter
from helpers import tips, i18n
DEFAULT_BATTLES_COUNT = 100
NEW_TIP_DURATION = 5

class BattleLoading(LobbySubView, BattleLoadingMeta, IArenaController):
    MAP_BG_SOURCE = 'gui/maps/icons/map/screen/%s.dds'
    SMALL_MAP_SOURCE = '../maps/icons/map/battleLoading/%s.png'

    def __init__(self, ctx = None):
        super(BattleLoading, self).__init__(backAlpha=0.0)
        self.__logArenaUniID = False
        self.__battleCtx = None
        self.__isArenaTypeDataInited = False
        self.__updateTipTI = None
        self.__tipsGetter = None
        return

    @storage_getter('users')
    def usersStorage(self):
        return None

    def _populate(self):
        super(BattleLoading, self)._populate()
        g_sessionProvider.addArenaCtrl(self)
        BigWorld.wg_updateColorGrading()
        BigWorld.wg_enableGUIBackground(True, False)
        self.__addArenaTypeData()
        Waiting.close()

    def _dispose(self):
        Waiting.close()
        g_sessionProvider.removeArenaCtrl(self)
        BigWorld.wg_enableGUIBackground(False, True)
        super(BattleLoading, self)._dispose()
        self.__tipsGetter = None
        if self.__updateTipTI:
            self.__updateTipTI.stop()
            self.__updateTipTI = None
        return

    def setBattleCtx(self, battleCtx):
        self.__battleCtx = battleCtx

    def invalidateArenaInfo(self):
        arenaDP = self.__battleCtx.getArenaDP()
        self.__setTipsInfo()
        self.__addArenaExtraData(arenaDP)
        self.__addPlayerData(arenaDP)
        self.invalidateVehiclesInfo(arenaDP)

    def invalidateVehiclesInfo(self, arenaDP):
        regionGetter = self.__battleCtx.getRegionCode
        isSpeaking = self.app.voiceChatManager.isPlayerSpeaking
        userGetter = self.usersStorage.getUser
        actionGetter = VehicleActions.getBitMask
        playerTeam = arenaDP.getNumberOfTeam()
        for isEnemy in (False, True):
            result = []
            for vInfoVO, _, _ in arenaDP.getTeamIterator(isEnemy):
                result.append(self.__makeItem(vInfoVO, userGetter, isSpeaking, actionGetter, regionGetter, playerTeam, isEnemy))

            self.as_setVehiclesDataS(isEnemy, result)

    def addVehicleInfo(self, vo, arenaDP):
        playerTeam = arenaDP.getNumberOfTeam()
        isEnemy = vo.team != playerTeam
        item = self.__makeItem(vo, self.usersStorage.getUser, self.app.voiceChatManager.isPlayerSpeaking, VehicleActions.getBitMask, self.__battleCtx.getRegionCode, playerTeam, isEnemy)
        self.as_addVehicleInfoS(isEnemy, item, arenaDP.getVehiclesIDs(isEnemy))

    def invalidateVehicleInfo(self, flags, vo, arenaDP):
        playerTeam = arenaDP.getNumberOfTeam()
        isEnemy = vo.team != playerTeam
        if flags & INVALIDATE_OP.SORTING > 0:
            vehiclesIDs = arenaDP.getVehiclesIDs(isEnemy)
        else:
            vehiclesIDs = None
        item = self.__makeItem(vo, self.usersStorage.getUser, self.app.voiceChatManager.isPlayerSpeaking, VehicleActions.getBitMask, self.__battleCtx.getRegionCode, playerTeam, isEnemy)
        self.as_updateVehicleInfoS(isEnemy, item, vehiclesIDs)
        return

    def invalidateVehicleStatus(self, flags, vo, arenaDP):
        isEnemy = vo.team != arenaDP.getNumberOfTeam()
        if flags & INVALIDATE_OP.SORTING > 0:
            vehiclesIDs = arenaDP.getVehiclesIDs(isEnemy)
        else:
            vehiclesIDs = None
        self.as_setVehicleStatusS(isEnemy, vo.vehicleID, vo.vehicleStatus, vehiclesIDs)
        return

    def invalidatePlayerStatus(self, flags, vo, arenaDP):
        self.as_setPlayerStatusS(vo.team != arenaDP.getNumberOfTeam(), vo.vehicleID, vo.playerStatus)

    def invalidateUsersTags(self):
        self.invalidateVehiclesInfo(self.__battleCtx.getArenaDP())

    def updateSpaceLoadProgress(self, progress):
        self.as_setProgressS(progress)

    def arenaLoadCompleted(self):
        if not BattleReplay.isPlaying():
            self.destroy()
        else:
            BigWorld.wg_enableGUIBackground(False, False)

    def __makeItem(self, vInfoVO, userGetter, isSpeaking, actionGetter, regionGetter, playerTeam, isEnemy):
        player = vInfoVO.player
        vTypeVO = vInfoVO.vehicleType
        dbID = player.accountDBID
        user = userGetter(dbID)
        if user:
            isMuted = user.isMuted()
        else:
            isMuted = False
        return {'accountDBID': dbID,
         'isMuted': isMuted,
         'isSpeaking': isSpeaking(dbID),
         'vehicleID': vInfoVO.vehicleID,
         'prebattleID': vInfoVO.prebattleID,
         'vehicleStatus': vInfoVO.vehicleStatus,
         'playerStatus': vInfoVO.getPlayerStatusInTeam(playerTeam=playerTeam),
         'squadIndex': vInfoVO.squadIndex,
         'vehicleAction': actionGetter(vInfoVO.events),
         'vehicleIcon': vTypeVO.iconPath,
         'vehicleName': vTypeVO.shortName,
         'vehicleGuiName': vTypeVO.guiName,
         'playerName': player.getPlayerLabel(),
         'igrType': player.igrType,
         'clanAbbrev': player.clanAbbrev,
         'region': regionGetter(dbID)}

    def __addArenaTypeData(self):
        arena = getClientArena()
        if arena:
            arenaType = arena.arenaType
            mapBG = arenaType.geometryName
            if arena.guiType != constants.ARENA_GUI_TYPE.EVENT_BATTLES:
                self.as_setMapNameS(arenaType.name)
            elif arenaType.gameplayName in ('fallout', 'fallout2'):
                mapBG += '_fallout'
            BigWorld.wg_setGUIBackground(BattleLoading.MAP_BG_SOURCE % mapBG)

    def _updateTipsInfo(self):
        if self.__tipsGetter is not None:
            statusStr, tipStr = next(self.__tipsGetter)
            self.as_setTipTitleS(text_styles.highTitle(statusStr))
            self.as_setTipS(text_styles.main(tipStr))
        return

    def __setTipsInfo(self):
        showFalloutEventInfo = False
        arena = getClientArena()
        if arena is not None:
            showFalloutEventInfo = arena.guiType == constants.ARENA_GUI_TYPE.EVENT_BATTLES
        if showFalloutEventInfo:
            self.as_setEventInfoPanelDataS({'bgUrl': RES_ICONS.MAPS_ICONS_EVENTINFOPANEL_FALLOUTEVENT,
             'items': FalloutInfoPanelHelper.getHelpTextAsDicts(arena.arenaType)})
        elif self.__updateTipTI is None:
            battlesCount = DEFAULT_BATTLES_COUNT
            if g_lobbyContext.getBattlesCount() is not None:
                battlesCount = g_lobbyContext.getBattlesCount()
            arenaDP = self.__battleCtx.getArenaDP()
            vType, vLvl, nation = arenaDP.getVehicleInfo().getTypeInfo()
            self.__tipsGetter = tips.getTipsIterator(battlesCount, vType, nation, vLvl)
            if self.__tipsGetter is not None:
                self._updateTipsInfo()
                self.__updateTipTI = TimeInterval(NEW_TIP_DURATION, self, '_updateTipsInfo')
                self.__updateTipTI.start()
        return

    def __addArenaExtraData(self, arenaDP):
        arena = getClientArena()
        if arena:
            extraData = arena.extraData or {}
            descExtra = getPrebattleFullDescription(extraData)
            arenaTypeID = getArenaTypeID()
            arenaSubType = getArenaSubTypeName(arenaTypeID)
            team = arenaDP.getNumberOfTeam()
            enemy = arenaDP.getNumberOfTeam(True)
            hasBase = isBaseExists(arenaTypeID, team)
            opponents = extraData.get('opponents', {})
            team1 = opponents.get(str(team), {}).get('name', '#menu:loading/team1')
            team2 = opponents.get(str(enemy), {}).get('name', '#menu:loading/team2')
            self.as_setTeamsS(team1, team2)
            if arena.guiType == constants.ARENA_GUI_TYPE.EVENT_BATTLES:
                self.as_setWinTextS(i18n.makeString('#arenas:type/fallout/description'))
            else:
                self.as_setWinTextS(getBattleSubTypeWinText(arenaTypeID, 1 if hasBase else 2))
            if descExtra:
                self.as_setBattleTypeNameS(descExtra)
                self.as_setBattleTypeFrameNumS(arena.guiType + 1)
            elif arena.guiType in [constants.ARENA_GUI_TYPE.RANDOM, constants.ARENA_GUI_TYPE.TRAINING]:
                self.as_setBattleTypeNameS('#arenas:type/%s/name' % arenaSubType)
                self.as_setBattleTypeFrameNameS(getNecessaryArenaFrameName(arenaSubType, hasBase))
                if arena.guiType == constants.ARENA_GUI_TYPE.TRAINING and self.__logArenaUniID == False:
                    self.__logArenaUniID = True
                    from time import strftime, localtime
                    from debug_utils import LOG_NOTE
                    LOG_NOTE('arenaUniqueID: %d | timestamp: %s' % (arena.arenaUniqueID, strftime('%d.%m.%Y %H:%M:%S', localtime())))
            else:
                self.as_setBattleTypeNameS('#menu:loading/battleTypes/%d' % arena.guiType)
                if arena.guiType in constants.ARENA_GUI_TYPE_LABEL.LABELS:
                    self.as_setBattleTypeFrameNameS(constants.ARENA_GUI_TYPE_LABEL.LABELS[arena.guiType])
                else:
                    self.as_setBattleTypeFrameNumS(arena.guiType + 1)

    def __addPlayerData(self, arenaDP):
        vInfoVO = arenaDP.getVehicleInfo()
        self.as_setPlayerDataS(vInfoVO.vehicleID, vInfoVO.getSquadID())
