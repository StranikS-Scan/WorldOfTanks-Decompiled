# Embedded file name: scripts/client/gui/Scaleform/Battle.py
import weakref
import BigWorld
from CTFManager import g_ctfManager
import GUI
import Math
import VOIP
import constants
import BattleReplay
import CommandMapping
from ConnectionManager import connectionManager
from account_helpers.settings_core.SettingsCore import g_settingsCore
from gui.Scaleform.daapi.view.battle.resource_points import ResourcePointsPlugin
from gui.Scaleform.daapi.view.battle.respawn_view import RespawnViewPlugin
from gui.Scaleform.daapi.view.battle.PlayersPanelsSwitcher import PlayersPanelsSwitcher
from gui.Scaleform.daapi.view.battle.RadialMenu import RadialMenu
from gui.Scaleform.daapi.view.battle.flag_notification import FlagNotificationPlugin
from gui.Scaleform.daapi.view.battle.players_panel import playersPanelFactory
from gui.Scaleform.daapi.view.battle.score_panel import scorePanelFactory
from gui.Scaleform.daapi.view.battle.ConsumablesPanel import ConsumablesPanel
from gui.Scaleform.daapi.view.battle.BattleRibbonsPanel import BattleRibbonsPanel
from gui.Scaleform.daapi.view.battle.TimersBar import TimersBar
from gui.Scaleform.daapi.view.battle.damage_panel import DamagePanel
from gui.Scaleform.daapi.view.battle.indicators import IndicatorsCollection
from gui.Scaleform.daapi.view.battle.messages import PlayerMessages, VehicleErrorMessages, VehicleMessages
from gui.Scaleform.daapi.view.battle.stats_form import statsFormFactory
from gui.Scaleform.daapi.view.battle.teams_bases_panel import TeamBasesPanel
from gui.Scaleform.daapi.view.battle.markers import MarkersManager
from gui.Scaleform.daapi.view.lobby.ReportBug import makeHyperLink, reportBugOpenConfirm
from gui.Scaleform.locale.MENU import MENU
import gui
from gui.battle_control import g_sessionProvider
from gui.battle_control.DynSquadViewListener import DynSquadViewListener
from gui.battle_control.battle_arena_ctrl import battleArenaControllerFactory
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE
from gui.battle_control.dyn_squad_arena_controllers import DynSquadSoundsController, DynSquadEntityController
from gui.prb_control.formatters import getPrebattleFullDescription
from gui.shared.utils.TimeInterval import TimeInterval
from gui.shared.utils.plugins import PluginsCollection
from messenger import MessengerEntry, g_settings
from windows import BattleWindow
from SettingsInterface import SettingsInterface
from debug_utils import LOG_DEBUG, LOG_ERROR
from helpers import i18n, isPlayerAvatar
from helpers.i18n import makeString
from gui import DEPTH_OF_Battle, GUI_SETTINGS, g_tankActiveCamouflage, g_guiResetters, g_repeatKeyHandlers, game_control
from gui.LobbyContext import g_lobbyContext
from gui.Scaleform import VoiceChatInterface, ColorSchemeManager, getNecessaryArenaFrameName
from gui.Scaleform.SoundManager import SoundManager
from gui.shared.utils import toUpper
from gui.shared.utils.functions import makeTooltip, getArenaSubTypeName, isBaseExists, getBattleSubTypeWinText
from gui.Scaleform.windows import UIInterface
from gui.Scaleform.MovingText import MovingText
from gui.Scaleform.Minimap import Minimap
from gui.Scaleform.CursorDelegator import g_cursorDelegator
from gui.Scaleform.ingame_help import IngameHelp
from gui.Scaleform import SCALEFORM_SWF_PATH
from gui.battle_control.arena_info import isEventBattle, getArenaIcon, hasFlags, hasRespawns, hasResourcePoints
from gui.battle_control import avatar_getter

def _isVehicleEntity(entity):
    import Vehicle
    return isinstance(entity, Vehicle.Vehicle)


