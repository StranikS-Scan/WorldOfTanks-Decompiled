# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/Battle.py
# Compiled at: 2019-02-28 17:28:16
import GUI, BigWorld, ResMgr, weakref, Avatar, FMOD
from account_helpers.AccountSettings import AccountSettings
import constants
import CommandMapping
from gui.Scaleform.Flash import Flash
from windows import BattleWindow
from SettingsInterface import SettingsInterface
from debug_utils import LOG_CURRENT_EXCEPTION, LOG_DEBUG, LOG_ERROR
from gui import DEPTH_OF_Battle, DEPTH_OF_VehicleMarker, TANKMEN_ROLES_ORDER_DICT
from gui.BattleContext import g_battleContext, PLAYER_ENTITY_NAME
from helpers import i18n
from helpers.i18n import makeString
from PlayerEvents import g_playerEvents
from battle_heroes import ACHIEVEMENT_TEXTS as heroesTexts, ACHIEVEMENT_NAMES as heroesNames
from gui.Scaleform.utils.sound import Sound
from gui.Scaleform.utils.functions import getBattleSubTypeBaseNumder, isPontrolPointExists
from MemoryCriticalController import g_critMemHandler
from items.vehicles import NUM_EQUIPMENT_SLOTS, VEHICLE_CLASS_TAGS
from messenger.gui import MessengerDispatcher
from messenger.wrappers import UserWrapper
from gui.Scaleform import VoiceChatInterface, ColorSchemeManager, FEATURES
from gui.Scaleform.Minimap import Minimap
from gui.Scaleform.CursorDelegator import g_cursorDelegator
from gui.Scaleform.ingame_help import IngameHelp
import BattleReplay
from gui.Scaleform.SoundManager import SoundManager
from gui.Scaleform import VehicleActions
_CONTOUR_ICONS_MASK = '../maps/icons/vehicle/contour/%(unicName)s.tga'
_BASE_CAPTURE_SOUND_NAME_ENEMY = '/GUI/notifications_FX/base_capture_2'
_BASE_CAPTURE_SOUND_NAME_ALLY = '/GUI/notifications_FX/base_capture_1'

