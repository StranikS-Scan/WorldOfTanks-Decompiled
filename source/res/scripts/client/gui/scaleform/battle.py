# Embedded file name: scripts/client/gui/Scaleform/Battle.py
from functools import partial
import weakref
import math
import BigWorld
import GUI
import Math
import VOIP
import SoundGroups
import Vehicle
import constants
import BattleReplay
import CommandMapping
from ConnectionManager import connectionManager
from account_helpers.settings_core.SettingsCore import g_settingsCore
from gui.Scaleform.daapi.view.battle.RadialMenu import RadialMenu
from gui.Scaleform.daapi.view.battle.PlayersPanel import PlayersPanel
from gui.Scaleform.daapi.view.battle.ConsumablesPanel import ConsumablesPanel
from gui.Scaleform.daapi.view.lobby.ReportBug import makeHyperLink, reportBugOpenConfirm
from gui.Scaleform.locale.INGAME_GUI import INGAME_GUI
from gui.Scaleform.locale.MENU import MENU
import gui
from gui.battle_control import g_sessionProvider, vehicle_getter
from gui.battle_control.battle_arena_ctrl import BattleArenaController
from gui.battle_control.arena_info.arena_vos import VehicleActions
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE, PLAYER_ENTITY_NAME
from gui.prb_control.formatters import getPrebattleFullDescription
from messenger import MessengerEntry, g_settings
import nations
from Math import Vector3
from windows import BattleWindow
from SettingsInterface import SettingsInterface
from debug_utils import LOG_CURRENT_EXCEPTION, LOG_DEBUG, LOG_ERROR
from helpers import i18n, html, isPlayerAvatar
from helpers.i18n import makeString
from PlayerEvents import g_playerEvents
from MemoryCriticalController import g_critMemHandler
from items import vehicles
from items.vehicles import VEHICLE_CLASS_TAGS
from gui import DEPTH_OF_Battle, DEPTH_OF_VehicleMarker, TANKMEN_ROLES_ORDER_DICT, GUI_SETTINGS, g_tankActiveCamouflage, g_guiResetters, g_repeatKeyHandlers, game_control
from gui.LobbyContext import g_lobbyContext
from gui.Scaleform import VoiceChatInterface, ColorSchemeManager, getNecessaryArenaFrameName
from gui.Scaleform.SoundManager import SoundManager
from gui.shared.utils import toUpper
from gui.shared.utils.sound import Sound
from gui.shared.utils.functions import getBattleSubTypeBaseNumder, isControlPointExists, makeTooltip
from gui.Scaleform.Flash import Flash
from gui.Scaleform.windows import UIInterface
from gui.Scaleform.MovingText import MovingText
from gui.Scaleform.Minimap import Minimap
from gui.Scaleform.CursorDelegator import g_cursorDelegator
from gui.Scaleform.ingame_help import IngameHelp
from gui.shared.gui_items.Vehicle import VEHICLE_BATTLE_TYPES_ORDER_INDICES
from gui.Scaleform import SCALEFORM_SWF_PATH
from gui.shared.utils.graphics import getScaleByIndex
from account_helpers.settings_core import settings_constants
_CONTOUR_ICONS_MASK = '../maps/icons/vehicle/contour/%(unicName)s.png'
_BASE_CAPTURE_SOUND_NAME_ENEMY = '/GUI/notifications_FX/base_capture_2'
_BASE_CAPTURE_SOUND_NAME_ALLY = '/GUI/notifications_FX/base_capture_1'
_BATTLE_START_NOTIFICATION_TIME = 5.0
_I18N_WAITING_PLAYER = makeString('#ingame_gui:timer/waiting')
_I18N_ARENA_STARTING = makeString('#ingame_gui:timer/starting')
_I18N_ARENA_STARTED = makeString('#ingame_gui:timer/started')

