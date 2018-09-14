# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/logitech/battle_screen.py
import weakref
from collections import namedtuple
import BigWorld
import CommandMapping
from gui.Scaleform.daapi.view.logitech.color_scheme import ColorSchemeManager
from gui.Scaleform.daapi.view.battle.fallout.battle_timer import FALLOUT_ENDING_SOON_TIME
from gui.Scaleform.daapi.view.logitech.LogitechMonitorMeta import LogitechMonitorBattleMonoScreenMeta, LogitechMonitorBattleColoredScreenMeta
from gui.Scaleform.framework.entities.EventSystemEntity import EventSystemEntity
from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES
from gui.battle_control import g_sessionProvider
from gui.battle_control.controllers.debug_ctrl import IDebugPanel, DebugController
from gui.battle_control.controllers.period_ctrl import ArenaPeriodController, ITimersBar
from gui.shared.events import ComponentEvent
from helpers import i18n
from messenger.gui.Scaleform.legacy_entry import LegacyBattleEntry as MessengerBattleEntry
from messenger.m_constants import MESSENGER_SCOPE
_VIEW_CMDS = (CommandMapping.CMD_CHAT_SHORTCUT_ATTACK,
 CommandMapping.CMD_CHAT_SHORTCUT_BACKTOBASE,
 CommandMapping.CMD_CHAT_SHORTCUT_POSITIVE,
 CommandMapping.CMD_CHAT_SHORTCUT_NEGATIVE,
 CommandMapping.CMD_CHAT_SHORTCUT_HELPME,
 CommandMapping.CMD_CHAT_SHORTCUT_RELOAD)
_TimerDisplayData = namedtuple('_TimerDisplayData', ('level', 'minutes', 'seconds'))
_MONO_FONT_WORKAROUND_ENABLE = True

class _ITimerView(object):

    def updateTimer(self, timerDisplayData):
        raise NotImplementedError


class _TimerPresenter(ITimersBar):
    """
    On-screen timer. Shared among colored/mono
    """

    def __init__(self, ui):
        super(_TimerPresenter, self).__init__()
        arenaVisitor = g_sessionProvider.arenaVisitor
        if arenaVisitor.gui.isFalloutBattle():
            self.__endingSoonTime = FALLOUT_ENDING_SOON_TIME
        else:
            self.__endingSoonTime = arenaVisitor.type.getBattleEndingSoonTime()
        self.__ui = ui
        self.__arenaPeriodCtrl = ArenaPeriodController()

    def start(self):
        self.__arenaPeriodCtrl.startControl(weakref.proxy(g_sessionProvider.getCtx()), weakref.proxy(g_sessionProvider.arenaVisitor))
        self.__arenaPeriodCtrl.setViewComponents(weakref.proxy(self), weakref.proxy(self))
        g_sessionProvider.addArenaCtrl(self.__arenaPeriodCtrl)

    def stop(self):
        g_sessionProvider.removeArenaCtrl(self.__arenaPeriodCtrl)
        self.__arenaPeriodCtrl.stopControl()
        self.__arenaPeriodCtrl.clearViewComponents()

    def setTotalTime(self, totalTime):
        self.__updateTimer(totalTime)

    def hideTotalTime(self):
        pass

    def setState(self, state):
        pass

    def setCountdown(self, state, timeLeft):
        self.__updateTimer(timeLeft)

    def hideCountdown(self, state, speed):
        pass

    def __updateTimer(self, time):
        if self.__ui is not None and time >= 0:
            minutes, seconds = divmod(int(time), 60)
            self.__ui.updateTimer(_TimerDisplayData(level=int(time <= self.__endingSoonTime), minutes='{:02d}'.format(minutes), seconds='{:02d}'.format(seconds)))
        return


_FragsDisplayData = namedtuple('_FragsDisplayData', ('progress', 'allyFrags', 'enemyFrags'))

def _makeFragsDisplayData(allyFrags, enemyFrags):
    arenaDP = g_sessionProvider.getArenaDP()
    vehsAlly = arenaDP.getAlliesVehiclesNumber()
    vehsEnemy = arenaDP.getEnemiesVehiclesNumber()
    if vehsAlly + vehsEnemy > 0:
        progress = float(vehsAlly + allyFrags - enemyFrags) / (vehsAlly + vehsEnemy)
    else:
        progress = 0.5
    progress = max(min(progress, 1.0), 0.0)
    return _FragsDisplayData(progress, allyFrags, enemyFrags)


class _IFragsView(object):

    def updateFrags(self, fragsDisplayData):
        """
        :param fragsDisplayData: _FragsDisplayData
        """
        raise NotImplementedError


class _FragsPresenter(EventSystemEntity):

    def __init__(self, ui):
        super(_FragsPresenter, self).__init__()
        self.__ui = ui

    def start(self):
        self.addListener(ComponentEvent.COMPONENT_REGISTERED, self.__onComponentRegistered)

    def stop(self):
        self.removeListener(ComponentEvent.COMPONENT_REGISTERED, self.__onComponentRegistered)

    def __updateFrags(self, leftScore, rightScore):
        self.__ui.updateFrags(_makeFragsDisplayData(leftScore, rightScore))

    def __onComponentRegistered(self, event):
        if event.alias == BATTLE_VIEW_ALIASES.BATTLE_STATISTIC_DATA_CONTROLLER:
            collector = event.componentPy.getStatsCollector()
            collector.onTotalScoreUpdated += self.__onTotalScoreUpdated
            self.__updateFrags(*collector.getTotalScore())

    def __onTotalScoreUpdated(self, leftScore, rightScore):
        self.__updateFrags(leftScore, rightScore)