class Battle(BattleWindow):
    PLAYERS_PANEL_LENGTH = 15
    teamBasesPanel = property(lambda self: self.__teamBasesPanel)
    consumablesPanel = property(lambda self: self.__consumablesPanel)
    damagePanel = property(lambda self: self.__damagePanel)
    vMarkersManager = property(lambda self: self.__vMarkersManager)
    vErrorsPanel = property(lambda self: self.__vErrorsPanel)
    vMsgsPanel = property(lambda self: self.__vMsgsPanel)
    pMsgsPanel = property(lambda self: self.__pMsgsPanel)
    minimap = property(lambda self: self.__minimap)
    damageInfoPanel = property(lambda self: self.__damageInfoPanel)
    VEHICLE_DESTROY_TIMER = {'ALL': 'all',
     constants.VEHICLE_MISC_STATUS.VEHICLE_WILL_DROWN: 'drown',
     constants.VEHICLE_MISC_STATUS.VEHICLE_IS_OVERTURNED: 'overturn',
     constants.VEHICLE_MISC_STATUS.IN_DEATH_ZONE: 'death_zone'}
    _speakPlayers = {}
    __cameraVehicleID = -1

    def __init__(self):
        self.__timerCallBackId = None
        self.__vehicles = {}
        self.__arena = BigWorld.player().arena
        self.__playersPanelStateChanged = False
        BattleWindow.__init__(self, 'battle.swf')
        self.__soundManager = None
        self.__timerSound = Sound('/GUI/notifications_FX/timer')
        self.__isTimerVisible = False
        self.component.wg_inputKeyMode = 1
        self.component.position.z = DEPTH_OF_Battle
        self.movie.backgroundAlpha = 0
        self.addFsCallbacks({'battle.leave': self.onExitBattle})
        self.addExternalCallbacks({'battle.showCursor': self.cursorVisibility,
         'Battle.UsersRoster.AppealOffend': self.onDenunciationInsult,
         'Battle.UsersRoster.AppealNotFairPlay': self.onDenunciationNotFairPlay,
         'Battle.UsersRoster.AppealTeamkill': self.onDenunciationTeamKill,
         'Battle.UsersRoster.AppealBot': self.onDenunciationBot,
         'Battle.playersPanelStateChange': self.onPlayersPanelStateChange})
        BigWorld.wg_setRedefineKeysMode(False)
        self.onPostmortemVehicleChanged(BigWorld.player().playerVehicleID)
        return

    def showAll(self, isShow):
        self.call('battle.showAll', [isShow])
        self.__vMarkersManager.active(isShow)

    def showCursor(self, isShow):
        self.cursorVisibility(-1, isShow)

    def onPlayersPanelStateChange(self, cid, state):
        ppSettings = dict(AccountSettings.getSettings('players_panel'))
        ppSettings['state'] = state
        AccountSettings.setSettings('players_panel', ppSettings)
        self.__playersPanelStateChanged = True

    def onDenunciationInsult(self, cid, uid, userName):
        self.__makeDenunciation(uid, userName, constants.DENUNCIATION.INSULT)

    def onDenunciationNotFairPlay(self, cid, uid, userName):
        self.__makeDenunciation(uid, userName, constants.DENUNCIATION.NOT_FAIR_PLAY)

    def onDenunciationTeamKill(self, cid, uid, userName):
        self.__makeDenunciation(uid, userName, constants.DENUNCIATION.TEAMKILL)

    def onDenunciationBot(self, cid, uid, userName):
        self.__makeDenunciation(uid, userName, constants.DENUNCIATION.BOT)

    def __makeDenunciation(self, uid, userName, topicID):
        player = BigWorld.player()
        violatorKind = constants.VIOLATOR_KIND.UNKNOWN
        for id, p in player.arena.vehicles.iteritems():
            if p['accountDBID'] == uid:
                violatorKind = constants.VIOLATOR_KIND.ALLY if player.team == p['team'] else constants.VIOLATOR_KIND.ENEMY

        player.makeDenunciation(uid, topicID, violatorKind)
        self.__updatePlayers()
        topicStr = makeString('#menu:denunciation/type%d' % topicID)
        MessengerDispatcher.g_instance.currentWindow.showActionFailureMessage(makeString('#system_messages:denunciation/success') % (userName, topicStr))

    def onPostmortemVehicleChanged(self, id):
        self.__cameraVehicleID = id
        self.__updatePlayers()

    def setVehicleTimer(self, code, time):
        if time > 0:
            self.call('destroyTimer.show', [self.VEHICLE_DESTROY_TIMER[code], time])
        else:
            self.call('destroyTimer.hide', [self.VEHICLE_DESTROY_TIMER[code]])

    def onHideVehicleDestroyTimers(self, *args):
        self.call('destroyTimer.hide', [self.VEHICLE_DESTROY_TIMER['ALL']])

    def speakingPlayersReset(self):
        for id in self._speakPlayers.keys():
            self.setPlayerSpeaking(id, False)

        self._speakPlayers.clear()

    def setVisible(self, bool):
        LOG_DEBUG('[Battle] visible', bool)
        self.component.visible = bool

    def afterCreate(self):
        LOG_DEBUG('[Battle] afterCreate')
        setattr(self.movie, '_global.wg_isShowLanguageBar', constants.SHOW_LANGUAGE_BAR)
        setattr(self.movie, '_global.wg_isShowVoiceChat', FEATURES.VOICE_CHAT)
        BattleWindow.afterCreate(self)
        g_playerEvents.onBattleResultsReceived += self.__showFinalStatsResults
        usersManager = MessengerDispatcher.g_instance.users
        usersManager.onUsersRosterUpdate += self.__updatePlayers
        usersManager.onUsersRosterReceived += self.__updatePlayers
        BigWorld.wg_setScreenshotNotifyCallback(self.__screenshotNotifyCallback)
        BigWorld.player().inputHandler.onPostmortemVehicleChanged += self.onPostmortemVehicleChanged
        AccountSettings.onSettingsChanging += self.__accs_onSettingsChanged
        if self.__arena:
            self.__arena.onPeriodChange += self.__onSetArenaTime
            self.__arena.onNewVehicleListReceived += self.__updatePlayers
            self.__arena.onNewStatisticsReceived += self.__updatePlayers
            self.__arena.onVehicleAdded += self.__updatePlayers
            self.__arena.onVehicleStatisticsUpdate += self.__updatePlayers
            self.__arena.onVehicleKilled += self.__updatePlayers
            self.__arena.onVehicleKilled += self.onHideVehicleDestroyTimers
            self.__arena.onAvatarReady += self.__updatePlayers
            self.__arena.onTeamKiller += self.__onTeamKiller
            self.__arena.onVehicleUpdated += self.__updatePlayers
        self.proxy = weakref.proxy(self)
        self._speakPlayers.clear()
        VoiceChatInterface.g_instance.populateUI(self.proxy)
        self.colorManager = ColorSchemeManager._ColorSchemeManager()
        self.colorManager.populateUI(self.proxy)
        self.__settingsInterface = SettingsInterface()
        self.__settingsInterface.populateUI(self.proxy)
        self.__teamBasesPanel = TeamBasesPanel(self.proxy)
        self.__fragCorrelation = FragCorrelationPanel(self.proxy)
        self.__debugPanel = DebugPanel(self.proxy)
        self.__consumablesPanel = ConsumablesPanel(self.proxy)
        self.__damagePanel = DamagePanel(self.proxy)
        self.__vMarkersManager = VehicleMarkersManager(self.proxy)
        self.__ingameHelp = IngameHelp(self.proxy)
        self.__minimap = Minimap(self.proxy)
        self.__soundManager = SoundManager()
        self.__soundManager.populateUI(self.proxy)
        self.__damageInfoPanel = VehicleDamageInfoPanel(self.proxy)
        isColorBlind = AccountSettings.getSettings('isColorBlind')
        self.__vErrorsPanel = FadingMessagesPanel(self.proxy, 'VehicleErrorsPanel', 'gui/vehicle_errors_panel.xml', isColorBlind=isColorBlind)
        self.__vMsgsPanel = FadingMessagesPanel(self.proxy, 'VehicleMessagesPanel', 'gui/vehicle_messages_panel.xml', isColorBlind=isColorBlind)
        self.__pMsgsPanel = FadingMessagesPanel(self.proxy, 'PlayerMessagesPanel', 'gui/player_messages_panel.xml', isColorBlind=isColorBlind)
        MessengerDispatcher.g_instance.battleMessenger.updateColors(isColorBlind=isColorBlind)
        self.__teamBasesPanel.start()
        self.__debugPanel.start()
        self.__consumablesPanel.start()
        self.__damagePanel.start()
        self.__ingameHelp.start()
        self.__vErrorsPanel.start()
        self.__vMsgsPanel.start()
        self.__pMsgsPanel.start()
        self.__vMarkersManager.start()
        self.__vMarkersManager.setMarkerDuration(FEATURES.MARKER_HIT_SPLASH_DURATION)
        self.__vMarkersManager.setMarkerSettings(AccountSettings.getSettings('markers'))
        self.__initMemoryCriticalHandlers()
        MessengerDispatcher.g_instance.battleMessenger.start(self.proxy)
        from game import g_guiResetters
        g_guiResetters.add(self.__onRecreateDevice)
        from game import g_repeatKeyHandlers
        g_repeatKeyHandlers.add(self.component.handleKeyEvent)
        self.__onRecreateDevice()
        self.__setPlayerInfo()
        self.__updatePlayers()
        self.__populateData()
        self.__minimap.start()
        VoiceChatInterface.g_instance.onVoiceChatInitFailed += self.onVoiceChatInitFailed
        BigWorld.callback(1, self.__setArenaTime)
        self.updateFlagsColor()
        self.movie.setFocussed()
        if self.__arena.period == constants.ARENA_PERIOD.BATTLE:
            self.call('players_panel.setState', [AccountSettings.getSettings('players_panel')['state']])
        else:
            self.call('players_panel.setState', ['large'])

    def beforeDelete(self):
        LOG_DEBUG('[Battle] beforeDelete')
        self.__destroyMemoryCriticalHandlers()
        if self.colorManager:
            self.colorManager.dispossessUI()
        if VoiceChatInterface.g_instance:
            VoiceChatInterface.g_instance.dispossessUI()
        if self.component:
            from game import g_repeatKeyHandlers
            g_repeatKeyHandlers.discard(self.component.handleKeyEvent)
        AccountSettings.onSettingsChanging -= self.__accs_onSettingsChanged
        self.__teamBasesPanel.destroy()
        self.__debugPanel.destroy()
        self.__consumablesPanel.destroy()
        self.__damagePanel.destroy()
        self.__vMarkersManager.destroy()
        self.__ingameHelp.destroy()
        self.__vErrorsPanel.destroy()
        self.__vMsgsPanel.destroy()
        self.__pMsgsPanel.destroy()
        self.__minimap.destroy()
        if self.__soundManager:
            self.__soundManager.dispossessUI()
            self.__soundManager = None
        self.__timerSound.stop()
        MessengerDispatcher.g_instance.battleMessenger.destroy()
        BattleWindow.beforeDelete(self)
        g_playerEvents.onBattleResultsReceived -= self.__showFinalStatsResults
        usersManager = MessengerDispatcher.g_instance.users
        usersManager.onUsersRosterUpdate -= self.__updatePlayers
        usersManager.onUsersRosterReceived -= self.__updatePlayers
        if self.__arena:
            self.__arena.onPeriodChange -= self.__onSetArenaTime
            self.__arena.onNewVehicleListReceived -= self.__updatePlayers
            self.__arena.onNewStatisticsReceived -= self.__updatePlayers
            self.__arena.onVehicleAdded -= self.__updatePlayers
            self.__arena.onVehicleStatisticsUpdate -= self.__updatePlayers
            self.__arena.onVehicleKilled -= self.__updatePlayers
            self.__arena.onVehicleKilled -= self.onHideVehicleDestroyTimers
            self.__arena.onAvatarReady -= self.__updatePlayers
            self.__arena.onTeamKiller -= self.__onTeamKiller
            self.__arena.onVehicleUpdated -= self.__updatePlayers
        self.__arena = None
        VoiceChatInterface.g_instance.onVoiceChatInitFailed -= self.onVoiceChatInitFailed
        from game import g_guiResetters
        g_guiResetters.discard(self.__onRecreateDevice)
        self.__settingsInterface.dispossessUI()
        self.__settingsInterface = None
        return

    def __screenshotNotifyCallback(self, path):
        self.vMsgsPanel.showMessage('SCREENSHOT_CREATED', {'path': path.encode('utf-8')})

    def onVoiceChatInitFailed(self):
        if FEATURES.VOICE_CHAT:
            self.call('VoiceChat.initFailed', [])

    def clearCommands(self):
        pass

    def bindCommands(self):
        self.__consumablesPanel.bindCommands()
        self.__ingameHelp.buildCmdMapping()

    def updateFlagsColor(self):
        scheme = 'color_blind' if AccountSettings.getSettings('isColorBlind') else 'default'
        LOG_DEBUG('Set flags color scheme: %s' % scheme)
        color = self.colorManager.getScheme('flag_team_blue').get('default').get('rgba')
        BigWorld.wg_setFlagColor(1, color / 255)
        color = self.colorManager.getScheme('flag_team_red').get(scheme).get('rgba')
        BigWorld.wg_setFlagColor(2, color / 255)

    def setPlayerSpeaking(self, accountDBID, flag):
        if not FEATURES.VOICE_CHAT:
            return
        self._speakPlayers[accountDBID] = flag
        self.__callEx('setPlayerSpeaking', [accountDBID, flag])
        vID = g_battleContext.getVehIDByAccDBID(accountDBID)
        if vID > 0:
            self.__vMarkersManager.showDynamic(vID, flag)

    def isPlayerSpeaking(self, accountDBID):
        if FEATURES.VOICE_CHAT:
            return self._speakPlayers.get(accountDBID, False)
        else:
            return False

    def showPostmortemTips(self):
        self.__callEx('showPostmortemTips', [1.0, 5.0, 1.0])

    def cursorVisibility(self, callbackId, visible):
        if visible:
            g_cursorDelegator.syncMousePosition(self)
        else:
            g_cursorDelegator.restoreMousePosition()
        if BigWorld.player() is not None:
            BigWorld.player().setForcedGuiControlMode(visible, False)
        return

    def onExitBattle(self, arg):
        LOG_DEBUG('onExitBattle')
        arena = getattr(BigWorld.player(), 'arena', None)
        if arena:
            BigWorld.player().leaveArena()
        return

    def __setPlayerInfo(self):
        player = BigWorld.player()
        playerName, vTypeName = ('', '')
        if player:
            vID = player.playerVehicleID
            vInfo = self.__arena.vehicles.get(vID)
            if vInfo is not None:
                playerName = g_battleContext.getFullPlayerName(vInfo, showVehShortName=False)
                vTypeName = vInfo['vehicleType'].type.userString
        self.__callEx('setPlayerInfo', [playerName, vTypeName])
        return

    def __populateData(self):
        from account_helpers.AccountPrebattle import AccountPrebattle
        from gui.Scaleform.utils.functions import getArenaSubTypeID, getBattleSubTypeWinText, getArenaSubTypeName
        arena = getattr(BigWorld.player(), 'arena', None)
        arenaData = ['',
         0,
         '',
         '',
         '']
        if arena:
            arenaData = [arena.typeDescriptor.name]
            descExtra = AccountPrebattle.getPrebattleDescription(arena.extraData or {})
            arenaSubType = getArenaSubTypeName(BigWorld.player().arenaTypeID)
            if descExtra:
                arenaData.extend([arena.guiType + 1, descExtra])
            elif arena.guiType == constants.ARENA_GUI_TYPE.RANDOM:
                arenaData.extend([arenaSubType, '#arenas:type/%s/name' % arenaSubType])
            else:
                arenaData.extend([arena.guiType + 1, '#menu:loading/battleTypes/%d' % arena.guiType])
            if not arena.extraData:
                extraData = {}
                myTeam = BigWorld.player().team
                team1 = extraData.get('opponents', {}).get('%s' % myTeam, {}).get('name', '#menu:loading/team1')
                team2 = extraData.get('opponents', {}).get('2' if myTeam == 1 else '1', {}).get('name', '#menu:loading/team2')
                arenaData.extend([team1, team2])
                winText = getBattleSubTypeWinText(BigWorld.player().arenaTypeID)
                winText = getArenaSubTypeID(BigWorld.player().arenaTypeID) == constants.ARENA_GAMEPLAY_TYPE.TYPE_2 and winText + '%d' % myTeam
            arenaData.append(winText)
        self.__callEx('arenaData', arenaData)
        return

    def __updatePlayers(self, *args):
        stat = {1: [],
         2: []}
        squads = {1: {},
         2: {}}
        player = BigWorld.player()
        if player is None or type(player) != Avatar.PlayerAvatar:
            return
        elif self.__arena is None:
            return
        else:
            vehicles = self.__arena.vehicles
            usersManager = MessengerDispatcher.g_instance.users
            for vId, vData in vehicles.items():
                team = vData['team']
                if vData['name'] is not None:
                    name = vData['name']
                    user = usersManager.getUser(vData['accountDBID'], vData['name'])
                else:
                    name = makeString('#ingame_gui:players_panel/unknown_name')
                    user = UserWrapper()
                if vData['vehicleType'] is not None:
                    vName = vData['vehicleType'].type.userString
                    vShortName = vData['vehicleType'].type.shortUserString
                    vIcon = _CONTOUR_ICONS_MASK % {'unicName': vData['vehicleType'].type.name.replace(':', '-')}
                    balanceWeight = vData['vehicleType'].balanceWeight
                    vLevel = vData['vehicleType'].level
                else:
                    vName = vShortName = makeString('#ingame_gui:players_panel/unknown_vehicle')
                    vIcon = _CONTOUR_ICONS_MASK % {'unicName': 'unknown'}
                    balanceWeight = 0.0
                    vLevel = -1
                isAlive = vData['isAlive']
                isAvatarReady = vData['isAvatarReady']
                vState = 0
                if isAlive:
                    vState |= 1
                if isAvatarReady:
                    vState |= 2
                if isAlive is None or isAvatarReady is None:
                    vState = 4
                if vData['prebattleID'] > 0:
                    if vData['prebattleID'] not in squads[team].keys():
                        squads[team][vData['prebattleID']] = 1
                    else:
                        squads[team][vData['prebattleID']] += 1
                vStats = self.__arena.statistics.get(vId, None)
                frags = 0 if vStats is None else vStats['frags']
                if vData['clanAbbrev']:
                    userDisplayName = name + '[%s]' % vData['clanAbbrev']
                else:
                    userDisplayName = name
                self.__vehicles.update({vId: (userDisplayName, vName)})
                vehActions = VehicleActions.getBitMask(vData.get('actions', {}))
                stat[team].append([name,
                 vIcon,
                 vShortName,
                 vState,
                 frags,
                 vId,
                 vData['prebattleID'],
                 vData['clanAbbrev'],
                 VoiceChatInterface.g_instance.isPlayerSpeaking(vData['accountDBID']),
                 user.uid,
                 user.roster,
                 user.isMuted(),
                 0,
                 False,
                 vData['isTeamKiller'],
                 vLevel,
                 vehActions,
                 not isAlive,
                 balanceWeight])

            squadsSorted = {1: sorted(squads[1].iteritems(), cmp=lambda x, y: cmp(x[0], y[0])),
             2: sorted(squads[2].iteritems(), cmp=lambda x, y: cmp(x[0], y[0]))}
            squadsFiltered = {1: [ id for id, num in squadsSorted[1] if 1 < num < 4 and self.__arena.guiType == constants.ARENA_GUI_TYPE.RANDOM ],
             2: [ id for id, num in squadsSorted[2] if 1 < num < 4 and self.__arena.guiType == constants.ARENA_GUI_TYPE.RANDOM ]}
            teamFrags = [0, 0]
            for team in (1, 2):
                if player.fogOfWar & 4:
                    isUnknownEnemies = team != player.team
                    value = ['team%d' % team,
                     -1,
                     -1,
                     BigWorld.player().denunciationsLeft,
                     AccountSettings.getSettings('isColorBlind'),
                     None]
                    data = sorted(stat[team], cmp=_playerComparator)
                    for item in data:
                        teamFrags[team - 1] += item[4]
                        sNumber = squadsFiltered[team].index(item[6]) + 1 if item[6] in squadsFiltered[team] else 0
                        item[6] = sNumber
                        if item[5] == player.playerVehicleID and item[6] > 0:
                            value[2] = item[6]
                        value.extend(item[:-4])
                        if team != player.team:
                            value[-1] = False
                        value.append(self.__cameraVehicleID == item[5])
                        value.append(item[15] if AccountSettings.getSettings('players_panel')['showLevels'] else 0)
                        value.append(item[16])

                    value[1] = team == player.team and player.playerVehicleID
                self.__callEx('setTeam', value)

            playerTeam = player.team - 1
            enemyTeam = 1 - playerTeam
            self.__fragCorrelation.updateFrags(teamFrags[playerTeam], teamFrags[enemyTeam])
            return

    def __showFinalStatsResults(self, isActiveVehicle, vehInvID, results):
        if isActiveVehicle:
            if not self.__vehicles:
                self.__updatePlayers()
            if results['killerID']:
                killer = makeString('#ingame_gui:statistics/final/lifeInfo/dead', '%s (%s)' % self.__vehicles.get(results['killerID'], ('n/a', 'n/a')))
            else:
                killer = makeString('#ingame_gui:statistics/final/lifeInfo/alive')
            isMultipliedXP = int(results['factors']['dailyXPFactor10'] / 10.0) > 1 and results['xp'] > 0
            stats = [results['xp'],
             results['credits'],
             results['repair'],
             isMultipliedXP,
             i18n.makeString('#ingame_gui:statistics/final/stats/multipliedExp') % int(results['factors']['dailyXPFactor10'] / 10.0) if isMultipliedXP else i18n.makeString('#ingame_gui:statistics/final/stats/experience'),
             self.__vehicles.get(BigWorld.player().playerVehicleID, ('n/a', 'n/a'))[0],
             killer]
            results['damaged'] = list(set(results['damaged']).difference(set(results['killed'])))
            for key in ('killed', 'damaged', 'spotted'):
                lt = set()
                for id in results[key]:
                    lt.add('%s (%s)' % self.__vehicles.get(id, ('n/a', 'n/a')))

                stats.append(len(lt))
                stats.extend(lt)

            hl = set()
            if results.has_key('achieveIndices'):
                for i, heroId in enumerate(results['achieveIndices']):
                    herolist = [makeString(heroesTexts[heroesNames[heroId]])]
                    if results.has_key('heroVehicleIDs') and len(results['heroVehicleIDs']) > i:
                        if self.__arena.vehicles.get(results['heroVehicleIDs'][i], False):
                            if not self.__arena.vehicles[results['heroVehicleIDs'][i]]['isAlive']:
                                herolist[0] += ' ' + makeString('#ingame_gui:statistics/final/personal/postmortem')
                        herolist.extend(self.__vehicles.get(results['heroVehicleIDs'][i], ('n/a', 'n/a')))
                        hl.add('%s - %s (%s)' % tuple(herolist))

            stats.append(len(hl))
            stats.extend(hl)
            for key in ('shots', 'hits', 'shotsReceived'):
                stats.append(makeString('#ingame_gui:statistics/final/personal/' + key, results[key]))

            for key in ('capturePoints', 'droppedCapturePoints'):
                stats.append(makeString('#ingame_gui:statistics/final/personal/' + key, min(results[key], 100)))

            self.__callEx('showFinalStatistic', stats)

    def __showFinalStats(self, winnerTeam, reason):
        if hasattr(BigWorld.player(), 'team'):
            status = 'tie' if winnerTeam == 0 else ('win' if winnerTeam == BigWorld.player().team else 'lose')
            if reason == 1:
                reason = makeString('#ingame_gui:statistics/final/reasons/reason%d%s' % (reason, status))
            else:
                reason = makeString('#ingame_gui:statistics/final/reasons/reason%d' % reason)
            status = makeString('#ingame_gui:statistics/final/status/%s' % status, reason)
            self.__callEx('showStatus', [status])

    def __onSetArenaTime(self, *args):
        if self.__timerCallBackId is not None:
            BigWorld.cancelCallback(self.__timerCallBackId)
        self.__setArenaTime()
        return

    def __setArenaTime(self):
        self.__timerCallBackId = None
        if self.__arena is None:
            return
        else:
            replayCtrl = BattleReplay.g_replayCtrl
            if replayCtrl.isPlaying:
                period = replayCtrl.getArenaPeriod()
                arenaLength = int(replayCtrl.getArenaLength())
                if period == 0:
                    self.__timerCallBackId = BigWorld.callback(1, self.__setArenaTime)
                    return
            else:
                period = self.__arena.period
                arenaLength = int(self.__arena.periodEndTime - BigWorld.serverTime())
                arenaLength = arenaLength if arenaLength > 0 else 0
                if replayCtrl.isRecording:
                    replayCtrl.setArenaPeriod(period)
                    replayCtrl.setArenaLength(arenaLength)
            self.__callEx('timerBar.setTotalTime', [arenaLength])
            if period == constants.ARENA_PERIOD.WAITING:
                self.__callEx('timerBig.setTimer', [makeString('#ingame_gui:timer/waiting')])
                self.__isTimerVisible = True
            elif period == constants.ARENA_PERIOD.PREBATTLE:
                self.__callEx('timerBig.setTimer', [makeString('#ingame_gui:timer/starting'), arenaLength])
                self.__isTimerVisible = True
                if not self.__timerSound.isPlaying and not replayCtrl.isPlaying:
                    self.__timerSound.play()
            elif period == constants.ARENA_PERIOD.BATTLE and self.__isTimerVisible:
                self.__isTimerVisible = False
                self.__timerSound.stop()
                self.__callEx('timerBig.setTimer', [makeString('#ingame_gui:timer/started')])
                self.__callEx('timerBig.hide')
                if not self.__playersPanelStateChanged:
                    self.call('players_panel.setState', [AccountSettings.getSettings('players_panel')['state']])
            elif period == constants.ARENA_PERIOD.AFTERBATTLE:
                self.__showFinalStats(*self.__arena.periodAdditionalInfo)
            if arenaLength > 1 or replayCtrl.isPlaying:
                self.__timerCallBackId = BigWorld.callback(1.0 if not replayCtrl.isPlaying else 0.0, self.__setArenaTime)
            return

    def __onTeamKiller(self, vID):
        self.__updatePlayers(vID)
        self.__vMarkersManager.setTeamKiller(vID)

    def __onRecreateDevice(self):
        self.call('Stage.Update', list(GUI.screenResolution()))

    def __callEx(self, funcName, args=None):
        self.call('battle.' + funcName, args)

    def __initMemoryCriticalHandlers(self):
        for message in g_critMemHandler.messages:
            self.__onMemoryCritical(message)

        g_critMemHandler.onMemCrit += self.__onMemoryCritical

    def __destroyMemoryCriticalHandlers(self):
        g_critMemHandler.onMemCrit -= self.__onMemoryCritical

    def __onMemoryCritical(self, message):
        self.__vMsgsPanel.showMessage(message[1])

    def __accs_onSettingsChanged(self, name):
        LOG_DEBUG('__accs_onSettingsChanging', name)
        if name == 'isColorBlind':
            self.colorManager.update()
            isColorBlind = AccountSettings.getSettings('isColorBlind')
            self.__vErrorsPanel.defineColorFlags(isColorBlind=isColorBlind)
            self.__vMsgsPanel.defineColorFlags(isColorBlind=isColorBlind)
            self.__pMsgsPanel.defineColorFlags(isColorBlind=isColorBlind)
            self.updateFlagsColor()
            self.__vMarkersManager.updateMarkers()
            self.__minimap.updateEntries()
            MessengerDispatcher.g_instance.battleMessenger.updateColors(isColorBlind=isColorBlind)
        if name == 'markers':
            self.vMarkersManager.setMarkerSettings(AccountSettings.getSettings('markers'))
            self.__vMarkersManager.updateMarkerSettings()
        self.__updatePlayers()

    def __getEntityUserString(self, entityName):
        player = BigWorld.player()
        if player and player.isVehicleAlive:
            extra = player.vehicleTypeDescriptor.extrasDict.get(entityName + 'Health')
            if extra is None:
                return entityName
            return extra.deviceUserString
        else:
            return

    def _showTankmanIsSafeMessage(self, entityName):
        if not self.__consumablesPanel.hasMedkit():
            return
        tankman = self.__getEntityUserString(entityName)
        if tankman:
            self.__vErrorsPanel.showMessage('medkitTankmanIsSafe', {'entity': tankman})

    def _showDeviceIsNotDamagedMessage(self, entityName):
        if not self.__consumablesPanel.hasRepairkit():
            return
        if entityName == 'chassis':
            device = i18n.makeString('#ingame_gui:devices/chassis')
        else:
            device = self.__getEntityUserString(entityName)
        if device:
            self.__vErrorsPanel.showMessage('repairkitDeviceIsNotDamaged', {'entity': device})