class Battle(BattleWindow):
    teamBasesPanel = property(lambda self: self.__teamBasesPanel)
    consumablesPanel = property(lambda self: self.__consumablesPanel)
    damagePanel = property(lambda self: self.__damagePanel)
    vMarkersManager = property(lambda self: self.__vMarkersManager)
    vErrorsPanel = property(lambda self: self.__vErrorsPanel)
    vMsgsPanel = property(lambda self: self.__vMsgsPanel)
    pMsgsPanel = property(lambda self: self.__pMsgsPanel)
    minimap = property(lambda self: self.__minimap)
    radialMenu = property(lambda self: self.__radialMenu)
    damageInfoPanel = property(lambda self: self.__damageInfoPanel)
    fragCorrelation = property(lambda self: self.__fragCorrelation)
    leftPlayersPanel = property(lambda self: self.__leftPlayersPanel)
    rightPlayersPanel = property(lambda self: self.__rightPlayersPanel)
    VEHICLE_DESTROY_TIMER = {'ALL': 'all',
     constants.VEHICLE_MISC_STATUS.VEHICLE_DROWN_WARNING: 'drown',
     constants.VEHICLE_MISC_STATUS.VEHICLE_IS_OVERTURNED: 'overturn',
     constants.VEHICLE_MISC_STATUS.IN_DEATH_ZONE: 'death_zone'}
    DENUNCIATIONS = {'bot': constants.DENUNCIATION.BOT,
     'flood': constants.DENUNCIATION.FLOOD,
     'offend': constants.DENUNCIATION.OFFEND,
     'notFairPlay': constants.DENUNCIATION.NOT_FAIR_PLAY,
     'forbiddenNick': constants.DENUNCIATION.FORBIDDEN_NICK,
     'swindle': constants.DENUNCIATION.SWINDLE,
     'blackmail': constants.DENUNCIATION.BLACKMAIL}
    __cameraVehicleID = -1

    def __init__(self):
        self.__soundManager = None
        self.__timerCallBackId = None
        self.__arena = BigWorld.player().arena
        self.__playersPanelStateChanged = False
        self.__battleNotificationExecuted = False
        BattleWindow.__init__(self, 'battle.swf')
        self.__timerSound = Sound(self.__arena.arenaType.battleCountdownTimerSound)
        self.__isTimerVisible = False
        self.__isHelpWindowShown = False
        self.__inBattlePlayingTime = 0
        self.component.wg_inputKeyMode = 1
        self.component.position.z = DEPTH_OF_Battle
        self.movie.backgroundAlpha = 0
        self.addFsCallbacks({'battle.leave': self.onExitBattle})
        self.addExternalCallbacks({'battle.showCursor': self.cursorVisibility,
         'battle.tryLeaveRequest': self.tryLeaveRequest,
         'battle.populateFragCorrelationBar': self.populateFragCorrelationBar,
         'Battle.UsersRoster.Appeal': self.onDenunciationReceived,
         'Battle.playersPanelStateChange': self.onPlayersPanelStateChange,
         'Battle.selectPlayer': self.selectPlayer,
         'battle.helpDialogOpenStatus': self.helpDialogOpenStatus,
         'battle.initLobbyDialog': self._initLobbyDialog,
         'battle.reportBug': self.reportBug})
        BigWorld.wg_setRedefineKeysMode(False)
        self.onPostmortemVehicleChanged(BigWorld.player().playerVehicleID)
        return

    def getCameraVehicleID(self):
        return self.__cameraVehicleID

    def populateFragCorrelationBar(self, cid):
        if self.__fragCorrelation is not None:
            self.__fragCorrelation.populate()
        return

    def showAll(self, isShow):
        self.call('battle.showAll', [isShow])
        self.__vMarkersManager.active(isShow)

    def showCursor(self, isShow):
        self.cursorVisibility(-1, isShow)

    def onPlayersPanelStateChange(self, cid, state):
        g_settingsCore.applySetting('ppState', state)
        self.__playersPanelStateChanged = True

    @property
    def soundManager(self):
        return self.__soundManager

    def selectPlayer(self, cid, vehId):
        player = BigWorld.player()
        if isPlayerAvatar():
            player.selectPlayer(int(vehId))

    def onDenunciationReceived(self, cid, uid, userName, topic):
        topicID = self.DENUNCIATIONS.get(topic)
        if topicID is not None:
            self.__makeDenunciation(uid, userName, topicID)
        return

    def __makeDenunciation(self, uid, userName, topicID):
        player = BigWorld.player()
        violatorKind = constants.VIOLATOR_KIND.UNKNOWN
        for id, p in player.arena.vehicles.iteritems():
            if p['accountDBID'] == uid:
                violatorKind = constants.VIOLATOR_KIND.ALLY if player.team == p['team'] else constants.VIOLATOR_KIND.ENEMY

        player.makeDenunciation(uid, topicID, violatorKind)
        self.__arenaCtrl.invalidateGUI()
        topicStr = makeString('#menu:denunciation/%d' % topicID)
        message = makeString('#system_messages:denunciation/success') % {'name': userName,
         'topic': topicStr}
        MessengerEntry.g_instance.gui.addClientMessage(g_settings.htmlTemplates.format('battleErrorMessage', ctx={'error': message}))

    def onPostmortemVehicleChanged(self, id):
        if self.__cameraVehicleID == id:
            return
        else:
            self.__cameraVehicleID = id
            self.__setPlayerInfo(id)
            self.__arenaCtrl.invalidateGUI(not g_sessionProvider.getCtx().isPlayerObserver())
            self.__damagePanel.switchToVehicle(id)
            self.hideVehicleTimer('ALL')
            self.vErrorsPanel.clear()
            self.vMsgsPanel.clear()
            aim = BigWorld.player().inputHandler.aim
            if aim is not None:
                aim.updateAmmoState(True)
            return

    def onCameraChanged(self, cameraMode, curVehID = None):
        LOG_DEBUG('onCameraChanged', cameraMode, curVehID)
        self.damagePanel.showAll(cameraMode != 'video')

        def setVisible(cname):
            m = self.getMember(cname)
            if m is not None:
                m.visible = cameraMode != 'video'
            return

        setVisible('vehicleMessagesPanel')
        setVisible('vehicleErrorsPanel')
        if cameraMode == 'video':
            self.__cameraVehicleID = -1
            self.damagePanel._reset()
            self.vErrorsPanel.clear()
            self.vMsgsPanel.clear()
            self.hideVehicleTimer('ALL')
            aim = BigWorld.player().inputHandler.aim
            if aim is not None:
                aim.updateAmmoState(True)
        aim = BigWorld.player().inputHandler.aim
        if aim is not None:
            aim.onCameraChange()
        return

    def showVehicleTimer(self, code, time, warnLvl = 'critical'):
        LOG_DEBUG('show vehicles destroy timer', code, time, warnLvl)
        self.call('destroyTimer.show', [self.VEHICLE_DESTROY_TIMER[code], time, warnLvl])

    def hideVehicleTimer(self, code):
        LOG_DEBUG('hide vehicles destroy timer', code)
        self.call('destroyTimer.hide', [self.VEHICLE_DESTROY_TIMER[code]])

    def setVehicleTimerPosition(self, code, time, warnLvl, position):
        self.call('destroyTimer.setTimerPosition', [self.VEHICLE_DESTROY_TIMER[code],
         time,
         warnLvl,
         position])

    def showSixthSenseIndicator(self, isShow):
        self.call('sixthSenseIndicator.show', [isShow])

    def setVisible(self, bool):
        LOG_DEBUG('[Battle] visible', bool)
        self.component.visible = bool

    def afterCreate(self):
        player = BigWorld.player()
        voice = VoiceChatInterface.g_instance
        LOG_DEBUG('[Battle] afterCreate')
        setattr(self.movie, '_global.wg_isShowLanguageBar', GUI_SETTINGS.isShowLanguageBar)
        setattr(self.movie, '_global.wg_isShowServerStats', constants.IS_SHOW_SERVER_STATS)
        setattr(self.movie, '_global.wg_isShowVoiceChat', GUI_SETTINGS.voiceChat)
        setattr(self.movie, '_global.wg_voiceChatProvider', voice.voiceChatProvider)
        setattr(self.movie, '_global.wg_isChina', constants.IS_CHINA)
        setattr(self.movie, '_global.wg_isKorea', constants.IS_KOREA)
        setattr(self.movie, '_global.wg_isReplayPlaying', BattleReplay.g_replayCtrl.isPlaying)
        BattleWindow.afterCreate(self)
        g_playerEvents.onBattleResultsReceived += self.__showFinalStatsResults
        BigWorld.wg_setScreenshotNotifyCallback(self.__screenshotNotifyCallback)
        player.inputHandler.onPostmortemVehicleChanged += self.onPostmortemVehicleChanged
        player.inputHandler.onCameraChanged += self.onCameraChanged
        g_settingsCore.onSettingsChanged += self.__accs_onSettingsChanged
        if self.__arena:
            self.__arena.onPeriodChange += self.__onSetArenaTime
            self.__arena.onCombatEquipmentUsed += self.__onCombatEquipmentUsed
        g_sessionProvider.getEquipmentsCtrl().onEquipmentUpdated += self.__onCombatEquipmentUpdated
        self.proxy = weakref.proxy(self)
        voice.populateUI(self.proxy)
        voice.onPlayerSpeaking += self.setPlayerSpeaking
        voice.onVoiceChatInitFailed += self.onVoiceChatInitFailed
        self.colorManager = ColorSchemeManager._ColorSchemeManager()
        self.colorManager.populateUI(self.proxy)
        self.movingText = MovingText()
        self.movingText.populateUI(self.proxy)
        self.__settingsInterface = SettingsInterface()
        self.__settingsInterface.populateUI(self.proxy)
        self.__soundManager = SoundManager()
        self.__soundManager.populateUI(self.proxy)
        self.__teamBasesPanel = TeamBasesPanel(self.proxy)
        self.__fragCorrelation = FragCorrelationPanel(self.proxy)
        self.__debugPanel = DebugPanel(self.proxy)
        self.__consumablesPanel = ConsumablesPanel(self.proxy)
        self.__damagePanel = DamagePanel(self.proxy)
        self.__vMarkersManager = VehicleMarkersManager(self.proxy)
        self.__ingameHelp = IngameHelp(self.proxy)
        self.__minimap = Minimap(self.proxy)
        self.__radialMenu = RadialMenu(self.proxy)
        isColorBlind = g_settingsCore.getSetting('isColorBlind')
        self.__leftPlayersPanel = PlayersPanel(self.proxy, True, isColorBlind=isColorBlind)
        self.__rightPlayersPanel = PlayersPanel(self.proxy, False, isColorBlind=isColorBlind)
        self.isVehicleCountersVisible = g_settingsCore.getSetting('showVehiclesCounter')
        self.__fragCorrelation.showVehiclesCounter(self.isVehicleCountersVisible)
        self.__damageInfoPanel = VehicleDamageInfoPanel(self.proxy)
        self.__vErrorsPanel = FadingMessagesPanel(self.proxy, 'VehicleErrorsPanel', 'gui/vehicle_errors_panel.xml', isColorBlind=isColorBlind)
        self.__vMsgsPanel = FadingMessagesPanel(self.proxy, 'VehicleMessagesPanel', 'gui/vehicle_messages_panel.xml', isColorBlind=isColorBlind)
        self.__pMsgsPanel = FadingMessagesPanel(self.proxy, 'PlayerMessagesPanel', 'gui/player_messages_panel.xml', isColorBlind=isColorBlind)
        self.__teamBasesPanel.start()
        self.__debugPanel.start()
        self.__consumablesPanel.start()
        self.__damagePanel.start()
        self.__ingameHelp.start()
        self.__vErrorsPanel.start()
        self.__vMsgsPanel.start()
        self.__pMsgsPanel.start()
        self.__vMarkersManager.start()
        self.__vMarkersManager.setMarkerDuration(GUI_SETTINGS.markerHitSplashDuration)
        markers = {'enemy': g_settingsCore.getSetting('enemy'),
         'dead': g_settingsCore.getSetting('dead'),
         'ally': g_settingsCore.getSetting('ally')}
        self.__vMarkersManager.setMarkerSettings(markers)
        self.__initMemoryCriticalHandlers()
        MessengerEntry.g_instance.gui.invoke('populateUI', self.proxy)
        g_guiResetters.add(self.__onRecreateDevice)
        g_repeatKeyHandlers.add(self.component.handleKeyEvent)
        self.__onRecreateDevice()
        self.__setPlayerInfo(player.playerVehicleID)
        self.__leftPlayersPanel.populateUI(self.proxy)
        self.__rightPlayersPanel.populateUI(self.proxy)
        self.__populateData()
        self.__minimap.start()
        self.__radialMenu.setSettings(self.__settingsInterface)
        self.__radialMenu.populateUI(self.proxy)
        g_sessionProvider.setBattleUI(self)
        self.__arenaCtrl = BattleArenaController(self)
        g_sessionProvider.addArenaCtrl(self.__arenaCtrl)
        BigWorld.callback(1, self.__setArenaTime)
        self.updateFlagsColor()
        self.movie.setFocussed(SCALEFORM_SWF_PATH)
        if self.__arena.period == constants.ARENA_PERIOD.BATTLE:
            self.call('players_panel.setState', [g_settingsCore.getSetting('ppState')])
        else:
            self.call('players_panel.setState', ['large'])
        self.call('sixthSenseIndicator.setDuration', [GUI_SETTINGS.sixthSenseDuration])
        g_tankActiveCamouflage[player.vehicleTypeDescriptor.type.compactDescr] = self.__arena.arenaType.vehicleCamouflageKind
        if BattleReplay.g_replayCtrl.isPlaying:
            BattleReplay.g_replayCtrl.onBattleSwfLoaded()
        player.battleMessages.onShowPlayerMessage += self.onShowPlayerMessage
        player.battleMessages.onShowVehicleMessage += self.onShowVehicleMessage
        keyCode = CommandMapping.g_instance.get('CMD_VOICECHAT_MUTE')
        if not BigWorld.isKeyDown(keyCode):
            VOIP.getVOIPManager().setMicMute(True)

    def beforeDelete(self):
        LOG_DEBUG('[Battle] beforeDelete')
        if not BattleReplay.g_replayCtrl.isPlaying:
            from gui import game_control
            game_control.g_instance.notifier.updateBattleFpsInfo(BigWorld.getBattleFPS()[2], self.__inBattlePlayingTime)
        if self.colorManager:
            self.colorManager.dispossessUI()
        voice = VoiceChatInterface.g_instance
        if voice:
            voice.dispossessUI(self.proxy)
            voice.onPlayerSpeaking -= self.setPlayerSpeaking
            voice.onVoiceChatInitFailed -= self.onVoiceChatInitFailed
        self.__destroyMemoryCriticalHandlers()
        if self.movingText is not None:
            self.movingText.dispossessUI()
            self.movingText = None
        if self.__soundManager is not None:
            self.__soundManager.dispossessUI()
            self.__soundManager = None
        if self.colorManager is not None:
            self.colorManager.dispossessUI()
            self.colorManager = None
        if self.component:
            g_repeatKeyHandlers.discard(self.component.handleKeyEvent)
        g_settingsCore.onSettingsChanged -= self.__accs_onSettingsChanged
        self.__teamBasesPanel.destroy()
        self.__debugPanel.destroy()
        self.__consumablesPanel.destroy()
        self.__damagePanel.destroy()
        self.__vMarkersManager.destroy()
        self.__ingameHelp.destroy()
        self.__vErrorsPanel.destroy()
        self.__vMsgsPanel.destroy()
        self.__pMsgsPanel.destroy()
        self.__radialMenu.destroy()
        self.__minimap.destroy()
        self.__timerSound.stop()
        g_sessionProvider.clearBattleUI()
        if self.__arenaCtrl is not None:
            g_sessionProvider.removeArenaCtrl(self.__arenaCtrl)
            self.__arenaCtrl.destroy()
            self.__arenaCtrl = None
        self.__leftPlayersPanel.dispossessUI()
        self.__rightPlayersPanel.dispossessUI()
        MessengerEntry.g_instance.gui.invoke('dispossessUI')
        g_playerEvents.onBattleResultsReceived -= self.__showFinalStatsResults
        g_sessionProvider.getEquipmentsCtrl().onEquipmentUpdated -= self.__onCombatEquipmentUpdated
        if self.__arena:
            self.__arena.onPeriodChange -= self.__onSetArenaTime
            self.__arena.onCombatEquipmentUsed -= self.__onCombatEquipmentUsed
        self.__arena = None
        g_guiResetters.discard(self.__onRecreateDevice)
        self.__settingsInterface.dispossessUI()
        self.__settingsInterface = None
        VoiceChatInterface.g_instance.onVoiceChatInitFailed -= self.onVoiceChatInitFailed
        BattleWindow.beforeDelete(self)
        return

    def __screenshotNotifyCallback(self, path):
        self.vMsgsPanel.showMessage('SCREENSHOT_CREATED', {'path': i18n.encodeUtf8(path)})

    def onVoiceChatInitFailed(self):
        if GUI_SETTINGS.voiceChat:
            self.call('VoiceChat.initFailed', [])

    def onShowPlayerMessage(self, code, postfix, targetID, attackerID):
        LOG_DEBUG('onShowPlayerMessage', code, postfix, targetID, attackerID)
        getFullName = g_sessionProvider.getCtx().getFullPlayerName
        self.pMsgsPanel.showMessage(code, {'target': getFullName(targetID, showClan=False),
         'attacker': getFullName(attackerID, showClan=False)}, extra=(('target', targetID), ('attacker', attackerID)), postfix=postfix)

    def onShowVehicleMessage(self, code, postfix, entityID, extra):
        LOG_DEBUG('onShowVehicleMessage', code, postfix, entityID, extra)
        names = {'device': '',
         'entity': '',
         'target': ''}
        if extra is not None:
            names['device'] = extra.deviceUserString
        if entityID:
            names['entity'] = g_sessionProvider.getCtx().getFullPlayerName(entityID)
        self.vMsgsPanel.showMessage(code, names, postfix=postfix)
        return

    def clearCommands(self):
        pass

    def bindCommands(self):
        self.__consumablesPanel.bindCommands()
        self.__ingameHelp.buildCmdMapping()

    def updateFlagsColor(self):
        isColorBlind = g_settingsCore.getSetting('isColorBlind')
        colorGreen = self.colorManager.getSubScheme('flag_team_green', isColorBlind=isColorBlind)['rgba']
        colorRed = self.colorManager.getSubScheme('flag_team_red', isColorBlind=isColorBlind)['rgba']
        if 1 == BigWorld.player().team:
            BigWorld.wg_setFlagColor(1, colorGreen / 255)
            BigWorld.wg_setFlagColor(2, colorRed / 255)
        else:
            BigWorld.wg_setFlagColor(2, colorGreen / 255)
            BigWorld.wg_setFlagColor(1, colorRed / 255)
        BigWorld.wg_setFlagEmblem(0, 'system/maps/wg_emblem.dds', Math.Vector4(0.0, 0.1, 0.5, 0.9))
        BigWorld.wg_setFlagEmblem(1, 'system/maps/wg_emblem.dds', Math.Vector4(0.0, 0.1, 0.5, 0.9))
        BigWorld.wg_setFlagEmblem(2, 'system/maps/wg_emblem.dds', Math.Vector4(0.0, 0.1, 0.5, 0.9))

    def setPlayerSpeaking(self, accountDBID, flag):
        self.__callEx('setPlayerSpeaking', [accountDBID, flag])
        vID = g_sessionProvider.getCtx().getVehIDByAccDBID(accountDBID)
        if vID > 0:
            self.__vMarkersManager.showDynamic(vID, flag)

    def isPlayerSpeaking(self, accountDBID):
        return VoiceChatInterface.g_instance.isPlayerSpeaking(accountDBID)

    def showPostmortemTips(self):
        if self.radialMenu is not None:
            self.radialMenu.forcedHide()
        if not g_sessionProvider.getCtx().isPlayerObserver():
            self.__callEx('showPostmortemTips', [1.0, 5.0, 1.0])
        return

    def cursorVisibility(self, callbackId, visible, x = None, y = None, customCall = False, enableAiming = True):
        if visible:
            g_cursorDelegator.syncMousePosition(self, x, y, customCall)
        else:
            g_cursorDelegator.restoreMousePosition()
        if BigWorld.player() is not None and isPlayerAvatar():
            BigWorld.player().setForcedGuiControlMode(visible, False, enableAiming)
        return

    def tryLeaveRequest(self, _):
        resStr = 'quitBattle'
        replayCtrl = BattleReplay.g_replayCtrl
        player = BigWorld.player()
        isVehicleAlive = getattr(player, 'isVehicleAlive', False)
        isNotTraining = self.__arena.guiType != constants.ARENA_GUI_TYPE.TRAINING
        if not replayCtrl.isPlaying:
            if constants.IS_KOREA and gui.GUI_SETTINGS.igrEnabled and self.__arena is not None and isNotTraining:
                vehicleID = getattr(player, 'playerVehicleID', -1)
                if vehicleID in self.__arena.vehicles:
                    vehicle = self.__arena.vehicles[vehicleID]
                    if isVehicleAlive and vehicle.get('igrType') != constants.IGR_TYPE.NONE:
                        resStr = 'quitBattleIGR'
                else:
                    LOG_ERROR("Player's vehicle not found", vehicleID)
            isDeserter = isVehicleAlive and isNotTraining
            if isDeserter:
                resStr += '/deserter'
        else:
            isDeserter = False
        self.__callEx('tryLeaveResponse', [resStr, isDeserter])
        return

    def onExitBattle(self, arg):
        arena = getattr(BigWorld.player(), 'arena', None)
        LOG_DEBUG('onExitBattle', arena)
        if arena:
            BigWorld.player().leaveArena()
        return

    def toggleHelpWindow(self):
        self.__callEx('showHideHelp', [not self.__isHelpWindowShown])

    def setAimingMode(self, isAiming):
        self.__callEx('setAimingMode', [isAiming])

    def helpDialogOpenStatus(self, cid, isOpened):
        self.__isHelpWindowShown = isOpened

    def _initLobbyDialog(self, cid):
        if connectionManager.serverUserName:
            tooltipBody = i18n.makeString('#tooltips:header/info/players_online_full/body')
            tooltipFullData = makeTooltip('#tooltips:header/info/players_online_full/header', tooltipBody % {'servername': connectionManager.serverUserName})
            self.__callEx('setServerStatsInfo', [tooltipFullData])
            self.__callEx('setServerName', [connectionManager.serverUserName])
            if constants.IS_SHOW_SERVER_STATS:
                stats = game_control.g_instance.serverStats.getStats()
                if 'clusterCCU' in stats and 'regionCCU' in stats:
                    self.__callEx('setServerStats', [stats['clusterCCU'], stats['regionCCU']])
                else:
                    self.__callEx('setServerStats', [None, None])
        else:
            self.__callEx('setServerName', ['\xe2\x80\x93'])
        links = GUI_SETTINGS.reportBugLinks
        if len(links):
            reportBugButton = makeHyperLink('ingameMenu', MENU.INGAME_MENU_LINKS_REPORT_BUG)
            self.__callEx('setReportBugLink', [reportBugButton])
        return

    def reportBug(self, _):
        from gui.battle_control import g_sessionProvider
        adp = g_sessionProvider.getArenaDP()
        accountId = adp.getVehicleInfo().player.accountDBID
        reportBugOpenConfirm(accountId)

    def __setPlayerInfo(self, vID):
        playerName, pName, clanAbbrev, regionCode, vTypeName = g_sessionProvider.getCtx().getFullPlayerNameWithParts(vID=vID, showVehShortName=False)
        self.__callEx('setPlayerInfo', [playerName,
         pName,
         clanAbbrev,
         regionCode,
         vTypeName])

    def __populateData(self):
        from gui.shared.utils.functions import getBattleSubTypeWinText, getArenaSubTypeName, isBaseExists
        arena = getattr(BigWorld.player(), 'arena', None)
        arenaData = ['',
         0,
         '',
         '',
         '']
        if arena:
            arenaData = [toUpper(arena.arenaType.name)]
            descExtra = getPrebattleFullDescription(arena.extraData or {})
            arenaSubType = getArenaSubTypeName(BigWorld.player().arenaTypeID)
            if descExtra:
                arenaData.extend([arena.guiType + 1, descExtra])
            elif arena.guiType in [constants.ARENA_GUI_TYPE.RANDOM, constants.ARENA_GUI_TYPE.TRAINING]:
                arenaTypeName = '#arenas:type/%s/name' % arenaSubType
                arenaData.extend([getNecessaryArenaFrameName(arenaSubType, isBaseExists(BigWorld.player().arenaTypeID, BigWorld.player().team)), arenaTypeName])
            elif arena.guiType == constants.ARENA_GUI_TYPE.EVENT_BATTLES:
                arenaData.extend(['neutral', '#menu:loading/battleTypes/%d' % arena.guiType])
            elif arena.guiType in constants.ARENA_GUI_TYPE.RANGE:
                arenaData.extend([constants.ARENA_GUI_TYPE_LABEL.LABELS[arena.guiType], '#menu:loading/battleTypes/%d' % arena.guiType])
            else:
                arenaData.extend([arena.guiType + 1, '#menu:loading/battleTypes/%d' % arena.guiType])
            extraData = arena.extraData or {}
            myTeam = BigWorld.player().team
            team1 = extraData.get('opponents', {}).get('%s' % myTeam, {}).get('name', '#menu:loading/team1')
            team2 = extraData.get('opponents', {}).get('2' if myTeam == 1 else '1', {}).get('name', '#menu:loading/team2')
            arenaData.extend([team1, team2])
            teamHasBase = 1 if isBaseExists(BigWorld.player().arenaTypeID, myTeam) else 2
            winText = getBattleSubTypeWinText(BigWorld.player().arenaTypeID, teamHasBase)
            arenaData.append(winText)
            arenaData.append('normal')
            arenaDP = g_sessionProvider.getArenaDP()
            vehInfo = arenaDP.getVehicleInfo(arenaDP.getPlayerVehicleID())
            pqTipData = [None] * 3
            if not BattleReplay.g_replayCtrl.isPlaying:
                pQuests = vehInfo.player.getPotapovQuests()
                isPQEnabled = g_lobbyContext.getServerSettings().isPotapovQuestEnabled()
                if isPQEnabled and (arena.guiType == constants.ARENA_GUI_TYPE.RANDOM or arena.guiType == constants.ARENA_GUI_TYPE.TRAINING and constants.IS_DEVELOPMENT):
                    if len(pQuests):
                        quest = pQuests[0]
                        pqTipData = [quest.getUserName(), quest.getUserMainCondition(), quest.getUserAddCondition()]
                    else:
                        pqTipData = [i18n.makeString('#ingame_gui:potapovQuests/tip'), None, None]
                arenaData.extend(pqTipData)
        self.__callEx('arenaData', arenaData)
        return

    def __showFinalStatsResults(self, isActiveVehicle, results):
        if isActiveVehicle:
            if self.__arena:
                if GUI_SETTINGS.battleStatsInHangar:
                    g_sessionProvider.getCtx().lastArenaUniqueID = self.__arena.arenaUniqueID
            self.onExitBattle(None)
        return

    def __showFinalStats(self, winnerTeam, reason):
        if hasattr(BigWorld.player(), 'team'):
            status = 'tie' if winnerTeam == 0 else ('win' if winnerTeam == BigWorld.player().team else 'lose')
            status = makeString('#menu:finalStatistic/commonStats/resultlabel/%s' % status)
            self.__callEx('showStatus', [status])

    def __hideTimer(self):
        self.__callEx('showBattleTimer', [False])

    def __onSetArenaTime(self, *args):
        if self.__timerCallBackId is not None:
            BigWorld.cancelCallback(self.__timerCallBackId)
        self.__setArenaTime()
        return

    def __onCombatEquipmentUsed(self, eqID):
        equipment = vehicles.g_cache.equipments().get(eqID)
        if equipment is not None:
            postfix = equipment.name.split('_')[0].upper()
            self.pMsgsPanel.showMessage('COMBAT_EQUIPMENT_USED', {}, postfix=postfix)
        return

    def __onCombatEquipmentUpdated(self, intCD, item, isOrder, isDeployed):
        if isDeployed:
            postfix = item.getDescriptor().name.split('_')[0].upper()
            self.pMsgsPanel.showMessage('COMBAT_EQUIPMENT_READY', {}, postfix=postfix)

    def __setArenaTime(self):
        self.__timerCallBackId = None
        if self.__arena is None:
            return
        else:
            skipGUIMessages = False
            mute_timer_sound = False
            replayCtrl = BattleReplay.g_replayCtrl
            if replayCtrl.isPlaying:
                period = replayCtrl.getArenaPeriod()
                arenaLengthExact = replayCtrl.getArenaLength()
                arenaLength = int(arenaLengthExact)
                mute_timer_sound = replayCtrl.playbackSpeed == 0
                if period == constants.ARENA_PERIOD.IDLE:
                    self.__timerCallBackId = BigWorld.callback(1, self.__setArenaTime)
                    return
                skipGUIMessages = replayCtrl.isTimeWarpInProgress
            else:
                period = self.__arena.period
                arenaLengthExact = self.__arena.periodEndTime - BigWorld.serverTime()
                arenaLength = int(arenaLengthExact)
                if period == constants.ARENA_PERIOD.PREBATTLE:
                    if arenaLength <= _BATTLE_START_NOTIFICATION_TIME and not self.__battleNotificationExecuted:
                        BigWorld.WGWindowsNotifier.onBattleBeginning()
                        self.__battleNotificationExecuted = True
                else:
                    self.__battleNotificationExecuted = False
                if replayCtrl.isRecording:
                    replayCtrl.setArenaPeriod(period, arenaLengthExact)
                if period == constants.ARENA_PERIOD.BATTLE:
                    self.__inBattlePlayingTime = self.__arena.periodLength - arenaLengthExact
            arenaLength = arenaLength if arenaLength > 0 else 0
            if period != constants.ARENA_PERIOD.AFTERBATTLE:
                if replayCtrl.isPlaying:
                    if replayCtrl.isFinished() == False:
                        self.__callEx('timerBar.setTotalTime', [arenaLength])
                else:
                    self.__callEx('timerBar.setTotalTime', [arenaLength])
            if not skipGUIMessages:
                if period == constants.ARENA_PERIOD.WAITING:
                    self.__callEx('timerBig.setTimer', [_I18N_WAITING_PLAYER])
                    self.__isTimerVisible = True
                elif period == constants.ARENA_PERIOD.PREBATTLE:
                    self.__callEx('timerBig.setTimer', [_I18N_ARENA_STARTING, arenaLength])
                    self.__isTimerVisible = True
                    if self.__timerSound.isPlaying == False and arenaLengthExact >= 0.0 and mute_timer_sound == False:
                        self.__timerSound.play()
                    if self.__timerSound.isPlaying and (arenaLengthExact < 0.0 or mute_timer_sound == True):
                        self.__timerSound.stop()
                elif period == constants.ARENA_PERIOD.BATTLE and self.__isTimerVisible:
                    self.__isTimerVisible = False
                    self.__timerSound.stop()
                    self.__callEx('timerBig.setTimer', [_I18N_ARENA_STARTED])
                    self.__callEx('timerBig.hide')
                    if not self.__playersPanelStateChanged:
                        userState = g_settingsCore.getSetting('ppState')
                        self.call('players_panel.setState', ['none'])
                        self.call('players_panel.setState', [userState])
                elif period == constants.ARENA_PERIOD.AFTERBATTLE:
                    self.__hideTimer()
            elif period == constants.ARENA_PERIOD.BATTLE and not self.__playersPanelStateChanged:
                userState = g_settingsCore.getSetting('ppState')
                self.call('players_panel.setState', ['none'])
                self.call('players_panel.setState', [userState])
            if replayCtrl.isPlaying:
                self.__timerCallBackId = BigWorld.callback(0.0, self.__setArenaTime)
            elif arenaLengthExact > 1:
                self.__timerCallBackId = BigWorld.callback(1.0, self.__setArenaTime)
            else:
                self.__timerCallBackId = BigWorld.callback(0.0, self.__setArenaTime)
            return

    def __onRecreateDevice(self):
        params = list(GUI.screenResolution())
        index = g_settingsCore.getSetting(settings_constants.GRAPHICS.INTERFACE_SCALE)
        params.append(getScaleByIndex(index))
        self.call('Stage.Update', params)
        self.__vMarkersManager.updateMarkersScale()

    def __callEx(self, funcName, args = None):
        self.call('battle.' + funcName, args)

    def __initMemoryCriticalHandlers(self):
        for message in g_critMemHandler.messages:
            self.__onMemoryCritical(message)

        g_critMemHandler.onMemCrit += self.__onMemoryCritical

    def __destroyMemoryCriticalHandlers(self):
        g_critMemHandler.onMemCrit -= self.__onMemoryCritical

    def __onMemoryCritical(self, message):
        self.__vMsgsPanel.showMessage(message[1])

    def __accs_onSettingsChanged(self, diff):
        self.colorManager.update()
        if 'isColorBlind' in diff:
            isColorBlind = diff['isColorBlind']
            self.__vErrorsPanel.defineColorFlags(isColorBlind=isColorBlind)
            self.__vMsgsPanel.defineColorFlags(isColorBlind=isColorBlind)
            self.__pMsgsPanel.defineColorFlags(isColorBlind=isColorBlind)
            self.__leftPlayersPanel.defineColorFlags(isColorBlind=isColorBlind)
            self.__rightPlayersPanel.defineColorFlags(isColorBlind=isColorBlind)
            self.updateFlagsColor()
            self.__vMarkersManager.updateMarkers()
            self.__minimap.updateEntries()
        if 'enemy' in diff or 'dead' in diff or 'ally' in diff:
            markers = {'enemy': g_settingsCore.getSetting('enemy'),
             'dead': g_settingsCore.getSetting('dead'),
             'ally': g_settingsCore.getSetting('ally')}
            self.vMarkersManager.setMarkerSettings(markers)
            self.__vMarkersManager.updateMarkerSettings()
        if 'showVehiclesCounter' in diff:
            self.isVehicleCountersVisible = diff['showVehiclesCounter']
            self.__fragCorrelation.showVehiclesCounter(self.isVehicleCountersVisible)
        if 'interfaceScale' in diff:
            self.__onRecreateDevice()
        self.__arenaCtrl.invalidateGUI()
        self.__arenaCtrl.invalidateArenaInfo()


