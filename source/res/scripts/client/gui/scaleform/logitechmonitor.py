# Embedded file name: scripts/client/gui/Scaleform/LogitechMonitor.py
import BigWorld
from collections import defaultdict
import constants
import CommandMapping
from debug_utils import LOG_DEBUG
from gui.Scaleform.Flash import Flash
from adisp import process
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.battle_control import g_sessionProvider
from gui.battle_control.battle_period_ctrl import getTimeLevel
from items.vehicles import getVehicleType
from gui.Scaleform.framework.entities.EventSystemEntity import EventSystemEntity
from gui.shared import EVENT_BUS_SCOPE, g_itemsCache
from CurrentVehicle import g_currentVehicle
from helpers import i18n, isPlayerAccount
from gui.shared.utils.functions import getArenaSubTypeName
from messenger.m_constants import MESSENGER_SCOPE
from gui.Scaleform.ColorSchemeManager import _ColorSchemeManager
from ConnectionManager import connectionManager
TOTAL_BLOCKS = (('common', (('a15x15', 'battlesCount'),
   ('a15x15', 'wins'),
   ('a15x15', 'losses'),
   ('a15x15', 'survivedBattles'))), ('battleeffect', (('a15x15', 'frags'),
   ('max15x15', 'maxFrags'),
   ('', 'effectiveShots'),
   ('a15x15', 'damageDealt'))), ('credits', (('a15x15', 'xp'), ('', 'avgExperience'), ('max15x15', 'maxXP'))))

def getDossierTotalBlocksSummary(dossier, isCompact = False):
    data = []
    for blockType, fields in TOTAL_BLOCKS:
        for field in fields:
            blockName, fieldType = field
            data.append('#menu:profile/stats/items/' + fieldType)
            data.append(__getData(blockName, fieldType, dossier))
            data.append(__getDataExtra(blockType, blockName, fieldType, dossier, True, isCompact))

    return data


def __getData(blockName, fieldType, dossier):
    if fieldType == 'effectiveShots':
        if dossier['a15x15']['shots'] != 0:
            return '%d%%' % round(float(dossier['a15x15']['directHits']) / dossier['a15x15']['shots'] * 100)
        return '0%'
    if fieldType == 'avgExperience':
        if dossier['a15x15']['battlesCount'] != 0:
            return BigWorld.wg_getIntegralFormat(round(float(dossier['a15x15']['xp']) / dossier['a15x15']['battlesCount']))
        return BigWorld.wg_getIntegralFormat(0)
    return BigWorld.wg_getIntegralFormat(dossier[blockName][fieldType])


def __getDataExtra(blockType, blockName, fieldType, dossier, isTotal = False, isCompact = False):
    extra = ''
    if blockType == 'common':
        if fieldType != 'battlesCount' and dossier['a15x15']['battlesCount'] != 0:
            extra = '(%d%%)' % round(float(dossier[blockName][fieldType]) / dossier['a15x15']['battlesCount'] * 100)
    if isTotal:
        if fieldType == 'maxFrags' and dossier['max15x15']['maxFrags'] != 0:
            extra = getVehicleType(dossier['max15x15']['maxFragsVehicle']).userString if not isCompact else getVehicleType(dossier['max15x15']['maxFragsVehicle']).shortUserString
        if fieldType == 'maxXP' and dossier['max15x15']['maxXP'] != 0:
            extra = getVehicleType(dossier['max15x15']['maxXPVehicle']).userString if not isCompact else getVehicleType(dossier['max15x15']['maxXPVehicle']).shortUserString
    return extra