class TeamBasesPanel(object):
    __settings = {0: {'weight': 2,
         'color': 'red',
         'capturing': i18n.makeString('#ingame_gui:player_messages/ally_base_captured_by_notification'),
         'captured': i18n.makeString('#ingame_gui:player_messages/ally_base_captured_notification')},
     3: {'weight': 1,
         'color': 'green',
         'capturing': i18n.makeString('#ingame_gui:player_messages/enemy_base_captured_by_notification'),
         'captured': i18n.makeString('#ingame_gui:player_messages/enemy_base_captured_notification')},
     'controlPoint': {'weight': 3,
                      'color': {0: 'red',
                                3: 'green'},
                      'capturing': i18n.makeString('#ingame_gui:player_messages/base_captured_by_notification'),
                      'captured': i18n.makeString('#ingame_gui:player_messages/base_captured_notification')}}

    def __init__(self, parentUI):
        self.__ui = parentUI
        self.__captureSounds = {}
        self.__baseIds = set()

    def start(self):
        LOG_DEBUG('TeamBasesPanel.start')
        arena = BigWorld.player().arena
        arena.onTeamBasePointsUpdate += self.__onTeamBasePointsUpdate
        arena.onTeamBaseCaptured += self.__onTeamBaseCaptured
        arena.onPeriodChange += self.__onPeriodChange

    def destroy(self):
        LOG_DEBUG('TeamBasesPanel.destroy')
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

    def __onTeamBasePointsUpdate(self, team, baseID, points, capturingStopped):
        if team not in (1, 2):
            return
        id = self._getID(team, baseID)
        if not points:
            if id in self.__baseIds:
                self.__baseIds.remove(id)
            self.__callFlash('remove', [id])
            self.__stopCaptureSound(team)
        else:
            if id in self.__baseIds:
                self.__callFlash('stop' if capturingStopped else 'updatePoints', [id, points])
            else:
                self.__baseIds.add(id)
                if isPontrolPointExists(BigWorld.player().arenaTypeID):
                    settings = self.__settings.get('controlPoint', {})
                    color = settings.get('color', {}).get(team ^ BigWorld.player().team, 'green')
                else:
                    settings = self.__settings.get(team ^ BigWorld.player().team, {})
                    color = settings.get('color', 'green')
                self.__callFlash('add', [id,
                 settings.get('weight', 0),
                 color,
                 settings.get('capturing', '') % getBattleSubTypeBaseNumder(BigWorld.player().arenaTypeID, team, baseID),
                 points])
                if capturingStopped:
                    self.__callFlash('stop', [id, points])
            if not capturingStopped:
                self.__playCaptureSound(team)
            else:
                self.__stopCaptureSound(team)

    def __onTeamBaseCaptured(self, team, baseID):
        if team not in (1, 2):
            return
        id = self._getID(team, baseID)
        if isPontrolPointExists(BigWorld.player().arenaTypeID):
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
                    snd = FMOD.getSound(_BASE_CAPTURE_SOUND_NAME_ALLY if isAllyTeam else _BASE_CAPTURE_SOUND_NAME_ENEMY)
                    self.__captureSounds[team] = snd
                except Exception:
                    LOG_CURRENT_EXCEPTION()

            return

    def __stopCaptureSound(self, team=None):
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