class TeamBasesPanel(object):
    __settings = {0: {'weight': 2,
         'color': 'red',
         'capturing': i18n.makeString('#ingame_gui:player_messages/ally_base_captured_by_notification'),
         'captured': i18n.makeString('#ingame_gui:player_messages/ally_base_captured_notification')},
     3: {'weight': 1,
         'color': 'green',
         'capturing': i18n.makeString('#ingame_gui:player_messages/enemy_base_captured_by_notification'),
         'captured': i18n.makeString('#ingame_gui:player_messages/enemy_base_captured_notification')},
     'controlPoint': {'weight': {0: 4,
                                 3: 3},
                      'color': {0: 'red',
                                3: 'green'},
                      'capturing': i18n.makeString('#ingame_gui:player_messages/base_captured_by_notification'),
                      'captured': i18n.makeString('#ingame_gui:player_messages/base_captured_notification')}}

    def __init__(self, parentUI):
        self.__ui = parentUI
        self.__captureSounds = {}
        self.__baseIds = set()
        self.__capturePoints = {}
        self.__updatePointsWorkers = {}

    def start(self):
        LOG_DEBUG('TeamBasesPanel.start')
        arena = BigWorld.player().arena
        arena.onTeamBasePointsUpdate += self.__onTeamBasePointsUpdate
        arena.onTeamBaseCaptured += self.__onTeamBaseCaptured
        arena.onPeriodChange += self.__onPeriodChange

    def destroy(self):
        LOG_DEBUG('TeamBasesPanel.destroy')
        self.__clearUpdateCallbacks()
        arena = getattr(BigWorld.player(), 'arena', None)
        if arena is not None:
            arena.onTeamBasePointsUpdate -= self.__onTeamBasePointsUpdate
            arena.onTeamBaseCaptured -= self.__onTeamBaseCaptured
            arena.onPeriodChange -= self.__onPeriodChange
        self.__stopCaptureSound()
        return

    def _getID(self, team, baseID):
        if baseID is None:
            baseID = 0
        return (int(baseID) << 2) + team

    def _hasBaseId(self, team, exclude = -1):
        return len(filter(lambda i: i & team != 0 and i != exclude, self.__baseIds)) > 0

    def __onTeamBasePointsUpdate(self, team, baseID, points, capturingStopped):
        if team not in (1, 2):
            return
        else:
            id = self._getID(team, baseID)
            if not points:
                if id in self.__baseIds:
                    self.__clearUpdateCallback(id)
                    self.__baseIds.remove(id)
                    self.__callFlash('remove', [id])
                    if not self._hasBaseId(team) or team ^ BigWorld.player().team:
                        self.__stopCaptureSound(team)
            else:
                if id in self.__baseIds:
                    self.__capturePoints[id] = points
                    if capturingStopped:
                        self.__callFlash('stop', [id, points])
                else:
                    self.__baseIds.add(id)
                    key = team ^ BigWorld.player().team
                    if isControlPointExists(BigWorld.player().arenaTypeID):
                        settings = self.__settings.get('controlPoint', {})
                        color = settings.get('color', {}).get(key, 'green')
                        weight = settings.get('weight', {}).get(key, 0)
                    else:
                        settings = self.__settings.get(key, {})
                        color = settings.get('color', 'green')
                        weight = settings.get('weight', 0)
                    capturingString = settings.get('capturing', '') % getBattleSubTypeBaseNumder(BigWorld.player().arenaTypeID, team, baseID)
                    rate = 1
                    replayCtrl = BattleReplay.g_replayCtrl
                    if replayCtrl.isPlaying and replayCtrl.playbackSpeed is not None:
                        rate = replayCtrl.playbackSpeed
                    self.__callFlash('add', [id,
                     weight,
                     color,
                     capturingString,
                     points,
                     rate])
                    if capturingStopped:
                        self.__callFlash('stop', [id, points])
                    self.__capturePoints[id] = points
                    self.__loadUpdateCallback(id)
                if not capturingStopped:
                    self.__playCaptureSound(team)
                elif not self._hasBaseId(team, exclude=id) or team ^ BigWorld.player().team:
                    self.__stopCaptureSound(team)
            return

    def __onTeamBaseCaptured(self, team, baseID):
        if team not in (1, 2):
            return
        id = self._getID(team, baseID)
        if isControlPointExists(BigWorld.player().arenaTypeID):
            settings = self.__settings.get('controlPoint', {})
            color = settings.get('color', {}).get(team ^ BigWorld.player().team, 'green')
        else:
            settings = self.__settings.get(team ^ BigWorld.player().team, {})
            color = settings.get('color', 'green')
        if id in self.__baseIds:
            self.__callFlash('setCaptured', [id, settings.get('captured', '') % getBattleSubTypeBaseNumder(BigWorld.player().arenaTypeID, team, baseID)])
        else:
            self.__baseIds.add(id)
            self.__callFlash('add', [id,
             color,
             settings.get('weight', 0),
             settings.get('captured', '') % getBattleSubTypeBaseNumder(BigWorld.player().arenaTypeID, team, baseID),
             100])
        self.__stopCaptureSound(team)

    def __onPeriodChange(self, period, *args):
        if period != constants.ARENA_PERIOD.AFTERBATTLE:
            return
        self.__callFlash('clear', [])
        self.__stopCaptureSound()

    def __callFlash(self, funcName, args):
        self.__ui.call('battle.teamBasesPanel.{0:>s}'.format(funcName), args)

    def __playCaptureSound(self, team):
        arena = getattr(BigWorld.player(), 'arena', None)
        if arena is not None and arena.period == constants.ARENA_PERIOD.AFTERBATTLE:
            return
        else:
            snd = self.__captureSounds.get(team)
            if snd is None:
                try:
                    isAllyTeam = True if team == BigWorld.player().team else False
                    snd = SoundGroups.g_instance.FMODplaySound(_BASE_CAPTURE_SOUND_NAME_ALLY if isAllyTeam else _BASE_CAPTURE_SOUND_NAME_ENEMY)
                    self.__captureSounds[team] = snd
                except Exception:
                    LOG_CURRENT_EXCEPTION()

            return

    def __stopCaptureSound(self, team = None):
        if team is None:
            for t in self.__captureSounds.keys():
                self.__stopCaptureSound(t)

        else:
            snd = self.__captureSounds.get(team)
            if snd is not None:
                try:
                    snd.stop()
                except Exception:
                    LOG_CURRENT_EXCEPTION()

                del self.__captureSounds[team]
        return

    def __updatePoints(self, baseId):
        if baseId in self.__baseIds:
            rate = 1
            replayCtrl = BattleReplay.g_replayCtrl
            if replayCtrl.isPlaying and replayCtrl.playbackSpeed is not None:
                rate = replayCtrl.playbackSpeed
            points = self.__capturePoints[baseId]
            LOG_DEBUG('Update points called for base with points', baseId, points, rate)
            self.__callFlash('updatePoints', [baseId, points, rate])
            self.__loadUpdateCallback(baseId)
        return

    def __loadUpdateCallback(self, baseId):
        self.__clearUpdateCallback(baseId)
        self.__updatePointsWorkers[baseId] = BigWorld.callback(1, lambda : self.__updatePoints(baseId))

    def __clearUpdateCallback(self, baseId):
        invalidateCbID = self.__updatePointsWorkers.get(baseId)
        if invalidateCbID is not None:
            BigWorld.cancelCallback(invalidateCbID)
            del self.__updatePointsWorkers[baseId]
        return

    def __clearUpdateCallbacks(self):
        for baseId, cbId in self.__updatePointsWorkers.items():
            BigWorld.cancelCallback(cbId)

        self.__updatePointsWorkers = {}