class _LogitechFlash(Flash, EventSystemEntity):

    def __init__(self, isColored, width, height):
        swf = 'keyboard.swf' if isColored else 'keyboardMono.swf'
        Flash.__init__(self, swf)
        EventSystemEntity.__init__(self)
        self.movie.wg_outputToLogitechLcd = True
        self.addListener(VIEW_ALIAS.LOGIN, self.__showLogoScreen, EVENT_BUS_SCOPE.GLOBAL)
        self.addListener(VIEW_ALIAS.LOBBY, self.__showStatsScreen, EVENT_BUS_SCOPE.GLOBAL)
        self.addListener(VIEW_ALIAS.BATTLE_LOADING, self.__showBattleLoadingScreen, EVENT_BUS_SCOPE.LOBBY)
        self.addListener(VIEW_ALIAS.TUTORIAL_LOADING, self.__showBattleLoadingScreen, EVENT_BUS_SCOPE.LOBBY)
        connectionManager.onDisconnected += self.__onDisconnect

    def beforeDelete(self):
        if self.movie:
            self.movie.wg_outputToLogitechLcd = False
        self.removeListener(VIEW_ALIAS.LOGIN, self.__showLogoScreen, EVENT_BUS_SCOPE.GLOBAL)
        self.removeListener(VIEW_ALIAS.LOBBY, self.__showStatsScreen, EVENT_BUS_SCOPE.GLOBAL)
        self.removeListener(VIEW_ALIAS.BATTLE_LOADING, self.__showBattleLoadingScreen, EVENT_BUS_SCOPE.LOBBY)
        self.removeListener(VIEW_ALIAS.TUTORIAL_LOADING, self.__showBattleLoadingScreen, EVENT_BUS_SCOPE.LOBBY)
        connectionManager.onDisconnected -= self.__onDisconnect
        super(_LogitechFlash, self).beforeDelete()

    def __showStatsScreen(self, event):
        LogitechMonitor.onScreenChange('hangar')

    def __showLogoScreen(self, event):
        LogitechMonitor.onScreenChange('login')

    def __showBattleLoadingScreen(self, event):
        LogitechMonitor.onScreenChange('battleloading')

    def __onDisconnect(self):
        LogitechMonitor.onScreenChange('login')


class _LogitechScreen(object):

    def __init__(self, component, frame):
        self.uiHolder = component
        self.__frameLabel = frame

    def __del__(self):
        LOG_DEBUG('_LogitechScreen::destroy', self)

    def load(self, isColored):
        LOG_DEBUG('Logitech changeScreen: ', self.__frameLabel)
        self.uiHolder.call('logitech.gotoFrame', [self.__frameLabel])
        if not isColored:
            self.onLoadedMono()

    def onLoaded(self):
        pass

    def onLoadedMono(self):
        pass

    def destroy(self, isColored):
        if not isColored:
            self.onUnloadMono()
        self.uiHolder = None
        self.onUnload()
        return

    def onUnload(self):
        pass

    def onUnloadMono(self):
        pass

    def onChangeView(self):
        self.call('logitech.changeView', [])

    def call(self, methodName, args = None):
        self.uiHolder.call(methodName, args)


class _LogoScreen(_LogitechScreen):

    def __init__(self, component):
        super(_LogoScreen, self).__init__(component, 'logo')

    def onLoadedMono(self):
        self.uiHolder.call('logitech.setMonoText', [i18n.makeString('#menu:login/version')])


class _StatsScreen(_LogitechScreen):

    def __init__(self, component):
        super(_StatsScreen, self).__init__(component, 'stats')

    def onLoadedMono(self):
        if g_currentVehicle.item:
            self.onVehicleChange()
        g_currentVehicle.onChanged += self.onVehicleChange

    def onUnloadMono(self):
        g_currentVehicle.onChanged -= self.onVehicleChange

    def onVehicleChange(self):
        self.uiHolder.call('logitech.setMonoText', [g_currentVehicle.item.userName + '\r\n' + i18n.makeString(g_currentVehicle.getHangarMessage()[1])])

    def onLoaded(self):
        dossier = g_itemsCache.items.stats.accountDossier
        self.call('logitech.setStatsData', getDossierTotalBlocksSummary(dossier, isCompact=True))


class _BattleLoadingScreen(_LogitechScreen):
    _MAP_SOURCE = '../maps/icons/map/screen/%s.png'

    def __init__(self, component):
        super(_BattleLoadingScreen, self).__init__(component, 'mapLoading')

    def onLoaded(self):
        arena = getattr(BigWorld.player(), 'arena', None)
        if arena:
            if arena.guiType == constants.ARENA_GUI_TYPE.RANDOM:
                arenaSubType = getArenaSubTypeName(BigWorld.player().arenaTypeID)
                battleType = '#arenas:type/%s/name' % arenaSubType
            else:
                battleType = '#menu:loading/battleTypes/%d' % arena.guiType
            self.call('logitech.setMap', [arena.arenaType.name, battleType, self._MAP_SOURCE % arena.arenaType.geometryName])
        return