class VehicleDamageInfoPanel(object):

    def __init__(self, parent):
        self.parent = parent
        self.isShown = False

    def show(self, vehicleID, damagedExtras=[], destroyedExtras=[]):
        if vehicleID not in BigWorld.player().arena.vehicles or not BigWorld.player().arena.vehicles[vehicleID].has_key('vehicleType'):
            return
        extras = BigWorld.player().arena.vehicles[vehicleID]['vehicleType'].extras
        data = [vehicleID, False]
        for i, id in enumerate(damagedExtras):
            if extras[id].name == 'fire':
                data[1] = True
                continue
            data.append({'name': extras[id].name,
             'userName': extras[id].deviceUserString,
             'state': 'damaged'})

        for i, id in enumerate(destroyedExtras):
            data.append({'name': extras[id].name,
             'userName': extras[id].deviceUserString,
             'state': 'destroyed'})

        self.parent.callNice('damageInfoPanel.show', data)
        self.isShown = True

    def hide(self):
        if not self.isShown:
            return
        self.parent.callNice('damageInfoPanel.hide')
        self.isShown = False


class FragCorrelationPanel(object):

    def __init__(self, parentUI):
        self.__ui = parentUI
        _alliedTeamName = i18n.makeString('#ingame_gui:player_messages/allied_team_name')
        _enemyTeamName = i18n.makeString('#ingame_gui:player_messages/enemy_team_name')
        self.__callFlash('setTeamNames', [_alliedTeamName, _enemyTeamName])

    def updateFrags(self, alliedFrags, enemyFrags):
        self.__callFlash('updateFrags', [alliedFrags, enemyFrags])

    def __callFlash(self, funcName, args):
        self.__ui.call('battle.fragCorrelationBar.' + funcName, args)