class VehicleDamageInfoPanel(object):

    def __init__(self, parent):
        self.parent = parent
        self.isShown = False

    def show(self, vehicleID, damagedExtras = [], destroyedExtras = []):
        if vehicleID not in BigWorld.player().arena.vehicles or not BigWorld.player().arena.vehicles[vehicleID].has_key('vehicleType'):
            return
        extras = BigWorld.player().arena.vehicles[vehicleID]['vehicleType'].extras
        isFire = False
        itemsList = []
        for i, id in enumerate(damagedExtras):
            if extras[id].name == 'fire':
                isFire = True
                continue
            itemsList.append({'name': extras[id].name,
             'userName': extras[id].deviceUserString,
             'state': 'damaged'})

        for i, id in enumerate(destroyedExtras):
            itemsList.append({'name': extras[id].name,
             'userName': extras[id].deviceUserString,
             'state': 'destroyed'})

        self.parent.movie.showDamageInfoPanel(vehicleID, itemsList, isFire)
        self.isShown = True

    def hide(self):
        if not self.isShown:
            return
        self.parent.movie.hideDamageInfoPanel()
        self.isShown = False


class FragCorrelationPanel(object):

    def __init__(self, parentUI):
        self.__ui = parentUI
        self.__teamsFrags = [0, 0]
        self.__fragsCache = [0, 0]
        self.clear()

    def populate(self):
        getNumberOfTeam = g_sessionProvider.getArenaDP().getNumberOfTeam
        getTeamName = g_sessionProvider.getCtx().getTeamName
        playerTeamIdx = getNumberOfTeam()
        _alliedTeamName = getTeamName(playerTeamIdx, True)
        _enemyTeamName = getTeamName(playerTeamIdx, False)
        self.__callFlash('setTeamNames', [_alliedTeamName, _enemyTeamName])
        self.showVehiclesCounter(g_settingsCore.getSetting('showVehiclesCounter'))
        self.updateFrags(playerTeamIdx)
        self.updateTeam(False, playerTeamIdx)
        self.updateTeam(True, getNumberOfTeam(True))

    def clear(self, team = None):
        if team is None:
            self.__teamsFrags = [0, 0]
            self.__teamsShortLists = {1: [],
             2: []}
        else:
            self.__teamsShortLists[team] = []
            oppositeTeamsIndexes = (1, 0)
            self.__teamsFrags[oppositeTeamsIndexes[team - 1]] = 0
        return

    def addFrags(self, team, count = 1):
        self.__teamsFrags[team - 1] += count

    def addKilled(self, team, count = 1):
        oppositeTeamsIndexes = (2, 1)
        self.addFrags(oppositeTeamsIndexes[team - 1], count=count)

    def addVehicle(self, team, vehicleID, vClassName, isAlive):
        self.__teamsShortLists[team].append([vehicleID, vClassName, isAlive])

    def updateFrags(self, playerTeam):
        if not playerTeam:
            return
        teamIndex = playerTeam - 1
        enemyIndex = 1 - teamIndex
        if len(self.__teamsFrags):
            self.__callFlash('updateFrags', [self.__teamsFrags[teamIndex], self.__teamsFrags[enemyIndex]])

    def updateTeam(self, isEnemy, team):
        if not team:
            return
        sortedList = sorted(self.__teamsShortLists[team], cmp=_markerComparator)
        team = [ pos for item in sortedList for pos in item ]
        if isEnemy:
            self.__callFlash('updateEnemyTeam', team)
        else:
            self.__callFlash('updatePlayerTeam', team)

    def showVehiclesCounter(self, isShown):
        self.__callFlash('showVehiclesCounter', [isShown])

    def __callFlash(self, funcName, args):
        self.__ui.call('battle.fragCorrelationBar.' + funcName, args)