class _BattleScreen(_LogitechScreen):
    __viewCmds = ('CMD_CHAT_SHORTCUT_ATTACK', 'CMD_CHAT_SHORTCUT_BACKTOBASE', 'CMD_CHAT_SHORTCUT_POSITIVE', 'CMD_CHAT_SHORTCUT_NEGATIVE', 'CMD_CHAT_SHORTCUT_HELPME', 'CMD_CHAT_SHORTCUT_RELOAD')
    __timerCallBackId = None
    __debugCallBackId = None

    def __init__(self, component, frame = 'battle'):
        super(_BattleScreen, self).__init__(component, frame)
        self._colorManager = None
        return

    def onLoadedMono(self):
        self.onUpdateMono()

    def onUnloadMono(self):
        if self.__timerCallBackId:
            BigWorld.cancelCallback(self.__timerCallBackId)
            self.__timerCallBackId = None
        return

    def onUpdateMono(self):
        self.__timerCallBackId = None
        player = BigWorld.player()
        arena = player.arena if hasattr(player, 'arena') else None
        if not g_sessionProvider.getCtx().isInBattle or arena is None:
            return
        else:
            arenaLength = int(arena.periodEndTime - BigWorld.serverTime())
            arenaLength = arenaLength if arenaLength > 0 else 0
            allayFrags, enemyFrags, _, _ = self.getFrags()
            msg = '%s :%s\n%d :%d\n' % (i18n.makeString('#ingame_gui:player_messages/allied_team_name'),
             i18n.makeString('#ingame_gui:player_messages/enemy_team_name'),
             allayFrags,
             enemyFrags)
            if arena.period == constants.ARENA_PERIOD.BATTLE:
                m, s = divmod(arenaLength, 60)
                msg += '\n%s: %d :%02d' % (i18n.makeString('#ingame_gui:timer/battlePeriod'), m, s)
            self.uiHolder.call('logitech.setMonoText', [msg])
            self.__timerCallBackId = BigWorld.callback(1, self.onUpdateMono)
            return

    def onLoaded(self):
        _alliedTeamName = '#ingame_gui:player_messages/allied_team_name'
        _enemyTeamName = '#ingame_gui:player_messages/enemy_team_name'
        self.call('battle.fragCorrelationBar.setTeamNames', [_alliedTeamName, _enemyTeamName])
        arena = getattr(BigWorld.player(), 'arena', None)
        if not g_sessionProvider.getCtx().isInBattle or arena is None:
            return
        else:
            CommandMapping.g_instance.onMappingChanged += self.setCommands
            self.__updateDebug()
            self.__onSetArenaTime()
            self.__updatePlayers()
            self.setCommands()
            arena.onPeriodChange += self.__onSetArenaTime
            arena.onNewVehicleListReceived += self.__updatePlayers
            arena.onNewStatisticsReceived += self.__updatePlayers
            arena.onVehicleAdded += self.__updatePlayers
            arena.onVehicleStatisticsUpdate += self.__updatePlayers
            arena.onVehicleKilled += self.__updatePlayers
            arena.onAvatarReady += self.__updatePlayers
            self._colorManager = _ColorSchemeManager()
            self._colorManager.populateUI(self.uiHolder)
            return

    def onUnload(self):
        arena = getattr(BigWorld.player(), 'arena', None)
        if not g_sessionProvider.getCtx().isInBattle or arena is None:
            return
        else:
            CommandMapping.g_instance.onMappingChanged -= self.setCommands
            arena.onPeriodChange -= self.__onSetArenaTime
            arena.onNewVehicleListReceived -= self.__updatePlayers
            arena.onNewStatisticsReceived -= self.__updatePlayers
            arena.onVehicleAdded -= self.__updatePlayers
            arena.onVehicleStatisticsUpdate -= self.__updatePlayers
            arena.onVehicleKilled -= self.__updatePlayers
            arena.onAvatarReady -= self.__updatePlayers
            if self.__timerCallBackId:
                BigWorld.cancelCallback(self.__timerCallBackId)
                self.__timerCallBackId = None
            if self.__debugCallBackId:
                BigWorld.cancelCallback(self.__debugCallBackId)
                self.__debugCallBackId = None
            if self._colorManager:
                self._colorManager.dispossessUI()
            _LogitechScreen.onUnload(self)
            return

    def __updatePlayers(self, *args):
        self.call('battle.fragCorrelationBar.updateFrags', list(self.getFrags()))

    def getFrags(self):
        arena = BigWorld.player().arena
        if not g_sessionProvider.getCtx().isInBattle or arena is None:
            return
        else:
            vehicles = arena.vehicles
            frags = defaultdict(int)
            total = defaultdict(int)
            for vId, vData in vehicles.items():
                vStats = arena.statistics.get(vId, None)
                frags[vData['team']] += 0 if vStats is None else vStats['frags']
                total[vData['team']] += 1

            playerTeam = BigWorld.player().team
            playerTeamFrags = frags[playerTeam]
            playerTeamTotalFrags = total[playerTeam]
            enemyTeamsFrags = [ v for t, v in frags.iteritems() if t != playerTeam ]
            enemyTeamsTotalFrags = [ v for t, v in total.iteritems() if t != playerTeam ]
            enemyTeamsFrags = sum(enemyTeamsFrags)
            enemyTeamsTotalFrags = sum(enemyTeamsTotalFrags)
            return (playerTeamFrags,
             enemyTeamsFrags,
             playerTeamTotalFrags,
             enemyTeamsTotalFrags)

    def __onSetArenaTime(self, *args):
        self.__timerCallBackId = None
        arena = getattr(BigWorld.player(), 'arena', None)
        if not g_sessionProvider.getCtx().isInBattle or arena is None:
            return
        else:
            arenaLength = int(arena.periodEndTime - BigWorld.serverTime())
            arenaLength = arenaLength if arenaLength > 0 else 0
            self.call('battle.timerBar.setTotalTime', [getTimeLevel(arenaLength), arenaLength])
            if arenaLength > 1:
                self.__timerCallBackId = BigWorld.callback(1, self.__onSetArenaTime)
            return

    def __updateDebug(self):
        self.__debugCallBackId = None
        player = BigWorld.player()
        if player is None or not hasattr(player, 'playerVehicleID'):
            return
        else:
            isLaggingNow = False
            ping = min(BigWorld.LatencyInfo().value[3] * 1000, 999)
            if ping < 999:
                ping = max(1, ping - 500.0 * constants.SERVER_TICK_LENGTH)
            fps = BigWorld.getFPS()[0]
            self.call('battle.debugBar.updateInfo', [int(fps), int(ping), isLaggingNow])
            self.__debugCallBackId = BigWorld.callback(0.01, self.__updateDebug)
            return

    def setCommands(self, *args):
        cmdMap = CommandMapping.g_instance
        viewCmdMapping = []
        for command in self.__viewCmds:
            key = cmdMap.get(command)
            viewCmdMapping.append(command)
            viewCmdMapping.append(BigWorld.keyToString(key) if key is not None else 'NONE')

        self.call('battle.ingameHelp.setCommandMapping', viewCmdMapping)
        return