class DebugPanel(object):
    __UPDATE_INTERVAL = 0.01

    def __init__(self, parentUI):
        self.__ui = parentUI
        self.__timeInterval = None
        return

    def start(self):
        self.__timeInterval = _TimeInterval(self.__UPDATE_INTERVAL, '_DebugPanel__update', weakref.proxy(self))
        self.__timeInterval.start()
        self.__update()

    def destroy(self):
        self.__timeInterval.stop()

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
                isLaggingNow = False
                vehicle = BigWorld.entity(player.playerVehicleID)
                if vehicle is not None and isinstance(vehicle.filter, BigWorld.WGVehicleFilter):
                    isLaggingNow = vehicle.filter.isLaggingNow
                ping = min(BigWorld.LatencyInfo().value[3] * 1000, 999)
                if ping < 999:
                    ping = max(1, ping - 500.0 * constants.SERVER_TICK_LENGTH)
                fps = BigWorld.getFPS()[1]
                if replayCtrl.isRecording:
                    replayCtrl.setFpsPingLag(fps, ping, isLaggingNow)
            self.__ui.call('battle.debugBar.updateInfo', [int(fps),
             int(ping),
             isLaggingNow,
             int(recordedFps)])
            return


class ConsumablesPanel(object):
    __supportedTags = set(('medkit', 'repairkit', 'stimulator', 'trigger', 'fuel', 'extinguisher'))
    __orderSets = {'medkit': TANKMEN_ROLES_ORDER_DICT['enum'],
     'repairkit': ('engine', 'ammoBay', 'gun', 'turretRotator', 'chassis', 'surveyingDevice', 'radio', 'fuelTank')}
    __mergedEntities = {'chassis': ('leftTrack', 'rightTrack')}
    _SHELL_ICON_PATH = '../maps/icons/ammopanel/ammo/%s'
    _NO_SHELL_ICON_PATH = '../maps/icons/ammopanel/ammo/NO_%s'
    _COMMAND_MAPPING_KEY_MASK = 'CMD_AMMO_CHOICE_%d'
    _START_EQUIPMENT_SLOT_IDX = 3

    def __init__(self, parentUI):
        self.__ui = parentUI
        self.__ui.addExternalCallbacks({'battle.consumablesPanel.onClickToSlot': self.onClickToSlot,
         'battle.consumablesPanel.onCollapseEquipment': self.onCollapseEquipment})
        self.__shellKCMap = {}
        self.__equipmentKCMap = {}
        self.__equipmentTagsByIdx = {}
        self.__entitiesKCMap = {}
        self.__expandEquipmentIdx = None
        self.__processedInfo = None
        self.__emptyEquipmentSlotCount = 0
        self.__disableTurretRotator = not vehicleHasTurretRotator(BigWorld.player().vehicleTypeDescriptor)
        return

    def start(self):
        pass

    def destroy(self):
        self.__ui = None
        return

    def setItemQuantityInSlot(self, idx, quantity):
        if self.__equipmentTagsByIdx.has_key(idx):
            self.__equipmentTagsByIdx[idx][1] = quantity
        self.__callFlash('setItemQuantityInSlot', [idx, quantity])

    def setCoolDownTime(self, idx, timeRemaining):
        self.__callFlash('setCoolDownTime', [idx, timeRemaining])

    def setDisabled(self, currentShellIdx):
        self.setCoolDownTime(currentShellIdx, 0)
        self.setCurrentShell(-1)
        self.setNextShell(-1)

    def __getKey(self, idx):
        assert -1 < idx < 10
        cmdMappingKey = self._COMMAND_MAPPING_KEY_MASK % (idx + 1) if idx < 9 else 0
        keyCode = CommandMapping.g_instance.get(cmdMappingKey)
        keyChr = ''
        if keyCode is not None and keyCode != 0:
            keyChr = BigWorld.keyToString(keyCode)
        return (keyCode, keyChr)

    def bindCommands(self):
        shellKCMap = {}
        for idx in self.__shellKCMap.values():
            keyCode, keyChr = self.__getKey(idx)
            shellKCMap[keyCode] = idx
            self.__callFlash('setKeyToSlot', [idx, keyCode, keyChr])

        self.__shellKCMap = shellKCMap
        equipmentKCMap = {}
        for idx in self.__equipmentKCMap.values():
            keyCode, keyChr = self.__getKey(idx)
            equipmentKCMap[keyCode] = idx
            self.__callFlash('setKeyToSlot', [idx, keyCode, keyChr])

        self.__equipmentKCMap = equipmentKCMap

    def setShellQuantityInSlot(self, idx, quantity, quantityInClip):
        if self.__equipmentTagsByIdx.has_key(idx):
            self.__equipmentTagsByIdx[idx][1] = quantity
        self.__callFlash('setShellQuantityInSlot', [idx, quantity, quantityInClip])

    def addShellSlot(self, idx, quantity, quantityInClip, clipCapacity, shellDescr, piercingPower):
        kind = shellDescr['kind']
        icon = shellDescr['icon'][0]
        toolTip = i18n.convert(i18n.makeString('#ingame_gui:shells_kinds/{0:>s}'.format(kind), caliber=shellDescr['caliber'], userString=shellDescr['userString'], damage=str(int(shellDescr['damage'][0])), piercingPower=str(int(piercingPower[0]))))
        shellIconPath = self._SHELL_ICON_PATH % icon
        noShellIconPath = self._NO_SHELL_ICON_PATH % icon
        keyCode, keyChr = self.__getKey(idx)
        self.__shellKCMap[keyCode] = idx
        self.__callFlash('addShellSlot', [idx,
         keyCode,
         keyChr,
         quantity,
         quantityInClip,
         clipCapacity,
         shellIconPath,
         noShellIconPath,
         toolTip])

    def setCurrentShell(self, idx):
        self.__callFlash('setCurrentShell', [idx])

    def setNextShell(self, idx):
        self.__callFlash('setNextShell', [idx])

    def hasMedkit(self):
        for tagName, quantity in self.__equipmentTagsByIdx.values():
            if tagName == 'medkit':
                return quantity > 0

        return False

    def hasRepairkit(self):
        for tagName, quantity in self.__equipmentTagsByIdx.values():
            if tagName == 'repairkit':
                return quantity > 0

        return False

    def checkEquipmentSlotIdx(self, idx):
        return max(self._START_EQUIPMENT_SLOT_IDX, idx)

    def addEquipmentSlot(self, idx, quantity, equipmentDescr):
        tags = self.__supportedTags & equipmentDescr.tags
        tagName = None
        if len(tags) == 1:
            tagName = tags.pop()
        iconPath = equipmentDescr.icon[0]
        toolTip = '{0:>s}\n{1:>s}'.format(equipmentDescr.userString, equipmentDescr.description)
        keyCode, keyChr = (None, None)
        if tagName:
            keyCode, keyChr = self.__getKey(idx)
            self.__equipmentKCMap[keyCode] = idx
            self.__equipmentTagsByIdx[idx] = [tagName, quantity]
        self.__callFlash('addEquipmentSlot', [idx,
         keyCode,
         keyChr,
         tagName,
         quantity,
         iconPath,
         toolTip])
        return

    def addEmptyEquipmentSlot(self, idx):
        self.__emptyEquipmentSlotCount += 1
        toolTip = i18n.makeString('#ingame_gui:consumables_panel/equipment/tooltip/empty')
        self.__callFlash('addEquipmentSlot', [idx,
         None,
         None,
         None,
         0,
         None,
         toolTip])
        if self.__emptyEquipmentSlotCount == NUM_EQUIPMENT_SLOTS:
            self.__callFlash('showEquipmentSlots', [False])
        return

    def expandEquipmentSlot(self, idx, tagName, entityStates):
        orderSet = self.__orderSets.get(tagName, None)
        if orderSet is None:
            if constants.IS_DEVELOPMENT:
                LOG_ERROR('Order set not determine for tag %s' % tagName)
            return
        else:
            self.__expandEquipmentIdx = idx
            self.__processedInfo = (tagName, entityStates)
            args = self.__buildEntitiesInfoList(idx, tagName, entityStates, orderSet)
            self.__callFlash('expandEquipmentSlot', args)
            return

    def updateExpandedEquipmentSlot(self, entityName, entityState):
        if self.__expandEquipmentIdx and self.__processedInfo:
            tagName, entityStates = self.__processedInfo
            if entityStates.has_key(entityName):
                entityStates[entityName] = entityState if entityState != 'repaired' else 'critical'
                self.__processedInfo = (tagName, entityStates)
                idx = self.__expandEquipmentIdx
                orderSet = self.__orderSets[tagName]
                args = self.__buildEntitiesInfoList(idx, tagName, entityStates, orderSet)
                self.__callFlash('updateExpandedEquipmentSlot', args)

    def collapseEquipmentSlot(self, idx):
        self.__callFlash('collapseEquipmentSlot', [idx])

    def __buildEntitiesInfoList(self, idx, tagName, entityStates, orderSet):
        args = [idx, tagName]
        for entityIdx, entityName in enumerate(orderSet):
            entityState, disabled = None, True
            keyCode, keyChr = self.__getKey(entityIdx)
            if self.__mergedEntities.has_key(entityName):
                realName = None
                for name in self.__mergedEntities[entityName]:
                    state = entityStates.get(name, None)
                    disabled &= not entityStates.has_key(name)
                    if realName is None and state == 'critical':
                        realName = name
                        entityState = 'critical'
                    elif state == 'destroyed':
                        realName = name
                        entityState = 'destroyed'
                        break

                if realName is not None:
                    self.__entitiesKCMap[keyCode] = (realName, False)
                else:
                    self.__entitiesKCMap[keyCode] = (entityName, True)
            elif entityStates.has_key(entityName):
                entityState = entityStates[entityName]
                if entityName == 'turretRotator':
                    disabled = self.__disableTurretRotator
                    self.__entitiesKCMap[keyCode] = disabled or (entityName, entityState not in ('destroyed', 'critical'))
            args.extend([keyCode,
             keyChr,
             entityName,
             entityState,
             disabled])

        return args

    def __removeExpandEquipment(self, idx):
        if idx == self.__expandEquipmentIdx:
            self.__expandEquipmentIdx = None
            self.__processedInfo = None
            self.__entitiesKCMap.clear()
        return

    def addOptionalDevice(self, idx, deviceDescr):
        iconPath = deviceDescr.icon[0]
        toolTip = '{0:>s}\n{1:>s}'.format(deviceDescr.userString, deviceDescr.description)
        self.__callFlash('addOptionalDeviceSlot', [idx, iconPath, toolTip])

    def setOptionalDeviceState(self, idx, isOn):
        self.setCoolDownTime(idx, -1 if isOn else 0)

    def handleKey(self, key):
        replayCtrl = BattleReplay.g_replayCtrl
        if replayCtrl.isPlaying:
            return
        elif self.__expandEquipmentIdx is not None:
            if key in self.__entitiesKCMap.keys():
                slotIdx = self.__expandEquipmentIdx
                devName, isNormal = self.__entitiesKCMap[key]
                if not isNormal:
                    self.collapseEquipmentSlot(slotIdx)
                    BigWorld.player().onEquipmentButtonPressed(slotIdx, deviceName=devName)
                else:
                    if self.__processedInfo is None:
                        LOG_ERROR("Can't determine equipment tag", slotIdx, devName)
                        return
                    tagName, _ = self.__processedInfo
                    if tagName == 'medkit':
                        self.__ui._showTankmanIsSafeMessage(devName)
                    elif tagName == 'repairkit':
                        self.__ui._showDeviceIsNotDamagedMessage(devName)
                    else:
                        LOG_ERROR("Can't determine message for tag", tagName)
            return
        else:
            if key in self.__shellKCMap.keys():
                BigWorld.player().onAmmoButtonPressed(self.__shellKCMap[key])
            elif key in self.__equipmentKCMap.keys():
                BigWorld.player().onEquipmentButtonPressed(self.__equipmentKCMap[key])
            return

    def onClickToSlot(self, requestID, keyCode):
        self.handleKey(int(keyCode))

    def onCollapseEquipment(self, requestID, idx):
        self.__removeExpandEquipment(int(idx))

    def __callFlash(self, funcName, args=None):
        self.__ui.call('battle.consumablesPanel.%s' % funcName, args)