class DebugPanel(UIInterface):
    __UPDATE_INTERVAL = 0.01

    def __init__(self, parentUI):
        UIInterface.__init__(self)
        self.__ui = parentUI
        self.__timeInterval = None
        self.__performanceStats = _PerformanceStats()
        self.__performanceStats.populateUI(parentUI)
        return

    def start(self):
        self.__timeInterval = _TimeInterval(self.__UPDATE_INTERVAL, '_DebugPanel__update', weakref.proxy(self))
        self.__timeInterval.start()
        self.__update()

    def destroy(self):
        self.__performanceStats.disposeUI()
        self.__performanceStats = None
        self.__timeInterval.stop()
        return

    def __update(self):
        player = BigWorld.player()
        if player is None or not hasattr(player, 'playerVehicleID'):
            return
        else:
            fps = 0
            recordedFps = -1
            ping = 0
            isLaggingNow = False
            replayCtrl = BattleReplay.g_replayCtrl
            if replayCtrl.isPlaying and replayCtrl.fps > 0:
                fps = BigWorld.getFPS()[1]
                recordedFps = replayCtrl.fps
                ping = replayCtrl.ping
                isLaggingNow = replayCtrl.isLaggingNow
            else:
                isLaggingNow = player.filter.isLaggingNow
                if not isLaggingNow:
                    for v in BigWorld.entities.values():
                        if isinstance(v, Vehicle.Vehicle):
                            if not v.isPlayer:
                                if v.isAlive() and isinstance(v.filter, BigWorld.WGVehicleFilter) and v.filter.isLaggingNow:
                                    isLaggingNow = True
                                    break

                ping = min(BigWorld.LatencyInfo().value[3] * 1000, 999)
                if ping < 999:
                    ping = max(1, ping - 500.0 * constants.SERVER_TICK_LENGTH)
                fpsInfo = BigWorld.getFPS()
                from helpers.statistics import g_statistics
                g_statistics.update(fpsInfo, ping, isLaggingNow)
                fps = fpsInfo[1]
                if replayCtrl.isRecording:
                    replayCtrl.setFpsPingLag(fps, ping, isLaggingNow)
            try:
                self.__performanceStats.updateDebugInfo(int(fps), int(ping), isLaggingNow, int(recordedFps))
            except:
                pass

            return