class LogitechMonitorBattleMonoScreen(LogitechMonitorBattleMonoScreenMeta, _ITimerView, _IFragsView):

    def __init__(self, frame):
        super(LogitechMonitorBattleMonoScreen, self).__init__(frame)
        self.__timerPresenter = _TimerPresenter(weakref.proxy(self))
        self.__fragsPresenter = _FragsPresenter(weakref.proxy(self))
        self.__timerDisplayData = None
        self.__fragsDisplayData = None
        return

    def _onLoaded(self):
        self.__timerPresenter.start()
        self.__fragsPresenter.start()
        self.__update()

    def _onUnloaded(self):
        self.__timerPresenter.stop()
        self.__fragsPresenter.stop()

    def updateTimer(self, timerDisplayData):
        self.__timerDisplayData = timerDisplayData
        self.__update()

    def updateFrags(self, fragsDisplayData):
        self.__fragsDisplayData = fragsDisplayData
        self.__update()

    def __update(self):
        parts = []
        sep = ' :' if _MONO_FONT_WORKAROUND_ENABLE else ':'
        if self.__fragsDisplayData is not None:
            parts.append('{ally} : {enemy}'.format(ally=i18n.makeString('#ingame_gui:player_messages/allied_team_name'), enemy=i18n.makeString('#ingame_gui:player_messages/enemy_team_name')))
            parts.append('{ally}{sep}{enemy}'.format(ally=self.__fragsDisplayData.allyFrags, sep=sep, enemy=self.__fragsDisplayData.enemyFrags))
        if self.__timerDisplayData is not None:
            parts.append('')
            parts.append('{text} {min}{sep}{sec}'.format(text=i18n.makeString('#ingame_gui:timer/battlePeriod'), min=self.__timerDisplayData.minutes, sep=sep, sec=self.__timerDisplayData.seconds))
        self.as_setText('\n'.join(parts))
        return


class LogitechMonitorBattleColoredScreen(LogitechMonitorBattleColoredScreenMeta, IDebugPanel, _ITimerView, _IFragsView):

    def __init__(self, frame):
        super(LogitechMonitorBattleColoredScreen, self).__init__(frame)
        self._colorManager = ColorSchemeManager()
        self.__debugCtrl = DebugController()
        self.__timerPresenter = _TimerPresenter(weakref.proxy(self))
        self.__fragsPresenter = _FragsPresenter(weakref.proxy(self))
        self.__messenger = MessengerBattleEntry()
        self.__isPostmortem = False

    def _onLoaded(self):
        self.__debugCtrl.setViewComponents(weakref.proxy(self))
        self.__debugCtrl.startControl()
        self._colorManager.populateUI(weakref.proxy(self._flashObject))
        self.__timerPresenter.start()
        self.__fragsPresenter.start()
        vehStateCtrl = g_sessionProvider.shared.vehicleState
        self.__isPostmortem = vehStateCtrl and vehStateCtrl.isInPostmortem
        if self.__isPostmortem:
            self.__onPostMortemSwitched()
        if vehStateCtrl is not None:
            vehStateCtrl.onPostMortemSwitched += self.__onPostMortemSwitched
        CommandMapping.g_instance.onMappingChanged += self.setCommands
        self.setCommands()
        self.__messenger.show()
        self.__messenger.enableRecord(False)
        self.__messenger.populateUI(weakref.proxy(self._flashObject))
        return

    def _onUnloaded(self):
        self.__debugCtrl.stopControl()
        self.__debugCtrl.clearViewComponents()
        self.__timerPresenter.stop()
        self.__fragsPresenter.stop()
        ctrl = g_sessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onPostMortemSwitched -= self.__onPostMortemSwitched
        CommandMapping.g_instance.onMappingChanged -= self.setCommands
        self._colorManager.dispossessUI()
        self.__messenger.close(MESSENGER_SCOPE.UNKNOWN)
        self.__messenger.dispossessUI()
        return

    def setCommands(self, *args):
        if self.__isPostmortem:
            return
        else:
            cmdMap = CommandMapping.g_instance
            viewCmdMapping = []
            for command in _VIEW_CMDS:
                commandName = cmdMap.getName(command)
                key = cmdMap.get(commandName)
                viewCmdMapping.append(commandName)
                viewCmdMapping.append(BigWorld.keyToString(key) if key is not None else 'NONE')

            self.as_setCommandMapping(viewCmdMapping)
            return

    def updateDebugInfo(self, ping, fps, isLaggingNow, fpsReplay=-1):
        self.as_updateDebugInfo(fps, ping, isLaggingNow)

    def updateTimer(self, timerDisplayData):
        self.as_setTotalTime(timerDisplayData.level, timerDisplayData.minutes, timerDisplayData.seconds)

    def updateFrags(self, fragsDisplayData):
        label = '{}/{}'.format(fragsDisplayData.allyFrags, fragsDisplayData.enemyFrags)
        self.as_updateFrags(fragsDisplayData.progress, label)

    def __onPostMortemSwitched(self):
        if not g_sessionProvider.getCtx().isPlayerObserver():
            self.__isPostmortem = True
            self.as_hideCommandMapping(True)