class DamagePanel():

    def __init__(self, parentUI):
        self.__ui = parentUI
        self.__hasYawLimits = False
        self.__ui.addExternalCallbacks({'battle.damagePanel.onClickToDeviceIconButon': self.__onClickToDeviceIconButon,
         'battle.damagePanel.onClickToTankmenIconButon': self.__onClickToTankmenIconButon})

    def start(self):
        vTypeDesc = BigWorld.player().vehicleTypeDescriptor
        vType = vTypeDesc.type
        self.__hasYawLimits = vTypeDesc.turret['yawLimits'] is not None
        modulesLayout = not vehicleHasTurretRotator(vTypeDesc)
        tankmensLayout = [ elem[0] for elem in vType.crewRoles ]
        order = TANKMEN_ROLES_ORDER_DICT['plain']
        lastIdx = len(order)

        def comparator(item, other):
            itemIdx = order.index(item) if item in order else lastIdx
            otherIdx = order.index(other) if other in order else lastIdx
            return cmp(itemIdx, otherIdx)

        tankmensLayout = sorted(tankmensLayout, cmp=comparator)
        layout = tankmensLayout + [modulesLayout]
        self.__callFlash('setIconsLayout', layout)
        self.__callFlash('setMaxHealth', [vTypeDesc.maxHealth])
        if self.__hasYawLimits:
            aih = BigWorld.player().inputHandler
            isAutorotation = aih.getAutorotation() if aih is not None else True
            self.onVehicleAutorotationEnabled(isAutorotation)
        return

    def destroy(self):
        self.__ui = None
        self.__hasYawLimits = False
        return

    def updateCriticalIcon(self, type, newState):
        LOG_DEBUG('[updateCriticalIcon] type = %s state = %s' % (type, newState))
        self.__callFlash('updateCriticalIcon', [type, newState])

    def onVehicleDestroyed(self):
        self.__callFlash('onVehicleDestroyed')
        self.__callFlash('onCrewDeactivated')

    def onCrewDeactivated(self):
        self.__callFlash('onCrewDeactivated')

    def onFireInVehicle(self, bool):
        self.__callFlash('onFireInVehicle', [bool])

    def onVehicleAutorotationEnabled(self, value):
        if self.__hasYawLimits:
            self.__callFlash('onVehicleAutorotationEnabled', [value])

    def updateHealth(self, cur):
        self.__callFlash('updateHealth', [cur])

    def __onClickToTankmenIconButon(self, requestID, entityName, entityState):
        if BattleReplay.g_replayCtrl.isPlaying:
            return
        if entityState == 'normal':
            self.__ui._showTankmanIsSafeMessage(entityName)
            return
        BigWorld.player().onDamageIconButtonPressed('medkit', entityName)

    def __onClickToDeviceIconButon(self, requestID, entityName, entityState):
        if BattleReplay.g_replayCtrl.isPlaying:
            return
        if entityState == 'normal':
            self.__ui._showDeviceIsNotDamagedMessage(entityName)
            return
        BigWorld.player().onDamageIconButtonPressed('repairkit', entityName)

    def __callFlash(self, funcName, args=None):
        self.__ui.call('battle.damagePanel.' + funcName, args)


