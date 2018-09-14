# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/Battle.py
import weakref
import BigWorld
import GUI
import Math
import SoundGroups
import VOIP
import constants
import BattleReplay
import CommandMapping
from ConnectionManager import connectionManager
from account_helpers.settings_core.SettingsCore import g_settingsCore
from gui.Scaleform.LogitechMonitor import LogitechMonitor
from gui.Scaleform.daapi.view.battle.damage_info_panel import VehicleDamageInfoPanel
from gui.Scaleform.daapi.view.battle.gas_attack import GasAttackPlugin
from gui.Scaleform.daapi.view.battle.repair_timer import RepairTimerPlugin
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
from gui.Scaleform.locale.ARENAS import ARENAS
from gui.Scaleform.locale.INGAME_GUI import INGAME_GUI
from gui.Scaleform.locale.MENU import MENU
import gui
from gui.battle_control import g_sessionProvider
from gui.battle_control.DynSquadViewListener import DynSquadViewListener, RecordDynSquadViewListener, ReplayDynSquadViewListener
from gui.battle_control.battle_arena_ctrl import battleArenaControllerFactory
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE
from gui.prb_control.formatters import getPrebattleFullDescription
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from gui.shared.formatters import text_styles
from gui.shared.utils.TimeInterval import TimeInterval
from gui.shared.utils.plugins import PluginsCollection
from messenger import MessengerEntry
from windows import BattleWindow
from SettingsInterface import SettingsInterface
from debug_utils import LOG_DEBUG, LOG_ERROR
from helpers import i18n, isPlayerAvatar
from gui import DEPTH_OF_Battle, GUI_SETTINGS, g_tankActiveCamouflage, g_guiResetters, g_repeatKeyHandlers, game_control
from gui.LobbyContext import g_lobbyContext
from gui.Scaleform import VoiceChatInterface, ColorSchemeManager, getNecessaryArenaFrameName
from gui.Scaleform.SoundManager import SoundManager
from gui.shared.denunciator import BattleDenunciator
from gui.shared.utils import toUpper
from gui.shared.utils.functions import makeTooltip, getArenaSubTypeName, isBaseExists, getBattleSubTypeWinText
from gui.Scaleform.windows import UIInterface
from gui.Scaleform.MovingText import MovingText
from gui.Scaleform.Minimap import Minimap
from gui.Scaleform.CursorDelegator import g_cursorDelegator
from gui.Scaleform.ingame_help import IngameHelp
from gui.Scaleform import SCALEFORM_SWF_PATH
from gui.battle_control.arena_info import getArenaIcon, hasFlags, hasRespawns, hasResourcePoints, isFalloutMultiTeam, hasRepairPoints, isFalloutBattle, hasGasAttack, isRandomBattle
from gui.battle_control import avatar_getter

def _isVehicleEntity(entity):
    import Vehicle
    return isinstance(entity, Vehicle.Vehicle)


def _getQuestsTipData(arena, arenaDP):
    pqTipData = [None] * 3
    serverSettings = g_lobbyContext.getServerSettings()
    isPQEnabled = serverSettings is not None and serverSettings.isPotapovQuestEnabled()
    if isPQEnabled and (arena.guiType == constants.ARENA_GUI_TYPE.RANDOM or arena.guiType == constants.ARENA_GUI_TYPE.TRAINING and constants.IS_DEVELOPMENT or isFalloutBattle()):
        vehInfo = arenaDP.getVehicleInfo(arenaDP.getPlayerVehicleID(forceUpdate=True))
        if isFalloutBattle():
            pQuests = vehInfo.player.getFalloutPotapovQuests()
        else:
            pQuests = vehInfo.player.getRandomPotapovQuests()
        if len(pQuests):
            quest = pQuests[0]
            pqTipData = [quest.getUserName(), _getQuestConditionsMessage(INGAME_GUI.POTAPOVQUESTS_TIP_MAINHEADER, quest.getUserMainCondition()), _getQuestConditionsMessage(INGAME_GUI.POTAPOVQUESTS_TIP_ADDITIONALHEADER, quest.getUserAddCondition())]
        else:
            pqTipData = [i18n.makeString(INGAME_GUI.POTAPOVQUESTS_TIP_NOQUESTS_BATTLETYPE if isFalloutBattle() else INGAME_GUI.POTAPOVQUESTS_TIP_NOQUESTS_VEHICLETYPE), None, None]
    return pqTipData


