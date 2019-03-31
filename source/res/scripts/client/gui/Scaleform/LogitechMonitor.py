# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/LogitechMonitor.py
# Compiled at: 2019-01-23 05:58:10
import BigWorld, _Scaleform, Avatar, constants, CommandMapping
from debug_utils import LOG_DEBUG
from gui.Scaleform.Flash import Flash
from adisp import process
from gui.Scaleform.utils.requesters import StatsRequester
from gui.Scaleform.utils import dossiers_utils
from messenger.wrappers import ChatActionWrapper
from messenger import filters, g_settings
from messenger.gui import MessengerDispatcher
from gui.Scaleform.ColorSchemeManager import _ColorSchemeManager

class _LogitachFlash(Flash):

    def __init__(self):
        Flash.__init__(self, 'keyboard.swf')
        self.movie.wg_outputToLogitechLcd = True

    def __del__(self):
        LOG_DEBUG('LM::destroy', self)

    @property
    def movie(self):
        return self.component.movie


class _LogitechScreen(object):

    def __init__(self, component, frame):
        self.uiHolder = component
        self.__frameLabel = frame

    def __del__(self):
        LOG_DEBUG('LM::destroy', self)

    def load(self):
        LOG_DEBUG('Logitech changeScreen: ', self.__frameLabel)
        self.uiHolder.call('logitech.gotoFrame', [self.__frameLabel])

    def onLoaded(self):
        pass

    def onUnload(self):
        self.uiHolder = None
        return

    def onChangeView(self):
        self.call('logitech.changeView', [])

    def call(self, methodName, args=None):
        self.uiHolder.call(methodName, args)


class _LogoScreen(_LogitechScreen):

    def __init__(self, component):
        _LogitechScreen.__init__(self, component, 'logo')


class _StatsScreen(_LogitechScreen):

    def __init__(self, component):
        _LogitechScreen.__init__(self, component, 'stats')

    @process
    def onLoaded(self):
        dossier = yield StatsRequester().getAccountDossier()
        self.call('logitech.setStatsData', dossiers_utils.getDossierTotalBlocksSummary(dossier))


class _BattleLoadingScreen(_LogitechScreen):
    _MAP_SOURCE = '../maps/icons/map/screen/%s.dds'

    def __init__(self, component):
        _LogitechScreen.__init__(self, component, 'mapLoading')

    def onLoaded(self):
        arena = getattr(BigWorld.player(), 'arena', None)
        if arena:
            self.call('logitech.setMap', [arena.typeDescriptor.name, self._MAP_SOURCE % arena.typeDescriptor.typeName])
        return


class _BattleScreen(_LogitechScreen):
    __viewCmds = ('CMD_CHAT_SHORTCUT_ATTACK', 'CMD_CHAT_SHORTCUT_BACKTOBASE', 'CMD_CHAT_SHORTCUT_FOLLOWME', 'CMD_CHAT_SHORTCUT_POSITIVE', 'CMD_CHAT_SHORTCUT_NEGATIVE', 'CMD_CHAT_SHORTCUT_HELPME', 'CMD_CHAT_SHORTCUT_ATTACK_MY_TARGET')
    __timerCallBackId = None
    __debugCallBackId = None

    def __init__(self, component):
        _LogitechScreen.__init__(self, component, 'battle')
        self.messenger = None
        self._colorManager = _ColorSchemeManager()
        return

    def onLoaded(self):
        _alliedTeamName = '#ingame_gui:player_messages/allied_team_name'
        _enemyTeamName = '#ingame_gui:player_messages/enemy_team_name'
        self.call('battle.fragCorrelationBar.setTeamNames', [_alliedTeamName, _enemyTeamName])
        player = BigWorld.player()
        if player is None or type(player) != Avatar.PlayerAvatar:
            return
        else:
            arena = BigWorld.player().arena
            if arena is None:
                return
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
            LogitechBattleMessanger.instance(self.uiHolder)
            self._colorManager.populateUI(self.uiHolder)
            return

    def onUnload(self):
        player = BigWorld.player()
        if player is None or type(player) != Avatar.PlayerAvatar:
            return
        else:
            arena = BigWorld.player().arena
            if arena is None:
                return
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
        player = BigWorld.player()
        if player is None or type(player) != Avatar.PlayerAvatar:
            return
        else:
            arena = BigWorld.player().arena
            if arena is None:
                return
            vehicles = arena.vehicles
            frags = {1: 0,
             2: 0}
            total = {1: 0,
             2: 0}
            for vId, vData in vehicles.items():
                vStats = arena.statistics.get(vId, None)
                frags[vData['team']] += 0 if vStats is None else vStats['frags']
                total[vData['team']] += 1

            playerTeam = player.team
            enemyTeam = 3 - playerTeam
            self.call('battle.fragCorrelationBar.updateFrags', [frags[playerTeam],
             frags[enemyTeam],
             total[playerTeam],
             total[enemyTeam]])
            return

    def __onSetArenaTime(self, *args):
        self.__timerCallBackId = None
        player = BigWorld.player()
        if player is None or type(player) != Avatar.PlayerAvatar:
            return
        else:
            arena = BigWorld.player().arena
            if arena is None:
                return
            arenaLength = int(arena.periodEndTime - BigWorld.serverTime())
            arenaLength = arenaLength if arenaLength > 0 else 0
            self.call('battle.timerBar.setTotalTime', [arenaLength])
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
            vehicle = BigWorld.entity(player.playerVehicleID)
            if vehicle is not None and isinstance(vehicle.filter, BigWorld.WGVehicleFilter):
                isLaggingNow = vehicle.filter.isLaggingNow
            ping = min(BigWorld.LatencyInfo().value[3] * 1000, 999)
            if ping < 999:
                ping = max(1, ping - 500.0 * constants.SERVER_TICK_LENGTH)
            fps = BigWorld.getFPS()[0]
            self.call('battle.debugBar.updateInfo', [int(fps), int(ping), isLaggingNow])
            self.__debugCallBackId = BigWorld.callback(0.01, self.__updateDebug)
            return

    def setCommands(self):
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
        _LogitechScreen.__init__(self, component, 'postmortem')
        self.messenger = None
        self._colorManager = _ColorSchemeManager()
        self.onLoaded()
        return

    def setCommands(self):
        self.call('battle.ingameHelp.setCommandMapping', [])

    def onUnload(self):
        LogitechBattleMessanger.destroyInstance()


