# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/comp7/prebattle_timer.py
import BattleReplay
from constants import ARENA_PERIOD, VEHICLE_SELECTION_BLOCK_DELAY
from gui.Scaleform.daapi.view.meta.Comp7PrebattleTimerMeta import Comp7PrebattleTimerMeta
from gui.Scaleform.genConsts.PREBATTLE_TIMER import PREBATTLE_TIMER
from gui.battle_control import avatar_getter
from gui.battle_control.battle_constants import COUNTDOWN_STATE
from gui.impl import backport
from gui.impl.gen import R
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import GameEvent
from gui.shared.utils.functions import makeTooltip
from helpers import dependency, i18n
from skeletons.gui.battle_session import IBattleSessionProvider

class Comp7PrebattleTimer(Comp7PrebattleTimerMeta):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)
    __RES_ROOT = R.strings.comp7.prebattleTimer

    def __init__(self):
        super(Comp7PrebattleTimer, self).__init__()
        self.__isSelectionConfirmed = False
        self.__winConditionStr = ''
        self.__isPrebattleInputStateLocked = False
        self.__isUIUpdateNeeded = True
        self.__lastProcessedState = self._state

    def updateBattleCtx(self, battleCtx):
        self.__winConditionStr = battleCtx.getArenaWinString()
        super(Comp7PrebattleTimer, self).updateBattleCtx(battleCtx)

    def setCountdown(self, state, timeLeft):
        if state == ARENA_PERIOD.PREBATTLE and timeLeft is not None:
            timeLeft -= VEHICLE_SELECTION_BLOCK_DELAY
        super(Comp7PrebattleTimer, self).setCountdown(state, timeLeft)
        self.__updateUIIfNeeded()
        return

    def onReadyBtnClick(self):
        self.__sessionProvider.dynamic.comp7PrebattleSetup.confirmVehicleSelection()
        self.__setIsSelectionConfirmed(True)
        self.as_hideInfoS()
        self.__updateMessageAndWinDescription()

    def hideCountdown(self, state, speed):
        if not self.__isSelectionConfirmed:
            self.as_setWinConditionTextS(self.__winConditionStr)
        super(Comp7PrebattleTimer, self).hideCountdown(state, speed)

    def _populate(self):
        super(Comp7PrebattleTimer, self)._populate()
        self.__isSelectionConfirmed = self.__sessionProvider.dynamic.comp7PrebattleSetup.isSelectionConfirmed()
        g_eventBus.addListener(GameEvent.PREBATTLE_INPUT_STATE_LOCKED, self.__onPrebattleInputStateLocked, scope=EVENT_BUS_SCOPE.BATTLE)
        self.__updateUIIfNeeded()

    def _dispose(self):
        g_eventBus.removeListener(GameEvent.PREBATTLE_INPUT_STATE_LOCKED, self.__onPrebattleInputStateLocked, scope=EVENT_BUS_SCOPE.BATTLE)
        super(Comp7PrebattleTimer, self)._dispose()

    def _isDisplayWinCondition(self):
        return False

    def _getMessage(self):
        if self._state == COUNTDOWN_STATE.WAIT:
            return backport.text(self.__RES_ROOT.wait.header())
        if self.__isSelectionPossible():
            if self.__isPrebattleInputStateLocked:
                return ''
            if self._state == COUNTDOWN_STATE.START:
                return backport.text(self.__RES_ROOT.wait.selectVehicle())
        return i18n.makeString(self._battleTypeStr)

    def __updateUIIfNeeded(self):
        self.__invalidateLastProcessedState()
        if self.__isUIUpdateNeeded:
            self.__updateHint()
            self.__updateButton()
            self.__updateMessageAndWinDescription()
            self.__isUIUpdateNeeded = False

    def __invalidateLastProcessedState(self):
        if self.__lastProcessedState != self._state:
            self.__lastProcessedState = self._state
            self.__isUIUpdateNeeded = True

    def __updateHint(self):
        if self.__isSelectionConfirmed:
            self.as_hideInfoS()
        elif not self.__isPrebattleInputStateLocked:
            self.as_setInfoHintS('')

    def __updateButton(self):
        if not self.__isSelectionPossible():
            self.as_hideInfoS()
        elif self._state == COUNTDOWN_STATE.START and not self.__isPrebattleInputStateLocked and not BattleReplay.g_replayCtrl.isPlaying:
            self.as_addInfoS(PREBATTLE_TIMER.COMP7_PREBATTLE_INFO_VIEW_LINKAGE, self.__getInfoVO())
            self.as_showInfoS()

    def __getInfoVO(self):
        return {'readyBtnLabel': backport.text(self.__RES_ROOT.info.readyBtn.label()),
         'readyBtnTooltip': makeTooltip(body=backport.text(self.__RES_ROOT.info.readyBtn.tooltip.body()))}

    def __onPrebattleInputStateLocked(self, _):
        self.__setIsPrebattleInputStateLocked(True)
        if not self.__isSelectionConfirmed:
            self.as_setMessageS(self._getMessage())
            self.as_hideInfoS()

    def __updateMessageAndWinDescription(self):
        if not self.__isSelectionPossible():
            self.as_setMessageS(self._getMessage())
            self.as_setWinConditionTextS(self.__winConditionStr)
        elif self._state == COUNTDOWN_STATE.WAIT:
            self.as_setWinConditionTextS(backport.text(self.__RES_ROOT.wait.additionalInfo()))
        else:
            self.as_setWinConditionTextS('')

    def __isSelectionPossible(self):
        return not self.__isSelectionConfirmed and not avatar_getter.isObserver()

    def __setIsSelectionConfirmed(self, value):
        self.__isUIUpdateNeeded = self.__isSelectionConfirmed != value
        self.__isSelectionConfirmed = value

    def __setIsPrebattleInputStateLocked(self, value):
        self.__isUIUpdateNeeded = self.__isPrebattleInputStateLocked != value
        self.__isPrebattleInputStateLocked = value