class _PostmortemScreen(_BattleScreen):

    def __init__(self, component):
        super(_PostmortemScreen, self).__init__(component, 'postmortem')

    def load(self, isColored):
        _BattleScreen.load(self, isColored)
        if isColored:
            self.onLoaded()

    def setCommands(self):
        self.call('battle.ingameHelp.setCommandMapping', [])


class LogitechBattleMessenger(object):

    def __init__(self):
        self.messenger = None
        return

    def __del__(self):
        LOG_DEBUG('Deleted:', self)

    def create(self, uiHolder):
        from messenger.gui.Scaleform.BattleEntry import BattleEntry
        self.messenger = BattleEntry()
        self.messenger.show()
        self.messenger.enableRecord(False)
        self.messenger.invoke('populateUI', uiHolder)

    def destroy(self):
        self.messenger.close(MESSENGER_SCOPE.UNKNOWN)
        self.messenger.invoke('dispossessUI')
        self.messenger = None
        return


class LogitechMonitor(object):
    __component = None
    __screen = None
    __currentScreen = None
    __messenger = None
    __isColored = False
    SCREEN_TO_FRAME = {'login': _LogoScreen,
     'hangar': _StatsScreen,
     'battleloading': _BattleLoadingScreen,
     'battle': _BattleScreen,
     'postmortem': _PostmortemScreen}
    MESSENGER_IN_SCREEN = ['battle', 'postmortem']

    @staticmethod
    def init():
        LogitechMonitor.onScreenChange('login')
        import LcdKeyboard
        if LcdKeyboard._g_instance:
            LcdKeyboard._g_instance.changeNotifyCallback = LogitechMonitor.onChange
        LOG_DEBUG('LogitechMonitor is initialized')

    @staticmethod
    def onChange(isEnabled, isColored, width, height):
        if isEnabled:
            LogitechMonitor.destroy()
            LogitechMonitor.__isColored = isColored
            LogitechMonitor.__component = _LogitechFlash(isColored, width, height)
            LogitechMonitor.__component.addExternalCallback('logitech.frameLoaded', LogitechMonitor.onScreenLoaded)
            LOG_DEBUG('Logitech keyboard display found: colored = %s,  size = %sx%s' % (isColored, width, height))
            LogitechMonitor.onScreenChange()
        else:
            LogitechMonitor.destroy()
            LOG_DEBUG('No logitech keyboard color display found')

    @staticmethod
    def isPresent():
        return LogitechMonitor.__component is not None

    @staticmethod
    def isPresentColor():
        return LogitechMonitor.__isColored

    @staticmethod
    def destroy():
        LogitechMonitor.__isColored = False
        if LogitechMonitor.__screen:
            LogitechMonitor.__screen.destroy(LogitechMonitor.__isColored)
            LogitechMonitor.__screen = None
        if LogitechMonitor.__messenger:
            LogitechMonitor.__messenger.destroy()
            LogitechMonitor.__messenger = None
        if LogitechMonitor.__component:
            LogitechMonitor.__component.close()
            LogitechMonitor.__component = None
        LOG_DEBUG('LogitechMonitor is finalized')
        return

    @staticmethod
    def onScreenChange(currentScreen = None):
        if not currentScreen and isPlayerAccount():
            currentScreen = 'hangar'
        if currentScreen in LogitechMonitor.SCREEN_TO_FRAME.keys():
            LogitechMonitor.__currentScreen = currentScreen
        if LogitechMonitor.__component:
            screenClass = LogitechMonitor.SCREEN_TO_FRAME[LogitechMonitor.__currentScreen]
            if not isinstance(LogitechMonitor.__screen, screenClass):
                if LogitechMonitor.__screen:
                    LogitechMonitor.__screen.destroy(LogitechMonitor.__isColored)
                LogitechMonitor.__screen = screenClass(LogitechMonitor.__component)
            LogitechMonitor.__screen.load(LogitechMonitor.__isColored)
            LogitechMonitor.onSwitchMessenger(currentScreen)

    @staticmethod
    def onScreenLoaded(callBackID, screenLabel):
        if LogitechMonitor.__screen:
            LOG_DEBUG('LogitechMonitor::screen loaded:', screenLabel)
            LogitechMonitor.__screen.onLoaded()

    @staticmethod
    def onChangeView():
        if LogitechMonitor.__screen:
            LOG_DEBUG('LogitechMonitor::screen change view:')
            LogitechMonitor.__screen.onChangeView()

    @staticmethod
    def onSwitchMessenger(currentScreen):
        delegator = LogitechMonitor.__messenger
        if currentScreen in LogitechMonitor.MESSENGER_IN_SCREEN:
            if delegator is None:
                delegator = LogitechBattleMessenger()
                delegator.create(LogitechMonitor.__screen.uiHolder)
                LogitechMonitor.__messenger = delegator
        elif delegator is not None:
            delegator.destroy()
            LogitechMonitor.__messenger = None
        return
