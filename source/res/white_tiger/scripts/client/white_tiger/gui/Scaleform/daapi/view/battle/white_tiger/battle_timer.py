# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/Scaleform/daapi/view/battle/white_tiger/battle_timer.py
import time
import BigWorld
from constants import ARENA_PERIOD
from white_tiger.gui.Scaleform.daapi.view.meta.WTBattleTimerMeta import WTBattleTimerMeta
from gui.battle_control.controllers.battle_hints_ctrl import IBattleHintView
from gui.impl import backport
from gui.impl.gen import R
from gui.wt_event.wt_event_helpers import isBoss
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider

class WhiteTigerBattleTimer(WTBattleTimerMeta, IBattleHintView):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(WhiteTigerBattleTimer, self).__init__()
        self.__arenaPeriod = None
        self.__periodEndTime = None
        self.currentHint = None
        self.currentHintStartTime = 0
        return

    def setPeriod(self, period):
        super(WhiteTigerBattleTimer, self).setPeriod(period)
        newEndTime = self.sessionProvider.shared.arenaPeriod.getEndTime()
        if self.__arenaPeriod == ARENA_PERIOD.BATTLE and period == ARENA_PERIOD.BATTLE:
            if self.__periodEndTime is not None:
                if newEndTime > self.__periodEndTime:
                    delta = min(newEndTime - self.__periodEndTime, newEndTime - BigWorld.serverTime())
                    self.as_showAdditionalTimeS('+{}'.format(time.strftime('%M:%S', time.gmtime(delta))))
        self.__periodEndTime = newEndTime
        self.__arenaPeriod = period
        return

    def showHint(self, hint, data):
        hintName = hint.name
        if hintName == 'wtTimeRemaining_hunter' or hintName == 'wtTimeRemaining_wtLowHP_hunter':
            message = backport.text(R.strings.white_tiger.battleTimer.timeRemaining.hunter.messageText())
            self.as_showMessageS(message, isOverTime=False)
        elif hintName == 'wtTimeRemaining_boss' or hintName == 'wtTimeRemaining_wtLowHP_boss':
            message = backport.text(R.strings.white_tiger.battleTimer.timeRemaining.boss.messageText())
            self.as_showMessageS(message, isOverTime=False)
        self.currentHint = hint
        self.currentHintStartTime = time.time()

    def hideHint(self, hint=None):
        if hint:
            if hint.name == 'wtTimeRemaining_hunter' or hint.name == 'wtTimeRemaining_wtLowHP_hunter' or hint.name == 'wtTimeRemaining_boss' or hint.name == 'wtTimeRemaining_wtLowHP_boss':
                self.as_hideMessageS()
                self.currentHint = None
        return

    def _populate(self):
        super(WhiteTigerBattleTimer, self)._populate()
        self.as_setPlayerTypeS(self.__isBossPlayer())

    def __isBossPlayer(self):
        vInfo = self.sessionProvider.getCtx().getVehicleInfo(BigWorld.player().playerVehicleID)
        tags = vInfo.vehicleType.tags
        return isBoss(tags)