class _PerformanceStats(UIInterface):

    def __init__(self):
        UIInterface.__init__(self)
        self.flashObject = None
        return

    def populateUI(self, proxy):
        UIInterface.populateUI(self, proxy)
        self.flashObject = self.uiHolder.getMember('_level0.debugPanel')
        self.flashObject.script = self

    def updateDebugInfo(self, fps, ping, lag, fpsReplay):
        if fpsReplay != 0 and fpsReplay != -1:
            fps = '{0}({1})'.format(fpsReplay, fps)
        else:
            fps = str(fps)
        ping = str(ping)
        self.flashObject.as_updateDebugInfo(fps, ping, lag)

    def disposeUI(self):
        self.flashObject.script = None
        self.flashObject = None
        return


class DamagePanel():
    _WAITING_INTERVAL = 0.05
    _UPDATING_INTERVAL = 0.03
    __stateHandlers = {VEHICLE_VIEW_STATE.HEALTH: '_updateHealth',
     VEHICLE_VIEW_STATE.DEVICES: '_updateDeviceState',
     VEHICLE_VIEW_STATE.DESTROYED: '_setVehicleDestroyed',
     VEHICLE_VIEW_STATE.CREW_DEACTIVATED: '_setCrewDeactivated',
     VEHICLE_VIEW_STATE.FIRE: '_setFireInVehicle',
     VEHICLE_VIEW_STATE.AUTO_ROTATION: '_setAutoRotation'}

    def __init__(self, parentUI):
        self.__ui = parentUI
        self.__hasYawLimits = False
        self.__vID = 0
        self.__speed = 0.0
        self.__health = 0
        self.__isRqToSwitch = False
        self.__waitingTI = _TimeInterval(self._WAITING_INTERVAL, '_waiting', weakref.proxy(self))
        self.__updateTI = _TimeInterval(self._UPDATING_INTERVAL, '_updateSelf', weakref.proxy(self))
        self.__tankIndicator = _TankIndicatorCtrl(self.__ui)
        self.__ui.addExternalCallbacks({'battle.damagePanel.onClickToDeviceIcon': self.__onClickToDeviceIcon,
         'battle.damagePanel.onClickToTankmenIcon': self.__onClickToTankmenIcon,
         'battle.damagePanel.onClickToFireIcon': self.__onClickToFireIcon})

    def start(self):
        g_sessionProvider.onVehicleStateUpdated += self.__onVehicleStateUpdated
        self.__tankIndicator.start()
        self.__vID = BigWorld.player().playerVehicleID
        self.__waitingTI.start()

    def destroy(self):
        g_sessionProvider.onVehicleStateUpdated -= self.__onVehicleStateUpdated
        self.__waitingTI.stop()
        self.__waitingTI = None
        self.__updateTI.stop()
        self.__updateTI = None
        self.__tankIndicator.destroy()
        self.__tankIndicator = None
        self.__hasYawLimits = False
        self.__ui = None
        return

    def updateModuleRepair(self, module, percents, seconds):
        self.__callFlash('updateModuleRepair', [module, percents, seconds])

    def setModuleRepairPosition(self, entityName, position):
        self.__callFlash('setModuleRepairPosition', [entityName, position])

    def updateSpeed(self, speed):
        if self.__speed is not speed:
            self.__speed = speed
            self.__callFlash('updateSpeed', [speed])

    def setCruiseMode(self, mode):
        if BattleReplay.g_replayCtrl.isRecording:
            BattleReplay.g_replayCtrl.onSetCruiseMode(mode)
        self.__callFlash('setCruiseMode', [mode])

    def switchToVehicle(self, vID):
        if self.__vID is vID or vID is None:
            return
        else:
            self._reset()
            self.__waitingTI.stop()
            self.__updateTI.stop()
            self.__vID = vID
            self.__isRqToSwitch = True
            self.__waitingTI.start()
            return

    def _reset(self):
        self.__vID = 0
        self.__speed = 0.0
        self.__health = 0
        self.__hasYawLimits = False
        self.__isRqToSwitch = False
        self.__callFlash('reset')

    def _waiting(self):
        vehicle = BigWorld.entity(self.__vID)
        if vehicle is not None:
            self.__waitingTI.stop()
            self._setup(vehicle)
        return

    def _setup(self, vehicle):
        vTypeDesc = vehicle.typeDescriptor
        vType = vTypeDesc.type
        if self.__isRqToSwitch:
            nationID = vType.id[0]
            BigWorld.player().soundNotifications.clear()
            SoundGroups.g_instance.soundModes.setCurrentNation(nations.NAMES[nationID])
        self.__tankIndicator._setup(vehicle)
        self.__hasYawLimits = vehicle_getter.hasYawLimits(vTypeDesc)
        modulesLayout = vehicle_getter.hasTurretRotator(vTypeDesc)
        crewLayout = [ elem[0] for elem in vType.crewRoles ]
        order = TANKMEN_ROLES_ORDER_DICT['plain']
        lastIdx = len(order)

        def comparator(item, other):
            itemIdx = order.index(item) if item in order else lastIdx
            otherIdx = order.index(other) if other in order else lastIdx
            return cmp(itemIdx, otherIdx)

        crewLayout = sorted(crewLayout, cmp=comparator)
        self.__callFlash('setIconsLayout', crewLayout + [modulesLayout])
        self.__callFlash('setMaxHealth', [vTypeDesc.maxHealth])
        self.__callFlash('updateHealth', [vehicle.health])
        if vehicle.isPlayer and self.__hasYawLimits:
            aih = BigWorld.player().inputHandler
            auto = False
            if aih is not None:
                auto = aih.getAutorotation()
            self._setAutoRotation(auto)
        if not vehicle.isAlive():
            self._setVehicleDestroyed()
            return
        else:
            self.__updateTI = None
            self.__updateTI = _TimeInterval(0.03, '_updateSelf' if vehicle.isPlayer else '_updateOther', weakref.proxy(self))
            self.__updateTI.start()
            return

    def _updateSelf(self):
        player = BigWorld.player()
        if player is None:
            return
        else:
            vehicle = BigWorld.entity(self.__vID)
            if vehicle is not None and vehicle.isStarted:
                speed, _ = player.getOwnVehicleSpeeds()
                self.updateSpeed(int(speed * 3.6))
            return

    def _updateOther(self):
        vehicle = BigWorld.entity(self.__vID)
        if vehicle is not None:
            self._updateHealth(vehicle.health)
            if vehicle.isStarted:
                try:
                    speed = vehicle.filter.speedInfo.value[0]
                    fwdSpeedLimit, bckwdSpeedLimit = vehicle.typeDescriptor.physics['speedLimits']
                    speed = max(min(speed, fwdSpeedLimit), -bckwdSpeedLimit)
                    self.updateSpeed(int(speed * 3.6))
                except (AttributeError, IndexError, ValueError):
                    LOG_CURRENT_EXCEPTION()
                    LOG_ERROR('Can not update speed. Stop')
                    self.__updateTI.stop()

            if not vehicle.isAlive():
                self._setVehicleDestroyed()
                self.__updateTI.stop()
        return

    def showAll(self, isShow):
        self.__callFlash('showAll', [isShow])

    def _updateHealth(self, health):
        if self.__health is not health:
            self.__health = health
            self.__callFlash('updateHealth', [health])

    def _updateDeviceState(self, value):
        deviceName, deviceState, _ = value
        self.__callFlash('updateState', [deviceName, deviceState])

    def _setVehicleDestroyed(self):
        self.__updateTI.stop()
        self.__callFlash('onVehicleDestroyed')
        self.__callFlash('onCrewDeactivated')

    def _setCrewDeactivated(self):
        self.__callFlash('onCrewDeactivated')

    def _setFireInVehicle(self, bool):
        self.__callFlash('onFireInVehicle', [bool])

    def _setAutoRotation(self, value):
        if self.__hasYawLimits:
            self.__callFlash('onVehicleAutorotationEnabled', [value])

    def __onVehicleStateUpdated(self, state, value):
        if state not in self.__stateHandlers:
            return
        else:
            handler = getattr(self, self.__stateHandlers[state], None)
            if handler and callable(handler):
                if value is not None:
                    handler(value)
                else:
                    handler()
            return

    def __changeVehicleSetting(self, tag, entityName):
        result, error = g_sessionProvider.getEquipmentsCtrl().changeSettingByTag(tag, entityName=entityName, avatar=BigWorld.player())
        if not result and error:
            self.__ui.vErrorsPanel.showMessage(error.key, error.ctx)

    def __onClickToTankmenIcon(self, _, entityName, entityState):
        self.__changeVehicleSetting('medkit', entityName)

    def __onClickToDeviceIcon(self, _, entityName, entityState):
        self.__changeVehicleSetting('repairkit', entityName)

    def __onClickToFireIcon(self, _):
        self.__changeVehicleSetting('extinguisher', None)
        return

    def __callFlash(self, funcName, args = None):
        self.__ui.call('battle.damagePanel.' + funcName, args)


