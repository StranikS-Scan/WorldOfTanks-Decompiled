# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/Scaleform/daapi/view/battle/battle_timer.py
import time
import BigWorld
from constants import ARENA_PERIOD
from gui.battle_control.controllers.battle_hints.component import IBattleHintView
from gui.impl import backport
from gui.impl.gen import R
from white_tiger.gui.wt_event_helpers import isBoss
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from white_tiger.gui.Scaleform.daapi.view.meta.WhiteTigerBattleTimerMeta import WhiteTigerBattleTimerMeta
from PlayerEvents import g_playerEvents

class WhiteTigerBattleTimer(WhiteTigerBattleTimerMeta, IBattleHintView):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(WhiteTigerBattleTimer, self).__init__()
        self.__arenaPeriod = None
        self.__periodEndTime = None
        return

    def setPeriod(self, period):
        super(WhiteTigerBattleTimer, self).setPeriod(period)
        newEndTime = self.sessionProvider.shared.arenaPeriod.getEndTime()
        if self.__arenaPeriod == ARENA_PERIOD.BATTLE and period == ARENA_PERIOD.BATTLE:
            if self.__periodEndTime is not None:
                if newEndTime > self.__periodEndTime:
                    self.hideTimerBackground()
                    delta = min(newEndTime - self.__periodEndTime, newEndTime - BigWorld.serverTime())
                    self.as_showAdditionalTimeS('+{}'.format(time.strftime('%M:%S', time.gmtime(delta))))
        self.__periodEndTime = newEndTime
        self.__arenaPeriod = period
        return

    def _startTicking(self):
        super(WhiteTigerBattleTimer, self)._startTicking()
        self.enableTimerBackground()

    def enableTimerBackground(self):
        if self.__isBossPlayer():
            message = backport.text(R.strings.white_tiger_battle.battleTimer.timeRemaining.boss.messageText())
            self.as_showMessageS(message, isOverTime=True)
        else:
            message = backport.text(R.strings.white_tiger_battle.battleTimer.timeRemaining.hunter.messageText())
            self.as_showMessageS(message, isOverTime=True)

    def hideTimerBackground(self):
        self.as_hideMessageS()

    def _populate(self):
        super(WhiteTigerBattleTimer, self)._populate()
        self.as_setPlayerTypeS(self.__isBossPlayer())
        g_playerEvents.onAvatarReady += self.__onAvatarReady

    def _dispose(self):
        super(WhiteTigerBattleTimer, self)._dispose()
        g_playerEvents.onAvatarReady -= self.__onAvatarReady

    def __isBossPlayer(self):
        vInfo = self.sessionProvider.getCtx().getVehicleInfo(BigWorld.player().playerVehicleID)
        tags = vInfo.vehicleType.tags
        return isBoss(tags)

    def __onAvatarReady(self):
        if self._isTicking:
            self.enableTimerBackground()