_CONTOUR_ICONS_MASK = '../maps/icons/vehicle/contour/%(unicName)s.png'

class Battle(BattleWindow):
    teamBasesPanel = property(lambda self: self.__teamBasesPanel)
    timersBar = property(lambda self: self.__timersBar)
    consumablesPanel = property(lambda self: self.__consumablesPanel)
    damagePanel = property(lambda self: self.__damagePanel)
    markersManager = property(lambda self: self.__markersManager)
    vErrorsPanel = property(lambda self: self.__vErrorsPanel)
    vMsgsPanel = property(lambda self: self.__vMsgsPanel)
    pMsgsPanel = property(lambda self: self.__pMsgsPanel)
    minimap = property(lambda self: self.__minimap)
    radialMenu = property(lambda self: self.__radialMenu)
    damageInfoPanel = property(lambda self: self.__damageInfoPanel)
    fragCorrelation = property(lambda self: self.__fragCorrelation)
    statsForm = property(lambda self: self.__statsForm)
    leftPlayersPanel = property(lambda self: self.__leftPlayersPanel)
    rightPlayersPanel = property(lambda self: self.__rightPlayersPanel)
    ribbonsPanel = property(lambda self: self.__ribbonsPanel)
    ppSwitcher = property(lambda self: self.__ppSwitcher)
    indicators = property(lambda self: self.__indicators)
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
    __stateHandlers = {VEHICLE_VIEW_STATE.FIRE: '_setFireInVehicle'}

    def __init__(self):
        self.__soundManager = None
        self.__arena = BigWorld.player().arena
        self.__plugins = PluginsCollection(self)
        plugins = {}
        if hasFlags():
            plugins['flagNotification'] = FlagNotificationPlugin
        if hasRespawns() and not BattleReplay.g_replayCtrl.isPlaying:
            plugins['respawnView'] = RespawnViewPlugin
        if hasResourcePoints():
            plugins['resources'] = ResourcePointsPlugin
        self.__plugins.addPlugins(plugins)
        BattleWindow.__init__(self, 'battle.swf')
        self.__isHelpWindowShown = False
        self.__cameraMode = None
        self.component.wg_inputKeyMode = 1
        self.component.position.z = DEPTH_OF_Battle
        self.movie.backgroundAlpha = 0
        self.addFsCallbacks({'battle.leave': self.onExitBattle})
        self.addExternalCallbacks({'battle.showCursor': self.cursorVisibility,
         'battle.tryLeaveRequest': self.tryLeaveRequest,
         'battle.populateFragCorrelationBar': self.populateFragCorrelationBar,
         'Battle.UsersRoster.Appeal': self.onDenunciationReceived,
         'Battle.selectPlayer': self.selectPlayer,
         'battle.helpDialogOpenStatus': self.helpDialogOpenStatus,
         'battle.initLobbyDialog': self._initLobbyDialog,
         'battle.reportBug': self.reportBug})
        self.__dynSquadListener = None
        BigWorld.wg_setRedefineKeysMode(False)
        self.onPostmortemVehicleChanged(BigWorld.player().playerVehicleID)
        return

    def getRoot(self):
        return self.__battle_flashObject

    def getCameraVehicleID(self):
        return self.__cameraVehicleID

    def populateFragCorrelationBar(self, _):
        if self.__fragCorrelation is not None:
            self.__fragCorrelation.populate()
        return

    def showAll(self, isShow):
        self.call('battle.showAll', [isShow])
        self.__markersManager.active(isShow)
        g_sessionProvider.getHitDirectionCtrl().setVisible(isShow)

    def showCursor(self, isShow):
        self.cursorVisibility(-1, isShow)

    @property
    def soundManager(self):
        return self.__soundManager

    def selectPlayer(self, cid, vehId):
        player = BigWorld.player()
        if isPlayerAvatar():
            player.selectPlayer(int(vehId))

    def onDenunciationReceived(self, _, uid, userName, topic):
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
            self.__arenaCtrl.invalidateGUI(not g_sessionProvider.getCtx().isPlayerObserver())
            g_sessionProvider.getVehicleStateCtrl().switchToAnother(id)
            self.hideVehicleTimer('ALL')
            self.__vErrorsPanel.clear()
            self.__vMsgsPanel.clear()
            aim = BigWorld.player().inputHandler.aim
            if aim is not None:
                aim.updateAmmoState(True)
            return

    def onCameraChanged(self, cameraMode, curVehID = None):
        LOG_DEBUG('onCameraChanged', cameraMode, curVehID)
        if self.__cameraMode == 'mapcase':
            self.setAimingMode(False)
        elif cameraMode == 'mapcase':
            self.setAimingMode(True)
        self.__cameraMode = cameraMode

        def setVisible(cname):
            m = self.getMember(cname)
            if m is not None:
                m.visible = cameraMode != 'video'
            return

        if self.__isGuiShown():
            self.damagePanel.showAll(cameraMode != 'video')
            setVisible('vehicleMessagesPanel')
            setVisible('vehicleErrorsPanel')
        if cameraMode == 'video':
            self.__cameraVehicleID = -1
            self.__vErrorsPanel.clear()
            self.__vMsgsPanel.clear()
            self.hideVehicleTimer('ALL')
            aim = BigWorld.player().inputHandler.aim
            if aim is not None:
                aim.updateAmmoState(True)
        aim = BigWorld.player().inputHandler.aim
        if aim is not None:
            aim.onCameraChange()
        return

    def __isGuiShown(self):
        m = self.getMember('_root')
        if m is not None and callable(m.isGuiVisible):
            return m.isGuiVisible()
        else:
            return False

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
        player.inputHandler.onPostmortemVehicleChanged += self.onPostmortemVehicleChanged
        player.inputHandler.onCameraChanged += self.onCameraChanged
        g_settingsCore.onSettingsChanged += self.__accs_onSettingsChanged
        g_settingsCore.interfaceScale.onScaleChanged += self.__onRecreateDevice
        isMutlipleTeams = g_sessionProvider.getArenaDP().isMultipleTeams()
        isEvent = isEventBattle()
        self.proxy = weakref.proxy(self)
        self.__battle_flashObject = self.proxy.getMember('_level0')
        if self.__battle_flashObject:
            self.__battle_flashObject.resync()
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
        self.__timersBar = TimersBar(self.proxy, isEvent)
        self.__teamBasesPanel = TeamBasesPanel(self.proxy)
        self.__dynSquadSoundCtrl = DynSquadSoundsController(self.__soundManager)
        self.__teamBasesPanel = TeamBasesPanel(self.proxy)
        self.__debugPanel = DebugPanel(self.proxy)
        self.__consumablesPanel = ConsumablesPanel(self.proxy)
        self.__damagePanel = DamagePanel(self.proxy)
        self.__markersManager = MarkersManager(self.proxy)
        self.__ingameHelp = IngameHelp(self.proxy)
        self.__minimap = Minimap(self.proxy)
        self.__radialMenu = RadialMenu(self.proxy)
        self.__ribbonsPanel = BattleRibbonsPanel(self.proxy)
        self.__indicators = IndicatorsCollection()
        self.__ppSwitcher = PlayersPanelsSwitcher(self.proxy)
        isColorBlind = g_settingsCore.getSetting('isColorBlind')
        self.__leftPlayersPanel = playersPanelFactory(self.proxy, True, isColorBlind, isEvent, isMutlipleTeams)
        self.__rightPlayersPanel = playersPanelFactory(self.proxy, False, isColorBlind, isEvent, isMutlipleTeams)
        self.__damageInfoPanel = VehicleDamageInfoPanel(self.proxy)
        self.__fragCorrelation = scorePanelFactory(self.proxy, isEvent, isMutlipleTeams)
        self.__statsForm = statsFormFactory(self.proxy, isEvent, isMutlipleTeams)
        self.__plugins.init()
        self.isVehicleCountersVisible = g_settingsCore.getSetting('showVehiclesCounter')
        self.__fragCorrelation.showVehiclesCounter(self.isVehicleCountersVisible)
        self.__vErrorsPanel = VehicleErrorMessages(self.proxy)
        self.__vMsgsPanel = VehicleMessages(self.proxy)
        self.__pMsgsPanel = PlayerMessages(self.proxy)
        self.__plugins.start()
        self.__debugPanel.start()
        self.__consumablesPanel.start()
        self.__damagePanel.start()
        self.__ingameHelp.start()
        self.__vErrorsPanel.start()
        self.__vMsgsPanel.start()
        self.__pMsgsPanel.start()
        self.__markersManager.start()
        self.__markersManager.setMarkerDuration(GUI_SETTINGS.markerHitSplashDuration)
        markers = {'enemy': g_settingsCore.getSetting('enemy'),
         'dead': g_settingsCore.getSetting('dead'),
         'ally': g_settingsCore.getSetting('ally')}
        self.__markersManager.setMarkerSettings(markers)
        MessengerEntry.g_instance.gui.invoke('populateUI', self.proxy)
        g_guiResetters.add(self.__onRecreateDevice)
        g_repeatKeyHandlers.add(self.component.handleKeyEvent)
        self.__onRecreateDevice()
        self.__statsForm.populate()
        self.__leftPlayersPanel.populateUI(self.proxy)
        self.__rightPlayersPanel.populateUI(self.proxy)
        if BattleReplay.g_replayCtrl.isPlaying:
            BattleReplay.g_replayCtrl.onBattleSwfLoaded()
        self.__populateData(isMutlipleTeams)
        self.__minimap.start()
        self.__radialMenu.setSettings(self.__settingsInterface)
        self.__radialMenu.populateUI(self.proxy)
        self.__ribbonsPanel.start()
        g_sessionProvider.setBattleUI(self)
        self.__dynSquadSoundCtrl = DynSquadSoundsController(self.__soundManager)
        self.__markersEntitiesCtrl = DynSquadEntityController((self.__minimap, self.__markersManager))
        self.__arenaCtrl = battleArenaControllerFactory(self, isEvent, isMutlipleTeams)
        g_sessionProvider.addArenaCtrl(self.__arenaCtrl)
        g_sessionProvider.addArenaCtrl(self.__dynSquadSoundCtrl)
        g_sessionProvider.addArenaCtrl(self.__markersEntitiesCtrl)
        self.updateFlagsColor()
        self.movie.setFocussed(SCALEFORM_SWF_PATH)
        self.call('battle.initDynamicSquad', self.__getDynamicSquadsInitParams())
        if self.__arena.period == constants.ARENA_PERIOD.BATTLE:
            self.call('players_panel.setState', [g_settingsCore.getSetting('ppState')])
        else:
            self.call('players_panel.setState', ['large'])
        self.call('sixthSenseIndicator.setDuration', [GUI_SETTINGS.sixthSenseDuration])
        g_tankActiveCamouflage[player.vehicleTypeDescriptor.type.compactDescr] = self.__arena.arenaType.vehicleCamouflageKind
        keyCode = CommandMapping.g_instance.get('CMD_VOICECHAT_MUTE')
        if not BigWorld.isKeyDown(keyCode):
            VOIP.getVOIPManager().setMicMute(True)
        ctrl = g_sessionProvider.getVehicleStateCtrl()
        ctrl.onVehicleStateUpdated += self.__onVehicleStateUpdated
        self.__dynSquadListener = DynSquadViewListener(self.proxy)

    def beforeDelete(self):
        LOG_DEBUG('[Battle] beforeDelete')
        ctrl = g_sessionProvider.getVehicleStateCtrl()
        ctrl.onVehicleStateUpdated -= self.__onVehicleStateUpdated
        if self.colorManager:
            self.colorManager.dispossessUI()
        voice = VoiceChatInterface.g_instance
        if voice:
            voice.dispossessUI(self.proxy)
            voice.onPlayerSpeaking -= self.setPlayerSpeaking
            voice.onVoiceChatInitFailed -= self.onVoiceChatInitFailed
        if self.__plugins is not None:
            self.__plugins.stop()
            self.__plugins.fini()
            self.__plugins = None
        if self.movingText is not None:
            self.movingText.dispossessUI()
            self.movingText = None
        if self.__soundManager is not None:
            self.__soundManager.dispossessUI()
            self.__soundManager = None
        if self.__dynSquadSoundCtrl is not None:
            g_sessionProvider.removeArenaCtrl(self.__dynSquadSoundCtrl)
            self.__dynSquadSoundCtrl.destroy()
            self.__dynSquadSoundCtrl = None
        if self.colorManager is not None:
            self.colorManager.dispossessUI()
            self.colorManager = None
        if self.component:
            g_repeatKeyHandlers.discard(self.component.handleKeyEvent)
        g_settingsCore.onSettingsChanged -= self.__accs_onSettingsChanged
        g_settingsCore.interfaceScale.onScaleChanged -= self.__onRecreateDevice
        self.__timersBar.destroy()
        self.__teamBasesPanel.destroy()
        self.__debugPanel.destroy()
        self.__consumablesPanel.destroy()
        self.__damagePanel.destroy()
        self.__markersManager.destroy()
        self.__ingameHelp.destroy()
        self.__vErrorsPanel.destroy()
        self.__vMsgsPanel.destroy()
        self.__pMsgsPanel.destroy()
        self.__radialMenu.destroy()
        self.__minimap.destroy()
        self.__ribbonsPanel.destroy()
        self.__fragCorrelation.destroy()
        self.__statsForm.destroy()
        g_sessionProvider.clearBattleUI()
        if self.__arenaCtrl is not None:
            g_sessionProvider.removeArenaCtrl(self.__arenaCtrl)
            self.__arenaCtrl.destroy()
            self.__arenaCtrl = None
        self.__ppSwitcher.destroy()
        if self.__markersEntitiesCtrl is not None:
            g_sessionProvider.removeArenaCtrl(self.__markersEntitiesCtrl)
            self.__markersEntitiesCtrl.destroy()
            self.__markersEntitiesCtrl = None
        self.__leftPlayersPanel.dispossessUI()
        self.__rightPlayersPanel.dispossessUI()
        MessengerEntry.g_instance.gui.invoke('dispossessUI')
        self.__arena = None
        g_guiResetters.discard(self.__onRecreateDevice)
        self.__settingsInterface.dispossessUI()
        self.__settingsInterface = None
        VoiceChatInterface.g_instance.onVoiceChatInitFailed -= self.onVoiceChatInitFailed
        if self.__dynSquadListener:
            self.__dynSquadListener.destroy()
            self.__dynSquadListener = None
        BattleWindow.beforeDelete(self)
        return

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

    def _setFireInVehicle(self, bool):
        self.call('destroyTimer.onFireInVehicle', [bool])

    def onVoiceChatInitFailed(self):
        if GUI_SETTINGS.voiceChat:
            self.call('VoiceChat.initFailed', [])

    def clearCommands(self):
        pass

    def bindCommands(self):
        self.__consumablesPanel.bindCommands()
        self.__ingameHelp.buildCmdMapping()

    def updateFlagsColor(self):
        isColorBlind = g_settingsCore.getSetting('isColorBlind')
        colorGreen = self.colorManager.getSubScheme('flag_team_green', isColorBlind=isColorBlind)['rgba']
        colorRed = self.colorManager.getSubScheme('flag_team_red', isColorBlind=isColorBlind)['rgba']
        arenaDP = g_sessionProvider.getArenaDP()
        teamsOnArena = arenaDP.getTeamsOnArena()
        for teamIdx in teamsOnArena:
            color = colorGreen if arenaDP.isAllyTeam(teamIdx) else colorRed
            BigWorld.wg_setFlagColor(teamIdx, color / 255)

        for teamIdx in [0] + teamsOnArena:
            BigWorld.wg_setFlagEmblem(teamIdx, 'system/maps/wg_emblem.dds', Math.Vector4(0.0, 0.1, 0.5, 0.9))

    def setPlayerSpeaking(self, accountDBID, flag):
        self.__callEx('setPlayerSpeaking', [accountDBID, flag])
        vID = g_sessionProvider.getCtx().getVehIDByAccDBID(accountDBID)
        if vID > 0:
            self.__markersManager.showDynamic(vID, flag)

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
        guiType = self.__arena.guiType
        if not GUI_SETTINGS.isBattlePanelsUpdatableInCtrl and guiType == constants.ARENA_GUI_TYPE.RANDOM or guiType == constants.ARENA_GUI_TYPE.TRAINING and constants.IS_DEVELOPMENT:
            self.__arenaCtrl.setPanelsUpdatable(value=not visible)
        if BigWorld.player() is not None and isPlayerAvatar():
            BigWorld.player().setForcedGuiControlMode(visible, False, enableAiming)
        return

    def tryLeaveRequest(self, _):
        resStr = 'quitBattle'
        replayCtrl = BattleReplay.g_replayCtrl
        player = BigWorld.player()
        isVehicleAlive = getattr(player, 'isVehicleAlive', False)
        isNotTraining = self.__arena.guiType != constants.ARENA_GUI_TYPE.TRAINING
        isNotEventBattle = self.__arena.guiType != constants.ARENA_GUI_TYPE.EVENT_BATTLES
        if not replayCtrl.isPlaying:
            if constants.IS_KOREA and gui.GUI_SETTINGS.igrEnabled and self.__arena is not None and isNotTraining:
                vehicleID = getattr(player, 'playerVehicleID', -1)
                if vehicleID in self.__arena.vehicles:
                    vehicle = self.__arena.vehicles[vehicleID]
                    if isVehicleAlive and vehicle.get('igrType') != constants.IGR_TYPE.NONE:
                        resStr = 'quitBattleIGR'
                else:
                    LOG_ERROR("Player's vehicle not found", vehicleID)
            isDeserter = isVehicleAlive and isNotTraining and isNotEventBattle
            if isDeserter:
                resStr += '/deserter'
        else:
            isDeserter = False
        self.__callEx('tryLeaveResponse', [resStr, isDeserter])
        return

    def onExitBattle(self, _):
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
            self.__callEx('setServerName', ['-'])
        links = GUI_SETTINGS.reportBugLinks
        if len(links):
            reportBugButton = makeHyperLink('ingameMenu', MENU.INGAME_MENU_LINKS_REPORT_BUG)
            self.__callEx('setReportBugLink', [reportBugButton])
        return

    def reportBug(self, _):
        reportBugOpenConfirm(g_sessionProvider.getArenaDP().getVehicleInfo().player.accountDBID)

    def __getDynamicSquadsInitParams(self):
        return [self.__arena.guiType == constants.ARENA_GUI_TYPE.RANDOM, False]

    def __populateData(self, isMutlipleTeams = False):
        arena = avatar_getter.getArena()
        arenaDP = g_sessionProvider.getArenaDP()
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
            elif arena.guiType in constants.ARENA_GUI_TYPE.RANGE:
                arenaData.append(constants.ARENA_GUI_TYPE_LABEL.LABELS[arena.guiType])
                if arena.guiType == constants.ARENA_GUI_TYPE.EVENT_BATTLES and hasResourcePoints():
                    arenaData.append(i18n.makeString(MENU.LOADING_BATTLETYPES_RESOURCEPOINTS_UPPER))
                elif arena.guiType == constants.ARENA_GUI_TYPE.EVENT_BATTLES and isMutlipleTeams:
                    arenaData.append(i18n.makeString(MENU.LOADING_BATTLETYPES_MIX_UPPER))
                else:
                    arenaData.append('#menu:loading/battleTypes/%d' % arena.guiType)
            else:
                arenaData.extend([arena.guiType + 1, '#menu:loading/battleTypes/%d' % arena.guiType])
            myTeamNumber = arenaDP.getNumberOfTeam()
            getTeamName = g_sessionProvider.getCtx().getTeamName
            arenaData.extend([getTeamName(myTeamNumber), getTeamName(arenaDP.getNumberOfTeam(enemy=True))])
            teamHasBase = 1 if isBaseExists(BigWorld.player().arenaTypeID, myTeamNumber) else 2
            if not isEventBattle():
                typeEvent = 'normal'
                winText = getBattleSubTypeWinText(BigWorld.player().arenaTypeID, teamHasBase)
            else:
                typeEvent = 'fallout'
                winText = i18n.makeString('#arenas:type/fallout/description')
            arenaData.append(winText)
            arenaData.append(typeEvent)
            vehInfo = arenaDP.getVehicleInfo(arenaDP.getPlayerVehicleID())
            pqTipData = [None] * 3
            pQuests = vehInfo.player.getPotapovQuests()
            serverSettings = g_lobbyContext.getServerSettings()
            isPQEnabled = serverSettings is not None and serverSettings.isPotapovQuestEnabled()
            if isPQEnabled and (arena.guiType == constants.ARENA_GUI_TYPE.RANDOM or arena.guiType == constants.ARENA_GUI_TYPE.TRAINING and constants.IS_DEVELOPMENT):
                if len(pQuests):
                    quest = pQuests[0]
                    pqTipData = [quest.getUserName(), quest.getUserMainCondition(), quest.getUserAddCondition()]
                else:
                    pqTipData = [i18n.makeString('#ingame_gui:potapovQuests/tip'), None, None]
            arenaData.extend(pqTipData)
        self.__callEx('arenaData', arenaData)
        return

    def __onRecreateDevice(self, scale = None):
        params = list(GUI.screenResolution())
        params.append(g_settingsCore.interfaceScale.get())
        self.call('Stage.Update', params)
        self.__markersManager.updateMarkersScale()

    def __callEx(self, funcName, args = None):
        self.call('battle.' + funcName, args)

    def __accs_onSettingsChanged(self, diff):
        self.colorManager.update()
        if 'isColorBlind' in diff:
            isColorBlind = diff['isColorBlind']
            self.__leftPlayersPanel.defineColorFlags(isColorBlind=isColorBlind)
            self.__rightPlayersPanel.defineColorFlags(isColorBlind=isColorBlind)
            self.updateFlagsColor()
            self.__markersManager.updateMarkers()
            self.__minimap.updateEntries()
        if 'enemy' in diff or 'dead' in diff or 'ally' in diff:
            markers = {'enemy': g_settingsCore.getSetting('enemy'),
             'dead': g_settingsCore.getSetting('dead'),
             'ally': g_settingsCore.getSetting('ally')}
            self.__markersManager.setMarkerSettings(markers)
            self.__markersManager.updateMarkerSettings()
        if 'showVehiclesCounter' in diff:
            self.isVehicleCountersVisible = diff['showVehiclesCounter']
            self.__fragCorrelation.showVehiclesCounter(self.isVehicleCountersVisible)
        if 'interfaceScale' in diff:
            self.__onRecreateDevice()
        self.__arenaCtrl.invalidateGUI()
        self.__arenaCtrl.invalidateArenaInfo()

    def setTeamValuesData(self, data):
        if self.__battle_flashObject is not None:
            self.__battle_flashObject.setTeamValues(data)
        return

    def setMultiteamValues(self, data):
        if self.__battle_flashObject is not None:
            self.__battle_flashObject.setMultiteamValues(data)
        return

    def getPlayerNameLength(self, isEnemy):
        panel = self.rightPlayersPanel if isEnemy else self.leftPlayersPanel
        return panel.getPlayerNameLength()


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
        self.__timeInterval = TimeInterval(self.__UPDATE_INTERVAL, self, '_DebugPanel__update')
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
                        if _isVehicleEntity(v):
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