class _TankIndicatorCtrl():

    def __init__(self, parentUI):
        self.__ui = parentUI

    def __del__(self):
        LOG_DEBUG('_TankIndicatorCtrl deleted')

    def start(self):
        self._define()

    def destroy(self):
        setattr(self.__ui.component, 'tankIndicator', None)
        self.__ui = None
        return

    def _define(self):
        mc = GUI.WGTankIndicatorFlash(self.__ui.movie, '_root.damagePanel.componentsContainer.tankIndicator')
        mc.wg_inputKeyMode = 2
        self.__ui.component.addChild(mc, 'tankIndicator')

    def _setup(self, vehicle):
        vTypeDesc = vehicle.typeDescriptor
        yawLimits = vehicle_getter.getYawLimits(vTypeDesc)
        hasYawLimits = yawLimits is not None
        self.__flashCall('setType', [vehicle_getter.getVehicleIndicatorType(vTypeDesc)])
        if hasYawLimits:
            args = [math.degrees(-yawLimits[0]), math.degrees(yawLimits[1]), True]
        else:
            args = [0, 0, False]
        self.__flashCall('setGunConstraints', args)
        if vehicle.isPlayer:
            hullMat = BigWorld.player().getOwnVehicleMatrix()
        else:
            hullMat = vehicle.matrix
        turretMat = vehicle.appearance.turretMatrix
        tankIndicator = self.__ui.component.tankIndicator
        tankIndicator.wg_turretYawConstraints = yawLimits if hasYawLimits else Math.Vector2(0.0, 0.0)
        tankIndicator.wg_hullMatProv = hullMat
        tankIndicator.wg_turretMatProv = turretMat
        return

    def __flashCall(self, funcName, args = None):
        if self.__ui:
            self.__ui.call('battle.tankIndicator.{0:>s}'.format(funcName), args)


class VehicleMarkersManager(Flash):
    __SWF_FILE_NAME = 'VehicleMarkersManager.swf'

    class DAMAGE_TYPE:
        FROM_UNKNOWN = 0
        FROM_ALLY = 1
        FROM_ENEMY = 2
        FROM_SQUAD = 3
        FROM_PLAYER = 4

    def __init__(self, parentUI):
        Flash.__init__(self, self.__SWF_FILE_NAME)
        self.component.wg_inputKeyMode = 2
        self.component.position.z = DEPTH_OF_VehicleMarker
        self.component.drawWithRestrictedViewPort = False
        self.movie.backgroundAlpha = 0
        self.colorManager = ColorSchemeManager._ColorSchemeManager()
        self.colorManager.populateUI(weakref.proxy(self))
        self.__ownUI = None
        self.__parentUI = parentUI
        self.__markers = dict()
        self.__equipmentsMarkers = {}
        return

    def showExtendedInfo(self, value):
        self.__invokeCanvas('setShowExInfoFlag', [value])
        for handle in self.__markers.iterkeys():
            self.invokeMarker(handle, 'showExInfo', [value])

    def setScaleProps(self, minScale = 40, maxScale = 100, defScale = 100, speed = 3.0):
        if constants.IS_DEVELOPMENT:
            self.__ownUI.scaleProperties = (minScale,
             maxScale,
             defScale,
             speed)

    def setAlphaProps(self, minAlpha = 40, maxAlpha = 100, defAlpha = 100, speed = 3.0):
        if constants.IS_DEVELOPMENT:
            self.__ownUI.alphaProperties = (minAlpha,
             maxAlpha,
             defAlpha,
             speed)

    def start(self):
        self.active(True)
        self.__ownUI = GUI.WGVehicleMarkersCanvasFlash(self.movie)
        self.__ownUI.wg_inputKeyMode = 2
        self.__ownUI.scaleProperties = GUI_SETTINGS.markerScaleSettings
        self.__ownUI.alphaProperties = GUI_SETTINGS.markerBgSettings
        self.__ownUIProxy = weakref.proxy(self.__ownUI)
        self.__ownUIProxy.markerSetScale(getScaleByIndex(g_settingsCore.getSetting('interfaceScale')))
        self.__parentUI.component.addChild(self.__ownUI, 'vehicleMarkersManager')
        self.__markersCanvasUI = self.getMember('vehicleMarkersCanvas')
        g_sessionProvider.getEquipmentsCtrl().onEquipmentMarkerShown += self.__onEquipmentMarkerShown

    def destroy(self):
        g_sessionProvider.getEquipmentsCtrl().onEquipmentMarkerShown -= self.__onEquipmentMarkerShown
        if self.__parentUI is not None:
            setattr(self.__parentUI.component, 'vehicleMarkersManager', None)
        for equipmentsMarker in self.__equipmentsMarkers.items():
            self.__ownUI.delMarker(equipmentsMarker[0])
            BigWorld.cancelCallback(equipmentsMarker[1])

        self.__equipmentsMarkers = None
        self.__parentUI = None
        self.__ownUI = None
        self.__markersCanvasUI = None
        self.colorManager.dispossessUI()
        self.close()
        return

    def createMarker(self, vProxy):
        vInfo = dict(vProxy.publicInfo)
        battleCtx = g_sessionProvider.getCtx()
        if battleCtx.isObserver(vProxy.id):
            return -1
        isFriend = vInfo['team'] == BigWorld.player().team
        vInfoEx = g_sessionProvider.getArenaDP().getVehicleInfo(vProxy.id)
        vTypeDescr = vProxy.typeDescriptor
        maxHealth = vTypeDescr.maxHealth
        mProv = vProxy.model.node('HP_gui')
        tags = set(vTypeDescr.type.tags & VEHICLE_CLASS_TAGS)
        vClass = tags.pop() if len(tags) > 0 else ''
        entityName = battleCtx.getPlayerEntityName(vProxy.id, vInfoEx.team)
        entityType = 'ally' if BigWorld.player().team == vInfoEx.team else 'enemy'
        speaking = False
        if GUI_SETTINGS.voiceChat:
            speaking = VoiceChatInterface.g_instance.isPlayerSpeaking(vInfoEx.player.accountDBID)
        hunting = VehicleActions.isHunting(vInfoEx.events)
        handle = self.__ownUI.addMarker(mProv, 'VehicleMarkerAlly' if isFriend else 'VehicleMarkerEnemy')
        self.__markers[handle] = _VehicleMarker(vProxy, self.__ownUIProxy, handle)
        fullName, pName, clanAbbrev, regionCode, vehShortName = battleCtx.getFullPlayerNameWithParts(vProxy.id)
        self.invokeMarker(handle, 'init', [vClass,
         vInfoEx.vehicleType.iconPath,
         vehShortName,
         vInfoEx.vehicleType.level,
         fullName,
         pName,
         clanAbbrev,
         regionCode,
         vProxy.health,
         maxHealth,
         entityName.name(),
         speaking,
         hunting,
         entityType])
        return handle

    def destroyMarker(self, handle):
        if self.__markers.has_key(handle):
            del self.__markers[handle]
            self.__ownUI.delMarker(handle)

    def createStaticMarker(self, pos, symbol):
        mProv = Math.Matrix()
        mProv.translation = pos
        handle = self.__ownUI.addMarker(mProv, symbol)
        return (mProv, handle)

    def destroyStaticMarker(self, handle):
        if self.__ownUI:
            self.__ownUI.delMarker(handle)

    def updateMarkerState(self, handle, newState, isImmediate = False):
        self.invokeMarker(handle, 'updateState', [newState, isImmediate])

    def showActionMarker(self, handle, newState):
        self.invokeMarker(handle, 'showActionMarker', [newState])

    def __getVehicleDamageType(self, attackerID):
        if not attackerID:
            return VehicleMarkersManager.DAMAGE_TYPE.FROM_UNKNOWN
        if attackerID == BigWorld.player().playerVehicleID:
            return VehicleMarkersManager.DAMAGE_TYPE.FROM_PLAYER
        entityName = g_sessionProvider.getCtx().getPlayerEntityName(attackerID, BigWorld.player().arena.vehicles.get(attackerID, dict()).get('team'))
        if entityName == PLAYER_ENTITY_NAME.squadman:
            return VehicleMarkersManager.DAMAGE_TYPE.FROM_SQUAD
        if entityName == PLAYER_ENTITY_NAME.ally:
            return VehicleMarkersManager.DAMAGE_TYPE.FROM_ALLY
        if entityName == PLAYER_ENTITY_NAME.enemy:
            return VehicleMarkersManager.DAMAGE_TYPE.FROM_ENEMY
        return VehicleMarkersManager.DAMAGE_TYPE.FROM_UNKNOWN

    def onVehicleHealthChanged(self, handle, curHealth, attackerID = -1, attackReasonID = 0):
        replayCtrl = BattleReplay.g_replayCtrl
        if replayCtrl.isPlaying and replayCtrl.isTimeWarpInProgress:
            return
        if curHealth < 0 and curHealth not in constants.SPECIAL_VEHICLE_HEALTH.AMMO_BAY_EXPLOSION:
            curHealth = 0
        self.invokeMarker(handle, 'updateHealth', [curHealth, self.__getVehicleDamageType(attackerID), constants.ATTACK_REASONS[attackReasonID]])

    def showDynamic(self, vID, flag):
        handle = getattr(BigWorld.entity(vID), 'marker', None)
        if handle is not None and GUI_SETTINGS.voiceChat:
            self.invokeMarker(handle, 'setSpeaking', [flag])
        return

    def updateMarkersScale(self):
        self.__ownUIProxy.markerSetScale(getScaleByIndex(g_settingsCore.getSetting('interfaceScale')))

    def setTeamKiller(self, vID):
        ctx = g_sessionProvider.getCtx()
        if not ctx.isTeamKiller(vID=vID) or ctx.isSquadMan(vID=vID):
            return
        else:
            handle = getattr(BigWorld.entity(vID), 'marker', None)
            if handle is not None:
                self.invokeMarker(handle, 'setEntityName', [PLAYER_ENTITY_NAME.teamKiller.name()])
            return

    def invokeMarker(self, handle, function, args = None):
        if handle == -1:
            return
        else:
            if args is None:
                args = []
            self.__ownUI.markerInvoke(handle, (function, args))
            return

    def __invokeCanvas(self, function, args = None):
        if args is None:
            args = []
        self.call('battle.vehicleMarkersCanvas.' + function, args)
        return

    def setMarkerSettings(self, settings):
        if self.__markersCanvasUI:
            self.__markersCanvasUI.setMarkerSettings(settings)

    def setMarkerDuration(self, value):
        self.__invokeCanvas('setMarkerDuration', [value])

    def updateMarkers(self):
        self.colorManager.update()
        for handle in self.__markers.iterkeys():
            self.invokeMarker(handle, 'update', [])

    def updateMarkerSettings(self):
        for handle in self.__markers.iterkeys():
            self.invokeMarker(handle, 'updateMarkerSettings', [])

    def __onEquipmentMarkerShown(self, item, pos, dir, time):
        mPov, handle = self.createStaticMarker(pos + Vector3(0, 12, 0), 'FortConsumablesMarker')
        defaultPostfix = i18n.makeString(INGAME_GUI.FORTCONSUMABLES_TIMER_POSTFIX)
        self.invokeMarker(handle, 'init', [item.getMarker(), str(int(time)), defaultPostfix])
        self.__initTimer(int(time), handle)

    def __initTimer(self, timer, handle):
        timer = timer - 1
        if timer < 0:
            self.destroyStaticMarker(handle)
            if handle in self.__equipmentsMarkers:
                del self.__equipmentsMarkers[handle]
            return
        self.invokeMarker(handle, 'updateTimer', [str(timer)])
        callbackId = BigWorld.callback(1, partial(self.__initTimer, timer, handle))
        self.__equipmentsMarkers[handle] = callbackId