class LogitechBattleMessanger(object):
    __inst = None

    @staticmethod
    def instance(uiHolder=None):
        if LogitechBattleMessanger.__inst is None:
            LogitechBattleMessanger.__inst = LogitechBattleMessanger()
            LogitechBattleMessanger.__inst.create()
        return LogitechBattleMessanger.__inst.messenger.start(uiHolder)

    @staticmethod
    def destroyInstance():
        if LogitechBattleMessanger.__inst:
            LogitechBattleMessanger.__inst.destroy()
        LogitechBattleMessanger.__inst = None
        return

    def __init__(self):
        messenger = None
        return

    def create(self):
        from messenger.gui.Scalefrom.MessengerBattleInterface import MessengerBattleInterface
        self.messenger = MessengerBattleInterface()
        from ChatManager import chatManager
        from chat_shared import CHAT_ACTIONS
        chatManager.subscribeChatAction(self.onBroadcast, CHAT_ACTIONS.broadcast)
        chatManager.subscribeChatAction(self.onSelfEnterChat, CHAT_ACTIONS.selfEnter)

    def destroy(self):
        from ChatManager import chatManager
        from chat_shared import CHAT_ACTIONS
        chatManager.unsubscribeChatAction(self.onBroadcast, CHAT_ACTIONS.broadcast)
        chatManager.unsubscribeChatAction(self.onSelfEnterChat, CHAT_ACTIONS.selfEnter)
        self.messenger.destroy()
        self.messenger = None
        return

    def onBroadcast(self, chatAction):
        """
        Event handler.
        When player post message to channel, adds message to this channel
        """
        wrapper = ChatActionWrapper(**dict(chatAction))
        cid = wrapper.channel
        filterChain = filters.FilterChain()
        if g_settings.userPreferences['enableOlFilter']:
            filterChain.addFilter('olFilter', filters.ObsceneLanguageFilter())
        filterChain.chainIn(wrapper)
        self.messenger.addChannelMessage(wrapper)

    def onSelfEnterChat(self, chatAction):
        wrapper = ChatActionWrapper(**dict(chatAction))
        cid = wrapper.channel
        uid = wrapper.originator
        channel = MessengerDispatcher.g_instance.channels.getChannel(cid)
        if not channel:
            raise ChannelNotFound(cid)
        self.messenger.addChannel(channel)


class LogitechMonitor(object):
    __component = None
    __screen = None
    SCREEN_TO_FRAME = {'login': _LogoScreen,
     'hangar': _StatsScreen,
     'battleloading': _BattleLoadingScreen,
     'battle': _BattleScreen,
     'postmortem': _PostmortemScreen}

    @staticmethod
    def init():
        lcdKeybParams = BigWorld.wg_getLogitechLcdKeyboardParams()
        if lcdKeybParams and lcdKeybParams[0]:
            LogitechMonitor.__component = _LogitachFlash()
            LogitechMonitor.__component.addExternalCallback('logitech.frameLoaded', LogitechMonitor.onScreenLoaded)
            LOG_DEBUG('Logitech keyboard display found: colored = %s,  size = %sx%s' % lcdKeybParams)
        else:
            LOG_DEBUG('No logitech keyboard color display found')

    @staticmethod
    def isPresent():
        return LogitechMonitor.__component is not None

    @staticmethod
    def destroy():
        if LogitechMonitor.__screen:
            LogitechMonitor.__screen.onUnload()
            LogitechMonitor.__screen = None
        if LogitechMonitor.__component:
            LogitechMonitor.__component.close()
            LogitechMonitor.__component = None
        return

    @staticmethod
    def onScreenChange(currentScreen):
        if LogitechMonitor.__component:
            if currentScreen in LogitechMonitor.SCREEN_TO_FRAME.keys():
                screenClass = LogitechMonitor.SCREEN_TO_FRAME[currentScreen]
                if not isinstance(LogitechMonitor.__screen, screenClass):
                    if LogitechMonitor.__screen:
                        LogitechMonitor.__screen.onUnload()
                    LogitechMonitor.__screen = screenClass(LogitechMonitor.__component)
                    LogitechMonitor.__screen.load()

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
