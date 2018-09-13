# Embedded file name: scripts/client/gui/Scaleform/daapi/view/BattleLoading.py
import BattleReplay
import constants
from helpers import i18n
from gui.BattleContext import g_battleContext
from gui.arena_info import IArenaController, getClientArena, getArenaTypeID, isEventBattle
from gui.arena_info.arena_vos import VehicleActions
from gui.arena_info.settings import INVALIDATE_OP
from gui.prb_control.formatters import getPrebattleFullDescription
from helpers import tips
from gui.shared.utils.functions import getBattleSubTypeWinText, getArenaSubTypeName, isBaseExists
from gui.Scaleform.Waiting import Waiting
from gui.Scaleform.daapi import LobbySubView
from gui.Scaleform.daapi.view.meta.BattleLoadingMeta import BattleLoadingMeta
from messenger.storage import storage_getter

class BattleLoading(LobbySubView, BattleLoadingMeta, IArenaController):
    MAP_BG_SOURCE = '../maps/icons/map/screen/%s.png'

    def __init__(self):
        super(BattleLoading, self).__init__(backAlpha=1.0)
        self.__logArenaUniID = False

    @storage_getter('users')
    def usersStorage(self):
        return None

    def _populate(self):
        super(BattleLoading, self)._populate()
        self.__addArenaTypeData()
        g_battleContext.addArenaCtrl(self)

    def onLoadComplete(self):
        Waiting.close()
        return True

    def _dispose(self):
        Waiting.close()
        g_battleContext.removeArenaCtrl(self)
        super(BattleLoading, self)._dispose()

    def invalidateArenaInfo(self):
        arenaDP = g_battleContext.arenaDP
        self.__addArenaExtraData(arenaDP)
        self.__addPlayerData(arenaDP)
        self.invalidateVehiclesInfo(arenaDP)

    def invalidateVehiclesInfo(self, arenaDP):
        regionGetter = g_battleContext.getRegionCode
        isSpeaking = self.app.voiceChatManager.isPlayerSpeaking
        userGetter = self.usersStorage.getUser
        actionGetter = VehicleActions.getBitMask
        playerTeam = arenaDP.getNumberOfTeam()
        for isEnemy in (False, True):
            result = []
            for vInfoVO, _ in arenaDP.getTeamIterator(isEnemy):
                result.append(self.__makeItem(vInfoVO, userGetter, isSpeaking, actionGetter, regionGetter, playerTeam))

            self.as_setVehiclesDataS(isEnemy, result)

    def addVehicleInfo(self, vo, arenaDP):
        playerTeam = arenaDP.getNumberOfTeam()
        item = self.__makeItem(vo, self.usersStorage.getUser, self.app.voiceChatManager.isPlayerSpeaking, VehicleActions.getBitMask, g_battleContext.getRegionCode, playerTeam)
        isEnemy = vo.team != playerTeam
        self.as_addVehicleInfoS(isEnemy, item, arenaDP.getVehiclesIDs(isEnemy))

    def invalidateVehicleInfo(self, flags, vo, arenaDP):
        playerTeam = arenaDP.getNumberOfTeam()
        isEnemy = vo.team != playerTeam
        if flags & INVALIDATE_OP.SORTING > 0:
            vehiclesIDs = arenaDP.getVehiclesIDs(isEnemy)
        else:
            vehiclesIDs = None
        item = self.__makeItem(vo, self.usersStorage.getUser, self.app.voiceChatManager.isPlayerSpeaking, VehicleActions.getBitMask, g_battleContext.getRegionCode, playerTeam)
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

    def invalidateChatRosters(self):
        self.invalidateVehiclesInfo(g_battleContext.arenaDP)

    def updateSpaceLoadProgress(self, progress):
        self.as_setProgressS(progress)

    def arenaLoadCompleted(self):
        if not BattleReplay.isPlaying():
            self.destroy()

    def __makeItem(self, vInfoVO, userGetter, isSpeaking, actionGetter, regionGetter, playerTeam):
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
         'playerName': player.getPlayerLabel(),
         'igrType': player.igrType,
         'clanAbbrev': player.clanAbbrev,
         'region': regionGetter(dbID)}

    def __addArenaTypeData(self):
        arena = getClientArena()
        if arena:
            arenaType = arena.arenaType
            self.as_setMapNameS(arenaType.name)
            self.as_setMapBGS(BattleLoading.MAP_BG_SOURCE % arenaType.geometryName)
        self.as_setTipS(tips.getTip())
        if isEventBattle():
            self.as_setTipTitleS(i18n.makeString('#menu:loading/helpTip/football'))

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
            self.as_setWinTextS(getBattleSubTypeWinText(arenaTypeID, 1 if hasBase else 2))
            if descExtra:
                self.as_setBattleTypeNameS(descExtra)
                self.as_setBattleTypeFrameNumS(arena.guiType + 1)
            elif arena.guiType in [constants.ARENA_GUI_TYPE.RANDOM, constants.ARENA_GUI_TYPE.TRAINING]:
                self.as_setBattleTypeNameS('#arenas:type/%s/name' % arenaSubType)
                astStr = arenaSubType
                if arenaSubType == 'assault':
                    astStr = '{0}{1}'.format(arenaSubType, '1' if hasBase else '2')
                self.as_setBattleTypeFrameNameS(astStr)
                if arena.guiType == constants.ARENA_GUI_TYPE.TRAINING and self.__logArenaUniID == False:
                    self.__logArenaUniID = True
                    from time import strftime, localtime
                    from debug_utils import LOG_NOTE
                    LOG_NOTE('arenaUniqueID: %d | timestamp: %s' % (arena.arenaUniqueID, strftime('%d.%m.%Y %H:%M:%S', localtime())))
            elif arena.guiType == constants.ARENA_GUI_TYPE.EVENT_BATTLES:
                self.as_setBattleTypeNameS('#menu:loading/battleTypes/%d' % arena.guiType)
                self.as_setBattleTypeFrameNameS('neutral')
            else:
                self.as_setBattleTypeNameS('#menu:loading/battleTypes/%d' % arena.guiType)
                if arena.guiType in constants.ARENA_GUI_TYPE_LABEL.LABELS:
                    self.as_setBattleTypeFrameNameS(constants.ARENA_GUI_TYPE_LABEL.LABELS[arena.guiType])
                else:
                    self.as_setBattleTypeFrameNumS(arena.guiType + 1)

    def __addPlayerData(self, arenaDP):
        vInfoVO = arenaDP.getVehicleInfo()
        self.as_setPlayerDataS(vInfoVO.vehicleID, vInfoVO.getSquadID())