class _VehicleMarker():

    def __init__(self, vProxy, uiProxy, handle):
        self.vProxy = vProxy
        self.uiProxy = uiProxy
        self.handle = handle
        self.uiProxy.markerSetScale(getScaleByIndex(g_settingsCore.getSetting('interfaceScale')))
        self.vProxy.appearance.onModelChanged += self.__onModelChanged

    def destroy(self):
        self.vProxy.appearance.onModelChanged -= self.__onModelChanged
        self.vProxy = None
        self.uiProxy = None
        self.handle = -1
        return

    def __onModelChanged(self):
        self.uiProxy.markerSetMatrix(self.handle, self.vProxy.model.node('HP_gui'))


class FadingMessagesPanel(object):
    __settings = []
    __messageDict = {}
    _EXTRA_COLOR_FORMAT = '<font color="#{0:02X}{1:02X}{2:02X}">{3:>s}</font>'

    def __init__(self, parentUI, name, cfgFileName, isColorBlind = False):
        self.__ui = parentUI
        self.__name = name
        self.__pathPrefix = 'battle.' + name + '.' + '%s'
        self.__readConfig(cfgFileName)
        self.__ui.addExternalCallbacks({'battle.%s.PopulateUI' % name: self.__onPopulateUI})
        self.defineColorFlags(isColorBlind=isColorBlind)
        self.__isPopulated = False
        self.__pendingMessages = []

    def start(self):
        self.__callFlash('RefreshUI')

    def destroy(self):
        self.__ui = None
        self.__isPopulated = False
        self.__pendingMessages = []
        return

    def clear(self):
        self.__callFlash('Clear')

    def defineColorFlags(self, isColorBlind = False):
        self.__colorGroup = 'color_blind' if isColorBlind else 'default'

    def showMessage(self, key, args = None, extra = None, postfix = ''):
        replayCtrl = BattleReplay.g_replayCtrl
        if replayCtrl.isPlaying and replayCtrl.isTimeWarpInProgress:
            return
        else:
            extKey = '%s_%s' % (key, postfix)
            if extKey in self.__messageDict:
                key = extKey
            msgText, colors = self.__messageDict.get(key, (None, ''))
            if msgText is None:
                return
            if args is not None:
                self.__formatEntitiesEx(args, extra=extra)
                try:
                    msgText = msgText % args
                except TypeError:
                    LOG_CURRENT_EXCEPTION()

            color = colors.get(self.__colorGroup if self.__colorGroup in colors else 'default')
            if self.__isPopulated:
                self.__showMessage(key, msgText, color)
            else:
                self.__pendingMessages.append([key, msgText, color])
            return

    def __showMessage(self, key, msgText, color):
        LOG_DEBUG('%s: show message with key = %s' % (self.__name, key))
        self.__callFlash('ShowMessage', [key, msgText, color])

    def __formatEntitiesEx(self, args, extra = None):
        if extra is None:
            extra = ()
        csManager = self.__ui.colorManager
        battleCtx = g_sessionProvider.getCtx()
        isTeamKiller = battleCtx.isTeamKiller
        isSquadMan = battleCtx.isSquadMan
        for argName, vID in extra:
            arg = args.get(argName)
            rgba = None
            if isTeamKiller(vID=vID):
                rgba = csManager.getScheme('teamkiller').get(self.__colorGroup, {}).get('rgba')
            elif isSquadMan(vID=vID):
                rgba = csManager.getScheme('squad').get(self.__colorGroup, {}).get('rgba')
            if arg and rgba:
                args[argName] = self._EXTRA_COLOR_FORMAT.format(int(rgba[0]), int(rgba[1]), int(rgba[2]), arg)

        return

    def __readConfig(self, cfgFileName):
        self.__settings = []
        import ResMgr
        sec = ResMgr.openSection(cfgFileName)
        if sec is None:
            raise Exception, "can not open '%s'" % cfgFileName
        self.__settings.append(sec.readInt('maxLinesCount', -1))
        direction = sec.readString('direction')
        if direction not in ('up', 'down'):
            raise Exception, 'Wrong direction value in %s' % cfgFileName
        self.__settings.append(direction)
        self.__settings.append(sec.readFloat('lifeTime'))
        self.__settings.append(sec.readFloat('alphaSpeed'))
        self.__settings.append(sec.readBool('showUniqueOnly', False))
        self.__messageDict = dict()
        for mTag, mSec in sec['messages'].items():
            text = mSec.readString('text')
            text = html.translation(text)
            aliasesSec = mSec['colorAlias']
            aliases = aliasesSec.items()
            if len(aliases):
                groups = dict(((key, section.asString) for key, section in aliases))
            else:
                groups = {'default': aliasesSec.asString}
            self.__messageDict[mTag] = (text, groups)

        return

    def __callFlash(self, funcName, args = None):
        self.__ui.call(self.__pathPrefix % funcName, args)

    def __onPopulateUI(self, requestId):
        args = [requestId]
        args.extend(self.__settings)
        self.__ui.respond(args)
        self.__isPopulated = True
        while len(self.__pendingMessages):
            self.__showMessage(*self.__pendingMessages.pop())


def _markerComparator(x1, x2):
    INDEX_IS_ALIVE = 2
    INDEX_VEHICLE_CLASS = 1
    if x1[INDEX_IS_ALIVE] < x2[INDEX_IS_ALIVE]:
        return 1
    if x1[INDEX_IS_ALIVE] > x2[INDEX_IS_ALIVE]:
        return -1
    x1Index = VEHICLE_BATTLE_TYPES_ORDER_INDICES.get(x1[INDEX_VEHICLE_CLASS], 100)
    x2Index = VEHICLE_BATTLE_TYPES_ORDER_INDICES.get(x2[INDEX_VEHICLE_CLASS], 100)
    if x1Index < x2Index:
        return -1
    if x1Index > x2Index:
        return 1
    return 0


class _TimeInterval():

    def __init__(self, interval, funcName, scopeProxy = None):
        self.__cbId = None
        self.__interval = interval
        self.__funcName = funcName
        self.__scopeProxy = scopeProxy
        return

    def start(self):
        if self.__cbId is not None:
            LOG_ERROR('To start a new time interval You should before stop already the running time interval.')
            return
        else:
            self.__cbId = BigWorld.callback(self.__interval, self.__update)
            return

    def stop(self):
        if self.__cbId is not None:
            BigWorld.cancelCallback(self.__cbId)
            self.__cbId = None
        return

    def __update(self):
        self.__cbId = None
        self.__cbId = BigWorld.callback(self.__interval, self.__update)
        if self.__scopeProxy is not None:
            funcObj = getattr(self.__scopeProxy, self.__funcName, None)
            if funcObj and callable(funcObj):
                funcObj()
        return