class VehicleMarkersManager(Flash):
    __SWF_FILE_NAME = 'VehicleMarkersManager.swf'

    def __init__(self, parentUI):
        Flash.__init__(self, self.__SWF_FILE_NAME)
        self.component.wg_inputKeyMode = 2
        self.component.position.z = DEPTH_OF_VehicleMarker
        self.movie.backgroundAlpha = 0
        self.colorManager = ColorSchemeManager._ColorSchemeManager()
        self.colorManager.populateUI(weakref.proxy(self))
        self.__ownUI = None
        self.__parentUI = parentUI
        self.__markers = dict()
        return

    def showExtendedInfo(self, value):
        self.__invokeCanvas('setShowExInfoFlag', [value])
        for handle in self.__markers.iterkeys():
            self.__invokeMarker(handle, 'showExInfo', [value])

    def setScaleProps(self, minScale=40, maxScale=100, defScale=100, speed=3.0):
        if constants.IS_DEVELOPMENT:
            self.__ownUI.scaleProperties = (minScale,
             maxScale,
             defScale,
             speed)

    def setAlphaProps(self, minAlpha=40, maxAlpha=100, defAlpha=100, speed=3.0):
        pass

    def start(self):
        self.active(True)
        self.__ownUI = GUI.WGVehicleMarkersCanvasFlash(self.movie)
        self.__ownUI.wg_inputKeyMode = 2
        self.__ownUI.scaleProperties = FEATURES.MARKER_SCALE_SETTINGS
        self.__ownUIProxy = weakref.proxy(self.__ownUI)
        self.__parentUI.component.addChild(self.__ownUI, 'vehicleMarkersManager')

    def destroy(self):
        if self.__parentUI is not None:
            setattr(self.__parentUI.component, 'vehicleMarkersManager', None)
        self.__parentUI = None
        self.__ownUI = None
        self.colorManager.dispossessUI()
        self.close()
        return

    def createMarker(self, vProxy):
        vInfo = dict(vProxy.publicInfo)
        isFriend = vInfo['team'] == BigWorld.player().team
        vehicles = BigWorld.player().arena.vehicles
        vInfoEx = vehicles.get(vProxy.id, {})
        vTypeDescr = vProxy.typeDescriptor
        maxHealth = vTypeDescr.maxHealth
        mProv = vProxy.model.node('HP_gui')
        tags = set(vTypeDescr.type.tags & VEHICLE_CLASS_TAGS)
        vClass = tags.pop() if len(tags) > 0 else ''
        vType = vTypeDescr.type
        vIconSource = _CONTOUR_ICONS_MASK % {'unicName': vType.name.replace(':', '-')}
        entityName = g_battleContext.getPlayerEntityName(vProxy.id, vInfoEx)
        speaking = False
        if FEATURES.VOICE_CHAT:
            speaking = VoiceChatInterface.g_instance.isPlayerSpeaking(vInfoEx.get('accountDBID', 0))
        hunting = VehicleActions.isHunting(vInfoEx.get('actions', {}))
        handle = self.__ownUI.addMarker(mProv, 'VehicleMarkerAlly' if isFriend else 'VehicleMarkerEnemy')
        self.__markers[handle] = _VehicleMarker(vProxy, self.__ownUIProxy, handle)
        self.__invokeMarker(handle, 'init', [vClass,
         vIconSource,
         vType.shortUserString,
         vType.level,
         g_battleContext.getFullPlayerName(vInfoEx, showVehShortName=False),
         vProxy.health,
         maxHealth,
         entityName.name(),
         speaking,
         hunting])
        return handle

    def destroyMarker(self, handle):
        del self.__markers[handle]
        self.__ownUI.delMarker(handle)

    def updateMarkerState(self, handle, newState, isImmediate=False):
        self.__invokeMarker(handle, 'updateState', [newState, isImmediate])

    def showActionMarker(self, handle, newState):
        self.__invokeMarker(handle, 'showActionMarker', [newState])

    def onVehicleHealthChanged(self, handle, curHealth):
        self.__invokeMarker(handle, 'updateHealth', [curHealth])

    def showDynamic(self, vID, flag):
        handle = getattr(BigWorld.entity(vID), 'marker', None)
        if handle is not None and FEATURES.VOICE_CHAT:
            self.__invokeMarker(handle, 'setSpeaking', [flag])
        return

    def setTeamKiller(self, vID):
        handle = getattr(BigWorld.entity(vID), 'marker', None)
        if handle is not None:
            self.__invokeMarker(handle, 'setEntityName', [PLAYER_ENTITY_NAME.teamKiller.name()])
        return

    def __invokeMarker(self, handle, function, args=None):
        if args is None:
            args = []
        self.__ownUI.markerInvoke(handle, (function, args))
        return

    def __invokeCanvas(self, function, args=None):
        if args is None:
            args = []
        self.call('battle.vehicleMarkersCanvas.' + function, args)
        return

    def __invokeCanvasNice(self, function, args=None):
        if args is None:
            args = []
        self.callNice('battle.vehicleMarkersCanvas.' + function, args)
        return

    def setMarkerSettings(self, settings):
        self.__invokeCanvasNice('setMarkerSettings', [settings])

    def setMarkerDuration(self, value):
        self.__invokeCanvas('setMarkerDuration', [value])

    def updateMarkers(self):
        self.colorManager.update()
        for handle in self.__markers.iterkeys():
            self.__invokeMarker(handle, 'update', [])

    def updateMarkerSettings(self):
        for handle in self.__markers.iterkeys():
            self.__invokeMarker(handle, 'updateMarkerSettings', [])


