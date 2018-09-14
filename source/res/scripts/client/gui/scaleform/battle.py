# Embedded file name: scripts/client/gui/Scaleform/Battle.py
import weakref
import BigWorld
from CTFManager import g_ctfManager
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
from external_strings_utils import unicode_from_utf8, normalized_unicode_trim
from gui.Scaleform.daapi.view.battle import findHTMLFormat
from gui.Scaleform.daapi.view.battle.respawn_view import RespawnViewPlugin
from gui.Scaleform.daapi.view.battle.RadialMenu import RadialMenu
from gui.Scaleform.daapi.view.battle.flag_notification import FlagNotificationPlugin
from gui.Scaleform.daapi.view.battle.players_panel import playersPanelFactory
from gui.Scaleform.daapi.view.battle.score_panel import scorePanelFactory
from gui.Scaleform.daapi.view.battle.ConsumablesPanel import ConsumablesPanel
from gui.Scaleform.daapi.view.battle.BattleRibbonsPanel import BattleRibbonsPanel
from gui.Scaleform.daapi.view.battle.damage_panel import DamagePanel
from gui.Scaleform.daapi.view.battle.markers import MarkersManager
from gui.Scaleform.daapi.view.lobby.ReportBug import makeHyperLink, reportBugOpenConfirm
from gui.Scaleform.locale.INGAME_GUI import INGAME_GUI
from gui.Scaleform.locale.MENU import MENU
import gui
from gui.battle_control import g_sessionProvider
from gui.battle_control.DynSquadViewListener import DynSquadViewListener
from gui.battle_control.battle_arena_ctrl import BattleArenaController
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE
from gui.battle_control.dyn_squad_arena_controllers import DynSquadSoundsController, DynSquadEntityController
from gui.prb_control.formatters import getPrebattleFullDescription
from gui.shared.utils.plugins import PluginsCollection
from messenger import MessengerEntry, g_settings
from windows import BattleWindow
from SettingsInterface import SettingsInterface
from debug_utils import LOG_CURRENT_EXCEPTION, LOG_DEBUG, LOG_ERROR
from helpers import i18n, html, isPlayerAvatar
from helpers.i18n import makeString
from PlayerEvents import g_playerEvents
from MemoryCriticalController import g_critMemHandler
from items import vehicles
from gui import DEPTH_OF_Battle, GUI_SETTINGS, g_tankActiveCamouflage, g_guiResetters, g_repeatKeyHandlers, game_control
from gui.LobbyContext import g_lobbyContext
from gui.Scaleform import VoiceChatInterface, ColorSchemeManager, getNecessaryArenaFrameName
from gui.Scaleform.SoundManager import SoundManager
from gui.shared.utils import toUpper
from gui.shared.utils.sound import Sound
from gui.shared.utils.functions import getBattleSubTypeBaseNumder, isControlPointExists, makeTooltip, getBattleSubTypeWinText, getArenaSubTypeName, isBaseExists
from gui.Scaleform.windows import UIInterface
from gui.Scaleform.MovingText import MovingText
from gui.Scaleform.Minimap import Minimap
from gui.Scaleform.CursorDelegator import g_cursorDelegator
from gui.Scaleform.ingame_help import IngameHelp
from gui.Scaleform import SCALEFORM_SWF_PATH
from gui.battle_control.arena_info import isEventBattle
from gui.prb_control.dispatcher import g_prbLoader
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
    markersManager = property(lambda self: self.__markersManager)
    vErrorsPanel = property(lambda self: self.__vErrorsPanel)
    vMsgsPanel = property(lambda self: self.__vMsgsPanel)
    pMsgsPanel = property(lambda self: self.__pMsgsPanel)
    minimap = property(lambda self: self.__minimap)
    radialMenu = property(lambda self: self.__radialMenu)
    damageInfoPanel = property(lambda self: self.__damageInfoPanel)
    fragCorrelation = property(lambda self: self.__fragCorrelation)
    leftPlayersPanel = property(lambda self: self.__leftPlayersPanel)
    rightPlayersPanel = property(lambda self: self.__rightPlayersPanel)
    ribbonsPanel = property(lambda self: self.__ribbonsPanel)
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
        self.__timerCallBackId = None
        self.__arena = BigWorld.player().arena
        self.__playersPanelStateChanged = False
        self.__battleNotificationExecuted = False
        self.__plugins = PluginsCollection(self)
        plugins = {}
        if isEventBattle():
            plugins.update({'flagNotification': FlagNotificationPlugin})
            if not BattleReplay.g_replayCtrl.isPlaying:
                plugins.update({'respawnView': RespawnViewPlugin})
        self.__plugins.addPlugins(plugins)
        BattleWindow.__init__(self, 'battle.swf')
        self.__timerSound = Sound(self.__arena.arenaType.battleCountdownTimerSound)
        self.__isTimerVisible = False
        self.__isHelpWindowShown = False
        self.__inBattlePlayingTime = 0
        self.__cameraMode = None
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
        self.__dynSquadListener = None
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
        self.__markersManager.active(isShow)

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
            self.__arenaCtrl.invalidateGUI(not g_sessionProvider.getCtx().isPlayerObserver())
            g_sessionProvider.getVehicleStateCtrl().switchToAnother(id)
            self.hideVehicleTimer('ALL')
            self.vErrorsPanel.clear()
            self.vMsgsPanel.clear()
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
        self.__teamBasesPanel = TeamBasesPanel(self.proxy)
        self.__debugPanel = DebugPanel(self.proxy)
        self.__consumablesPanel = ConsumablesPanel(self.proxy)
        self.__damagePanel = DamagePanel(self.proxy)
        self.__markersManager = MarkersManager(self.proxy)
        self.__ingameHelp = IngameHelp(self.proxy)
        self.__minimap = Minimap(self.proxy)
        self.__radialMenu = RadialMenu(self.proxy)
        self.__ribbonsPanel = BattleRibbonsPanel(self.proxy)
        isColorBlind = g_settingsCore.getSetting('isColorBlind')
        self.__leftPlayersPanel = playersPanelFactory(self.proxy, True, isColorBlind)
        self.__rightPlayersPanel = playersPanelFactory(self.proxy, False, isColorBlind)
        self.__damageInfoPanel = VehicleDamageInfoPanel(self.proxy)
        self.__fragCorrelation = scorePanelFactory(self.proxy)
        self.__plugins.init()
        if isEventBattle():
            statsSwfPath = 'FalloutStatisticForm.swf'
            self.movie.preinitializeStatsHintView('FalloutStatisticHint.swf', INGAME_GUI.TABSTATSHINT)
        else:
            statsSwfPath = 'StatisticForm.swf'
        self.movie.preinitializeStatsView(statsSwfPath)
        self.isVehicleCountersVisible = g_settingsCore.getSetting('showVehiclesCounter')
        self.__fragCorrelation.showVehiclesCounter(self.isVehicleCountersVisible)
        self.__vErrorsPanel = FadingMessagesPanel(self.proxy, 'VehicleErrorsPanel', 'gui/vehicle_errors_panel.xml', isColorBlind=isColorBlind)
        self.__vMsgsPanel = FadingMessagesPanel(self.proxy, 'VehicleMessagesPanel', 'gui/vehicle_messages_panel.xml', isColorBlind=isColorBlind)
        self.__pMsgsPanel = FadingMessagesPanel(self.proxy, 'PlayerMessagesPanel', 'gui/player_messages_panel.xml', isColorBlind=isColorBlind)
        self.__plugins.start()
        self.__teamBasesPanel.start()
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
        self.__initMemoryCriticalHandlers()
        MessengerEntry.g_instance.gui.invoke('populateUI', self.proxy)
        g_guiResetters.add(self.__onRecreateDevice)
        g_repeatKeyHandlers.add(self.component.handleKeyEvent)
        self.__onRecreateDevice()
        self.__leftPlayersPanel.populateUI(self.proxy)
        self.__rightPlayersPanel.populateUI(self.proxy)
        self.__populateData()
        self.__minimap.start()
        self.__radialMenu.setSettings(self.__settingsInterface)
        self.__radialMenu.populateUI(self.proxy)
        self.__ribbonsPanel.start()
        g_sessionProvider.setBattleUI(self)
        self.__dynSquadSoundCtrl = DynSquadSoundsController(self.__soundManager)
        self.__markersEntitiesCtrl = DynSquadEntityController((self.__minimap, self.__markersManager))
        self.__arenaCtrl = BattleArenaController(self)
        g_sessionProvider.addArenaCtrl(self.__arenaCtrl)
        g_sessionProvider.addArenaCtrl(self.__dynSquadSoundCtrl)
        g_sessionProvider.addArenaCtrl(self.__markersEntitiesCtrl)
        BigWorld.callback(1, self.__setArenaTime)
        self.updateFlagsColor()
        self.movie.setFocussed(SCALEFORM_SWF_PATH)
        self.call('battle.initDynamicSquad', [self.__arena.guiType == constants.ARENA_GUI_TYPE.RANDOM, False])
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
        ctrl = g_sessionProvider.getVehicleStateCtrl()
        ctrl.onVehicleStateUpdated += self.__onVehicleStateUpdated
        self.__dynSquadListener = DynSquadViewListener(self.proxy)

    def beforeDelete(self):
        LOG_DEBUG('[Battle] beforeDelete')
        ctrl = g_sessionProvider.getVehicleStateCtrl()
        ctrl.onVehicleStateUpdated -= self.__onVehicleStateUpdated
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
        self.__timerSound.stop()
        g_sessionProvider.clearBattleUI()
        if self.__arenaCtrl is not None:
            g_sessionProvider.removeArenaCtrl(self.__arenaCtrl)
            self.__arenaCtrl.destroy()
            self.__arenaCtrl = None
        if self.__markersEntitiesCtrl is not None:
            g_sessionProvider.removeArenaCtrl(self.__markersEntitiesCtrl)
            self.__markersEntitiesCtrl.destroy()
            self.__markersEntitiesCtrl = None
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

    def __populateData(self):
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
            if not isEventBattle():
                typeEvent = 'normal'
                winText = getBattleSubTypeWinText(BigWorld.player().arenaTypeID, teamHasBase)
            else:
                typeEvent = 'fallout'
                winText = i18n.makeString('#arenas:type/fallout/description')
            arenaData.append(winText)
            arenaData.append(typeEvent)
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

    def __showFinalStatsResults(self, isActiveVehicle, _):
        if isActiveVehicle:
            if self.__arena:
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

    def __isVehicleFlagbearer(self, vehicleID):
        for flagID in g_ctfManager.getFlags():
            flagInfo = g_ctfManager.getFlagInfo(flagID)
            vehicle = flagInfo['vehicle']
            if vehicleID == vehicle:
                return True

        return False

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
        params.append(g_settingsCore.interfaceScale.get())
        self.call('Stage.Update', params)
        self.__markersManager.updateMarkersScale()

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

    def getFormattedStrings(self, vInfoVO, vStatsVO, ctx, fullPlayerName):
        format = findHTMLFormat(vInfoVO, ctx, self.colorManager)
        unicodeStr, _ = unicode_from_utf8(fullPlayerName)
        if len(unicodeStr) > ctx.labelMaxLength:
            fullPlayerName = '{0}..'.format(normalized_unicode_trim(fullPlayerName, ctx.labelMaxLength - 2))
        fragsString = format % ' '
        if vStatsVO.frags:
            fragsString = format % str(vStatsVO.frags)
        return (format % fullPlayerName, fragsString, format % vInfoVO.vehicleType.shortName)

    def setTeamValuesData(self, data):
        if self.__battle_flashObject is not None:
            self.__battle_flashObject.setTeamValues(data)
        return

    def getPlayerNameLength(self, isEnemy):
        panel = self.rightPlayersPanel if isEnemy else self.leftPlayersPanel
        return panel.getPlayerNameLength()


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
        arenaSubType = getArenaSubTypeName(BigWorld.player().arenaTypeID)
        needRedOffset = arenaSubType not in ('assault', 'assault2', 'domination')
        self.__callFlash('init', [needRedOffset])

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
        elif key == 'ALLY_HIT' and isEventBattle():
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
