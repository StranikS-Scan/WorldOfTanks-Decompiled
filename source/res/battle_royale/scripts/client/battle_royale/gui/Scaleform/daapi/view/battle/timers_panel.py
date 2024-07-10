# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/Scaleform/daapi/view/battle/timers_panel.py
import weakref
import math
import BigWorld
from gui.Scaleform.daapi.view.meta.BattleRoyaleTimersPanelMeta import BattleRoyaleTimersPanelMeta
from gui.battle_control.controllers.period_ctrl import IAbstractPeriodView
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import AirDropEvent
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from constants import ARENA_PERIOD
from gui.Scaleform.daapi.view.battle.shared.timers_common import TimerComponent, PythonTimer

def _setRespawnTime(panel, timeLeft):
    panel.as_setRespawnTimeS(timeLeft)


def _setAirDropTime(panel, timeLeft):
    panel.as_setAirDropTimeS(timeLeft)


class _AsTimer(TimerComponent):

    def __init__(self, panel, totalTime, viewFunc):
        super(_AsTimer, self).__init__(weakref.proxy(panel), 0, 0, totalTime, 0)
        self._viewFunc = viewFunc

    def _startTick(self):
        pass

    def _stopTick(self):
        pass

    def _hideView(self):
        pass

    def _showView(self, isBubble):
        self._viewFunc(self._viewObject, self._totalTime)


class _ReplayTimer(PythonTimer):

    def __init__(self, panel, totalTime, viewFunc):
        super(_ReplayTimer, self).__init__(weakref.proxy(panel), 0, 0, totalTime, 0)
        self._viewFunc = viewFunc

    def _hideView(self):
        self._viewFunc(self._viewObject, 0)

    def _showView(self, isBubble):
        pass

    def _setViewSnapshot(self, timeLeft):
        self._viewFunc(self._viewObject, int(math.ceil(timeLeft)))


class TimersPanelPanel(BattleRoyaleTimersPanelMeta, IAbstractPeriodView):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)
    __timerCreator = property(lambda self: _ReplayTimer if self.__sessionProvider.isReplayPlaying else _AsTimer)

    def __init__(self):
        super(TimersPanelPanel, self).__init__()
        self._respawnPeriod = 0

    def _populate(self):
        super(TimersPanelPanel, self)._populate()
        g_eventBus.addListener(AirDropEvent.AIR_DROP_NXT_SPAWNED, self.__onAirDropLootSpawned, scope=EVENT_BUS_SCOPE.BATTLE)
        arenaInfo = BigWorld.player().arena.arenaInfo
        self._respawnPeriod = arenaInfo.arenaInfoBRComponent.respawnPeriod if arenaInfo else 0
        self.as_setIsReplayS(self.__sessionProvider.isReplayPlaying)
        self._airDroptimer = self._respawnTimer = None
        if self.__sessionProvider.isReplayPlaying:
            period = self.__sessionProvider.arenaVisitor.getArenaPeriod()
            self.setPeriod(period)
        return

    def _dispose(self):
        super(TimersPanelPanel, self)._dispose()
        g_eventBus.removeListener(AirDropEvent.AIR_DROP_NXT_SPAWNED, self.__onAirDropLootSpawned, scope=EVENT_BUS_SCOPE.BATTLE)

    def setPeriod(self, period):
        if period == ARENA_PERIOD.BATTLE:
            timeout = self._respawnPeriod
            periodCtrl = self.__sessionProvider.shared.arenaPeriod
            if periodCtrl:
                startTime = periodCtrl.getEndTime() - periodCtrl.getLength()
                timeout -= BigWorld.serverTime() - startTime
            self._respawnTimer = self.__timerCreator(self, timeout, _setRespawnTime)
            self._respawnTimer.show()

    def __onAirDropLootSpawned(self, event):
        self._airDroptimer = self.__timerCreator(self, event.ctx['timeout'] - BigWorld.serverTime(), _setAirDropTime)
        self._airDroptimer.show()