class _VehicleMarker():

    def __init__(self, vProxy, uiProxy, handle):
        self.vProxy = vProxy
        self.uiProxy = uiProxy
        self.handle = handle
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

    def __init__(self, parentUI, name, cfgFileName, isColorBlind=False):
        self.__ui = parentUI
        self.__name = name
        self.__pathPrefix = 'battle.' + name + '.' + '%s'
        self.__readConfig(cfgFileName)
        self.__ui.addExternalCallbacks({'battle.%s.PopulateUI' % name: self.__onPopulateUI})
        self.defineColorFlags(isColorBlind=isColorBlind)

    def start(self):
        self.__callFlash('RefreshUI')

    def destroy(self):
        self.__ui = None
        return

    def defineColorFlags(self, isColorBlind=False):
        self.__colorGroup = 'colorBlind' if isColorBlind else 'default'

    def showMessage(self, key, args=None, extra=None):
        msgText, colors = self.__messageDict.get(key, (None, ''))
        if msgText is None:
            self.__showMessage(key, key, args.get('colorAlias') if args else None)
            return
        else:
            if args is not None:
                self.__formatEntitiesEx(args, extra=extra)
                try:
                    msgText = msgText % args
                except TypeError:
                    LOG_CURRENT_EXCEPTION()

            self.__showMessage(key, msgText, colors.get(self.__colorGroup if self.__colorGroup in colors else 'default'))
            return

    def __showMessage(self, key, msgText, color):
        LOG_DEBUG('%s: show message with key = %s' % (self.__name, key))
        self.__callFlash('ShowMessage', [key, msgText, color])

    def __formatEntitiesEx(self, args, extra=None):
        if extra is None:
            extra = ()
        csManager = self.__ui.colorManager
        for argName, vID in extra:
            arg = args.get(argName)
            rgba = None
            if g_battleContext.isTeamKiller(vID=vID):
                rgba = csManager.getScheme('teamkiller').get(self.__colorGroup, {}).get('rgba')
            elif g_battleContext.isSquadMan(vID=vID):
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
        import re
        srePattern = re.compile('\\_\\(([^)]+)\\)', re.U | re.M)

        def makeString(mutchobj):
            if mutchobj.group(1):
                return i18n.makeString(mutchobj.group(1))

        self.__messageDict = dict()
        for mTag, mSec in sec['messages'].items():
            text = mSec.readString('text')
            text = srePattern.sub(makeString, text)
            aliasesSec = mSec['colorAlias']
            aliases = aliasesSec.items()
            if len(aliases):
                groups = dict(((key, section.asString) for key, section in aliases))
            else:
                groups = {'default': aliasesSec.asString}
            self.__messageDict[mTag] = (text, groups)

        return

    def __callFlash(self, funcName, args=None):
        self.__ui.call(self.__pathPrefix % funcName, args)

    def __onPopulateUI(self, requestId):
        args = [requestId]
        args.extend(self.__settings)
        self.__ui.respond(args)


def _playerComparator(x1, x2):
    if x1[17] < x2[17]:
        return -1
    if x1[17] > x2[17]:
        return 1
    if x1[18] < x2[18]:
        return 1
    if x1[18] > x2[18]:
        return -1
    if x1[2] < x2[2]:
        return -1
    if x1[2] > x2[2]:
        return 1
    if x1[0] < x2[0]:
        return -1
    if x1[0] > x2[0]:
        return 1


class _TimeInterval():

    def __init__(self, interval, funcName, scopeProxy=None):
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
            if funcObj is not None:
                funcObj()
        return


def vehicleHasTurretRotator(vTypeDesc):
    result = True
    if vTypeDesc.type.tags & set(['SPG', 'AT-SPG']) and len(vTypeDesc.hull.get('fakeTurrets', {}).get('battle', ())) > 0:
        result = False
    return result