def _getQuestConditionsMessage(header, text):
    return i18n.makeString(text_styles.middleTitle(header) + '\n' + text_styles.main(text))


_CONTOUR_ICONS_MASK = '../maps/icons/vehicle/contour/%(unicName)s.png'
_SMALL_MAP_SOURCE = '../maps/icons/map/battleLoading/%s.png'
_SCOPE = EVENT_BUS_SCOPE.BATTLE

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
     constants.VEHICLE_MISC_STATUS.VEHICLE_IS_OVERTURNED: 'overturn'}
    VEHICLE_DEATHZONE_TIMER = {'ALL': 'all',
     constants.DEATH_ZONES.STATIC: 'death_zone',
     constants.DEATH_ZONES.GAS_ATTACK: 'gas_attack'}
    VEHICLE_DEATHZONE_TIMER_SOUND = {constants.DEATH_ZONES.GAS_ATTACK: ({'warning': 'fallout_gaz_sphere_warning',
                                         'critical': 'fallout_gaz_sphere_timer'}, {'warning': '/GUI/fallout/fallout_gaz_sphere_warning',
                                         'critical': '/GUI/fallout/fallout_gaz_sphere_timer'})}
    __cameraVehicleID = -1
    __stateHandlers = {VEHICLE_VIEW_STATE.FIRE: '_setFireInVehicle',
     VEHICLE_VIEW_STATE.SHOW_DESTROY_TIMER: '_showVehicleTimer',
     VEHICLE_VIEW_STATE.HIDE_DESTROY_TIMER: '_hideVehicleTimer',
     VEHICLE_VIEW_STATE.SHOW_DEATHZONE_TIMER: 'showDeathzoneTimer',
     VEHICLE_VIEW_STATE.HIDE_DEATHZONE_TIMER: 'hideDeathzoneTimer',
     VEHICLE_VIEW_STATE.OBSERVED_BY_ENEMY: '_showSixthSenseIndicator'}

    def __init__(self, appNS):
        self.__ns = appNS
        self.__soundManager = None
        self.__arena = BigWorld.player().arena
        self.__plugins = PluginsCollection(self)
        plugins = {}
        if hasFlags():
            plugins['flagNotification'] = FlagNotificationPlugin
        if hasRepairPoints():
            plugins['repairTimer'] = RepairTimerPlugin
        if hasRespawns() and (constants.IS_DEVELOPMENT or not BattleReplay.g_replayCtrl.isPlaying):
            plugins['respawnView'] = RespawnViewPlugin
        if hasResourcePoints():
            plugins['resources'] = ResourcePointsPlugin
        if hasGasAttack():
            plugins['gasAttack'] = GasAttackPlugin
        self.__plugins.addPlugins(plugins)
        self.__denunciator = BattleDenunciator()
        self.__timerSounds = {}
        for timer, sounds in self.VEHICLE_DEATHZONE_TIMER_SOUND.iteritems():
            self.__timerSounds[timer] = {}
            for level, sound in sounds[False].iteritems():
                self.__timerSounds[timer][level] = SoundGroups.g_instance.getSound2D(sound)

        self.__timerSound = None
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

    @property
    def appNS(self):
        return self.__ns

    @property
    def soundManager(self):
        return self.__soundManager

    def attachCursor(self):
        return g_cursorDelegator.activateCursor()

    def detachCursor(self):
        return g_cursorDelegator.detachCursor()

    def getRoot(self):
        return self.__battle_flashObject

    def getCameraVehicleID(self):
        return self.__cameraVehicleID

    def populateFragCorrelationBar(self, _):
        if self.__fragCorrelation is not None:
            self.__fragCorrelation.populate()
        return

    def showAll(self, event):
        self.call('battle.showAll', [event.ctx['visible']])

    def showCursor(self, isShow):
        self.cursorVisibility(-1, isShow)

    def selectPlayer(self, cid, vehId):
        player = BigWorld.player()
        if isPlayerAvatar():
            player.selectPlayer(int(vehId))

    def onDenunciationReceived(self, _, uid, userName, topic):
        self.__denunciator.makeAppeal(uid, userName, topic)
        self.__arenaCtrl.invalidateGUI()

    def onPostmortemVehicleChanged(self, id):
        if self.__cameraVehicleID == id:
            return
        else:
            self.__cameraVehicleID = id
            self.__arenaCtrl.invalidateGUI(not g_sessionProvider.getCtx().isPlayerObserver())
            g_sessionProvider.getVehicleStateCtrl().switchToAnother(id)
            self._hideVehicleTimer('ALL')
            self.hideDeathzoneTimer('ALL')
            self.__vErrorsPanel.clear()
            self.__vMsgsPanel.clear()
            aim = BigWorld.player().inputHandler.aim
            if aim is not None:
                aim.updateAmmoState(True)
            return

    def onCameraChanged(self, cameraMode, curVehID=None):
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
            setVisible('vehicleErrorsPanel')
        if cameraMode == 'video':
            self.__cameraVehicleID = -1
            self.__vErrorsPanel.clear()
            self.__vMsgsPanel.clear()
            self._hideVehicleTimer('ALL')
            self.hideDeathzoneTimer('ALL')
            aim = BigWorld.player().inputHandler.aim
            if aim is not None:
                aim.updateAmmoState(True)
        aim = BigWorld.player().inputHandler.aim
        if aim is not None:
            aim.onCameraChange()
        return

    def __isGuiShown(self):
        m = self.getMember('_root')
        return m.isGuiVisible() if m is not None and callable(m.isGuiVisible) else False

    def _showVehicleTimer(self, value):
        code, time, warnLvl = value
        LOG_DEBUG('show vehicles destroy timer', code, time, warnLvl)
        self.call('destroyTimer.show', [self.VEHICLE_DESTROY_TIMER[code], time, warnLvl])

    def _hideVehicleTimer(self, code=None):
        LOG_DEBUG('hide vehicles destroy timer', code)
        if code is None:
            code = 'ALL'
        self.call('destroyTimer.hide', [self.VEHICLE_DESTROY_TIMER[code]])
        return

    def showDeathzoneTimer(self, value):
        zoneID, time, warnLvl = value
        if self.__timerSound is not None:
            self.__timerSound.stop()
            self.__timerSound = None
        sound = self.__timerSounds.get(zoneID, {}).get(warnLvl)
        if sound is not None:
            self.__timerSound = sound
            self.__timerSound.play()
        LOG_DEBUG('show vehicles deathzone timer', zoneID, time, warnLvl)
        self.call('destroyTimer.show', [self.VEHICLE_DEATHZONE_TIMER[zoneID], time, warnLvl])
        return

    def hideDeathzoneTimer(self, zoneID=None):
        if self.__timerSound is not None:
            self.__timerSound.stop()
            self.__timerSound = None
        if zoneID is None:
            zoneID = 'ALL'
        LOG_DEBUG('hide vehicles deathzone timer', zoneID)
        self.call('destroyTimer.hide', [self.VEHICLE_DEATHZONE_TIMER[zoneID]])
        return

    def _showSixthSenseIndicator(self, isShow):
        self.call('sixthSenseIndicator.show', [isShow])

    def setVisible(self, bool):
        LOG_DEBUG('[Battle] visible', bool)
        self.component.visible = bool

    def afterCreate(self):
        event = events.AppLifeCycleEvent
        g_eventBus.handleEvent(event(self.__ns, event.INITIALIZING))
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
        addListener = g_eventBus.addListener
        addListener(events.GameEvent.HELP, self.toggleHelpWindow, scope=_SCOPE)
        addListener(events.GameEvent.GUI_VISIBILITY, self.showAll, scope=_SCOPE)
        player.inputHandler.onPostmortemVehicleChanged += self.onPostmortemVehicleChanged
        player.inputHandler.onCameraChanged += self.onCameraChanged
        g_settingsCore.onSettingsChanged += self.__accs_onSettingsChanged
        g_settingsCore.interfaceScale.onScaleChanged += self.__onRecreateDevice
        isMutlipleTeams = isFalloutMultiTeam()
        isFallout = isFalloutBattle()
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
        self.__timersBar = TimersBar(self.proxy, isFallout)
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
        self.__leftPlayersPanel = playersPanelFactory(self.proxy, True, isColorBlind, isFallout, isMutlipleTeams)
        self.__rightPlayersPanel = playersPanelFactory(self.proxy, False, isColorBlind, isFallout, isMutlipleTeams)
        self.__damageInfoPanel = VehicleDamageInfoPanel(self.proxy)
        self.__damageInfoPanel.start()
        self.__fragCorrelation = scorePanelFactory(self.proxy, isFallout, isMutlipleTeams)
        self.__statsForm = statsFormFactory(self.proxy, isFallout, isMutlipleTeams)
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
        self.__populateData()
        self.__minimap.start()
        self.__radialMenu.setSettings(self.__settingsInterface)
        self.__radialMenu.populateUI(self.proxy)
        self.__ribbonsPanel.start()
        g_sessionProvider.setBattleUI(self)
        self.__arenaCtrl = battleArenaControllerFactory(self, isFallout, isMutlipleTeams)
        g_sessionProvider.addArenaCtrl(self.__arenaCtrl)
        self.updateFlagsColor()
        self.movie.setFocussed(SCALEFORM_SWF_PATH)
        self.call('battle.initDynamicSquad', self.__getDynamicSquadsInitParams(enableButton=not BattleReplay.g_replayCtrl.isPlaying))
        self.call('sixthSenseIndicator.setDuration', [GUI_SETTINGS.sixthSenseDuration])
        g_tankActiveCamouflage[player.vehicleTypeDescriptor.type.compactDescr] = self.__arena.arenaType.vehicleCamouflageKind
        keyCode = CommandMapping.g_instance.get('CMD_VOICECHAT_MUTE')
        if not BigWorld.isKeyDown(keyCode):
            VOIP.getVOIPManager().setMicMute(True)
        ctrl = g_sessionProvider.getVehicleStateCtrl()
        ctrl.onVehicleStateUpdated += self.__onVehicleStateUpdated
        ctrl.onPostMortemSwitched += self.__onPostMortemSwitched
        if BattleReplay.g_replayCtrl.isPlaying:
            self.__dynSquadListener = ReplayDynSquadViewListener(self.proxy)
        elif BattleReplay.g_replayCtrl.isRecording:
            self.__dynSquadListener = RecordDynSquadViewListener(self.proxy)
        else:
            self.__dynSquadListener = DynSquadViewListener(self.proxy)
        g_eventBus.handleEvent(event(self.__ns, event.INITIALIZED))

    def beforeDelete(self):
        LOG_DEBUG('[Battle] beforeDelete')
        removeListener = g_eventBus.removeListener
        removeListener(events.GameEvent.HELP, self.toggleHelpWindow, scope=_SCOPE)
        removeListener(events.GameEvent.GUI_VISIBILITY, self.showAll, scope=_SCOPE)
        ctrl = g_sessionProvider.getVehicleStateCtrl()
        if ctrl is not None:
            ctrl.onVehicleStateUpdated -= self.__onVehicleStateUpdated
            ctrl.onPostMortemSwitched -= self.__onPostMortemSwitched
        player = BigWorld.player()
        if player and player.inputHandler:
            player.inputHandler.onPostmortemVehicleChanged -= self.onPostmortemVehicleChanged
            player.inputHandler.onCameraChanged -= self.onCameraChanged
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
        if self.__timerSound is not None:
            self.__timerSound.stop()
            self.__timerSound = None
        if self.__soundManager is not None:
            self.__soundManager.dispossessUI()
            self.__soundManager = None
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
        self.__damageInfoPanel.destroy()
        g_sessionProvider.clearBattleUI()
        if self.__arenaCtrl is not None:
            g_sessionProvider.removeArenaCtrl(self.__arenaCtrl)
            self.__arenaCtrl.clear()
            self.__arenaCtrl = None
        self.__ppSwitcher.destroy()
        self.__leftPlayersPanel.dispossessUI()
        self.__rightPlayersPanel.dispossessUI()
        MessengerEntry.g_instance.gui.invoke('dispossessUI')
        self.__arena = None
        self.__denunciator = None
        g_guiResetters.discard(self.__onRecreateDevice)
        self.__settingsInterface.dispossessUI()
        self.__settingsInterface = None
        if self.__dynSquadListener:
            self.__dynSquadListener.destroy()
            self.__dynSquadListener = None
        BattleWindow.beforeDelete(self)
        event = events.AppLifeCycleEvent
        g_eventBus.handleEvent(event(self.__ns, event.DESTROYED))
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

    def __onPostMortemSwitched(self):
        LogitechMonitor.onScreenChange('postmortem')
        if self.radialMenu is not None:
            self.radialMenu.forcedHide()
        if not g_sessionProvider.getCtx().isPlayerObserver():
            self.__callEx('showPostmortemTips', [1.0, 5.0, 1.0])
        return

    def cursorVisibility(self, callbackId, visible, x=None, y=None, customCall=False, enableAiming=True):
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
        canRespawn = False
        player = BigWorld.player()
        if hasRespawns():
            isVehicleAlive = not g_sessionProvider.getArenaDP().getVehicleInteractiveStats().stopRespawn
            canRespawn = isVehicleAlive
        else:
            isVehicleAlive = getattr(player, 'isVehicleAlive', False)
        isVehicleOverturned = getattr(player, 'isVehicleOverturned', False)
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
            if canRespawn:
                isDeserter = isVehicleAlive and isNotTraining
            else:
                isDeserter = isVehicleAlive and isNotTraining and not isVehicleOverturned
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

    def toggleHelpWindow(self, _):
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

    def __getDynamicSquadsInitParams(self, enableAlly=True, enableEnemy=False, enableButton=True):
        return [isRandomBattle() and enableAlly, enableEnemy, isRandomBattle() and enableButton]

    def __populateData(self):
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
                arenaData.append('#menu:loading/battleTypes/%d' % arena.guiType)
            else:
                arenaData.extend([arena.guiType + 1, '#menu:loading/battleTypes/%d' % arena.guiType])
            myTeamNumber = arenaDP.getNumberOfTeam()
            getTeamName = g_sessionProvider.getCtx().getTeamName
            arenaData.extend([getTeamName(myTeamNumber), getTeamName(arenaDP.getNumberOfTeam(enemy=True))])
            teamHasBase = 1 if isBaseExists(BigWorld.player().arenaTypeID, myTeamNumber) else 2
            if not isFalloutBattle():
                typeEvent = 'normal'
                winText = getBattleSubTypeWinText(BigWorld.player().arenaTypeID, teamHasBase)
            else:
                typeEvent = 'fallout'
                if isFalloutMultiTeam():
                    winText = i18n.makeString(ARENAS.TYPE_FALLOUTMUTLITEAM_DESCRIPTION)
                else:
                    winText = i18n.makeString('#arenas:type/%s/description' % arenaSubType)
            arenaData.append(winText)
            arenaData.append(typeEvent)
            arenaData.extend(_getQuestsTipData(arena, arenaDP))
            arenaData.extend([_SMALL_MAP_SOURCE % arena.arenaType.geometryName])
        self.__callEx('arenaData', arenaData)

    def __onRecreateDevice(self, scale=None):
        params = list(GUI.screenResolution())
        params.append(g_settingsCore.interfaceScale.get())
        self.call('Stage.Update', params)
        self.__markersManager.updateMarkersScale()

    def invalidateGUI(self):
        arenaCtrl = getattr(self, '_Battle__arenaCtrl', None)
        if arenaCtrl is not None:
            arenaCtrl.invalidateGUI()
        return

    def __callEx(self, funcName, args=None):
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

    def getVehicleNameLength(self, isEnemy):
        panel = self.rightPlayersPanel if isEnemy else self.leftPlayersPanel
        return panel.getVehicleNameLength()

    def getTeamBasesPanel(self):
        return self.__teamBasesPanel

    def getBattleTimer(self):
        return self.__timersBar

    def getPreBattleTimer(self):
        return self.__timersBar

    def getConsumablesPanel(self):
        return self.__consumablesPanel

    def getDamagePanel(self):
        return self.__damagePanel

    def getMarkersManager(self):
        return self.__markersManager

    def getVErrorsPanel(self):
        return self.__vErrorsPanel

    def getVMsgsPanel(self):
        return self.__vMsgsPanel

    def getPMsgsPanel(self):
        return self.__pMsgsPanel

    def getMinimap(self):
        return self.__minimap

    def getRadialMenu(self):
        return self.__radialMenu

    def getDamageInfoPanel(self):
        return self.__damageInfoPanel

    def getFragCorrelation(self):
        return self.__fragCorrelation

    def getStatsForm(self):
        return self.__statsForm

    def getLeftPlayersPanel(self):
        return self.__leftPlayersPanel

    def getRightPlayersPanel(self):
        return self.__rightPlayersPanel

    def getRibbonsPanel(self):
        return self.__ribbonsPanel

    def getPlayersPanelsSwitcher(self):
        return self.__ppSwitcher

    def getIndicators(self):
        return self.__indicators

    def getDebugPanel(self):
        return self.__debugPanel


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
                            if not v.isPlayerVehicle:
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
