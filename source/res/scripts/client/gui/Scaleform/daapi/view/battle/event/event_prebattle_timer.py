# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/event_prebattle_timer.py
import BigWorld
from constants import ARENA_PERIOD
from gui.battle_control import avatar_getter
from gui.Scaleform.daapi.view.meta.EventPrebattleTimerMeta import EventPrebattleTimerMeta
from gui.Scaleform.genConsts.PREBATTLE_TIMER import PREBATTLE_TIMER as _PBT
from gui.Scaleform.genConsts.EVENT_CONSTS import EVENT_CONSTS
from gui.battle_control.battle_constants import COUNTDOWN_STATE
from gui.shared import EVENT_BUS_SCOPE, g_eventBus
from gui.shared.events import WtGameEvent
from gui.impl import backport
from gui.impl.gen import R
from helpers import time_utils
from PlayerEvents import g_playerEvents
_HUNTER_LIVES_MAX = 3

class MessageHighlightedTypes(object):
    SIMPLE_MESSAGE = 'simpleMessage'
    ADD_EXTRA_TIME = 'addExtraTime'
    MAX_POWER_UP = 'maxPowerUp'


class EventPreBattleTimer(EventPrebattleTimerMeta):

    def __init__(self):
        super(EventPreBattleTimer, self).__init__()
        self.__team = 0
        self.__powerPoints = 0
        self.__maxPowerPoints = 0
        self.__extraLootBoxTime = 0
        self.__endingSoonTime = self.sessionProvider.arenaVisitor.type.getBattleEndingSoonTime()
        self.__endWarningEnabled = False
        self.__addExtraTimerCallbacks = []
        self.__maxPowerUpInShowing = False
        self.__maxPowerUpCallback = None
        self.__arenaWinStr = None
        self.__totalTime = 0
        return

    def _populate(self):
        super(EventPreBattleTimer, self)._populate()
        g_eventBus.addListener(WtGameEvent.GROUPDRPOP_POSITIONS, self.__onUpdateDropPositions, scope=EVENT_BUS_SCOPE.BATTLE)
        ctrl = self.sessionProvider.dynamic.arenaInfo
        if ctrl is not None:
            ctrl.onPowerPointsChanged += self.__onPowerChanged
            self.__powerPoints = ctrl.powerPoints
            self.__maxPowerPoints = ctrl.maxPowerPoints
            self.__extraLootBoxTime = ctrl.extraLootBoxTime
        vStateCtrl = self.sessionProvider.shared.vehicleState
        if vStateCtrl is not None:
            vStateCtrl.onVehicleControlling += self.__onVehicleControlling
        g_playerEvents.onRoundFinished += self.__onRoundFinished
        self.__team = BigWorld.player().team
        return

    def _dispose(self):
        if self.__maxPowerUpCallback is not None:
            BigWorld.cancelCallback(self.__maxPowerUpCallback)
            self.__maxPowerUpCallback = None
        super(EventPreBattleTimer, self)._dispose()
        g_eventBus.removeListener(WtGameEvent.GROUPDRPOP_POSITIONS, self.__onUpdateDropPositions, scope=EVENT_BUS_SCOPE.BATTLE)
        ctrl = self.sessionProvider.dynamic.arenaInfo
        if ctrl is not None:
            ctrl.onPowerPointsChanged -= self.__onPowerChanged
        vStateCtrl = self.sessionProvider.shared.vehicleState
        if vStateCtrl is not None:
            vStateCtrl.onVehicleControlling += self.__onVehicleControlling
        g_playerEvents.onRoundFinished -= self.__onRoundFinished
        return

    def updateBattleCtx(self, battleCtx):
        self.__arenaWinStr = battleCtx.getArenaWinString()
        super(EventPreBattleTimer, self).updateBattleCtx(battleCtx)

    def setTotalTime(self, totalTime):
        super(EventPreBattleTimer, self).setTotalTime(totalTime)
        if self._arenaPeriod != ARENA_PERIOD.BATTLE:
            return
        if not self.__endWarningEnabled:
            if 0 < totalTime < self.__endingSoonTime:
                self.__endWarningEnabled = True
                self.__maxPowerUpInShowing or self.__setCountDown(totalTime)
        self.__totalTime = totalTime

    def setPeriod(self, period):
        if self.__endWarningEnabled:
            return
        else:
            if self._arenaPeriod is None and period == ARENA_PERIOD.BATTLE:
                self.__showHighLightedMessage(description=backport.text(R.strings.wt_event.pbt.onBattleStarts.num(self.__team)()))
            elif period == ARENA_PERIOD.PREBATTLE and self.__arenaWinStr is not None:
                self.as_setWinConditionTextS(self.__arenaWinStr)
            super(EventPreBattleTimer, self).setPeriod(period)
            return

    def showAddExtraTime(self, diff):
        if not self.__endWarningEnabled:
            self.__showExtraTimeInCorner(diff)
        minutes, seconds = divmod(int(diff), time_utils.ONE_MINUTE)
        if self.__team == EVENT_CONSTS.TEAM_HUNTER:
            highlight = _PBT.MSG_HIGHLIGHT_BLUE
        else:
            highlight = _PBT.MSG_HIGHLIGHT_RED
        if self.__endWarningEnabled:
            self.as_showExtraMessageS(value=backport.text(R.strings.wt_event.pbt.endWarning.timeAdded(), minutes='{:02d}'.format(minutes), seconds='{:02d}'.format(seconds)), highlight=highlight)
            avatar_getter.getSoundNotifications().play('ev_white_tiger_increase_time')
        elif self.__team == EVENT_CONSTS.TEAM_HUNTER:
            self.__showHighLightedMessage(msgType=MessageHighlightedTypes.ADD_EXTRA_TIME, msg=backport.text(R.strings.wt_event.pbt.timeAdded(), minutes='{:02d}'.format(minutes), seconds='{:02d}'.format(seconds)), icon=_PBT.MSG_ICON_TIMER, highlight=highlight)

    def highlightedMessageShown(self, msgType):
        if msgType == MessageHighlightedTypes.ADD_EXTRA_TIME:
            avatar_getter.getSoundNotifications().play('ev_white_tiger_increase_time')
            if self.__addExtraTimerCallbacks:
                self.__addExtraTimerCallbacks.pop()()
        elif msgType == MessageHighlightedTypes.MAX_POWER_UP:
            self.__maxPowerUpCallback = BigWorld.callback(5.5, self.__maxPowerUpShown)

    def _isDisplayWinCondition(self):
        return False

    def _hideCountdownSetMessage(self, state, speed):
        if state != COUNTDOWN_STATE.STOP:
            super(EventPreBattleTimer, self)._hideCountdownSetMessage(state, speed)
        else:
            self.as_hideAllS(False)
            if not self.__endWarningEnabled:
                self.__showHighLightedMessage(description=backport.text(R.strings.wt_event.pbt.onBattleStarts.num(self.__team)()), duration=5000, flush=True)

    def __maxPowerUpShown(self):
        self.__maxPowerUpInShowing = False
        self.__maxPowerUpCallback = None
        return

    def __onUpdateDropPositions(self, event):
        if self.__endWarningEnabled:
            return
        if event.ctx['addPositions']:
            self.__showHighLightedMessage(description=backport.text(R.strings.wt_event.pbt.onLootAppear.num(self.__team)()), duration=5000)

    def __onRoundFinished(self, winTeam, reason):
        finishType = 'victory'
        highlight = _PBT.MSG_HIGHLIGHT_BLUE
        if self.__team != winTeam:
            finishType = 'defeat'
            highlight = _PBT.MSG_HIGHLIGHT_RED
        text = backport.text(R.strings.wt_event.pbt.dyn(finishType)())
        descr = backport.text(R.strings.wt_event.pbt.dyn(finishType).num(self.__team).num(reason)())
        self.__showHighLightedMessage(msg=text, description=descr, highlight=highlight, isBigMsg=True, duration=60000, flush=True, fadeInDuration=5000)

    def __onPowerChanged(self, value):
        timeDiff = (value - self.__powerPoints) * self.__extraLootBoxTime
        self.__powerPoints = value
        self.__onPowerUp(value)
        self.showAddExtraTime(timeDiff)

    def __onPowerUp(self, value):
        isMaxLevel = self.__maxPowerPoints == value
        if self.__team == EVENT_CONSTS.TEAM_BOSS and isMaxLevel:
            self.__showMaxPopUp()
        elif self.__team == EVENT_CONSTS.TEAM_HUNTER and not self.__endWarningEnabled:
            self.__showHighLightedMessage(msg=backport.text(R.strings.wt_event.pbt.onPowerUp_hunter.num(int(isMaxLevel))()), icon=_PBT.MSG_ICON_ARROW_BLUE, highlight=_PBT.MSG_HIGHLIGHT_BLUE)

    def __setCountDown(self, value):
        minutes, seconds = divmod(value, time_utils.ONE_MINUTE)
        self.__showHighLightedMessage(msg=backport.text(R.strings.wt_event.pbt.timer(), minutes='{:02d}'.format(minutes), seconds='{:02d}'.format(seconds)), description=backport.text(R.strings.wt_event.pbt.endWarning.num(self.__team)()), highlight=_PBT.MSG_HIGHLIGHT_BLUE if self.__team == EVENT_CONSTS.TEAM_BOSS else _PBT.MSG_HIGHLIGHT_RED, isBigMsg=True, duration=60000, flush=True)

    def __onVehicleControlling(self, vehicle):
        if vehicle.isAlive() and vehicle.isPlayerVehicle:
            ctrl = self.sessionProvider.dynamic.respawn
            if ctrl is not None:
                countLives = ctrl.teammatesLives.get(vehicle.id, 0)
                if 1 < countLives < _HUNTER_LIVES_MAX:
                    self.__showHighLightedMessage(description=backport.text(R.strings.wt_event.pbt.onHunterRespawn()))
        return

    def __showHighLightedMessage(self, msgType=MessageHighlightedTypes.SIMPLE_MESSAGE, msg='', description='', icon=None, highlight=None, duration=None, isBigMsg=False, flush=False, fadeInDuration=None):
        data = {'msgType': msgType,
         'msg': msg,
         'winCondition': description,
         'isBigMsg': isBigMsg}
        if icon is not None:
            data.update({'icon': icon})
        if highlight is not None:
            data.update({'hightLight': highlight})
        if duration is not None:
            data.update({'duration': duration})
        if fadeInDuration is not None:
            data.update({'fadeInDuration': fadeInDuration})
        self.as_queueHighlightedMessageS(data, flush=flush)
        return

    def __showExtraTimeInCorner(self, diff):
        event = WtGameEvent(WtGameEvent.TIMER_ADDED_ANIMATION, ctx={'diff': diff})
        g_eventBus.handleEvent(event, scope=EVENT_BUS_SCOPE.BATTLE)

    def __showMaxPopUp(self):
        self.__maxPowerUpInShowing = True
        if self.__endWarningEnabled:
            minutes, seconds = divmod(self.__totalTime, time_utils.ONE_MINUTE)
            self.__showHighLightedMessage(msg=backport.text(R.strings.wt_event.pbt.timer(), minutes='{:02d}'.format(minutes), seconds='{:02d}'.format(seconds)), description=backport.text(R.strings.wt_event.pbt.endWarning.num(self.__team)()), highlight=_PBT.MSG_HIGHLIGHT_BLUE if self.__team == EVENT_CONSTS.TEAM_BOSS else _PBT.MSG_HIGHLIGHT_RED, isBigMsg=True, duration=1500, flush=True)
            self.__showHighLightedMessage(msgType=MessageHighlightedTypes.MAX_POWER_UP, msg=backport.text(R.strings.wt_event.pbt.onPowerUp_boss()), icon=_PBT.MSG_ICON_ARROW_RED, highlight=_PBT.MSG_HIGHLIGHT_RED, duration=5000, fadeInDuration=500)
        else:
            self.__showHighLightedMessage(msgType=MessageHighlightedTypes.MAX_POWER_UP, msg=backport.text(R.strings.wt_event.pbt.onPowerUp_boss()), icon=_PBT.MSG_ICON_ARROW_RED, highlight=_PBT.MSG_HIGHLIGHT_RED)
